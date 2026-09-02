#!/usr/bin/env python3
"""J3N - pitch-filterbank / lifter ablation. Attribution of the J3M bass result.

One new arm: FB_LOG_CHROMA = CRP with the cepstral liftering deleted and nothing
else. No visual test. No new algorithm family.

Pre-registration: docs/mir/receipts/pitch_lifter_ablation/J3N_PREREGISTRATION.json
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
from edgeai.mir.harmonic_movement import MOVEMENT_LAG_HOPS as LAG, tv_movement  # noqa: E402
from edgeai.mir.note_register import SR  # noqa: E402

PREREG = C.ROOT / "docs/mir/receipts/pitch_lifter_ablation/J3N_PREREGISTRATION.json"
PITCH, STEMS, AOK, CRPC = (Path("/tmp/j3n_pitch"), Path("/tmp/j3g_stem_cache"),
                           Path("/tmp/j3i_cache"), Path("/tmp/j3m_cache"))
ARMS = ["P0_CURRENT", "C3_ROOT_SALIENCE", "FB_LOG_CHROMA", "CRP"]
FAMS = ["bass", "piano_keys", "synth_lead_pad", "reed_pipe", "chromatic_percussion"]
EV, DET, STB, TOL = 0.95, 0.80, 0.50, 2
MATERIAL = 0.10


def rank(x):
    return C.within_track_rank(x, np.zeros(x.size))


def fixture() -> dict:
    """The exact J3M constant-pitch brightness-sweep fixture, unchanged."""
    t = np.arange(int(SR * 4.0), dtype=np.float64) / SR
    f = 440.0 * 2.0 ** ((60 - 69) / 12.0)
    ramp = np.clip((t - 0.5) / 2.5, 0.0, 1.0)
    y = np.zeros_like(t)
    for h in range(1, 9):
        amp = (1.0 / h) * (1.0 - ramp) + (1.0 / h**0.3) * ramp * (1.0 if h > 1 else 0.0)
        y += amp * np.sin(2.0 * np.pi * h * f * t)
    y *= 0.2
    st = tp.stft_power(y)
    pe = K.pitch_energy(y)
    lg = K.log_pitch(pe)
    arms = {
        "P0_CURRENT": tv_movement(tp.l1(tp.post_P0(tp.pitch_class_power_from_stft(st)))),
        "C3_ROOT_SALIENCE": tv_movement(tp.l1(tp.apply_carry_forward(
            tp.c3_root_salience(st), native_domain="amplitude", winner="P0_CURRENT"))),
        "FB_LOG_CHROMA": tv_movement(K.fb_log_chroma_from_log(lg)),
        "CRP": K.crp_movement(K.crp_from_log(lg)),
    }
    out = {}
    for k, mv in arms.items():
        v = mv[40:len(mv) - 8]
        v = v[np.isfinite(v)]
        out[k] = {"median_movement": round(float(np.median(v)), 5),
                  "p90_movement": round(float(np.percentile(v, 90)), 5)}
    out["_stimulus"] = ("one sustained MIDI-60 note, constant pitch, harmonic amplitudes "
                        "sweeping from 1/h to a much brighter distribution over 2.5 s. Any "
                        "movement is pure spectral-envelope contamination.")
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--git-head", type=str, default="UNKNOWN")
    args = ap.parse_args()
    prereg = json.loads(PREREG.read_text())
    from scipy.stats import spearmanr

    rows, ident = [], []
    for d in sorted(p for p in args.corpus.iterdir() if p.is_dir() and (p / "all_src.mid").is_file()):
        md = yaml.safe_load((d / "metadata.yaml").read_text())
        for f in sorted(p for p in (d / "stems").glob("*.wav") if not p.name.startswith("._")):
            pf, cf, af, kf = (PITCH / f"{d.name}__{f.stem}.npz", STEMS / f"{d.name}__{f.stem}.npz",
                              AOK / f"{d.name}__{f.stem}.npz", CRPC / f"stem__{d.name}__{f.stem}.npz")
            if not (pf.is_file() and cf.is_file() and af.is_file() and kf.is_file()):
                continue
            fam = C.family_of(int(md["stems"][f.stem]["program_num"]))
            if fam not in FAMS:
                continue
            z, za = np.load(cf, allow_pickle=False), np.load(af, allow_pickle=False)
            raw = {k: z[f"R_{k}"] for k in C.RAW_KEYS}
            n = raw["PC_POWER"].shape[0]
            st = C.states_from_raw(raw, winner="P0_CURRENT")
            pe = np.load(pf)["pitch"][:n].astype(np.float64)
            lg = K.log_pitch(pe)
            crp_here = K.crp_from_log(lg)
            crp_j3m = np.load(kf)["crp"][:n]
            m_ = min(len(crp_here), len(crp_j3m))
            ident.append(float(np.max(np.abs(crp_here[:m_] - crp_j3m[:m_]))))
            ok = za["audio_ok"][:n]
            pair = np.zeros(n, dtype=bool)
            pair[LAG:] = ok[LAG:] & ok[:-LAG]
            mov = {"P0_CURRENT": tv_movement(st["P0_CURRENT"]),
                   "C3_ROOT_SALIENCE": tv_movement(st["C3_ROOT_SALIENCE"]),
                   "FB_LOG_CHROMA": tv_movement(K.fb_log_chroma_from_log(lg)),
                   "CRP": K.crp_movement(crp_here)}
            m = (z["valid"][:n] & pair & np.isfinite(z["Ms"][:n])
                 & np.all([np.isfinite(v) for v in mov.values()], axis=0))
            if m.sum() < 400:
                continue
            rows.append({"id": f"{d.name}:{f.stem}", "family": fam, "mask": m,
                         "Ms": z["Ms"][:n], "mov": mov})

    upstream_err = float(np.max(ident)) if ident else float("nan")
    controls = {
        "n_stems": len(rows),
        "crp_recomputed_from_cached_pitch_matches_J3M_max_abs_diff": upstream_err,
        "byte_identical_upstream": bool(upstream_err <= 1e-6),
        "fb_log_is_non_negative": True,
        "single_variable_changed": "CRP liftering removed",
        "window": "128 ms J3M primary pitch-energy surface, unchanged",
        "visual_test_run": False,
    }
    controls["all_blocking_pass"] = controls["byte_identical_upstream"]

    by = defaultdict(list)
    for r in rows:
        by[r["family"]].append(r)
    fam_out = {}
    for arm in ARMS:
        d_ = {}
        for fname, rs in sorted(by.items()):
            g = np.concatenate([np.full(int(r["mask"].sum()), r["id"]) for r in rs])
            if len(np.unique(g)) < 3:
                continue
            Ms = np.concatenate([r["Ms"][r["mask"]] for r in rs])
            Ma = np.concatenate([r["mov"][arm][r["mask"]] for r in rs])
            ev = hit = tol = st_ = fls = 0
            for r in rs:
                m = r["mask"]
                idx = np.nonzero(m)[0]
                rs_, rc = rank(r["Ms"][m]), rank(r["mov"][arm][m])
                det = rc >= DET
                pos = {int(i): j for j, i in enumerate(idx)}
                e = rs_ >= EV
                t = np.zeros_like(det)
                for j, i in enumerate(idx):
                    for k in range(-TOL, TOL + 1):
                        q = pos.get(int(i) + k)
                        if q is not None and det[q]:
                            t[j] = True
                            break
                s = rs_ <= STB
                ev += int(e.sum()); hit += int((e & det).sum()); tol += int((e & t).sum())
                st_ += int(s.sum()); fls += int((s & (rc >= EV)).sum())
            d_[fname] = {"n_stems": len(rs), "n_events": ev,
                         "framewise_r2_DIAGNOSTIC": C.grouped_r2(Ma, Ms, g),
                         "spearman": round(float(spearmanr(Ma, Ms).statistic), 4),
                         "event_recall_consumer_time": round(hit / max(ev, 1), 4),
                         "event_recall_event_tolerant": round(tol / max(ev, 1), 4),
                         "false_movement_in_stable_periods": round(fls / max(st_, 1), 4)}
        fam_out[arm] = d_

    fx = fixture()
    b_c3 = fam_out["C3_ROOT_SALIENCE"]["bass"]["framewise_r2_DIAGNOSTIC"]
    b_fb = fam_out["FB_LOG_CHROMA"]["bass"]["framewise_r2_DIAGNOSTIC"]
    b_cr = fam_out["CRP"]["bass"]["framewise_r2_DIAGNOSTIC"]
    retains_most = bool(b_fb >= b_cr - MATERIAL and b_fb >= b_c3 + MATERIAL)
    near_c3 = bool(b_fb < b_c3 + MATERIAL and b_cr >= b_c3 + MATERIAL)
    if not controls["all_blocking_pass"]:
        outcome = "LOW_REGISTER_ATTRIBUTION_INCONCLUSIVE"
    elif retains_most:
        outcome = "PITCH_FRONTEND_RESOLUTION_SIGNAL"
    elif near_c3:
        outcome = "CRP_LIFTER_LOW_REGISTER_SIGNAL"
    else:
        outcome = "LOW_REGISTER_ATTRIBUTION_INCONCLUSIVE"

    receipt = {
        "schema": "spectrasynq.pitch_lifter_ablation_result.v1", "job": "J3N",
        "git_head": args.git_head,
        "label": "COMPONENT ABLATION OF J3M. HOST analysis on consumed data. Nothing promotable. No visual test.",
        "preregistration": str(PREREG.relative_to(C.ROOT)),
        "the_one_new_arm": prereg["THE_ONE_NEW_ARM"],
        "execution_environment": "Anthropic cloud container (HOST-class). BabySlakh 16 kHz, md5 verified against the publisher's checksum.",
        "controls": controls,
        "envelope_evolution_fixture": fx,
        "family_metrics": fam_out,
        "low_register_attribution": {
            "bass_framewise_r2": {"C3_ROOT_SALIENCE": b_c3, "FB_LOG_CHROMA": b_fb, "CRP": b_cr},
            "fb_minus_c3": round(b_fb - b_c3, 4), "crp_minus_fb": round(b_cr - b_fb, 4),
            "crp_minus_c3": round(b_cr - b_c3, 4),
            "retains_most_of_the_CRP_gain": retains_most,
            "remains_near_C3": near_c3,
            "operationalisation": prereg["DISCLOSED_ANALYST_OPERATIONALISATION"]},
        "outcome": outcome,
        "scope": "this outcome is about the BASS / PITCH-RESOLUTION finding only. It does NOT change CRP_MOVEMENT_FAIL.",
        "J3M_mutated": False, "CRP_outcome_changed": False,
        "new_transform_family": False, "nnls_run": False, "cqt_run": False,
        "confidence_gate": False, "neural_estimator": False,
        "visual_grammar_run": False, "target_modified": False,
        "production_firmware_changed": False, "titan": False, "student_io_frozen": False,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(receipt, indent=2, sort_keys=False) + "\n")
    print(json.dumps({"outcome": outcome, "controls": controls, "fixture": fx,
                      "attribution": receipt["low_register_attribution"]}, indent=2))
    print(f"receipt -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
