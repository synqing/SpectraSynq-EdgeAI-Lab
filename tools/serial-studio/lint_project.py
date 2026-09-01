#!/usr/bin/env python3
"""Semantic linter for the K1 Serial Studio v2 project."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
DEFAULT_PROJECT = HERE / "projects/K1-Dual-UART-Observability-v2.ssproj"
CATALOGUE = HERE / "schemas/telemetry-catalogue.v1.json"
PARSER = HERE / "parsers/k1_observe_v1_2.js"

WIDGET_TYPES = {"datagrid": 1, "multiplot": 2, "webview": 16, "painter": 22}
LINTER_VERSION = "1.1.0"
REQUIRED_WORKSPACES = {
    "Mission Control",
    "Rhythm & Events",
    "Audio Dynamics",
    "Timing & Transport",
    "System Health",
    "Raw / Forensics",
}
FORBIDDEN_TEXT = (
    "deviceWrite",
    "deviceWriteAndWait",
    "actionFire",
    "apiCall",
    "tableSet",
    "dashboardTick",
    "io.writeData",
    "k1_gate",
)


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} is not a JSON object")
    return value


def lint(project: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    catalogue = _load(CATALOGUE)
    canonical_parser = PARSER.read_text(encoding="utf-8").rstrip() + "\n"
    fields_by_index = {int(field["index"]): field for field in catalogue["fields"]}

    def require(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)

    require(project.get("schemaVersion") == 3, "schemaVersion must be 3")
    require(project.get("writerVersion") == "4.0.3", "writerVersion must be 4.0.3")
    require(project.get("observeOnly") is True, "observeOnly must be true")
    require(project.get("plotTimeRange") == 20, "plot time range must be 20 seconds")
    require(project.get("pointCount") == 4096, "plot point count must be 4096")
    require(project.get("customizeWorkspaces") is True, "custom workspaces must be enabled")
    require(project.get("actions") == [], "actions must be empty")
    require(project.get("tables") == [], "tables must be empty")
    require(not str(project.get("controlScriptCode") or "").strip(), "control script must be empty")

    blob = json.dumps(project, sort_keys=True)
    for token in FORBIDDEN_TEXT:
        require(token not in blob, f"forbidden write surface present: {token}")

    sources = project.get("sources") or []
    require({source.get("sourceId") for source in sources} == {0, 1}, "source IDs must equal {0,1}")
    source_ids = {source.get("sourceId") for source in sources}
    serials: list[str] = []
    for source in sources:
        sid = source.get("sourceId")
        require(source.get("busType") == 0, f"source {sid} must be passive UART")
        require(source.get("frameParserCode") == canonical_parser, f"source {sid} parser drift")
        connection = source.get("connection") or {}
        require(connection.get("autoReconnect") is False, f"source {sid} autoReconnect must be false")
        serial = str((connection.get("deviceId") or {}).get("serial") or "")
        require(bool(serial), f"source {sid} has no USB serial identity")
        serials.append(serial)
    require(len(serials) == len(set(serials)), "USB serial identities must be unique")

    groups = project.get("groups") or []
    group_uids = [group.get("uniqueId") for group in groups]
    require(len(group_uids) == len(set(group_uids)), "group uniqueIds must be unique")
    dataset_uids: list[int] = []
    group_by_uid: dict[int, dict[str, Any]] = {}
    for group_position, group in enumerate(groups):
        uid = group.get("uniqueId")
        if isinstance(uid, int):
            group_by_uid[uid] = group
        require(group.get("widget") in WIDGET_TYPES, f"group {uid} has unsupported widget")
        if group.get("widget") != "webview":
            require("sourceId" in group, f"group {uid} sourceId must be explicit")
            require(group.get("sourceId") in source_ids, f"group {uid} sourceId is invalid")
        if group.get("widget") == "webview":
            require(
                str(group.get("webViewUrl") or "").startswith("http://127.0.0.1:8765/"),
                f"group {uid} Web View must use the loopback bridge",
            )
        domains: set[str] = set()
        for dataset_position, dataset in enumerate(group.get("datasets") or []):
            dataset_uids.append(dataset.get("uniqueId"))
            require(dataset.get("groupId") == group_position, f"group {uid} dataset groupId drift")
            require(dataset.get("datasetId") == dataset_position, f"group {uid} datasetId drift")
            require("sourceId" not in dataset, f"group {uid} dataset has ignored sourceId residue")
            index = dataset.get("index")
            require(isinstance(index, int) and 1 <= index <= catalogue["slot_count"], f"group {uid} index {index} out of range")
            field = fields_by_index.get(index) if isinstance(index, int) else None
            if field:
                require(dataset.get("title") == field["title"], f"group {uid} slot {index} title drift")
                require(dataset.get("units") == field["units"], f"group {uid} slot {index} units drift")
                domains.add(field["domain"])
                if field["semantics"] in {"event", "mixed_event"}:
                    require(dataset.get("led") is False, f"event {field['id']} must not be an LED")
            require(not str(dataset.get("title") or "").startswith("unused_slot_"), "dead unused_slot dataset")
            require(dataset.get("fft") is False, "FFT is not admitted without a run-proven cadence")
        if group.get("widget") == "multiplot":
            require(len(domains) <= 1, f"MultiPlot {group.get('title')} mixes domains {sorted(domains)}")
            for dataset in group.get("datasets") or []:
                require(dataset.get("plotMin") != dataset.get("plotMax"), f"MultiPlot {uid} has autoscale/degenerate bounds")
        if group.get("widget") == "painter":
            code = str(group.get("painterCode") or "")
            require("update_mask" in code or "bitFresh" in code, f"Painter {uid} lacks freshness logic")

    all_uids = [uid for uid in group_uids + dataset_uids if isinstance(uid, int)]
    require(len(all_uids) == len(set(all_uids)), "persistent group/dataset IDs collide")
    if all_uids:
        require(project.get("nextUniqueId", 0) > max(all_uids), "nextUniqueId must exceed every persistent ID")

    buckets: dict[int, list[int]] = {kind: [] for kind in WIDGET_TYPES.values()}
    for group in groups:
        widget = group.get("widget")
        if widget in WIDGET_TYPES and isinstance(group.get("uniqueId"), int):
            buckets[WIDGET_TYPES[widget]].append(group["uniqueId"])

    workspaces = project.get("workspaces") or []
    titles = {workspace.get("title") for workspace in workspaces}
    require(titles == REQUIRED_WORKSPACES, f"workspace set drift: {sorted(str(x) for x in titles)}")
    workspace_ids = [workspace.get("workspaceId") for workspace in workspaces]
    require(len(workspace_ids) == len(set(workspace_ids)), "workspace IDs must be unique")
    for workspace in workspaces:
        wid = workspace.get("workspaceId")
        require(isinstance(wid, int) and wid >= 5000, f"workspace {wid} is in reserved range")
        refs = workspace.get("widgetRefs") or []
        require(bool(refs), f"workspace {workspace.get('title')} is empty")
        seen_refs: set[tuple[Any, Any, Any]] = set()
        for ref in refs:
            key = (ref.get("widgetType"), ref.get("groupId"), ref.get("relativeIndex"))
            require(key not in seen_refs, f"workspace {wid} contains duplicate ref {key}")
            seen_refs.add(key)
            uid = ref.get("groupId")
            widget_type = ref.get("widgetType")
            relative = ref.get("relativeIndex")
            require(uid in group_by_uid, f"workspace {wid} references missing group {uid}")
            if uid in group_by_uid:
                widget_name = group_by_uid[uid].get("widget")
                if widget_name not in WIDGET_TYPES:
                    require(False, f"workspace {wid} references unsupported group widget {widget_name}")
                    continue
                expected_type = WIDGET_TYPES[widget_name]
                require(widget_type == expected_type, f"workspace {wid} widget type mismatch for {uid}")
                require(
                    isinstance(relative, int)
                    and 0 <= relative < len(buckets[expected_type])
                    and buckets[expected_type][relative] == uid,
                    f"workspace {wid} bucket ordinal mismatch for {uid}",
                )

    mission = next(
        (workspace for workspace in workspaces if workspace.get("title") == "Mission Control"),
        None,
    )
    if mission is not None:
        refs = mission.get("widgetRefs") or []
        require(
            len(refs) == 1,
            "Mission Control must contain exactly one dominant Web View",
        )
        if len(refs) == 1:
            group = group_by_uid.get(refs[0].get("groupId"))
            require(
                group is not None
                and group.get("widget") == "webview"
                and group.get("title") == "K1 Mission Control",
                "Mission Control may reference only the canonical K1 Mission Control Web View",
            )
            if group is not None:
                require(
                    not (group.get("datasets") or []),
                    "Mission Control Web View must not carry decorative native datasets",
                )
    require("Renderer" not in titles, "Renderer workspace is forbidden until renderer telemetry exists")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("project", nargs="?", type=Path, default=DEFAULT_PROJECT)
    args = parser.parse_args()
    project = _load(args.project)
    errors = lint(project)
    if errors:
        print("SSV2_PROJECT_VALID=FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("SSV2_PROJECT_VALID=PASS")
    print("SSV2_NO_CONFIGURED_WRITE=PASS")
    print(f"SSV2_LINTER_VERSION={LINTER_VERSION}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
