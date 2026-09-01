"""Tests for the independent Serial Studio zero-TX witness."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools/serial-studio/zero_tx_witness.py"
SPEC = importlib.util.spec_from_file_location("serial_studio_zero_tx_witness", MODULE_PATH)
assert SPEC and SPEC.loader
witness = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = witness
SPEC.loader.exec_module(witness)


def test_trace_parser_separates_uart_writes_from_coverage_writes() -> None:
    trace = """
14:01:00.000 write F=89 B=4096 /tmp/session.db Serial-Studio-Pro.1
14:01:00.010 read F=62 B=512 /dev/cu.usbmodem1401 Serial-Studio-Pro.2
14:01:00.020 write_nocancel F=91 B=128 /tmp/session.csv Serial-Studio-Pro.3
"""
    result = witness.parse_trace(trace, {62, 64})
    assert result["write_events_any_fd"] == 2
    assert result["target_write_events"] == []
    assert result["target_write_bytes"] == 0


def test_target_write_forces_receipt_failure() -> None:
    trace = """
14:01:00.000 write F=89 B=4096 /tmp/session.db Serial-Studio-Pro.1
14:01:00.010 write F=62 B=0x10 /dev/cu.usbmodem1401 Serial-Studio-Pro.2
"""
    receipt = witness.build_receipt(
        pid=123,
        devices=["/dev/cu.usbmodem1401", "/dev/cu.usbmodem12201"],
        duration_s=60,
        before={"/dev/cu.usbmodem1401": 62, "/dev/cu.usbmodem12201": 64},
        after={"/dev/cu.usbmodem1401": 62, "/dev/cu.usbmodem12201": 64},
        trace=trace,
        returncode=0,
    )
    assert receipt["status"] == "FAIL"
    assert receipt["reasons"] == ["HOST_TO_DUT_WRITE_OBSERVED"]
    assert receipt["measurement"]["target_write_bytes"] == 16


def test_descriptor_drift_and_empty_coverage_fail_closed() -> None:
    receipt = witness.build_receipt(
        pid=123,
        devices=["/dev/a", "/dev/b"],
        duration_s=60,
        before={"/dev/a": 5, "/dev/b": 6},
        after={"/dev/a": 7, "/dev/b": 6},
        trace="",
        returncode=0,
    )
    assert receipt["status"] == "FAIL"
    assert "UART_DESCRIPTOR_DRIFT" in receipt["reasons"]
    assert "TRACE_COVERAGE_EMPTY" in receipt["reasons"]
    assert "WRITE_SYSCALL_COVERAGE_UNPROVEN" in receipt["reasons"]


def test_target_descriptor_lifecycle_churn_fails_even_when_endpoints_match() -> None:
    trace = """
14:01:00.000 write F=89 B=4096 /tmp/session.db Serial-Studio-Pro.1
14:01:00.010 close F=62 /dev/cu.usbmodem1401 Serial-Studio-Pro.2
14:01:00.020 open F=72 /dev/cu.usbmodem1401 Serial-Studio-Pro.2
"""
    receipt = witness.build_receipt(
        pid=123,
        devices=["/dev/cu.usbmodem1401", "/dev/cu.usbmodem12201"],
        duration_s=60,
        before={"/dev/cu.usbmodem1401": 62, "/dev/cu.usbmodem12201": 64},
        after={"/dev/cu.usbmodem1401": 62, "/dev/cu.usbmodem12201": 64},
        trace=trace,
        returncode=0,
    )
    assert receipt["status"] == "FAIL"
    assert "UART_DESCRIPTOR_LIFECYCLE_CHURN" in receipt["reasons"]
    assert len(receipt["measurement"]["target_descriptor_lifecycle_events"]) == 2


def test_historian_progress_requires_both_uart_sources() -> None:
    before = {
        "session_id": 5,
        "sources": {"0": {"raw_rows": 10, "raw_bytes": 100}, "1": {"raw_rows": 20, "raw_bytes": 200}},
    }
    after = {
        "session_id": 5,
        "sources": {"0": {"raw_rows": 11, "raw_bytes": 110}, "1": {"raw_rows": 22, "raw_bytes": 240}},
    }
    progress = witness.historian_progress(before, after)
    assert progress["progressed"] is True
    after["sources"]["1"] = before["sources"]["1"]
    assert witness.historian_progress(before, after)["progressed"] is False


def test_historian_continuity_fails_one_stalled_interval() -> None:
    samples = [
        {"session_id": 5, "sources": {"0": {"raw_rows": 10, "raw_bytes": 100}, "1": {"raw_rows": 20, "raw_bytes": 200}}},
        {"session_id": 5, "sources": {"0": {"raw_rows": 11, "raw_bytes": 110}, "1": {"raw_rows": 21, "raw_bytes": 220}}},
        {"session_id": 5, "sources": {"0": {"raw_rows": 12, "raw_bytes": 120}, "1": {"raw_rows": 21, "raw_bytes": 220}}},
    ]
    continuity = witness.historian_continuity(samples)
    assert continuity["interval_count"] == 2
    assert continuity["continuous"] is False
