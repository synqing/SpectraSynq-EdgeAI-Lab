"""Cadence/latency of the extra-DoF driver. These tests must go RED if hold or
delay is a no-op. HOST-ONLY. Not Gate C0. No firmware, no training.
"""

from __future__ import annotations

import numpy as np
import pytest

from edgeai.mir.gate_c_cadence import (
    DELAYS_S,
    DELTA_FLOOR,
    GAIN_HI,
    GAIN_LO,
    HOLD_POLICY,
    HOLD_RATES_HZ,
    HOP_S,
    NATIVE_HZ,
    NATIVE_KEEP_FRACTION,
    SHARE_SOURCES,
    SILICON_DELAY_S,
    SILICON_RATE_HZ,
    actual_delay_s,
    apply_cadence,
    causal_delay,
    cell_passes,
    delay_below_absolute_floor_s,
    delay_cliff_s,
    delay_hops,
    extra_gain_cadence,
    honest_delay_bracket,
    honest_rate_bracket,
    is_native_cell,
    largest_passing_delay_s,
    lowest_passing_rate_hz,
    q_binding_from_summary,
    require_four_source_share,
    slowest_passing_rate_hz,
    summarise_holdout,
    sweep_cells,
    zero_order_hold,
)
from edgeai.mir.p3c_quant import partial_pearson, spearman
from edgeai.mir.p3c_score import head_position_upper


def _sine(hz: float, n: int = 512, hop_s: float = HOP_S) -> np.ndarray:
    t = np.arange(n, dtype=np.float64) * hop_s
    return np.sin(2.0 * np.pi * hz * t)


def _head_leds(series: np.ndarray) -> np.ndarray:
    s = np.clip(np.asarray(series, dtype=np.float64).reshape(-1), 0.0, 1.0)
    leds = np.zeros((s.size, 160, 3), dtype=np.uint8)
    pos = 80 + np.rint(s * 79.0).astype(np.int64)
    for i, p in enumerate(pos):
        leds[i, int(p), :] = 180
    return leds


def test_share_sources_are_four_including_other():
    assert SHARE_SOURCES == ("vocals", "drums", "bass", "other")


def test_four_source_share_rejects_three():
    oracle = {f"{n}_share": np.ones(8) for n in ("vocals", "drums", "bass")}
    with pytest.raises(ValueError, match="other"):
        require_four_source_share(oracle)
    oracle["other_share"] = np.ones(8)
    require_four_source_share(oracle)


def test_native_hold_is_identity():
    x = np.linspace(0.1, 0.9, 200)
    y = zero_order_hold(x, hop_s=HOP_S, rate_hz=NATIVE_HZ)
    assert np.allclose(y, x)


def test_native_cadence_zero_delay_is_identity():
    x = np.linspace(0.0, 1.0, 180)
    y = apply_cadence(x, hop_s=HOP_S, rate_hz=NATIVE_HZ, delay_s=0.0)
    assert np.allclose(y, x)
    assert is_native_cell(NATIVE_HZ, 0.0)


def test_hold_of_sine_drops_spearman():
    """2 Hz hold of a 4 Hz driver must not look like the original. Identity hold goes RED."""
    x = _sine(4.0, n=400)
    held = zero_order_hold(x, hop_s=HOP_S, rate_hz=2.0)
    r_hold = spearman(held, x)
    r_self = spearman(x, x)
    assert r_self > 0.99
    assert r_hold < 0.85
    assert r_hold < r_self - 0.10


def test_slower_hold_drops_spearman_more():
    x = _sine(5.0, n=400)
    r5 = spearman(zero_order_hold(x, hop_s=HOP_S, rate_hz=5.0), x)
    r2 = spearman(zero_order_hold(x, hop_s=HOP_S, rate_hz=2.0), x)
    assert r2 < r5


def test_hold_does_not_read_the_future():
    x = np.arange(80, dtype=np.float64)
    y = zero_order_hold(x, hop_s=HOP_S, rate_hz=5.0)
    for i, v in enumerate(y):
        j = int(round(v))
        assert 0 <= j <= i


def test_delay_shifts_a_spike_later():
    x = np.zeros(80, dtype=np.float64)
    x[20] = 1.0
    y = causal_delay(x, hop_s=HOP_S, delay_s=0.096)  # 3 hops at 32 ms
    assert delay_hops(0.096) == 3
    assert y[23] == pytest.approx(1.0)
    assert y[20] == pytest.approx(0.0)
    assert y[22] == pytest.approx(0.0)


def test_delay_of_sine_drops_spearman():
    """200 ms delay of a 3 Hz driver must not match the original. Identity delay goes RED."""
    x = _sine(3.0, n=400)
    delayed = causal_delay(x, hop_s=HOP_S, delay_s=0.200)
    r0 = spearman(x, x)
    r200 = spearman(delayed, x)
    assert r200 < 0.50
    assert r200 < r0 - 0.40


def test_more_delay_drops_spearman_more():
    x = _sine(3.0, n=400)
    r50 = spearman(causal_delay(x, hop_s=HOP_S, delay_s=0.050), x)
    r200 = spearman(causal_delay(x, hop_s=HOP_S, delay_s=0.200), x)
    assert r200 < r50


def test_delay_is_causal_no_lookahead():
    rng = np.random.default_rng(0)
    x = rng.normal(size=100)
    d = delay_hops(0.100)
    y = causal_delay(x, hop_s=HOP_S, delay_s=0.100)
    assert np.allclose(y[d:], x[:-d])
    assert np.allclose(y[:d], x[0])
    # Mutate a future sample; the present must not move.
    x2 = x.copy()
    x2[-1] = 99.0
    y2 = causal_delay(x2, hop_s=HOP_S, delay_s=0.100)
    assert y2[10] == pytest.approx(y[10])


def test_fifty_ms_quantizes_to_two_hops():
    assert delay_hops(0.050) == 2
    assert actual_delay_s(0.050) == pytest.approx(0.064)


def test_twenty_five_ms_quantizes_to_one_hop():
    assert delay_hops(0.025) == 1
    assert actual_delay_s(0.025) == pytest.approx(0.032)


def test_fifteen_hz_hold_is_not_identity():
    x = np.linspace(0.0, 1.0, 200)
    y = zero_order_hold(x, hop_s=HOP_S, rate_hz=15.0)
    assert not np.allclose(y, x)
    assert np.all(np.diff(np.where(np.diff(y) != 0)[0]) >= 1)


def test_silicon_grid_is_the_named_bracket():
    assert SILICON_RATE_HZ == (20.0, 15.0, 10.0, 5.0)
    assert SILICON_DELAY_S == (0.0, 0.025, 0.050, 0.100, 0.200)
    assert "zero-order-hold" in HOLD_POLICY
    assert "no interpolation" in HOLD_POLICY


def test_q_binding_uses_c0v2_bars_not_host_keep_rate():
    ho = {
        "Q1_knob_is_head_position": "PASS",
        "Q2_share_increment_in_pixels": "PASS",
        "Q3_source_abs_after_mix": "PASS",
    }
    assert q_binding_from_summary(ho)["verdict"] == "PASS"
    ho["Q2_share_increment_in_pixels"] = "FAIL"
    assert q_binding_from_summary(ho)["verdict"] == "FAIL"


def test_honest_brackets_do_not_invent_precision():
    rates = [
        {"rate_hz": 31.25, "verdict": "PASS"},
        {"rate_hz": 20.0, "verdict": "PASS"},
        {"rate_hz": 15.0, "verdict": "PASS"},
        {"rate_hz": 10.0, "verdict": "FAIL"},
        {"rate_hz": 5.0, "verdict": "FAIL"},
    ]
    text = honest_rate_bracket(rates)
    assert "15" in text and "10" in text
    assert "13.7" not in text
    assert slowest_passing_rate_hz(rates) == pytest.approx(15.0)
    delays = [
        {"delay_s": 0.0, "verdict": "PASS"},
        {"delay_s": 0.025, "verdict": "PASS"},
        {"delay_s": 0.050, "verdict": "FAIL"},
        {"delay_s": 0.100, "verdict": "FAIL"},
    ]
    dtext = honest_delay_bracket(delays)
    assert "25" in dtext and "50" in dtext
    assert "49" not in dtext
    assert largest_passing_delay_s(delays) == pytest.approx(0.025)


def test_held_extra_gain_stays_in_p3c_band():
    rng = np.random.default_rng(2)
    frozen = rng.random(120)
    g = extra_gain_cadence(frozen, rate_hz=5.0, delay_s=0.100)
    assert float(g.min()) >= GAIN_LO - 1e-12
    assert float(g.max()) <= GAIN_HI + 1e-12


def test_pass_criterion_needs_both_floors():
    native = 0.63
    assert cell_passes(0.50, native)  # ≥0.15 and ≥0.441
    assert not cell_passes(0.40, native)  # above 0.15 but below 70% of native
    assert not cell_passes(0.10, 0.20)
    assert not cell_passes(float("nan"), native)
    assert NATIVE_KEEP_FRACTION * native == pytest.approx(0.441)
    assert DELTA_FLOOR == pytest.approx(0.15)


def test_lowest_passing_rate_is_the_slowest_that_clears():
    rows = [
        {"rate_hz": 2.0, "pass": False},
        {"rate_hz": 5.0, "pass": False},
        {"rate_hz": 10.0, "pass": True},
        {"rate_hz": 20.0, "pass": True},
        {"rate_hz": 31.25, "pass": True},
    ]
    assert lowest_passing_rate_hz(rows) == pytest.approx(10.0)
    assert lowest_passing_rate_hz([{"rate_hz": 31.25, "pass": False}]) is None


def test_delay_cliff_is_first_fail_above_zero():
    rows = [
        {"delay_s": 0.0, "pass": True},
        {"delay_s": 0.050, "pass": True},
        {"delay_s": 0.100, "pass": False},
        {"delay_s": 0.200, "pass": False},
    ]
    assert delay_cliff_s(rows) == pytest.approx(0.100)
    all_ok = [{"delay_s": d, "pass": True} for d in DELAYS_S]
    assert delay_cliff_s(all_ok) is None
    abs_rows = [
        {"delay_s": 0.0, "median_delta_pos_share": 0.63},
        {"delay_s": 0.050, "median_delta_pos_share": 0.40},
        {"delay_s": 0.100, "median_delta_pos_share": 0.34},
        {"delay_s": 0.200, "median_delta_pos_share": 0.10},
    ]
    assert delay_below_absolute_floor_s(abs_rows) == pytest.approx(0.200)


def test_summarise_holdout_matches_pass_rule():
    native = 0.63
    out = summarise_holdout([0.50, 0.52, 0.48], native_median=native)
    assert out["verdict"] == "PASS"
    assert out["n_finite"] == 3
    bad = summarise_holdout([0.20, 0.22, 0.18], native_median=native)
    assert bad["verdict"] == "FAIL"


def test_sweep_cells_cover_rates_and_delays_without_duplicating_native():
    cells = sweep_cells()
    assert ("rate", NATIVE_HZ, 0.0) in cells
    families = [c[0] for c in cells]
    assert families.count("rate") == len(HOLD_RATES_HZ)
    assert families.count("delay") == len(DELAYS_S) - 1
    assert ("delay", NATIVE_HZ, 0.0) not in cells


def test_synthetic_head_delta_falls_when_share_is_held():
    """Aligned D-vs-B extra DoF shrinks when the share driver is held at 2 Hz.

    Identity hold would keep native Δ and this goes RED.
    """
    n = 250
    t = np.arange(n) * HOP_S
    mix = 0.4 + 0.1 * np.sin(2.0 * np.pi * 0.3 * t)
    share = 0.5 + 0.5 * np.sin(2.0 * np.pi * 4.0 * t)
    leds_b = _head_leds(mix)
    leds_d = _head_leds(share)
    native = partial_pearson(head_position_upper(leds_d), share, mix) - partial_pearson(
        head_position_upper(leds_b), share, mix
    )
    held = apply_cadence(share, hop_s=HOP_S, rate_hz=2.0, delay_s=0.0)
    leds_d_held = _head_leds(held)
    held_delta = partial_pearson(head_position_upper(leds_d_held), share, mix) - partial_pearson(
        head_position_upper(leds_b), share, mix
    )
    assert native > 0.6
    assert held_delta < native - 0.15
