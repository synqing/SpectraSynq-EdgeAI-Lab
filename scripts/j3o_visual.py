#!/usr/bin/env python3
"""J3O - CONDITIONAL mixture visual test.

Triggered by the pre-registered rule: at least one PRIMARY family reduced false
movement versus C3 while satisfying the recall guard. The J3E visual grammar is
used UNCHANGED. No visual grammar change.
"""
from __future__ import annotations

import argparse
import json
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import j3g_common as C  # noqa: E402

sys.path.insert(0, str(C.ROOT / "src"))
from edgeai.mir import crp as K  # noqa: E402
from edgeai.mir.harmonic_movement import tv_movement  # noqa: E402
from edgeai.mir.harmonic_visual import pipeline  # noqa: E402

NNLSC, PITCHMIX = Path("/tmp/j3o_cache"), Path("/tmp/j3m_cache")
TOL_HOPS = 2
ORDER = ["P0_CURRENT", "C3_ROOT_SALIENCE", "NNLS_FRONTEND_ONLY", "NNLS_NOTES",
         "NNLS_PUBLISHED_CHROMA", "ORACLE"]


def l1n(x):
    s = np.abs(x).sum(axis=1, keepdims=True)
    return np.divide(x, s, out=np.zeros_like(x), where=s > 0)


def add_nnls(b: dict) -> dict:
    f = NNLSC / f"mix__{b['track']}.npz"
    n = b["n"]
    z = np.load(f, allow_pickle=False)
    for arm in ("NNLS_FRONTEND_ONLY", "NNLS_NOTES", "NNLS_PUBLISHED_CHROMA"):
        x = z[arm][:n].astype(np.float64)
        bad = ~np.isfinite(x).all(axis=1)
        x[bad] = 0.0
        st = l1n(x)
        # the J3E grammar needs a colour state on every valid frame; the 3 leading
        # frames with no plugin frame are removed from validity instead of filled
        b["states"][arm] = st
        mv = tv_movement(st)
        mv[bad] = np.nan
        b["mov"][arm] = mv
        b["valid"] = b["valid"] & ~bad & np.isfinite(mv)
    return b


def visual(blocks, key, cls, resting) -> dict:
    de_all, rev_all = [], []
    for b in blocks:
        r = pipeline(b["states"][key], b["mov"][key], with_floor=False)
        de = np.nan_to_num(r["delta_e"], nan=0.0)
        tol = np.copy(de)
        for k in range(1, TOL_HOPS + 1):
            tol[:-k] = np.maximum(tol[:-k], de[k:])
            tol[k:] = np.maximum(tol[k:], de[:-k])
        de_all.append(np.column_stack([de[b["valid"]], tol[b["valid"]]]))
        d = np.diff(r["colour"], axis=0)
        dot = (d[1:] * d[:-1]).sum(axis=1)
        m = b["valid"][2:]
        rev_all.append(dot[m] < 0 if m.sum() else np.zeros(0, dtype=bool))
    arr = np.vstack(de_all)
    de_now, de_tol = arr[:, 0], arr[:, 1]
    rev = np.concatenate(rev_all)
    thr = float(np.percentile(de_now[resting], 90))
    rt, rn = de_tol >= thr, de_now >= thr
    et = {k: round(float(rt[m].mean()), 4) for k, m in cls.items()}
    hr = 0.5 * (et["HARMONIC_CHANGE_FLAT_ENERGY"] + et["HARMONIC_CHANGE_NO_ONSET"])
    return {"threshold_deltaE_p90_of_own_resting_frames": round(thr, 4),
            "consumer_time": {k: round(float(rn[m].mean()), 4) for k, m in cls.items()},
            "event_tolerant": et,
            "resting_median_deltaE": round(float(np.median(de_now[resting])), 4),
            "direction_reversal_rate": round(float(rev.mean()), 4) if rev.size else None,
            "mean_harmonic_recall": round(hr, 4),
            "selectivity_margin": round(hr - et["ACOUSTIC_CHANGE_LOW_HARMONIC_CHANGE"], 4),
            "n_frames": int(len(de_now))}


def run(blocks) -> dict:
    cls, _, _ = C.challenge_masks(blocks)
    resting = ~(cls["HARMONIC_CHANGE_FLAT_ENERGY"] | cls["HARMONIC_CHANGE_NO_ONSET"]
                | cls["ACOUSTIC_CHANGE_LOW_HARMONIC_CHANGE"])
    out = {k: visual(blocks, k, cls, resting) for k in ORDER}
    out["_counts"] = {k: int(v.sum()) for k, v in cls.items()}
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    split = C.split_tracks(args.corpus)
    allb = []
    for t in split["all"]:
        b = C.cached_track(args.corpus / t)
        b["n"] = len(b["valid"])
        b = add_nnls(b)
        b["states"]["ORACLE"] = b["oracle_state"]
        b["mov"]["ORACLE"] = b["M_oracle"]
        allb.append(b)

    prim = run(allb)
    hold = [b for b in allb if b["track"] in set(split["final_holdout"])]
    sec = run(hold)

    payload = {
        "schema": "spectrasynq.nnls_visual.v1", "job": "J3O",
        "label": "CONDITIONAL MIXTURE VISUAL TEST. J3E grammar UNCHANGED. HOST analysis on consumed data.",
        "grammar": ("J3E HARMONIC COLOUR TRANSITION unchanged: M_REF 0.35, A_MIN 0.02, A_MAX 0.60, "
                    "photons 1.0, exposure 2.2, without_floor, +/-2-hop event tolerance, threshold = "
                    "p90 of each condition's own resting frames"),
        "grammar_modified": False,
        "headline_metric": "selectivity margin = mean(event-tolerant harmonic recall) - event-tolerant acoustic false response",
        "PRIMARY_all_20_mixes": prim,
        "SECONDARY_10_track_subset_for_comparability_with_J3G2": {
            "why": ("the published J3G.2 Level-C margins were computed on the 10-track former holdout. "
                    "This subset is reported so those numbers are compared like with like. The "
                    "dev/holdout split is CONSUMED and protects nothing; it is a comparability aid only."),
            "conditions": sec},
        "margins_primary": {k: prim[k]["selectivity_margin"] for k in ORDER},
        "margins_secondary": {k: sec[k]["selectivity_margin"] for k in ORDER},
        "validity_note": ("the 3 leading frames per mix that have no corresponding plugin frame under "
                          "the +3 alignment are REMOVED from validity for every arm, so all arms are "
                          "scored on an identical frame set. They are not zero-filled."),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps({"counts_primary": prim["_counts"],
                      "margins_primary": payload["margins_primary"],
                      "margins_secondary": payload["margins_secondary"]}, indent=2))
    print(f"receipt -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
