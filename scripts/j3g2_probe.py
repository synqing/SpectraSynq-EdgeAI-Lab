#!/usr/bin/env python3
"""J3G.2 - POST-HOC mechanistic probe on consumed BabySlakh tracks.

Nothing here is promotable. C2's Level C is POST_HOC_LEVEL_C_CONFIRMATION;
everything about the hybrid is POST_HOC_MECHANISTIC_PROBE. The decision axis is
TIMBRE, not R-squared.

Pre-registration: docs/mir/receipts/peak_root_hybrid/J3G2_PREREGISTRATION.json
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import j3g_common as C  # noqa: E402

sys.path.insert(0, str(C.ROOT / "src"))
from edgeai.mir import tonal_projection as tp  # noqa: E402
from edgeai.mir.harmonic_movement import pitch_class_state, tv_movement  # noqa: E402
from edgeai.mir.harmonic_visual import pipeline  # noqa: E402
from edgeai.mir.note_register import SR, Note, frame_grid  # noqa: E402

PREREG = C.ROOT / "docs/mir/receipts/peak_root_hybrid/J3G2_PREREGISTRATION.json"
SIDE = Path("/tmp/j3g2_cache")
STEMS = Path("/tmp/j3g_stem_cache")
HYBRID = "C5_PEAK_ROOT_HYBRID"
ORDER = ["P0_CURRENT", "C2_PEAK_HPCP", "C3_ROOT_SALIENCE", HYBRID]
TOL_HOPS = 2
NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def add_hybrid(b: dict) -> dict:
    v = np.load(SIDE / f"track__{b['track']}.npz")["C5"][: b["n"]]
    b["states"][HYBRID] = tp.l1(tp.apply_carry_forward(v, native_domain="amplitude", winner="P0_CURRENT"))
    b["mov"][HYBRID] = tv_movement(b["states"][HYBRID])
    return b


# ------------------------------------------------------------- fixtures
def _tone(midi: float, harmonics: int, dur: float = 3.0) -> np.ndarray:
    f = 440.0 * 2.0 ** ((midi - 69.0) / 12.0)
    t = np.arange(int(SR * dur), dtype=np.float64) / SR
    return sum((1.0 / h) * np.sin(2.0 * np.pi * h * f * t) for h in range(1, harmonics + 1))


FIXTURES = {"PURE_SINE": lambda: 0.2 * _tone(60, 1),
            "HARMONIC_NOTE": lambda: 0.2 * _tone(60, 8),
            "TWO_NOTE_FIFTH": lambda: 0.2 * (_tone(60, 8) + _tone(67, 8)),
            "MAJOR_TRIAD": lambda: 0.2 * (_tone(60, 8) + _tone(64, 8) + _tone(67, 8))}
TONES = {"PURE_SINE": [0], "HARMONIC_NOTE": [0], "TWO_NOTE_FIFTH": [0, 7], "MAJOR_TRIAD": [0, 4, 7]}


def fixtures() -> dict:
    out = {}
    for fid, gen in FIXTURES.items():
        st = tp.stft_power(gen())
        raw = C.raw_projections(st)
        raw.pop("_c4_rectified_mass_fraction")
        s = C.states_from_raw(raw, winner="P0_CURRENT")
        s[HYBRID] = tp.l1(tp.apply_carry_forward(tp.c5_peak_root(st), native_domain="amplitude", winner="P0_CURRENT"))
        i = s["P0_CURRENT"].shape[0] // 2
        rows = {}
        for k in ORDER:
            x = s[k][i]
            t = TONES[fid]
            ct = float(sum(x[j] for j in t))
            nonc = [float(x[j]) for j in range(12) if j not in t]
            rows[k] = {"vector": {NAMES[j]: round(float(x[j]), 4) for j in range(12)},
                       "chord_tone_mass": round(ct, 4), "non_chord_tone_mass": round(1.0 - ct, 4),
                       "top_set_is_the_chord": sorted(int(z) for z in np.argsort(-x)[:len(t)]) == sorted(t),
                       "weakest_over_strongest_chord_tone": round(float(min(x[j] for j in t) / max(x[j] for j in t)), 4),
                       "largest_single_non_chord_class": round(max(nonc), 4)}
        out[fid] = rows
    p0 = out["MAJOR_TRIAD"]["P0_CURRENT"]["chord_tone_mass"]
    h = {k: out[k][HYBRID] for k in FIXTURES}
    out["_captains_four_requirements"] = {
        "preserve_both_notes_of_the_fifth": bool(h["TWO_NOTE_FIFTH"]["top_set_is_the_chord"]
                                                 and h["TWO_NOTE_FIFTH"]["weakest_over_strongest_chord_tone"] >= 0.50),
        "preserve_all_three_triad_tones": bool(h["MAJOR_TRIAD"]["top_set_is_the_chord"]
                                               and h["MAJOR_TRIAD"]["chord_tone_mass"] >= 0.70 * p0
                                               and h["MAJOR_TRIAD"]["weakest_over_strongest_chord_tone"] >= 0.50),
        "not_collapsed_to_root_only": bool(h["TWO_NOTE_FIFTH"]["weakest_over_strongest_chord_tone"] >= 0.50
                                           and h["MAJOR_TRIAD"]["weakest_over_strongest_chord_tone"] >= 0.50),
        "no_gross_phantom_chord_mass": bool(all(h[f]["largest_single_non_chord_class"] <= 0.25 for f in FIXTURES)),
    }
    out["_captains_four_requirements"]["all_pass"] = all(out["_captains_four_requirements"].values())
    out["_F2_demoted_diagnostic"] = {
        "clause": "HARMONIC_NOTE non-root mass <= P0 measured (0.472)",
        "hybrid": out["HARMONIC_NOTE"][HYBRID]["non_chord_tone_mass"],
        "passes": bool(out["HARMONIC_NOTE"][HYBRID]["non_chord_tone_mass"]
                       <= out["HARMONIC_NOTE"]["P0_CURRENT"]["non_chord_tone_mass"]),
        "status": "REPORTED, NOT BLOCKING - see the pre-registration amendment"}
    return out


# ---------------------------------------------------------- solo family
def solo(tracks: list[str], corpus: Path) -> dict:
    from scipy.stats import spearmanr
    import yaml
    rows = []
    for tname in tracks:
        d = corpus / tname
        md = yaml.safe_load((d / "metadata.yaml").read_text())
        for f in sorted(p for p in (d / "stems").glob("*.wav") if not p.name.startswith("._")):
            cf = STEMS / f"{tname}__{f.stem}.npz"
            sc = SIDE / f"stem__{tname}__{f.stem}.npz"
            if not cf.is_file() or not sc.is_file():
                continue
            z = np.load(cf, allow_pickle=False)
            raw = {k: z[f"R_{k}"] for k in C.RAW_KEYS}
            st = C.states_from_raw(raw, winner="P0_CURRENT")
            n = raw["PC_POWER"].shape[0]
            st[HYBRID] = tp.l1(tp.apply_carry_forward(np.load(sc)["C5"][:n],
                                                      native_domain="amplitude", winner="P0_CURRENT"))
            Ms, valid = z["Ms"], z["valid"]
            mv = {k: tv_movement(st[k]) for k in ORDER}
            v = valid & np.all([np.isfinite(x) for x in mv.values()], axis=0) & np.isfinite(Ms)
            if v.sum() < 400:
                continue
            rows.append({"track": tname, "stem": f.stem, "family": C.family_of(int(md["stems"][f.stem]["program_num"])),
                         "Ms": Ms[v], "Ma": {k: mv[k][v] for k in ORDER}})
    by_fam = defaultdict(list)
    for r in rows:
        by_fam[r["family"]].append(r)
    out = {"_n_stems": len(rows)}
    for name in ORDER:
        fam = {}
        for fname, rs in sorted(by_fam.items()):
            g = np.concatenate([np.full(len(r["Ms"]), f"{r['track']}:{r['stem']}") for r in rs])
            if len(np.unique(g)) < 3:
                continue
            Ms = np.concatenate([r["Ms"] for r in rs])
            Ma = np.concatenate([r["Ma"][name] for r in rs])
            fam[fname] = {"n_stems": len(rs), "n_frames": int(len(Ms)),
                          "solo_stem_r2": C.grouped_r2(Ma, Ms, g),
                          "spearman": round(float(spearmanr(Ma, Ms).statistic), 4)}
        allg = np.concatenate([np.full(len(r["Ms"]), f"{r['track']}:{r['stem']}") for r in rows])
        vals = [v["solo_stem_r2"] for v in fam.values()]
        out[name] = {"overall_r2": C.grouped_r2(np.concatenate([r["Ma"][name] for r in rows]),
                                                np.concatenate([r["Ms"] for r in rows]), allg),
                     "by_family": fam, "spread": round(max(vals) - min(vals), 4) if vals else None,
                     "worst_family": min(fam, key=lambda k: fam[k]["solo_stem_r2"]) if fam else None,
                     "worst_family_r2": round(min(vals), 4) if vals else None}
    return out


# -------------------------------------------------------------- level C
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
            "resting_median_deltaE": round(float(np.median(de_now[resting])), 4),
            "direction_reversal_rate": round(float(rev.mean()), 4) if rev.size else None,
            "resting_above_threshold_VACUOUS_BY_CONSTRUCTION": round(float(rn[resting].mean()), 4),
            "mean_harmonic_recall": round(hr, 4),
            "selectivity_margin": round(hr - et["ACOUSTIC_CHANGE_LOW_HARMONIC_CHANGE"], 4),
            "n_frames": int(len(de_now))}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--git-head", type=str, default="UNKNOWN")
    args = ap.parse_args()
    prereg = json.loads(PREREG.read_text())
    fx = fixtures()
    if not fx["_captains_four_requirements"]["all_pass"]:
        args.out.write_text(json.dumps({"job": "J3G.2", "outcome": "J3G2_INCONCLUSIVE",
                                        "reason": "hybrid failed a blocking fixture requirement",
                                        "fixtures": fx}, indent=2) + "\n")
        print(json.dumps(fx["_captains_four_requirements"], indent=2))
        return 1

    split = C.split_tracks(args.corpus)
    allb = [add_hybrid(C.cached_track(args.corpus / t)) for t in split["all"]]
    cls_all, _, _ = C.challenge_masks(allb)
    counts = {k: int(v.sum()) for k, v in cls_all.items()}
    membership_ok = counts == {"HARMONIC_CHANGE_FLAT_ENERGY": 2299, "HARMONIC_CHANGE_NO_ONSET": 4000,
                               "ACOUSTIC_CHANGE_LOW_HARMONIC_CHANGE": 3292}

    hold = [b for b in allb if b["track"] in set(split["final_holdout"])]
    cls, groups, rM = C.challenge_masks(hold)
    resting = ~(cls["HARMONIC_CHANGE_FLAT_ENERGY"] | cls["HARMONIC_CHANGE_NO_ONSET"]
                | cls["ACOUSTIC_CHANGE_LOW_HARMONIC_CHANGE"])
    level_ab = {k: C.level_a_b(hold, k, cls, groups, rM) for k in ORDER}
    lags = {HYBRID: C.lag_curve(hold, HYBRID)}

    solo_all = solo(split["all"], args.corpus)
    solo_hold = solo(split["final_holdout"], args.corpus)

    for b in hold:
        b["states"]["_ORACLE"] = b["oracle_state"]
        b["mov"]["_ORACLE"] = b["M_oracle"]
    vis = {k: visual(hold, k, k, cls, resting) for k in ORDER}
    vis["ORACLE"] = visual(hold, "_ORACLE", "_ORACLE", cls, resting)

    # ---- pre-registered decision, TIMBRE axis, primary = all 20 tracks ----
    P, H = solo_all["P0_CURRENT"], solo_all[HYBRID]
    T1 = round(H["worst_family_r2"] - P["worst_family_r2"], 4)
    T2 = round(P["spread"] - H["spread"], 4)
    timbre = {"T1_worst_family_improvement": T1, "T1_met": bool(T1 >= 0.10),
              "T2_spread_shrink": T2, "T2_met": bool(T2 >= 0.10),
              "either_met": bool(T1 >= 0.10 or T2 >= 0.10)}
    R1 = round(0.5 * (level_ab[HYBRID]["challenge_recall"]["HARMONIC_CHANGE_FLAT_ENERGY"]
                      + level_ab[HYBRID]["challenge_recall"]["HARMONIC_CHANGE_NO_ONSET"])
               - 0.5 * (level_ab["P0_CURRENT"]["challenge_recall"]["HARMONIC_CHANGE_FLAT_ENERGY"]
                        + level_ab["P0_CURRENT"]["challenge_recall"]["HARMONIC_CHANGE_NO_ONSET"]), 4)
    R2 = round(level_ab[HYBRID]["challenge_recall"]["ACOUSTIC_CHANGE_LOW_HARMONIC_CHANGE"]
               - level_ab["P0_CURRENT"]["challenge_recall"]["ACOUSTIC_CHANGE_LOW_HARMONIC_CHANGE"], 4)
    R3 = round(vis[HYBRID]["selectivity_margin"] - vis["P0_CURRENT"]["selectivity_margin"], 4)
    regress = {"R1_harmonic_recall_delta": R1, "R1_ok": bool(R1 >= -0.02),
               "R2_false_response_delta": R2, "R2_ok": bool(R2 <= 0.02),
               "R3_selectivity_margin_delta": R3, "R3_ok": bool(R3 >= 0.0)}
    competitive = bool(vis[HYBRID]["selectivity_margin"]
                       >= min(vis["C2_PEAK_HPCP"]["selectivity_margin"], vis["C3_ROOT_SALIENCE"]["selectivity_margin"]))

    if not membership_ok:
        outcome = "J3G2_INCONCLUSIVE"
    elif not timbre["either_met"]:
        outcome = "SAME_STFT_PROJECTION_TIMBRE_LIMIT"
    elif all(regress[k] for k in ("R1_ok", "R2_ok", "R3_ok")) and competitive:
        outcome = "PEAK_ROOT_HYBRID_PROMISING"
    else:
        outcome = "J3G2_INCONCLUSIVE"

    receipt = {
        "schema": "spectrasynq.peak_root_hybrid_result.v1",
        "job": "J3G.2", "git_head": args.git_head,
        "label": "POST_HOC_MECHANISTIC_PROBE - the BabySlakh tracks are CONSUMED. Nothing here is promotable.",
        "preregistration": str(PREREG.relative_to(C.ROOT)),
        "preregistration_amendments": prereg.get("amendments_before_any_corpus_metric", []),
        "execution_environment": "Anthropic cloud container (HOST-class). BabySlakh 16 kHz, md5 verified against the publisher's checksum.",
        "labels": {"C2_level_C": "POST_HOC_LEVEL_C_CONFIRMATION", "hybrid": "POST_HOC_MECHANISTIC_PROBE"},
        "control_challenge_membership": {"counts": counts, "matches_J3D_A_v2": membership_ok},
        "hybrid_definition": prereg["J3G2_B_THE_ONE_HYBRID"],
        "fixtures": fx,
        "LEVEL_A_B_holdout_POST_HOC": level_ab,
        "lag_curve_hybrid_REPORTED_NOT_OPTIMISED": lags,
        "TIMBRE_primary_all_20_tracks": solo_all,
        "TIMBRE_secondary_holdout_10_tracks": solo_hold,
        "LEVEL_C_visual_POST_HOC": {
            "grammar_modified": False,
            "grammar": "J3E HARMONIC COLOUR TRANSITION unchanged: M_REF 0.35, A_MIN 0.02, A_MAX 0.60, photons 1.0, exposure 2.2, without_floor, +/-2-hop event tolerance, threshold = p90 of each condition's own resting frames",
            "headline_metric": "selectivity margin = mean(event-tolerant harmonic recall) - event-tolerant acoustic false response",
            "retired_metric": "the arithmetic mean of five oracle-gap fractions - retired because J3G showed it is flattered by recall overshoot",
            "conditions": vis,
            "ordering_P0_to_C2_to_C3_to_ORACLE": {k: vis[k]["selectivity_margin"] for k in
                                                  ["P0_CURRENT", "C2_PEAK_HPCP", "C3_ROOT_SALIENCE", HYBRID, "ORACLE"]},
        },
        "decision_timbre_axis": timbre,
        "decision_regression_guards": regress,
        "decision_visual_competitive": competitive,
        "outcome": outcome,
        "fresh_validation_required": "YES" if outcome == "PEAK_ROOT_HYBRID_PROMISING" else "NO",
        "J3G_outcome_changed": False, "original_holdout_treated_as_fresh": False,
        "cqt_run": False, "basic_pitch_run": False, "neural_student_trained": False,
        "source_separator_run": False, "foundation_model_run": False,
        "production_firmware_changed": False, "titan": False, "student_io_frozen": False,
        "J3D_mutated": False, "J3E_mutated": False, "J3F_mutated": False, "J3G_mutated": False,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(receipt, indent=2, sort_keys=False) + "\n")
    print(json.dumps({"outcome": outcome, "timbre": timbre, "regress": regress,
                      "competitive": competitive,
                      "margins": receipt["LEVEL_C_visual_POST_HOC"]["ordering_P0_to_C2_to_C3_to_ORACLE"],
                      "level_ab": {k: level_ab[k]["r2"] for k in ORDER},
                      "solo_all": {k: {"overall": solo_all[k]["overall_r2"], "spread": solo_all[k]["spread"],
                                       "worst": solo_all[k]["worst_family"], "worst_r2": solo_all[k]["worst_family_r2"]}
                                   for k in ORDER}}, indent=2))
    print(f"receipt -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
