"""HOST-ONLY cadence/latency of the P3-C extra-DoF. Not Gate C0. Not silicon.

The load-bearing series is the extra-DoF *gain* (waveform peak + chroma gain).
Zero-order-hold that series, delay it causally, then re-render. Resampling LED
frames is wrong: it invents motion the engine never drew.
"""

from __future__ import annotations

from typing import Any, Mapping

import numpy as np
from numpy.typing import NDArray

from edgeai.mir.host_chroma import extra_gain
from edgeai.mir.p3c_quant import partial_pearson, score_clip
from edgeai.mir.p3c_score import head_position_upper
from edgeai.mir.source_oracle import SOURCES

# Native P3-C host hop. 16000/512 is exact 31.25 Hz.
SR = 16_000
HOP = 512
HOP_S = HOP / SR
NATIVE_HZ = SR / HOP
HOLD_RATES_HZ: tuple[float, ...] = (2.0, 5.0, 10.0, 20.0, NATIVE_HZ)
DELAYS_S: tuple[float, ...] = (0.0, 0.050, 0.100, 0.200)
# Silicon cadence grid (Captain K1-C0-CADENCE-LATENCY-FLASH-GO). Host 2 Hz is
# not in this sweep. Reference ~31.25 Hz is the C0-v2 receipt, not a re-run.
SILICON_RATE_HZ: tuple[float, ...] = (20.0, 15.0, 10.0, 5.0)
SILICON_DELAY_S: tuple[float, ...] = (0.0, 0.025, 0.050, 0.100, 0.200)
HOLD_POLICY = (
    "zero-order-hold of extra_gain on the 32 ms hop grid; causal delay of "
    "round(delay_s/0.032) hops with first-sample freeze on the pad; no "
    "interpolation; device hop_us stays 32000"
)
GAIN_LO = 0.62
GAIN_HI = 1.0
DELTA_FLOOR = 0.15
NATIVE_KEEP_FRACTION = 0.70
# Documented P3-C holdout median Δ (not a freeze; this run measures native again).
P3C_HOLDOUT_MEDIAN_DELTA = 0.63
SHARE_SOURCES = SOURCES  # vocals, drums, bass, other
WARMUP_S = 1.0
PREVIEW_EXPOSURE = 2.2
FROZEN_MAP_VERSION = "p3b-v1"
BINDING = "source_share × WaveformTempo × head_position"


def delay_hops(delay_s: float, hop_s: float = HOP_S) -> int:
    if delay_s <= 0.0:
        return 0
    return int(round(float(delay_s) / float(hop_s)))


def actual_delay_s(delay_s: float, hop_s: float = HOP_S) -> float:
    return float(delay_hops(delay_s, hop_s)) * float(hop_s)


def zero_order_hold(x: NDArray, *, hop_s: float = HOP_S, rate_hz: float) -> NDArray[np.float64]:
    """Hold the last emitted sample at `rate_hz`. Native rate is identity.

    At time t = i * hop_s the value is x[j] where j is the hop nearest the last
    emission time floor(t * rate_hz) / rate_hz. No future samples.
    """
    x = np.asarray(x, dtype=np.float64).reshape(-1)
    n = int(x.size)
    if n == 0:
        return x.copy()
    rate = float(rate_hz)
    if rate <= 0.0:
        raise ValueError("rate_hz must be positive")
    hop = float(hop_s)
    if hop <= 0.0:
        raise ValueError("hop_s must be positive")
    t = np.arange(n, dtype=np.float64) * hop
    tick = np.floor(t * rate + 1e-12)
    t_emit = tick / rate
    src = np.rint(t_emit / hop).astype(np.int64)
    src = np.clip(src, 0, n - 1)
    # Causal: never read a hop after i.
    src = np.minimum(src, np.arange(n, dtype=np.int64))
    return x[src]


def causal_delay(x: NDArray, *, hop_s: float = HOP_S, delay_s: float) -> NDArray[np.float64]:
    """Shift the series later by round(delay_s / hop_s) hops. No lookahead.

    y[i] = x[i - d]; the first d hops freeze x[0]. Delay is extra pipeline
    latency after the sample exists, not a smoothing filter.
    """
    x = np.asarray(x, dtype=np.float64).reshape(-1)
    d = delay_hops(delay_s, hop_s)
    if d <= 0:
        return x.copy()
    y = np.empty_like(x)
    y[: min(d, x.size)] = x[0] if x.size else 0.0
    if d < x.size:
        y[d:] = x[:-d]
    return y


def apply_cadence(
    x: NDArray,
    *,
    hop_s: float = HOP_S,
    rate_hz: float,
    delay_s: float,
) -> NDArray[np.float64]:
    """Student-at-R plus latency: zero-order hold, then causal delay."""
    held = zero_order_hold(x, hop_s=hop_s, rate_hz=rate_hz)
    return causal_delay(held, hop_s=hop_s, delay_s=delay_s)


def extra_gain_cadence(
    frozen_01: NDArray,
    *,
    hop_s: float = HOP_S,
    rate_hz: float,
    delay_s: float,
    lo: float = GAIN_LO,
    hi: float = GAIN_HI,
) -> NDArray[np.float64]:
    """Map a frozen 0–1 driver then hold/delay. Same [0.62, 1.0] band as P3-C."""
    g = extra_gain(frozen_01, lo=lo, hi=hi)
    return apply_cadence(g, hop_s=hop_s, rate_hz=rate_hz, delay_s=delay_s)


def require_four_source_share(oracle: Mapping[str, Any]) -> None:
    missing = [name for name in SHARE_SOURCES if f"{name}_share" not in oracle]
    if missing:
        raise ValueError(f"share oracle missing {missing}; four-source simplex required")


def median_finite(xs: list[float] | NDArray) -> float:
    a = np.asarray([x for x in np.asarray(xs, dtype=np.float64).reshape(-1) if x == x], dtype=np.float64)
    return float(np.median(a)) if a.size else float("nan")


def cell_passes(median_delta: float, native_median: float) -> bool:
    """PASS iff median Δ ≥ 0.15 and ≥ 70% of this run's native-rate Δ."""
    if median_delta != median_delta or native_median != native_median:
        return False
    return float(median_delta) >= DELTA_FLOOR and float(median_delta) >= NATIVE_KEEP_FRACTION * float(
        native_median
    )


def summarise_holdout(deltas: list[float], *, native_median: float) -> dict[str, Any]:
    med = median_finite(deltas)
    finite = [float(d) for d in deltas if d == d]
    wins = int(sum(d > 0.0 for d in finite))
    rel = NATIVE_KEEP_FRACTION * float(native_median) if native_median == native_median else float("nan")
    passed = cell_passes(med, native_median)
    frac = float(med / native_median) if (native_median == native_median and native_median != 0.0) else float("nan")
    return {
        "n": int(len(deltas)),
        "n_finite": int(len(finite)),
        "wins_positive_delta": [wins, int(len(finite))],
        "median_delta_pos_share": med,
        "floor": DELTA_FLOOR,
        "relative_floor": rel,
        "fraction_of_native": frac,
        "pass": passed,
        "verdict": "PASS" if passed else "FAIL",
    }


def lowest_passing_rate_hz(rate_rows: list[Mapping[str, Any]]) -> float | None:
    ok = [
        float(r["rate_hz"])
        for r in sorted(rate_rows, key=lambda z: float(z["rate_hz"]))
        if bool(r.get("pass")) or r.get("verdict") == "PASS"
    ]
    return ok[0] if ok else None


def delay_cliff_s(delay_rows: list[Mapping[str, Any]]) -> float | None:
    """Smallest requested delay > 0 at native rate that fails the combined pass rule."""
    for row in sorted(delay_rows, key=lambda z: float(z["delay_s"])):
        if float(row["delay_s"]) <= 0.0:
            continue
        passed = bool(row.get("pass")) or row.get("verdict") == "PASS"
        if not passed:
            return float(row["delay_s"])
    return None


def delay_below_absolute_floor_s(delay_rows: list[Mapping[str, Any]]) -> float | None:
    """Smallest requested delay > 0 whose median Δ is below 0.15. None if none are."""
    for row in sorted(delay_rows, key=lambda z: float(z["delay_s"])):
        if float(row["delay_s"]) <= 0.0:
            continue
        med = float(row["median_delta_pos_share"])
        if med != med or med < DELTA_FLOOR:
            return float(row["delay_s"])
    return None


def sweep_cells() -> list[tuple[str, float, float]]:
    """(family, rate_hz, delay_s). Rate sweep at delay 0; delay sweep at native rate."""
    cells: list[tuple[str, float, float]] = []
    for rate in HOLD_RATES_HZ:
        cells.append(("rate", float(rate), 0.0))
    for delay in DELAYS_S:
        if delay == 0.0:
            continue
        cells.append(("delay", float(NATIVE_HZ), float(delay)))
    return cells


def is_native_cell(rate_hz: float, delay_s: float, *, hop_s: float = HOP_S) -> bool:
    return abs(float(rate_hz) - NATIVE_HZ) < 1e-9 and delay_hops(delay_s, hop_s) == 0


def q_binding_from_summary(holdout: Mapping[str, Any]) -> dict[str, Any]:
    """Silicon PASS uses C0-v2 Q1–Q3. Not the host 70%-of-native extra rule."""
    q1 = holdout.get("Q1_knob_is_head_position")
    q2 = holdout.get("Q2_share_increment_in_pixels")
    q3 = holdout.get("Q3_source_abs_after_mix")
    ok = q1 == "PASS" and q2 == "PASS" and q3 == "PASS"
    return {
        "Q1": q1,
        "Q2": q2,
        "Q3": q3,
        "pass": bool(ok),
        "verdict": "PASS" if ok else "FAIL",
    }


def slowest_passing_rate_hz(rate_rows: list[Mapping[str, Any]]) -> float | None:
    """Slowest tested rate whose silicon binding still PASSES. INVALID is not FAIL."""
    ok = [
        float(r["rate_hz"])
        for r in rate_rows
        if str(r.get("verdict") or "") == "PASS" and str(r.get("c0v2") or r.get("status") or "PASS") != "INVALID_RUN"
    ]
    return min(ok) if ok else None


def largest_passing_delay_s(delay_rows: list[Mapping[str, Any]]) -> float | None:
    ok = [
        float(r["delay_s"])
        for r in delay_rows
        if str(r.get("verdict") or "") == "PASS" and str(r.get("status") or "PASS") != "INVALID_RUN"
    ]
    return max(ok) if ok else None


def honest_rate_bracket(rate_rows: list[Mapping[str, Any]]) -> str:
    rows = sorted(
        [r for r in rate_rows if str(r.get("status") or r.get("c0v2") or "") != "INVALID_RUN"],
        key=lambda z: float(z["rate_hz"]),
    )
    if not rows:
        return "no valid rate cells"
    passing = [r for r in rows if str(r.get("verdict")) == "PASS"]
    failing = [r for r in rows if str(r.get("verdict")) != "PASS"]
    if passing and not failing:
        slow = min(float(r["rate_hz"]) for r in passing)
        return f"PASS at all valid tested rates down to {slow:g} Hz"
    if failing and not passing:
        fast = max(float(r["rate_hz"]) for r in failing)
        return f"FAIL at all valid tested rates (fastest fail {fast:g} Hz)"
    slow_pass = min(float(r["rate_hz"]) for r in passing)
    fast_fail = max((float(r["rate_hz"]) for r in failing if float(r["rate_hz"]) < slow_pass), default=None)
    if fast_fail is None:
        return f"PASS at {slow_pass:g} Hz (no slower valid fail on this grid)"
    return (
        f"PASS at {slow_pass:g} Hz; FAIL at {fast_fail:g} Hz → required rate is "
        f">{fast_fail:g} Hz and ≤{slow_pass:g} Hz on this evidence"
    )


def honest_delay_bracket(delay_rows: list[Mapping[str, Any]]) -> str:
    rows = sorted(
        [r for r in delay_rows if str(r.get("status") or "") != "INVALID_RUN"],
        key=lambda z: float(z["delay_s"]),
    )
    if not rows:
        return "no valid delay cells"
    passing = [r for r in rows if str(r.get("verdict")) == "PASS"]
    if not passing:
        return "FAIL at every valid tested added delay, including 0 ms"
    largest = max(float(r["delay_s"]) for r in passing)
    larger_fail = [
        float(r["delay_s"])
        for r in rows
        if str(r.get("verdict")) != "PASS" and float(r["delay_s"]) > largest
    ]
    largest_ms = largest * 1000.0
    if not larger_fail:
        return f"PASS at all valid tested delays through {largest_ms:.0f} ms"
    next_fail = min(larger_fail) * 1000.0
    return (
        f"PASS at {largest_ms:.0f} ms; FAIL at {next_fail:.0f} ms → admissible added "
        f"semantic delay lies below {next_fail:.0f} ms and is demonstrated through "
        f"{largest_ms:.0f} ms"
    )


def score_head_delta(
    leds: Mapping[str, NDArray],
    oracle: Mapping[str, NDArray],
    meta: Mapping[str, Any],
) -> dict[str, Any]:
    """Reuse P3-C score_clip; keep the extra-DoF fields the cadence question needs."""
    rec = score_clip(leds, oracle, meta)
    return {
        "track": rec.get("track"),
        "set": rec.get("set"),
        "share_driver": rec.get("share_driver"),
        "n": rec.get("n"),
        "partial_B_pos_share_mix": rec["partial_B_pos_share_mix"],
        "partial_D_pos_share_mix": rec["partial_D_pos_share_mix"],
        "delta_pos_share": rec["delta_pos_share"],
        "spearman_B_pos_gain": rec["spearman_B_pos_gain"],
        "spearman_D_pos_gain": rec["spearman_D_pos_gain"],
    }


def head_partial_r(leds: NDArray, share: NDArray, mix: NDArray) -> float:
    pos = head_position_upper(np.asarray(leds))
    return partial_pearson(pos, share, mix)
