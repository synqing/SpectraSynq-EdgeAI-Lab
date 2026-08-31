"""Quantitative P3-C close on LED dumps. Captain is not the validator.

Circular trap: D is driven by source share, so r(pixels, share) without a
mix control is not a pass. The extra-DoF test is whether D's *wave head
position* tracks share after mix RMS is partialled out, compared with B
(same extra DoF driven by mix).

Waveform Tempo native polarity: extra gain moves the head toward the tip
and shortens the trail, so mean luminance often *falls* as gain rises.
Position is the load-bearing feature; luminance is a diagnostic.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

import numpy as np
from numpy.typing import NDArray

from edgeai.mir.p3c_score import frame_luminance, head_position_upper
from edgeai.mir.trigger_budget import local_peaks

HOP_S = 512.0 / 16_000.0
DELTA_SHARE_MIN = 0.15
POS_GAIN_MIN = 0.40
ARRANGEMENT_DELTA_MIN = 0.15
EVENT_F1_DELTA_MIN = 0.05


def _finite_pair(x: NDArray, y: NDArray) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    a = np.asarray(x, dtype=np.float64).reshape(-1)
    b = np.asarray(y, dtype=np.float64).reshape(-1)
    n = min(a.size, b.size)
    a, b = a[:n], b[:n]
    m = np.isfinite(a) & np.isfinite(b)
    return a[m], b[m]


def pearson(x: NDArray, y: NDArray) -> float:
    a, b = _finite_pair(x, y)
    if a.size < 8 or float(a.std()) < 1e-12 or float(b.std()) < 1e-12:
        return float("nan")
    return float(np.corrcoef(a, b)[0, 1])


def spearman(x: NDArray, y: NDArray) -> float:
    a, b = _finite_pair(x, y)
    if a.size < 8 or float(a.std()) < 1e-12 or float(b.std()) < 1e-12:
        return float("nan")
    ra = a.argsort().argsort().astype(np.float64)
    rb = b.argsort().argsort().astype(np.float64)
    return pearson(ra, rb)


def partial_pearson(x: NDArray, y: NDArray, z: NDArray) -> float:
    """r(x, y | z). Mix RMS is z when testing share increment in pixels."""
    rxy, rxz, ryz = pearson(x, y), pearson(x, z), pearson(y, z)
    if any(v != v for v in (rxy, rxz, ryz)):
        return float("nan")
    den = (1.0 - rxz * rxz) * (1.0 - ryz * ryz)
    if den <= 1e-12:
        return float("nan")
    return float((rxy - rxz * ryz) / np.sqrt(den))


def f1_at_tol(pred: list[int], truth: list[int], *, tol: int = 3) -> float:
    if not pred and not truth:
        return float("nan")
    if not pred or not truth:
        return 0.0
    used: set[int] = set()
    tp = 0
    for p in pred:
        hits = [g for g in truth if g not in used and abs(g - p) <= tol]
        if not hits:
            continue
        g = min(hits, key=lambda t: abs(t - p))
        used.add(g)
        tp += 1
    prec = tp / len(pred)
    rec = tp / len(truth)
    if prec + rec == 0.0:
        return 0.0
    return float(2.0 * prec * rec / (prec + rec))


def visual_transients(leds: NDArray, *, refractory: int = 4) -> list[int]:
    lum = frame_luminance(leds)
    d = np.abs(np.diff(lum, prepend=lum[:1]))
    std = float(np.std(d))
    thresh = max(1.0, 0.5 * std)
    return local_peaks(d, thresh=thresh, refractory=refractory)


def slice_oracle(oracle: Mapping[str, NDArray], start_s: float, n: int) -> dict[str, NDArray]:
    t = np.asarray(oracle["times"], dtype=np.float64)
    i0 = int(np.searchsorted(t, float(start_s), side="left"))
    out: dict[str, NDArray] = {}
    for k, v in oracle.items():
        a = np.asarray(v)
        if a.shape[:1] == (t.shape[0],):
            out[k] = a[i0 : i0 + n]
        else:
            out[k] = a
    return out


def cache_path(cache_dir: Path, track: str) -> Path:
    safe = "".join(ch if ch.isalnum() or ch in "-_." else "_" for ch in track)
    for sub in ("train", "test"):
        p = Path(cache_dir) / f"{sub}_{safe}.npz"
        if p.is_file():
            return p
    raise FileNotFoundError(f"oracle cache missing for {track}")


def leds_path(p3c_dir: Path, track: str, set_name: str) -> Path:
    safe = "".join(ch if ch.isalnum() or ch in "-_." else "_" for ch in track)
    return Path(p3c_dir) / f"{safe}_{set_name}_leds.npz"


def score_clip(leds: Mapping[str, NDArray], oracle: Mapping[str, NDArray], meta: Mapping[str, Any]) -> dict[str, Any]:
    n = min(int(meta["n"]), int(np.asarray(leds["A"]).shape[0]), int(np.asarray(oracle["mix_rms"]).shape[0]))
    src = str(meta["share_driver"]).replace("_share", "")
    share = np.asarray(oracle[f"{src}_share"], dtype=np.float64)[:n]
    ab = np.asarray(oracle[f"{src}_abs"], dtype=np.float64)[:n]
    mix = np.asarray(oracle["mix_rms"], dtype=np.float64)[:n]
    cc = np.asarray(oracle["composition_change"], dtype=np.float64)[:n]
    drums = np.asarray(oracle["drums_abs"], dtype=np.float64)[:n]
    rec: dict[str, Any] = {
        "track": meta["track"],
        "set": meta.get("set"),
        "share_driver": meta["share_driver"],
        "n": n,
        "start_s": float(meta.get("start_s") or 0.0),
        "mad_B_vs_D": float(meta.get("mad_B_vs_D") or float("nan")),
        "mad_control_vs_mir": float(meta.get("mad_control_vs_mir") or float("nan")),
        "triggers_control": int(meta.get("triggers_control") or 0),
        "triggers_mir": int(meta.get("triggers_mir") or 0),
    }
    for cond in ("A", "B", "D"):
        pos = head_position_upper(np.asarray(leds[cond])[:n])
        lum = frame_luminance(np.asarray(leds[cond])[:n])
        gain = np.asarray(leds[f"gain_{cond}"], dtype=np.float64)[:n]
        rec[f"spearman_{cond}_pos_gain"] = spearman(pos, gain)
        rec[f"spearman_{cond}_lum_gain"] = spearman(lum, gain)
        rec[f"partial_{cond}_pos_share_mix"] = partial_pearson(pos, share, mix)
        rec[f"partial_{cond}_pos_abs_mix"] = partial_pearson(pos, ab, mix)
        rec[f"partial_{cond}_pos_cc_mix"] = partial_pearson(pos, cc, mix)
        rec[f"partial_{cond}_lum_share_mix"] = partial_pearson(lum, share, mix)
    rec["delta_pos_share"] = rec["partial_D_pos_share_mix"] - rec["partial_B_pos_share_mix"]
    rec["delta_pos_abs"] = rec["partial_D_pos_abs_mix"] - rec["partial_B_pos_abs_mix"]
    rec["delta_pos_cc"] = rec["partial_D_pos_cc_mix"] - rec["partial_B_pos_cc_mix"]

    ref = max(1, int(round(0.25 / HOP_S)))
    drum_peaks = local_peaks(drums, thresh=float(np.quantile(drums, 0.85)), refractory=ref)
    cc_peaks = local_peaks(cc, thresh=float(np.quantile(cc, 0.85)), refractory=ref)
    rec["n_drum_peaks"] = len(drum_peaks)
    rec["n_cc_peaks"] = len(cc_peaks)
    for ev in ("control", "mir"):
        vis = visual_transients(np.asarray(leds[ev])[:n])
        rec[f"n_visual_{ev}"] = len(vis)
        rec[f"f1_{ev}_drums"] = f1_at_tol(vis, drum_peaks, tol=3)
        rec[f"f1_{ev}_cc"] = f1_at_tol(vis, cc_peaks, tol=3)
    rec["delta_f1_drums"] = rec["f1_mir_drums"] - rec["f1_control_drums"]
    rec["delta_f1_cc"] = rec["f1_mir_cc"] - rec["f1_control_cc"]
    rec["event_vacuous"] = rec["triggers_control"] == 0 and rec["triggers_mir"] == 0
    return rec


def _median(xs: list[float]) -> float:
    a = np.asarray([x for x in xs if x == x], dtype=np.float64)
    return float(np.median(a)) if a.size else float("nan")


def _wins(rows: list[dict[str, Any]], field: str) -> tuple[int, int]:
    vals = [r[field] for r in rows if r.get(field) == r.get(field)]
    return int(sum(v > 0 for v in vals)), int(len(vals))


def summarise(rows: list[dict[str, Any]]) -> dict[str, Any]:
    def pack(subset: str | None) -> dict[str, Any]:
        rs = rows if subset is None else [r for r in rows if r.get("set") == subset]
        w_share, n_share = _wins(rs, "delta_pos_share")
        w_abs, n_abs = _wins(rs, "delta_pos_abs")
        w_cc, n_cc = _wins(rs, "delta_pos_cc")
        w_f1, n_f1 = _wins(rs, "delta_f1_drums")
        vacuous = int(sum(bool(r.get("event_vacuous")) for r in rs))
        q1 = _median([r["spearman_B_pos_gain"] for r in rs] + [r["spearman_D_pos_gain"] for r in rs])
        q1_pass = q1 >= POS_GAIN_MIN
        d_share = _median([r["delta_pos_share"] for r in rs])
        q2_pass = d_share >= DELTA_SHARE_MIN and (n_share == 0 or w_share / n_share >= 0.70)
        d_abs = _median([r["delta_pos_abs"] for r in rs])
        q3_pass = d_abs >= DELTA_SHARE_MIN and (n_abs == 0 or w_abs / n_abs >= 0.70)
        d_cc = _median([r["delta_pos_cc"] for r in rs])
        q4_pass = d_cc >= ARRANGEMENT_DELTA_MIN
        d_f1 = _median([r["delta_f1_drums"] for r in rs])
        q5_pass = d_f1 >= EVENT_F1_DELTA_MIN and (n_f1 == 0 or w_f1 / n_f1 >= 0.60)
        return {
            "n_clips": len(rs),
            "median_spearman_pos_gain": q1,
            "median_spearman_B_pos_gain": _median([r["spearman_B_pos_gain"] for r in rs]),
            "median_spearman_D_pos_gain": _median([r["spearman_D_pos_gain"] for r in rs]),
            "median_spearman_lum_gain": _median(
                [r["spearman_B_lum_gain"] for r in rs] + [r["spearman_D_lum_gain"] for r in rs]
            ),
            "median_partial_B_pos_share_mix": _median([r["partial_B_pos_share_mix"] for r in rs]),
            "median_partial_D_pos_share_mix": _median([r["partial_D_pos_share_mix"] for r in rs]),
            "median_delta_pos_share": d_share,
            "wins_delta_pos_share": [w_share, n_share],
            "median_delta_pos_abs": d_abs,
            "wins_delta_pos_abs": [w_abs, n_abs],
            "median_delta_pos_cc": d_cc,
            "wins_delta_pos_cc": [w_cc, n_cc],
            "median_f1_control_drums": _median([r["f1_control_drums"] for r in rs]),
            "median_f1_mir_drums": _median([r["f1_mir_drums"] for r in rs]),
            "median_delta_f1_drums": d_f1,
            "wins_delta_f1_drums": [w_f1, n_f1],
            "median_delta_f1_cc": _median([r["delta_f1_cc"] for r in rs]),
            "n_event_vacuous": vacuous,
            "Q1_knob_is_head_position": "PASS" if q1_pass else "FAIL",
            "Q2_share_increment_in_pixels": "PASS" if q2_pass else "FAIL",
            "Q3_source_abs_after_mix": "PASS" if q3_pass else "FAIL",
            "Q4_arrangement_in_pixels": "PASS" if q4_pass else "FAIL",
            "Q5_comet_beats_loudness_at_drums": "PASS" if q5_pass else "FAIL",
        }

    all_s = pack(None)
    ch = pack("challenge")
    ho = pack("holdout")
    share_ok = ho["Q2_share_increment_in_pixels"] == "PASS" and ho["Q3_source_abs_after_mix"] == "PASS"
    events_ok = ho["Q5_comet_beats_loudness_at_drums"] == "PASS"
    return {
        "label": "HOST-ONLY",
        "phase": "P3-C-QUANT",
        "engine_feature": "waveform_tempo upper-half head position",
        "circular_trap": "r(pixels, share) without partialling mix is not a pass",
        "all": all_s,
        "challenge": ch,
        "holdout": ho,
        "stamps": {
            "share_x_waveform_tempo_x_head_position": "PASS" if share_ok else "FAIL",
            "composition_change_x_comet_x_impact_launch": "FAIL" if not events_ok else "PASS",
            "composition_change_x_comet_x_impact_launch_note": (
                "Fails this comparator only. Not a global verdict on composition_change. "
                "Arrangement-state may still suit morph/transition/spatial-redistribution grammars."
            ),
            "student_share_head": "CANDIDATE" if share_ok else "NO",
            "student_event_head": "NO",
            "demucs": "NO",
            "student_gate": "OPEN",
            "waveform_tempo_role": "reference_continuity_carrier",
        },
    }
