"""J3P - cross-view reliability gate.

C3 is the state and movement estimator under test. The resolved FB_LOG pitch view
is a RELIABILITY WITNESS ONLY: it never supplies state and never supplies movement.
This is not fusion. The C3 state is never replaced.

    A(t)       = 1 - 0.5 * L1( C3_state(t), FB_state(t) )   in [0, 1]
    C(t)       = min( A(t), A(t - LAG) )                    in [0, 1]
    M_GATED(t) = C3_movement(t) * C(t)

No threshold, no fitted coefficient, no normalisation, no family rule.

Pre-registration: docs/mir/receipts/cross_view_reliability/J3P_PREREGISTRATION.json
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from .harmonic_movement import MOVEMENT_LAG_HOPS

__all__ = ["endpoint_agreement", "transition_confidence", "gated_movement"]


def endpoint_agreement(c3_state: NDArray, fb_state: NDArray) -> NDArray[np.float64]:
    """A(t) = 1 - 0.5 * L1 between the two views' states at the same frame.

    Both inputs must be non-negative and L1-normalised, which makes 0.5 * L1 the
    total-variation distance and therefore bounds A to [0, 1] with no clipping.
    """
    a = np.asarray(c3_state, dtype=np.float64)
    b = np.asarray(fb_state, dtype=np.float64)
    if a.shape != b.shape:
        raise ValueError(f"state shape mismatch {a.shape} vs {b.shape}")
    return 1.0 - 0.5 * np.abs(a - b).sum(axis=1)


def transition_confidence(agreement: NDArray, *, lag: int = MOVEMENT_LAG_HOPS) -> NDArray[np.float64]:
    """C(t) = min(A(t), A(t - lag)). The first `lag` frames have no earlier
    endpoint and are NaN, never filled."""
    a = np.asarray(agreement, dtype=np.float64)
    out = np.full(a.shape, np.nan, dtype=np.float64)
    if a.size > lag:
        out[lag:] = np.minimum(a[lag:], a[:-lag])
    return out


def gated_movement(c3_movement: NDArray, confidence: NDArray) -> NDArray[np.float64]:
    """M_GATED = C3 movement * cross-view confidence. Pure attenuation."""
    m = np.asarray(c3_movement, dtype=np.float64)
    c = np.asarray(confidence, dtype=np.float64)
    if m.shape != c.shape:
        raise ValueError(f"shape mismatch {m.shape} vs {c.shape}")
    return m * c
