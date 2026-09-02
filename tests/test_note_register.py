"""J3A note/register representation — causality, arithmetic, and receipt bindings."""

import json
from pathlib import Path

import numpy as np
import pytest

from edgeai.mir.note_register import (
    HOP,
    N_FFT,
    SR,
    Note,
    dsp_register_features,
    frame_grid,
    l1_normalise,
    midi_targets,
    silence_mask,
)

ROOT = Path(__file__).resolve().parents[1]
RECEIPTS = ROOT / "docs" / "mir" / "receipts" / "note_register"
PREREG = RECEIPTS / "PREREGISTRATION.json"


def test_grid_matches_the_repo_oracle_convention():
    times, ends = frame_grid(SR * 2)
    assert times.size == (SR * 2) // HOP
    # hop-centre timestamps, frame ends at (i+1)*hop - same as host_chroma12
    assert times[0] == pytest.approx((HOP * 0.5) / SR)
    assert ends[0] == HOP


def test_labels_never_see_the_future():
    n = 62
    _, _ = frame_grid(SR * 2)
    onset = 1.5
    r = midi_targets([Note(onset, onset + 0.1, 72, 100)], n)
    ends_s = (np.arange(n) + 1) * HOP / SR
    # a frame whose window has entirely closed before the note sounds must be untouched
    assert float(r["weight_total"][ends_s <= onset].sum()) == 0.0


def test_register_centroid_is_velocity_weighted_mean_midi_number():
    n = 62
    r = midi_targets([Note(0.5, 1.0, 60, 100), Note(0.5, 1.0, 64, 100)], n)
    i = int(0.75 * SR / HOP)
    assert r["register_centroid"][i] == pytest.approx(62.0, abs=1e-6)


def test_silent_frames_are_undefined_not_zero():
    r = midi_targets([Note(0.5, 0.6, 60, 100)], 62)
    quiet = r["weight_total"] == 0
    assert quiet.any()
    assert np.isnan(r["register_centroid"][quiet]).all(), "no note != register 0"


def test_l1_normalise_is_safe_on_empty_rows():
    x = np.zeros((3, 12))
    x[1, 3] = 2.0
    y = l1_normalise(x)
    assert y[0].sum() == 0.0
    assert y[1, 3] == pytest.approx(1.0)


def test_dsp_register_features_are_causal_and_named():
    y = np.zeros(SR, dtype=np.float64)
    y[SR // 2 :] = np.sin(2 * np.pi * 440 * np.arange(SR // 2) / SR)
    feats, rms, names = dsp_register_features(y)
    assert len(names) == feats.shape[1] == 6
    assert "log_centroid" in names and "log_rolloff85" in names
    # nothing before the tone should register above the silence floor
    ends = (np.arange(len(rms)) + 1) * HOP
    pre = ends <= (SR // 2) - N_FFT
    assert not silence_mask(rms[pre]).any()


def test_chroma_is_never_used_as_the_register_comparator():
    """Octave-folded chroma cannot represent register; using it would manufacture a PASS."""
    prereg = json.loads(PREREG.read_text())
    h2 = prereg["hypotheses"]["H2_register"]
    assert "chroma" not in h2["primary_comparator_B1"].lower()
    assert "FORBIDDEN" in h2["note"]


def test_preregistration_was_written_before_any_score():
    prereg = json.loads(PREREG.read_text())
    assert prereg["written_before_any_score"] is True
    assert prereg["label"] == "SYNTHETIC_UPPER_BOUND"
    assert len(prereg["pre_registered_outcomes"]) >= 5


def test_amendments_disclose_whether_scores_had_been_seen():
    prereg = json.loads(PREREG.read_text())
    for a in prereg.get("amendments", []):
        assert "amended_before_any_hypothesis_score_was_seen" in a
        if a["amended_before_any_hypothesis_score_was_seen"] is False:
            assert "DISCLOSURE" in a, "a post-hoc amendment must disclose itself"


def test_both_receipts_are_retained_and_the_original_is_not_rewritten():
    v1 = json.loads((RECEIPTS / "J3A_RESULT_v1.json").read_text())
    v2 = json.loads((RECEIPTS / "J3A_RESULT_v2.json").read_text())
    assert v1["verdict"] == "INVALID_RUN", "the pre-amendment record must stand as it fell"
    assert v1["H1_pitch_class"]["verdict"].startswith("NOT_ISSUED")
    assert v2["label"] == "SYNTHETIC_UPPER_BOUND"
    for r in (v1, v2):
        assert r["student_io_frozen"] is False
        assert r["titan"] is False


def test_synthetic_result_cannot_be_read_as_selection_gate_criterion_3():
    v2 = json.loads((RECEIPTS / "J3A_RESULT_v2.json").read_text())
    assert "criterion 3" in v2["interpretation_ceiling"]
    assert v2["label"] == "SYNTHETIC_UPPER_BOUND"


# --- J3C ---------------------------------------------------------------------

J3C_PREREG = RECEIPTS / "J3C_PREREGISTRATION.json"
J3C_RESULT = RECEIPTS / "J3C_RESULT.json"
J3C_DIAG = RECEIPTS / "J3C_DIAGNOSTIC_target_validity.json"


def test_spec80_midi_axis_matches_the_frontend_binning():
    from edgeai.mir.note_register import spec80_midi_positions

    m = spec80_midi_positions()
    assert m.size == 80
    assert 27.0 < m[0] < 29.0 and 118.0 < m[-1] < 120.0
    assert np.all(np.diff(m) > 0)


def test_harmonic_sum_removes_the_upward_harmonic_bias():
    """E4's whole justification: a plain centroid over a harmonic series reads
    far above the fundamental; subharmonic summation must not."""
    from edgeai.mir.note_register import (
        harmonic_sum_spectrum,
        spec80_midi_positions,
        weighted_centroid,
    )

    m = spec80_midi_positions()
    w = np.zeros((1, 80))
    for k in range(1, 6):
        f = 440 * 2 ** ((60 - 69) / 12) * k
        w[0, int(np.argmin(np.abs(m - (69 + 12 * np.log2(f / 440)))))] = 1.0 / k
    S, grid = harmonic_sum_spectrum(w, m)
    peak = grid[int(np.argmax(S[0]))]
    plain = float(weighted_centroid(w, m)[0])
    assert abs(peak - 60.0) < 2.0, "harmonic sum must peak at the fundamental"
    assert plain - peak > 5.0, "the plain centroid must show the bias E4 exists to remove"


def test_j3c_preregistration_states_construct_validity_before_scoring():
    p = json.loads(J3C_PREREG.read_text())
    assert p["written_before_any_score"] is True
    cv = p["construct_validity"]
    for k in (
        "exact_construct_under_test",
        "representation_used_as_proxy_for_register",
        "why_that_proxy_has_sufficient_construct_validity_FOR_THIS_QUESTION",
        "what_a_PASS_permits",
        "what_a_FAIL_permits",
        "broader_conclusions_that_remain_FORBIDDEN",
    ):
        assert k in cv and cv[k], f"construct-validity field {k} missing"
    assert any("valuable" in s or "value" in s for s in cv["broader_conclusions_that_remain_FORBIDDEN"])


def test_j3c_result_cannot_be_read_as_a_value_claim():
    r = json.loads(J3C_RESULT.read_text())
    assert r["label"] == "SYNTHETIC_UPPER_BOUND"
    assert "NOTHING" in r["what_this_says_about_visual_value"]
    assert r["outcome"] in {
        "REGISTER_FRONTEND_DSP",
        "REGISTER_FRONTEND_LATENT",
        "REGISTER_FRONTEND_INSUFFICIENT",
        "REGISTER_INCONCLUSIVE",
    }
    assert r["student_io_frozen"] is False and r["titan"] is False


def test_j3c_diagnostic_keeps_falsified_and_supported_apart():
    d = json.loads(J3C_DIAG.read_text())
    assert d["hypothesis_FALSIFIED"]["verdict"].startswith("FALSIFIED")
    assert d["hypothesis_SUPPORTED"]["verdict"].startswith("SUPPORTED")
    # the load-bearing number: top and bottom voice move independently
    assert d["correlations"]["highest_voice_vs_lowest_voice"] < 0.20
    assert "register is absent from this frontend" in d["consequence_for_reading_J3C"]["the_forbidden_inference"]
