from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "tools/serial-studio/projects/K1-Dual-UART-Observability-v2.ssproj"
CAPTURE = ROOT / "tools/serial-studio/capture_audio_source_binding.py"
GENERATE = ROOT / "tools/serial-studio/generate_audio_profile.py"
LINTER = ROOT / "tools/serial-studio/lint_audio_profile.py"


def _source() -> dict[str, object]:
    return {
        "busType": 3,
        "checksum": "",
        "checksumAlgorithm": "",
        "connection": {
            "inputDevice": 1,
            "sampleRate": 4,
            "normalization": False,
            "inputFormat": 1,
            "inputChannels": 1,
            "deviceId": {
                "inputDeviceName": "Deterministic Test Loopback",
                "sampleRateValue": 48000,
                "formatName": "Signed 16-bit",
                "channelCount": 2,
            },
        },
        "decoder": 0,
        "decoderMethod": 0,
        "frameDetection": 0,
        "frameEnd": "\n",
        "frameParserCode": "",
        "frameParserParams": {
            "quoteChar": "",
            "separator": ",",
            "skipEmpty": False,
            "trimFields": False,
        },
        "frameParserTemplate": "delimited",
        "frameStart": "$",
        "hexadecimalDelimiters": False,
        "sourceId": 2,
        "title": "Host Audio Reference",
    }


def _binding(tmp_path: Path) -> tuple[Path, Path]:
    project = json.loads(BASE.read_text(encoding="utf-8"))
    project["sources"].append(_source())
    saved = tmp_path / "pro-saved.ssproj"
    saved.write_text(json.dumps(project), encoding="utf-8")
    binding = tmp_path / "binding.json"
    result = subprocess.run(
        [sys.executable, str(CAPTURE), str(saved), "--output", str(binding)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    return binding, saved


def test_audio_profile_is_separate_and_base_generation_is_unchanged(tmp_path: Path) -> None:
    before = hashlib.sha256(BASE.read_bytes()).hexdigest()
    binding, _ = _binding(tmp_path)
    output = tmp_path / "audio.ssproj"
    generated = subprocess.run(
        [sys.executable, str(GENERATE), "--binding", str(binding), "--output", str(output)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert generated.returncode == 0, generated.stdout + generated.stderr
    linted = subprocess.run(
        [sys.executable, str(LINTER), str(output), "--binding", str(binding)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert linted.returncode == 0, linted.stdout + linted.stderr
    assert hashlib.sha256(BASE.read_bytes()).hexdigest() == before
    project = json.loads(output.read_text(encoding="utf-8"))
    assert {item["sourceId"] for item in project["sources"]} == {0, 1, 2}
    workspaces = {item["title"]: item for item in project["workspaces"]}
    assert set(workspaces) >= {"Mission Control", "Audio Reference", "AP Validation"}
    assert len(workspaces["Mission Control"]["widgetRefs"]) == 1


def test_audio_binding_rejects_normalisation_and_missing_stable_identity(tmp_path: Path) -> None:
    project = json.loads(BASE.read_text(encoding="utf-8"))
    source = _source()
    source["connection"]["normalization"] = True  # type: ignore[index]
    project["sources"].append(source)
    saved = tmp_path / "bad-normalisation.ssproj"
    saved.write_text(json.dumps(project), encoding="utf-8")
    output = tmp_path / "binding.json"
    result = subprocess.run(
        [sys.executable, str(CAPTURE), str(saved), "--output", str(output)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 1
    assert "NORMALIZATION_MUST_BE_EXPLICITLY_FALSE" in result.stdout
    assert not output.exists()

    source["connection"]["normalization"] = False  # type: ignore[index]
    del source["connection"]["deviceId"]["inputDeviceName"]  # type: ignore[index]
    saved.write_text(json.dumps(project), encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(CAPTURE), str(saved), "--output", str(output)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 1
    assert "DEVICE_ID_INVALID_inputDeviceName" in result.stdout


def test_audio_linter_rejects_uart_drift_and_mission_control_spectacle(tmp_path: Path) -> None:
    binding, _ = _binding(tmp_path)
    output = tmp_path / "audio.ssproj"
    subprocess.run(
        [sys.executable, str(GENERATE), "--binding", str(binding), "--output", str(output)],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    project = json.loads(output.read_text(encoding="utf-8"))
    project["sources"][0]["title"] = "drift"
    mission = next(item for item in project["workspaces"] if item["title"] == "Mission Control")
    mission["widgetRefs"].append(copy.deepcopy(mission["widgetRefs"][0]))
    output.write_text(json.dumps(project), encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(LINTER), str(output), "--binding", str(binding)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 1
    assert "UART source 0" in result.stdout
    assert "Mission Control must remain one Web View" in result.stdout


def test_capture_profiles_keep_audio_optional_and_unbound() -> None:
    catalogue = json.loads(
        (ROOT / "tools/serial-studio/profiles/capture-profiles.v1.json").read_text(
            encoding="utf-8"
        )
    )["profiles"]
    assert catalogue["PASSIVE_DUAL_UART"]["required_source_ids"] == [0, 1]
    audio = catalogue["PASSIVE_DUAL_UART_AUDIO_REF"]
    assert audio["status"] == "BLOCKED_UNBOUND"
    assert audio["required_source_ids"] == [0, 1, 2]
    assert audio["audio_source_contract"]["normalization"] is False
    assert audio["audio_source_contract"]["edition"] == "OFFICIAL_PRO"
    assert audio["audio_source_contract"]["input_device_name"] == "BlackHole 2ch"
    assert audio["audio_source_contract"]["sample_rate_hz"] == 48000
    assert audio["application_egress_guard"] == "STOCK_PRO_NOT_PATCHED"
    assert audio["independent_tx_witness"] == "REQUIRED_ZERO_BYTES"
    assert audio["patched_pro_hardening"] == "OPTIONAL_NOT_CRITICAL_PATH"
    assert "PRO_RUNTIME_NOT_VALIDATED" not in audio["blockers"]
    assert audio["playback_owner"] == "EXTERNAL_NOT_SERIAL_STUDIO"
