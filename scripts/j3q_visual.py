#!/usr/bin/env python3
"""J3Q - CONDITIONAL mixture visual test, strictly out of fold.

For every held-out track, THAT fold's model is applied to the MIXTURE from the
same held-out track. No mixture-specific model is trained. J3E grammar unchanged.
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
from j3q_head import FAMS, N_FOLDS, SEED, labels_for, load_rows  # noqa: E402

sys.path.insert(0, str(C.ROOT / "src"))
from edgeai.mir.harmonic_movement import tv_movement  # noqa: E402
from edgeai.mir.harmonic_visual import pipeline  # noqa: E402
from edgeai.mir.restraint_head import TinyHead, standardiser  # noqa: E402

FEAT = Path("/tmp/j3q_feat")
TOL_HOPS = 2
ORDER = ["CONTROL_C3", "TREATMENT_C3_TIMES_Q_OOF", "ORACLE"]


def visual(blocks, state_key, mov_key, cls, resting) -> dict:
    de_all, rev_all = [], []
    for b in blocks:
        r = pipeline(b["states"][state_key], b["mov"][mov_key], with_floor=False)
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
            "flat_energy_harmonic_recall": et["HARMONIC_CHANGE_FLAT_ENERGY"],
            "no_onset_harmonic_recall": et["HARMONIC_CHANGE_NO_ONSET"],
            "acoustic_only_false_response": et["ACOUSTIC_CHANGE_LOW_HARMONIC_CHANGE"],
            "resting_median_deltaE": round(float(np.median(de_now[resting])), 4),
            "direction_reversal_rate": round(float(rev.mean()), 4) if rev.size else None,
            "mean_harmonic_recall": round(hr, 4),
            "selectivity_margin": round(hr - et["ACOUSTIC_CHANGE_LOW_HARMONIC_CHANGE"], 4),
            "n_frames": int(len(de_now))}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    rows = load_rows(args.corpus)
    tracks = sorted({r["track"] for r in rows})
    folds = np.array_split(np.random.default_rng(SEED).permutation(np.array(tracks)), N_FOLDS)

    mix_q, oof_check = {}, []
    for fi, held in enumerate(folds):
        held = set(held.tolist())
        tr_rows = [r for r in rows if r["track"] not in held]
        if not tr_rows:
            continue
        Xs, Ys = [], []
        for r in tr_rows:
            use, y = labels_for(r)
            Xs.append(r["x"][r["mask"]][use]); Ys.append(y)
        X, Y = np.vstack(Xs), np.concatenate(Ys)
        mu, sd = standardiser(X)
        head = TinyHead(seed=SEED + fi)
        head.fit((X - mu) / sd, Y, seed=SEED + fi)
        for t in sorted(held):                       # the mixture of a HELD-OUT track only
            ff = FEAT / f"mix__{t}.npz"
            if not ff.is_file():
                continue
            x = np.load(ff)["x"].astype(np.float64)
            good = np.isfinite(x).all(axis=1)
            q = np.full(x.shape[0], np.nan)
            q[good] = head.forward((x[good] - mu) / sd)
            mix_q[t] = q
            oof_check.append(t not in {r["track"] for r in tr_rows})

    blocks = []
    for t in tracks:
        if t not in mix_q:
            continue
        b = C.cached_track(args.corpus / t)
        n = len(b["valid"])
        q = mix_q[t][:n]
        good = np.isfinite(q)
        c3s = b["states"]["C3_ROOT_SALIENCE"]
        b["states"]["CONTROL_C3"] = c3s
        b["states"]["TREATMENT_C3_TIMES_Q_OOF"] = c3s          # SAME state, by design
        b["states"]["ORACLE"] = b["oracle_state"]
        mv = tv_movement(c3s)
        b["mov"]["CONTROL_C3"] = mv
        b["mov"]["TREATMENT_C3_TIMES_Q_OOF"] = mv * q
        b["mov"]["ORACLE"] = b["M_oracle"]
        b["valid"] = b["valid"] & good & np.isfinite(mv * q)
        blocks.append(b)

    cls, _, _ = C.challenge_masks(blocks)
    counts = {k: int(v.sum()) for k, v in cls.items()}
    resting = ~(cls["HARMONIC_CHANGE_FLAT_ENERGY"] | cls["HARMONIC_CHANGE_NO_ONSET"]
                | cls["ACOUSTIC_CHANGE_LOW_HARMONIC_CHANGE"])
    vis = {k: visual(blocks, k, k, cls, resting) for k in ORDER}

    ctrl, trt = vis["CONTROL_C3"], vis["TREATMENT_C3_TIMES_Q_OOF"]
    guards = {
        "G1_selectivity_margin_ge_C3": {
            "control": ctrl["selectivity_margin"], "treatment": trt["selectivity_margin"],
            "pass": bool(trt["selectivity_margin"] >= ctrl["selectivity_margin"])},
        "G2_resting_median_deltaE_le_C3": {
            "control": ctrl["resting_median_deltaE"], "treatment": trt["resting_median_deltaE"],
            "pass": bool(trt["resting_median_deltaE"] <= ctrl["resting_median_deltaE"])},
        "G3_reversal_rate_le_C3": {
            "control": ctrl["direction_reversal_rate"], "treatment": trt["direction_reversal_rate"],
            "pass": bool(trt["direction_reversal_rate"] <= ctrl["direction_reversal_rate"])},
    }
    payload = {
        "schema": "spectrasynq.learned_restraint_visual.v1", "job": "J3Q",
        "label": "CONDITIONAL MIXTURE VISUAL TEST, STRICTLY OUT OF FOLD. J3E grammar UNCHANGED.",
        "grammar": ("J3E HARMONIC COLOUR TRANSITION unchanged: M_REF 0.35, A_MIN 0.02, A_MAX 0.60, "
                    "photons 1.0, exposure 2.2, without_floor, +/-2-hop event tolerance, threshold = "
                    "p90 of each condition's own resting frames"),
        "grammar_modified": False,
        "out_of_fold_construction": ("for each fold, the model trained WITHOUT a track was applied to "
                                     "that track's mixture. No mixture-specific model was trained."),
        "every_mixture_strictly_held_out": bool(all(oof_check)),
        "control_challenge_membership": {"counts": counts,
                                         "matches_J3D_A_v2": counts == {
                                             "HARMONIC_CHANGE_FLAT_ENERGY": 2299,
                                             "HARMONIC_CHANGE_NO_ONSET": 4000,
                                             "ACOUSTIC_CHANGE_LOW_HARMONIC_CHANGE": 3292}},
        "same_state_both_arms": "the C3 state is identical in CONTROL and TREATMENT; only the movement differs",
        "conditions": vis,
        "restraint_guards": guards,
        "all_three_guards_pass": bool(all(g["pass"] for g in guards.values())),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps({"counts": counts, "guards": guards,
                      "margins": {k: vis[k]["selectivity_margin"] for k in ORDER}}, indent=2))
    print(f"receipt -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
