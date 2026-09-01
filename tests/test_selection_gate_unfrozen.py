"""Student I/O stays UNFROZEN. C1 does not freeze. Pins must be real."""

from __future__ import annotations

from pathlib import Path

from edgeai.mir.registry import load_registry

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "docs" / "mir" / "SELECTION_GATE.md"


def test_selection_gate_still_unfrozen() -> None:
    text = GATE.read_text(encoding="utf-8")
    assert "UNFROZEN" in text
    assert "not automatic" in text.lower()
    assert "C1 does not freeze" in text
    assert "I/O remains UNFROZEN" in text
    assert "freeze_ready?" in text.lower() or "freeze_ready" in text.lower()
    assert "Unblock map 2026-09-01" in text


def test_no_io_freeze_stamp() -> None:
    text = GATE.read_text(encoding="utf-8")
    lowered = text.lower()
    plain = lowered.replace("*", "")
    assert "student_io_frozen: true" not in lowered
    assert "i/o frozen" not in plain.replace("unfrozen", "")
    assert "do not stamp `lgp_perceptual_validated`" in plain
    assert "| no |" in text
    assert text.count("| no |") >= 9


def test_registry_has_measured_content_sha256() -> None:
    data = load_registry()
    pinned = [
        e
        for e in data["entries"]
        if str(e.get("content_sha256") or "").strip()
        and str(e.get("content_sha256")).upper() != "UNKNOWN"
    ]
    assert pinned, "at least one registry entry must have a non-empty content_sha256"
    for e in pinned:
        h = str(e["content_sha256"]).strip().lower().removeprefix("sha256:")
        assert len(h) == 64
        assert all(c in "0123456789abcdef" for c in h)
        assert e.get("pin_label") == "HOST-ONLY"
