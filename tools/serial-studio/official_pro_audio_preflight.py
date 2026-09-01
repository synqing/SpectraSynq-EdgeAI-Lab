#!/usr/bin/env python3
"""Read-only fail-closed preflight for official Serial Studio Pro Audio Source C.

The client has a fixed getter-only command surface.  It never selects a device,
changes an Audio setting, connects an I/O source, or writes to a DUT.  Indices
are recorded only after exact names/values are resolved and are never treated as
stable identity.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import plistlib
import socket
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "spectrasynq.serial-studio.official-pro-audio-preflight.v1"
EXPECTED_VERSION = "4.0.3"
EXPECTED_DEVICE = "BlackHole 2ch"
EXPECTED_RATE_HZ = 48_000
EXPECTED_FORMAT = "Float 32-bit"
EXPECTED_CHANNEL_COUNT = 2
DEFAULT_APP = Path("/Applications/Serial Studio Pro.app")
DEFAULT_OUTPUT = Path(__file__).resolve().parent / "projects/official-pro-audio-preflight.v1.json"
API_ENDPOINT = ("127.0.0.1", 7777)

# Load-bearing allow-list: this tool cannot call Audio setters or I/O lifecycle commands.
READ_ONLY_COMMANDS = (
    "api.getCommands",
    "io.audio.listInputDevices",
    "io.audio.listSampleRates",
    "io.audio.listInputFormats",
    "io.audio.getConfig",
)

REQUIRED_AUDIO_GETTERS = {
    "io.audio.getConfig",
    "io.audio.listInputDevices",
    "io.audio.listInputFormats",
    "io.audio.listSampleRates",
}


class PreflightError(ValueError):
    pass


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def inspect_runtime(app: Path) -> dict[str, str]:
    plist_path = app / "Contents/Info.plist"
    if not plist_path.is_file():
        raise PreflightError(f"OFFICIAL_PRO_INFO_PLIST_MISSING:{plist_path}")
    with plist_path.open("rb") as handle:
        plist = plistlib.load(handle)
    executable = str(plist.get("CFBundleExecutable") or "")
    binary = app / "Contents/MacOS" / executable
    if not executable or not binary.is_file():
        raise PreflightError(f"OFFICIAL_PRO_EXECUTABLE_MISSING:{binary}")
    return {
        "bundle": str(app),
        "version": str(plist.get("CFBundleShortVersionString") or ""),
        "build_version": str(plist.get("CFBundleVersion") or ""),
        "bundle_identifier": str(plist.get("CFBundleIdentifier") or ""),
        "binary_path": str(binary),
        "binary_sha256": sha256_file(binary),
    }


def _read_json_line(stream: Any) -> dict[str, Any]:
    line = stream.readline()
    if not line:
        raise PreflightError("OFFICIAL_PRO_API_CLOSED")
    try:
        value = json.loads(line)
    except json.JSONDecodeError as error:
        raise PreflightError("OFFICIAL_PRO_API_MALFORMED_JSON") from error
    if not isinstance(value, dict):
        raise PreflightError("OFFICIAL_PRO_API_NON_OBJECT")
    return value


def query_runtime(timeout_s: float = 3.0) -> dict[str, Any]:
    pending: dict[str, str] = {}
    results: dict[str, Any] = {}
    try:
        with socket.create_connection(API_ENDPOINT, timeout=timeout_s) as connection:
            connection.settimeout(timeout_s)
            stream = connection.makefile("rwb", buffering=0)
            for index, command in enumerate(READ_ONLY_COMMANDS, 1):
                request_id = f"k1-audio-preflight-{index}"
                pending[request_id] = command
                request = {"type": "command", "id": request_id, "command": command}
                stream.write((json.dumps(request, separators=(",", ":")) + "\n").encode())

            while pending:
                response = _read_json_line(stream)
                if response.get("type") != "response":
                    continue
                request_id = response.get("id")
                if request_id not in pending:
                    continue
                command = pending.pop(str(request_id))
                if response.get("success") is not True:
                    raise PreflightError(f"OFFICIAL_PRO_API_COMMAND_FAILED:{command}")
                result = response.get("result")
                if not isinstance(result, dict):
                    raise PreflightError(f"OFFICIAL_PRO_API_RESULT_INVALID:{command}")
                results[command] = result
    except (OSError, TimeoutError) as error:
        raise PreflightError("OFFICIAL_PRO_API_UNREACHABLE") from error
    return results


def _selected(values: list[Any], index: Any) -> Any | None:
    if not isinstance(index, int) or index < 0 or index >= len(values):
        return None
    return values[index]


def _binding_connection(binding: dict[str, Any] | None) -> dict[str, Any] | None:
    if binding is None:
        return None
    if binding.get("schema") != "spectrasynq.serial-studio.audio-source-binding.v1":
        raise PreflightError("AUDIO_SOURCE_BINDING_SCHEMA_INVALID")
    source = binding.get("source_projection")
    if not isinstance(source, dict) or source.get("sourceId") != 2 or source.get("busType") != 3:
        raise PreflightError("AUDIO_SOURCE_BINDING_SOURCE_INVALID")
    connection = source.get("connection")
    if not isinstance(connection, dict):
        raise PreflightError("AUDIO_SOURCE_BINDING_CONNECTION_INVALID")
    return connection


def evaluate_audio_binding(
    snapshot: dict[str, Any], binding: dict[str, Any] | None
) -> dict[str, Any]:
    reasons: list[str] = []
    command_result = snapshot.get("api.getCommands") or {}
    registered = {
        item.get("name")
        for item in command_result.get("commands", [])
        if isinstance(item, dict)
    }
    if not REQUIRED_AUDIO_GETTERS.issubset(registered):
        reasons.append("OFFICIAL_PRO_AUDIO_GETTERS_MISSING")

    device_result = snapshot.get("io.audio.listInputDevices") or {}
    rate_result = snapshot.get("io.audio.listSampleRates") or {}
    format_result = snapshot.get("io.audio.listInputFormats") or {}
    config = snapshot.get("io.audio.getConfig") or {}
    devices = device_result.get("devices") if isinstance(device_result.get("devices"), list) else []
    rates = rate_result.get("sampleRates") if isinstance(rate_result.get("sampleRates"), list) else []
    formats = format_result.get("formats") if isinstance(format_result.get("formats"), list) else []

    matches = [index for index, name in enumerate(devices) if name == EXPECTED_DEVICE]
    if not matches:
        reasons.append("EXPECTED_INPUT_DEVICE_ABSENT")
        expected_device_index = None
    elif len(matches) != 1:
        reasons.append("EXPECTED_INPUT_DEVICE_AMBIGUOUS")
        expected_device_index = None
    else:
        expected_device_index = matches[0]

    selected_device = _selected(devices, device_result.get("selectedIndex"))
    if expected_device_index is not None and selected_device != EXPECTED_DEVICE:
        reasons.append("EXPECTED_INPUT_DEVICE_NOT_SELECTED")
    if config.get("selectedInputDevice") != device_result.get("selectedIndex"):
        reasons.append("INPUT_DEVICE_INDEX_INCONSISTENT")

    rate_strings = [str(value) for value in rates]
    expected_rate_text = str(EXPECTED_RATE_HZ)
    rate_matches = [index for index, value in enumerate(rate_strings) if value == expected_rate_text]
    if len(rate_matches) != 1:
        reasons.append("EXPECTED_SAMPLE_RATE_UNAVAILABLE")
    selected_rate = _selected(rate_strings, rate_result.get("selectedIndex"))
    if selected_rate != expected_rate_text:
        reasons.append("EXPECTED_SAMPLE_RATE_NOT_SELECTED")
    if config.get("selectedSampleRate") != rate_result.get("selectedIndex"):
        reasons.append("SAMPLE_RATE_INDEX_INCONSISTENT")

    format_matches = [index for index, value in enumerate(formats) if value == EXPECTED_FORMAT]
    if len(format_matches) != 1:
        reasons.append("EXPECTED_INPUT_FORMAT_UNAVAILABLE")
    selected_format = _selected(formats, format_result.get("selectedIndex"))
    if selected_format != EXPECTED_FORMAT:
        reasons.append("EXPECTED_INPUT_FORMAT_NOT_SELECTED")
    if config.get("selectedInputSampleFormat") != format_result.get("selectedIndex"):
        reasons.append("INPUT_FORMAT_INDEX_INCONSISTENT")

    connection = _binding_connection(binding)
    channel_count: int | None = None
    if connection is None:
        reasons.extend(["AUDIO_SOURCE_BINDING_MISSING", "CHANNEL_COUNT_UNPROVEN"])
    else:
        device_id = connection.get("deviceId")
        if not isinstance(device_id, dict):
            reasons.append("AUDIO_SOURCE_BINDING_DEVICE_ID_INVALID")
        else:
            channel_count = device_id.get("channelCount")
            expected_pairs = (
                ("inputDeviceName", EXPECTED_DEVICE, "EXPECTED_INPUT_DEVICE_BINDING_MISMATCH"),
                ("sampleRateValue", EXPECTED_RATE_HZ, "EXPECTED_SAMPLE_RATE_BINDING_MISMATCH"),
                ("formatName", EXPECTED_FORMAT, "EXPECTED_INPUT_FORMAT_BINDING_MISMATCH"),
                ("channelCount", EXPECTED_CHANNEL_COUNT, "EXPECTED_CHANNEL_COUNT_MISMATCH"),
            )
            for key, expected, reason in expected_pairs:
                if device_id.get(key) != expected:
                    reasons.append(reason)
        if connection.get("normalization") is not False:
            reasons.append("NORMALIZATION_MUST_BE_FALSE")
        binding_indices = (
            ("inputDevice", device_result.get("selectedIndex"), "INPUT_DEVICE_BINDING_INDEX_DRIFT"),
            ("sampleRate", rate_result.get("selectedIndex"), "SAMPLE_RATE_BINDING_INDEX_DRIFT"),
            ("inputFormat", format_result.get("selectedIndex"), "INPUT_FORMAT_BINDING_INDEX_DRIFT"),
            (
                "inputChannels",
                config.get("selectedInputChannelConfig"),
                "INPUT_CHANNEL_BINDING_INDEX_DRIFT",
            ),
        )
        for key, observed_index, reason in binding_indices:
            if connection.get(key) != observed_index:
                reasons.append(reason)

    return {
        "status": "PASS" if not reasons else "BLOCKED",
        "reason_codes": sorted(set(reasons)),
        "expected": {
            "input_device_name": EXPECTED_DEVICE,
            "sample_rate_hz": EXPECTED_RATE_HZ,
            "input_format": EXPECTED_FORMAT,
            "channel_count": EXPECTED_CHANNEL_COUNT,
            "normalization": False,
        },
        "observed": {
            "input_devices": devices,
            "input_device_name": selected_device,
            "input_device_index": device_result.get("selectedIndex"),
            "sample_rates": rate_strings,
            "sample_rate_hz": int(selected_rate) if selected_rate and selected_rate.isdigit() else None,
            "sample_rate_index": rate_result.get("selectedIndex"),
            "input_formats": formats,
            "input_format": selected_format,
            "input_format_index": format_result.get("selectedIndex"),
            "input_channel_config_index": config.get("selectedInputChannelConfig"),
            "channel_count": channel_count,
            "normalization": connection.get("normalization") if connection else None,
        },
    }


def build_receipt(
    *,
    runtime: dict[str, Any],
    snapshot: dict[str, Any],
    binding: dict[str, Any] | None,
    observed_at: str,
) -> dict[str, Any]:
    audio = evaluate_audio_binding(snapshot, binding)
    runtime_reasons: list[str] = []
    if runtime.get("version") != EXPECTED_VERSION:
        runtime_reasons.append("OFFICIAL_PRO_VERSION_MISMATCH")
    binary_sha = runtime.get("binary_sha256")
    if not isinstance(binary_sha, str) or len(binary_sha) != 64:
        runtime_reasons.append("OFFICIAL_PRO_BINARY_IDENTITY_INVALID")
    runtime_status = "PASS" if not runtime_reasons else "BLOCKED"
    return {
        "schema": SCHEMA,
        "observed_at_utc": observed_at,
        "runtime_identity": {
            **runtime,
            "status": runtime_status,
            "reason_codes": runtime_reasons,
            "edition": "OFFICIAL_PRO",
        },
        "application_policy": {
            "project_policy": "OBSERVE_ONLY",
            "app_egress_guard": "STOCK_PRO_NOT_PATCHED",
            "external_fail_closed_preflight": "ENFORCED_BY_THIS_TOOL",
            "tx_witness": "REQUIRED_PENDING",
            "patched_pro_hardening": "OPTIONAL_NOT_CRITICAL_PATH",
        },
        "audio_binding_preflight": audio,
        "overall_status": "PASS" if runtime_status == "PASS" and audio["status"] == "PASS" else "BLOCKED",
        "non_claims": [
            "This receipt does not claim that stock Pro contains the observe-only application patch.",
            "This receipt does not prove zero DUT egress; an independent TX witness is required.",
            "This receipt does not validate K1 microphone capture, acoustic delivery, or device time.",
            "No Audio setter, I/O lifecycle command, DUT command, or serial-port operation is used.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--app", type=Path, default=DEFAULT_APP)
    parser.add_argument("--binding", type=Path)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--timeout-seconds", type=float, default=3.0)
    args = parser.parse_args()

    try:
        runtime = inspect_runtime(args.app)
        snapshot = query_runtime(args.timeout_seconds)
        binding = json.loads(args.binding.read_text(encoding="utf-8")) if args.binding else None
        receipt = build_receipt(
            runtime=runtime,
            snapshot=snapshot,
            binding=binding,
            observed_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        )
    except (OSError, json.JSONDecodeError, PreflightError) as error:
        print(f"OFFICIAL_PRO_AUDIO_PREFLIGHT=FAIL REASON={error}")
        return 1

    args.output.parent.mkdir(parents=True, exist_ok=True)
    payload = (json.dumps(receipt, indent=2, ensure_ascii=False) + "\n").encode()
    args.output.write_bytes(payload)
    print(
        "OFFICIAL_PRO_AUDIO_PREFLIGHT="
        f"{receipt['overall_status']} SHA256={hashlib.sha256(payload).hexdigest()}"
    )
    return 0 if receipt["overall_status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
