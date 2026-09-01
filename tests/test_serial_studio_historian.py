"""Historian snapshot and receipt contract tests."""

from __future__ import annotations

import importlib.util
import json
import sqlite3
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SESSION_19_FIXTURE = (
    ROOT
    / "tools/serial-studio/fixtures/historian/session-19-project-drift.instrument-receipt.json"
)
MODULE_PATH = ROOT / "tools/serial-studio/historian.py"
SPEC = importlib.util.spec_from_file_location("serial_studio_historian", MODULE_PATH)
assert SPEC and SPEC.loader
historian = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(historian)


def _project() -> dict:
    return {
        "writerVersion": "4.0.3",
        "sources": [
            {"sourceId": 0, "title": "Bench", "connection": {"deviceId": {"serial": "BENCH"}}},
            {"sourceId": 1, "title": "Main", "connection": {"deviceId": {"serial": "MAIN"}}},
        ],
    }


def _database(path: Path, project: dict, *, open_session: bool = False) -> None:
    connection = sqlite3.connect(path)
    connection.executescript(
        """
        CREATE TABLE sessions (session_id INTEGER PRIMARY KEY, project_title TEXT NOT NULL,
          started_at TEXT NOT NULL, ended_at TEXT, project_json TEXT, notes TEXT);
        CREATE TABLE columns (column_id INTEGER PRIMARY KEY, session_id INTEGER NOT NULL,
          unique_id INTEGER NOT NULL, source_id INTEGER NOT NULL, source_title TEXT NOT NULL,
          group_title TEXT NOT NULL, title TEXT NOT NULL, units TEXT, widget TEXT,
          is_virtual INTEGER NOT NULL DEFAULT 0);
        CREATE TABLE readings (reading_id INTEGER PRIMARY KEY, session_id INTEGER NOT NULL,
          timestamp_ns INTEGER NOT NULL, unique_id INTEGER NOT NULL, raw_numeric_value REAL,
          raw_string_value TEXT, final_numeric_value REAL, final_string_value TEXT,
          is_numeric INTEGER NOT NULL DEFAULT 1);
        CREATE TABLE raw_bytes (raw_id INTEGER PRIMARY KEY, session_id INTEGER NOT NULL,
          timestamp_ns INTEGER NOT NULL, device_id INTEGER NOT NULL, data BLOB NOT NULL);
        """
    )
    connection.execute(
        "INSERT INTO sessions VALUES (1,'fixture','2026-09-01T00:00:00Z',?,?,NULL)",
        (None if open_session else "2026-09-01T00:01:00Z", json.dumps(project)),
    )
    mask = (1 << 0) | (1 << 17) | (1 << 19) | (1 << 20)
    column_id = 1
    reading_id = 1
    for source_id, title in [(0, "Bench"), (1, "Main")]:
        for offset, field_title, value in [
            (1, "BPM", 132),
            (2, "Update mask", mask),
            (3, "Record kind", 1),
            (4, "Device time", 1000 + source_id),
            (5, "Host parse sequence", 1),
        ]:
            unique_id = 100 * (source_id + 1) + offset
            connection.execute(
                "INSERT INTO columns VALUES (?,?,?,?,?,?,?,?,?,0)",
                (column_id, 1, unique_id, source_id, title, "Decoded forensics", field_title, "", "datagrid"),
            )
            connection.execute(
                "INSERT INTO readings VALUES (?,?,?,?,NULL,NULL,?,NULL,1)",
                (reading_id, 1, 1000, unique_id, value),
            )
            column_id += 1
            reading_id += 1
        connection.execute(
            "INSERT INTO raw_bytes VALUES (?,?,?,?,?)",
            (source_id + 1, 1, 1000, source_id, b"frame\n"),
        )
    connection.commit()
    connection.close()


def _receipt(tmp_path: Path, *, open_session: bool = False) -> dict:
    project = _project()
    source = tmp_path / "live.db"
    snapshot = tmp_path / "snapshot.db"
    project_path = tmp_path / "project.ssproj"
    project_path.write_text(json.dumps(project), encoding="utf-8")
    _database(source, project, open_session=open_session)
    historian.freeze_database(source, snapshot)
    return historian.build_receipt(
        snapshot,
        session_id=1,
        project_path=project_path,
        source_project_path=project_path,
        parser_path=ROOT / "tools/serial-studio/parsers/k1_observe_v1_2.js",
        catalogue_path=ROOT / "tools/serial-studio/schemas/telemetry-catalogue.v1.json",
        capture_profile="PASSIVE_DUAL",
        expected_source_ids={0, 1},
    )


def test_closed_complete_snapshot_is_valid(tmp_path: Path) -> None:
    receipt = _receipt(tmp_path)
    assert receipt["status"] == "VALID"
    assert receipt["snapshot"]["sqlite_integrity_check"] == "ok"
    assert {row["source_id"] for row in receipt["counts"]["raw_by_source"]} == {0, 1}
    assert all(row["raw_bytes"] > 0 for row in receipt["counts"]["raw_by_source"])
    assert all(row["status"] == "MEASURED" for row in receipt["freshness"])
    assert receipt["serial_studio"]["runtime_projection_differs_from_source"] is False
    assert (
        receipt["serial_studio"]["source_project_sha256"]
        == receipt["serial_studio"]["runtime_project_sha256"]
    )


def test_open_session_fails_closed(tmp_path: Path) -> None:
    receipt = _receipt(tmp_path, open_session=True)
    assert receipt["status"] == "INVALID"
    assert "session was still open at snapshot time" in receipt["reasons"]
    assert receipt["session"]["recording_active_at_snapshot"] is True
    assert receipt["session"]["open_session_ids_at_snapshot"] == [1]


def test_snapshot_refuses_overwrite(tmp_path: Path) -> None:
    source = tmp_path / "live.db"
    destination = tmp_path / "snapshot.db"
    _database(source, _project())
    destination.write_bytes(b"owned")
    with pytest.raises(FileExistsError):
        historian.freeze_database(source, destination)
    assert destination.read_bytes() == b"owned"


def test_real_session_19_project_drift_fixture_stays_invalid() -> None:
    receipt = json.loads(SESSION_19_FIXTURE.read_text(encoding="utf-8"))
    assert receipt["status"] == "INVALID"
    assert receipt["reasons"] == ["embedded project differs from the canonical project"]
    assert receipt["serial_studio"]["project_drift"] is True
    assert receipt["session"]["target_session_open_at_snapshot"] is False
    assert receipt["snapshot"]["sqlite_integrity_check"] == "ok"
    assert {row["source_id"] for row in receipt["counts"]["raw_by_source"]} == {0, 1}
    assert all(row["raw_bytes"] > 17_000_000 for row in receipt["counts"]["raw_by_source"])
