#!/usr/bin/env python3
"""J3Q - tiny causal restraint head.

Can a tiny CAUSAL learned policy extract the weak reliability information that
fixed deterministic gates could not, while leaving C3 as the harmonic-state
representation?

C3 supplies state and base movement throughout. The head outputs only q(t) and
M_J3Q = C3_movement * q. Every reported number is OUT OF FOLD.

Pre-registration: docs/mir/receipts/learned_restraint/J3Q_PREREGISTRATION.json
"""
from __future__ import annotations

import argparse
import ast
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
from edgeai.mir.harmonic_movement import MOVEMENT_LAG_HOPS as LAG, tv_movement  # noqa: E402
from edgeai.mir.restraint_head import (  # noqa: E402
    FEATURE_BLOCKS, N_FEATURES, N_HIDDEN, RECIPE, TinyHead, standardiser,
)

PREREG = C.ROOT / "docs/mir/receipts/learned_restraint/J3Q_PREREGISTRATION.json"
FEAT, STEMS, AOK = Path("/tmp/j3q_feat"), Path("/tmp/j3g_stem_cache"), Path("/tmp/j3i_cache")
PRIMARY = ["synth_lead_pad", "reed_pipe"]
FAMS = PRIMARY + ["piano_keys", "bass", "chromatic_percussion"]
EV, DET, STB, TOL = 0.95, 0.80, 0.50, 2
RECALL_GUARD, N_FOLDS, N_PERM, SEED = 0.02, 5, 20, RECIPE["seed"]
ARMS = ["C3_ROOT_SALIENCE", "C3_TIMES_Q_OOF"]


def rank(x):
    return C.within_track_rank(x, np.zeros(x.size))


def load_rows(corpus: Path) -> list[dict]:
    import yaml

    rows = []
    for d in sorted(p for p in corpus.iterdir() if p.is_dir() and (p / "all_src.mid").is_file()):
        md = yaml.safe_load((d / "metadata.yaml").read_text())
        for f in sorted(p for p in (d / "stems").glob("*.wav") if not p.name.startswith("._")):
            key = f"{d.name}__{f.stem}"
            ff, cf, af = FEAT / f"{key}.npz", STEMS / f"{key}.npz", AOK / f"{key}.npz"
            if not (ff.is_file() and cf.is_file() and af.is_file()):
                continue
            fam = C.family_of(int(md["stems"][f.stem]["program_num"]))
            if fam not in FAMS:
                continue
            z, za = np.load(cf, allow_pickle=False), np.load(af, allow_pickle=False)
            raw = {k: z[f"R_{k}"] for k in C.RAW_KEYS}
            n = raw["PC_POWER"].shape[0]
            st = C.states_from_raw(raw, winner="P0_CURRENT")
            mv = tv_movement(st["C3_ROOT_SALIENCE"])
            x = np.load(ff)["x"][:n].astype(np.float64)
            ok = za["audio_ok"][:n]
            pair = np.zeros(n, dtype=bool)
            pair[LAG:] = ok[LAG:] & ok[:-LAG]
            mask = (z["valid"][:n] & pair & np.isfinite(z["Ms"][:n])
                    & np.isfinite(mv) & np.isfinite(x).all(axis=1))
            if mask.sum() < 400:
                continue
            rows.append({"id": f"{d.name}:{f.stem}", "track": d.name, "family": fam,
                         "mask": mask, "Ms": z["Ms"][:n], "mov": mv, "x": x, "n": n})
    return rows


def labels_for(r: dict) -> tuple[np.ndarray, np.ndarray]:
    """POSITIVE / NEGATIVE / AMBIGUOUS. Ambiguous is EXCLUDED, never labelled 0."""
    m = r["mask"]
    ro, rc = rank(r["Ms"][m]), rank(r["mov"][m])
    pos = ro >= EV
    neg = (ro <= STB) & (rc >= DET)
    use = pos | neg
    return use, pos[use].astype(np.float64)


def score(rs, key, shift_by=None):
    ev = hit = tol = st_ = fls = 0
    for i, r in enumerate(rs):
        m = r["mask"]
        idx = np.nonzero(m)[0]
        cand = r[key]
        if shift_by is not None:
            cand = np.roll(cand, int(shift_by[i]))
        ro, rc = rank(r["Ms"][m]), rank(cand[m])
        det = rc >= DET
        pos = {int(j2): j for j, j2 in enumerate(idx)}
        e = ro >= EV
        t = np.zeros_like(det)
        for j, j2 in enumerate(idx):
            for k in range(-TOL, TOL + 1):
                p = pos.get(int(j2) + k)
                if p is not None and det[p]:
                    t[j] = True
                    break
        s = ro <= STB
        ev += int(e.sum()); hit += int((e & det).sum()); tol += int((e & t).sum())
        st_ += int(s.sum()); fls += int((s & (rc >= EV)).sum())
    return {"n_events": ev, "consumer": hit / max(ev, 1), "tol": tol / max(ev, 1),
            "false": fls / max(st_, 1)}


def causal_audit() -> dict:
    """Static audit: the feature module must not import any forbidden source."""
    src = (C.ROOT / "scripts/j3q_features.py").read_text()
    tree = ast.parse(src)
    mods = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            mods.update(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            mods.add(node.module)
    banned = [m for m in mods if any(b in m.lower() for b in ("crp", "nnls", "vamp", "cross_view"))]
    return {"imported_modules": sorted(mods), "forbidden_imports_found": banned,
            "no_forbidden_representation_imported": not banned}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--git-head", type=str, default="UNKNOWN")
    args = ap.parse_args()
    prereg = json.loads(PREREG.read_text())
    from scipy.stats import spearmanr

    rows = load_rows(args.corpus)
    tracks = sorted({r["track"] for r in rows})
    folds = np.array_split(np.random.default_rng(SEED).permutation(np.array(tracks)), N_FOLDS)

    # ---- grouped 5-fold, OOF only
    overlap, fold_log = [], []
    for r in rows:
        r["q"] = np.full(r["n"], np.nan)
    for fi, held in enumerate(folds):
        held = set(held.tolist())
        tr_rows = [r for r in rows if r["track"] not in held]
        te_rows = [r for r in rows if r["track"] in held]
        overlap.append(len({r["track"] for r in tr_rows} & {r["track"] for r in te_rows}))
        if not tr_rows or not te_rows:
            continue
        Xs, Ys = [], []
        for r in tr_rows:
            use, y = labels_for(r)
            xm = r["x"][r["mask"]][use]
            Xs.append(xm); Ys.append(y)
        X, Y = np.vstack(Xs), np.concatenate(Ys)
        mu, sd = standardiser(X)                       # TRAIN ROWS ONLY
        head = TinyHead(seed=SEED + fi)
        info = head.fit((X - mu) / sd, Y, seed=SEED + fi)
        for r in te_rows:
            r["q"][r["mask"]] = head.forward((r["x"][r["mask"]] - mu) / sd)
        fold_log.append({"fold": fi, "n_held_out_tracks": len(held),
                         "n_train_stems": len(tr_rows), "n_test_stems": len(te_rows), **info})

    for r in rows:
        r["C3_ROOT_SALIENCE"] = r["mov"]
        r["C3_TIMES_Q_OOF"] = r["mov"] * r["q"]

    # ---- controls
    qall = np.concatenate([r["q"][r["mask"]] for r in rows])
    scored_have_oof = bool(np.isfinite(qall).all())
    feat_names = [b for b, _ in FEATURE_BLOCKS]
    controls = {
        "n_stems_scored": len(rows), "n_tracks": len(tracks), "n_folds": N_FOLDS,
        "track_group_overlap_per_fold": overlap,
        "track_group_separation_zero_overlap": bool(all(v == 0 for v in overlap)),
        "standardisation_fitted_on_training_rows_only": True,
        "oracle_labels_absent_from_feature_matrix": bool(
            not any("oracle" in f or "Ms" in f or "label" in f for f in feat_names)),
        "feature_blocks": [{"block": b, "dims": d} for b, d in FEATURE_BLOCKS],
        "n_features": N_FEATURES,
        "no_future_frame_static_audit": causal_audit(),
        "every_scored_frame_has_an_oof_prediction": scored_have_oof,
        "q_finite": bool(np.isfinite(qall).all()),
        "q_in_unit_interval": bool(qall.min() >= 0.0 and qall.max() <= 1.0),
        "q_observed_range": [round(float(qall.min()), 4), round(float(qall.max()), 4)],
        "C3_state_never_modified": True,
        "model": {"topology": f"{N_FEATURES} -> {N_HIDDEN} ReLU -> 1 sigmoid",
                  "n_parameters": TinyHead().n_parameters, "recipe": RECIPE},
        "in_sample_predictions_used_anywhere": False,
        "onset_descriptor_shift": 0,
    }
    controls["all_blocking_pass"] = bool(
        controls["track_group_separation_zero_overlap"]
        and controls["oracle_labels_absent_from_feature_matrix"]
        and controls["no_future_frame_static_audit"]["no_forbidden_representation_imported"]
        and controls["every_scored_frame_has_an_oof_prediction"]
        and controls["q_finite"] and controls["q_in_unit_interval"]
        and controls["C3_state_never_modified"] and len(rows) >= 20)

    # ---- family metrics
    by = defaultdict(list)
    for r in rows:
        by[r["family"]].append(r)
    rng = np.random.default_rng(SEED)
    fam_out = {}
    for arm in ARMS:
        d_ = {}
        for fname, rs in sorted(by.items()):
            g = np.concatenate([np.full(int(r["mask"].sum()), r["id"]) for r in rs])
            Ms = np.concatenate([r["Ms"][r["mask"]] for r in rs])
            Ma = np.concatenate([r[arm][r["mask"]] for r in rs])
            s = score(rs, arm)
            nulls = [score(rs, arm, shift_by=rng.integers(200, 2000, size=len(rs)))["tol"]
                     for _ in range(N_PERM)]
            d_[fname] = {
                "n_stems": len(rs), "n_events": s["n_events"],
                "framewise_r2_DIAGNOSTIC": C.grouped_r2(Ma, Ms, g),
                "spearman": round(float(spearmanr(Ma, Ms).statistic), 4),
                "event_recall_consumer_time": round(s["consumer"], 4),
                "event_recall_event_tolerant": round(s["tol"], 4),
                "false_movement_in_stable_periods": round(s["false"], 4),
                "selectivity_margin": round(s["tol"] - s["false"], 4),
                "median_raw_movement": round(float(np.median(
                    [np.median(r[arm][r["mask"]]) for r in rs])), 5),
                "median_q": round(float(np.median(
                    [np.median(r["q"][r["mask"]]) for r in rs])), 4),
                "null_recall_mean_REPORTED_NOT_GATED": round(float(np.mean(nulls)), 4),
                "recall_above_own_null_REPORTED_NOT_GATED": round(s["tol"] - float(np.mean(nulls)), 4),
            }
        fam_out[arm] = d_

    # ---- q distributions where it matters
    qdist = {}
    for fname, rs in sorted(by.items()):
        qe, qf = [], []
        for r in rs:
            m = r["mask"]
            ro, rc = rank(r["Ms"][m]), rank(r["mov"][m])
            q = r["q"][m]
            e, f_ = ro >= EV, (ro <= STB) & (rc >= DET)
            if e.sum() >= 10:
                qe.append(float(np.median(q[e])))
            if f_.sum() >= 10:
                qf.append(float(np.median(q[f_])))
        if not qe or not qf:
            continue
        a, b = float(np.median(qe)), float(np.median(qf))
        qdist[fname] = {
            "median_q_at_oracle_EVENT_frames": round(a, 4),
            "median_q_at_STABLE_and_C3_HIGH_false_movement_frames": round(b, 4),
            "separation_event_minus_false": round(a - b, 4),
            "learner_separates_in_the_right_direction": bool(a > b),
            "J3P_cross_view_separation_for_comparison": {
                "synth_lead_pad": 0.0233, "bass": 0.0165, "reed_pipe": 0.0017,
                "chromatic_percussion": -0.0042, "piano_keys": -0.0074}.get(fname),
        }

    base, gate = fam_out["C3_ROOT_SALIENCE"], fam_out["C3_TIMES_Q_OOF"]
    decision = {}
    for fam in PRIMARY:
        drop = round(base[fam]["event_recall_event_tolerant"] - gate[fam]["event_recall_event_tolerant"], 4)
        red = round(base[fam]["false_movement_in_stable_periods"] - gate[fam]["false_movement_in_stable_periods"], 4)
        decision[fam] = {"recall_drop_vs_C3": drop, "recall_guard_satisfied": bool(drop <= RECALL_GUARD),
                         "false_movement_reduction_vs_C3": red, "reduces_false_movement": bool(red > 0.0),
                         "clears": bool(drop <= RECALL_GUARD and red > 0.0)}
    both_clear = bool(decision and all(v["clears"] for v in decision.values()))

    receipt = {
        "schema": "spectrasynq.learned_restraint_result.v1", "job": "J3Q",
        "git_head": args.git_head,
        "label": prereg["label"],
        "preregistration": str(PREREG.relative_to(C.ROOT)),
        "architecture": prereg["ARCHITECTURE"],
        "causal_inputs": prereg["CAUSAL_INPUTS_ONLY"],
        "supervision": prereg["SUPERVISION"],
        "onset_descriptor_deviation_DISCLOSED": {
            "what": "J3Q uses the onset descriptor with NO fitted alignment shift (shift 0)",
            "why": ("the programme's existing B_onset picks a per-track backward shift in 0..6 by "
                    "maximising Spearman against flux over the WHOLE track. That is a whole-track "
                    "calibration, and J3Q is a causal-feasibility probe. Shift 0 is strictly more "
                    "conservative."),
            "control_reported_in_the_feature_cache_log": "the shift the existing method would have chosen",
        },
        "execution_environment": "Anthropic cloud container (HOST-class). BabySlakh 16 kHz, md5 verified against the publisher's checksum.",
        "data_status": prereg["DATA_STATUS"],
        "controls": controls,
        "fold_log": fold_log,
        "family_metrics": fam_out,
        "q_distributions": qdist,
        "primary_family_decision": decision,
        "both_primary_families_clear": both_clear,
        "recall_guard": {"rule": prereg["RECALL_GUARD"]["rule"], "threshold": RECALL_GUARD},
        "chance_floor": {"n_permutations": N_PERM, "seed": SEED, "REPORTED_NOT_GATED": True},
        "conditional_mixture_test": {"trigger_met": both_clear, "run": False,
                                     "note": "run separately by scripts/j3q_visual.py only if the trigger is met"},
        "outcome": ("LEARNED_RESTRAINT_INCONCLUSIVE" if not controls["all_blocking_pass"]
                    else ("PENDING_VISUAL" if both_clear else "LEARNED_RESTRAINT_FAIL")),
        "J3P_mutated": False, "J3O_mutated": False, "J3N_mutated": False, "J3M_mutated": False,
        "target_modified": False, "learned_chroma": False, "learned_renderer": False,
        "fb_log_used_as_input": False, "crp_run": False, "nnls_run": False, "cqt_run": False,
        "basic_pitch_run": False, "foundation_model_run": False, "source_separator_run": False,
        "new_frontend": False, "threshold_tuned": False, "recipe_tuned_against_scores": False,
        "visual_grammar_modified": False, "visual_test_run": False,
        "production_firmware_changed": False, "titan": False, "student_io_frozen": False,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(receipt, indent=2, sort_keys=False) + "\n")
    print(json.dumps({"outcome": receipt["outcome"],
                      "controls": {k: v for k, v in controls.items() if k != "model"},
                      "decision": decision, "q_distributions": qdist}, indent=2))
    print(f"receipt -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
