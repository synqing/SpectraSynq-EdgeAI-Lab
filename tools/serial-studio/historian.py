#!/usr/bin/env python3
"""Freeze and inspect Serial Studio Historian evidence without mutating source DBs."""

from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Any


REQUIRED_TABLES = {"sessions", "columns", "readings", "raw_bytes"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def read_only_connection(path: Path) -> sqlite3.Connection:
    return sqlite3.connect(f"file:{path.resolve()}?mode=ro", uri=True)


def freeze_database(source: Path, destination: Path) -> None:
    """Create a standalone SQLite backup; refuse overwrite and source aliasing."""

    source = source.resolve()
    destination = destination.resolve()
    if source == destination:
        raise ValueError("Historian source and snapshot paths must differ")
    if destination.exists():
        raise FileExistsError(f"snapshot already exists: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with read_only_connection(source) as live, sqlite3.connect(destination) as frozen:
        live.backup(frozen)


def integrity_check(connection: sqlite3.Connection) -> str:
    row = connection.execute("PRAGMA integrity_check").fetchone()
    return str(row[0]) if row else "no result"


def _tables(connection: sqlite3.Connection) -> set[str]:
    return {
        str(row[0])
        for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")
    }


def _session(connection: sqlite3.Connection, session_id: int) -> dict[str, Any]:
    connection.row_factory = sqlite3.Row
    row = connection.execute(
        "SELECT session_id, project_title, started_at, ended_at, project_json, notes "
        "FROM sessions WHERE session_id = ?",
        (session_id,),
    ).fetchone()
    if row is None:
        raise ValueError(f"Historian session {session_id} does not exist")
    return dict(row)


def _project_sources(project: dict[str, Any]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for source in project.get("sources") or []:
        connection = source.get("connection") or {}
        device_id = connection.get("deviceId") or {}
        result.append(
            {
                "source_id": source.get("sourceId"),
                "title": source.get("title"),
                "device": connection.get("portName") or connection.get("device"),
                "usb_serial": device_id.get("serial"),
            }
        )
    return result


def _count_by_source(connection: sqlite3.Connection, session_id: int) -> list[dict[str, Any]]:
    rows = connection.execute(
        "SELECT c.source_id, c.source_title, COUNT(r.reading_id) "
        "FROM columns c LEFT JOIN readings r "
        "ON r.session_id=c.session_id AND r.unique_id=c.unique_id "
        "WHERE c.session_id=? GROUP BY c.source_id, c.source_title ORDER BY c.source_id",
        (session_id,),
    )
    return [
        {"source_id": int(source_id), "source_title": title, "reading_rows": int(count)}
        for source_id, title, count in rows
    ]


def _raw_by_source(connection: sqlite3.Connection, session_id: int) -> list[dict[str, Any]]:
    rows = connection.execute(
        "SELECT device_id, COUNT(*), COALESCE(SUM(length(data)),0), "
        "MIN(timestamp_ns), MAX(timestamp_ns) FROM raw_bytes "
        "WHERE session_id=? GROUP BY device_id ORDER BY device_id",
        (session_id,),
    )
    return [
        {
            "source_id": int(source_id),
            "raw_rows": int(count),
            "raw_bytes": int(byte_count),
            "first_timestamp_ns": first_timestamp,
            "last_timestamp_ns": last_timestamp,
        }
        for source_id, count, byte_count, first_timestamp, last_timestamp in rows
    ]


def _counter_bounds(
    connection: sqlite3.Connection, session_id: int, titles: tuple[str, ...]
) -> list[dict[str, Any]]:
    placeholders = ",".join("?" for _ in titles)
    rows = connection.execute(
        "SELECT c.source_id, c.source_title, r.timestamp_ns, r.final_numeric_value "
        "FROM columns c JOIN readings r "
        "ON r.session_id=c.session_id AND r.unique_id=c.unique_id "
        f"WHERE c.session_id=? AND lower(c.title) IN ({placeholders}) "
        "AND r.final_numeric_value IS NOT NULL "
        "ORDER BY c.source_id, r.timestamp_ns, r.reading_id",
        (session_id, *(title.casefold() for title in titles)),
    )
    grouped: dict[int, dict[str, Any]] = {}
    for source_id, source_title, timestamp_ns, value in rows:
        source_id = int(source_id)
        entry = grouped.setdefault(
            source_id,
            {
                "source_id": source_id,
                "source_title": source_title,
                "first": value,
                "first_timestamp_ns": timestamp_ns,
                "last": value,
                "last_timestamp_ns": timestamp_ns,
                "reading_rows": 0,
                "regressions": 0,
                "_previous": value,
            },
        )
        if value < entry["_previous"]:
            entry["regressions"] += 1
        entry["_previous"] = value
        entry["last"] = value
        entry["last_timestamp_ns"] = timestamp_ns
        entry["reading_rows"] += 1
    output: list[dict[str, Any]] = []
    for source_id in sorted(grouped):
        entry = grouped[source_id]
        entry.pop("_previous", None)
        output.append(entry)
    return output


def _freshness_counts(
    connection: sqlite3.Connection,
    session_id: int,
    catalogue: dict[str, Any],
) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    sources = connection.execute(
        "SELECT DISTINCT source_id FROM columns WHERE session_id=? ORDER BY source_id",
        (session_id,),
    )
    for (source_id,) in sources:
        candidates = connection.execute(
            "SELECT unique_id, title, group_title FROM columns "
            "WHERE session_id=? AND source_id=? "
            "AND lower(title) IN ('update mask','update_mask','record kind','record_kind') "
            "ORDER BY CASE WHEN group_title LIKE '%forensic%' THEN 0 ELSE 1 END, unique_id",
            (session_id, source_id),
        ).fetchall()
        chosen: dict[str, int] = {}
        for unique_id, title, _ in candidates:
            chosen.setdefault(str(title).casefold().replace(" ", "_"), int(unique_id))
        mask_uid = chosen.get("update_mask")
        kind_uid = chosen.get("record_kind")
        if mask_uid is None or kind_uid is None:
            output.append(
                {
                    "source_id": int(source_id),
                    "status": "NOT_INSTRUMENTED",
                    "reason": "Update mask or record kind column is absent.",
                }
            )
            continue
        rows = connection.execute(
            "SELECT m.timestamp_ns, CAST(m.final_numeric_value AS INTEGER), "
            "CAST(k.final_numeric_value AS INTEGER) FROM readings m JOIN readings k "
            "ON k.session_id=m.session_id AND k.timestamp_ns=m.timestamp_ns "
            "WHERE m.session_id=? AND m.unique_id=? AND k.unique_id=?",
            (session_id, mask_uid, kind_uid),
        )
        counts: dict[tuple[str, int], int] = {}
        fields = catalogue.get("fields") or []
        for _, mask, kind in rows:
            for field in fields:
                bit = int(field["index"]) - 1
                if int(mask or 0) & (1 << bit):
                    key = (str(field["id"]), int(kind or 0))
                    counts[key] = counts.get(key, 0) + 1
        output.append(
            {
                "source_id": int(source_id),
                "status": "MEASURED",
                "counts": [
                    {"metric": metric, "record_kind": kind, "fresh_frames": count}
                    for (metric, kind), count in sorted(counts.items())
                ],
            }
        )
    return output


def build_receipt(
    snapshot: Path,
    *,
    session_id: int,
    project_path: Path,
    source_project_path: Path | None = None,
    parser_path: Path,
    catalogue_path: Path,
    capture_profile: str,
    expected_source_ids: set[int],
) -> dict[str, Any]:
    project_text = project_path.read_text(encoding="utf-8")
    project = json.loads(project_text)
    source_project_text = (
        source_project_path.read_text(encoding="utf-8")
        if source_project_path is not None
        else None
    )
    parser_sha = sha256_file(parser_path)
    catalogue = json.loads(catalogue_path.read_text(encoding="utf-8"))

    with read_only_connection(snapshot) as connection:
        integrity = integrity_check(connection)
        present_tables = _tables(connection)
        missing_tables = sorted(REQUIRED_TABLES - present_tables)
        if missing_tables:
            raise ValueError(f"Historian snapshot lacks required tables: {missing_tables}")
        session = _session(connection, session_id)
        open_session_ids = [
            int(row[0])
            for row in connection.execute(
                "SELECT session_id FROM sessions WHERE ended_at IS NULL ORDER BY session_id"
            )
        ]
        embedded_text = session.get("project_json") or ""
        try:
            embedded_project = json.loads(embedded_text) if embedded_text else None
        except json.JSONDecodeError:
            embedded_project = None
        readings = _count_by_source(connection, session_id)
        raw = _raw_by_source(connection, session_id)
        device_bounds = _counter_bounds(connection, session_id, ("Device time", "device_ms"))
        parser_bounds = _counter_bounds(
            connection, session_id, ("Host parse sequence", "host_parse_seq")
        )
        freshness = _freshness_counts(connection, session_id, catalogue)

    reasons: list[str] = []
    if integrity != "ok":
        reasons.append(f"SQLite integrity check: {integrity}")
    if session.get("ended_at") is None:
        reasons.append("session was still open at snapshot time")
    if open_session_ids:
        reasons.append(f"Historian database had open sessions at snapshot time: {open_session_ids}")
    if embedded_project is None:
        reasons.append("embedded sessions.project_json is absent or invalid")
    elif embedded_project != project:
        reasons.append("embedded project differs from the canonical project")

    reading_by_source = {row["source_id"]: row["reading_rows"] for row in readings}
    raw_by_source = {row["source_id"]: row["raw_bytes"] for row in raw}
    for source_id in sorted(expected_source_ids):
        if reading_by_source.get(source_id, 0) <= 0:
            reasons.append(f"source {source_id} has zero parsed readings")
        if raw_by_source.get(source_id, 0) <= 0:
            reasons.append(f"source {source_id} has zero raw bytes")

    return {
        "schema": "spectrasynq.serial-studio.instrument-receipt.v1",
        "status": "VALID" if not reasons else "INVALID",
        "reasons": reasons,
        "capture_profile": capture_profile,
        "session": {
            "session_id": session_id,
            "project_title": session.get("project_title"),
            "started_at": session.get("started_at"),
            "ended_at": session.get("ended_at"),
            "target_session_open_at_snapshot": session.get("ended_at") is None,
            "recording_active_at_snapshot": bool(open_session_ids),
            "open_session_ids_at_snapshot": open_session_ids,
        },
        "serial_studio": {
            "writer_version": project.get("writerVersion"),
            "project_path": str(project_path.resolve()),
            "project_sha256": sha256_file(project_path),
            "runtime_project_path": str(project_path.resolve()),
            "runtime_project_sha256": sha256_file(project_path),
            "source_project_path": (
                str(source_project_path.resolve()) if source_project_path else None
            ),
            "source_project_sha256": (
                sha256_file(source_project_path) if source_project_path else None
            ),
            "runtime_projection_differs_from_source": (
                source_project_text is not None and source_project_text != project_text
            ),
            "embedded_project_json_sha256": sha256_text(embedded_text) if embedded_text else None,
            "project_drift": embedded_project != project,
            "parser_path": str(parser_path.resolve()),
            "parser_sha256": parser_sha,
            "catalogue_path": str(catalogue_path.resolve()),
            "catalogue_sha256": sha256_file(catalogue_path),
            "sources": _project_sources(project),
            "plugins": {"status": "NOT_INSTRUMENTED", "items": []},
        },
        "snapshot": {
            "path": str(snapshot.resolve()),
            "sha256": sha256_file(snapshot),
            "bytes": snapshot.stat().st_size,
            "sqlite_integrity_check": integrity,
        },
        "counts": {"readings_by_source": readings, "raw_by_source": raw},
        "counter_bounds": {
            "device_time": device_bounds,
            "host_parse_sequence": parser_bounds,
        },
        "freshness": freshness,
        "verdict_boundary": "This receipt scores capture integrity only, not product behaviour.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-db", type=Path, required=True)
    parser.add_argument("--snapshot", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--session-id", type=int, required=True)
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument(
        "--source-project",
        type=Path,
        help="Optional authored source contract used to load the runtime project",
    )
    parser.add_argument("--parser", type=Path, required=True)
    parser.add_argument("--catalogue", type=Path, required=True)
    parser.add_argument("--capture-profile", required=True)
    parser.add_argument("--expected-source-id", type=int, action="append", required=True)
    args = parser.parse_args()

    if args.receipt.exists():
        raise FileExistsError(f"receipt already exists: {args.receipt}")
    freeze_database(args.source_db, args.snapshot)
    receipt = build_receipt(
        args.snapshot,
        session_id=args.session_id,
        project_path=args.project,
        source_project_path=args.source_project,
        parser_path=args.parser,
        catalogue_path=args.catalogue,
        capture_profile=args.capture_profile,
        expected_source_ids=set(args.expected_source_id),
    )
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(
        f"HISTORIAN_RECEIPT={receipt['status']} "
        f"SNAPSHOT_SHA256={receipt['snapshot']['sha256']} RECEIPT={args.receipt}"
    )
    return 0 if receipt["status"] == "VALID" else 2


if __name__ == "__main__":
    raise SystemExit(main())
