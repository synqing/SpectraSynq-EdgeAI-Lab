"""Match event counts so P3-C2 tests selection quality, not quantity."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def local_peaks(x: NDArray, *, thresh: float, refractory: int) -> list[int]:
    """Causal-enough peaks: strictly above neighbours, above thresh, refractory hops."""
    a = np.asarray(x, dtype=np.float64).reshape(-1)
    if a.size < 3:
        return []
    ev: list[int] = []
    last = -10**9
    ref = max(1, int(refractory))
    for i in range(1, a.size - 1):
        if a[i] < thresh:
            continue
        if a[i] < a[i - 1] or a[i] < a[i + 1]:
            continue
        if i - last < ref:
            continue
        ev.append(i)
        last = i
    return ev


def _count(x: NDArray, thresh: float, refractory: int) -> int:
    return len(local_peaks(x, thresh=thresh, refractory=refractory))


def _threshold_for_count(x: NDArray, target: int, refractory: int) -> float:
    a = np.asarray(x, dtype=np.float64)
    a = a[np.isfinite(a)]
    if a.size == 0 or target <= 0:
        return float("inf")
    lo, hi = float(np.min(a)), float(np.max(a))
    if hi <= lo:
        return hi + 1.0
    best = hi
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        n = _count(a, mid, refractory)
        if n > target:
            lo = mid
        else:
            hi = mid
            best = mid
        if abs(n - target) <= max(1, int(0.1 * target)):
            best = mid
            break
    return best


def match_thresholds(
    a: NDArray,
    b: NDArray,
    *,
    hop_s: float,
    refractory_s: float = 0.25,
    target_per_min: float | None = None,
) -> tuple[float, float, int, int]:
    """Independent thresholds so both series fire about the same number of events.

    Returns (thresh_a, thresh_b, n_a, n_b).
    """
    refractory = max(1, int(round(refractory_s / max(hop_s, 1e-6))))
    duration_min = max(len(a), 1) * hop_s / 60.0
    if target_per_min is None:
        # Aim at the sparser 90th-percentile rate so we do not invent chatter.
        pa = float(np.percentile(a, 90))
        pb = float(np.percentile(b, 90))
        na = _count(a, pa, refractory)
        nb = _count(b, pb, refractory)
        target_n = max(1, int(round(0.5 * (na + nb))))
    else:
        target_n = max(1, int(round(target_per_min * duration_min)))
    ta = _threshold_for_count(a, target_n, refractory)
    tb = _threshold_for_count(b, target_n, refractory)
    return ta, tb, _count(a, ta, refractory), _count(b, tb, refractory)


def triggers_per_minute(n_events: int, duration_s: float) -> float:
    if duration_s <= 0:
        return 0.0
    return 60.0 * float(n_events) / float(duration_s)
