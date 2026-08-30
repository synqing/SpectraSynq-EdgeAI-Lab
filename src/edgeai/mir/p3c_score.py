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
