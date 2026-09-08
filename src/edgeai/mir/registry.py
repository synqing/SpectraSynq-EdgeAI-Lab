"""Load and validate mir/registry.yaml.

Structural honesty, not optimism: UNKNOWN is a legal value everywhere. What the
loader refuses is a MISSING field, an off-vocabulary lineage value, or a lineage
claim that its own licence fields contradict.
"""

from __future__ import annotations

import re
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
    "commercial_training_lineage",
    "status",
    "spectrasynq",
)

LINEAGE_FIELDS = ("code_licence", "weight_licence", "dataset_licence")

# See the vocabulary comment block at the top of mir/registry.yaml.
LINEAGE_VOCAB = {"true", "false", "conditional", "unknown", "n/a"}

# Tokens that make an unqualified `true` self-contradictory. Deliberately blunt:
# this catches copy-paste optimism, not every legal nuance.
BLOCKING_TOKENS = (
    "nc",
    "noncommercial",
    "non-commercial",
    "educational",
    "unknown",
    "research only",
    "research-only",
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_PATH = ROOT / "mir" / "registry.yaml"


def _norm(v: Any) -> str:
    if isinstance(v, bool):
        return "true" if v else "false"
    return str(v).strip().lower()


def _has_blocking_token(text: str) -> bool:
    low = text.lower()
    for tok in BLOCKING_TOKENS:
        if tok == "nc":
            # word-ish match so "sync"/"encoder" do not trip it
            if re.search(r"\bnc\b|by-nc|-nc-|\bnc-", low):
                return True
        elif tok in low:
            return True
    return False


def load_registry(path: Path | None = None) -> dict[str, Any]:
    p = path or DEFAULT_PATH
    data = yaml.safe_load(p.read_text())
    if not isinstance(data, dict) or "entries" not in data:
        raise ValueError(f"bad registry: {p}")
    ids: list[str] = []
    problems: list[str] = []
    for i, e in enumerate(data["entries"]):
        missing = [k for k in REQUIRED if k not in e]
        if missing:
            problems.append(f"entry {i} ({e.get('id', '?')}) missing {missing}")
            continue
        ids.append(e["id"])

        ctl = _norm(e["commercial_training_lineage"])
        if ctl not in LINEAGE_VOCAB:
            problems.append(
                f"{e['id']}: commercial_training_lineage {e['commercial_training_lineage']!r} "
                f"not in {sorted(LINEAGE_VOCAB)} — prose belongs in `spectrasynq`"
            )
            continue

        if ctl == "true":
            if _norm(e["commercial_use"]) == "no":
                problems.append(
                    f"{e['id']}: commercial_training_lineage true but commercial_use no"
                )
            blockers = [
                f for f in LINEAGE_FIELDS if _has_blocking_token(str(e[f]))
            ]
            if blockers:
                problems.append(
                    f"{e['id']}: commercial_training_lineage true but "
                    f"{blockers} carry a non-commercial/unknown token"
                )

    dupes = {x for x in ids if ids.count(x) > 1}
    if dupes:
        problems.append(f"duplicate registry ids: {sorted(dupes)}")
    if problems:
        raise ValueError("registry invalid:\n  - " + "\n  - ".join(problems))
    return data


def by_status(data: dict[str, Any], status: str) -> list[dict[str, Any]]:
    return [e for e in data["entries"] if e["status"] == status]


def lineage_class(entry: dict[str, Any]) -> str:
    """Normalised commercial-training-lineage class for one entry."""
    return _norm(entry["commercial_training_lineage"])


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
                "commercial_training_lineage": lineage_class(e),
                "teacher": str(e.get("teacher_use", "")),
                "derived": str(e.get("derived_weight_status", "")),
            }
        )
    return rows
