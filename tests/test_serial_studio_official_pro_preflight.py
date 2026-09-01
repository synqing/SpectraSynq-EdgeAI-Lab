from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools/serial-studio/official_pro_audio_preflight.py"


def _module():
    spec = importlib.util.spec_from_file_location("official_pro_audio_preflight", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _snapshot(*, devices: list[str] | None = None) -> dict[str, object]:
    commands = [
        "io.audio.getConfig",
        "io.audio.listInputDevices",
        "io.audio.listInputFormats",
        "io.audio.listOutputDevices",
        "io.audio.listOutputFormats",
        "io.audio.listSampleRates",
        "io.audio.setInputChannelConfig",
        "io.audio.setInputDevice",
        "io.audio.setInputSampleFormat",
        "io.audio.setOutputChannelConfig",
        "io.audio.setOutputDevice",
        "io.audio.setOutputSampleFormat",
        "io.audio.setSampleRate",
    ]
    return {
        "api.getCommands": {"commands": [{"name": name} for name in commands]},
        "io.audio.listInputDevices": {
            "devices": devices or ["MacBook Pro Microphone", "BlackHole 2ch"],
            "selectedIndex": 1,
        },
        "io.audio.listSampleRates": {
            "sampleRates": ["44100", "48000"],
            "selectedIndex": 1,
        },
        "io.audio.listInputFormats": {
            "formats": ["Float 32-bit"],
            "selectedIndex": 0,
        },
        "io.audio.getConfig": {
            "normalization": False,
            "selectedInputDevice": 1,
            "selectedSampleRate": 1,
            "selectedInputSampleFormat": 0,
            "selectedInputChannelConfig": 0,
        },
    }


def _binding() -> dict[str, object]:
    return {
        "schema": "spectrasynq.serial-studio.audio-source-binding.v1",
        "profile_id": "PASSIVE_DUAL_UART_AUDIO_REF",
        "source_projection": {
            "sourceId": 2,
            "busType": 3,
            "connection": {
                "inputDevice": 1,
                "sampleRate": 1,
                "normalization": False,
                "inputFormat": 0,
                "inputChannels": 0,
                "deviceId": {
                    "inputDeviceName": "BlackHole 2ch",
                    "sampleRateValue": 48000,
                    "formatName": "Float 32-bit",
                    "channelCount": 2,
                },
            },
        },
    }


def test_exact_official_pro_binding_passes() -> None:
    module = _module()
    result = module.evaluate_audio_binding(_snapshot(), _binding())
    assert result["status"] == "PASS"
    assert result["reason_codes"] == []
    assert result["observed"]["input_device_name"] == "BlackHole 2ch"
    assert result["observed"]["channel_count"] == 2


def test_device_identity_is_exact_and_index_is_not_authority() -> None:
    module = _module()
    absent = module.evaluate_audio_binding(
        _snapshot(devices=["BlackHole 16ch", "MacBook Pro Microphone"]), _binding()
    )
    assert absent["status"] == "BLOCKED"
    assert "EXPECTED_INPUT_DEVICE_ABSENT" in absent["reason_codes"]

    duplicate = module.evaluate_audio_binding(
        _snapshot(devices=["BlackHole 2ch", "BlackHole 2ch"]), _binding()
    )
    assert "EXPECTED_INPUT_DEVICE_AMBIGUOUS" in duplicate["reason_codes"]


def test_selected_rate_format_and_saved_channel_contract_must_match() -> None:
    module = _module()
    snapshot = _snapshot()
    snapshot["io.audio.listSampleRates"]["selectedIndex"] = 0
    result = module.evaluate_audio_binding(snapshot, _binding())
    assert "EXPECTED_SAMPLE_RATE_NOT_SELECTED" in result["reason_codes"]

    snapshot = _snapshot()
    binding = _binding()
    binding["source_projection"]["connection"]["deviceId"]["channelCount"] = 1
    result = module.evaluate_audio_binding(snapshot, binding)
    assert "EXPECTED_CHANNEL_COUNT_MISMATCH" in result["reason_codes"]


def test_missing_saved_binding_fails_closed_on_unobservable_fields() -> None:
    module = _module()
    result = module.evaluate_audio_binding(_snapshot(), None)
    assert result["status"] == "BLOCKED"
    assert "AUDIO_SOURCE_BINDING_MISSING" in result["reason_codes"]
    assert "CHANNEL_COUNT_UNPROVEN" in result["reason_codes"]


def test_client_allowlist_contains_no_mutating_audio_commands() -> None:
    module = _module()
    assert module.READ_ONLY_COMMANDS == (
        "api.getCommands",
        "io.audio.listInputDevices",
        "io.audio.listSampleRates",
        "io.audio.listInputFormats",
        "io.audio.getConfig",
    )
    assert all(".set" not in command for command in module.READ_ONLY_COMMANDS)


def test_receipt_never_serialises_api_token() -> None:
    module = _module()
    receipt = module.build_receipt(
        runtime={
            "bundle": "/Applications/Serial Studio Pro.app",
            "version": "4.0.3",
            "binary_path": "/Applications/Serial Studio Pro.app/Contents/MacOS/Serial-Studio-Pro",
            "binary_sha256": "a" * 64,
        },
        snapshot=_snapshot(),
        binding=_binding(),
        observed_at="2026-09-01T00:00:00Z",
    )
    serialised = json.dumps(receipt)
    assert "token" not in serialised.lower()
    assert receipt["application_policy"]["app_egress_guard"] == "STOCK_PRO_NOT_PATCHED"
    assert receipt["application_policy"]["tx_witness"] == "REQUIRED_PENDING"

    schema = json.loads(
        (ROOT / "tools/serial-studio/schemas/official-pro-audio-preflight.schema.json").read_text(
            encoding="utf-8"
        )
    )
    jsonschema.Draft202012Validator(schema).validate(receipt)
