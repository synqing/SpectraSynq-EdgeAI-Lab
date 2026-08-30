"""HOST-ONLY 12-bin chroma on the source-oracle hop grid.

Not firmware GDFT. The same series is fed to bloom for every P3-C condition,
so chroma error cannot favour share over RMS.

Causal: each hop uses only samples up to hop end. Timestamp is hop centre.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def _bin_power(frame: NDArray, window: NDArray, pc: NDArray) -> NDArray[np.float64]:
    mag = np.abs(np.fft.rfft(frame * window)) ** 2
    out = np.zeros(12, dtype=np.float64)
    for k in range(12):
        out[k] = float(mag[pc == k].sum())
    return out


def chroma_ref_amp(*, sr: int = 16_000, hop: int = 512, n_fft: int = 2048) -> float:
    """Peak pitch-class amplitude of a 0.5-scale A4 sine. Frozen physical 1.0."""
    t = np.arange(n_fft, dtype=np.float64) / float(sr)
    y = 0.5 * np.sin(2.0 * np.pi * 440.0 * t)
    window = np.hanning(n_fft).astype(np.float64)
    freqs = np.fft.rfftfreq(n_fft, d=1.0 / float(sr))
    with np.errstate(divide="ignore", invalid="ignore"):
        midi = 69.0 + 12.0 * np.log2(np.maximum(freqs, 1e-12) / 440.0)
    pc = np.mod(np.rint(midi).astype(np.int64), 12)
    pc[freqs < 40.0] = -1
    power = _bin_power(y, window, pc)
    return float(np.sqrt(np.max(power)) + 1e-12)


_REF_AMP = None


def host_chroma12(
    pcm: NDArray,
    *,
    sr: int = 16_000,
    hop: int = 512,
    n_fft: int = 2048,
) -> tuple[NDArray[np.float32], NDArray[np.float32]]:
    global _REF_AMP
    y = np.asarray(pcm, dtype=np.float32).reshape(-1)
    n = max(1, int(y.size // hop)) if y.size >= hop else 1
    times = ((np.arange(n, dtype=np.float64) * hop) + hop * 0.5) / float(sr)
    chroma = np.zeros((n, 12), dtype=np.float64)
    window = np.hanning(n_fft).astype(np.float64)
    freqs = np.fft.rfftfreq(n_fft, d=1.0 / float(sr))
    with np.errstate(divide="ignore", invalid="ignore"):
        midi = 69.0 + 12.0 * np.log2(np.maximum(freqs, 1e-12) / 440.0)
    pc = np.mod(np.rint(midi).astype(np.int64), 12)
    pc[freqs < 40.0] = -1
    if _REF_AMP is None:
        _REF_AMP = chroma_ref_amp(sr=sr, hop=hop, n_fft=n_fft)
    ref = _REF_AMP
    for i in range(n):
        end = min(y.size, (i + 1) * hop)
        start = end - n_fft
        frame = np.zeros(n_fft, dtype=np.float64)
        if start < 0:
            take = y[:end]
            frame[-take.size :] = take.astype(np.float64)
        else:
            frame[:] = y[start:end].astype(np.float64)
        power = _bin_power(frame, window, pc)
        chroma[i] = np.clip(np.sqrt(power) / ref, 0.0, 1.0)
    return times.astype(np.float32), chroma.astype(np.float32)


def bloom_chromagram(chroma: NDArray, mix_01: NDArray, *, floor: float = 0.65) -> NDArray[np.float32]:
    """Map HOST pitch-class amps into the range bloom's squared chromagram path can light.

    Firmware bloom does `hsv(..., bin² / 6)` then squares RGB again. A sparse 0.4
    one-hot renders black; a 0.7 broadband fixture does not. This adapter is the
    same for every P3-C condition. It is not firmware GDFT.
    """
    c = np.asarray(chroma, dtype=np.float64)
    mix = np.clip(np.asarray(mix_01, dtype=np.float64).reshape(-1), 0.0, 1.0)
    if c.ndim != 2 or c.shape[1] != 12:
        raise ValueError(f"chroma must be (T,12), got {c.shape}")
    if mix.size != c.shape[0]:
        raise ValueError("mix length must match chroma")
    peak = np.max(c, axis=1, keepdims=True)
    shape = np.divide(c, peak, out=np.zeros_like(c), where=peak > 1e-9)
    gain = 0.12 + 0.88 * mix.reshape(-1, 1)
    drive = gain * (floor + (1.0 - floor) * shape)
    return np.clip(drive, 0.0, 1.0).astype(np.float32)


def host_spectrogram80(
    pcm: NDArray,
    *,
    sr: int = 16_000,
    hop: int = 512,
    n_fft: int = 2048,
    n_bins: int = 80,
) -> tuple[NDArray[np.float32], NDArray[np.float32]]:
    """HOST-ONLY 80-bin log-frequency spectrogram on the oracle hop grid.

    Same causality as host_chroma12. Not firmware GDFT. Identical across P3-C
    versions before the extra-DoF gain is applied.
    """
    y = np.asarray(pcm, dtype=np.float32).reshape(-1)
    n = max(1, int(y.size // hop)) if y.size >= hop else 1
    times = ((np.arange(n, dtype=np.float64) * hop) + hop * 0.5) / float(sr)
    spec = np.zeros((n, n_bins), dtype=np.float64)
    window = np.hanning(n_fft).astype(np.float64)
    freqs = np.fft.rfftfreq(n_fft, d=1.0 / float(sr))
    fmin, fmax = 40.0, max(80.0, float(sr) * 0.5)
    edges = np.geomspace(fmin, fmax, n_bins + 1)
    for i in range(n):
        end = min(y.size, (i + 1) * hop)
        start = end - n_fft
        frame = np.zeros(n_fft, dtype=np.float64)
        if start < 0:
            take = y[:end]
            frame[-take.size :] = take.astype(np.float64)
        else:
            frame[:] = y[start:end].astype(np.float64)
        mag = np.abs(np.fft.rfft(frame * window))
        for k in range(n_bins):
            m = (freqs >= edges[k]) & (freqs < edges[k + 1])
            if np.any(m):
                spec[i, k] = float(mag[m].mean())
    spec = np.log1p(spec)
    # Frozen physical scale: a 0.4-amp broadband frame sits near 1.0.
    spec = np.clip(spec / 4.0, 0.0, 1.0)
    return times.astype(np.float32), spec.astype(np.float32)


def extra_gain(frozen_01: NDArray, *, lo: float = 0.62, hi: float = 1.0) -> NDArray[np.float64]:
    """Map a frozen 0–1 driver into a high visual-gain range.

    Low-range PHOTONS² made the previous page unreadable. This keeps the extra
    DoF identical between energy and share without crushing the floor.
    """
    x = np.clip(np.asarray(frozen_01, dtype=np.float64).reshape(-1), 0.0, 1.0)
    return lo + (hi - lo) * x


def preview_encode(leds: NDArray, *, exposure: float = 2.2) -> NDArray[np.uint8]:
    """HOST preview: exposure + sRGB so a linear dump is readable on a display.

    The firmware dump is pre-gamma. Displaying it raw on sRGB looks near-black.
    This does not change the engine; it is the page's view of the bytes.
    """
    arr = np.asarray(leds, dtype=np.float64) / 255.0
    x = np.clip(arr * float(exposure), 0.0, 1.0)
    a = 0.055
    srgb = np.where(x <= 0.0031308, 12.92 * x, (1.0 + a) * np.power(x, 1.0 / 2.2) - a)
    return np.clip(np.rint(srgb * 255.0), 0, 255).astype(np.uint8)
