#!/usr/bin/env python3
"""Generate the separately bound K1 dual-UART plus Audio Reference project."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

from capture_audio_source_binding import SCHEMA as BINDING_SCHEMA
from capture_audio_source_binding import canonical


HERE = Path(__file__).resolve().parent
BASE_PROJECT = HERE / "projects/K1-Dual-UART-Observability-v2.ssproj"
DEFAULT_OUT = HERE / "projects/K1-Dual-UART-Audio-Reference-v2.1.ssproj"
PROFILE = "PASSIVE_DUAL_UART_AUDIO_REF"
EXTRA_SURFACES = (
    (2500, 5006, "K1 Audio Reference", "Audio Reference", "/?view=audio-reference"),
    (2600, 5007, "K1 AP Validation", "AP Validation", "/?view=ap-validation"),
)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain an object")
    return value


def generate(binding_path: Path) -> dict[str, Any]:
    base = load(BASE_PROJECT)
    binding = load(binding_path)
    if binding.get("schema") != BINDING_SCHEMA or binding.get("profile_id") != PROFILE:
        raise ValueError("audio binding schema/profile mismatch")
    source = binding.get("source_projection")
    if not isinstance(source, dict):
        raise ValueError("audio binding has no source projection")
    actual_source_sha = sha256_bytes(canonical(source))
    if actual_source_sha != binding.get("source_projection_sha256"):
        raise ValueError("audio source projection hash mismatch")

    project = copy.deepcopy(base)
    if {item.get("sourceId") for item in project["sources"]} != {0, 1}:
        raise ValueError("base project source set drift")
    if source.get("sourceId") != 2 or source.get("busType") != 3:
        raise ValueError("binding must contain Audio source 2")
    connection = source.get("connection") or {}
    if connection.get("normalization") is not False:
        raise ValueError("Audio source normalization must be explicitly false")
    project["sources"].append(copy.deepcopy(source))

    webview_ordinal = sum(1 for group in project["groups"] if group.get("widget") == "webview")
    for ordinal, (group_id, workspace_id, group_title, workspace_title, route) in enumerate(
        EXTRA_SURFACES
    ):
        project["groups"].append(
            {
                "datasets": [],
                "title": group_title,
                "uniqueId": group_id,
                "widget": "webview",
                "webViewUrl": "http://127.0.0.1:8765" + route,
            }
        )
        project["workspaces"].append(
            {
                "description": "Question-driven optional host Audio Reference surface",
                "title": workspace_title,
                "widgetRefs": [
                    {
                        "groupId": group_id,
                        "relativeIndex": webview_ordinal + ordinal,
                        "widgetType": 16,
                    }
                ],
                "workspaceId": workspace_id,
            }
        )
    project["title"] = "K1 Dual UART + Audio Reference Observability v2.1"
    project["nextUniqueId"] = max(int(project.get("nextUniqueId", 0)), 2601)
    return project


def serialise(value: dict[str, Any]) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--binding", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = serialise(generate(args.binding))
    if args.check:
        if not args.output.is_file() or args.output.read_bytes() != payload:
            raise SystemExit(f"generated audio profile drift: {args.output}")
        print(f"AUDIO_PROFILE_GENERATION=PASS SHA256={sha256_bytes(payload)}")
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(payload)
    print(f"WROTE={args.output} SHA256={sha256_bytes(payload)} BYTES={len(payload)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
