"""SSA receipt waves are not ship. Marker must stay in live authority files."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARKER = "SSA_RECEIPT_WAVE_IS_NOT_SHIP"


def test_agents_md_carries_receipt_wave_ban() -> None:
    text = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    assert MARKER in text
    assert "Lxx.md" in text or "L*.md" in text or "lanes/L" in text


def test_session_scar_exists_and_names_the_failure() -> None:
    path = ROOT / "docs/agent/SESSION_SCAR_2026-08-31_SSA_SWARM.md"
    text = path.read_text(encoding="utf-8")
    assert MARKER in text
    assert "147" in text
    assert "bar" in text.lower()
    assert "DONE_WHEN" in text


def test_d23_exists() -> None:
    text = (ROOT / "docs/DECISIONS.md").read_text(encoding="utf-8")
    assert "## D23" in text
    assert MARKER in text or "receipt wave" in text.lower()


def test_parallel_lanes_are_receipts_not_done_when() -> None:
    text = (ROOT / "docs/agent/PARALLEL_LANES.md").read_text(encoding="utf-8")
    assert "not DONE_WHEN" in text or "not a DONE_WHEN" in text
