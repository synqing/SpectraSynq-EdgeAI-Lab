"""Versioned timestamped oracle traces for pre-Titan visual replay.

jsonl: one header object, then one frame per line. Optional keys omitted.
A visual engine may consume this without knowing the teacher.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

SCHEMA = "spectrasynq.semantic_trace.v1"


def write_trace(
    path: Path,
    *,
    audio: str,
    provenance: list[str],
    frames: Iterable[dict[str, Any]],
    extra_header: dict[str, Any] | None = None,
) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    header = {
        "type": "header",
        "schema": SCHEMA,
        "audio": audio,
        "provenance": provenance,
        "label": "HOST-ONLY",
    }
    if extra_header:
        header.update(extra_header)
    with path.open("w") as f:
        f.write(json.dumps(header) + "\n")
        for fr in frames:
            if "t" not in fr:
                raise ValueError("frame missing t")
            row = {"t": float(fr["t"])}
            for k, v in fr.items():
                if k == "t" or v is None:
                    continue
                row[k] = float(v) if isinstance(v, (int, float)) else v
            f.write(json.dumps(row) + "\n")
    return path


def read_trace(path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    lines = path.read_text().splitlines()
    header = json.loads(lines[0])
    if header.get("schema") != SCHEMA:
        raise ValueError(f"unknown schema {header.get('schema')}")
    frames = [json.loads(x) for x in lines[1:] if x.strip()]
    return header, frames
