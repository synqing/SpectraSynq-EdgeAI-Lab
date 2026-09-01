"""Lightweight four-source hop-power primitive shared by oracle and teachers."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

SOURCES = ("vocals", "drums", "bass", "other")


def _mono(pcm: NDArray) -> NDArray[np.float32]:
    values = np.asarray(pcm, dtype=np.float32)
    if values.ndim == 2:
        values = values.mean(axis=-1)
    return values.reshape(-1)


def frame_mean_square(pcm: NDArray, hop: int = 512) -> NDArray[np.float64]:
    """Hop power. No numerical floor; silence stays silence for share."""
    values = _mono(pcm).astype(np.float64)
    if values.size < hop:
        if values.size == 0:
            return np.zeros(1, dtype=np.float64)
        return np.array([float(np.mean(values * values))], dtype=np.float64)
    count = int(values.size // hop)
    frames = values[: count * hop].reshape(count, hop)
    return np.mean(frames * frames, axis=1)
