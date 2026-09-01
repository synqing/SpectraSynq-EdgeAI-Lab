"""Fail-closed evidence bundle validator tests."""

from __future__ import annotations

import importlib.util
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools/serial-studio/validate_bundle.py"
SPEC = importlib.util.spec_from_file_location("serial_studio_bundle", MODULE_PATH)
assert SPEC and SPEC.loader
bundle = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(bundle)


def _entry(root: Path, role: str, name: str, payload: bytes) -> dict:
    path = root / name
    path.write_bytes(payload)
    return {"role": role, "path": name, "sha256": bundle.sha256_file(path), "bytes": len(payload)}


def _index(tmp_path: Path) -> Path:
    snapshot = _entry(tmp_path, "historian_snapshot", "session.sqlite", b"sqlite")
    receipt = _entry(tmp_path, "instrument_receipt", "instrument.json", b"receipt")
    profile = _entry(tmp_path, "scoring_profile", "score.json", b"score")
    value = {
        "schema": "k1.evidence-bundle.v1",
        "session_id": "fixture-1",
        "capture_profile_id": "REPLAY_FORENSICS",
        "status": "VALID",
        "reasons": [],
        "snapshot_sha256": snapshot["sha256"],
        "instrument_receipt_sha256": receipt["sha256"],
        "scoring_profile_id": "fixture-score-v1",
        "scoring_profile_sha256": profile["sha256"],
        "files": [snapshot, receipt, profile],
    }
    path = tmp_path / "bundle.json"
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


def test_complete_bundle_passes(tmp_path: Path) -> None:
    assert bundle.validate(_index(tmp_path)) == []


def test_tampered_file_fails(tmp_path: Path) -> None:
    index = _index(tmp_path)
    (tmp_path / "session.sqlite").write_bytes(b"tampered")
    assert "historian_snapshot SHA-256 mismatch" in bundle.validate(index)


def test_path_escape_and_false_validity_fail(tmp_path: Path) -> None:
    index = _index(tmp_path)
    value = json.loads(index.read_text(encoding="utf-8"))
    value["reasons"] = ["known acquisition fault"]
    value["files"][0]["path"] = "../outside.sqlite"
    index.write_text(json.dumps(value), encoding="utf-8")
    errors = bundle.validate(index)
    assert "VALID bundle must have no rejection reasons" in errors
    assert "historian_snapshot path escapes the bundle root" in errors


def _v2_index(tmp_path: Path, profile_id: str, entries: list[dict]) -> Path:
    profiles = ROOT / "tools/serial-studio/profiles/capture-profiles.v1.json"
    value = {
        "schema": "k1.evidence-bundle.v2",
        "session_id": "fixture-v2",
        "capture_profile_id": profile_id,
        "capture_profile_catalogue_sha256": hashlib.sha256(profiles.read_bytes()).hexdigest(),
        "status": "VALID",
        "reasons": [],
        "bindings": {entry["role"]: entry["sha256"] for entry in entries},
        "scoring_profile_id": None,
        "scoring_profile_sha256": None,
        "files": entries,
    }
    path = tmp_path / "bundle-v2.json"
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


def test_v2_exclusive_probe_does_not_require_serial_studio(tmp_path: Path) -> None:
    probe = _entry(tmp_path, "exclusive_probe_receipt", "probe.json", b"probe")
    index = _v2_index(tmp_path, "EXCLUSIVE_PROBE", [probe])

    assert bundle.validate(index) == []


def test_v2_passive_uart_requires_serial_studio_evidence(tmp_path: Path) -> None:
    unrelated = _entry(tmp_path, "scoring_profile", "score.json", b"score")
    index = _v2_index(tmp_path, "PASSIVE_DUAL_UART", [unrelated])
    value = json.loads(index.read_text(encoding="utf-8"))
    value["scoring_profile_id"] = "fixture"
    value["scoring_profile_sha256"] = unrelated["sha256"]
    index.write_text(json.dumps(value), encoding="utf-8")
    errors = bundle.validate(index)

    assert "profile PASSIVE_DUAL_UART requires exactly one historian_snapshot file" in errors
    assert "profile PASSIVE_DUAL_UART requires exactly one instrument_receipt file" in errors


def test_v2_audio_profile_cannot_false_promote_while_unbound(tmp_path: Path) -> None:
    snapshot = _entry(tmp_path, "historian_snapshot", "session.sqlite", b"sqlite")
    instrument = _entry(tmp_path, "instrument_receipt", "instrument.json", b"instrument")
    binding = _entry(tmp_path, "audio_source_binding", "binding.json", b"binding")
    audio_receipt_payload = json.dumps(
        {
            "schema": "spectrasynq.audio-reference-validation.v1",
            "integrity_status": "VALID",
            "authority": "HOST_AUDIO_REFERENCE",
            "time_authority": "HOST_AUDIO_REFERENCE_TIME",
            "claims": {
                "k1_capture_pipeline_validated": False,
                "acoustic_delivery_validated": False,
                "device_time_alignment_validated": False,
                "product_verdict": False,
            },
        }
    ).encode()
    audio = _entry(
        tmp_path,
        "audio_reference_validation",
        "audio-validation.json",
        audio_receipt_payload,
    )
    index = _v2_index(
        tmp_path,
        "PASSIVE_DUAL_UART_AUDIO_REF",
        [snapshot, instrument, binding, audio],
    )
    errors = bundle.validate(index)

    assert (
        "capture profile PASSIVE_DUAL_UART_AUDIO_REF is not admitted: BLOCKED_UNBOUND"
        in errors
    )


def test_v2_profile_catalogue_and_bindings_are_hash_bound(tmp_path: Path) -> None:
    probe = _entry(tmp_path, "exclusive_probe_receipt", "probe.json", b"probe")
    index = _v2_index(tmp_path, "EXCLUSIVE_PROBE", [probe])
    value = json.loads(index.read_text(encoding="utf-8"))
    value["capture_profile_catalogue_sha256"] = "0" * 64
    value["bindings"]["exclusive_probe_receipt"] = "f" * 64
    index.write_text(json.dumps(value), encoding="utf-8")
    errors = bundle.validate(index)

    assert "capture_profile_catalogue_sha256 does not bind the profile catalogue" in errors
    assert any(
        error.startswith("bindings.exclusive_probe_receipt does not bind")
        for error in errors
    )
