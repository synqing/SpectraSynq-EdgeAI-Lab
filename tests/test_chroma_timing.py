"""J3D-C1 — the chroma timing fixture must be independent and self-limiting."""

import json
from pathlib import Path

import numpy as np

from edgeai.mir.note_register import HOP, N_FFT, SR

ROOT = Path(__file__).resolve().parents[1]
R = ROOT / "docs" / "mir" / "receipts" / "chroma_timing"


def test_analytical_frontend_phase_is_arithmetic_not_assertion():
    """frame i window = [(i-3)*hop, (i+1)*hop); centre (i-1)*hop; timestamp (i+0.5)*hop."""
    frames_of_history = N_FFT // HOP
    assert frames_of_history == 4
    i = 100
    win_start = (i + 1) * HOP - N_FFT
    win_end = (i + 1) * HOP
    centre = 0.5 * (win_start + win_end)
    nominal = i * HOP + HOP / 2
    assert (centre - nominal) / HOP == -1.5
    assert round((centre - nominal) / SR * 1000, 1) == -48.0


def test_fixture_never_touched_the_corpus_or_the_hypothesis():
    r = json.loads((R / "J3D_C1_RESULT.json").read_text())
    assert r["used_babyslakh"] is False
    assert r["used_M_tv"] is False
    assert r["optimised_a_lag_against_a_hypothesis"] is False
    p = json.loads((R / "J3D_C1_PREREGISTRATION.json").read_text())
    assert p["written_before_any_fixture_score"] is True
    assert "inspect M_tv" in p["hard_boundary"]["must_not"]


def test_two_independent_estimators_agree_in_sign():
    r = json.loads((R / "J3D_C1_RESULT.json").read_text())
    hr = r["summary"]["offset_hops_half_rise"]["median"]
    ct = r["summary"]["offset_hops_movement_centroid"]["median"]
    assert hr < 0 and ct < 0, "both estimators must agree the residual is negative"
    assert abs(hr - ct) < 0.5, "the two estimators must not disagree materially"


def test_peak_estimator_was_not_used_as_primary():
    """The lag-8 difference of a step is a plateau, so argmax is arbitrary.
    The receipt must name the half-rise crossing as primary."""
    r = json.loads((R / "J3D_C1_RESULT.json").read_text())
    assert "half_rise" in r["primary_estimator"]
    assert r["summary"]["offset_hops_peak"]["iqr"] > 1.0, "peak really is the noisy one"


def test_outcome_is_one_of_the_three_and_gates_c2():
    r = json.loads((R / "J3D_C1_RESULT.json").read_text())
    assert r["outcome"] in {"CHROMA_PHASE_EXPLAINED", "CHROMA_PHASE_NOT_EXPLAINED",
                            "CHROMA_PHASE_INCONCLUSIVE"}
    if r["outcome"] != "CHROMA_PHASE_EXPLAINED":
        assert not (ROOT / "docs" / "mir" / "receipts" / "harmonic_movement" /
                    "J3D_C2_RESULT.json").exists(), "C2 must not exist unless C1 EXPLAINED"


def test_measured_residual_does_not_reach_one_hop():
    """The load-bearing number: a residual smaller than half a hop cannot explain a
    -1 hop argmax on a discrete lag grid."""
    r = json.loads((R / "J3D_C1_RESULT.json").read_text())
    med = r["summary"]["offset_hops_half_rise"]["median"]
    assert -0.5 < med < 0.0, f"measured {med}; if this ever reaches -0.5 the outcome changes"


def test_j3d_a_receipts_untouched_by_this_job():
    h = ROOT / "docs" / "mir" / "receipts" / "harmonic_movement"
    v1 = json.loads((h / "J3D_A_RESULT_v1.json").read_text())
    v2 = json.loads((h / "J3D_A_RESULT_v2.json").read_text())
    assert v1["outcome"] == "HARMONIC_MOVEMENT_INCONCLUSIVE"
    assert v2["outcome"] == "HARMONIC_MOVEMENT_INCONCLUSIVE"
