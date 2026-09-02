#!/usr/bin/env python3
"""J3Q ANALYST-ADDED REPORTED DIAGNOSTIC - which causal feature blocks carry the
restraint signal, and is the synth/pad information absent or merely unused?

Block-level permutation importance on OUT-OF-FOLD predictions: for each frozen
feature block, shuffle that block across rows of the held-out data, recompute q,
and measure how much the family's q separation (median q at oracle EVENT frames
minus median q at STABLE-and-C3-high false-movement frames) collapses.

REPORTED, NOT GATED. No J3Q outcome depends on this.
"""
from __future__ import annotations

import argparse
import json
import sys
import warnings
from collections import defaultdict
from pathlib import Path

warnings.filterwarnings("ignore")
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import j3g_common as C  # noqa: E402
from j3q_head import EV, DET, N_FOLDS, SEED, STB, labels_for, load_rows, rank  # noqa: E402

sys.path.insert(0, str(C.ROOT / "src"))
from edgeai.mir.restraint_head import FEATURE_BLOCKS, TinyHead, standardiser  # noqa: E402


def separation(rs, qkey) -> float | None:
    qe, qf = [], []
    for r in rs:
        m = r["mask"]
        ro, rc = rank(r["Ms"][m]), rank(r["mov"][m])
        q = r[qkey][m]
        e, f_ = ro >= EV, (ro <= STB) & (rc >= DET)
        if e.sum() >= 10:
            qe.append(float(np.median(q[e])))
        if f_.sum() >= 10:
            qf.append(float(np.median(q[f_])))
    if not qe or not qf:
        return None
    return float(np.median(qe) - np.median(qf))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    rows = load_rows(args.corpus)
    tracks = sorted({r["track"] for r in rows})
    folds = np.array_split(np.random.default_rng(SEED).permutation(np.array(tracks)), N_FOLDS)

    spans, o = [], 0
    for name, d in FEATURE_BLOCKS:
        spans.append((name, o, o + d))
        o += d

    for r in rows:
        r["q"] = np.full(r["n"], np.nan)
        for name, _, _ in spans:
            r[f"q__{name}"] = np.full(r["n"], np.nan)

    prng = np.random.default_rng(SEED + 999)
    for fi, held in enumerate(folds):
        held = set(held.tolist())
        tr_rows = [r for r in rows if r["track"] not in held]
        te_rows = [r for r in rows if r["track"] in held]
        if not tr_rows or not te_rows:
            continue
        Xs, Ys = [], []
        for r in tr_rows:
            use, y = labels_for(r)
            Xs.append(r["x"][r["mask"]][use]); Ys.append(y)
        X, Y = np.vstack(Xs), np.concatenate(Ys)
        mu, sd = standardiser(X)
        head = TinyHead(seed=SEED + fi)
        head.fit((X - mu) / sd, Y, seed=SEED + fi)
        for r in te_rows:
            xm = (r["x"][r["mask"]] - mu) / sd
            r["q"][r["mask"]] = head.forward(xm)
            for name, a, b in spans:
                xp = xm.copy()
                xp[:, a:b] = xp[prng.permutation(xp.shape[0]), a:b]
                r[f"q__{name}"][r["mask"]] = head.forward(xp)

    by = defaultdict(list)
    for r in rows:
        by[r["family"]].append(r)

    out = {}
    for fam, rs in sorted(by.items()):
        base = separation(rs, "q")
        if base is None:
            continue
        row = {"intact_q_separation": round(base, 4), "by_block": {}}
        for name, _, _ in spans:
            s = separation(rs, f"q__{name}")
            if s is None:
                continue
            row["by_block"][name] = {
                "q_separation_with_block_permuted": round(s, 4),
                "separation_lost": round(base - s, 4)}
        ranked = sorted(row["by_block"].items(), key=lambda kv: -kv[1]["separation_lost"])
        row["most_load_bearing_blocks"] = [k for k, _ in ranked[:3]]
        out[fam] = row
        print(fam, json.dumps(row["most_load_bearing_blocks"]), "base", round(base, 4), flush=True)

    payload = {
        "schema": "spectrasynq.learned_restraint_block_importance.v1", "job": "J3Q",
        "label": ("ANALYST-ADDED REPORTED DIAGNOSTIC. NOT GATED - no J3Q outcome depends on this. "
                  "Designed and run AFTER the family metrics were seen."),
        "method": ("block-level permutation importance on OUT-OF-FOLD predictions. For each frozen "
                   "feature block, shuffle that block across rows of the held-out data, recompute q, "
                   "and measure how much the family's q separation collapses. Same folds, same seed, "
                   "same frozen recipe as the J3Q result."),
        "metric": ("q separation = median q at oracle EVENT frames minus median q at STABLE-and-"
                   "C3-high false-movement frames. Higher is better; that is the quantity the head "
                   "exists to produce."),
        "why": ("J3Q fails on synth_lead_pad while the learner separates strongly on bass and piano. "
                "The question that decides the next lane is whether the synth information is ABSENT "
                "from the causal feature set or merely UNUSED by this head."),
        "by_family": out,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"receipt -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
