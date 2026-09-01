#!/usr/bin/env python3
"""Semantic linter for the separately bound Serial Studio Audio profile."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from capture_audio_source_binding import SCHEMA as BINDING_SCHEMA
from capture_audio_source_binding import canonical, sha256_bytes
from generate_audio_profile import BASE_PROJECT, EXTRA_SURFACES, PROFILE


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain an object")
    return value


def lint(project: dict[str, Any], binding: dict[str, Any], base: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    def require(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)

    require(project.get("observeOnly") is True, "observeOnly must be true")
    require(project.get("actions") == [], "actions must be empty")
    require(project.get("tables") == [], "tables must be empty")
    require(not str(project.get("controlScriptCode") or "").strip(), "control script must be empty")
    require(binding.get("schema") == BINDING_SCHEMA, "binding schema mismatch")
    require(binding.get("profile_id") == PROFILE, "binding profile mismatch")

    sources = project.get("sources") or []
    source_by_id = {source.get("sourceId"): source for source in sources}
    require(set(source_by_id) == {0, 1, 2}, "audio profile source IDs must equal {0,1,2}")
    base_by_id = {source.get("sourceId"): source for source in base.get("sources") or []}
    for source_id in (0, 1):
        require(
            source_by_id.get(source_id) == base_by_id.get(source_id),
            f"UART source {source_id} must be byte-semantically identical to v2",
        )
    bound_source = binding.get("source_projection")
    require(isinstance(bound_source, dict), "binding source projection missing")
    if isinstance(bound_source, dict):
        require(
            binding.get("source_projection_sha256") == sha256_bytes(canonical(bound_source)),
            "binding source hash mismatch",
        )
        require(source_by_id.get(2) == bound_source, "project Source C differs from binding")
    source_c = source_by_id.get(2) or {}
    require(source_c.get("busType") == 3, "Source C must use Audio bus type 3")
    connection = source_c.get("connection") or {}
    require(connection.get("normalization") is False, "Source C normalization must be false")
    device_id = connection.get("deviceId") or {}
    for key in ("inputDeviceName", "sampleRateValue", "formatName", "channelCount"):
        require(device_id.get(key) not in (None, "", 0), f"Source C deviceId lacks {key}")

    base_group_ids = {group.get("uniqueId") for group in base.get("groups") or []}
    groups = project.get("groups") or []
    group_by_id = {group.get("uniqueId"): group for group in groups}
    expected_extra_ids = {item[0] for item in EXTRA_SURFACES}
    require(
        set(group_by_id) == base_group_ids | expected_extra_ids,
        "audio profile group set differs from base plus two Web Views",
    )
    for group_id, _, group_title, _, route in EXTRA_SURFACES:
        group = group_by_id.get(group_id) or {}
        require(group.get("title") == group_title, f"group {group_id} title drift")
        require(group.get("widget") == "webview", f"group {group_id} must be Web View")
        require(group.get("datasets") == [], f"group {group_id} must have zero datasets")
        require(
            group.get("webViewUrl") == "http://127.0.0.1:8765" + route,
            f"group {group_id} route drift",
        )

    base_workspace_titles = {item.get("title") for item in base.get("workspaces") or []}
    workspaces = project.get("workspaces") or []
    workspace_by_title = {item.get("title"): item for item in workspaces}
    expected_titles = base_workspace_titles | {item[3] for item in EXTRA_SURFACES}
    require(set(workspace_by_title) == expected_titles, "audio profile workspace set drift")
    base_workspace_by_title = {
        item.get("title"): item for item in base.get("workspaces") or []
    }
    for title in base_workspace_titles:
        require(
            workspace_by_title.get(title) == base_workspace_by_title.get(title),
            f"base workspace {title} must remain unchanged",
        )
    mission = workspace_by_title.get("Mission Control") or {}
    require(len(mission.get("widgetRefs") or []) == 1, "Mission Control must remain one Web View")
    if len(mission.get("widgetRefs") or []) == 1:
        mission_group = group_by_id.get(mission["widgetRefs"][0].get("groupId")) or {}
        require(mission_group.get("title") == "K1 Mission Control", "Mission Control group drift")
        require(mission_group.get("datasets") == [], "Mission Control datasets must remain empty")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("project", type=Path)
    parser.add_argument("--binding", type=Path, required=True)
    args = parser.parse_args()
    errors = lint(load(args.project), load(args.binding), load(BASE_PROJECT))
    if errors:
        print("SSV2_1_AUDIO_PROFILE_VALID=FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("SSV2_1_AUDIO_PROFILE_VALID=PASS")
    print("SSV2_1_AUDIO_PROFILE_NO_CONFIGURED_WRITE=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
