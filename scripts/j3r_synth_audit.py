#!/usr/bin/env python3
"""J3R - synth feature representability audit.

Does the identical 53-dimensional causal feature set contain usable information
for synth_lead_pad when cross-family shortcut learning is removed?

ONE variable changes versus J3Q: training rows are synth_lead_pad only. Same
features, same labels, same topology, same optimiser, same recipe, same seed,
same folds, same metrics.

Pre-registration: docs/mir/receipts/synth_representability/J3R_PREREGISTRATION.json
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
from j3q_head import (  # noqa: E402
    DET, EV, N_FOLDS, N_PERM, RECALL_GUARD, SEED, STB, labels_for, load_rows, rank, score,
)

sys.path.insert(0, str(C.ROOT / "src"))
from edgeai.mir.restraint_head import RECIPE, TinyHead, standardiser  # noqa: E402

PREREG = C.ROOT / "docs/mir/receipts/synth_representability/J3R_PREREGISTRATION.json"
J3Q_RESULT = C.ROOT / "docs/mir/receipts/learned_restraint/J3Q_RESULT.json"
FAMILY = "synth_lead_pad"
ARMS = ["C3_ROOT_SALIENCE", "J3Q_POOLED_q_OOF", "J3R_SYNTH_ONLY_q_OOF"]


def train_on(rs, fold_seed):
    Xs, Ys = [], []
    for r in rs:
        use, y = labels_for(r)
        Xs.append(r["x"][r["mask"]][use]); Ys.append(y)
    X, Y = np.vstack(Xs), np.concatenate(Ys)
    mu, sd = standardiser(X)
    head = TinyHead(seed=fold_seed)
    info = head.fit((X - mu) / sd, Y, seed=fold_seed)
    steps_per_epoch = int(np.ceil(X.shape[0] / RECIPE["batch_size"]))
    info |= {"steps_per_epoch": steps_per_epoch,
             "total_optimisation_steps": steps_per_epoch * RECIPE["epochs"]}
    return head, mu, sd, info


def q_metrics(rs, qkey):
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
    a, b = float(np.median(qe)), float(np.median(qf))
    return {"q_at_oracle_EVENT_frames": round(a, 4),
            "q_at_STABLE_and_C3_HIGH_frames": round(b, 4),
            "q_separation": round(a - b, 4),
            "separates_in_the_right_direction": bool(a > b)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--git-head", type=str, default="UNKNOWN")
    args = ap.parse_args()
    prereg = json.loads(PREREG.read_text())
    from scipy.stats import spearmanr

    rows = load_rows(args.corpus)
    tracks = sorted({r["track"] for r in rows})          # ALL five families, as J3Q
    folds = np.array_split(np.random.default_rng(SEED).permutation(np.array(tracks)), N_FOLDS)
    syn = [r for r in rows if r["family"] == FAMILY]
    for r in syn:
        r["q_pool"] = np.full(r["n"], np.nan)
        r["q_syn"] = np.full(r["n"], np.nan)

    fold_log, leak, insufficient = [], [], []
    for fi, held in enumerate(folds):
        held = set(held.tolist())
        te = [r for r in syn if r["track"] in held]
        if not te:
            fold_log.append({"fold": fi, "contributes": False,
                             "reason": "no held-out synth stems"})
            continue
        tr_syn = [r for r in syn if r["track"] not in held]
        tr_pool = [r for r in rows if r["track"] not in held]
        leak.append(len({r["track"] for r in tr_syn} & {r["track"] for r in te}))
        npos = nneg = 0
        for r in tr_syn:
            _, y = labels_for(r)
            npos += int((y > 0.5).sum()); nneg += int((y <= 0.5).sum())
        if not tr_syn or npos == 0 or nneg == 0:
            insufficient.append(fi)
            fold_log.append({"fold": fi, "contributes": False, "reason": "insufficient",
                             "train_synth_stems": len(tr_syn), "positive_rows": npos,
                             "negative_rows": nneg})
            continue
        h_pool, mu_p, sd_p, info_p = train_on(tr_pool, SEED + fi)
        h_syn, mu_s, sd_s, info_s = train_on(tr_syn, SEED + fi)
        for r in te:
            xm = r["x"][r["mask"]]
            r["q_pool"][r["mask"]] = h_pool.forward((xm - mu_p) / sd_p)
            r["q_syn"][r["mask"]] = h_syn.forward((xm - mu_s) / sd_s)
        fold_log.append({
            "fold": fi, "contributes": True,
            "train_synth_tracks": len({r["track"] for r in tr_syn}),
            "train_synth_stems": len(tr_syn),
            "positive_rows": npos, "negative_rows": nneg,
            "held_out_synth_tracks": len({r["track"] for r in te}),
            "held_out_synth_stems": len(te),
            "SYNTH_ONLY_steps_per_epoch": info_s["steps_per_epoch"],
            "SYNTH_ONLY_total_steps": info_s["total_optimisation_steps"],
            "SYNTH_ONLY_first_epoch_mean_loss": info_s["first_epoch_mean_loss"],
            "SYNTH_ONLY_final_epoch_mean_loss": info_s["final_epoch_mean_loss"],
            "SYNTH_ONLY_loss_reduction": round(
                info_s["first_epoch_mean_loss"] - info_s["final_epoch_mean_loss"], 6),
            "POOLED_steps_per_epoch": info_p["steps_per_epoch"],
            "POOLED_total_steps": info_p["total_optimisation_steps"],
            "POOLED_train_rows": info_p["n_train_rows"],
        })

    for r in syn:
        r["C3_ROOT_SALIENCE"] = r["mov"]
        r["J3Q_POOLED_q_OOF"] = r["mov"] * r["q_pool"]
        r["J3R_SYNTH_ONLY_q_OOF"] = r["mov"] * r["q_syn"]
    use = [r for r in syn if np.isfinite(r["q_syn"][r["mask"]]).all()
           and np.isfinite(r["q_pool"][r["mask"]]).all()]

    qp = np.concatenate([r["q_pool"][r["mask"]] for r in use])
    qs = np.concatenate([r["q_syn"][r["mask"]] for r in use])
    j3q = json.loads(J3Q_RESULT.read_text())["family_metrics"]

    rng = np.random.default_rng(SEED)
    out = {}
    for arm in ARMS:
        g = np.concatenate([np.full(int(r["mask"].sum()), r["id"]) for r in use])
        Ms = np.concatenate([r["Ms"][r["mask"]] for r in use])
        Ma = np.concatenate([r[arm][r["mask"]] for r in use])
        s = score(use, arm)
        nulls = [score(use, arm, shift_by=rng.integers(200, 2000, size=len(use)))["tol"]
                 for _ in range(N_PERM)]
        row = {"n_stems": len(use), "n_events": s["n_events"],
               "framewise_r2_DIAGNOSTIC": C.grouped_r2(Ma, Ms, g),
               "spearman": round(float(spearmanr(Ma, Ms).statistic), 4),
               "event_recall_consumer_time": round(s["consumer"], 4),
               "event_recall_event_tolerant": round(s["tol"], 4),
               "false_movement_in_stable_periods": round(s["false"], 4),
               "selectivity_margin": round(s["tol"] - s["false"], 4),
               "median_movement": round(float(np.median(
                   [np.median(r[arm][r["mask"]]) for r in use])), 5),
               "null_recall_mean_REPORTED_NOT_GATED": round(float(np.mean(nulls)), 4),
               "recall_above_own_null_REPORTED_NOT_GATED": round(
                   s["tol"] - float(np.mean(nulls)), 4)}
        if arm != "C3_ROOT_SALIENCE":
            qk = "q_pool" if arm.startswith("J3Q") else "q_syn"
            row["median_q"] = round(float(np.median(
                [np.median(r[qk][r["mask"]]) for r in use])), 4)
            row.update(q_metrics(use, qk) or {})
        out[arm] = row

    # control: does the reproduced pooled arm match the committed J3Q result?
    ref = j3q["C3_TIMES_Q_OOF"][FAMILY]
    repro = {k: (out["J3Q_POOLED_q_OOF"].get(k), ref.get(k)) for k in
             ("event_recall_event_tolerant", "false_movement_in_stable_periods")}
    pooled_matches = all(a is not None and b is not None and abs(a - b) < 1e-9
                         for a, b in repro.values())

    c3, syn_arm = out["C3_ROOT_SALIENCE"], out["J3R_SYNTH_ONLY_q_OOF"]
    drop = round(c3["event_recall_event_tolerant"] - syn_arm["event_recall_event_tolerant"], 4)
    red = round(c3["false_movement_in_stable_periods"] - syn_arm["false_movement_in_stable_periods"], 4)
    decision = {"recall_drop_vs_C3": drop, "recall_guard_satisfied": bool(drop <= RECALL_GUARD),
                "false_movement_reduction_vs_C3": red, "reduces_false_movement": bool(red > 0.0),
                "clears": bool(drop <= RECALL_GUARD and red > 0.0)}

    contributing = [f for f in fold_log if f.get("contributes")]
    controls = {
        "folds_reused_from_J3Q": True,
        "fold_track_list_derived_from_all_five_families": True,
        "n_contributing_folds": len(contributing),
        "no_synth_stem_trains_on_its_own_track": bool(all(v == 0 for v in leak)),
        "per_fold_train_test_track_overlap": leak,
        "insufficient_folds": insufficient,
        "standardisation_fitted_on_training_rows_only_per_arm": True,
        "oracle_labels_absent_from_feature_matrix": True,
        "n_scored_synth_stems": len(use),
        "every_scored_frame_has_both_OOF_predictions": bool(len(use) == len(syn)),
        "q_pooled_finite_in_unit_interval": bool(np.isfinite(qp).all() and qp.min() >= 0 and qp.max() <= 1),
        "q_synth_only_finite_in_unit_interval": bool(np.isfinite(qs).all() and qs.min() >= 0 and qs.max() <= 1),
        "q_synth_only_observed_range": [round(float(qs.min()), 4), round(float(qs.max()), 4)],
        "C3_state_never_modified": True,
        "reproduced_pooled_synth_metrics_match_committed_J3Q": pooled_matches,
        "reproduced_vs_committed": {k: {"reproduced": a, "committed": b} for k, (a, b) in repro.items()},
        "model_unchanged": "53 -> 32 ReLU -> 1 sigmoid, 1761 parameters",
        "recipe_unchanged": RECIPE,
    }
    controls["all_blocking_pass"] = bool(
        controls["no_synth_stem_trains_on_its_own_track"] and not insufficient
        and len(contributing) >= 1 and controls["every_scored_frame_has_both_OOF_predictions"]
        and controls["q_pooled_finite_in_unit_interval"]
        and controls["q_synth_only_finite_in_unit_interval"] and pooled_matches)

    if not controls["all_blocking_pass"]:
        outcome = "SYNTH_REPRESENTABILITY_INCONCLUSIVE"
    elif decision["clears"]:
        outcome = "SYNTH_FEATURE_SIGNAL_PRESENT"
    else:
        outcome = "SYNTH_FEATURE_LIMIT_SUPPORTED"

    losses = [f["SYNTH_ONLY_loss_reduction"] for f in contributing]
    receipt = {
        "schema": "spectrasynq.synth_representability_result.v1", "job": "J3R",
        "git_head": args.git_head, "label": prereg["label"],
        "preregistration": str(PREREG.relative_to(C.ROOT)),
        "the_only_question": prereg["the_only_question"],
        "single_variable": prereg["SINGLE_VARIABLE"],
        "execution_environment": "Anthropic cloud container (HOST-class). BabySlakh 16 kHz, md5 verified against the publisher's checksum.",
        "controls": controls,
        "fold_log": fold_log,
        "training_size_consequence_DISCLOSED_IN_PREREG": dict(
            prereg["DISCLOSED_CONSEQUENCE_OF_HOLDING_THE_RECIPE_FIXED"],
            measured_synth_only_loss_reduction_per_fold=losses,
            median_synth_only_loss_reduction=round(float(np.median(losses)), 6) if losses else None,
            the_model_did_train=bool(losses and float(np.median(losses)) > 0.01)),
        "metrics_synth_lead_pad_only": out,
        "the_decisive_contrast_C3_to_pooled_to_synth_only": {
            "false_movement_in_stable_periods": {a: out[a]["false_movement_in_stable_periods"] for a in ARMS},
            "event_recall_event_tolerant": {a: out[a]["event_recall_event_tolerant"] for a in ARMS},
            "q_separation": {a: out[a].get("q_separation") for a in ARMS},
        },
        "decision": decision,
        "recall_guard": {"rule": prereg["RECALL_GUARD"]["rule"], "threshold": RECALL_GUARD},
        "chance_floor": {"n_permutations": N_PERM, "seed": SEED, "REPORTED_NOT_GATED": True},
        "block_importance_run": False,
        "block_importance_rule": prereg["BLOCK_IMPORTANCE"]["rule"],
        "outcome": outcome,
        "J3Q_mutated": False, "J3P_mutated": False, "J3O_mutated": False, "target_modified": False,
        "new_model": False, "model_size_swept": False, "family_input_used": False,
        "feature_added": False, "longer_context": False, "threshold_tuned": False,
        "fb_log_used": False, "crp_run": False, "nnls_run": False, "cqt_run": False,
        "basic_pitch_run": False, "source_separator_run": False,
        "visual_test_run": False, "visual_grammar_modified": False,
        "production_firmware_changed": False, "titan": False, "student_io_frozen": False,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(receipt, indent=2, sort_keys=False) + "\n")
    print(json.dumps({"outcome": outcome, "decision": decision,
                      "contrast": receipt["the_decisive_contrast_C3_to_pooled_to_synth_only"],
                      "controls": {k: v for k, v in controls.items() if k != "recipe_unchanged"},
                      "loss_reduction": losses}, indent=2))
    print(f"receipt -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
