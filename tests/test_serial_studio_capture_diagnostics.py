"""Tests for freshness-normalised Serial Studio capture diagnostics."""

from __future__ import annotations

import importlib.util
import sqlite3
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools/serial-studio/capture_diagnostics.py"
SPEC = importlib.util.spec_from_file_location("serial_studio_capture_diagnostics", MODULE_PATH)
assert SPEC and SPEC.loader
diagnostics = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = diagnostics
SPEC.loader.exec_module(diagnostics)


def test_diagnostics_use_update_mask_and_valid_uptime(tmp_path: Path) -> None:
    database = tmp_path / "capture.db"
    with sqlite3.connect(database) as connection:
        connection.executescript(
            """
            CREATE TABLE sessions (
              session_id INTEGER PRIMARY KEY, project_title TEXT,
              started_at TEXT, ended_at TEXT
            );
            CREATE TABLE columns (
              session_id INTEGER, source_id INTEGER, unique_id INTEGER,
              title TEXT, group_title TEXT
            );
            CREATE TABLE readings (
              session_id INTEGER, timestamp_ns INTEGER, unique_id INTEGER,
              final_numeric_value REAL
            );
            CREATE TABLE raw_bytes (
              session_id INTEGER, timestamp_ns INTEGER, device_id INTEGER, data BLOB
            );
            INSERT INTO sessions VALUES (1,'fixture','start','end');
            INSERT INTO raw_bytes VALUES (1,0,0,X'01'),(1,60000000000,0,X'02');
            """
        )
        titles = [
            "BPM", "Legacy mixed confidence", "Lock", "Onset",
            "Bass onset", "Peak envelope", "Update mask",
        ]
        for unique_id, title in enumerate(titles, 1):
            connection.execute(
                "INSERT INTO columns VALUES (1,0,?,?,?)",
                (unique_id, title, "Bench decoded forensics"),
            )
        full_mask = sum(1 << (slot - 1) for _, slot, _ in diagnostics.FIELDS.values())
        mask_uid = len(titles)
        values = {
            "BPM": [120, 121],
            "Legacy mixed confidence": [0.8, 0.9],
            "Lock": [1, 0],
            "Onset": [1, 0],
            "Bass onset": [0, 1],
            "Peak envelope": [0.2, 0.4],
        }
        for timestamp, index in [(0, 0), (1_000_000_000, 1)]:
            connection.execute(
                "INSERT INTO readings VALUES (1,?,?,?)",
                (timestamp, mask_uid, full_mask),
            )
            for unique_id, title in enumerate(titles[:-1], 1):
                connection.execute(
                    "INSERT INTO readings VALUES (1,?,?,?)",
                    (timestamp, unique_id, values[title][index]),
                )

    result = diagnostics.summarise(database, 1)
    source = result["sources"][0]
    assert source["valid_uptime_s"] == 60
    assert source["metrics"]["onset"]["fresh_updates"] == 2
    assert source["metrics"]["onset"]["high_fresh_updates"] == 1
    assert source["metrics"]["onset"]["high_fraction"] == 0.5
    assert source["metrics"]["onset"]["high_updates_per_valid_minute"] == 1.0
