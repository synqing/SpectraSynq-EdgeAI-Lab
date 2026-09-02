"""J3D-A - causal harmonic movement from exact symbolic pitch-class state.

The construct is CHANGE in the sounding pitch-class collection, not chord
identity, key, tonal centre or tension. Those are separate constructs and this
module deliberately cannot express them.

Weighting is duration-overlap ONLY. Velocity is excluded on purpose: harmonic
identity is which pitch classes sound, not how loudly, and velocity weighting
would let a crescendo register as harmonic movement - the exact confound the
flat-energy challenge class exists to remove.

Timebase is identical to `note_register` / `host_chroma12`: causal frame ending
at (i+1)*hop, hop-centre timestamp, no label lookahead.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from .note_register import HOP, N_FFT, SR, Note

# General MIDI 112-119 Percussive, 120-127 Sound Effects: no reliable tonal content.
GM_NON_TONAL_PROGRAM_MIN = 112
MOVEMENT_LAG_HOPS = 8


def is_tonal_instrument(is_drum: bool, program: int) -> bool:
    return (not is_drum) and int(program) < GM_NON_TONAL_PROGRAM_MIN


def pitch_class_state(
    notes: list[Note],
    n_frames: int,
    *,
    sr: int = SR,
    hop: int = HOP,
    n_fft: int = N_FFT,
) -> dict[str, NDArray]:
    """Duration-weighted 12-D pitch-class state on the causal grid.

    Returns pc_mass (T,12), weight_total (T,), silent (T,) bool.
    A silent frame is SILENT - never a zero vector standing in for one.
    """
    win_s = n_fft / float(sr)
    hop_s = hop / float(sr)
    starts = (np.arange(n_frames, dtype=np.float64) + 1.0) * hop_s - win_s
    ends = (np.arange(n_frames, dtype=np.float64) + 1.0) * hop_s

    mass = np.zeros((n_frames, 12), dtype=np.float64)
    wtot = np.zeros(n_frames, dtype=np.float64)

    for nt in notes:
        if nt.end_s <= nt.start_s:
            continue
        lo = max(int(np.floor((nt.start_s / hop_s) - 1.0)), 0)
        hi = min(int(np.ceil((nt.end_s + win_s) / hop_s)), n_frames)
        if hi <= lo:
            continue
        ov = np.minimum(ends[lo:hi], nt.end_s) - np.maximum(starts[lo:hi], nt.start_s)
        np.clip(ov, 0.0, None, out=ov)
        hit = ov > 0.0
        if not hit.any():
            continue
        idx = np.arange(lo, hi)[hit]
        w = ov[hit]  # duration only - no velocity
        np.add.at(mass, (idx, nt.pitch % 12), w)
        np.add.at(wtot, idx, w)

    return {"pc_mass": mass, "weight_total": wtot, "silent": wtot <= 0.0}


def l1_rows(x: NDArray, *, eps: float = 1e-12) -> NDArray[np.float64]:
    a = np.asarray(x, dtype=np.float64)
    s = np.sum(np.abs(a), axis=1, keepdims=True)
    return np.divide(a, s, out=np.zeros_like(a), where=s > eps)


def tv_movement(state: NDArray, *, lag: int = MOVEMENT_LAG_HOPS) -> NDArray[np.float64]:
    """0.5 * L1 between the L1-normalised state now and `lag` hops ago. [0, 1]."""
    p = l1_rows(state)
    out = np.full(p.shape[0], np.nan)
    if p.shape[0] > lag:
        out[lag:] = 0.5 * np.abs(p[lag:] - p[:-lag]).sum(axis=1)
    return out


def cosine_movement(state: NDArray, *, lag: int = MOVEMENT_LAG_HOPS) -> NDArray[np.float64]:
    """1 - cosine similarity. More sensitive to WHICH classes are present."""
    p = l1_rows(state)
    out = np.full(p.shape[0], np.nan)
    if p.shape[0] > lag:
        a, b = p[lag:], p[:-lag]
        na = np.linalg.norm(a, axis=1) + 1e-12
        nb = np.linalg.norm(b, axis=1) + 1e-12
        out[lag:] = 1.0 - (a * b).sum(axis=1) / (na * nb)
    return out


def lagged_abs_delta(x: NDArray, *, lag: int = MOVEMENT_LAG_HOPS) -> NDArray[np.float64]:
    a = np.asarray(x, dtype=np.float64).reshape(-1)
    out = np.full(a.size, np.nan)
    if a.size > lag:
        out[lag:] = np.abs(a[lag:] - a[:-lag])
    return out


def rectified_flux(spec: NDArray, *, lag: int = MOVEMENT_LAG_HOPS) -> NDArray[np.float64]:
    """Positive-part spectral flux over the existing host_spectrogram80 frames."""
    s = np.asarray(spec, dtype=np.float64)
    out = np.full(s.shape[0], np.nan)
    if s.shape[0] > lag:
        d = s[lag:] - s[:-lag]
        out[lag:] = np.clip(d, 0.0, None).sum(axis=1)
    return out


def within_track_rank(values: NDArray, groups: NDArray) -> NDArray[np.float64]:
    """Percentile rank inside each track, so track scaling cannot make a class."""
    v = np.asarray(values, dtype=np.float64)
    r = np.full(v.size, np.nan)
    for g in np.unique(groups):
        m = (groups == g) & np.isfinite(v)
        if not m.any():
            continue
        x = v[m]
        order = np.argsort(np.argsort(x))
        r[m] = order / max(len(x) - 1, 1)
    return r
