"""Ground-truth source oracle: presence, dominance, change.

These tests must go RED if we only emit RMS(stem). A buried loud-mix vocal
and a quiet-breakdown vocal can share similar absolute energy and still
differ in dominance.
"""

from __future__ import annotations

import numpy as np
import pytest

from edgeai.mir.source_oracle import SOURCES, log_rms_activity, source_oracle


SR = 16_000
HOP = 512


def _sine(freq: float, n: int, amp: float) -> np.ndarray:
    t = np.arange(n, dtype=np.float32) / SR
    return (amp * np.sin(2 * np.pi * freq * t)).astype(np.float32)


def _clicks(n: int, amp: float, interval_s: float = 0.25) -> np.ndarray:
    y = np.zeros(n, dtype=np.float32)
    step = int(interval_s * SR)
    width = int(0.008 * SR)
    for i in range(0, n - width, step):
        y[i : i + width] = amp
    return y


def test_share_not_abs_when_vocals_are_buried():
    n = SR * 3
    vocals = _sine(220.0, n, 0.08)
    drums = _clicks(n, 0.9)
    bass = _sine(55.0, n, 0.35)
    other = 0.05 * np.random.default_rng(0).normal(size=n).astype(np.float32)
    buried = source_oracle(
        {"vocals": vocals, "drums": drums, "bass": bass, "other": other},
        sr=SR,
        hop=HOP,
    )
    solo = source_oracle(
        {
            "vocals": vocals,
            "drums": np.zeros(n, dtype=np.float32),
            "bass": np.zeros(n, dtype=np.float32),
            "other": np.zeros(n, dtype=np.float32),
        },
        sr=SR,
        hop=HOP,
    )
    # Absolute vocal energy is about the same stem.
    assert abs(float(np.mean(buried["vocals_abs"])) - float(np.mean(solo["vocals_abs"]))) < 0.15
    # Dominance is not.
    assert float(np.mean(solo["vocals_share"])) > 0.85
    assert float(np.mean(buried["vocals_share"])) < 0.35
    assert float(np.mean(solo["vocals_share"])) > float(np.mean(buried["vocals_share"])) + 0.4


def test_share_sums_to_one():
    n = SR * 2
    stems = {
        "vocals": _sine(180.0, n, 0.2),
        "drums": _clicks(n, 0.4),
        "bass": _sine(60.0, n, 0.25),
        "other": _sine(800.0, n, 0.1),
    }
    out = source_oracle(stems, sr=SR, hop=HOP)
    total = sum(out[f"{k}_share"] for k in SOURCES)
    assert np.allclose(total, 1.0, atol=1e-5)


def test_delta_goes_red_when_source_never_enters():
    n = SR * 3
    vocals = np.zeros(n, dtype=np.float32)
    out = source_oracle(
        {
            "vocals": vocals,
            "drums": _clicks(n, 0.5),
            "bass": np.zeros(n, dtype=np.float32),
            "other": np.zeros(n, dtype=np.float32),
        },
        sr=SR,
        hop=HOP,
    )
    assert float(np.max(np.abs(out["vocals_delta"]))) < 0.05


def test_delta_spikes_when_vocals_enter():
    n = SR * 4
    vocals = np.zeros(n, dtype=np.float32)
    enter = int(2.0 * SR)
    vocals[enter:] = _sine(220.0, n - enter, 0.35)
    out = source_oracle(
        {
            "vocals": vocals,
            "drums": _clicks(n, 0.25),
            "bass": _sine(55.0, n, 0.15),
            "other": np.zeros(n, dtype=np.float32),
        },
        sr=SR,
        hop=HOP,
    )
    t = out["times"]
    before = out["vocals_delta"][t < 1.8]
    around = out["vocals_delta"][(t >= 1.8) & (t <= 2.4)]
    assert float(np.max(around)) > 0.2
    assert float(np.max(around)) > float(np.max(np.abs(before))) + 0.1


def test_log_rms_activity_is_physical_not_per_clip_peak():
    quiet = log_rms_activity(np.array([1e-3, 1e-3], dtype=np.float32))
    loud = log_rms_activity(np.array([0.15, 0.15], dtype=np.float32))
    assert quiet[0] < 0.5
    assert loud[0] == pytest.approx(1.0, abs=0.02)
    # A quiet clip must not be stretched to 1.0.
    assert quiet[0] != pytest.approx(1.0, abs=0.2)


def test_composition_change_zero_when_shares_are_constant():
    from edgeai.mir.source_oracle import composition_change, source_oracle

    n = SR * 3
    out = source_oracle(
        {
            "vocals": _sine(220.0, n, 0.3),
            "drums": _sine(150.0, n, 0.3),
            "bass": _sine(55.0, n, 0.3),
            "other": _sine(800.0, n, 0.3),
        },
        sr=SR,
        hop=HOP,
    )
    cc = composition_change(out, lag_s=0.5)
    assert float(np.median(cc[int(0.6 * SR / HOP) :])) < 0.05


def test_composition_change_detects_vocal_handoff_not_loudness():
    from edgeai.mir.source_oracle import composition_change, source_oracle

    n = SR * 4
    vocals = np.zeros(n, dtype=np.float32)
    other = np.zeros(n, dtype=np.float32)
    cut = int(2.0 * SR)
    vocals[:cut] = _sine(220.0, cut, 0.4)
    other[cut:] = _sine(800.0, n - cut, 0.4)
    drums = _sine(180.0, n, 0.15)
    bass = _sine(55.0, n, 0.15)
    out = source_oracle(
        {"vocals": vocals, "drums": drums, "bass": bass, "other": other},
        sr=SR,
        hop=HOP,
    )
    cc = composition_change(out, lag_s=0.5)
    t = out["times"]
    before = cc[t < 1.4]
    around = cc[(t >= 1.9) & (t <= 2.6)]
    assert float(np.max(around)) > 0.3
    assert float(np.max(around)) > float(np.median(before)) + 0.2
    # Mix energy stays in the same ballpark — this is not an RMS event.
    mix_jump = abs(float(out["mix_rms"][np.argmin(np.abs(t - 2.2))]) - float(np.median(out["mix_rms"][t < 1.5])))
    assert mix_jump < 0.25


def test_timebase_is_hop_centre_and_causal():
    from edgeai.mir.source_oracle import timebase

    tb = timebase(sr=16_000, hop=512, lag_s=0.5)
    assert tb["alignment"] == "hop-centre"
    assert tb["causal"] is True
    assert tb["lookahead_s"] == 0.0
    assert tb["composition_change_lag_s"] == 0.5
    assert abs(tb["hop_s"] - 512 / 16_000) < 1e-9


def test_frozen_map_is_not_per_song_minmax():
    from edgeai.mir.visual_hook import apply_frozen_map, fit_frozen_map

    a = np.array([0.10, 0.20, 0.30], dtype=np.float32)
    b = np.array([0.40, 0.80, 0.90], dtype=np.float32)
    spec = fit_frozen_map({"mix_rms": np.concatenate([a, b])})
    fa = apply_frozen_map(a, spec["mix_rms"])
    fb = apply_frozen_map(b, spec["mix_rms"])
    # A quiet-ish series must not be stretched to fill 0–1 by itself.
    assert float(np.ptp(fa)) < 0.5
    assert float(np.max(fb)) > float(np.max(fa))


def test_empty_stems_do_not_nan_the_share():
    n = SR
    out = source_oracle(
        {
            "vocals": np.zeros(n, dtype=np.float32),
            "drums": np.zeros(n, dtype=np.float32),
            "bass": np.zeros(n, dtype=np.float32),
            "other": np.zeros(n, dtype=np.float32),
        },
        sr=SR,
        hop=HOP,
    )
    assert np.all(np.isfinite(out["vocals_share"]))
    assert float(np.max(out["vocals_share"])) == 0.0


def test_oracle_reexports_the_shared_power_primitive():
    from edgeai.mir import source_oracle as oracle_module
    from edgeai.mir.source_power import SOURCES as SHARED_SOURCES
    from edgeai.mir.source_power import frame_mean_square as shared_frame_mean_square

    assert oracle_module.SOURCES is SHARED_SOURCES
    assert oracle_module.frame_mean_square is shared_frame_mean_square
