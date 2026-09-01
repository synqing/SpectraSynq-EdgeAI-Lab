"""Security and fixture tests for the Mission Control bridge."""

from __future__ import annotations

import http.client
import hashlib
import importlib.util
import json
import sqlite3
import sys
import threading
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools/serial-studio/webview/bridge.py"
SPEC = importlib.util.spec_from_file_location("serial_studio_webview_bridge", MODULE_PATH)
assert SPEC and SPEC.loader
bridge = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = bridge
SPEC.loader.exec_module(bridge)


def _server() -> tuple[object, threading.Thread, int]:
    fixture = json.loads(
        (ROOT / "tools/serial-studio/fixtures/healthy.json").read_text(encoding="utf-8")
    )
    server = bridge.MissionControlServer(
        ("127.0.0.1", 0), bridge.SnapshotCache(fixture), bridge.load_font_assets()
    )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread, server.server_port


def _request(port: int, method: str, path: str, *, host: str | None = None):
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=2)
    headers = {"Host": host} if host else {}
    connection.request(method, path, headers=headers)
    response = connection.getresponse()
    payload = response.read()
    headers_out = dict(response.getheaders())
    connection.close()
    return response.status, headers_out, payload


def test_bridge_is_get_only_same_origin_and_cached() -> None:
    server, thread, port = _server()
    try:
        status, headers, payload = _request(port, "GET", "/api/v1/snapshot")
        assert status == 200
        assert json.loads(payload)["schema"] == "spectrasynq.serial-studio.mission-control.v2"
        assert headers["Cache-Control"] == "no-store"
        assert "script-src 'self'" in headers["Content-Security-Policy"]
        assert _request(port, "GET", "/live")[0] == 200
        assert _request(port, "POST", "/api/v1/snapshot")[0] == 405
        assert _request(port, "GET", "/api/v1/snapshot", host="attacker.invalid")[0] == 403
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_fonts_are_hash_verified_without_repository_copies() -> None:
    assets = bridge.load_font_assets()
    assert len(assets) == 3
    for asset in assets.values():
        assert str(asset["resolved_path"]).startswith("/Users/spectrasynq/Library/Fonts/")
        assert not str(asset["resolved_path"]).startswith(str(ROOT))


def test_browser_code_contains_no_upstream_command_surface() -> None:
    app = (ROOT / "tools/serial-studio/webview/app.js").read_text(encoding="utf-8")
    assert "/api/v1/snapshot" in app
    for forbidden in ("io.writeData", "deviceWrite", "project.source", "dashboard.getData"):
        assert forbidden not in app
    assert 'view === "audio-reference"' in app
    assert 'view === "ap-validation"' in app
    assert "HOST REFERENCE · NOT DEVICE INPUT" in app
    assert "OBSERVE-ONLY ENFORCED" not in app
    assert "STOCK PRO / NOT PATCHED" in app
    assert "TX WITNESS · ZERO BYTES" in app


def test_empty_snapshot_keeps_project_app_and_witness_authorities_separate() -> None:
    policy = bridge.empty_snapshot("live")["instrument"]["policy"]
    assert policy == {
        "project_policy": "OBSERVE_ONLY",
        "app_egress_guard": "STOCK_PRO_NOT_PATCHED",
        "tx_witness": "REQUIRED_PENDING",
    }


def test_audio_binding_and_validation_receipt_are_hash_checked(tmp_path: Path) -> None:
    source = {
        "sourceId": 2,
        "busType": 3,
        "connection": {
            "normalization": False,
            "deviceId": {
                "inputDeviceName": "Test Loopback",
                "sampleRateValue": 48000,
                "formatName": "Signed 16-bit",
                "channelCount": 2,
            },
        },
    }
    source_sha = bridge._canonical_sha(source)
    binding_path = tmp_path / "binding.json"
    binding_path.write_text(
        json.dumps(
            {
                "schema": "spectrasynq.serial-studio.audio-source-binding.v1",
                "profile_id": "PASSIVE_DUAL_UART_AUDIO_REF",
                "source_projection_sha256": source_sha,
                "source_projection": source,
            }
        ),
        encoding="utf-8",
    )
    binding = bridge.load_audio_binding(binding_path)
    assert binding is not None
    assert binding["binding_sha256"] == hashlib.sha256(binding_path.read_bytes()).hexdigest()

    receipt_path = tmp_path / "receipt.json"
    receipt_path.write_text(
        json.dumps(
            {
                "schema": "spectrasynq.audio-reference-validation.v1",
                "integrity_status": "VALID",
                "time_authority": "HOST_AUDIO_REFERENCE_TIME",
                "score": {"status": "NOT_SCORED", "profile_id": None, "profile_sha256": None},
                "capture": {"sha256": "a" * 64},
                "reference": {"sha256": "b" * 64},
                "claims": {"k1_capture_pipeline_validated": False},
            }
        ),
        encoding="utf-8",
    )
    loaded = bridge.load_audio_validation(receipt_path)
    assert loaded is not None
    assert loaded["score_status"] == "NOT_SCORED"
    assert loaded["time_authority"] == "HOST_AUDIO_REFERENCE_TIME"

    value = json.loads(binding_path.read_text(encoding="utf-8"))
    value["source_projection"]["connection"]["deviceId"]["inputDeviceName"] = "Retargeted"
    binding_path.write_text(json.dumps(value), encoding="utf-8")
    try:
        bridge.load_audio_binding(binding_path)
    except RuntimeError as error:
        assert "hash mismatch" in str(error)
    else:
        raise AssertionError("mutated binding was accepted")


class _FakeAudioClient:
    def latest_frame(self, source_id: str) -> dict[str, object]:
        assert source_id == "2"
        return {"hasData": True, "ageMs": 18, "sequence": 91, "values": [0.1, -0.2]}


def test_live_audio_source_is_not_decoded_as_k1_telemetry() -> None:
    sampler = bridge.LiveSampler(bridge.SnapshotCache({}), 7777, 0.25)
    result = sampler._sample_audio_reference(
        _FakeAudioClient(),  # type: ignore[arg-type]
        [{"sourceId": 2, "busType": 3, "title": "Host Audio Reference"}],
    )

    assert result["state"] == "LIVE_UNVERIFIED"
    assert result["age_ms"] == 18
    assert result["capture"]["level_dbfs"] is None
    assert "metrics" not in result
    assert "FRESHNESS_THRESHOLD_PROFILE_MISSING" in result["reason_codes"]


def test_historian_ingress_sampler_measures_per_source_rates(tmp_path: Path) -> None:
    database = tmp_path / "live.db"
    with sqlite3.connect(database) as connection:
        connection.executescript(
            """
            CREATE TABLE sessions (session_id INTEGER PRIMARY KEY, ended_at TEXT);
            CREATE TABLE raw_bytes (
              session_id INTEGER, device_id INTEGER, data BLOB
            );
            CREATE TABLE columns (
              session_id INTEGER, source_id INTEGER, unique_id INTEGER,
              title TEXT, group_title TEXT
            );
            CREATE TABLE readings (
              session_id INTEGER, unique_id INTEGER, final_numeric_value REAL
            );
            INSERT INTO sessions VALUES (9, NULL);
            INSERT INTO columns VALUES
              (9, 0, 100, 'Host parse sequence', 'Bench decoded forensics'),
              (9, 1, 200, 'Host parse sequence', 'Main decoded forensics');
            INSERT INTO readings VALUES (9, 100, 10), (9, 200, 20);
            INSERT INTO raw_bytes VALUES (9, 0, X'0102'), (9, 1, X'010203');
            """
        )

    sampler = bridge.HistorianIngressSampler(database)
    first = sampler.sample(10.0)
    assert first["state"] == "MEASURED"
    assert first["session_id"] == 9
    assert first["sources"]["0"]["raw_bytes"] == 2
    assert first["sources"]["0"]["raw_bytes_per_second"] is None

    with sqlite3.connect(database) as connection:
        connection.executescript(
            """
            INSERT INTO readings VALUES (9, 100, 14), (9, 200, 22);
            INSERT INTO raw_bytes VALUES (9, 0, X'01020304'), (9, 1, X'0102030405');
            """
        )

    second = sampler.sample(12.0)
    assert second["sources"]["0"]["raw_bytes_per_second"] == 2.0
    assert second["sources"]["0"]["raw_rows_per_second"] == 0.5
    assert second["sources"]["0"]["parsed_publications_per_second"] == 2.0
    assert sampler.sample(14.0)["sources"]["0"]["last_raw_byte_age_ms"] == 2000
