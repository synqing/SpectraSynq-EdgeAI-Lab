"""C1 close is a scored dump, not Captain eyes."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_gate_c1_stamp_applied() -> None:
    text = (ROOT / "docs/mir/GATE_C1.md").read_text(encoding="utf-8")
    assert "LGP_PERCEPTUAL_VALIDATED" in text
    assert "**STATUS: CLOSED.**" in text or "STATUS: CLOSED" in text
    assert "Captain eyes" in text or "not Captain" in text.lower()


def test_pixel_rescore_is_pass() -> None:
    rec = json.loads((ROOT / "artifacts/gate_c1/PIXEL_RESCORE.json").read_text())
    assert rec["c0v2"] == "PASS"
    assert rec["Q1"] == "PASS"
    assert rec["Q2"] == "PASS"
    assert rec["Q3"] == "PASS"
    assert rec["audio"] is False
    assert rec["captain_eyes"] is False
    assert rec.get("lgp_perceptual_validated") is True


def test_d25_exists() -> None:
    text = (ROOT / "docs/DECISIONS.md").read_text(encoding="utf-8")
    assert "## D25" in text
    assert "LGP_PERCEPTUAL_VALIDATED" in text
