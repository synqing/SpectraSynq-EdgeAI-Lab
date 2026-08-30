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
