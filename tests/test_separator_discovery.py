"""J3H asset discovery — a null result must stay a null result."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
R = ROOT / "docs" / "mir" / "receipts" / "separator_conditioning" / "J3H_ASSET_DISCOVERY.json"


def test_outcome_is_the_preregistered_null_category():
    d = json.loads(R.read_text())
    assert d["outcome"] == "REAL_AUDIO_SEPARATOR_INCONCLUSIVE"
    assert d["what_was_found"]["separator_exports"].startswith("NONE")


def test_no_copyrighted_audio_entered_the_repository():
    d = json.loads(R.read_text())
    assert d["copyrighted_audio_committed"] is False
    audio = list((ROOT / "docs").rglob("*.mp3")) + list((ROOT / "docs").rglob("*.wav"))
    assert audio == [], f"audio must never be committed: {audio}"


def test_j3f_is_not_reinterpreted_by_this_job():
    d = json.loads(R.read_text())
    assert d["J3F_mutated"] is False
    assert "never a test of J3F" in d["programme_impact"]["J3F_untouched"]
    j3f = json.loads((ROOT / "docs" / "mir" / "receipts" / "harmonic_observability" /
                      "J3F_RESULT.json").read_text())
    assert j3f["outcome"] == "TIMBRE_FRONTEND_DOMINANT"


def test_the_three_design_traps_are_on_record():
    d = json.loads(R.read_text())
    traps = {t["trap"] for t in d["design_traps_recorded_for_when_J3H_RUNS"]}
    assert "consensus is not truth" in traps
    assert any("taxonom" in t for t in traps)
    assert any("resampling" in t for t in traps)


def test_unblock_set_spans_the_best_and_worst_j3f_families():
    d = json.loads(R.read_text())
    why = " ".join(t["why"] for t in d["what_would_unblock_J3H"]["recommended_track_set_and_why"])
    assert "0.097" in why and "0.591" in why, "the set must be justified against measured J3F families"
    assert "ADVERSARIAL" in why
