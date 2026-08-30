"""Delay-aware onset scoring. Synthetic clicks only — no recorded audio.

These tests must be able to go RED. A delayed-but-preserved click train is
not a dead onset detector; deleting half the clicks is.
"""

from __future__ import annotations

import numpy as np
import pytest

from edgeai.mir.onset_align import (
    advance_pcm,
    direct_path_lag_samples,
    onset_prf,
    pearson,
    pick_onset_times,
    shift_series,
    xcorr_lag_frames,
)


SR = 16_000


def _click_track(duration_s: float = 3.0, interval_s: float = 0.25, width_ms: float = 5.0):
    n = int(duration_s * SR)
    y = np.zeros(n, dtype=np.float32)
    width = int(width_ms / 1000.0 * SR)
    times = []
    t = 0.2
    while t + 0.05 < duration_s:
        i = int(t * SR)
        click = np.sin(2 * np.pi * 1000 * np.arange(width) / SR).astype(np.float32)
        y[i : i + width] = click
        times.append(t)
        t += interval_s
    return y, np.asarray(times, dtype=np.float32)


def test_direct_path_lag_finds_delayed_impulse():
    rir = np.zeros(SR, dtype=np.float32)
    rir[int(0.08 * SR)] = 1.0
    lag, lag_s = direct_path_lag_samples(rir, SR)
    assert lag == int(0.08 * SR)
    assert abs(lag_s - 0.08) < 1e-6


def test_advance_pcm_undoes_known_delay():
    y, _ = _click_track()
    lag = int(0.08 * SR)
    delayed = np.zeros_like(y)
    delayed[lag:] = y[:-lag]
    recovered = advance_pcm(delayed, lag)
    assert recovered.shape == y.shape
    # Ignore the tail that cannot be recovered.
    err = np.max(np.abs(recovered[:-lag] - y[:-lag]))
    assert err < 1e-6


def test_onset_prf_identical_is_one():
    t = np.array([0.2, 0.45, 0.70, 0.95], dtype=np.float64)
    scores = onset_prf(t, t, window_s=0.05)
    assert scores["f1"] == 1.0
    assert scores["precision"] == 1.0
    assert scores["recall"] == 1.0
    assert scores["n_ref"] == 4
    assert scores["n_est"] == 4


def test_onset_prf_80ms_delay_fails_50ms_window():
    ref = np.array([0.2, 0.45, 0.70, 0.95], dtype=np.float64)
    est = ref + 0.08
    scores = onset_prf(ref, est, window_s=0.05)
    assert scores["f1"] < 0.1
    assert scores["tp"] == 0


def test_onset_prf_80ms_delay_passes_100ms_window():
    ref = np.array([0.2, 0.45, 0.70, 0.95], dtype=np.float64)
    est = ref + 0.08
    scores = onset_prf(ref, est, window_s=0.10)
    assert scores["f1"] == 1.0
    assert scores["mean_jitter_s"] == pytest.approx(0.08, abs=1e-9)


def test_onset_prf_goes_red_when_half_the_clicks_are_deleted():
    ref = np.array([0.2, 0.45, 0.70, 0.95], dtype=np.float64)
    est = ref[::2]
    scores = onset_prf(ref, est, window_s=0.05)
    assert scores["recall"] == pytest.approx(0.5)
    assert scores["precision"] == 1.0
    assert scores["f1"] < 0.8


def test_onset_prf_goes_red_on_false_onsets():
    ref = np.array([0.2, 0.45], dtype=np.float64)
    est = np.array([0.2, 0.45, 0.33, 0.61], dtype=np.float64)
    scores = onset_prf(ref, est, window_s=0.05)
    assert scores["precision"] == pytest.approx(0.5)
    assert scores["recall"] == 1.0


def test_xcorr_lag_frames_recovers_delay():
    rng = np.random.default_rng(0)
    a = rng.normal(size=200).astype(np.float32)
    lag = 7
    b = np.zeros_like(a)
    b[lag:] = a[:-lag]
    got = xcorr_lag_frames(a, b, max_lag_frames=20)
    assert got == lag


def test_shift_series_then_pearson_recovers_delay():
    rng = np.random.default_rng(1)
    a = rng.normal(size=400).astype(np.float32)
    lag = 12
    b = shift_series(a, -lag)  # b is a delayed
    r_raw = pearson(a, b)
    r_al = pearson(a, shift_series(b, lag))
    assert r_al > 0.99
    assert r_al > r_raw + 0.2


def test_delayed_click_train_native_onset_recovers_after_align():
    """The load-bearing product question, on a fixture whose answer is known."""
    from edgeai.mir.conventional import extract_onset_bundle
    from edgeai.mir.live_domain import convolve_rir

    y, click_t = _click_track()
    rir = np.zeros(int(0.2 * SR), dtype=np.float32)
    rir[int(0.08 * SR)] = 1.0
    wet = convolve_rir(y, rir, mix=1.0)
    lag, lag_s = direct_path_lag_samples(rir, SR)
    assert abs(lag_s - 0.08) < 1e-4

    clean_f = extract_onset_bundle(y, sr=SR)
    wet_f = extract_onset_bundle(wet, sr=SR)
    aligned = advance_pcm(wet, lag)
    al_f = extract_onset_bundle(aligned, sr=SR)

    r_zero = pearson(clean_f["onset_env"], wet_f["onset_env"])
    r_al = pearson(clean_f["onset_env"], al_f["onset_env"])
    assert r_al > 0.85
    assert r_al > r_zero

    ref = pick_onset_times(clean_f["onset_env"], clean_f["times"])
    est_u = pick_onset_times(wet_f["onset_env"], wet_f["times"])
    est_a = pick_onset_times(al_f["onset_env"], al_f["times"])
    f1_u = onset_prf(ref, est_u, window_s=0.05)["f1"]
    f1_a = onset_prf(ref, est_a, window_s=0.05)["f1"]
    assert f1_a > 0.8
    assert f1_a > f1_u
    # Detector should see the click train at all.
    assert ref.size >= click_t.size - 2
