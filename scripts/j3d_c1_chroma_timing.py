#!/usr/bin/env python3
"""J3D-C1 - independent chroma timing / group-delay fixture.

Answers ONE question: what is the effective temporal alignment of
`host_chroma12 -> chroma movement` relative to the same movement measure taken
on exact symbolic state, using a deterministic synthetic fixture with known
transition times?

HARD BOUNDARY: this script never reads BabySlakh, never reads M_tv, and never
optimises a lag against any hypothesis metric. Using the J3D-A result to justify
a correction to the J3D-A result would be circular.

Pre-registration: docs/mir/receipts/chroma_timing/J3D_C1_PREREGISTRATION.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from edgeai.mir.harmonic_movement import (  # noqa: E402
    MOVEMENT_LAG_HOPS,
    l1_rows,
    pitch_class_state,
    tv_movement,
)
from edgeai.mir.host_chroma import host_chroma12  # noqa: E402
from edgeai.mir.note_register import HOP, N_FFT, SR, Note  # noqa: E402

PREREG = ROOT / "docs" / "mir" / "receipts" / "chroma_timing" / "J3D_C1_PREREGISTRATION.json"
N_HARMONICS = 6
CROSSFADE_S = 0.004

PAIRS = [
    ("C_major", [60, 64, 67], "F_major", [65, 69, 72]),
    ("C_major", [60, 64, 67], "A_minor", [57, 60, 64]),
    ("C_major", [60, 64, 67], "G_major", [55, 59, 62]),
    ("D_minor", [62, 65, 69], "Bb_major", [58, 62, 65]),
    ("E_major", [64, 68, 71], "Cs_minor", [61, 64, 68]),
    ("F_major", [65, 69, 72], "C_major", [60, 64, 67]),
]


def midi_hz(m: int) -> float:
    return 440.0 * 2.0 ** ((m - 69) / 12.0)


def state_signal(pitches: list[int], n: int, *, sr: int = SR) -> np.ndarray:
    """Full-length phase-continuous additive signal for one harmonic state."""
    t = np.arange(n, dtype=np.float64) / sr
    y = np.zeros(n, dtype=np.float64)
    for p in pitches:
        f0 = midi_hz(p)
        for k in range(1, N_HARMONICS + 1):
            f = f0 * k
            if f >= sr / 2:
                break
            y += (1.0 / k) * np.sin(2.0 * np.pi * f * t)
    return y / (np.max(np.abs(y)) + 1e-12) * 0.5


def gate(n: int, spans: list[tuple[float, float]], *, sr: int = SR, crossfade_s: float) -> np.ndarray:
    """Envelope that is 1 inside the given spans, with equal-power ramps."""
    g = np.zeros(n, dtype=np.float64)
    cf = max(int(round(crossfade_s * sr)), 0)
    for a, b in spans:
        ia, ib = int(round(a * sr)), int(round(b * sr))
        ia, ib = max(ia, 0), min(ib, n)
        if ib <= ia:
            continue
        g[ia:ib] = 1.0
        if cf > 0:
            r = np.arange(cf) / cf
            up = np.sin(0.5 * np.pi * r)
            dn = np.cos(0.5 * np.pi * r)
            s = min(cf, ib - ia)
            if ia > 0:
                g[ia:ia + s] = up[:s]
            if ib < n:
                g[max(ib - s, ia):ib] = dn[:s][::-1][:s]
    return g


def build_case(a_name, a_pitch, b_name, b_pitch, *, shape: str, crossfade_s: float,
               energy_matched: bool):
    if shape == "AB":
        dur, spans_a, spans_b, transitions = 8.0, [(0.0, 4.0)], [(4.0, 8.0)], [4.0]
    elif shape == "ABA":
        dur, spans_a, spans_b, transitions = 9.0, [(0.0, 3.0), (6.0, 9.0)], [(3.0, 6.0)], [3.0, 6.0]
    else:
        raise ValueError(shape)
    n = int(round(dur * SR))
    ya, yb = state_signal(a_pitch, n), state_signal(b_pitch, n)
    if energy_matched:
        ra = np.sqrt(np.mean(ya**2)) + 1e-12
        rb = np.sqrt(np.mean(yb**2)) + 1e-12
        yb = yb * (ra / rb)
    y = ya * gate(n, spans_a, crossfade_s=crossfade_s) + yb * gate(n, spans_b, crossfade_s=crossfade_s)

    notes: list[Note] = []
    for s, e in spans_a:
        notes += [Note(s, e, p, 100) for p in a_pitch]
    for s, e in spans_b:
        notes += [Note(s, e, p, 100) for p in b_pitch]
    return y, notes, transitions, f"{a_name}->{b_name}"


def response_centre(resp: np.ndarray, centre_frame: int, half: int = 24) -> tuple[float, int]:
    lo, hi = max(centre_frame - half, 0), min(centre_frame + half, resp.size)
    seg = np.nan_to_num(resp[lo:hi], nan=0.0)
    base = float(np.median(seg[: max(half // 3, 1)]))
    w = np.clip(seg - base, 0.0, None)
    if w.sum() <= 1e-12:
        return float("nan"), -1
    idx = np.arange(lo, hi, dtype=np.float64)
    return float((idx * w).sum() / w.sum()), int(lo + np.argmax(seg))


def half_rise(state: np.ndarray, ref_frame: int, centre_frame: int, half: int = 24) -> float:
    """Frame at which distance-from-reference crosses 50% of its post-transition level."""
    p = l1_rows(state)
    ref = p[ref_frame]
    d = 0.5 * np.abs(p - ref[None, :]).sum(axis=1)
    lo, hi = max(centre_frame - half, 0), min(centre_frame + half, d.size)
    seg = d[lo:hi]
    if seg.size < 4:
        return float("nan")
    final = float(np.median(seg[-max(half // 3, 1):]))
    start = float(np.median(seg[: max(half // 3, 1)]))
    if final - start < 1e-6:
        return float("nan")
    tgt = start + 0.5 * (final - start)
    above = np.nonzero(seg >= tgt)[0]
    if above.size == 0:
        return float("nan")
    j = int(above[0])
    if j == 0:
        return float(lo)
    y0, y1 = seg[j - 1], seg[j]
    frac = 0.0 if y1 == y0 else (tgt - y0) / (y1 - y0)
    return float(lo + (j - 1) + frac)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--git-head", type=str, default="UNKNOWN")
    args = ap.parse_args()
    prereg = json.loads(PREREG.read_text())

    rows = []
    for cf_id, cf_s in (("crossfade_4ms", CROSSFADE_S), ("hard_switch", 0.0)):
        for shape, energy in (("AB", False), ("ABA", False), ("AB", True)):
            cond = f"{shape}{'_energy_matched' if energy else ''}"
            for a_name, a_p, b_name, b_p in PAIRS:
                y, notes, transitions, pair = build_case(
                    a_name, a_p, b_name, b_p, shape=shape, crossfade_s=cf_s, energy_matched=energy)
                times, chroma = host_chroma12(y.astype(np.float32))
                n = times.size
                st = pitch_class_state(notes, n)
                mov_audio = tv_movement(l1_rows(chroma[:n].astype(np.float64)))
                mov_sym = tv_movement(st["pc_mass"][:n])
                for T in transitions:
                    cf_frame = int(round(T * SR / HOP))
                    ca, pa = response_centre(mov_audio, cf_frame + MOVEMENT_LAG_HOPS // 2)
                    cs, ps = response_centre(mov_sym, cf_frame + MOVEMENT_LAG_HOPS // 2)
                    ref = max(cf_frame - 30, 0)
                    ha = half_rise(chroma[:n].astype(np.float64), ref, cf_frame)
                    hs = half_rise(st["pc_mass"][:n], ref, cf_frame)
                    rows.append({
                        "crossfade": cf_id, "condition": cond, "pair": pair,
                        "transition_s": T, "transition_frame": cf_frame,
                        "audio_response_centre_frame": round(ca, 3) if np.isfinite(ca) else None,
                        "symbolic_response_centre_frame": round(cs, 3) if np.isfinite(cs) else None,
                        "offset_hops_movement_centroid": round(ca - cs, 3) if np.isfinite(ca) and np.isfinite(cs) else None,
                        "audio_peak_frame": pa, "symbolic_peak_frame": ps,
                        "offset_hops_peak": pa - ps if pa >= 0 and ps >= 0 else None,
                        "audio_half_rise_frame": round(ha, 3) if np.isfinite(ha) else None,
                        "symbolic_half_rise_frame": round(hs, 3) if np.isfinite(hs) else None,
                        "offset_hops_half_rise": round(ha - hs, 3) if np.isfinite(ha) and np.isfinite(hs) else None,
                    })

    def agg(key, sel=None):
        v = [r[key] for r in rows if r[key] is not None and (sel is None or sel(r))]
        if not v:
            return None
        v = np.asarray(v, dtype=np.float64)
        return {"n": int(v.size), "median": round(float(np.median(v)), 3),
                "iqr": round(float(np.percentile(v, 75) - np.percentile(v, 25)), 3),
                "min": round(float(v.min()), 3), "max": round(float(v.max()), 3)}

    summary = {
        "offset_hops_movement_centroid": agg("offset_hops_movement_centroid"),
        "offset_hops_half_rise": agg("offset_hops_half_rise"),
        "offset_hops_peak": agg("offset_hops_peak"),
        "by_crossfade": {
            c: agg("offset_hops_half_rise", lambda r, c=c: r["crossfade"] == c)
            for c in ("crossfade_4ms", "hard_switch")
        },
        "by_condition": {
            c: agg("offset_hops_half_rise", lambda r, c=c: r["condition"] == c)
            for c in ("AB", "ABA", "AB_energy_matched")
        },
    }

    # primary estimator is the half-rise crossing: a step-response group delay,
    # far more robust than a centroid over a windowed difference signal.
    prim = summary["offset_hops_half_rise"]
    med, iqr = (prim or {}).get("median"), (prim or {}).get("iqr")
    conds = [v["median"] for v in summary["by_condition"].values() if v]
    cfs = [v["median"] for v in summary["by_crossfade"].values() if v]
    cf_disagree = (len(cfs) == 2 and abs(cfs[0] - cfs[1]) > 1.0)

    if med is None or iqr is None:
        outcome = "CHROMA_PHASE_INCONCLUSIVE"
    elif med >= -0.25 or cf_disagree:
        outcome = "CHROMA_PHASE_NOT_EXPLAINED"
    elif -1.5 <= med <= -0.5 and iqr <= 1.0 and all(c < 0 for c in conds):
        outcome = "CHROMA_PHASE_EXPLAINED"
    else:
        outcome = "CHROMA_PHASE_INCONCLUSIVE"

    receipt = {
        "schema": "spectrasynq.chroma_timing_result.v1",
        "job": "J3D-C1", "label": "HOST-ONLY DETERMINISTIC FIXTURE",
        "git_head": args.git_head,
        "preregistration": str(PREREG.relative_to(ROOT)),
        "preregistration_written_before_any_fixture_score": prereg["written_before_any_fixture_score"],
        "used_babyslakh": False, "used_M_tv": False, "optimised_a_lag_against_a_hypothesis": False,
        "analytical_timing": prereg["analytical_timing"],
        "fixture": {"pairs": len(PAIRS), "conditions": 3, "crossfades": 2,
                    "n_transitions_measured": len(rows),
                    "n_harmonics": N_HARMONICS, "crossfade_s": CROSSFADE_S},
        "primary_estimator": "offset_hops_half_rise = (audio 50% rise frame) - (symbolic 50% rise frame). A step-response group delay.",
        "summary": summary,
        "rows": rows,
        "outcome": outcome,
        "thresholds_applied": prereg["outcome_thresholds"],
        "what_this_can_never_establish": prereg["what_this_can_never_establish"],
        "student_io_frozen": False, "titan": False, "production_firmware_changed": False,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"outcome": outcome, "summary": summary}, indent=2))
    print(f"receipt -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
