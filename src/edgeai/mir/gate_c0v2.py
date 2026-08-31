"""Gate C0-v2: join pixels to applied PRSM from device-epoch metadata.

The retired two-clock C0 runner is not used. Lag search cannot promote a PASS.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

import numpy as np
from numpy.typing import NDArray

from edgeai.mir.p3c_quant import (
    DELTA_SHARE_MIN,
    POS_GAIN_MIN,
    score_clip,
    spearman,
    summarise,
)
from edgeai.mir.p3c_score import head_position_upper

HOP_S = 512.0 / 16_000.0
HOP_US = 32_000
SEM_NONE = 65535
SINCE_NONE = 65535
LAG_SEARCH = range(-20, 21)
LAG_INVALID_HOPS = 3
LAG_INVALID_IMPROVE = 0.15
HEAD_STEP_MIN_PX = 5.0

BEGIN_RE = re.compile(r"^\[RTRACE-BEGIN\b(?P<body>[^\]]*)\]\s*$")
EPOCH_RE = re.compile(
    r"^\[C0_EPOCH\s+frame=(?P<frame>\d+)\s+device_us=(?P<us>\d+)"
    r"(?:\s+semantic_idx=(?P<sem>\d+))?(?:\s+cond=(?P<cond>\d+))?"
    r"(?:\s+epoch_id=(?P<eid>\d+))?(?:\s+tick=(?P<tick>\d+))?\]\s*$"
)
EPOCH_MISSING = "[C0_EPOCH missing]"
F_RE = re.compile(r"^F,(?P<idx>\d+),(?P<ms>\d+),(?P<mode>\d+),(?P<hex>[0-9a-fA-F]+)\s*$")
M_RE = re.compile(
    r"^M,(?P<idx>\d+),(?P<tick>\d+),(?P<us>\d+),(?P<epoch_id>\d+),"
    r"(?P<since>\d+),(?P<cond>\d+),(?P<sem>\d+),(?P<prsm>\d+),"
    r"(?P<inj>\d+),(?P<marker>\d+)\s*$"
)


@dataclass
class C0Dump:
    begin: str
    fmt: str
    n_declared: int
    epoch_id: int
    hop_us: int
    cond: int
    n_sem: int
    pipeline_lat: int
    epoch: dict[str, int] | None
    epoch_missing: bool
    leds: NDArray[np.uint8]
    t_ms: NDArray[np.float64]
    modes: NDArray[np.int32]
    tick: NDArray[np.int64]
    device_us: NDArray[np.int64]
    since: NDArray[np.int64]
    sem_idx: NDArray[np.int64]
    applied_u16: NDArray[np.int64]
    inj: NDArray[np.int64]
    marker: NDArray[np.int64]
    meta_epoch_id: NDArray[np.int64]
    dropped_f: int = 0
    dropped_m: int = 0


@dataclass
class Integrity:
    status: str
    reasons: list[str] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return self.status == "OK"


def _kv(body: str, key: str, default: str = "") -> str:
    m = re.search(rf"\b{re.escape(key)}=([^\s\]]+)", body)
    return m.group(1) if m else default


def decode_c0_dump(text: str) -> C0Dump:
    """Primary decoder. A second independent parser lives in tests/test_gate_c0v2.py."""
    begin = ""
    fmt = "unknown"
    n_declared = 0
    epoch_id = 0
    hop_us = 0
    cond = 0
    n_sem = 0
    pipeline_lat = 0
    epoch: dict[str, int] | None = None
    epoch_missing = False
    frames: dict[int, dict[str, Any]] = {}
    dropped_f = 0
    dropped_m = 0
    for raw in text.splitlines():
        s = raw.strip()
        bm = BEGIN_RE.match(s)
        if bm:
            begin = bm.group("body")
            fmt = _kv(begin, "fmt", "unknown")
            n_declared = int(_kv(begin, "frames", "0") or 0)
            epoch_id = int(_kv(begin, "epoch_id", "0") or 0)
            hop_us = int(_kv(begin, "hop_us", "0") or 0)
            cond = int(_kv(begin, "cond", "0") or 0)
            n_sem = int(_kv(begin, "n_sem", "0") or 0)
            pipeline_lat = int(_kv(begin, "pipeline_lat", "0") or 0)
            continue
        if s.startswith(EPOCH_MISSING):
            epoch_missing = True
            continue
        em = EPOCH_RE.match(s)
        if em:
            epoch = {k: int(v) for k, v in em.groupdict().items() if v is not None}
            continue
        fm = F_RE.match(s)
        if fm:
            idx = int(fm.group("idx"))
            hexs = fm.group("hex")
            if fmt != "rgb16hex" or not hexs or len(hexs) != 160 * 12:
                dropped_f += 1
                continue
            raw_b = bytes.fromhex(hexs)
            rgb16 = np.frombuffer(raw_b, dtype=">u2").reshape(-1, 3).copy()
            if rgb16.shape[0] != 160:
                dropped_f += 1
                continue
            rec = frames.setdefault(idx, {})
            rec["leds"] = (rgb16 >> 8).astype(np.uint8)
            rec["ms"] = int(fm.group("ms"))
            rec["mode"] = int(fm.group("mode"))
            continue
        mm = M_RE.match(s)
        if mm:
            idx = int(mm.group("idx"))
            rec = frames.setdefault(idx, {})
            rec["tick"] = int(mm.group("tick"))
            rec["us"] = int(mm.group("us"))
            rec["epoch_id"] = int(mm.group("epoch_id"))
            rec["since"] = int(mm.group("since"))
            rec["cond"] = int(mm.group("cond"))
            rec["sem"] = int(mm.group("sem"))
            rec["prsm"] = int(mm.group("prsm"))
            rec["inj"] = int(mm.group("inj"))
            rec["marker"] = int(mm.group("marker"))
            continue
    idxs = sorted(i for i, rec in frames.items() if "leds" in rec and "prsm" in rec)
    orphan = sum(1 for rec in frames.values() if ("leds" in rec) ^ ("prsm" in rec))
    dropped_m += orphan
    if not idxs:
        empty = np.zeros((0,), dtype=np.int64)
        return C0Dump(
            begin=begin,
            fmt=fmt,
            n_declared=n_declared,
            epoch_id=epoch_id,
            hop_us=hop_us,
            cond=cond,
            n_sem=n_sem,
            pipeline_lat=pipeline_lat,
            epoch=epoch,
            epoch_missing=epoch_missing,
            leds=np.zeros((0, 160, 3), dtype=np.uint8),
            t_ms=np.zeros((0,), dtype=np.float64),
            modes=np.zeros((0,), dtype=np.int32),
            tick=empty,
            device_us=empty,
            since=empty,
            sem_idx=empty,
            applied_u16=empty,
            inj=empty,
            marker=empty,
            meta_epoch_id=empty,
            dropped_f=dropped_f,
            dropped_m=dropped_m,
        )
    leds = np.stack([frames[i]["leds"] for i in idxs], axis=0)
    return C0Dump(
        begin=begin,
        fmt=fmt,
        n_declared=n_declared,
        epoch_id=epoch_id,
        hop_us=hop_us,
        cond=cond,
        n_sem=n_sem,
        pipeline_lat=pipeline_lat,
        epoch=epoch,
        epoch_missing=epoch_missing,
        leds=leds,
        t_ms=np.asarray([frames[i]["ms"] for i in idxs], dtype=np.float64),
        modes=np.asarray([frames[i]["mode"] for i in idxs], dtype=np.int32),
        tick=np.asarray([frames[i]["tick"] for i in idxs], dtype=np.int64),
        device_us=np.asarray([frames[i]["us"] for i in idxs], dtype=np.int64),
        since=np.asarray([frames[i]["since"] for i in idxs], dtype=np.int64),
        sem_idx=np.asarray([frames[i]["sem"] for i in idxs], dtype=np.int64),
        applied_u16=np.asarray([frames[i]["prsm"] for i in idxs], dtype=np.int64),
        inj=np.asarray([frames[i]["inj"] for i in idxs], dtype=np.int64),
        marker=np.asarray([frames[i]["marker"] for i in idxs], dtype=np.int64),
        meta_epoch_id=np.asarray([frames[i]["epoch_id"] for i in idxs], dtype=np.int64),
        dropped_f=dropped_f,
        dropped_m=dropped_m,
    )


def check_integrity(dump: C0Dump, samples_u16: NDArray) -> Integrity:
    reasons: list[str] = []
    details: dict[str, Any] = {}
    samples = np.asarray(samples_u16, dtype=np.uint16).reshape(-1)
    if dump.epoch_missing or dump.epoch is None:
        reasons.append("epoch_marker_absent")
    if dump.fmt != "rgb16hex":
        reasons.append("fmt_not_rgb16hex")
    if dump.leds.shape[0] < 8:
        reasons.append("too_few_frames")
    details["dropped_f"] = dump.dropped_f
    details["dropped_m"] = dump.dropped_m
    if dump.leds.shape[0]:
        if not np.all(np.diff(dump.tick) > 0):
            reasons.append("tick_not_strictly_increasing")
        if not np.all(np.diff(dump.device_us.astype(np.int64)) >= 0):
            wrap = int(np.sum(np.diff(dump.device_us.astype(np.int64)) < 0))
            if wrap:
                reasons.append("device_us_not_monotonic")
                details["us_decreases"] = wrap
        dtick = np.diff(dump.tick)
        if dtick.size:
            details["tick_gaps"] = int((dtick != 1).sum())
            details["max_tick_gap"] = int(dtick.max())
        marked = np.where(dump.marker == 1)[0]
        details["n_markers"] = int(marked.size)
        if marked.size != 1:
            reasons.append("epoch_marker_count")
        else:
            i = int(marked[0])
            if int(dump.inj[i]) == 1 and int(dump.sem_idx[i]) not in (0, SEM_NONE):
                if int(dump.sem_idx[i]) != 0:
                    reasons.append("epoch_sem_idx_not_zero")
        if samples.size:
            inj = dump.inj == 1
            if int(inj.sum()) == 0:
                reasons.append("no_injection_frames")
            else:
                sem = dump.sem_idx[inj]
                if np.any((sem < 0) | (sem >= samples.size) | (sem == SEM_NONE)):
                    reasons.append("sem_idx_out_of_range")
                else:
                    expect = samples[sem].astype(np.int64)
                    got = dump.applied_u16[inj]
                    n_mismatch = int(np.sum(expect != got))
                    details["applied_mismatches"] = n_mismatch
                    if n_mismatch:
                        reasons.append("applied_prsm_mismatch")
                hops, _, present = hop_join(dump, int(samples.size))
                cov = float(present.sum()) / float(samples.size)
                details["hop_coverage"] = cov
                details["hops_present"] = int(present.sum())
                if cov < 0.98:
                    reasons.append("incomplete_hop_coverage")
        if dump.epoch_id:
            live = (dump.inj == 1) | (dump.marker == 1)
            if live.any() and int(np.sum(dump.meta_epoch_id[live] != dump.epoch_id)):
                reasons.append("epoch_id_inconsistent")
        details["n_frames"] = int(dump.leds.shape[0])
        details["n_inject"] = int((dump.inj == 1).sum())
        details["declared_frames"] = dump.n_declared
        if dump.n_declared and dump.n_declared != dump.leds.shape[0]:
            details["begin_frames_delta"] = int(dump.n_declared) - int(dump.leds.shape[0])
    status = "OK" if not reasons else "INVALID_RUN"
    return Integrity(status=status, reasons=reasons, details=details)


def hop_join(dump: C0Dump, n_sem: int) -> tuple[NDArray[np.uint8], NDArray[np.float64], NDArray[np.int64]]:
    """One LED cube row per semantic index: last inject frame of that hop.

    Alignment comes from M.sem_idx, never from host time or a lag search.
    """
    n = int(n_sem)
    out = np.zeros((n, 160, 3), dtype=np.uint8)
    gain = np.full(n, np.nan, dtype=np.float64)
    present = np.zeros(n, dtype=np.int64)
    inj = dump.inj == 1
    if not inj.any():
        return out, gain, present
    for i in range(dump.leds.shape[0]):
        if dump.inj[i] != 1:
            continue
        sem = int(dump.sem_idx[i])
        if sem < 0 or sem >= n or sem == SEM_NONE:
            continue
        out[sem] = dump.leds[i]
        gain[sem] = float(dump.applied_u16[i]) / 65535.0
        present[sem] = 1
    return out, gain, present


def lag_disagreement(head: NDArray, applied: NDArray) -> dict[str, Any]:
    """Error detector only. Never used to correct the PASS calculation."""
    h = np.asarray(head, dtype=np.float64).reshape(-1)
    a = np.asarray(applied, dtype=np.float64).reshape(-1)
    n = min(h.size, a.size)
    h, a = h[:n], a[:n]
    m = np.isfinite(h) & np.isfinite(a)
    h, a = h[m], a[m]
    out: dict[str, Any] = {
        "lag0_spearman": float("nan"),
        "best_lag_hops": 0,
        "best_spearman": float("nan"),
        "invalid": False,
    }
    if h.size < 8:
        return out
    s0 = spearman(h, a)
    out["lag0_spearman"] = s0
    best_lag = 0
    best = s0 if s0 == s0 else -2.0
    for lag in LAG_SEARCH:
        if lag == 0:
            s = s0
        elif lag > 0:
            s = spearman(h[lag:], a[:-lag]) if h.size > lag + 8 else float("nan")
        else:
            k = -lag
            s = spearman(h[:-k], a[k:]) if h.size > k + 8 else float("nan")
        if s == s and s > best:
            best = s
            best_lag = int(lag)
    out["best_lag_hops"] = best_lag
    out["best_spearman"] = float(best)
    improve = (best - s0) if (s0 == s0 and best == best) else 0.0
    out["improve"] = float(improve)
    if abs(best_lag) >= LAG_INVALID_HOPS and improve >= LAG_INVALID_IMPROVE:
        out["invalid"] = True
    return out


def applied_transitions(dump: C0Dump) -> list[dict[str, int]]:
    inj = np.where(dump.inj == 1)[0]
    if inj.size < 2:
        return []
    out = []
    last_sem = int(dump.sem_idx[inj[0]])
    last_prsm = int(dump.applied_u16[inj[0]])
    for i in inj[1:]:
        sem = int(dump.sem_idx[i])
        prsm = int(dump.applied_u16[i])
        if sem != last_sem or prsm != last_prsm:
            out.append(
                {
                    "frame": int(i),
                    "sem_idx": sem,
                    "applied_u16": prsm,
                    "prev_sem": last_sem,
                    "prev_applied": last_prsm,
                }
            )
            last_sem = sem
            last_prsm = prsm
    return out


def timing_selftest(
    dump: C0Dump,
    samples_u16: NDArray,
    *,
    expected_change_at: list[int],
) -> dict[str, Any]:
    integ = check_integrity(dump, samples_u16)
    hops, gain, present = hop_join(dump, int(np.asarray(samples_u16).size))
    pos = head_position_upper(hops) if hops.shape[0] else np.zeros((0,), dtype=np.float64)
    trans = applied_transitions(dump)
    declared = [int(x) for x in expected_change_at]
    seen_sem = [t["sem_idx"] for t in trans]
    changes_ok = True
    missing = []
    for idx in declared:
        if idx not in seen_sem:
            changes_ok = False
            missing.append(idx)
    high = samples_u16 == samples_u16.max()
    low = samples_u16 == samples_u16.min()
    head_high = float(np.nanmean(pos[high])) if hops.shape[0] else float("nan")
    head_low = float(np.nanmean(pos[low])) if hops.shape[0] else float("nan")
    head_delta = head_high - head_low if (head_high == head_high and head_low == head_low) else float("nan")
    lag = lag_disagreement(pos, gain)
    reasons = list(integ.reasons)
    if not changes_ok:
        reasons.append("applied_did_not_change_at_declared_indices")
    if not (head_delta == head_delta and head_delta >= HEAD_STEP_MIN_PX):
        reasons.append("head_did_not_follow_pressure_step")
    if lag.get("invalid"):
        reasons.append("lag_detector_disagrees_with_declared_timing")
    if int(present.sum()) < int(samples_u16.size) * 0.9:
        reasons.append("incomplete_hop_coverage")
        integ.details["hop_present"] = int(present.sum())
    status = "PASS" if not reasons else "INVALID_RUN"
    return {
        "status": status,
        "integrity": integ.status,
        "reasons": reasons,
        "details": integ.details,
        "transitions": trans,
        "missing_change_sem": missing,
        "head_high": head_high,
        "head_low": head_low,
        "head_delta": head_delta,
        "lag": lag,
        "n_frames": int(dump.leds.shape[0]),
        "epoch": dump.epoch,
        "pipeline_lat": dump.pipeline_lat,
    }


def score_nominal(
    leds_by_cond: dict[str, NDArray],
    gain_by_cond: dict[str, NDArray],
    oracle: dict[str, NDArray],
    meta: dict[str, Any],
    lag_rows: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """P3-C thresholds unchanged. No lag correction."""
    pack = {
        "A": leds_by_cond["A"],
        "B": leds_by_cond["B"],
        "D": leds_by_cond["D"],
        "gain_A": gain_by_cond["A"],
        "gain_B": gain_by_cond["B"],
        "gain_D": gain_by_cond["D"],
        "control": leds_by_cond["A"],
        "mir": leds_by_cond["A"],
    }
    rec = score_clip(pack, oracle, meta)
    rec["lag"] = lag_rows
    rec["lag_corrected"] = False
    if any(v.get("invalid") for v in lag_rows.values()):
        rec["timing_invalid"] = True
    else:
        rec["timing_invalid"] = False
    return rec


def verdict(integrity_ok: bool, q1: str, q2: str, q3: str, lag_invalid: bool) -> str:
    if not integrity_ok or lag_invalid:
        return "INVALID_RUN"
    if q1 == "PASS" and q2 == "PASS" and q3 == "PASS":
        return "PASS"
    return "BINDING_FAIL"


def u16be_hex(samples: NDArray) -> str:
    a = np.asarray(samples, dtype=np.uint16).reshape(-1)
    return "".join(f"{int(v):04x}" for v in a)


def chunk_hex(hexs: str, n_chars: int = 128) -> list[str]:
    return [hexs[i : i + n_chars] for i in range(0, len(hexs), n_chars)]


def step_trace(*, n_seg: int = 16, low: float = 0.20, high: float = 1.0) -> tuple[NDArray[np.uint16], list[int]]:
    lo = int(round(low * 65535))
    hi = int(round(high * 65535))
    samples = np.array(
        [lo] * n_seg + [hi] * n_seg + [lo] * n_seg + [hi] * n_seg,
        dtype=np.uint16,
    )
    changes = [n_seg, 2 * n_seg, 3 * n_seg]
    return samples, changes
