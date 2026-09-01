"""HOST share-stream sketch: emit envelope is R XOR D. Never AND 5 Hz with 50 ms."""

from __future__ import annotations

import pytest

from edgeai.mir.stream_sketch import (
    JointCliffError,
    classify_emit_envelope,
    emit_schedule,
)


def test_r_zero_delay() -> None:
    assert classify_emit_envelope(5.0, 0.0) == "R"
    assert classify_emit_envelope(31.25, delay_s=0.0) == "R"


def test_d_delay_at_least_20hz() -> None:
    assert classify_emit_envelope(20.0, 0.050) == "D"
    assert classify_emit_envelope(rate_hz=40.0, delay_s=0.050) == "D"


def test_rejects_joint_5hz_50ms() -> None:
    with pytest.raises(JointCliffError, match="XOR|5 Hz"):
        classify_emit_envelope(5.0, 0.050)
    with pytest.raises(JointCliffError):
        classify_emit_envelope(rate_hz=5, delay_s=50e-3)


def test_r_xor_d_never_both() -> None:
    r = classify_emit_envelope(5.0, 0.0)
    d = classify_emit_envelope(20.0, 0.050)
    assert {r, d} == {"R", "D"}
    assert r != d
    # same args cannot classify as both
    args = (20.0, 0.0)
    one = classify_emit_envelope(*args)
    assert one in {"R", "D"}
    assert not (one == "R" and one == "D")


def test_slow_rate_with_delay_is_and_not_d() -> None:
    with pytest.raises(JointCliffError):
        classify_emit_envelope(10.0, 0.025)


def test_emit_schedule_uses_one_envelope() -> None:
    env_r, times_r = emit_schedule(1.0, rate_hz=5.0, delay_s=0.0)
    assert env_r == "R"
    assert times_r[0] == 0.0
    env_d, times_d = emit_schedule(1.0, rate_hz=20.0, delay_s=0.050)
    assert env_d == "D"
    assert times_d[0] == pytest.approx(0.050)
    with pytest.raises(JointCliffError):
        emit_schedule(1.0, rate_hz=5.0, delay_s=0.050)
