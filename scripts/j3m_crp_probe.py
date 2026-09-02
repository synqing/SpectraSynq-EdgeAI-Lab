#!/usr/bin/env python3
"""J3M - faithful CRP movement probe. POST_HOC_CRP_MECHANISTIC_PROBE.

CRP supplies WHEN harmonic colour transitions. It never supplies WHAT colour.
Pre-registration: docs/mir/receipts/crp_probe/J3M_PREREGISTRATION.json
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
from edgeai.mir import crp as K  # noqa: E402
from edgeai.mir import tonal_projection as tp  # noqa: E402
from edgeai.mir.harmonic_movement import MOVEMENT_LAG_HOPS, tv_movement, within_track_rank  # noqa: E402
from edgeai.mir.harmonic_visual import pipeline  # noqa: E402
from edgeai.mir.note_register import SR  # noqa: E402

LAG = MOVEMENT_LAG_HOPS
PREREG = C.ROOT / "docs/mir/receipts/crp_probe/J3M_PREREGISTRATION.json"
STEMS, SIDE_A, CRPC = Path("/tmp/j3g_stem_cache"), Path("/tmp/j3i_cache"), Path("/tmp/j3m_cache")
FAMS = ["synth_lead_pad", "reed_pipe", "piano_keys", "bass", "chromatic_percussion"]
PRIMARY_FAMS, CONTROL_FAMS = ["synth_lead_pad", "reed_pipe"], ["piano_keys", "bass"]
ARMS = ["P0_CURRENT", "C3_ROOT_SALIENCE", "CRP"]
EVENT_RANK, DETECT_RANK, STABLE_RANK, TOL = 0.95, 0.80, 0.50, 2


def rank(x):
    return C.within_track_rank(x, np.zeros(x.size))


def envelope_fixture() -> dict:
    """Mechanism fixture: fixed pitch, evolving spectral envelope. Reported diagnostic."""
    t = np.arange(int(SR * 4.0), dtype=np.float64) / SR
    f = 440.0 * 2.0 ** ((60 - 69) / 12.0)
    ramp = np.clip((t - 0.5) / 2.5, 0.0, 1.0)          # brightness sweep, constant pitch
    y = np.zeros_like(t)
    for h in range(1, 9):
        amp = (1.0 / h) * (1.0 - ramp) + (1.0 / h**0.3) * ramp * (1.0 if h > 1 else 0.0)
        y += amp * np.sin(2.0 * np.pi * h * f * t)
    y *= 0.2
    st = tp.stft_power(y)
    c3 = tp.l1(tp.apply_carry_forward(tp.c3_root_salience(st), native_domain="amplitude",
                                      winner="P0_CURRENT"))
    p0 = tp.l1(tp.post_P0(tp.pitch_class_power_from_stft(st)))
    cr = K.crp(K.pitch_energy(y))
    n = min(len(c3), len(cr))
    sl = slice(40, n - 8)
    out = {}
    for name, mv in (("P0_CURRENT", tv_movement(p0[:n])), ("C3_ROOT_SALIENCE", tv_movement(c3[:n])),
                     ("CRP", K.crp_movement(cr[:n]))):
        v = mv[sl]
        v = v[np.isfinite(v)]
        out[name] = {"median_movement": round(float(np.median(v)), 5),
                     "p90_movement": round(float(np.percentile(v, 90)), 5)}
    out["_what_it_shows"] = ("a single sustained MIDI-60 note whose harmonic amplitudes sweep from "
                             "1/h to a much brighter distribution over 2.5 s, at constant pitch. "
                             "Any movement reported here is pure spectral-envelope contamination.")
    return out


def load_stems(corpus: Path) -> list[dict]:
    rows = []
    for d in sorted(p for p in corpus.iterdir() if p.is_dir() and (p / "all_src.mid").is_file()):
        md = yaml.safe_load((d / "metadata.yaml").read_text())
        for f in sorted(p for p in (d / "stems").glob("*.wav") if not p.name.startswith("._")):
            cf, af, kf = (STEMS / f"{d.name}__{f.stem}.npz", SIDE_A / f"{d.name}__{f.stem}.npz",
                          CRPC / f"stem__{d.name}__{f.stem}.npz")
            if not (cf.is_file() and af.is_file() and kf.is_file()):
                continue
            fam = C.family_of(int(md["stems"][f.stem]["program_num"]))
            if fam not in FAMS:
                continue
            z, za = np.load(cf, allow_pickle=False), np.load(af, allow_pickle=False)
            raw = {k: z[f"R_{k}"] for k in C.RAW_KEYS}
            n = raw["PC_POWER"].shape[0]
            st = C.states_from_raw(raw, winner="P0_CURRENT")
            cr = np.load(kf)["crp"][:n]
            ok = za["audio_ok"][:n]
            pair = np.zeros(n, dtype=bool)
            pair[LAG:] = ok[LAG:] & ok[:-LAG]
            mov = {"P0_CURRENT": tv_movement(st["P0_CURRENT"]),
                   "C3_ROOT_SALIENCE": tv_movement(st["C3_ROOT_SALIENCE"]),
                   "CRP": K.crp_movement(cr)}
            m = (z["valid"][:n] & pair & np.isfinite(z["Ms"][:n])
                 & np.all([np.isfinite(v) for v in mov.values()], axis=0))
            if m.sum() < 400:
                continue
            rows.append({"id": f"{d.name}:{f.stem}", "family": fam, "mask": m,
                         "Ms": z["Ms"][:n], "mov": mov,
                         "crp_min": float(cr.min()),
                         "crp_neg_mass": float(np.abs(np.clip(cr, None, 0)).sum()
                                               / (np.abs(cr).sum() + 1e-20))})
    return rows


def family_metrics(rows: list[dict]) -> dict:
    from scipy.stats import spearmanr
    by = defaultdict(list)
    for r in rows:
        by[r["family"]].append(r)
    out = {}
    for name in ARMS:
        fam = {}
        for fname, rs in sorted(by.items()):
            g = np.concatenate([np.full(int(r["mask"].sum()), r["id"]) for r in rs])
            if len(np.unique(g)) < 3:
                continue
            Ms = np.concatenate([r["Ms"][r["mask"]] for r in rs])
            Ma = np.concatenate([r["mov"][name][r["mask"]] for r in rs])
            ev = hit = tol = st = fls = 0
            for r in rs:
                m = r["mask"]
                idx = np.nonzero(m)[0]
                rs_, rc = rank(r["Ms"][m]), rank(r["mov"][name][m])
                det = rc >= DETECT_RANK
                pos = {int(i): j for j, i in enumerate(idx)}
                e = rs_ >= EVENT_RANK
                t = np.zeros_like(det)
                for j, i in enumerate(idx):
                    for k in range(-TOL, TOL + 1):
                        q = pos.get(int(i) + k)
                        if q is not None and det[q]:
                            t[j] = True
                            break
                s = rs_ <= STABLE_RANK
                ev += int(e.sum()); hit += int((e & det).sum()); tol += int((e & t).sum())
                st += int(s.sum()); fls += int((s & (rc >= EVENT_RANK)).sum())
            fam[fname] = {"n_stems": len(rs), "n_events": ev,
                          "framewise_r2_DIAGNOSTIC": C.grouped_r2(Ma, Ms, g),
                          "spearman": round(float(spearmanr(Ma, Ms).statistic), 4),
                          "event_recall_consumer_time": round(hit / max(ev, 1), 4),
                          "event_recall_event_tolerant": round(tol / max(ev, 1), 4),
                          "false_movement_in_stable_periods": round(fls / max(st, 1), 4)}
        out[name] = fam
    return out


def visual(blocks, state_key, mov_key, cls, resting) -> dict:
    de_all, rev_all = [], []
    for b in blocks:
        r = pipeline(b[state_key], b[mov_key], with_floor=False)
        de = np.nan_to_num(r["delta_e"], nan=0.0)
        tol = np.copy(de)
        for k in range(1, TOL + 1):
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
    et = {k: round(float((de_tol >= thr)[m].mean()), 4) for k, m in cls.items()}
    hr = 0.5 * (et["HARMONIC_CHANGE_FLAT_ENERGY"] + et["HARMONIC_CHANGE_NO_ONSET"])
    return {"threshold_deltaE_p90_of_own_resting": round(thr, 4),
            "consumer_time": {k: round(float((de_now >= thr)[m].mean()), 4) for k, m in cls.items()},
            "event_tolerant": et,
            "resting_median_deltaE": round(float(np.median(de_now[resting])), 4),
            "direction_reversal_rate": round(float(rev.mean()), 4) if rev.size else None,
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

    rows = load_stems(args.corpus)
    fid = K.filterbank_fidelity()
    signed = {"min_crp_value_across_stems": round(float(min(r["crp_min"] for r in rows)), 5),
              "median_negative_mass_fraction": round(float(np.median([r["crp_neg_mass"] for r in rows])), 4),
              "negatives_present": bool(min(r["crp_min"] for r in rows) < 0.0),
              "movement_normaliser": "sum(|x|) where non-zero",
              "rectification_applied": False, "absolute_value_applied": False,
              "row_min_shift_applied": False, "non_negative_floor_applied": False}
    controls = {"filterbank_fidelity": fid, "signed_vector_controls": signed,
                "fidelity_established": bool(fid["passband_min_gain_within_pm25_cents_dB"]["worst"] >= -1.0
                                             and fid["adjacent_semitone_rejection_dB"]["worst"] <= -40.0),
                "n_stems": len(rows)}
    controls["all_blocking_pass"] = bool(controls["fidelity_established"] and signed["negatives_present"])

    fam = family_metrics(rows)
    fixture = envelope_fixture()

    # ---- mixture visual ----
    blocks = []
    for d in sorted(p for p in args.corpus.iterdir() if p.is_dir() and (p / "all_src.mid").is_file()):
        b = C.cached_track(d)
        n = b["n"]
        cr = np.load(CRPC / f"mix__{d.name}.npz")["crp"][:n]
        b["mov"]["CRP"] = K.crp_movement(cr)
        b["valid"] = b["valid"] & np.isfinite(b["mov"]["CRP"])
        blocks.append(b)
    cls, groups, _ = C.challenge_masks(blocks)
    counts = {k: int(v.sum()) for k, v in cls.items()}
    membership_ok = counts == {"HARMONIC_CHANGE_FLAT_ENERGY": 2299, "HARMONIC_CHANGE_NO_ONSET": 4000,
                               "ACOUSTIC_CHANGE_LOW_HARMONIC_CHANGE": 3292}
    resting = ~(cls["HARMONIC_CHANGE_FLAT_ENERGY"] | cls["HARMONIC_CHANGE_NO_ONSET"]
                | cls["ACOUSTIC_CHANGE_LOW_HARMONIC_CHANGE"])
    for b in blocks:
        b["S_C3"] = b["states"]["C3_ROOT_SALIENCE"]
        b["S_ORACLE"] = b["oracle_state"]
        b["M_C3"] = b["mov"]["C3_ROOT_SALIENCE"]
        b["M_CRP"] = b["mov"]["CRP"]
        b["M_ORACLE"] = b["M_oracle"]
    vis = {"CONTROL_C3_state_C3_movement": visual(blocks, "S_C3", "M_C3", cls, resting),
           "TREATMENT_C3_state_CRP_movement": visual(blocks, "S_C3", "M_CRP", cls, resting),
           "ORACLE": visual(blocks, "S_ORACLE", "M_ORACLE", cls, resting)}

    # ---- outcome, brief's conditions only ----
    c3f, crf = fam["C3_ROOT_SALIENCE"], fam["CRP"]
    dec = {}
    for f in PRIMARY_FAMS:
        dec[f] = {"false_movement_C3": c3f[f]["false_movement_in_stable_periods"],
                  "false_movement_CRP": crf[f]["false_movement_in_stable_periods"],
                  "false_movement_reduced": bool(crf[f]["false_movement_in_stable_periods"]
                                                 < c3f[f]["false_movement_in_stable_periods"]),
                  "relative_change": round((crf[f]["false_movement_in_stable_periods"]
                                            - c3f[f]["false_movement_in_stable_periods"])
                                           / max(c3f[f]["false_movement_in_stable_periods"], 1e-9), 4),
                  "recall_C3": c3f[f]["event_recall_event_tolerant"],
                  "recall_CRP": crf[f]["event_recall_event_tolerant"],
                  "recall_drop": round(c3f[f]["event_recall_event_tolerant"]
                                       - crf[f]["event_recall_event_tolerant"], 4),
                  "recall_guard_ok": bool(c3f[f]["event_recall_event_tolerant"]
                                          - crf[f]["event_recall_event_tolerant"] <= 0.02)}
    CTRL, TRT = vis["CONTROL_C3_state_C3_movement"], vis["TREATMENT_C3_state_CRP_movement"]
    vis_ok = {"margin_no_worse": bool(TRT["selectivity_margin"] >= CTRL["selectivity_margin"]),
              "resting_deltaE_no_regression": bool(TRT["resting_median_deltaE"] <= CTRL["resting_median_deltaE"]),
              "reversal_no_regression": bool((TRT["direction_reversal_rate"] or 0.0)
                                             <= (CTRL["direction_reversal_rate"] or 0.0))}
    all_false_down = all(dec[f]["false_movement_reduced"] for f in PRIMARY_FAMS)
    all_recall_ok = all(dec[f]["recall_guard_ok"] for f in PRIMARY_FAMS)
    if not controls["all_blocking_pass"] or not membership_ok:
        outcome = "CRP_PROBE_INCONCLUSIVE"
    elif all_false_down and all_recall_ok and all(vis_ok.values()):
        outcome = "CRP_MOVEMENT_SIGNAL"
    else:
        outcome = "CRP_MOVEMENT_FAIL"

    receipt = {
        "schema": "spectrasynq.crp_movement_probe_result.v1", "job": "J3M",
        "git_head": args.git_head,
        "label": "POST_HOC_CRP_MECHANISTIC_PROBE - HOST information probe. Consumed data. Nothing promotable.",
        "preregistration": str(PREREG.relative_to(C.ROOT)),
        "crp_implementation_provenance": prereg["CRP_IMPLEMENTATION_PROVENANCE"],
        "execution_environment": "Anthropic cloud container (HOST-class). BabySlakh 16 kHz, md5 verified against the publisher's checksum.",
        "controls": controls,
        "challenge_membership": {"counts": counts, "matches_J3D_A_v2": membership_ok},
        "REPORTED_DIAGNOSTIC_envelope_evolution_fixture": fixture,
        "solo_family_metrics": fam,
        "primary_family_decision": dec,
        "chromatic_percussion_reported_separately": {
            "C3": c3f.get("chromatic_percussion"), "CRP": crf.get("chromatic_percussion"),
            "reading": prereg["CHROMATIC_PERCUSSION_HANDLING"]["correct_reading"],
            "not_evidence_against_CRP": True},
        "mixture_visual": vis,
        "mixture_visual_guards": vis_ok,
        "outcome": outcome,
        "fresh_validation_required": "YES" if outcome == "CRP_MOVEMENT_SIGNAL" else "NO",
        "J3D_mutated": False, "J3E_mutated": False, "J3F_mutated": False, "J3G_mutated": False,
        "J3I_mutated": False, "J3J_mutated": False, "J3K_mutated": False,
        "visual_grammar_altered": False, "target_modified": False,
        "nnls_run": False, "cqt_run": False, "basic_pitch_run": False, "neural_estimator": False,
        "foundation_model": False, "source_separator_run": False,
        "production_firmware_changed": False, "titan": False, "student_io_frozen": False,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(receipt, indent=2, sort_keys=False) + "\n")
    print(json.dumps({"outcome": outcome, "controls": controls, "decision": dec,
                      "visual": vis, "guards": vis_ok, "fixture": fixture}, indent=2))
    print(f"receipt -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
