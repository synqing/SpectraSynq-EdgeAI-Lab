"""P3-C quantitative close: extra DoF in pixels, not r(pixels, driver)."""

from __future__ import annotations

import numpy as np
import pytest

from edgeai.mir.p3c_quant import f1_at_tol, partial_pearson, pearson, score_clip, spearman, summarise
from edgeai.mir.p3c_score import frame_luminance, head_position_upper


def test_head_position_is_nan_when_dark():
    leds = np.zeros((4, 160, 3), dtype=np.uint8)
    pos = head_position_upper(leds)
    assert pos.shape == (4,)
    assert np.all(np.isnan(pos))


def test_head_position_tracks_a_bright_tip():
    leds = np.zeros((1, 160, 3), dtype=np.uint8)
    leds[0, 150, :] = 200
    pos = head_position_upper(leds)
    assert pos[0] == pytest.approx(70.0)  # 150 - 80


def test_partial_pearson_near_zero_when_share_is_mix():
    rng = np.random.default_rng(0)
    mix = rng.normal(size=400)
    x = mix + 0.15 * rng.normal(size=400)
    share = mix + 0.15 * rng.normal(size=400)
    r = partial_pearson(x, share, mix)
    assert abs(r) < 0.2


def test_partial_pearson_recovers_unique_share():
    rng = np.random.default_rng(1)
    mix = rng.normal(size=300)
    share = rng.normal(size=300)
    x = 0.2 * mix + 0.8 * share
    r_raw = pearson(x, share)
    r_part = partial_pearson(x, share, mix)
    assert r_part > 0.7
    assert r_part == pytest.approx(r_raw, abs=0.15)


def test_spearman_handles_monotone_not_linear():
    x = np.linspace(0, 1, 80)
    y = x**3
    assert spearman(x, y) > 0.95


def test_f1_at_tol_is_one_for_matched_peaks():
    assert f1_at_tol([10, 20], [11, 19], tol=3) == pytest.approx(1.0)
    assert f1_at_tol([10], [50], tol=3) == 0.0
    assert f1_at_tol([], []) != f1_at_tol([], [])  # NaN


def test_score_clip_does_not_pass_on_raw_share_correlation():
    n = 120
    t = np.arange(n) * 0.032
    mix = np.linspace(0, 1, n)
    share = np.sin(np.linspace(0, 6.0, n)) * 0.5 + 0.5
    # B lights follow mix; D lights follow share. That is the extra-DoF we want.
    leds_b = np.zeros((n, 160, 3), dtype=np.uint8)
    leds_d = np.zeros((n, 160, 3), dtype=np.uint8)
    for i in range(n):
        pb = 80 + int(round(mix[i] * 79))
        pd = 80 + int(round(share[i] * 79))
        leds_b[i, pb, :] = 180
        leds_d[i, pd, :] = 180
    leds = {
        "A": leds_b,
        "B": leds_b,
        "D": leds_d,
        "control": leds_b,
        "mir": leds_d,
        "gain_A": np.full(n, 0.81),
        "gain_B": 0.62 + 0.38 * mix,
        "gain_D": 0.62 + 0.38 * share,
    }
    oracle = {
        "times": t,
        "mix_rms": mix,
        "vocals_share": share,
        "vocals_abs": share * 0.8 + 0.1,
        "composition_change": np.zeros(n),
        "drums_abs": np.zeros(n),
    }
    meta = {
        "track": "synth",
        "set": "holdout",
        "share_driver": "vocals_share",
        "n": n,
        "start_s": 0.0,
        "mad_B_vs_D": 5.0,
        "mad_control_vs_mir": 2.0,
        "triggers_control": 2,
        "triggers_mir": 2,
    }
    rec = score_clip(leds, oracle, meta)
    assert rec["delta_pos_share"] > 0.4
    assert rec["partial_D_pos_share_mix"] > rec["partial_B_pos_share_mix"]
    # Raw r(D, share) would also be high; the pass is the *delta after mix*.
    summary = summarise([rec])
    assert summary["holdout"]["Q2_share_increment_in_pixels"] == "PASS"
    assert "share_x_waveform_tempo_x_head_position" in summary["stamps"]
    assert "composition_change_x_comet_x_impact_launch" in summary["stamps"]
    assert "composition_change_events" not in summary["stamps"]


def test_frame_luminance_shape():
    leds = np.full((3, 160, 3), 10, dtype=np.uint8)
    lum = frame_luminance(leds)
    assert lum.shape == (3,)
    assert float(lum[0]) == pytest.approx(10.0)
