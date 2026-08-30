"""Delay-aware onset comparison. HOST-ONLY scoring, not a detector for Titan.

A delayed-but-preserved transient sequence can produce low or negative
zero-lag Pearson. Score at native hop, then again after aligning to the
RIR direct-path peak. Event F1 is the product-relevant number.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def pearson(a: NDArray, b: NDArray) -> float:
    a = np.asarray(a, dtype=np.float64).reshape(-1)
    b = np.asarray(b, dtype=np.float64).reshape(-1)
    n = min(a.size, b.size)
    if n < 8:
        return float("nan")
    a = a[:n]
    b = b[:n]
    if a.std() < 1e-12 or b.std() < 1e-12:
        return float("nan")
    return float(np.corrcoef(a, b)[0, 1])


def direct_path_lag_samples(rir: NDArray, sr: int) -> tuple[int, float]:
    """Index and seconds of peak |h|. Causal RIRs: this is the direct-path delay."""
    h = np.asarray(rir, dtype=np.float64).reshape(-1)
    if h.size == 0:
        return 0, 0.0
    lag = int(np.argmax(np.abs(h)))
    return lag, float(lag) / float(sr)


def advance_pcm(pcm: NDArray, lag_samples: int) -> NDArray[np.float32]:
    """Positive lag: signal is late; drop the leading delay, zero-pad the tail."""
    y = np.asarray(pcm, dtype=np.float32).reshape(-1).copy()
    lag = int(lag_samples)
    if lag == 0:
        return y
    out = np.zeros_like(y)
    if lag > 0:
        if lag < y.size:
            out[:-lag] = y[lag:]
        return out
    lead = -lag
    if lead < y.size:
        out[lead:] = y[:-lead]
    return out


def shift_series(x: NDArray, lag_frames: int) -> NDArray[np.float32]:
    """Positive lag: series is late; advance it. Same convention as advance_pcm."""
    y = np.asarray(x, dtype=np.float32).reshape(-1)
    lag = int(lag_frames)
    if lag == 0:
        return y.copy()
    out = np.zeros_like(y)
    if lag > 0:
        if lag < y.size:
            out[:-lag] = y[lag:]
        return out
    lead = -lag
    if lead < y.size:
        out[lead:] = y[:-lead]
    return out


def xcorr_lag_frames(clean: NDArray, wet: NDArray, max_lag_frames: int) -> int:
    """Lag of `wet` relative to `clean` in frames. Positive = wet is later."""
    a = np.asarray(clean, dtype=np.float64).reshape(-1)
    b = np.asarray(wet, dtype=np.float64).reshape(-1)
    n = min(a.size, b.size)
    a = a[:n] - a[:n].mean()
    b = b[:n] - b[:n].mean()
    if n < 8 or a.std() < 1e-12 or b.std() < 1e-12:
        return 0
    max_lag = int(max(0, max_lag_frames))
    corr = np.correlate(b, a, mode="full")
    mid = n - 1
    lo = max(0, mid - max_lag)
    hi = min(corr.size, mid + max_lag + 1)
    sl = corr[lo:hi]
    offsets = np.arange(lo, hi) - mid
    return int(offsets[int(np.argmax(sl))])


def pick_onset_times(
    onset_env: NDArray,
    times: NDArray,
    *,
    wait_s: float = 0.03,
    height: float = 0.2,
    prominence: float = 0.1,
) -> NDArray[np.float64]:
    """Peak-pick a unit-normalised onset envelope. Same params on clean and wet."""
    from scipy.signal import find_peaks

    env = np.asarray(onset_env, dtype=np.float64).reshape(-1)
    t = np.asarray(times, dtype=np.float64).reshape(-1)
    n = min(env.size, t.size)
    env = env[:n]
    t = t[:n]
    if n < 3:
        return np.zeros(0, dtype=np.float64)
    dt = float(np.median(np.diff(t))) if n > 1 else 0.032
    distance = max(1, int(round(wait_s / max(dt, 1e-6))))
    peaks, _ = find_peaks(env, height=height, prominence=prominence, distance=distance)
    return t[peaks].astype(np.float64)


def onset_prf(
    ref_times: NDArray,
    est_times: NDArray,
    window_s: float = 0.05,
) -> dict[str, float]:
    """Greedy nearest-neighbour onset F1. Each ref and each est used at most once."""
    ref = np.sort(np.asarray(ref_times, dtype=np.float64).reshape(-1))
    est = np.sort(np.asarray(est_times, dtype=np.float64).reshape(-1))
    n_ref = int(ref.size)
    n_est = int(est.size)
    if n_ref == 0 and n_est == 0:
        return {
            "precision": 1.0,
            "recall": 1.0,
            "f1": 1.0,
            "tp": 0.0,
            "n_ref": 0.0,
            "n_est": 0.0,
            "mean_jitter_s": float("nan"),
        }
    used = np.zeros(n_est, dtype=bool)
    tp = 0
    jitters: list[float] = []
    for r in ref:
        if n_est == 0:
            break
        d = np.abs(est - r)
        d[used] = np.inf
        j = int(np.argmin(d))
        if np.isfinite(d[j]) and d[j] <= window_s:
            used[j] = True
            tp += 1
            jitters.append(float(est[j] - r))
    fp = n_est - tp
    fn = n_ref - tp
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    return {
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1),
        "tp": float(tp),
        "n_ref": float(n_ref),
        "n_est": float(n_est),
        "mean_jitter_s": float(np.mean(np.abs(jitters))) if jitters else float("nan"),
    }


def downsample_to_times(times_src: NDArray, values: NDArray, times_dst: NDArray) -> NDArray[np.float32]:
    """Linear interpolation onto an arbitrary time grid (the old 2 Hz trap)."""
    t0 = np.asarray(times_src, dtype=np.float64).reshape(-1)
    v = np.asarray(values, dtype=np.float64).reshape(-1)
    t1 = np.asarray(times_dst, dtype=np.float64).reshape(-1)
    if t0.size == 0 or t1.size == 0:
        return np.zeros(t1.size, dtype=np.float32)
    return np.interp(t1, t0, v[: t0.size]).astype(np.float32)
