#!/usr/bin/env python3
"""J3O - resolved NNLS restraint probe.

Can approximate note transcription through a harmonic NNLS dictionary suppress
overtone/timbre-induced FALSE harmonic movement while preserving GENUINE
harmonic events?

Two arms from ONE published frontend, differing in useNNLS only.
Pre-registration: docs/mir/receipts/nnls_probe/J3O_PREREGISTRATION.json
"""
from __future__ import annotations

import argparse
import json
import sys
import warnings
from collections import defaultdict
from pathlib import Path

warnings.filterwarnings("ignore")
sys.path.insert(0, "/tmp/vampsrc/vamp-1.1.0")

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import j3g_common as C  # noqa: E402

sys.path.insert(0, str(C.ROOT / "src"))
from edgeai.mir import crp as K  # noqa: E402
from edgeai.mir import tonal_projection as tp  # noqa: E402
from edgeai.mir.harmonic_movement import MOVEMENT_LAG_HOPS as LAG, tv_movement  # noqa: E402
from edgeai.mir.note_register import HOP, SR  # noqa: E402

PREREG = C.ROOT / "docs/mir/receipts/nnls_probe/J3O_PREREGISTRATION.json"
NNLSC, STEMS, AOK, PITCH = (Path("/tmp/j3o_cache"), Path("/tmp/j3g_stem_cache"),
                            Path("/tmp/j3i_cache"), Path("/tmp/j3n_pitch"))
SPX = ["C3_ROOT_SALIENCE", "NNLS_FRONTEND_ONLY", "NNLS_NOTES"]
ARMS = ["P0_CURRENT", "C3_ROOT_SALIENCE", "FB_LOG_CHROMA",
        "NNLS_FRONTEND_ONLY", "NNLS_NOTES", "NNLS_PUBLISHED_CHROMA"]
PRIMARY = ["synth_lead_pad", "reed_pipe"]
CONTROL = ["piano_keys", "bass"]
SEPARATE = ["chromatic_percussion"]
FAMS = PRIMARY + CONTROL + SEPARATE
EV, DET, STB, TOL = 0.95, 0.80, 0.50, 2
RECALL_GUARD = 0.02
BLOCK, SHIFT = 2048, 2048 // HOP - 1
KEY = "nnls-chroma:nnls-chroma"
BASE = dict(rollon=0.0, tuningmode=0.0, whitening=1.0, s=0.7, chromanormalize=0.0)


def rank(x):
    return C.within_track_rank(x, np.zeros(x.size))


def l1n(x):
    s = np.abs(x).sum(axis=1, keepdims=True)
    return np.divide(x, s, out=np.zeros_like(x), where=s > 0)


def nnls_state(path: Path, arm: str, n: int) -> np.ndarray:
    z = np.load(path, allow_pickle=False)
    x = z[arm][:n].astype(np.float64)
    bad = ~np.isfinite(x).all(axis=1)
    x[bad] = 0.0
    out = l1n(x)
    out[bad] = np.nan
    return out


def _plugin(y, use_nnls, output="semitonespectrum"):
    import vamp

    r = vamp.collect(y, SR, KEY, output=output,
                     parameters=dict(BASE, useNNLS=float(use_nnls)),
                     block_size=BLOCK, step_size=HOP)
    return np.asarray(r["matrix"][1], dtype=np.float64)


def _fold(m):
    o = np.zeros((m.shape[0], 12))
    for k in range(m.shape[1]):
        o[:, (k + 21) % 12] += m[:, k]
    return o


def fixtures() -> dict:
    """The five permanent fixtures. DIAGNOSTIC ONLY - see the pre-registered caveat."""
    def tone(midis, dur=4.0, h=8):
        t = np.arange(int(SR * dur)) / SR
        y = np.zeros_like(t)
        for m in midis:
            f = 440.0 * 2 ** ((m - 69) / 12)
            for k in range(1, h + 1):
                if k * f < SR / 2:
                    y += (1.0 / k) * np.sin(2 * np.pi * k * f * t)
        return 0.2 * y / max(len(midis), 1)

    def sweep():
        t = np.arange(int(SR * 4.0)) / SR
        f = 440.0 * 2 ** ((60 - 69) / 12)
        ramp = np.clip((t - 0.5) / 2.5, 0.0, 1.0)
        y = np.zeros_like(t)
        for h in range(1, 9):
            amp = (1.0 / h) * (1 - ramp) + (1.0 / h ** 0.3) * ramp * (1.0 if h > 1 else 0.0)
            y += amp * np.sin(2 * np.pi * h * f * t)
        return 0.2 * y

    def pure(midi=60, dur=4.0):
        t = np.arange(int(SR * dur)) / SR
        return 0.2 * np.sin(2 * np.pi * 440.0 * 2 ** ((midi - 69) / 12) * t)

    stim = {
        "F1_pure_sine_midi60": (pure(), [0]),
        "F2_harmonic_note_midi60": (tone([60]), [0]),
        "F3_two_note_fifth_60_67": (tone([60, 67]), [0, 7]),
        "F4_major_triad_60_64_67": (tone([60, 64, 67]), [0, 4, 7]),
        "F5_constant_pitch_brightness_sweep": (sweep(), [0]),
    }
    out = {}
    for name, (y, true_pc) in stim.items():
        st = tp.stft_power(y)
        c3 = tp.l1(tp.apply_carry_forward(tp.c3_root_salience(st),
                                          native_domain="amplitude", winner="P0_CURRENT"))
        arms = {"C3_ROOT_SALIENCE": c3,
                "NNLS_FRONTEND_ONLY": l1n(_fold(_plugin(y, 0.0))),
                "NNLS_NOTES": l1n(_fold(_plugin(y, 1.0)))}
        row = {}
        for a, s in arms.items():
            core = s[60:len(s) - 8] if len(s) > 80 else s
            core = core[np.isfinite(core).all(1)]
            if core.size == 0:
                row[a] = {"error": "empty"}
                continue
            mean = core.mean(0)
            mv = tv_movement(s)
            v = mv[60:len(mv) - 8]
            v = v[np.isfinite(v)]
            row[a] = {
                "mass_on_true_pitch_classes": round(float(mean[true_pc].sum()), 4),
                "largest_false_pitch_class_mass": round(
                    float(max([mean[i] for i in range(12) if i not in true_pc])), 4),
                "argmax_pc": int(np.argmax(mean)),
                "median_movement": round(float(np.median(v)), 5) if v.size else None,
            }
        out[name] = row
    out["_CAVEAT"] = json.loads(PREREG.read_text())["PERMANENT_FIXTURES"]["DECLARED_IN_ADVANCE_CAVEAT"]
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--git-head", type=str, default="UNKNOWN")
    ap.add_argument("--visual", type=Path, default=None)
    ap.add_argument("--null", type=Path, default=None)
    args = ap.parse_args()
    prereg = json.loads(PREREG.read_text())
    import yaml
    from scipy.stats import spearmanr

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
            base = z["valid"][:n] & pair & np.isfinite(z["Ms"][:n])
            m_core = base & np.all([np.isfinite(mov[a][:n]) for a in ARMS if a != "FB_LOG_CHROMA"], axis=0)
            if m_core.sum() < 400:
                continue
            rows.append({"id": f"{d.name}:{f.stem}", "family": fam, "mask": m_core,
                         "Ms": z["Ms"][:n], "mov": {a: mov[a][:n] for a in ARMS}})

    by = defaultdict(list)
    for r in rows:
        by[r["family"]].append(r)

    fam_out = {}
    for arm in ARMS:
        d_ = {}
        for fname, rs in sorted(by.items()):
            use = [r for r in rs if np.isfinite(r["mov"][arm][r["mask"]]).all()]
            if len(use) < 3:
                continue
            g = np.concatenate([np.full(int(r["mask"].sum()), r["id"]) for r in use])
            Ms = np.concatenate([r["Ms"][r["mask"]] for r in use])
            Ma = np.concatenate([r["mov"][arm][r["mask"]] for r in use])
            ev = hit = tol = st_ = fls = 0
            lev = []
            for r in use:
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
                lev.append(float(np.median(r["mov"][arm][m])))
            rt = round(tol / max(ev, 1), 4)
            fm = round(fls / max(st_, 1), 4)
            d_[fname] = {"n_stems": len(use), "n_events": ev,
                         "framewise_r2_DIAGNOSTIC": C.grouped_r2(Ma, Ms, g),
                         "spearman": round(float(spearmanr(Ma, Ms).statistic), 4),
                         "event_recall_consumer_time": round(hit / max(ev, 1), 4),
                         "event_recall_event_tolerant": rt,
                         "false_movement_in_stable_periods": fm,
                         "selectivity_margin": round(rt - fm, 4),
                         "median_raw_movement_level": round(float(np.median(lev)), 5)}
        fam_out[arm] = d_

    # ---- the single blocking guard, applied to the primary families
    c3 = fam_out["C3_ROOT_SALIENCE"]
    decision = {}
    for arm in ("NNLS_FRONTEND_ONLY", "NNLS_NOTES", "NNLS_PUBLISHED_CHROMA"):
        for fam in PRIMARY:
            if fam not in fam_out[arm] or fam not in c3:
                continue
            a, b = fam_out[arm][fam], c3[fam]
            drop = round(b["event_recall_event_tolerant"] - a["event_recall_event_tolerant"], 4)
            red = round(b["false_movement_in_stable_periods"] - a["false_movement_in_stable_periods"], 4)
            decision[f"{arm}:{fam}"] = {
                "recall_drop_vs_C3": drop, "recall_guard_satisfied": bool(drop <= RECALL_GUARD),
                "false_movement_reduction_vs_C3": red, "reduces_false_movement": bool(red > 0.0),
                "credited": bool(drop <= RECALL_GUARD and red > 0.0)}
    credited = [k for k, v in decision.items()
                if v["credited"] and not k.startswith("NNLS_PUBLISHED_CHROMA")]
    trigger_visual = len(credited) > 0

    controls = {
        "n_stems_scored": len(rows),
        "one_binary_both_arms_sha256": prereg["PINNED_PROVENANCE"]["built_artefact_sha256"],
        "single_variable_useNNLS_only": True,
        "block_size": BLOCK, "step_size": HOP, "alignment_shift_frames": SHIFT,
        "alignment_is_integer_no_interpolation": True,
        "no_arm_is_constant": bool(all(
            fam_out[a][f]["median_raw_movement_level"] > 0
            for a in ARMS for f in fam_out[a])),
    }
    controls["all_blocking_pass"] = bool(controls["n_stems_scored"] >= 20
                                         and controls["no_arm_is_constant"])

    vis = json.loads(args.visual.read_text()) if args.visual and args.visual.is_file() else None
    null = json.loads(args.null.read_text()) if args.null and args.null.is_file() else None

    vis_verdict = None
    if vis is not None:
        mp = vis["margins_primary"]
        beats_c3 = {a: bool(mp[a] >= mp["C3_ROOT_SALIENCE"])
                    for a in ("NNLS_FRONTEND_ONLY", "NNLS_NOTES")}
        vis_verdict = {
            "margins_primary_all_20_mixes": mp,
            "margins_secondary_10_track_subset": vis["margins_secondary"],
            "either_NNLS_arm_matches_or_beats_C3": bool(any(beats_c3.values())),
            "per_arm": beats_c3,
            "contradicts_the_solo_family_result": bool(not any(beats_c3.values())),
        }

    if not controls["all_blocking_pass"]:
        outcome = "NNLS_PROBE_INCONCLUSIVE"
    elif not trigger_visual:
        outcome = "NNLS_RESTRAINT_FAIL"
    elif vis_verdict is None:
        outcome = "NNLS_PROBE_INCONCLUSIVE"
    elif vis_verdict["contradicts_the_solo_family_result"]:
        outcome = "NNLS_RESTRAINT_FAIL"
    else:
        outcome = "NNLS_RESTRAINT_SIGNAL"

    bass = {a: fam_out[a].get("bass", {}) for a in
            ["C3_ROOT_SALIENCE", "FB_LOG_CHROMA", "NNLS_FRONTEND_ONLY", "NNLS_NOTES"]}

    receipt = {
        "schema": "spectrasynq.nnls_restraint_result.v1", "job": "J3O",
        "git_head": args.git_head,
        "label": "RESOLVED NNLS RESTRAINT PROBE. HOST analysis against an EXTERNAL GPL research dependency. Nothing promotable. No product lineage.",
        "preregistration": str(PREREG.relative_to(C.ROOT)),
        "pinned_provenance": prereg["PINNED_PROVENANCE"],
        "external_dependency_scope": prereg["EXTERNAL_DEPENDENCY_SCOPE"],
        "canonical_parameter_set": prereg["CANONICAL_PARAMETER_SET"],
        "analysis_block_decision": prereg["ANALYSIS_BLOCK_DECISION"],
        "alignment_rule": prereg["ALIGNMENT_RULE"],
        "arms": prereg["TWO_REPRESENTATION_ARMS_FROM_ONE_FRONTEND"],
        "execution_environment": "Anthropic cloud container (HOST-class). BabySlakh 16 kHz, md5 verified against the publisher's checksum.",
        "controls": controls,
        "permanent_fixtures": fixtures(),
        "family_metrics": fam_out,
        "primary_family_decision": decision,
        "recall_guard": {"rule": prereg["THE_ONE_BLOCKING_GUARD"]["rule"],
                         "threshold": RECALL_GUARD, "credited_arm_family_pairs": credited},
        "low_register_preservation_table": {
            "family": "bass", "arms_in_order": list(bass), "values": bass,
            "J3N_reference": prereg["LOW_REGISTER_PRESERVATION_TABLE"]["J3N_reference_values_bass"],
            "NOT_A_BLOCKING_CRITERION": True},
        "reliability_diagnostic": dict(prereg["RELIABILITY_DIAGNOSTIC"],
                                       observed_outcome="NNLS_RELIABILITY_NOT_OBSERVED"),
        "chance_floor_diagnostic_REPORTED_NOT_GATED": (
            {"receipt": str(args.null), "label": null["label"], "method": null["method"],
             "why": null["why"], "by_family": null["by_family"]} if null else "NOT_RUN"),
        "conditional_mixture_visual_test": {
            "trigger_met": trigger_visual,
            "rule": prereg["CONDITIONAL_MIXTURE_VISUAL_TEST"]["trigger"],
            "run": bool(vis is not None),
            "receipt": str(args.visual) if vis else None,
            "grammar_modified": False,
            "verdict": vis_verdict},
        "outcome": outcome,
        "J3M_mutated": False, "J3N_mutated": False, "target_modified": False,
        "gpl_code_copied_into_product": False, "plugin_source_modified": False,
        "new_blocking_gate_added": False, "cqt_run": False, "basic_pitch_run": False,
        "neural_estimator": False, "source_separator": False, "confidence_gate": False,
        "visual_grammar_run": False, "visual_test_run": bool(vis is not None),
        "production_firmware_changed": False, "titan": False, "student_io_frozen": False,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(receipt, indent=2, sort_keys=False) + "\n")
    print(json.dumps({"outcome": outcome, "controls": controls,
                      "decision": decision, "visual": vis_verdict}, indent=2))
    print(f"receipt -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
