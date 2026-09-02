"""J3E — the harmonic colour-transition sandbox must stay a sandbox, and must not
be able to win by being louder."""

import json
from pathlib import Path

import numpy as np
import pytest

from edgeai.mir.harmonic_visual import (
    A_MAX,
    A_MIN,
    BIN_RGB,
    M_REF,
    frame_delta_e,
    pipeline,
    render_strip,
    srgb_to_lab,
    target_colour,
    transition,
)
from edgeai.mir.k1_photons import LED_COUNT

ROOT = Path(__file__).resolve().parents[1]
R = ROOT / "docs" / "mir" / "receipts" / "harmonic_visual"


def _state(bins):
    s = np.zeros((1, 12))
    s[0, bins] = 1.0 / len(bins)
    return s


def test_twelve_frozen_bin_hues():
    assert BIN_RGB.shape == (12, 3)
    assert np.all((BIN_RGB >= 0) & (BIN_RGB <= 1))
    assert not np.allclose(BIN_RGB[0], BIN_RGB[6]), "opposite pitch classes must differ"


def test_movement_never_touches_brightness():
    """The verb is a colour transition. Movement may change WHEN the colour moves,
    never how bright the frame is."""
    s = np.repeat(_state([0, 4, 7]), 40, axis=0)
    slow = pipeline(s, np.zeros(40), with_floor=False)
    fast = pipeline(s, np.full(40, 1.0), with_floor=False)
    # static tonal state: whatever the movement value, the colour is the same
    assert np.allclose(slow["colour"][-1], fast["colour"][-1], atol=1e-9)


def test_photons_are_fixed_so_luminance_carries_nothing():
    c = np.tile(np.array([[0.3, 0.6, 0.2]]), (5, 1))
    leds = render_strip(c)
    assert leds.shape == (5, LED_COUNT, 3)
    assert len({tuple(x) for x in leds[:, 0, :]}) == 1, "identical colour must give identical bytes"


def test_transition_rate_is_bounded_by_the_frozen_constants():
    tgt = np.repeat(np.array([[1.0, 0.0, 0.0]]), 3, axis=0)
    tgt[0] = [0.0, 0.0, 0.0]
    for m, expect in ((0.0, A_MIN), (M_REF * 10, A_MAX)):
        out = transition(tgt, np.full(3, m))
        step = out[1] - out[0]
        assert step[0] == pytest.approx(expect * (1.0 - out[0][0]), rel=1e-6)


def test_chord_change_moves_the_colour_without_the_floor():
    a, b = target_colour(_state([0, 4, 7]), with_floor=False), target_colour(_state([5, 9, 0]), with_floor=False)
    assert np.linalg.norm(a - b) > 0.1


def test_product_floor_extinguishes_the_chord_change():
    """The compatibility pin's own warning, as a test: under the product-faithful
    bloom drive two different chords collapse to the same pixel."""
    a = target_colour(_state([0, 4, 7]), with_floor=True)
    b = target_colour(_state([5, 9, 0]), with_floor=True)
    assert np.linalg.norm(a - b) < 0.1, "if this ever grows, re-read the diagnostic"
    no_floor = np.linalg.norm(target_colour(_state([0, 4, 7]), with_floor=False)
                              - target_colour(_state([5, 9, 0]), with_floor=False))
    assert no_floor > 3.0 * np.linalg.norm(a - b), "the floor must be the dominant mechanism"
    # after the existing HOST preview exposure the two chords land on the same pixel
    from edgeai.mir.harmonic_visual import EXPOSURE
    from edgeai.mir.host_chroma import preview_encode
    pa = preview_encode(render_strip(a)[:, :1, :], exposure=EXPOSURE)[0, 0]
    pb = preview_encode(render_strip(b)[:, :1, :], exposure=EXPOSURE)[0, 0]
    assert np.array_equal(pa, pb), f"expected extinction, got {pa} vs {pb}"


def test_lab_conversion_is_sane():
    assert srgb_to_lab(np.array([255, 255, 255]))[0] == pytest.approx(100.0, abs=0.5)
    assert srgb_to_lab(np.array([0, 0, 0]))[0] == pytest.approx(0.0, abs=0.5)


def test_delta_e_first_frame_is_undefined_not_zero():
    de = frame_delta_e(np.tile(np.array([[0.2, 0.4, 0.6]]), (4, 1)))
    assert np.isnan(de[0])


# --- receipts ---------------------------------------------------------------


def test_preregistration_froze_the_grammar_and_the_fairness_control():
    p = json.loads((R / "J3E_PREREGISTRATION.json").read_text())
    assert p["written_before_any_score"] is True
    assert p["label"] == "HOST_ORACLE_VISUAL_FEASIBILITY"
    fz = p["visual_verb"]["movement_to_transition"]["frozen"]
    assert fz["A_MIN"] == A_MIN and fz["A_MAX"] == A_MAX and fz["M_REF"] == M_REF
    assert "movement modulating brightness" in p["visual_verb"]["movement_to_transition"]["forbidden"]
    assert "FAIRNESS CONTROL" in p["metric"]["response_threshold"]["why"]
    assert p["visual_verb"]["compositor"]["photons"].startswith("HELD FIXED")


def test_M_REF_was_taken_from_the_control_side():
    """A scale taken from the treatment side would tilt the experiment."""
    p = json.loads((R / "J3E_PREREGISTRATION.json").read_text())
    j = p["visual_verb"]["movement_to_transition"]["M_REF_justification"]
    assert "CONTROL side" in j and "cannot favour the oracle" in j


def test_challenge_membership_was_reused_not_reselected():
    r = json.loads((R / "J3E_RESULT.json").read_text())
    assert r["challenge_membership"]["matches"] is True
    assert r["challenge_membership"]["counts"] == r["challenge_membership"]["expected_from_J3D_A_v2"]


def test_result_is_a_sandbox_result_and_says_so():
    r = json.loads((R / "J3E_RESULT.json").read_text())
    assert r["label"] == "HOST_ORACLE_VISUAL_FEASIBILITY"
    assert r["production_firmware_changed"] is False
    assert r["compatibility_pin_changed"] is False
    assert r["product_mode_created"] is False
    assert r["student_io_frozen"] is False and r["titan"] is False
    for s in ("Gate B", "Gate C", "a production effect"):
        assert s in r["what_this_is_not"]


def test_with_floor_degeneracy_is_flagged_not_reported_as_success():
    d = json.loads((R / "J3E_DIAGNOSTIC_product_palette_extinction.json").read_text())
    assert "divide-by-degenerate artefact" in d["the_degenerate_numbers"]["why_they_are_not_a_100_percent_recall"]
    assert d["what_this_supports"]["finding"] == "PRODUCT_HARMONIC_GRAMMAR_GAP"
    assert "lacks visual value" in d["what_this_supports"]["what_it_is_NOT"]
    assert "L6/L7" in d["what_this_supports"]["what_it_is_NOT"]
    assert d["honest_caveats"]


def test_upstream_receipts_untouched():
    hm = ROOT / "docs" / "mir" / "receipts" / "harmonic_movement"
    ct = ROOT / "docs" / "mir" / "receipts" / "chroma_timing"
    assert json.loads((hm / "J3D_A_RESULT_v1.json").read_text())["outcome"] == "HARMONIC_MOVEMENT_INCONCLUSIVE"
    assert json.loads((hm / "J3D_A_RESULT_v2.json").read_text())["outcome"] == "HARMONIC_MOVEMENT_INCONCLUSIVE"
    assert json.loads((ct / "J3D_C1_RESULT.json").read_text())["outcome"] == "CHROMA_PHASE_INCONCLUSIVE"
    assert not (hm / "J3D_A_RESULT_v3.json").exists()
    assert not (ct / "J3D_C1B_RESULT.json").exists()
