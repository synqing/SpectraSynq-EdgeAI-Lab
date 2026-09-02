"""J3D-A harmonic movement — construct behaviour and receipt bindings."""

import json
from pathlib import Path

import numpy as np
import pytest

from edgeai.mir.harmonic_movement import (
    GM_NON_TONAL_PROGRAM_MIN,
    MOVEMENT_LAG_HOPS,
    cosine_movement,
    is_tonal_instrument,
    l1_rows,
    pitch_class_state,
    tv_movement,
    within_track_rank,
)
from edgeai.mir.note_register import HOP, SR, Note

ROOT = Path(__file__).resolve().parents[1]
R = ROOT / "docs" / "mir" / "receipts" / "harmonic_movement"


def test_percussion_exclusion_rule():
    assert is_tonal_instrument(False, 30) is True          # Distortion Guitar
    assert is_tonal_instrument(True, 0) is False           # drum kit
    assert is_tonal_instrument(False, GM_NON_TONAL_PROGRAM_MIN) is False   # Percussive
    assert is_tonal_instrument(False, 127) is False        # Sound Effects
    assert is_tonal_instrument(False, 111) is True         # last tonal program


def test_state_is_duration_weighted_not_velocity_weighted():
    """Velocity must not move the pitch-class distribution — a crescendo is not
    harmonic movement."""
    quiet = pitch_class_state([Note(0.0, 2.0, 60, 1), Note(0.0, 2.0, 64, 1)], 60)
    loud = pitch_class_state([Note(0.0, 2.0, 60, 127), Note(0.0, 2.0, 64, 127)], 60)
    assert np.allclose(l1_rows(quiet["pc_mass"]), l1_rows(loud["pc_mass"]))


def test_static_chord_produces_zero_movement():
    st = pitch_class_state([Note(0.0, 4.0, 60, 100), Note(0.0, 4.0, 67, 100)], 125)
    m = tv_movement(st["pc_mass"])
    mid = m[int(2.0 * SR / HOP)]
    assert mid == pytest.approx(0.0, abs=1e-9)


def test_chord_change_produces_movement():
    notes = [Note(0.0, 2.0, 60, 100), Note(0.0, 2.0, 64, 100), Note(0.0, 2.0, 67, 100),
             Note(2.0, 4.0, 65, 100), Note(2.0, 4.0, 69, 100), Note(2.0, 4.0, 72, 100)]
    st = pitch_class_state(notes, 125)
    m = tv_movement(st["pc_mass"])
    assert m[int(2.3 * SR / HOP)] > 0.3


def test_silence_is_explicit_never_zero_filled():
    st = pitch_class_state([Note(1.0, 1.2, 60, 100)], 125)
    assert st["silent"].any()
    m = tv_movement(st["pc_mass"])
    assert np.isnan(m[:MOVEMENT_LAG_HOPS]).all(), "the first lag frames have no pair"


def test_movement_is_bounded_and_causal():
    st = pitch_class_state([Note(0.0, 1.0, 60, 100), Note(1.0, 2.0, 61, 100)], 100)
    for fn in (tv_movement, cosine_movement):
        m = fn(st["pc_mass"])
        f = m[np.isfinite(m)]
        assert f.min() >= -1e-9 and f.max() <= 1.0 + 1e-9


def test_within_track_rank_is_per_track():
    g = np.array(["a"] * 5 + ["b"] * 5)
    v = np.array([1.0, 2, 3, 4, 5, 100, 200, 300, 400, 500])
    r = within_track_rank(v, g)
    assert np.allclose(r[:5], r[5:]), "rank must not depend on a track's absolute scale"


# --- receipts ----------------------------------------------------------------


def test_preregistration_declares_velocity_and_lag_before_scores():
    p = json.loads((R / "J3D_A_PREREGISTRATION.json").read_text())
    assert p["written_before_any_score"] is True
    assert "NO velocity weighting" in p["pitch_class_state"]["weighting"]
    assert p["pitch_class_state"]["velocity_justification_declared_before_scores"]
    assert p["timebase"]["movement_lag_hops"] == MOVEMENT_LAG_HOPS
    assert p["timebase"]["lag_justification_declared_before_scores"]
    forbidden = p["construct_validity"]["broader_conclusions_that_remain_FORBIDDEN"]
    for word in ("tension", "melody", "key detection", "tonal centre"):
        assert any(word in f for f in forbidden), f"{word} must stay forbidden"


def test_both_runs_retained_and_v1_not_mutated():
    v1 = json.loads((R / "J3D_A_RESULT_v1.json").read_text())
    v2 = json.loads((R / "J3D_A_RESULT_v2.json").read_text())
    assert v1["outcome"] == "HARMONIC_MOVEMENT_INCONCLUSIVE"
    assert v2.get("run") == "v2"
    assert v1["alignment"]["onset_frame_shift_applied"] == 3, "v1 keeps the defective shift on record"
    assert v2["alignment"]["onset_frame_shift_measured_per_track"] == [1]
    for r in (v1, v2):
        assert r["label"] == "SYNTHETIC_UPPER_BOUND"
        assert r["student_io_frozen"] is False and r["titan"] is False
        assert "NOTHING" in r["what_this_says_about_visual_value"]


def test_defect_record_discloses_that_scores_were_seen():
    d = json.loads((R / "J3D_A_DEFECT_onset_alignment.json").read_text())
    assert d["defect"]["measurement"]["correct_shift"] == 1
    assert d["defect"]["measurement"]["shift_used_in_v1"] == 3
    assert "v1 scores WERE seen" in d["repair_and_its_boundary"]["disclosure"]
    assert "the pre-registered thresholds" in d["repair_and_its_boundary"]["what_is_NOT_being_changed"]


def test_j3d_b_did_not_run_and_invented_no_lever():
    b = json.loads((R / "J3D_B_NOT_RUN_pin_reconnaissance.json").read_text())
    assert b["STATUS"] == "NOT RUN"
    assert b["production_firmware_changed"] is False
    assert "no lever was invented" in b["the_obstacle_this_creates_for_a_future_J3D_B"]["explicitly_not_done_here"]
    assert b["the_only_pinned_harmonic_binding"]["fit"] == "CANDIDATE"
    assert b["the_grammar_status"]["status"] == "partial"
