#!/usr/bin/env python3
"""Freeze one exact Serial Studio Pro Audio Source C projection.

The input must be a project actually saved by Serial Studio Pro with source 2
configured as Audio.  This tool does not invent device indices or substitute a
default microphone when the intended device is absent.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


SCHEMA = "spectrasynq.serial-studio.audio-source-binding.v1"
PROFILE = "PASSIVE_DUAL_UART_AUDIO_REF"


class BindingError(ValueError):
    pass


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode(
        "utf-8"
    )


def read_project(path: Path) -> tuple[dict[str, Any], bytes]:
    raw = path.read_bytes()
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise BindingError("project must be a JSON object")
    return value, raw


def validate_source(project: dict[str, Any]) -> dict[str, Any]:
    if project.get("observeOnly") is not True:
        raise BindingError("AUDIO_BINDING_REQUIRES_OBSERVE_ONLY_PROJECT")
    if project.get("actions") != [] or project.get("tables") != []:
        raise BindingError("AUDIO_BINDING_PROJECT_HAS_WRITE_SURFACES")
    if str(project.get("controlScriptCode") or "").strip():
        raise BindingError("AUDIO_BINDING_PROJECT_HAS_CONTROL_SCRIPT")

    matches = [source for source in project.get("sources") or [] if source.get("sourceId") == 2]
    if len(matches) != 1:
        raise BindingError("AUDIO_SOURCE_2_REQUIRED_EXACTLY_ONCE")
    source = matches[0]
    if source.get("busType") != 3:
        raise BindingError("AUDIO_SOURCE_2_BUS_TYPE_MUST_BE_3")
    connection = source.get("connection")
    if not isinstance(connection, dict):
        raise BindingError("AUDIO_SOURCE_CONNECTION_MISSING")
    required = ("inputDevice", "sampleRate", "normalization", "inputFormat", "inputChannels")
    for key in required:
        if key not in connection:
            raise BindingError(f"AUDIO_SOURCE_CONNECTION_MISSING_{key}")
    if connection.get("normalization") is not False:
        raise BindingError("AUDIO_SOURCE_NORMALIZATION_MUST_BE_EXPLICITLY_FALSE")
    device_id = connection.get("deviceId")
    if not isinstance(device_id, dict):
        raise BindingError("AUDIO_SOURCE_DEVICE_ID_MISSING")
    checks = {
        "inputDeviceName": lambda value: isinstance(value, str) and bool(value.strip()),
        "sampleRateValue": lambda value: isinstance(value, int) and value > 0,
        "formatName": lambda value: isinstance(value, str) and bool(value.strip()),
        "channelCount": lambda value: isinstance(value, int) and value > 0,
    }
    for key, predicate in checks.items():
        if not predicate(device_id.get(key)):
            raise BindingError(f"AUDIO_SOURCE_DEVICE_ID_INVALID_{key}")
    return source


def capture(path: Path) -> dict[str, Any]:
    project, raw = read_project(path)
    source = validate_source(project)
    return {
        "schema": SCHEMA,
        "profile_id": PROFILE,
        "authority": "SERIAL_STUDIO_PRO_SAVED_SOURCE",
        "captured_from": {
            "project_path": str(path),
            "project_sha256": sha256_bytes(raw),
            "writer_version": str(project.get("writerVersion") or ""),
            "observe_only": True,
        },
        "source_projection_sha256": sha256_bytes(canonical(source)),
        "source_projection": source,
        "non_claims": [
            "A saved source binding does not prove that the device is currently present.",
            "The Audio source is host reference capture, not K1 microphone or device time authority.",
            "Playback remains externally owned; Serial Studio is capture-only in observe-only mode."
        ],
    }


def serialise(value: dict[str, Any]) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("project", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        payload = serialise(capture(args.project))
    except (OSError, json.JSONDecodeError, BindingError) as error:
        print(f"AUDIO_SOURCE_BINDING=FAIL REASON={error}")
        return 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(payload)
    print(f"AUDIO_SOURCE_BINDING=PASS SHA256={sha256_bytes(payload)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
