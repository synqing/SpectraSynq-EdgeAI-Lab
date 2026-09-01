#!/usr/bin/env python3
"""Derive freshness-normalised diagnostics from a frozen K1 Historian session."""

from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Any


FIELDS = {
    "bpm": ("BPM", 1, "value"),
    "confidence": ("Legacy mixed confidence", 2, "value"),
    "lock": ("Lock", 3, "state"),
    "onset": ("Onset", 5, "event"),
    "bass_onset": ("Bass onset", 6, "event"),
    "peak_envelope": ("Peak envelope", 9, "value"),
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _uid(connection: sqlite3.Connection, session_id: int, source_id: int, title: str) -> int:
    row = connection.execute(
        "SELECT unique_id FROM columns WHERE session_id=? AND source_id=? "
        "AND title=? AND lower(group_title) LIKE '%decoded forensics%' "
        "ORDER BY unique_id LIMIT 1",
        (session_id, source_id, title),
    ).fetchone()
    if row is None:
        raise ValueError(f"missing decoded-forensics column: source={source_id} title={title}")
    return int(row[0])


def summarise(snapshot: Path, session_id: int) -> dict[str, Any]:
    uri = f"file:{snapshot.resolve()}?immutable=1"
    with sqlite3.connect(uri, uri=True) as connection:
        session = connection.execute(
            "SELECT project_title,started_at,ended_at FROM sessions WHERE session_id=?",
            (session_id,),
        ).fetchone()
        if session is None or session[2] is None:
            raise ValueError("target session is absent or not closed")
        source_ids = [
            int(row[0])
            for row in connection.execute(
                "SELECT DISTINCT source_id FROM columns WHERE session_id=? ORDER BY source_id",
                (session_id,),
            )
        ]
        sources: list[dict[str, Any]] = []
        for source_id in source_ids:
            raw = connection.execute(
                "SELECT COUNT(*),COALESCE(SUM(length(data)),0),MIN(timestamp_ns),MAX(timestamp_ns) "
                "FROM raw_bytes WHERE session_id=? AND device_id=?",
                (session_id, source_id),
            ).fetchone()
            duration_s = (
                max(0.0, (int(raw[3]) - int(raw[2])) / 1e9)
                if raw and raw[2] is not None and raw[3] is not None
                else 0.0
            )
            mask_uid = _uid(connection, session_id, source_id, "Update mask")
            metrics: dict[str, Any] = {}
            for field_id, (title, slot, semantics) in FIELDS.items():
                metric_uid = _uid(connection, session_id, source_id, title)
                row = connection.execute(
                    "SELECT COUNT(*),"
                    "SUM(CASE WHEN v.final_numeric_value>=0.5 THEN 1 ELSE 0 END),"
                    "MIN(v.final_numeric_value),AVG(v.final_numeric_value),MAX(v.final_numeric_value) "
                    "FROM readings m JOIN readings v "
                    "ON v.session_id=m.session_id AND v.timestamp_ns=m.timestamp_ns "
                    "WHERE m.session_id=? AND m.unique_id=? AND v.unique_id=? "
                    "AND (CAST(m.final_numeric_value AS INTEGER) & ?) != 0",
                    (session_id, mask_uid, metric_uid, 1 << (slot - 1)),
                ).fetchone()
                fresh = int(row[0] or 0)
                assertions = int(row[1] or 0)
                entry = {
                    "semantics": semantics,
                    "fresh_updates": fresh,
                    "minimum": row[2],
                    "mean": row[3],
                    "maximum": row[4],
                }
                if semantics in {"event", "state"}:
                    entry.update(
                        {
                            "high_fresh_updates": assertions,
                            "high_fraction": assertions / fresh if fresh else None,
                            "high_updates_per_valid_minute": (
                                assertions / (duration_s / 60) if duration_s > 0 else None
                            ),
                        }
                    )
                metrics[field_id] = entry
            sources.append(
                {
                    "source_id": source_id,
                    "valid_uptime_s": duration_s,
                    "raw_rows": int(raw[0] or 0),
                    "raw_bytes": int(raw[1] or 0),
                    "metrics": metrics,
                }
            )
    return {
        "schema": "spectrasynq.serial-studio.capture-diagnostics.v1",
        "status": "MEASURED",
        "session_id": session_id,
        "project_title": session[0],
        "snapshot_sha256": sha256_file(snapshot),
        "sources": sources,
        "verdict_boundary": (
            "Freshness-normalised observer diagnostics only; no controlled shared stimulus, "
            "acoustic equivalence, clock map, or algorithm verdict is claimed."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", type=Path, required=True)
    parser.add_argument("--session-id", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = summarise(args.snapshot, args.session_id)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(
        f"CAPTURE_DIAGNOSTICS=MEASURED SESSION={args.session_id} "
        f"SNAPSHOT_SHA256={result['snapshot_sha256']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
