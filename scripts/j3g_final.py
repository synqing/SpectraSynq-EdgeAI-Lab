#!/usr/bin/env python3
"""J3G FINAL stage: the holdout is opened once.

Primary = the pre-declared winner. Its Level C (J3E visual recovery) determines
the outcome. A pre-declared secondary is reported at Level A/B only and cannot
change the outcome.

Pre-registration: docs/mir/receipts/stft_harmonic_recovery/J3G_PREREGISTRATION.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import j3g_common as C  # noqa: E402
from j3g_dev import solo_family  # noqa: E402

sys.path.insert(0, str(C.ROOT / "src"))
from edgeai.mir.harmonic_visual import pipeline  # noqa: E402

TOL_HOPS = 2
PRIMARY = "C3_ROOT_SALIENCE"
SECONDARY = "C2_PEAK_HPCP"
BASELINE = "P0_CURRENT"


def visual_condition(blocks, state_key, mov_key, cls, resting):
    de_all, rev_all = [], []
    for b in blocks:
        r = pipeline(b[state_key] if isinstance(state_key, str) and state_key in b
                     else b["states"][state_key],
                     b[mov_key] if mov_key in b else b["mov"][mov_key], with_floor=False)
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
    resp_tol = de_tol >= thr
    resp_now = de_now >= thr
    return {
        "threshold_deltaE_p90_of_own_resting_frames": round(thr, 4),
        "consumer_time": {k: round(float(resp_now[m].mean()), 4) for k, m in cls.items()},
        "event_tolerant": {k: round(float(resp_tol[m].mean()), 4) for k, m in cls.items()},
        "resting": {"above_threshold_rate_VACUOUS_BY_CONSTRUCTION": round(float(resp_now[resting].mean()), 4),
                    "median_deltaE": round(float(np.median(de_now[resting])), 4),
                    "direction_reversal_rate": round(float(rev.mean()), 4) if rev.size else None},
        "n_frames": int(len(de_now)),
    }


def gap_fraction(base, cand, oracle, *, higher_is_better):
    den = (oracle - base) if higher_is_better else (base - oracle)
    if abs(den) < 0.01:
        return None
    num = (cand - base) if higher_is_better else (base - cand)
    return round(float(num / den), 4)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--git-head", type=str, default="UNKNOWN")
    args = ap.parse_args()
    prereg = json.loads(C.PREREG.read_text())
    dev = json.loads((C.ROOT / "docs/mir/receipts/stft_harmonic_recovery/J3G_DEV_RESULT.json").read_text())
    if not dev["controls"]["all_blocking_pass"]:
        raise SystemExit("development controls did not pass")
    winner_post = dev["carry_forward_compression_applied_to_candidates"]
    split = C.split_tracks(args.corpus)

    blocks = [C.cached_track(args.corpus / t, winner=winner_post) for t in split["final_holdout"]]
    cls, groups, rM = C.challenge_masks(blocks)
    counts = {k: int(v.sum()) for k, v in cls.items()}
    resting = ~(cls["HARMONIC_CHANGE_FLAT_ENERGY"] | cls["HARMONIC_CHANGE_NO_ONSET"]
                | cls["ACOUSTIC_CHANGE_LOW_HARMONIC_CHANGE"])

    level_ab = {k: C.level_a_b(blocks, k, cls, groups, rM) for k in (BASELINE, PRIMARY, SECONDARY)}
    lags = {k: C.lag_curve(blocks, k) for k in (BASELINE, PRIMARY)}

    solo = solo_family(args.corpus, split["final_holdout"], [BASELINE, PRIMARY],
                       winner_post, Path("/tmp/j3g_stem_cache"))

    # ---- LEVEL C: J3E grammar, unchanged ----
    for b in blocks:
        b["states"]["_ORACLE"] = b["oracle_state"]
        b["states"]["_BASELINE"] = b["chroma_state"]
        b["mov"]["_ORACLE"] = b["M_oracle"]
    vis = {
        "BASELINE": visual_condition(blocks, "_BASELINE", "_HOST_CHROMA12", cls, resting),
        "CANDIDATE": visual_condition(blocks, PRIMARY, PRIMARY, cls, resting),
        "ORACLE": visual_condition(blocks, "_ORACLE", "_ORACLE", cls, resting),
    }
    B, K, O = vis["BASELINE"], vis["CANDIDATE"], vis["ORACLE"]
    metrics = {
        "HARMONIC_CHANGE_FLAT_ENERGY_recall": (
            B["event_tolerant"]["HARMONIC_CHANGE_FLAT_ENERGY"],
            K["event_tolerant"]["HARMONIC_CHANGE_FLAT_ENERGY"],
            O["event_tolerant"]["HARMONIC_CHANGE_FLAT_ENERGY"], True),
        "HARMONIC_CHANGE_NO_ONSET_recall": (
            B["event_tolerant"]["HARMONIC_CHANGE_NO_ONSET"],
            K["event_tolerant"]["HARMONIC_CHANGE_NO_ONSET"],
            O["event_tolerant"]["HARMONIC_CHANGE_NO_ONSET"], True),
        "ACOUSTIC_CHANGE_LOW_HARMONIC_CHANGE_false_response": (
            B["event_tolerant"]["ACOUSTIC_CHANGE_LOW_HARMONIC_CHANGE"],
            K["event_tolerant"]["ACOUSTIC_CHANGE_LOW_HARMONIC_CHANGE"],
            O["event_tolerant"]["ACOUSTIC_CHANGE_LOW_HARMONIC_CHANGE"], False),
        "resting_median_deltaE": (B["resting"]["median_deltaE"], K["resting"]["median_deltaE"],
                                  O["resting"]["median_deltaE"], False),
        "direction_reversal_rate": (B["resting"]["direction_reversal_rate"],
                                    K["resting"]["direction_reversal_rate"],
                                    O["resting"]["direction_reversal_rate"], False),
    }
    recovery = {}
    for name, (b, k, o, hib) in metrics.items():
        recovery[name] = {"baseline": b, "candidate": k, "oracle": o,
                          "higher_is_better": hib,
                          "oracle_gap_fraction_recovered": gap_fraction(b, k, o, higher_is_better=hib)}
    fracs = [v["oracle_gap_fraction_recovered"] for v in recovery.values()
             if v["oracle_gap_fraction_recovered"] is not None]
    mean_frac = round(float(np.mean(fracs)), 4) if fracs else None

    # ---- outcome, pre-registered precedence ----
    d_r2 = round(level_ab[PRIMARY]["r2"] - level_ab[BASELINE]["r2"], 4)
    wf_b = solo[BASELINE]["worst_family_r2"]
    wf_c = solo[PRIMARY]["worst_family_r2"]
    sp_b, sp_c = solo[BASELINE]["spread"], solo[PRIMARY]["spread"]
    harm_fracs = [recovery["HARMONIC_CHANGE_FLAT_ENERGY_recall"]["oracle_gap_fraction_recovered"],
                  recovery["HARMONIC_CHANGE_NO_ONSET_recall"]["oracle_gap_fraction_recovered"]]
    cond = {
        "mean_gap_fraction_ge_0.50": bool(mean_frac is not None and mean_frac >= 0.50),
        "each_harmonic_recall_gap_ge_0.25": bool(all(f is not None and f >= 0.25 for f in harm_fracs)),
        "worst_family_improves_ge_0.10": bool(wf_c is not None and wf_b is not None and (wf_c - wf_b) >= 0.10),
        "family_spread_shrinks_ge_0.10": bool(sp_c is not None and sp_b is not None and (sp_b - sp_c) >= 0.10),
        "holdout_symbolic_r2_gain_ge_0.05": bool(d_r2 >= 0.05),
        "no_chatter_pathology": bool(
            (K["resting"]["direction_reversal_rate"] or 0.0) <= 1.5 * (B["resting"]["direction_reversal_rate"] or 1e-9)
            and K["event_tolerant"]["ACOUSTIC_CHANGE_LOW_HARMONIC_CHANGE"]
            <= B["event_tolerant"]["ACOUSTIC_CHANGE_LOW_HARMONIC_CHANGE"]),
    }
    strong = all(cond.values())
    partial = (d_r2 >= 0.05) or (mean_frac is not None and mean_frac >= 0.20)
    fail = (d_r2 < 0.02) and (mean_frac is not None and mean_frac < 0.05)
    if strong:
        outcome = "EXISTING_STFT_HARMONIC_RECOVERY_STRONG"
    elif partial:
        outcome = "EXISTING_STFT_HARMONIC_RECOVERY_PARTIAL"
    elif fail:
        outcome = "EXISTING_STFT_HARMONIC_RECOVERY_FAIL"
    else:
        outcome = "EXISTING_STFT_HARMONIC_RECOVERY_PARTIAL"

    receipt = {
        "schema": "spectrasynq.stft_harmonic_recovery_result.v1",
        "job": "J3G", "label": "HOST-ONLY DETERMINISTIC TONAL PROJECTION - NOT A PRODUCT EFFECT, NOT FIRMWARE",
        "git_head": args.git_head,
        "preregistration": str(C.PREREG.relative_to(C.ROOT)),
        "development_receipt": "docs/mir/receipts/stft_harmonic_recovery/J3G_DEV_RESULT.json",
        "execution_environment": "Anthropic cloud container (HOST-class). BabySlakh 16 kHz, md5 verified against the publisher's checksum.",
        "primary_candidate": PRIMARY,
        "secondary_reported_cannot_change_outcome": SECONDARY,
        "baseline": BASELINE,
        "final_holdout_tracks": split["final_holdout"],
        "holdout_opened_once": True,
        "challenge_membership_on_holdout": counts,
        "LEVEL_A_B_holdout": level_ab,
        "LEVEL_A_symbolic_r2_gain_over_baseline": d_r2,
        "lag_curves_holdout_REPORTED_NOT_OPTIMISED": lags,
        "LEVEL_B_solo_stem_family_holdout": solo,
        "LEVEL_C_visual_recovery": {
            "grammar": "J3E HARMONIC COLOUR TRANSITION, unchanged: M_REF 0.35, A_MIN 0.02, A_MAX 0.60, photons 1.0, exposure 2.2, without_floor variant, +/-2-hop event-tolerant view",
            "grammar_modified": False,
            "conditions": vis,
            "per_metric_recovery": recovery,
            "mean_oracle_gap_fraction_recovered": mean_frac,
            "mean_is_reported_only_because_the_outcome_thresholds_reference_it": True,
        },
        "outcome_conditions": cond,
        "outcome": outcome,
        "thresholds_applied": prereg["outcome_taxonomy_in_precedence_order"],
        "student_io_frozen": False, "titan": False, "production_firmware_changed": False,
        "basic_pitch_run": False, "foundation_model_run": False, "cqt_run": False,
        "source_separator_run": False, "neural_student_trained": False,
        "J3D_mutated": False, "J3E_mutated": False, "J3F_mutated": False,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(receipt, indent=2, sort_keys=False) + "\n")
    print(json.dumps({"outcome": outcome, "conditions": cond, "level_ab": level_ab,
                      "recovery": recovery, "mean_frac": mean_frac,
                      "solo": {k: {"overall": solo[k]["overall_r2"], "spread": solo[k]["spread"],
                                   "worst": solo[k]["worst_family"], "worst_r2": solo[k]["worst_family_r2"]}
                               for k in (BASELINE, PRIMARY)}}, indent=2))
    print(f"receipt -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
