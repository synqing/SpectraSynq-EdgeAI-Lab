"""Pixel-dump scores. Captain is not the validator for 'did the bytes change'."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def mean_abs_diff(a: NDArray, b: NDArray) -> float:
    x = np.asarray(a, dtype=np.int16)
    y = np.asarray(b, dtype=np.int16)
    if x.shape != y.shape:
        raise ValueError("shape mismatch")
    return float(np.mean(np.abs(x - y)))


def mean_luminance(leds: NDArray) -> float:
    arr = np.asarray(leds, dtype=np.float64)
    return float(np.mean(0.2126 * arr[..., 0] + 0.7152 * arr[..., 1] + 0.0722 * arr[..., 2]))


def occupancy(leds: NDArray, thresh: int = 8) -> float:
    arr = np.asarray(leds, dtype=np.uint8)
    lit = np.max(arr, axis=-1) >= thresh
    return float(np.mean(lit))


def luminance_map(leds: NDArray) -> NDArray[np.float64]:
    """Rec. 709 luma per LED. Shape (T, N)."""
    arr = np.asarray(leds, dtype=np.float64)
    if arr.ndim != 3 or arr.shape[-1] != 3:
        raise ValueError(f"leds must be (T,N,3), got {arr.shape}")
    return 0.2126 * arr[..., 0] + 0.7152 * arr[..., 1] + 0.0722 * arr[..., 2]


def frame_luminance(leds: NDArray) -> NDArray[np.float64]:
    return luminance_map(leds).mean(axis=1)


def head_position_upper(leds: NDArray, *, min_weight: float = 1.0) -> NDArray[np.float64]:
    """Luma-weighted centroid of the upper half-strip (LEDs 80–159).

    Waveform Tempo injects in the upper half then mirrors. NaN when the half
    is dark. Range 0..79 inside that half (0 = centre seam, 79 = tip).
    """
    luma = luminance_map(leds)
    if luma.shape[1] != 160:
        raise ValueError(f"expected 160 LEDs, got {luma.shape[1]}")
    half = luma[:, 80:]
    weight = half.sum(axis=1)
    idx = np.arange(half.shape[1], dtype=np.float64)
    pos = np.full(half.shape[0], np.nan, dtype=np.float64)
    ok = weight > float(min_weight)
    if np.any(ok):
        pos[ok] = (half[ok] * idx).sum(axis=1) / weight[ok]
    return pos
