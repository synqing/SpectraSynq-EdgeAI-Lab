"""J3F instrumentation: per-pitch-class POWER on the host_chroma12 grid.

`host_chroma12` emits a CLIPPED SQUARE ROOT of pitch-class power. The J3F ladder
needs the power itself, because only power is additive across stems:

    |sum_i x_i|^2 = sum_i |x_i|^2 + cross terms

so summing per-stem POWER gives the cross-term-free mixture, and the difference
from running the frontend on the waveform sum isolates exactly the interference.

This module INSTRUMENTS the existing frontend. It does not replace it: the same
sample rate, hop, FFT size, Hann window, 40 Hz floor, nearest-equal-tempered
pitch-class assignment and reference amplitude. `assert_matches_host_chroma12`
proves the equivalence on real audio and is called by the ladder before use.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from .host_chroma import chroma_ref_amp, host_chroma12

SR = 16_000
HOP = 512
N_FFT = 2048
FREQ_FLOOR_HZ = 40.0
_CACHE: dict[tuple[int, int], tuple[NDArray, NDArray]] = {}


def pitch_class_map(*, sr: int = SR, n_fft: int = N_FFT) -> NDArray[np.int64]:
    """Nearest equal-tempered pitch class per rfft bin; -1 below the 40 Hz floor."""
    freqs = np.fft.rfftfreq(n_fft, d=1.0 / float(sr))
    with np.errstate(divide="ignore", invalid="ignore"):
        midi = 69.0 + 12.0 * np.log2(np.maximum(freqs, 1e-12) / 440.0)
    pc = np.mod(np.rint(midi).astype(np.int64), 12)
    pc[freqs < FREQ_FLOOR_HZ] = -1
    return pc


def _fold(sr: int, n_fft: int) -> tuple[NDArray, NDArray]:
    key = (sr, n_fft)
    if key not in _CACHE:
        pc = pitch_class_map(sr=sr, n_fft=n_fft)
        fold = np.zeros((12, pc.size), dtype=np.float64)
        for b in range(12):
            fold[b, pc == b] = 1.0
        _CACHE[key] = (fold, np.hanning(n_fft).astype(np.float64))
    return _CACHE[key]


def pitch_class_power(
    pcm: NDArray, *, sr: int = SR, hop: int = HOP, n_fft: int = N_FFT, block: int = 4096
) -> NDArray[np.float64]:
    """(T, 12) per-pitch-class power. Same frames host_chroma12 uses."""
    y = np.asarray(pcm, dtype=np.float64).reshape(-1)
    n = max(1, int(y.size // hop)) if y.size >= hop else 1
    fold, window = _fold(sr, n_fft)
    out = np.zeros((n, 12), dtype=np.float64)
    for s in range(0, n, block):
        e = min(s + block, n)
        frames = np.zeros((e - s, n_fft), dtype=np.float64)
        for j, i in enumerate(range(s, e)):
            end = min(y.size, (i + 1) * hop)
            start = end - n_fft
            if start < 0:
                take = y[:end]
                if take.size:
                    frames[j, -take.size:] = take
            else:
                frames[j] = y[start:end]
        mag = np.abs(np.fft.rfft(frames * window[None, :], axis=1))
        out[s:e] = (mag**2) @ fold.T
    return out


def power_to_chroma12(power: NDArray, *, sr: int = SR, hop: int = HOP, n_fft: int = N_FFT) -> NDArray[np.float32]:
    """Apply the frontend's own sqrt / reference / clip to pitch-class power."""
    ref = chroma_ref_amp(sr=sr, hop=hop, n_fft=n_fft)
    return np.clip(np.sqrt(np.asarray(power, dtype=np.float64)) / ref, 0.0, 1.0).astype(np.float32)


def assert_matches_host_chroma12(pcm: NDArray, *, atol: float = 1e-5) -> float:
    """Blocking control: the instrumented path must reproduce the frontend."""
    _, ref_chroma = host_chroma12(np.asarray(pcm, dtype=np.float32))
    got = power_to_chroma12(pitch_class_power(pcm))
    n = min(len(ref_chroma), len(got))
    err = float(np.max(np.abs(ref_chroma[:n].astype(np.float64) - got[:n].astype(np.float64))))
    if err > atol:
        raise AssertionError(
            f"instrumented chroma diverges from host_chroma12 by {err:.3g} (> {atol}). "
            "J3F must test the frontend as it is."
        )
    return err
