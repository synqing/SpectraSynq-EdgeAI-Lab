#!/usr/bin/env python3
"""Generate the write-free K1 Serial Studio v2 project.

The generator consumes only checked-in declarative manifests. Live v1 is a
mutable replay artefact and can be audited explicitly, but it is never a v2
generation input.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
DEFAULT_V1 = Path.home() / "Documents/Serial Studio/Projects/K1 Dual UART Observability.ssproj"
DEFAULT_OUT = HERE / "projects/K1-Dual-UART-Observability-v2.ssproj"
V1_MANIFEST = HERE / "projects/v1.manifest.json"
WORKSPACE_MANIFEST = HERE / "projects/v2.workspace-manifest.json"
ENTITY_IDS = HERE / "projects/entity-ids.v1.json"
CATALOGUE = HERE / "schemas/telemetry-catalogue.v1.json"
PARSER = HERE / "parsers/k1_observe_v1_2.js"
PAINTER = HERE / "parsers/event_raster.js"

WIDGET_TYPES = {"datagrid": 1, "multiplot": 2, "webview": 16, "painter": 22}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return obj


def verify_v1(path: Path) -> None:
    frozen = load_json(V1_MANIFEST)["live"]
    raw = path.read_bytes()
    actual = sha256_bytes(raw)
    if actual != frozen["sha256"]:
        raise ValueError(
            f"v1 drift: expected {frozen['sha256']}, got {actual}; "
            "freeze a new manifest explicitly instead of transforming unknown state"
        )
    project = json.loads(raw)
    if project.get("writerVersion") != frozen["writer_version"]:
        raise ValueError("v1 writer version disagrees with freeze manifest")
    print(f"V1_FREEZE=PASS SHA256={actual}")


def dataset_for(
    field: dict[str, Any], *, group_position: int, dataset_position: int, unique_id: int
) -> dict[str, Any]:
    display_range = field.get("display_range")
    lo, hi = (display_range if display_range is not None else [0, 0])
    return {
        "datasetId": dataset_position,
        "displayFormat": "0d",
        "displayTickCount": 5,
        "fft": False,
        "fftMax": hi,
        "fftMin": lo,
        "fftSamples": 256,
        "fftSamplingRate": 0,
        "fftWindow": 5,
        "graph": False,
        "groupId": group_position,
        "index": field["index"],
        "led": False,
        "ledHigh": 0.5,
        "log": False,
        "numericValue": 0,
        "plotMax": hi,
        "plotMin": lo,
        "title": field["title"],
        "uniqueId": unique_id,
        "units": field["units"],
        "value": "",
        "widget": "",
        "widgetMax": hi,
        "widgetMin": lo,
        "xAxis": -2,
    }


def source_projection(
    frozen_sources: list[dict[str, Any]], parser_code: str
) -> list[dict[str, Any]]:
    sources = copy.deepcopy(frozen_sources)
    if {s.get("sourceId") for s in sources} != {0, 1}:
        raise ValueError("v2 requires exactly source IDs 0 and 1")
    serials: list[str] = []
    for source in sources:
        connection = source.get("connection") or {}
        device_id = connection.get("deviceId") or {}
        serial = str(device_id.get("serial") or "")
        if not serial:
            raise ValueError(f"source {source.get('sourceId')} has no USB serial identity")
        serials.append(serial)
        connection["autoReconnect"] = False
        source["frameParserCode"] = parser_code
    if len(set(serials)) != len(serials):
        raise ValueError("source USB serial identities are not unique")
    return sorted(sources, key=lambda source: int(source["sourceId"]))


def generate() -> dict[str, Any]:
    v1_manifest = load_json(V1_MANIFEST)
    manifest = load_json(WORKSPACE_MANIFEST)
    ids = load_json(ENTITY_IDS)
    catalogue = load_json(CATALOGUE)
    fields = {field["id"]: field for field in catalogue["fields"]}
    parser_code = PARSER.read_text(encoding="utf-8").rstrip() + "\n"
    painter_code = PAINTER.read_text(encoding="utf-8").rstrip() + "\n"

    groups: list[dict[str, Any]] = []
    group_by_slug: dict[str, dict[str, Any]] = {}
    for group_position, spec in enumerate(manifest["groups"]):
        slug = spec["slug"]
        uid = int(ids["groups"][slug])
        group: dict[str, Any] = {
            "datasets": [],
            "title": spec["title"],
            "uniqueId": uid,
            "widget": spec["widget"],
        }
        if "source_id" in spec:
            group["sourceId"] = int(spec["source_id"])
        if spec["widget"] == "webview":
            group["webViewUrl"] = manifest["webview_base_url"] + spec["url"]
        if spec["widget"] == "painter":
            group["painterCode"] = painter_code

        field_ids = list(fields) if spec.get("fields") == "all" else spec.get("fields", [])
        for dataset_position, field_id in enumerate(field_ids):
            if field_id not in fields:
                raise ValueError(f"unknown field {field_id!r} in group {slug}")
            offset = int(ids["dataset_offsets"][field_id])
            group["datasets"].append(
                dataset_for(
                    fields[field_id],
                    group_position=group_position,
                    dataset_position=dataset_position,
                    unique_id=uid + offset,
                )
            )
        groups.append(group)
        group_by_slug[slug] = group

    buckets: dict[int, list[str]] = {kind: [] for kind in WIDGET_TYPES.values()}
    for spec in manifest["groups"]:
        buckets[WIDGET_TYPES[spec["widget"]]].append(spec["slug"])

    workspaces: list[dict[str, Any]] = []
    for workspace in manifest["workspaces"]:
        refs: list[dict[str, Any]] = []
        for slug in workspace["groups"]:
            group = group_by_slug[slug]
            widget_type = WIDGET_TYPES[group["widget"]]
            refs.append(
                {
                    "groupId": group["uniqueId"],
                    "relativeIndex": buckets[widget_type].index(slug),
                    "widgetType": widget_type,
                }
            )
        workspaces.append(
            {
                "description": "Question-driven K1 observability surface",
                "title": workspace["title"],
                "widgetRefs": refs,
                "workspaceId": int(workspace["id"]),
            }
        )

    persistent_ids = [group["uniqueId"] for group in groups]
    persistent_ids.extend(dataset["uniqueId"] for group in groups for dataset in group["datasets"])

    return {
        "actions": [],
        "changeDrivenTransforms": False,
        "controlScriptCode": "",
        "customizeWorkspaces": True,
        "frozen": False,
        "groups": groups,
        "hexadecimalDelimiters": "",
        "luaFastMode": False,
        "nextUniqueId": max(persistent_ids) + 1,
        "observeOnly": True,
        "plotTimeRange": 20,
        "pointCount": 4096,
        "schemaVersion": 3,
        "sources": source_projection(v1_manifest["source_projection"], parser_code),
        "tables": [],
        "title": manifest["project_title"],
        "widgetSettings": {"externalWindows": {"data": []}},
        "workspaces": workspaces,
        "writerVersion": "4.0.3",
        "writerVersionAtCreation": "4.0.3",
    }


def serialise(project: dict[str, Any]) -> bytes:
    return (json.dumps(project, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--verify-v1",
        nargs="?",
        const=DEFAULT_V1,
        type=Path,
        help="audit the frozen v1 hash before generation; optionally name a path",
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--check", action="store_true", help="fail if output differs; do not write")
    args = parser.parse_args()

    if args.verify_v1 is not None:
        verify_v1(args.verify_v1)
    generated = serialise(generate())
    if args.check:
        if not args.output.is_file() or args.output.read_bytes() != generated:
            raise SystemExit(f"generated project drift: {args.output}")
        print(f"PROJECT_GENERATION=PASS SHA256={sha256_bytes(generated)}")
        return 0

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(generated)
    print(f"WROTE={args.output} SHA256={sha256_bytes(generated)} BYTES={len(generated)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
