#!/usr/bin/env python3
"""J3O REPORTED DIAGNOSTIC - chance floor for the event-tolerant recall metric.

Event-tolerant recall gives every oracle event five chances (+/- 2 hops) to be
matched by a frame in the candidate's top 20 percent, so it has a substantial
chance floor. This measures that floor per family per arm by circularly shifting
each stem's candidate movement series, which destroys the true temporal
correspondence while preserving the series' own distribution and autocorrelation.

REPORTED, NOT GATED. No outcome depends on this.
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

sys.path.insert(0, str(C.ROOT / "src"))
from edgeai.mir import crp as K  # noqa: E402
from edgeai.mir.harmonic_movement import MOVEMENT_LAG_HOPS as LAG, tv_movement  # noqa: E402

sys.path.insert(0, str(C.ROOT / "scripts"))
from j3o_nnls_probe import ARMS, EV, DET, FAMS, STB, TOL, nnls_state  # noqa: E402

NNLSC, STEMS, AOK, PITCH = (Path("/tmp/j3o_cache"), Path("/tmp/j3g_stem_cache"),
                            Path("/tmp/j3i_cache"), Path("/tmp/j3n_pitch"))
N_PERM = 20
RNG = np.random.default_rng(20260902)


def rank(x):
    return C.within_track_rank(x, np.zeros(x.size))


def score(rs, arm, shift_by=None):
    ev = tol = st_ = fls = 0
    for i, r in enumerate(rs):
        m = r["mask"]
        idx = np.nonzero(m)[0]
        cand = r["mov"][arm]
        if shift_by is not None:
            cand = np.roll(cand, int(shift_by[i]))
        rs_, rc = rank(r["Ms"][m]), rank(cand[m])
        det = rc >= DET
        pos = {int(i2): j for j, i2 in enumerate(idx)}
        e = rs_ >= EV
        t = np.zeros_like(det)
        for j, i2 in enumerate(idx):
            for k in range(-TOL, TOL + 1):
                q = pos.get(int(i2) + k)
                if q is not None and det[q]:
                    t[j] = True
                    break
        s = rs_ <= STB
        ev += int(e.sum()); tol += int((e & t).sum())
        st_ += int(s.sum()); fls += int((s & (rc >= EV)).sum())
    return tol / max(ev, 1), fls / max(st_, 1)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    import yaml

    rows = []
    for d in sorted(p for p in args.corpus.iterdir() if p.is_dir() and (p / "all_src.mid").is_file()):
        md = yaml.safe_load((d / "metadata.yaml").read_text())
        for f in sorted(p for p in (d / "stems").glob("*.wav") if not p.name.startswith("._")):
            key = f"{d.name}__{f.stem}"
            nf, cf, af, pf = NNLSC / f"{key}.npz", STEMS / f"{key}.npz", AOK / f"{key}.npz", PITCH / f"{key}.npz"
            if not (nf.is_file() and cf.is_file() and af.is_file()):
                continue
            fam = C.family_of(int(md["stems"][f.stem]["program_num"]))
            if fam not in FAMS:
                continue
            z, za = np.load(cf, allow_pickle=False), np.load(af, allow_pickle=False)
            raw = {k: z[f"R_{k}"] for k in C.RAW_KEYS}
            n = raw["PC_POWER"].shape[0]
            st = C.states_from_raw(raw, winner="P0_CURRENT")
            mov = {"P0_CURRENT": tv_movement(st["P0_CURRENT"]),
                   "C3_ROOT_SALIENCE": tv_movement(st["C3_ROOT_SALIENCE"])}
            if pf.is_file():
                lg = K.log_pitch(np.load(pf)["pitch"][:n].astype(np.float64))
                mov["FB_LOG_CHROMA"] = tv_movement(K.fb_log_chroma_from_log(lg))
            else:
                mov["FB_LOG_CHROMA"] = np.full(n, np.nan)
            for a in ("NNLS_FRONTEND_ONLY", "NNLS_NOTES", "NNLS_PUBLISHED_CHROMA"):
                mov[a] = tv_movement(nnls_state(nf, a, n))
            ok = za["audio_ok"][:n]
            pair = np.zeros(n, dtype=bool)
            pair[LAG:] = ok[LAG:] & ok[:-LAG]
            m_core = (z["valid"][:n] & pair & np.isfinite(z["Ms"][:n])
                      & np.all([np.isfinite(mov[a][:n]) for a in ARMS if a != "FB_LOG_CHROMA"], axis=0))
            if m_core.sum() < 400:
                continue
            for a in ARMS:
                mov[a] = np.nan_to_num(mov[a][:n], nan=0.0)
            rows.append({"family": fam, "mask": m_core, "Ms": z["Ms"][:n], "mov": mov})

    by = defaultdict(list)
    for r in rows:
        by[r["family"]].append(r)

    out = {}
    for fam, rs in sorted(by.items()):
        out[fam] = {}
        for arm in ARMS:
            use = [r for r in rs if np.isfinite(r["mov"][arm][r["mask"]]).all()
                   and np.ptp(r["mov"][arm][r["mask"]]) > 0]
            if len(use) < 3:
                continue
            obs_r, obs_f = score(use, arm)
            nr, nf_ = [], []
            for _ in range(N_PERM):
                shifts = RNG.integers(200, 2000, size=len(use))
                a, b = score(use, arm, shift_by=shifts)
                nr.append(a); nf_.append(b)
            out[fam][arm] = {
                "observed_event_tolerant_recall": round(obs_r, 4),
                "null_recall_mean": round(float(np.mean(nr)), 4),
                "null_recall_p95": round(float(np.percentile(nr, 95)), 4),
                "recall_above_null_mean": round(obs_r - float(np.mean(nr)), 4),
                "observed_false_movement": round(obs_f, 4),
                "null_false_movement_mean": round(float(np.mean(nf_)), 4),
                "false_movement_below_null_mean": round(float(np.mean(nf_)) - obs_f, 4),
            }
        print(fam, json.dumps(out[fam], indent=None)[:200], flush=True)

    payload = {
        "schema": "spectrasynq.nnls_null_diagnostic.v1", "job": "J3O",
        "label": "REPORTED DIAGNOSTIC. Chance floor of the event-tolerant recall metric. NOT GATED - no J3O outcome depends on this.",
        "method": ("per stem, circularly shift the candidate movement series by a random offset in "
                   "[200, 2000] hops, destroying temporal correspondence with the oracle while "
                   "preserving the series' own distribution and autocorrelation; recompute the "
                   "identical metric. 20 permutations, seed 20260902."),
        "why": ("event-tolerant recall matches an oracle event if ANY of 5 frames (+/- 2 hops) is in "
                "the candidate's top 20 percent by within-stem rank. That has a high chance floor, so "
                "absolute recall figures in weak families must not be read as 'this fraction of events "
                "was recovered'. The floor is identical across arms, so ARM COMPARISONS remain valid."),
        "n_permutations": N_PERM,
        "by_family": out,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"receipt -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
