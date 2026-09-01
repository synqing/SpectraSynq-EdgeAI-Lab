#!/usr/bin/env python3
"""Local read-only cache and asset server for K1 Mission Control.

Browser requests never trigger an upstream Serial Studio call. A single sampler
thread owns the fixed read allow-list and publishes immutable cache snapshots.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import mimetypes
import sqlite3
import sys
import threading
import time
from dataclasses import dataclass, field
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
SRC = REPO / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from edgeai.serial_studio import SerialStudioError, SerialStudioReadClient  # noqa: E402


HOST = "127.0.0.1"
PORT = 8765
STATIC_ROUTES = {
    "/": "index.html",
    "/live": "index.html",
    "/index.html": "index.html",
    "/app.js": "app.js",
    "/styles.css": "styles.css",
}
METRICS = {
    1: ("bpm", "BPM"),
    2: ("confidence", "ratio"),
    3: ("lock", "bool"),
    4: ("beat", "event"),
    5: ("onset", "event"),
    6: ("bass_onset", "event"),
    7: ("silence", "bool"),
    8: ("agc_gain", "×"),
    9: ("peak_scaled", "relative"),
    10: ("ssl", "raw"),
    11: ("energy", "ratio"),
    12: ("novelty", "ratio"),
    13: ("system_fps", "Hz"),
    14: ("led_fps", "Hz"),
    15: ("lightshow", "id"),
    16: ("device_ms", "ms"),
    17: ("frame_ms", "ms"),
    18: ("host_parse_seq", "count"),
    19: ("event_tid", "count"),
    20: ("record_kind", "enum"),
    21: ("update_mask", "bitmask"),
    22: ("phase", "mixed"),
    23: ("orbit_x", "derived"),
    24: ("orbit_y", "derived"),
}
AUDIO_REFERENCE_SCHEMA = "spectrasynq.audio-reference-validation.v1"


def _hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_font_assets() -> dict[str, dict[str, Any]]:
    manifest = json.loads((HERE / "font-assets.json").read_text(encoding="utf-8"))
    assets: dict[str, dict[str, Any]] = {}
    for item in manifest["assets"]:
        path = Path(item["path"])
        if not path.is_file():
            raise RuntimeError(f"local font is missing: {path}")
        actual = _hash_file(path)
        if actual != item["sha256"]:
            raise RuntimeError(f"local font hash mismatch: {path}")
        assets[item["route"]] = {**item, "resolved_path": path}
    return assets


@dataclass
class SnapshotCache:
    value: dict[str, Any]
    lock: threading.Lock = field(default_factory=threading.Lock)

    def replace(self, value: dict[str, Any]) -> None:
        with self.lock:
            self.value = value

    def read(self) -> dict[str, Any]:
        with self.lock:
            return copy.deepcopy(self.value)


class HistorianIngressSampler:
    """Measure per-source ingress from the live Historian without writing to it."""

    def __init__(self, database: Path) -> None:
        self.database = database
        self.previous: dict[int, dict[str, float | int]] = {}
        self.last_change_at: dict[int, float] = {}

    def sample(self, now: float) -> dict[str, Any]:
        if not self.database.is_file():
            return {"state": "DATABASE_MISSING", "session_id": None, "sources": {}}
        try:
            with sqlite3.connect(
                f"file:{self.database}?mode=ro", uri=True, timeout=0.2
            ) as connection:
                session = connection.execute(
                    "SELECT session_id FROM sessions WHERE ended_at IS NULL "
                    "ORDER BY session_id DESC LIMIT 1"
                ).fetchone()
                if session is None:
                    return {"state": "NO_OPEN_SESSION", "session_id": None, "sources": {}}
                session_id = int(session[0])
                raw_rows = connection.execute(
                    "SELECT device_id, COUNT(*), COALESCE(SUM(length(data)),0) "
                    "FROM raw_bytes WHERE session_id=? GROUP BY device_id",
                    (session_id,),
                ).fetchall()
                parsed_rows = connection.execute(
                    "SELECT c.source_id, MAX(r.final_numeric_value) "
                    "FROM columns c JOIN readings r "
                    "ON r.session_id=c.session_id AND r.unique_id=c.unique_id "
                    "WHERE c.session_id=? AND lower(c.title) IN "
                    "('host parse sequence','host_parse_seq') "
                    "AND lower(c.group_title) LIKE '%decoded forensics%' "
                    "GROUP BY c.source_id",
                    (session_id,),
                ).fetchall()
        except sqlite3.Error as error:
            return {
                "state": "QUERY_FAILED",
                "session_id": None,
                "sources": {},
                "error": str(error),
            }

        parsed = {int(source_id): int(value or 0) for source_id, value in parsed_rows}
        sources: dict[str, Any] = {}
        for source_id, raw_count, raw_bytes in raw_rows:
            sid = int(source_id)
            current = {
                "session_id": session_id,
                "sampled_at": now,
                "raw_rows": int(raw_count),
                "raw_bytes": int(raw_bytes),
                "parsed_publications": parsed.get(sid, 0),
            }
            previous = self.previous.get(sid)
            rates = {
                "raw_bytes_per_second": None,
                "raw_rows_per_second": None,
                "parsed_publications_per_second": None,
            }
            if previous and previous.get("session_id") == session_id:
                elapsed = now - float(previous["sampled_at"])
                if elapsed > 0:
                    rates = {
                        "raw_bytes_per_second": round(
                            (current["raw_bytes"] - int(previous["raw_bytes"])) / elapsed,
                            1,
                        ),
                        "raw_rows_per_second": round(
                            (current["raw_rows"] - int(previous["raw_rows"])) / elapsed,
                            2,
                        ),
                        "parsed_publications_per_second": round(
                            (
                                current["parsed_publications"]
                                - int(previous["parsed_publications"])
                            )
                            / elapsed,
                            2,
                        ),
                    }
            if not previous or current["raw_bytes"] != previous.get("raw_bytes"):
                self.last_change_at[sid] = now
            current.update(rates)
            current["last_raw_byte_age_ms"] = round(
                max(0.0, now - self.last_change_at.get(sid, now)) * 1000
            )
            self.previous[sid] = current
            sources[str(sid)] = current
        return {"state": "MEASURED", "session_id": session_id, "sources": sources}


def empty_snapshot(mode: str) -> dict[str, Any]:
    return {
        "schema": "spectrasynq.serial-studio.mission-control.v2",
        "mode": mode,
        "sampled_at_unix_ms": int(time.time() * 1000),
        "bridge": {"api_state": "STARTING", "last_error": None},
        "instrument": {
            "policy": {
                "project_policy": "OBSERVE_ONLY",
                "app_egress_guard": "STOCK_PRO_NOT_PATCHED",
                "tx_witness": "REQUIRED_PENDING",
            },
            "dashboard": {"state": "UNKNOWN"},
            "historian": {"state": "UNKNOWN", "session_id": None, "row_count": None},
            "raw_bytes_per_second": None,
            "raw_bytes_note": "NOT INSTRUMENTED BY THE CURRENT READ API",
        },
        "sources": [],
        "audio_reference": {
            "capability_state": "NOT_INSTRUMENTED",
            "required_for_session": False,
            "mode": "none",
            "state": "NOT_INSTRUMENTED",
            "reason_codes": [],
            "age_ms": None,
            "fresh_in_last_sample": None,
            "threshold_profile": None,
            "capture": None,
            "provenance_state": "unbound",
            "validation_receipt": None,
            "non_claim": "HOST REFERENCE · NOT DEVICE INPUT",
        },
        "ap_validation": {
            "state": "BLOCKED",
            "reason_codes": ["AP_SCORER_RECEIPT_MISSING", "CLOCK_MAP_MISSING"],
            "receipt": None,
        },
        "non_claims": [
            "Raw byte rate is not exposed by the selected read API.",
            "No warning or critical age threshold is applied without a sourced contract.",
            "Host parse sequence is not a device-loss counter.",
        ],
    }


class LiveSampler(threading.Thread):
    def __init__(
        self,
        cache: SnapshotCache,
        api_port: int,
        interval_s: float,
        audio_binding: dict[str, Any] | None = None,
        audio_validation: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(daemon=True, name="serial-studio-read-sampler")
        self.cache = cache
        self.api_port = api_port
        self.interval_s = interval_s
        self.stop_event = threading.Event()
        self.metric_state: dict[str, dict[str, dict[str, Any]]] = {}
        self.audio_binding = audio_binding
        self.audio_validation = audio_validation

    def stop(self) -> None:
        self.stop_event.set()

    def run(self) -> None:
        backoff_s = 0.25
        while not self.stop_event.is_set():
            try:
                with SerialStudioReadClient(port=self.api_port, timeout_s=1.0) as client:
                    self._sample_loop(client)
                backoff_s = 0.25
            except SerialStudioError as error:
                snapshot = self.cache.read()
                snapshot["sampled_at_unix_ms"] = int(time.time() * 1000)
                snapshot["bridge"] = {"api_state": "DOWN", "last_error": str(error)}
                self.cache.replace(snapshot)
                self.stop_event.wait(backoff_s)
                backoff_s = min(backoff_s * 2, 5.0)

    def _sample_loop(self, client: SerialStudioReadClient) -> None:
        sources = client.list_sources()
        project = client.project_status()
        project_title = str(project.get("title") or "")
        ingress_sampler = HistorianIngressSampler(
            client.sessions_db_path(project_title)
        )
        source_configs = {
            str(source.get("sourceId")): client.source_config(str(source.get("sourceId")))
            for source in sources
        }
        next_slow = 0.0
        slow: dict[str, Any] = {}
        while not self.stop_event.is_set():
            now = time.monotonic()
            if now >= next_slow:
                slow = {
                    "dashboard": client.dashboard_status(),
                    "io": client.io_status("0"),
                    "historian": client.sessions_status(),
                    "ingress": ingress_sampler.sample(now),
                }
                next_slow = now + 1.0

            audio_sources = [
                source
                for source in sources
                if source.get("busType") == 3 or str(source.get("sourceId")) == "2"
            ]
            uart_sources = [source for source in sources if source not in audio_sources]
            source_rows = [
                self._sample_source(
                    client,
                    source,
                    source_configs.get(str(source.get("sourceId")), {}),
                    now,
                )
                for source in uart_sources
            ]
            historian = slow.get("historian", {})
            ingress = slow.get("ingress", {})
            ingress_sources = ingress.get("sources", {})
            for source_row in source_rows:
                source_row["ingress"] = ingress_sources.get(
                    str(source_row.get("source_id")), {}
                )
            snapshot = empty_snapshot("live")
            snapshot["bridge"] = {"api_state": "UP", "last_error": None}
            snapshot["instrument"]["dashboard"] = slow.get("dashboard", {})
            snapshot["instrument"]["io"] = slow.get("io", {})
            snapshot["instrument"]["historian"] = {
                "state": "RECORDING" if historian.get("isOpen") else "NOT_RECORDING",
                "export_enabled": historian.get("exportEnabled"),
                "session_id": ingress.get("session_id"),
                "row_count": sum(
                    int(item.get("raw_rows", 0)) for item in ingress_sources.values()
                ),
                "note": "Session identity and ingress counts are measured read-only from the Historian.",
            }
            rates = [
                item.get("raw_bytes_per_second") for item in ingress_sources.values()
            ]
            snapshot["instrument"]["raw_bytes_per_second"] = (
                round(sum(float(rate) for rate in rates), 1)
                if rates and all(isinstance(rate, (int, float)) for rate in rates)
                else None
            )
            snapshot["instrument"]["raw_bytes_note"] = (
                "MEASURED READ-ONLY FROM HISTORIAN RAW_BYTES"
                if ingress.get("state") == "MEASURED"
                else ingress.get("state", "NOT INSTRUMENTED")
            )
            snapshot["sources"] = source_rows
            snapshot["audio_reference"] = self._sample_audio_reference(
                client, audio_sources
            )
            self.cache.replace(snapshot)
            self.stop_event.wait(self.interval_s)

    def _sample_audio_reference(
        self, client: SerialStudioReadClient, sources: list[dict[str, Any]]
    ) -> dict[str, Any]:
        if not sources:
            return empty_snapshot("live")["audio_reference"]
        if len(sources) != 1:
            return {
                **empty_snapshot("live")["audio_reference"],
                "capability_state": "SUPPORTED",
                "required_for_session": True,
                "mode": "live",
                "state": "PROVENANCE_MISMATCH",
                "reason_codes": ["AUDIO_SOURCE_COUNT_MISMATCH"],
                "provenance_state": "mismatch",
            }

        source = sources[0]
        source_id = source.get("sourceId")
        frame = client.latest_frame(str(source_id))
        has_data = bool(frame.get("hasData"))
        age_ms = frame.get("ageMs") if has_data else None
        reason_codes = ["FRESHNESS_THRESHOLD_PROFILE_MISSING"]
        provenance_state = "partial"
        binding_sha = None
        expected_device = None
        if self.audio_binding is None:
            reason_codes.append("AUDIO_SOURCE_BINDING_NOT_LOADED")
        else:
            binding_sha = self.audio_binding.get("binding_sha256")
            expected_device = (
                self.audio_binding.get("source_projection", {})
                .get("connection", {})
                .get("deviceId")
            )
            runtime_connection = source.get("connection")
            if isinstance(runtime_connection, dict) and isinstance(expected_device, dict):
                if runtime_connection.get("deviceId") == expected_device:
                    provenance_state = "verified"
                else:
                    provenance_state = "mismatch"
                    reason_codes.append("AUDIO_SOURCE_RUNTIME_IDENTITY_MISMATCH")
            else:
                reason_codes.append("AUDIO_SOURCE_RUNTIME_IDENTITY_NOT_EXPOSED")

        state = "LIVE_UNVERIFIED" if has_data else "REQUIRED_MISSING"
        if provenance_state == "mismatch":
            state = "PROVENANCE_MISMATCH"
        if not has_data:
            reason_codes.append("AUDIO_SOURCE_NO_DATA")
        return {
            "capability_state": "SUPPORTED",
            "required_for_session": True,
            "mode": "live",
            "state": state,
            "reason_codes": reason_codes,
            "age_ms": age_ms,
            "fresh_in_last_sample": has_data,
            "threshold_profile": None,
            "capture": {
                "source_id": source_id,
                "title": source.get("title"),
                "sequence": frame.get("sequence") if has_data else None,
                "binding_sha256": binding_sha,
                "expected_device_id": expected_device,
                "runtime_device_id": (source.get("connection") or {}).get("deviceId")
                if isinstance(source.get("connection"), dict)
                else None,
                "level_dbfs": None,
                "clip_count": None,
                "drop_count": None,
            },
            "provenance_state": provenance_state,
            "validation_receipt": self.audio_validation,
            "non_claim": "HOST REFERENCE · NOT DEVICE INPUT",
        }

    def _sample_source(
        self,
        client: SerialStudioReadClient,
        source: dict[str, Any],
        source_config: dict[str, Any],
        now: float,
    ) -> dict[str, Any]:
        source_id = str(source.get("sourceId"))
        frame = client.latest_frame(source_id)
        values = frame.get("values") if isinstance(frame.get("values"), list) else []
        sequence = frame.get("sequence")
        state = self.metric_state.setdefault(source_id, {})
        last_sequence = state.get("_meta", {}).get("sequence")
        is_new = bool(frame.get("hasData")) and sequence != last_sequence

        if is_new:
            mask = _number_at(values, 21, 0)
            record_kind = _number_at(values, 20, None)
            frame_age_ms = frame.get("ageMs") if isinstance(frame.get("ageMs"), (int, float)) else 0
            observed_at = now - max(0.0, float(frame_age_ms)) / 1000.0
            for slot, (name, unit) in METRICS.items():
                value = _number_at(values, slot, None)
                if value is not None:
                    previous = state.setdefault(name, {})
                    previous["value"] = value
                    previous["unit"] = unit
                    previous["record_kind"] = record_kind
                    previous["fresh_in_last_frame"] = bool(int(mask) & (1 << (slot - 1)))
                    if previous["fresh_in_last_frame"]:
                        previous["observed_at"] = observed_at
            state["_meta"] = {"sequence": sequence}

        metrics: dict[str, Any] = {}
        for name, metric in state.items():
            if name == "_meta":
                continue
            exported = {key: value for key, value in metric.items() if key != "observed_at"}
            observed_at = metric.get("observed_at")
            exported["age_ms"] = (
                round(max(0.0, now - observed_at) * 1000)
                if isinstance(observed_at, (int, float))
                else None
            )
            metrics[name] = exported

        has_data = bool(frame.get("hasData"))
        connection = source_config.get("connection")
        device_id = connection.get("deviceId") if isinstance(connection, dict) else None
        serial = device_id.get("serial") if isinstance(device_id, dict) else None
        return {
            "source_id": source.get("sourceId"),
            "title": source.get("title", f"Source {source_id}"),
            "identity": serial or source.get("title", f"Source {source_id}"),
            "device_id": device_id if isinstance(device_id, dict) else None,
            "rx": {
                "state": "HAS_DATA_UNCLASSIFIED" if has_data else "NO_DATA",
                "has_data": has_data,
                "age_ms": frame.get("ageMs") if has_data else None,
                "sequence": sequence if has_data else None,
                "threshold_profile": None,
            },
            "metrics": metrics,
        }


def _number_at(values: list[Any], one_based_slot: int, default: Any) -> Any:
    index = one_based_slot - 1
    if not (0 <= index < len(values)):
        return default
    value = values[index]
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, (int, float)):
        return value if math.isfinite(float(value)) else default
    try:
        parsed = float(value)
        return parsed if math.isfinite(parsed) else default
    except (TypeError, ValueError):
        return default


def _canonical_sha(value: Any) -> str:
    payload = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def load_audio_binding(path: Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    value = json.loads(path.read_text(encoding="utf-8"))
    if value.get("schema") != "spectrasynq.serial-studio.audio-source-binding.v1":
        raise RuntimeError("Audio source binding schema mismatch")
    source = value.get("source_projection")
    if not isinstance(source, dict):
        raise RuntimeError("Audio source binding has no source projection")
    if value.get("source_projection_sha256") != _canonical_sha(source):
        raise RuntimeError("Audio source binding projection hash mismatch")
    return {**value, "binding_sha256": _hash_file(path)}


def load_audio_validation(path: Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    value = json.loads(path.read_text(encoding="utf-8"))
    if value.get("schema") != AUDIO_REFERENCE_SCHEMA:
        raise RuntimeError("Audio Reference validation receipt schema mismatch")
    if value.get("integrity_status") != "VALID":
        raise RuntimeError("Audio Reference validation receipt is not VALID")
    score = value.get("score") if isinstance(value.get("score"), dict) else {}
    return {
        "receipt_sha256": _hash_file(path),
        "integrity_status": "VALID",
        "score_status": score.get("status"),
        "profile_id": score.get("profile_id"),
        "profile_sha256": score.get("profile_sha256"),
        "capture_sha256": (value.get("capture") or {}).get("sha256"),
        "reference_sha256": (value.get("reference") or {}).get("sha256"),
        "time_authority": value.get("time_authority"),
        "claims": value.get("claims"),
    }


class MissionControlHandler(BaseHTTPRequestHandler):
    server_version = "K1MissionControl/1"

    def do_GET(self) -> None:  # noqa: N802
        if not self._request_is_local():
            self.send_error(HTTPStatus.FORBIDDEN)
            return
        path = urlsplit(self.path).path
        if path == "/api/v1/snapshot":
            self._send_json(self.server.cache.read())  # type: ignore[attr-defined]
            return
        if path in STATIC_ROUTES:
            self._send_file(HERE / STATIC_ROUTES[path])
            return
        asset = self.server.font_assets.get(path)  # type: ignore[attr-defined]
        if asset:
            self._send_file(asset["resolved_path"], content_type=asset["mime"])
            return
        self.send_error(HTTPStatus.NOT_FOUND)

    def do_HEAD(self) -> None:  # noqa: N802
        self.do_GET()

    def do_POST(self) -> None:  # noqa: N802
        self.send_error(HTTPStatus.METHOD_NOT_ALLOWED)

    do_PUT = do_POST
    do_PATCH = do_POST
    do_DELETE = do_POST
    do_OPTIONS = do_POST

    def _request_is_local(self) -> bool:
        allowed_hosts = {f"127.0.0.1:{self.server.server_port}", "127.0.0.1"}  # type: ignore[attr-defined]
        if self.headers.get("Host") not in allowed_hosts:
            return False
        origin = self.headers.get("Origin")
        return origin in {None, f"http://127.0.0.1:{self.server.server_port}"}  # type: ignore[attr-defined]

    def _security_headers(self) -> None:
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; font-src 'self'; connect-src 'self'; img-src 'self' data:; object-src 'none'; frame-ancestors 'self'")
        self.send_header("Cross-Origin-Resource-Policy", "same-origin")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("X-Content-Type-Options", "nosniff")

    def _send_json(self, value: Any) -> None:
        payload = json.dumps(value, separators=(",", ":"), allow_nan=False).encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self._security_headers()
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(payload)

    def _send_file(self, path: Path, content_type: str | None = None) -> None:
        if not path.is_file():
            self.send_error(HTTPStatus.SERVICE_UNAVAILABLE, "Mission Control asset unavailable")
            return
        payload = path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type or mimetypes.guess_type(path.name)[0] or "application/octet-stream")
        self.send_header("Content-Length", str(len(payload)))
        self._security_headers()
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(payload)

    def log_message(self, fmt: str, *args: object) -> None:
        return

    def log_error(self, fmt: str, *args: object) -> None:
        print(f"MISSION_CONTROL_HTTP_ERROR {self.client_address[0]} {fmt % args}")


class MissionControlServer(ThreadingHTTPServer):
    allow_reuse_address = True

    def __init__(
        self,
        address: tuple[str, int],
        cache: SnapshotCache,
        font_assets: dict[str, dict[str, Any]],
    ) -> None:
        super().__init__(address, MissionControlHandler)
        self.cache = cache
        self.font_assets = font_assets


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=PORT)
    parser.add_argument("--api-port", type=int, default=7777)
    parser.add_argument("--fixture", type=Path)
    parser.add_argument("--audio-source-binding", type=Path)
    parser.add_argument("--audio-validation-receipt", type=Path)
    parser.add_argument("--sample-interval-ms", type=int, default=250)
    args = parser.parse_args()

    audio_binding = load_audio_binding(args.audio_source_binding)
    audio_validation = load_audio_validation(args.audio_validation_receipt)

    if args.fixture:
        snapshot = json.loads(args.fixture.read_text(encoding="utf-8"))
        snapshot["mode"] = "fixture"
        sampler = None
    else:
        snapshot = empty_snapshot("live")
        sampler = LiveSampler(
            SnapshotCache(snapshot),
            args.api_port,
            max(0.05, args.sample_interval_ms / 1000),
            audio_binding,
            audio_validation,
        )

    cache = sampler.cache if sampler else SnapshotCache(snapshot)
    fonts = load_font_assets()
    server = MissionControlServer((HOST, args.port), cache, fonts)
    if sampler:
        sampler.start()
    print(f"MISSION_CONTROL_LISTEN=http://{HOST}:{args.port} MODE={snapshot['mode']}")
    try:
        server.serve_forever(poll_interval=0.25)
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        if sampler:
            sampler.stop()
            sampler.join(timeout=2)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
