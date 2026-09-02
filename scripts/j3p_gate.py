#!/usr/bin/env python3
"""J3P - cross-view reliability gate.

Can disagreement between two independently useful tonal views identify moments
where C3 harmonic movement should not be trusted?

C3 is the state and movement estimator under test. FB_LOG is a reliability
witness only. Not fusion. The C3 state is never replaced.

Pre-registration: docs/mir/receipts/cross_view_reliability/J3P_PREREGISTRATION.json
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
from edgeai.mir import tonal_projection as tp  # noqa: E402
from edgeai.mir.cross_view import endpoint_agreement, gated_movement, transition_confidence  # noqa: E402
from edgeai.mir.harmonic_movement import MOVEMENT_LAG_HOPS as LAG, tv_movement  # noqa: E402
from edgeai.mir.note_register import SR  # noqa: E402

PREREG = C.ROOT / "docs/mir/receipts/cross_view_reliability/J3P_PREREGISTRATION.json"
STEMS, AOK, PITCH = Path("/tmp/j3g_stem_cache"), Path("/tmp/j3i_cache"), Path("/tmp/j3n_pitch")
ARMS = ["C3_ROOT_SALIENCE", "C3_GATED"]
PRIMARY = ["synth_lead_pad", "reed_pipe"]
CONTROL = ["piano_keys", "bass"]
SEPARATE = ["chromatic_percussion"]
FAMS = PRIMARY + CONTROL + SEPARATE
EV, DET, STB, TOL = 0.95, 0.80, 0.50, 2
RECALL_GUARD = 0.02
N_PERM, SEED = 20, 20260902


def rank(x):
    return C.within_track_rank(x, np.zeros(x.size))


def c3_state_of(raw: dict) -> np.ndarray:
    return tp.l1(tp.apply_carry_forward(raw["C3_ROOT_SALIENCE"],
                                        native_domain="amplitude", winner="P0_CURRENT"))


def fixtures() -> dict:
    """The reused deterministic fixtures. Diagnostic only. No new threshold."""
    def tone(midis, dur=4.0, h=8):
        t = np.arange(int(SR * dur)) / SR
        y = np.zeros_like(t)
        for m in midis:
            f = 440.0 * 2 ** ((m - 69) / 12)
            for k in range(1, h + 1):
                if k * f < SR / 2:
                    y += (1.0 / k) * np.sin(2 * np.pi * k * f * t)
        return 0.2 * y / max(len(midis), 1)

    def pure(midi=60, dur=4.0):
        t = np.arange(int(SR * dur)) / SR
        return 0.2 * np.sin(2 * np.pi * 440.0 * 2 ** ((midi - 69) / 12) * t)

    def sweep():
        t = np.arange(int(SR * 4.0)) / SR
        f = 440.0 * 2 ** ((60 - 69) / 12)
        ramp = np.clip((t - 0.5) / 2.5, 0.0, 1.0)
        y = np.zeros_like(t)
        for h in range(1, 9):
            amp = (1.0 / h) * (1 - ramp) + (1.0 / h ** 0.3) * ramp * (1.0 if h > 1 else 0.0)
            y += amp * np.sin(2 * np.pi * h * f * t)
        return 0.2 * y

    stim = {"F1_pure_sine_midi60": pure(),
            "F2_harmonic_note_midi60": tone([60]),
            "F3_perfect_fifth_60_67": tone([60, 67]),
            "F4_major_triad_60_64_67": tone([60, 64, 67]),
            "F5_constant_pitch_brightness_sweep": sweep()}
    out = {}
    for name, y in stim.items():
        st = tp.stft_power(y)
        c3s = tp.l1(tp.apply_carry_forward(tp.c3_root_salience(st),
                                           native_domain="amplitude", winner="P0_CURRENT"))
        fb = K.fb_log_chroma_from_log(K.log_pitch(K.pitch_energy(y)))
        n = min(len(c3s), len(fb))
        conf = transition_confidence(endpoint_agreement(c3s[:n], fb[:n]))
        mv = tv_movement(c3s[:n])
        mg = gated_movement(mv, conf)
        core = slice(60, n - 8)
        cc, m0, m1 = conf[core], mv[core], mg[core]
        k = np.isfinite(cc) & np.isfinite(m0)
        med0 = float(np.median(m0[k]))
        out[name] = {"median_cross_view_confidence": round(float(np.median(cc[k])), 4),
                     "median_C3_movement": round(med0, 5),
                     "median_gated_movement": round(float(np.median(m1[k])), 5),
                     "attenuation_ratio": round(float(np.median(m1[k]) / med0), 4) if med0 > 0 else None}
    out["_the_question"] = json.loads(PREREG.read_text())["FIXTURES"]["the_question_that_matters"]
    out["_diagnostic_only"] = True
    return out


def score(rs, arm, shift_by=None):
    ev = hit = tol = st_ = fls = 0
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
        ev += int(e.sum()); hit += int((e & det).sum()); tol += int((e & t).sum())
        st_ += int(s.sum()); fls += int((s & (rc >= EV)).sum())
    return {"n_events": ev, "consumer": hit / max(ev, 1), "tol": tol / max(ev, 1),
            "false": fls / max(st_, 1)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--git-head", type=str, default="UNKNOWN")
    args = ap.parse_args()
    prereg = json.loads(PREREG.read_text())
    import yaml
    from scipy.stats import spearmanr

    rows, upstream, conf_rng, atten_ok = [], [], [], []
    for d in sorted(p for p in args.corpus.iterdir() if p.is_dir() and (p / "all_src.mid").is_file()):
        md = yaml.safe_load((d / "metadata.yaml").read_text())
        for f in sorted(p for p in (d / "stems").glob("*.wav") if not p.name.startswith("._")):
            key = f"{d.name}__{f.stem}"
            cf, af, pf = STEMS / f"{key}.npz", AOK / f"{key}.npz", PITCH / f"{key}.npz"
            if not (cf.is_file() and af.is_file() and pf.is_file()):
                continue
            fam = C.family_of(int(md["stems"][f.stem]["program_num"]))
            if fam not in FAMS:
                continue
            z, za = np.load(cf, allow_pickle=False), np.load(af, allow_pickle=False)
            raw = {k: z[f"R_{k}"] for k in C.RAW_KEYS}
            n = raw["PC_POWER"].shape[0]
            c3s = c3_state_of(raw)
            fb = K.fb_log_chroma_from_log(K.log_pitch(np.load(pf)["pitch"][:n].astype(np.float64)))
            m_ = min(len(c3s), len(fb), n)
            c3s, fb = c3s[:m_], fb[:m_]
            agree = endpoint_agreement(c3s, fb)
            conf = transition_confidence(agree)
            mv = tv_movement(c3s)
            mg = gated_movement(mv, conf)
            ok = za["audio_ok"][:m_]
            pair = np.zeros(m_, dtype=bool)
            pair[LAG:] = ok[LAG:] & ok[:-LAG]
            mask = (z["valid"][:m_] & pair & np.isfinite(z["Ms"][:m_])
                    & np.isfinite(mv) & np.isfinite(mg) & np.isfinite(conf))
            if mask.sum() < 400:
                continue
            conf_rng.append((float(conf[mask].min()), float(conf[mask].max())))
            atten_ok.append(bool(np.all(mg[mask] <= mv[mask] + 1e-12)))
            # shared-upstream control: FB_LOG here vs the J3N path (same function, same cache)
            upstream.append(float(np.max(np.abs(
                fb - K.fb_log_chroma_from_log(K.log_pitch(np.load(pf)["pitch"][:m_].astype(np.float64)))))))
            rows.append({"id": f"{d.name}:{f.stem}", "family": fam, "mask": mask,
                         "Ms": z["Ms"][:m_], "conf": conf,
                         "mov": {"C3_ROOT_SALIENCE": mv, "C3_GATED": mg}})

    # ---- controls
    s_id = np.abs(np.random.default_rng(0).normal(size=(64, 12)))
    s_id /= s_id.sum(1, keepdims=True)
    c_id = transition_confidence(endpoint_agreement(s_id, s_id))
    m_id = np.random.default_rng(1).random(64)
    identity_err = float(np.nanmax(np.abs(gated_movement(m_id, c_id) - m_id)))
    lo = min(a for a, _ in conf_rng) if conf_rng else float("nan")
    hi = max(b for _, b in conf_rng) if conf_rng else float("nan")
    controls = {
        "n_stems_scored": len(rows),
        "confidence_in_range_0_1": bool(lo >= 0.0 and hi <= 1.0),
        "confidence_observed_range": [round(lo, 4), round(hi, 4)],
        "gate_is_pure_attenuation": bool(all(atten_ok)),
        "identity_check_max_abs_diff": identity_err,
        "identity_check_pass": bool(identity_err == 0.0),
        "C3_state_never_replaced": True,
        "fb_log_shared_upstream_max_abs_diff": float(np.max(upstream)) if upstream else float("nan"),
        "fb_log_shared_upstream_within_1e_6": bool(upstream and np.max(upstream) <= 1e-6),
        "frame_parity_both_arms": True,
        "nnls_used": False, "crp_used": False, "new_transform": False,
    }
    controls["all_blocking_pass"] = bool(
        controls["n_stems_scored"] >= 20 and controls["confidence_in_range_0_1"]
        and controls["gate_is_pure_attenuation"] and controls["identity_check_pass"]
        and controls["fb_log_shared_upstream_within_1e_6"])

    by = defaultdict(list)
    for r in rows:
        by[r["family"]].append(r)

    rng = np.random.default_rng(SEED)
    fam_out = {}
    for arm in ARMS:
        d_ = {}
        for fname, rs in sorted(by.items()):
            g = np.concatenate([np.full(int(r["mask"].sum()), r["id"]) for r in rs])
            if len(np.unique(g)) < 3:
                continue
            Ms = np.concatenate([r["Ms"][r["mask"]] for r in rs])
            Ma = np.concatenate([r["mov"][arm][r["mask"]] for r in rs])
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
                    [np.median(r["mov"][arm][r["mask"]]) for r in rs])), 5),
                "median_confidence": round(float(np.median(
                    [np.median(r["conf"][r["mask"]]) for r in rs])), 4),
                "null_recall_mean_REPORTED_NOT_GATED": round(float(np.mean(nulls)), 4),
                "recall_above_own_null_REPORTED_NOT_GATED": round(s["tol"] - float(np.mean(nulls)), 4),
            }
        fam_out[arm] = d_

    base, gate = fam_out["C3_ROOT_SALIENCE"], fam_out["C3_GATED"]
    decision = {}
    for fam in PRIMARY:
        if fam not in base or fam not in gate:
            continue
        drop = round(base[fam]["event_recall_event_tolerant"] - gate[fam]["event_recall_event_tolerant"], 4)
        red = round(base[fam]["false_movement_in_stable_periods"] - gate[fam]["false_movement_in_stable_periods"], 4)
        decision[fam] = {
            "recall_drop_vs_C3": drop, "recall_guard_satisfied": bool(drop <= RECALL_GUARD),
            "false_movement_reduction_vs_C3": red, "reduces_false_movement": bool(red > 0.0),
            "clears": bool(drop <= RECALL_GUARD and red > 0.0)}
    both_primaries_clear = bool(decision and all(v["clears"] for v in decision.values())
                                and set(decision) == set(PRIMARY))

    # ---- ANALYST-ADDED REPORTED DIAGNOSTIC (not pre-registered, not a gate).
    # Where does the confidence signal actually sit? A gate is only useful if
    # confidence is LOWER at contaminated frames than at genuine harmonic events.
    mech = {}
    for fname, rs in sorted(by.items()):
        ev_c, st_c, ratios = [], [], []
        for r in rs:
            m = r["mask"]
            rs_ = rank(r["Ms"][m])
            c = r["conf"][m]
            e, st = rs_ >= EV, rs_ <= STB
            if e.sum() < 10 or st.sum() < 10:
                continue
            ev_c.append(float(np.median(c[e]))); st_c.append(float(np.median(c[st])))
            mv_, mg_ = r["mov"]["C3_ROOT_SALIENCE"][m], r["mov"]["C3_GATED"][m]
            k = mv_ > 0
            if k.sum() > 10:
                ratios.append(float(np.median(mg_[k] / mv_[k])))
        if not ev_c:
            continue
        a, b = float(np.median(ev_c)), float(np.median(st_c))
        mech[fname] = {
            "median_confidence_at_oracle_EVENT_frames": round(a, 4),
            "median_confidence_at_oracle_STABLE_frames": round(b, 4),
            "event_minus_stable": round(a - b, 4),
            "gate_favours_genuine_events": bool(a > b),
            "median_attenuation_ratio": round(float(np.median(ratios)), 4) if ratios else None,
        }

    conf_by_fam = {f: gate[f]["median_confidence"] for f in gate}
    chrom = {
        "median_confidence": conf_by_fam.get("chromatic_percussion"),
        "median_confidence_piano_keys": conf_by_fam.get("piano_keys"),
        "median_confidence_bass": conf_by_fam.get("bass"),
        "substantially_lower_than_both_strong_controls": bool(
            conf_by_fam.get("chromatic_percussion") is not None
            and all(conf_by_fam.get("chromatic_percussion") < conf_by_fam.get(k, 0) - 0.10
                    for k in ("piano_keys", "bass") if conf_by_fam.get(k) is not None)),
        "how_it_must_not_be_read": prereg["CHROMATIC_PERCUSSION"]["how_it_must_NOT_be_read"],
        "no_win_required": True}

    receipt = {
        "schema": "spectrasynq.cross_view_reliability_result.v1", "job": "J3P",
        "git_head": args.git_head,
        "label": "CROSS-VIEW RELIABILITY GATE. HOST information probe on consumed data. Nothing promotable.",
        "preregistration": str(PREREG.relative_to(C.ROOT)),
        "the_one_confidence_signal": prereg["THE_ONE_CONFIDENCE_SIGNAL"],
        "roles": prereg["roles_which_must_not_be_confused"],
        "causality_disclosure": prereg["inputs"]["causality_disclosure"],
        "execution_environment": "Anthropic cloud container (HOST-class). BabySlakh 16 kHz, md5 verified against the publisher's checksum.",
        "controls": controls,
        "fixtures": fixtures(),
        "family_metrics": fam_out,
        "primary_family_decision": decision,
        "both_primary_families_clear": both_primaries_clear,
        "recall_guard": {"rule": prereg["RECALL_GUARD"]["rule"], "threshold": RECALL_GUARD},
        "chance_floor": {"method": prereg["CHANCE_FLOOR_NOW_STANDING_PROGRAMME_PRACTICE"]["method"],
                         "n_permutations": N_PERM, "seed": SEED, "REPORTED_NOT_GATED": True},
        "chromatic_percussion_diagnostic": chrom,
        "WHERE_THE_CONFIDENCE_SITS_ANALYST_ADDED_REPORTED_NOT_GATED": {
            "status": ("added by the analyst AFTER the family metrics were seen. REPORTED, NOT GATED - "
                       "it changed no outcome. It exists because a reliability gate is only useful if "
                       "confidence is LOWER where movement is contaminated than where events are genuine."),
            "by_family": mech},
        "conditional_visual_test": {"trigger_met": both_primaries_clear, "run": False,
                                    "note": "run separately by scripts/j3p_visual.py only if the trigger is met"},
        "outcome": ("CROSS_VIEW_RELIABILITY_INCONCLUSIVE" if not controls["all_blocking_pass"]
                    else ("PENDING_VISUAL" if both_primaries_clear else "CROSS_VIEW_RELIABILITY_FAIL")),
        "J3O_mutated": False, "J3N_mutated": False, "J3M_mutated": False, "target_modified": False,
        "new_representation": False, "new_blocking_gate_added": False, "threshold_tuned": False,
        "nnls_run": False, "crp_run": False, "cqt_run": False, "basic_pitch_run": False,
        "source_separator_run": False, "neural_model": False, "visual_grammar_modified": False,
        "production_firmware_changed": False, "titan": False, "student_io_frozen": False,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(receipt, indent=2, sort_keys=False) + "\n")
    print(json.dumps({"outcome": receipt["outcome"], "controls": controls,
                      "decision": decision, "fixtures": receipt["fixtures"],
                      "chrom": chrom}, indent=2))
    print(f"receipt -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
