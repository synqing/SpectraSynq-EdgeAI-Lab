#!/usr/bin/env python3
"""Offline C0 diagnosis from captured dumps. No device. Does not change FAIL stamp."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from edgeai.mir.p3c_quant import HOP_S, cache_path, score_clip, slice_oracle, spearman, summarise
from edgeai.mir.p3c_score import frame_luminance, head_position_upper

DUMP = ROOT / "artifacts/gate_c0/dumps"
OUT = ROOT / "artifacts/gate_c0"


def _safe(name: str) -> str:
    return "".join(ch if ch.isalnum() or ch in "-_." else "_" for ch in name)


def load_cond(track: str, rate_tag: str) -> dict | None:
    s = _safe(track)
    out: dict = {}
    for cond in "ABD":
        p = DUMP / f"{s}_{rate_tag}_{cond}.npz"
        if not p.is_file():
            return None
        z = np.load(p)
        out[cond] = np.asarray(z["leds"])
        out[f"gain_{cond}"] = np.asarray(z["gain"], dtype=np.float64)
    out["control"] = out["A"]
    out["mir"] = out["A"]
    return out


def oracle_for(row: dict, cache_dir: Path) -> tuple[dict, int]:
    n = int(row["n"])
    start = float(row["start_s"])
    full = dict(np.load(cache_path(cache_dir, row["track"])))
    o = slice_oracle(full, start, n)
    n = min(n, int(np.asarray(o["mix_rms"]).shape[0]))
    nt = int(np.asarray(o["times"]).shape[0])
    for k, v in list(o.items()):
        a = np.asarray(v)
        if a.shape[:1] == (nt,):
            o[k] = a[:n]
    return o, n


def lag_scan(leds: np.ndarray, gain: np.ndarray, max_lag: int = 40) -> dict:
    pos = head_position_upper(leds)
    g = np.asarray(gain, dtype=np.float64).reshape(-1)
    n = min(int(pos.size), int(g.size))
    pos, g = pos[:n], g[:n]
    best = {"lag": 0, "lag_s": 0.0, "spearman": float("nan")}
    for lag in range(-max_lag, max_lag + 1):
        if lag > 0:
            a, b = pos[lag:], g[: n - lag]
        elif lag < 0:
            a, b = pos[: n + lag], g[-lag:]
        else:
            a, b = pos, g
        sp = spearman(a, b)
        if sp == sp and (best["spearman"] != best["spearman"] or sp > best["spearman"]):
            best = {"lag": int(lag), "lag_s": float(lag) * HOP_S, "spearman": float(sp)}
    return best


def shift_pair(leds: np.ndarray, gain: np.ndarray, lag: int) -> tuple[np.ndarray, np.ndarray]:
    n = min(int(leds.shape[0]), int(gain.shape[0]))
    a, g = leds[:n], gain[:n]
    if lag > 0:
        return a[lag:], g[: n - lag]
    if lag < 0:
        return a[: n + lag], g[-lag:]
    return a, g


def main() -> int:
    receipt = json.loads((ROOT / "artifacts/source_activity/p3c/receipt_musdb18_p3c.json").read_text())
    holdout = [r for r in receipt["scores"] if r.get("set") == "holdout"]
    cache_dir = ROOT / "artifacts/source_activity/musdb18_oracle_cache"

    diag_clips: list[dict] = []
    native_rows: list[dict] = []
    for row in holdout:
        leds = load_cond(row["track"], "r31.25_d0ms")
        if leds is None:
            diag_clips.append({"track": row["track"], "missing": True})
            continue
        oracle, n = oracle_for(row, cache_dir)
        rec = score_clip(leds, oracle, row)
        native_rows.append(rec)
        clip: dict = {"track": row["track"]}
        for cond in "ABD":
            pos = head_position_upper(leds[cond])[:n]
            g = leds[f"gain_{cond}"][:n]
            lum = frame_luminance(leds[cond])[:n]
            best = lag_scan(leds[cond][:n], g)
            clip[cond] = {
                "gain_min": float(np.min(g)),
                "gain_max": float(np.max(g)),
                "gain_std": float(np.std(g)),
                "pos_min": float(np.nanmin(pos)),
                "pos_max": float(np.nanmax(pos)),
                "pos_std": float(np.nanstd(pos)),
                "pos_finite": int(np.isfinite(pos).sum()),
                "frac_rail_tip": float(np.mean(np.isfinite(pos) & (pos >= 78.0))),
                "lum_mean": float(np.nanmean(lum)),
                "spearman_pos_gain": rec[f"spearman_{cond}_pos_gain"],
                "best_lag_hops": best["lag"],
                "best_lag_s": best["lag_s"],
                "best_lag_spearman": best["spearman"],
            }
        clip["delta_pos_share"] = rec["delta_pos_share"]
        clip["partial_B"] = rec["partial_B_pos_share_mix"]
        clip["partial_D"] = rec["partial_D_pos_share_mix"]
        diag_clips.append(clip)

    lags = [
        int(c["D"]["best_lag_hops"])
        for c in diag_clips
        if "D" in c and c["D"]["best_lag_spearman"] == c["D"]["best_lag_spearman"]
    ]
    med_best_lag = int(np.median(np.asarray(lags))) if lags else 0

    lag_rows: list[dict] = []
    for row in holdout:
        leds = load_cond(row["track"], "r31.25_d0ms")
        if leds is None:
            continue
        oracle, n = oracle_for(row, cache_dir)
        shifted: dict = {}
        nn = n
        for cond in "ABD":
            a, g = shift_pair(leds[cond][:n], leds[f"gain_{cond}"][:n], med_best_lag)
            shifted[cond] = a
            shifted[f"gain_{cond}"] = g
            nn = min(nn, int(a.shape[0]), int(g.shape[0]))
        for cond in "ABD":
            shifted[cond] = shifted[cond][:nn]
            shifted[f"gain_{cond}"] = shifted[f"gain_{cond}"][:nn]
        nt = int(np.asarray(oracle["times"]).shape[0])
        o2 = {}
        for k, v in oracle.items():
            a = np.asarray(v)
            o2[k] = a[:nn] if a.shape[:1] == (nt,) else v
        shifted["control"] = shifted["A"]
        shifted["mir"] = shifted["A"]
        meta = dict(row)
        meta["n"] = nn
        lag_rows.append(score_clip(shifted, o2, meta))

    hz20: list[dict] = []
    for row in holdout:
        leds = load_cond(row["track"], "r20_d0ms")
        if leds is None:
            continue
        oracle, n = oracle_for(row, cache_dir)
        rec = score_clip(leds, oracle, row)
        rec["rate_hz"] = 20.0
        hz20.append(rec)

    nat_sum = summarise(native_rows)
    lag_sum = summarise(lag_rows) if lag_rows else {}
    hz20_sum = summarise(hz20) if hz20 else None

    q1 = nat_sum["holdout"]["median_spearman_pos_gain"]
    q1_lag = lag_sum.get("holdout", {}).get("median_spearman_pos_gain")
    rail = float(np.median([c["D"]["frac_rail_tip"] for c in diag_clips if "D" in c]))
    pos_std_a = float(np.median([c["A"]["pos_std"] for c in diag_clips if "A" in c]))
    pos_std_d = float(np.median([c["D"]["pos_std"] for c in diag_clips if "D" in c]))
    best_sp_d = float(np.median([c["D"]["best_lag_spearman"] for c in diag_clips if "D" in c]))
    alignment = bool(q1_lag == q1_lag and q1_lag >= 0.40 and q1 < 0.40)
    if alignment:
        primary = "alignment: a fixed hop lag lifts Q1 over 0.40"
    elif best_sp_d == best_sp_d and best_sp_d < 0.40 and rail >= 0.40:
        primary = "head railed at tip — extra_gain mostly saturates the spatial carrier"
    elif best_sp_d == best_sp_d and best_sp_d < 0.40:
        primary = (
            "carrier moves but does not rank-track extra_gain even at best lag "
            "(inject/mic-swamp or live-tempo). Not a missing dump."
        )
    else:
        primary = "mixed: best-lag Spearman still below host; FAIL stands"

    out = {
        "stamp_unchanged": "ON_SILICON_PIXEL_FAIL",
        "native_summary": nat_sum["holdout"],
        "lag_diagnostic": {
            "note": "offline LED-vs-gain lag. Does not change stamped FAIL. Not a new threshold.",
            "fixed_lag_hops": med_best_lag,
            "fixed_lag_s": med_best_lag * HOP_S,
            "summary": lag_sum.get("holdout"),
        },
        "cadence_20hz": {
            "n_complete_clips": len(hz20),
            "tracks": [r["track"] for r in hz20],
            "summary": None if hz20_sum is None else hz20_sum["holdout"],
            "not_a_contract": True,
        },
        "cause": {
            "primary": primary,
            "alignment_lag_explains_Q1": alignment,
            "median_best_lag_hops": med_best_lag,
            "Q1_native": q1,
            "Q1_after_median_lag": q1_lag,
            "Q1_best_per_clip_lag_median_D": best_sp_d,
            "median_D_frac_railed_at_tip": rail,
            "median_pos_std_A_vs_D": [pos_std_a, pos_std_d],
        },
        "clips": diag_clips,
    }
    (OUT / "diagnosis.json").write_text(json.dumps(out, indent=2, default=str) + "\n")
    print("PRIMARY", primary)
    print("Q1", q1, "Q1_lag", q1_lag, "bestD", best_sp_d, "lag", med_best_lag, "rail", rail)
    print("20Hz", len(hz20))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
