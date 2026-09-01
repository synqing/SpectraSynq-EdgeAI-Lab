"""HOST-ONLY share-stream emit-envelope sketch. Not a product net. Not Titan.

Cadence silicon is CLOSED. Two 1-D PASSes do not make a 2-D PASS:

* R — extra delay 0, emit at least 5 Hz
* D — extra delay > 0, emit at least 20 Hz

5 Hz **and** 50 ms extra delay together rebuild ``r5_d50`` Q1 FAIL.
A helper here picks R XOR D and raises on the joint cliff.
Student I/O stays UNFROZEN. Do not export ONNX. Do not train.
"""

from __future__ import annotations

from typing import Literal

Envelope = Literal["R", "D"]

R_MIN_HZ = 5.0
D_MIN_HZ = 20.0
JOINT_CLIFF_HZ = 5.0
JOINT_CLIFF_DELAY_S = 0.050


class JointCliffError(ValueError):
    """AND of the cadence cliffs — 5 Hz together with 50 ms extra delay."""


def _near(a: float, b: float, tol: float = 1e-9) -> bool:
    return abs(float(a) - float(b)) <= tol


def classify_emit_envelope(rate_hz: float, delay_s: float = 0.0) -> Envelope:
    """Return ``R`` or ``D``. Raise if the args AND the cliffs.

    Accepts ``delay_s == 0`` with ``rate_hz >= 5`` (R), or ``delay_s > 0``
    with ``rate_hz >= 20`` (D). Rejects 5 Hz + 50 ms and any other AND.
    """
    rate = float(rate_hz)
    delay = float(delay_s)
    if rate <= 0.0:
        raise ValueError(f"rate_hz must be > 0, got {rate_hz!r}")
    if delay < 0.0:
        raise ValueError(f"delay_s must be >= 0, got {delay_s!r}")

    if _near(rate, JOINT_CLIFF_HZ) and _near(delay, JOINT_CLIFF_DELAY_S):
        raise JointCliffError(
            "R XOR D: 5 Hz and 50 ms extra delay together FAIL (r5_d50 Q1)"
        )

    r_ok = delay == 0.0 and rate >= R_MIN_HZ
    d_ok = delay > 0.0 and rate >= D_MIN_HZ
    if r_ok and d_ok:
        raise JointCliffError("R XOR D: cannot satisfy both envelopes")
    if r_ok:
        return "R"
    if d_ok:
        return "D"
    raise JointCliffError(
        f"R XOR D: rate_hz={rate} delay_s={delay} is not R "
        f"(delay_s==0 and rate>={R_MIN_HZ}) and not D "
        f"(delay_s>0 and rate>={D_MIN_HZ}); never AND the cliffs"
    )


def emit_schedule(
    duration_s: float,
    *,
    rate_hz: float,
    delay_s: float = 0.0,
) -> tuple[Envelope, list[float]]:
    """Causal emit times for one exclusive envelope. HOST sketch only."""
    env = classify_emit_envelope(rate_hz, delay_s)
    if float(duration_s) < 0.0:
        raise ValueError(f"duration_s must be >= 0, got {duration_s!r}")
    n = int(float(duration_s) * float(rate_hz))
    step = 1.0 / float(rate_hz)
    extra = float(delay_s) if env == "D" else 0.0
    times = [i * step + extra for i in range(n)]
    return env, times
