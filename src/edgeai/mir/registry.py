"""Load and validate mir/registry.yaml."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

REQUIRED = (
    "id",
    "kind",
    "name",
    "task",
    "deployment",
    "code_licence",
    "weight_licence",
    "dataset_licence",
    "research_use",
    "commercial_use",
    "status",
    "spectrasynq",
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_PATH = ROOT / "mir" / "registry.yaml"


def load_registry(path: Path | None = None) -> dict[str, Any]:
    p = path or DEFAULT_PATH
    data = yaml.safe_load(p.read_text())
    if not isinstance(data, dict) or "entries" not in data:
        raise ValueError(f"bad registry: {p}")
    ids = []
    for i, e in enumerate(data["entries"]):
        missing = [k for k in REQUIRED if k not in e]
        if missing:
            raise ValueError(f"entry {i} missing {missing}")
        ids.append(e["id"])
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate registry ids")
    return data


def by_status(data: dict[str, Any], status: str) -> list[dict[str, Any]]:
    return [e for e in data["entries"] if e["status"] == status]


def licensing_matrix(data: dict[str, Any]) -> list[dict[str, str]]:
    rows = []
    for e in data["entries"]:
        rows.append(
            {
                "id": e["id"],
                "code": str(e["code_licence"]),
                "weights": str(e["weight_licence"]),
                "dataset": str(e["dataset_licence"]),
                "research": str(e["research_use"]),
                "commercial": str(e["commercial_use"]),
                "teacher": str(e.get("teacher_use", "")),
                "derived": str(e.get("derived_weight_status", "")),
            }
        )
    return rows
