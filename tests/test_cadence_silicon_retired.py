"""Cadence silicon runner is mechanically retired (D20). Closed means closed."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "gate_c0_cadence_silicon.py"


def test_cadence_runner_source_is_retired() -> None:
    src = SCRIPT.read_text(encoding="utf-8")
    assert "RETIRED: D20 CADENCE CLOSED" in src
    assert "refuse_if_cadence_closed" in src
    assert src.find("refuse_if_cadence_closed()") < src.find("ap.parse_args()")


def test_cadence_runner_execution_dies_before_usb_or_audio() -> None:
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--resume", "--skip-flash", "--skip-restore"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )
    text = proc.stdout + proc.stderr
    assert proc.returncode != 0
    assert "RETIRED: D20 CADENCE CLOSED" in text
    assert "Do not run more silicon cells" in text
    assert "usbmodem" not in text.lower()
    assert "ffplay" not in text.lower()
    assert "AUDIO:" not in text
