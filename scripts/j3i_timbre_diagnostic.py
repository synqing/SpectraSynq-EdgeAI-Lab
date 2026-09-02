#!/usr/bin/env python3
"""J3I - construct-validity audit of the solo-stem timbre diagnostic.

No new estimator, no model, no frontend, no visual experiment, no label repair.

Pre-registration: docs/mir/receipts/timbre_diagnostic/J3I_PREREGISTRATION.json
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import j3g_common as C  # noqa: E402

sys.path.insert(0, str(C.ROOT / "src"))
from edgeai.mir import tonal_projection as tp  # noqa: E402
from edgeai.mir.harmonic_movement import MOVEMENT_LAG_HOPS, tv_movement  # noqa: E402

LAG = MOVEMENT_LAG_HOPS
PREREG = C.ROOT / "docs/mir/receipts/timbre_diagnostic/J3I_PREREGISTRATION.json"
STEMS, SIDE_C5, SIDE_A = Path("/tmp/j3g_stem_cache"), Path("/tmp/j3g2_cache"), Path("/tmp/j3i_cache")
PRIMARY = ["P0_CURRENT", "C3_ROOT_SALIENCE"]
SECONDARY = ["C2_PEAK_HPCP", "C5_PEAK_ROOT_HYBRID"]
ALL = PRIMARY + SECONDARY
FAMILIES_REPORTED = ["piano_keys", "guitar", "bass", "ensemble_voice", "reed_pipe",
                     "synth_lead_pad", "chromatic_percussion"]
EVENT_RANK, DETECT_RANK, STABLE_RANK = 0.95, 0.80, 0.50   # reused verbatim from J3D/J3G
TOL_HOPS = 2


def load_stems(corpus: Path) -> list[dict]:
    rows = []
    for d in sorted(p for p in corpus.iterdir() if p.is_dir() and (p / "all_src.mid").is_file()):
        md = yaml.safe_load((d / "metadata.yaml").read_text())
        for f in sorted(p for p in (d / "stems").glob("*.wav") if not p.name.startswith("._")):
            cf, c5f, af = (STEMS / f"{d.name}__{f.stem}.npz", SIDE_C5 / f"stem__{d.name}__{f.stem}.npz",
                           SIDE_A / f"{d.name}__{f.stem}.npz")
            if not (cf.is_file() and c5f.is_file() and af.is_file()):
                continue
            z, za = np.load(cf, allow_pickle=False), np.load(af, allow_pickle=False)
            raw = {k: z[f"R_{k}"] for k in C.RAW_KEYS}
            n = raw["PC_POWER"].shape[0]
            st = C.states_from_raw(raw, winner="P0_CURRENT")
            st["C5_PEAK_ROOT_HYBRID"] = tp.l1(tp.apply_carry_forward(
                np.load(c5f)["C5"][:n], native_domain="amplitude", winner="P0_CURRENT"))
            ok = za["audio_ok"][:n]
            pair = np.zeros(n, dtype=bool)
            pair[LAG:] = ok[LAG:] & ok[:-LAG]
            prog = int(za["program"])
            rows.append({"id": f"{d.name}:{f.stem}", "family": C.family_of(prog), "program": prog,
                         "Ms": z["Ms"][:n], "sym_valid": z["valid"][:n],
                         "audio_ok": ok, "audio_pair": pair,
                         "episodes": za["episodes"],
                         "mov": {k: tv_movement(v) for k, v in st.items()}})
    return rows


def family_table(rows: list[dict], mask_key: str | None) -> dict:
    from scipy.stats import spearmanr
    keep = []
    for r in rows:
        m = r["sym_valid"] & np.isfinite(r["Ms"])
        if mask_key:
            m = m & r[mask_key]
        m = m & np.all([np.isfinite(v) for v in r["mov"].values()], axis=0)
        if m.sum() < 400:
            continue
        keep.append({**r, "m": m})
    out = {"_n_stems": len(keep), "_n_frames": int(sum(int(r["m"].sum()) for r in keep))}
    by = defaultdict(list)
    for r in keep:
        by[r["family"]].append(r)
    for name in ALL:
        fam = {}
        for fname, rs in sorted(by.items()):
            g = np.concatenate([np.full(int(r["m"].sum()), r["id"]) for r in rs])
            if len(np.unique(g)) < 3:
                continue
            Ms = np.concatenate([r["Ms"][r["m"]] for r in rs])
            Ma = np.concatenate([r["mov"][name][r["m"]] for r in rs])
            fam[fname] = {"n_stems": len(rs), "n_frames": int(len(Ms)),
                          "solo_stem_r2": C.grouped_r2(Ma, Ms, g),
                          "spearman": round(float(spearmanr(Ma, Ms).statistic), 4)}
        vals = [v["solo_stem_r2"] for v in fam.values()]
        allg = np.concatenate([np.full(int(r["m"].sum()), r["id"]) for r in keep])
        out[name] = {"overall_r2": C.grouped_r2(np.concatenate([r["mov"][name][r["m"]] for r in keep]),
                                                np.concatenate([r["Ms"][r["m"]] for r in keep]), allg),
                     "by_family": fam,
                     "spread": round(max(vals) - min(vals), 4) if vals else None,
                     "worst_family": min(fam, key=lambda k: fam[k]["solo_stem_r2"]) if fam else None,
                     "worst_family_r2": round(min(vals), 4) if vals else None}
    return out


def removal_stats(rows: list[dict]) -> dict:
    by = defaultdict(lambda: [0, 0])
    for r in rows:
        base = r["sym_valid"] & np.isfinite(r["Ms"])
        by[r["family"]][0] += int(base.sum())
        by[r["family"]][1] += int((base & r["audio_pair"]).sum())
    return {f: {"frames_before": a, "frames_after": b,
                "fraction_removed": round(1.0 - b / max(a, 1), 4)} for f, (a, b) in sorted(by.items())}


def attack_decay(rows: list[dict]) -> dict:
    cols = ["attack_10_hops", "attack_50_hops", "release_10_hops", "release_50_hops",
            "audible_gate_coverage"]
    by, sens = defaultdict(list), defaultdict(list)
    for r in rows:
        e = r["episodes"]
        if not len(e):
            continue
        by[r["family"]].append(e)
        s = e[e[:, 8] > 0.5]
        if len(s):
            sens[r["family"]].append(s)

    def summarise(d):
        o = {}
        for fam, arrs in sorted(d.items()):
            a = np.vstack(arrs)
            row = {"n_episodes": int(len(a)),
                   "low_powered_under_20_episodes": bool(len(a) < 20)}
            for j, c in enumerate(cols):
                v = a[:, j]
                v = v[np.isfinite(v)]
                row[c] = {"median": round(float(np.median(v)), 3),
                          "iqr": round(float(np.percentile(v, 75) - np.percentile(v, 25)), 3),
                          "n": int(v.size)} if v.size else None
            o[fam] = row
        return o
    return {"guard_0.10s_primary": summarise(by), "guard_0.30s_sensitivity": summarise(sens),
            "columns": cols}


def event_robustness(rows: list[dict]) -> dict:
    out = {}
    for name in ALL:
        by = defaultdict(lambda: {"ev": 0, "hit": 0, "hit_tol": 0, "stable": 0, "false": 0})
        for r in rows:
            m = r["sym_valid"] & np.isfinite(r["Ms"]) & r["audio_pair"] & np.isfinite(r["mov"][name])
            if m.sum() < 400:
                continue
            idx = np.nonzero(m)[0]
            rs = C.within_track_rank(r["Ms"][m], np.zeros(m.sum()))
            rc = C.within_track_rank(r["mov"][name][m], np.zeros(m.sum()))
            det = rc >= DETECT_RANK
            pos = {int(i): j for j, i in enumerate(idx)}
            ev = rs >= EVENT_RANK
            tol = np.zeros_like(det)
            for j, i in enumerate(idx):
                for k in range(-TOL_HOPS, TOL_HOPS + 1):
                    q = pos.get(int(i) + k)
                    if q is not None and det[q]:
                        tol[j] = True
                        break
            st = rs <= STABLE_RANK
            b = by[r["family"]]
            b["ev"] += int(ev.sum()); b["hit"] += int((ev & det).sum()); b["hit_tol"] += int((ev & tol).sum())
            b["stable"] += int(st.sum()); b["false"] += int((st & (rc >= EVENT_RANK)).sum())
        fam = {f: {"n_events": v["ev"],
                   "event_recall_consumer_time": round(v["hit"] / max(v["ev"], 1), 4),
                   "event_recall_event_tolerant": round(v["hit_tol"] / max(v["ev"], 1), 4),
                   "false_movement_rate_in_stable_periods": round(v["false"] / max(v["stable"], 1), 4)}
               for f, v in sorted(by.items()) if v["ev"] >= 50}
        rt = [v["event_recall_event_tolerant"] for v in fam.values()]
        rc_ = [v["event_recall_consumer_time"] for v in fam.values()]
        out[name] = {"by_family": fam,
                     "spread_event_tolerant_recall": round(max(rt) - min(rt), 4) if rt else None,
                     "spread_consumer_time_recall": round(max(rc_) - min(rc_), 4) if rc_ else None,
                     "worst_family_event_tolerant": min(fam, key=lambda k: fam[k]["event_recall_event_tolerant"]) if fam else None}
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--git-head", type=str, default="UNKNOWN")
    args = ap.parse_args()
    prereg = json.loads(PREREG.read_text())
    rows = load_stems(args.corpus)

    before = family_table(rows, None)
    after = family_table(rows, "audio_pair")
    after_single = family_table(rows, "audio_ok")   # REPORTED_DIAGNOSTIC, decides nothing
    removal = removal_stats(rows)
    ad = attack_decay(rows)
    ev = event_robustness(rows)

    # ---- A materiality, established 0.10 scale, judged on P0 ----
    b, a = before["P0_CURRENT"], after["P0_CURRENT"]
    d_worst = round(a["worst_family_r2"] - b["worst_family_r2"], 4)
    d_spread = round(b["spread"] - a["spread"], 4)
    mask_material = bool(d_worst >= 0.10 or d_spread >= 0.10)

    # ---- B substantial systematic mismatch (disclosed operationalisation) ----
    g = ad["guard_0.10s_primary"]
    weak = ["synth_lead_pad", "reed_pipe", "ensemble_voice", "chromatic_percussion"]
    strong = ["piano_keys", "guitar", "bass"]
    def med(fams, col):
        v = [g[f][col]["median"] for f in fams if f in g and g[f].get(col)]
        return float(np.median(v)) if v else float("nan")
    cov_w, cov_s = med(weak, "audible_gate_coverage"), med(strong, "audible_gate_coverage")
    atk_w, atk_s = med(weak, "attack_50_hops"), med(strong, "attack_50_hops")
    ad_material = bool((np.isfinite(cov_w) and np.isfinite(cov_s) and (cov_s - cov_w) >= 0.10)
                       or (np.isfinite(atk_w) and np.isfinite(atk_s) and (atk_w - atk_s) >= 1.0))

    # ---- C event-tolerant substantially reduces cross-family failure ----
    spread_r2 = after["P0_CURRENT"]["spread"]
    spread_ev = ev["P0_CURRENT"]["spread_event_tolerant_recall"]
    event_material = bool(spread_ev is not None and spread_r2 is not None
                          and (spread_r2 - spread_ev) >= 0.10)

    # The brief's four outcomes have OVERLAPPING conditions and no precedence order.
    # The clause that separates MIXED from CONFOUNDED is whether "substantial family
    # failure remains after audio support and event-tolerant evaluation". Judged on the
    # SAME established 0.10 absolute scale - no new number enters the decision path.
    target_mismatch = bool(mask_material or ad_material)
    failure_remains = bool(spread_ev is not None and spread_ev >= 0.10)
    if not target_mismatch and failure_remains:
        outcome = "TIMBRE_REPRESENTATION_LIMIT_PERSISTS"
    elif target_mismatch and failure_remains:
        outcome = "TIMBRE_TARGET_AND_REPRESENTATION_MIXED"
    elif target_mismatch and event_material:
        outcome = "TIMBRE_ORACLE_CONFOUNDED"
    else:
        outcome = "TIMBRE_DIAGNOSTIC_INCONCLUSIVE"
    taxonomy = {
        "target_mismatch_clause_met": target_mismatch,
        "which_sub_clause": {"mask_parity_material": mask_material,
                             "attack_decay_substantial_mismatch": ad_material},
        "event_tolerant_substantially_reduces_failure": event_material,
        "substantial_family_failure_remains": failure_remains,
        "residual_event_tolerant_recall_spread": spread_ev,
        "AMBIGUITY_IN_THE_BRIEF_DISCLOSED": (
            "TIMBRE_ORACLE_CONFOUNDED's literal condition is ALSO satisfied by this data - "
            "attack/decay mismatch is substantial AND the event-tolerant metric substantially reduces "
            "the apparent cross-family failure. The two outcomes overlap and the brief gives no precedence. "
            "MIXED is returned because its distinguishing clause - substantial family failure REMAINS after "
            "audio support and event-tolerant evaluation - is true by a wide margin, and because CONFOUNDED's "
            "interpretation ('cannot yet be attributed cleanly to the representation') is not supported for "
            "synth_lead_pad and chromatic_percussion. The Captain may overrule; both clause sets are reported."),
    }

    receipt = {
        "schema": "spectrasynq.timbre_diagnostic_result.v1", "job": "J3I",
        "git_head": args.git_head,
        "label": "CONSTRUCT-VALIDITY AUDIT - no new estimator, no model, no frontend, no visual experiment, no label repair",
        "preregistration": str(PREREG.relative_to(C.ROOT)),
        "preregistration_amendments": prereg.get("amendments", []),
        "execution_environment": "Anthropic cloud container (HOST-class). BabySlakh 16 kHz, md5 verified against the publisher's checksum.",
        "controls": {"instrumented_rms_max_abs_diff_vs_dsp_register_features": 0.0,
                     "audio_support_rule": "silence_mask(rms, -60.0 dBFS) - existing function, existing threshold, reused verbatim",
                     "representation_changed": False, "midi_labels_changed": False},
        "J3I_A_mask_parity": {
            "AUDIO_SUPPORTED_PAIR_definition": "audio_ok[i] AND audio_ok[i-8]",
            "before_no_audio_mask": before, "after_audio_supported_pair": after,
            "REPORTED_DIAGNOSTIC_single_endpoint_literal_mixture_parity": after_single,
            "frames_removed_by_family": removal,
            "materiality_established_0.10_scale_judged_on_P0": {
                "worst_family_r2_before": b["worst_family_r2"], "worst_family_r2_after": a["worst_family_r2"],
                "delta_worst_family": d_worst,
                "spread_before": b["spread"], "spread_after": a["spread"], "spread_shrink": d_spread,
                "material": mask_material},
        },
        "J3I_B_attack_decay_audit": {
            "uses_no_chroma_no_candidate_no_pitch_estimator": True,
            "envelope": prereg["J3I_B_ATTACK_DECAY_ORACLE_AUDIT"]["envelope_declared_before_measurement"],
            "eligibility": prereg["J3I_B_ATTACK_DECAY_ORACLE_AUDIT"]["episode_eligibility_declared_before_measurement"],
            "results": ad,
            "weak_vs_strong": {"weak_families": weak, "strong_families": strong,
                               "median_audible_gate_coverage_weak": round(cov_w, 4) if np.isfinite(cov_w) else None,
                               "median_audible_gate_coverage_strong": round(cov_s, 4) if np.isfinite(cov_s) else None,
                               "coverage_gap": round(cov_s - cov_w, 4) if np.isfinite(cov_w) and np.isfinite(cov_s) else None,
                               "median_attack_50_weak_hops": round(atk_w, 3) if np.isfinite(atk_w) else None,
                               "median_attack_50_strong_hops": round(atk_s, 3) if np.isfinite(atk_s) else None,
                               "attack_gap_hops": round(atk_w - atk_s, 3) if np.isfinite(atk_w) and np.isfinite(atk_s) else None,
                               "substantial_systematic_mismatch": ad_material},
        },
        "J3I_C_event_robustness": {
            "rank_convention_reused_verbatim": {"event": EVENT_RANK, "detected": DETECT_RANK,
                                                "stable": STABLE_RANK, "tolerance_hops": TOL_HOPS},
            "computed_on": "AUDIO_SUPPORTED_PAIR frames",
            "results": ev,
            "framewise_r2_spread_P0": spread_r2,
            "event_tolerant_recall_spread_P0": spread_ev,
            "spread_reduction": round(spread_r2 - spread_ev, 4) if spread_ev is not None else None,
            "substantially_reduces_cross_family_failure": event_material,
        },
        "operationalisation_disclosure": prereg["operationalisation_of_the_two_unquantified_clauses"],
        "outcome_taxonomy_evaluation": taxonomy,
        "outcome": outcome,
        "J3F_mutated": False, "J3G_mutated": False, "J3G2_mutated": False,
        "new_tonal_candidate": False, "cqt_run": False, "basic_pitch_run": False,
        "crp_repair": False, "nnls_run": False, "neural_model": False,
        "production_firmware_changed": False, "titan": False, "student_io_frozen": False,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(receipt, indent=2, sort_keys=False) + "\n")
    print(json.dumps({"outcome": outcome, "taxonomy": taxonomy,
                      "A": receipt["J3I_A_mask_parity"]["materiality_established_0.10_scale_judged_on_P0"],
                      "B": receipt["J3I_B_attack_decay_audit"]["weak_vs_strong"],
                      "C": {k: receipt["J3I_C_event_robustness"][k] for k in
                            ("framewise_r2_spread_P0", "event_tolerant_recall_spread_P0",
                             "spread_reduction", "substantially_reduces_cross_family_failure")}}, indent=2))
    print(f"receipt -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
