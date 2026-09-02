"""J3F — the frontend must be tested as it is, and the ladder must stay a ladder."""

import json
from pathlib import Path

import numpy as np

from edgeai.mir.chroma_power import (
    FREQ_FLOOR_HZ,
    N_FFT,
    SR,
    assert_matches_host_chroma12,
    pitch_class_map,
    pitch_class_power,
    power_to_chroma12,
)

ROOT = Path(__file__).resolve().parents[1]
R = ROOT / "docs" / "mir" / "receipts" / "harmonic_observability"


def test_instrumented_path_reproduces_the_frontend():
    """host_chroma12 is the OBJECT UNDER TEST. Instrumenting it is allowed;
    substituting different maths is not."""
    rng = np.random.default_rng(0)
    y = rng.standard_normal(SR * 3) * 0.2
    assert assert_matches_host_chroma12(y) <= 1e-5


def test_pitch_class_map_keeps_the_frontend_rules():
    pc = pitch_class_map()
    freqs = np.fft.rfftfreq(N_FFT, d=1.0 / SR)
    assert np.all(pc[freqs < FREQ_FLOOR_HZ] == -1)
    assert set(np.unique(pc[freqs >= FREQ_FLOOR_HZ])) <= set(range(12))


def test_power_is_additive_but_the_waveform_sum_is_not():
    """The whole basis of Q3: |sum x|^2 = sum |x|^2 + cross terms."""
    t = np.arange(SR) / SR
    a = 0.4 * np.sin(2 * np.pi * 261.63 * t)
    b = 0.4 * np.sin(2 * np.pi * 392.00 * t)
    pa, pb, ps = pitch_class_power(a), pitch_class_power(b), pitch_class_power(a + b)
    rel = float(np.mean(np.abs(ps - (pa + pb)) / (ps + 1e-12)))
    assert rel > 0.01, "if cross terms vanished, Q3 would be meaningless"


def test_analytical_resolution_limit_is_arithmetic():
    """Below MIDI 49 a semitone is narrower than one FFT bin at 16 kHz / 2048."""
    bin_hz = SR / N_FFT
    for midi, resolvable in ((28, False), (40, False), (48, False), (49, True), (61, True)):
        lo = 440 * 2 ** ((midi - 0.5 - 69) / 12)
        hi = 440 * 2 ** ((midi + 0.5 - 69) / 12)
        assert ((hi - lo) / bin_hz >= 1.0) is resolvable, midi


def test_single_note_leaks_a_triad():
    """Q0b: one harmonic note already reads as root + fifth + major third."""
    t = np.arange(SR) / SR
    f0 = 440 * 2 ** ((60 - 69) / 12)
    y = sum((1.0 / k) * np.sin(2 * np.pi * f0 * k * t) for k in range(1, 7)) * 0.3
    p = pitch_class_power(y)[SR // (2 * 512):].mean(axis=0)
    p = p / p.sum()
    root = 60 % 12
    assert p[root] > 0.5
    assert p[(root + 7) % 12] > p[(root + 1) % 12], "the fifth must dominate a neighbouring semitone"


# --- receipts ---------------------------------------------------------------


def test_preregistration_named_the_frontend_as_the_object_under_test():
    p = json.loads((R / "J3F_PREREGISTRATION.json").read_text())
    assert p["written_before_any_ladder_metric"] is True
    for f in ("substituting librosa chroma", "HPCP", "CQT", "any second frontend"):
        assert f in p["object_under_test"]["forbidden"]
    assert p["preflight_controls"]["unrendered_oracle_mass_HYPOTHESIS_FALSIFIED"]["verdict"].startswith("FALSIFIED")


def test_ladder_reproduces_j3d_at_the_full_mix_rung():
    """S3 is the J3D condition. If it drifts, the ladder is not measuring the same thing."""
    r = json.loads((R / "J3F_RESULT.json").read_text())
    j3d = json.loads((ROOT / "docs" / "mir" / "receipts" / "harmonic_movement" /
                      "J3D_A_RESULT_v2.json").read_text())
    assert r["Q2_ladder"]["S3_full_mix"]["r2"] == j3d["information"]["M_tv_from_B_chroma_alone"]


def test_ladder_is_monotone_and_mixing_is_the_smaller_cost():
    r = json.loads((R / "J3F_RESULT.json").read_text())
    L = r["Q2_ladder"]
    s1, s2, s3 = (L[k]["r2"] for k in ("S1_aggregate", "S2_pitched_mix", "S3_full_mix"))
    assert s1 >= s2 >= s3, "removing interference must not make observability worse"
    assert (s1 - s3) < s1, "the load-bearing claim: the stem-level ceiling exceeds the total mixing cost"


def test_controls_and_no_forbidden_tool_was_used():
    r = json.loads((R / "J3F_RESULT.json").read_text())
    assert r["controls"]["all_blocking_pass"] is True
    assert r["controls"]["instrumented_chroma_ok"] is True
    assert r["basic_pitch_run"] is False and r["foundation_model_run"] is False
    assert r["student_io_frozen"] is False and r["titan"] is False


def test_interpretation_discloses_the_clause_sequence_and_the_confound():
    d = json.loads((R / "J3F_INTERPRETATION.json").read_text())
    assert d["outcome"] == "TIMBRE_FRONTEND_DOMINANT"
    assert d["family_spread_fills_the_preregistered_clause"]["met"] is True
    assert "disclosure" in d["family_spread_fills_the_preregistered_clause"]
    assert "must NOT be read" in d["confound_that_limits_how_the_absolute_numbers_may_be_read"]["consequence"]
    assert d["Q1_renderer_timing_hypothesis_FALSIFIED"]["verdict"].startswith("NOT systematic")
    assert d["recommended_next_path"]["choice"] == "J3G_EXISTING_STFT_HARMONIC_RECOVERY"
    assert any("CQT" in x for x in d["recommended_next_path"]["explicitly_not_recommended_yet"])


def test_upstream_receipts_untouched():
    hm = ROOT / "docs" / "mir" / "receipts" / "harmonic_movement"
    ct = ROOT / "docs" / "mir" / "receipts" / "chroma_timing"
    hv = ROOT / "docs" / "mir" / "receipts" / "harmonic_visual"
    assert json.loads((hm / "J3D_A_RESULT_v1.json").read_text())["outcome"] == "HARMONIC_MOVEMENT_INCONCLUSIVE"
    assert json.loads((hm / "J3D_A_RESULT_v2.json").read_text())["outcome"] == "HARMONIC_MOVEMENT_INCONCLUSIVE"
    assert json.loads((ct / "J3D_C1_RESULT.json").read_text())["outcome"] == "CHROMA_PHASE_INCONCLUSIVE"
    assert json.loads((hv / "J3E_RESULT.json").read_text())["outcome"] == "HARMONIC_VISUAL_INFORMATION_GAIN"
