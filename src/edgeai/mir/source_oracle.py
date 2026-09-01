"""Perfect-information source oracle from stems. HOST-ONLY. Not a student.

Three channels per source — presence, dominance, change:

    abs   — how much acoustic energy this stem has (fixed log-RMS map)
    share — fraction of summed stem power at this hop (dominance)
    delta — first difference of share (enter / exit / surge)

Share is NOT mix RMS. A moderate vocal in a quiet breakdown can dominate
even when its absolute energy is below a buried vocal in a loud chorus.

Stems can interfere; mixture power is not exactly the sum. Share is
defined on stem powers so it stays in [0, 1] and sums to 1.
"""

from __future__ import annotations

import math
from typing import Mapping

import numpy as np
from numpy.typing import NDArray

from edgeai.dataset import LOUD_RMS, SILENCE_RMS
from edgeai.mir.source_power import SOURCES, frame_mean_square


def _mono(pcm: NDArray) -> NDArray[np.float32]:
    y = np.asarray(pcm, dtype=np.float32)
    if y.ndim == 2:
        y = y.mean(axis=-1)
    return y.reshape(-1)


def frame_rms(pcm: NDArray, sr: int, hop: int = 512) -> tuple[NDArray[np.float32], NDArray[np.float32]]:
    y = _mono(pcm)
    n = max(1, int(y.size // hop)) if y.size >= hop else 1
    times = ((np.arange(n, dtype=np.float32) * hop) + hop * 0.5) / float(sr)
    if y.size < hop:
        times = np.array([0.5 * y.size / sr if y.size else 0.0], dtype=np.float32)
    ms = frame_mean_square(y, hop)
    rms = np.sqrt(ms + 1e-12).astype(np.float32)
    return times[: ms.size], rms


def log_rms_activity(rms: NDArray) -> NDArray[np.float32]:
    """Fixed physical map, not per-clip peak-norm. Same constants as D7 labels."""
    lo = math.log10(SILENCE_RMS)
    hi = math.log10(LOUD_RMS)
    v = (np.log10(np.asarray(rms, dtype=np.float64) + 1e-12) - lo) / (hi - lo)
    return np.clip(v, 0.0, 1.0).astype(np.float32)


def source_oracle(
    stems: Mapping[str, NDArray],
    *,
    sr: int,
    hop: int = 512,
    mix: NDArray | None = None,
) -> dict[str, NDArray[np.float32]]:
    """Return aligned abs / share / delta traces plus mix RMS.

    `stems` must contain vocals, drums, bass, other (missing → zeros).
    `mix` is optional; if given, `mix_rms` is the official mixture envelope.
    """
    first = next(iter(stems.values()))
    n_samples = int(_mono(first).size)
    aligned: dict[str, NDArray[np.float32]] = {}
    for name in SOURCES:
        if name in stems:
            y = _mono(stems[name])
        else:
            y = np.zeros(n_samples, dtype=np.float32)
        if y.size != n_samples:
            out = np.zeros(n_samples, dtype=np.float32)
            m = min(n_samples, y.size)
            out[:m] = y[:m]
            y = out
        aligned[name] = y

    times, _ = frame_rms(aligned["vocals"], sr, hop)
    power = {name: frame_mean_square(aligned[name], hop) for name in SOURCES}
    n = int(times.size)
    for name in SOURCES:
        power[name] = power[name][:n]
    rms = {name: np.sqrt(power[name] + 1e-12).astype(np.float32) for name in SOURCES}

    total = np.sum(np.stack([power[name] for name in SOURCES], axis=0), axis=0)
    silent = total < 1e-10

    out: dict[str, NDArray[np.float32]] = {"times": times.astype(np.float32)}
    for name in SOURCES:
        share = np.zeros(n, dtype=np.float64)
        share[~silent] = power[name][~silent] / total[~silent]
        abs_act = log_rms_activity(rms[name])
        delta = np.diff(share, prepend=share[:1])
        out[f"{name}_abs"] = abs_act
        out[f"{name}_share"] = share.astype(np.float32)
        out[f"{name}_delta"] = delta.astype(np.float32)
        out[f"{name}_rms"] = rms[name].astype(np.float32)

    if mix is None:
        mix_y = np.sum(np.stack([aligned[name] for name in SOURCES], axis=0), axis=0)
    else:
        mix_y = _mono(mix)
        if mix_y.size != n_samples:
            tmp = np.zeros(n_samples, dtype=np.float32)
            m = min(n_samples, mix_y.size)
            tmp[:m] = mix_y[:m]
            mix_y = tmp
    _, mix_r = frame_rms(mix_y, sr, hop)
    out["mix_rms"] = log_rms_activity(mix_r[:n])
    out["mix_rms_raw"] = mix_r[:n].astype(np.float32)
    out["composition_change"] = composition_change(out, lag_s=0.5)
    return out


def share_matrix(oracle: Mapping[str, NDArray]) -> NDArray[np.float64]:
    return np.stack([np.asarray(oracle[f"{name}_share"], dtype=np.float64) for name in SOURCES], axis=1)


def composition_change(oracle: Mapping[str, NDArray], *, lag_s: float = 0.5) -> NDArray[np.float32]:
    """Causal L1/2 distance between the current share vector and the one lag_s ago.

    Range [0, 1]. 1 = complete ownership swap. Timestamp is the current hop centre.
    No lookahead. This is arrangement change, not loudness.
    """
    times = np.asarray(oracle["times"], dtype=np.float64)
    if times.size < 2:
        return np.zeros(times.size, dtype=np.float32)
    hop_s = float(np.median(np.diff(times)))
    lag_frames = max(1, int(round(lag_s / max(hop_s, 1e-6))))
    shares = share_matrix(oracle)
    prev = np.vstack([np.repeat(shares[:1], lag_frames, axis=0), shares[:-lag_frames]])
    prev = prev[: shares.shape[0]]
    l1 = np.sum(np.abs(shares - prev), axis=1)
    return np.clip(0.5 * l1, 0.0, 1.0).astype(np.float32)


def timebase(*, sr: int, hop: int, lag_s: float = 0.5) -> dict:
    """Explicit hop alignment. Standing rule after the PaRIRset zero-lag miss."""
    hop_s = float(hop) / float(sr)
    return {
        "sr": int(sr),
        "hop_samples": int(hop),
        "window_samples": int(hop),
        "window_s": hop_s,
        "hop_s": hop_s,
        "alignment": "hop-centre",
        "causal": True,
        "lookahead_s": 0.0,
        "smoothing": "none",
        "composition_change_lag_s": float(lag_s),
        "timestamp": "seconds at hop centre; composition_change compares to t-lag",
    }
