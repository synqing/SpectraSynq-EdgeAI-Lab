#!/usr/bin/env python3
"""J3K - mixture-level acoustic-activation target. The final fair test of the
target-timing hypothesis.

per-instrument raw MIDI pitch-class mass -> family-specific cross-fitted attack
weighting -> sum all tonal instruments -> L1-normalise ONCE at mixture level.

Pre-registration: docs/mir/receipts/mixture_activation/J3K_PREREGISTRATION.json
"""
from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import j3g_common as C  # noqa: E402

sys.path.insert(0, str(C.ROOT / "src"))
from edgeai.mir import acoustic_activation as AA  # noqa: E402
from edgeai.mir import tonal_projection as tp  # noqa: E402
from edgeai.mir.harmonic_movement import (  # noqa: E402
    MOVEMENT_LAG_HOPS, is_tonal_instrument, l1_rows, pitch_class_state, tv_movement,
)
from edgeai.mir.note_register import Note  # noqa: E402

LAG = MOVEMENT_LAG_HOPS
PREREG = C.ROOT / "docs/mir/receipts/mixture_activation/J3K_PREREGISTRATION.json"
CURVES = Path("/tmp/j3j_curves.npz")
SIDE_C5 = Path("/tmp/j3g2_cache")
PRIMARY = ["P0_CURRENT", "C3_ROOT_SALIENCE"]
ALL = PRIMARY + ["C2_PEAK_HPCP", "C5_PEAK_ROOT_HYBRID"]
EVENT_RANK, DETECT_RANK, STABLE_RANK, TOL = 0.95, 0.80, 0.50, 2


def rank(x: np.ndarray) -> np.ndarray:
    return C.within_track_rank(x, np.zeros(x.size))


def build(corpus: Path, kb: AA.KernelBank) -> list[dict]:
    import pretty_midi
    out = []
    for d in sorted(p for p in corpus.iterdir() if p.is_dir() and (p / "all_src.mid").is_file()):
        b = C.cached_track(d)
        n = b["n"]
        c5 = np.load(SIDE_C5 / f"track__{d.name}.npz")["C5"][:n]
        b["states"]["C5_PEAK_ROOT_HYBRID"] = tp.l1(tp.apply_carry_forward(
            c5, native_domain="amplitude", winner="P0_CURRENT"))
        b["mov"]["C5_PEAK_ROOT_HYBRID"] = tv_movement(b["states"]["C5_PEAK_ROOT_HYBRID"])

        pm = pretty_midi.PrettyMIDI(str(d / "all_src.mid"))
        rect = np.zeros((n, 12)); act = np.zeros((n, 12))
        wr = np.zeros(n); wa = np.zeros(n)
        fam_active = np.zeros((n, 0), dtype=bool)
        fam_cols, kern_use = [], {}
        for inst in pm.instruments:
            if not is_tonal_instrument(inst.is_drum, inst.program):
                continue
            notes = [Note(float(x.start), float(x.end), int(x.pitch), int(x.velocity)) for x in inst.notes]
            if not notes:
                continue
            fam = C.family_of(int(inst.program))
            kern, meta = kb.for_stem(fam, d.name)
            kern_use.setdefault(fam, meta["level"])
            r = pitch_class_state(notes, n)
            a = AA.acoustic_activation_state(notes, n, kern)
            rect += r["pc_mass"]; act += a["pc_mass"]
            wr += r["weight_total"]; wa += a["weight_total"]
            fam_cols.append((fam, r["weight_total"] > 0.0, AA.box_filtered(kern)))
        if not fam_cols:
            continue
        if fam_cols:
            fam_active = np.column_stack([c[1] for c in fam_cols])
        M_old = tv_movement(rect)
        M_new = tv_movement(act)
        m = b["valid"][:n] & np.isfinite(M_old) & np.isfinite(M_new)
        m &= np.all([np.isfinite(v[:n]) for k, v in b["mov"].items() if not k.startswith("_")], axis=0)
        fam_names = np.array([c[0] for c in fam_cols])
        n_fams = np.array([len(set(fam_names[row])) for row in fam_active])
        out.append({"track": d.name, "n": n, "mask": m,
                    "M_old": M_old, "M_new": M_new,
                    "M_cached_oracle": b["M_oracle"][:n],
                    "state_old": l1_rows(rect), "state_new": l1_rows(act),
                    "mov": {k: v[:n] for k, v in b["mov"].items() if not k.startswith("_")},
                    "n_families_per_frame": n_fams, "kernel_levels": kern_use,
                    "n_tonal_instruments": len(fam_cols)})
    return out


def pooled(rows, key):
    return np.concatenate([r[key][r["mask"]] for r in rows])


def metrics(rows, target_key: str) -> dict:
    from scipy.stats import spearmanr
    g = np.concatenate([np.full(int(r["mask"].sum()), r["track"]) for r in rows])
    Ms = pooled(rows, target_key)
    out = {}
    for name in ALL:
        Ma = np.concatenate([r["mov"][name][r["mask"]] for r in rows])
        ev = hit = tol = st = fls = 0
        cls_hit = {k: [0, 0] for k in ("HARMONIC_CHANGE_FLAT_ENERGY", "HARMONIC_CHANGE_NO_ONSET")}
        for r in rows:
            m = r["mask"]
            idx = np.nonzero(m)[0]
            rs_, rc = rank(r[target_key][m]), rank(r["mov"][name][m])
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
        out[name] = {"framewise_r2_DIAGNOSTIC": C.grouped_r2(Ma, Ms, g),
                     "spearman": round(float(spearmanr(Ma, Ms).statistic), 4),
                     "n_events": ev,
                     "event_recall_consumer_time": round(hit / max(ev, 1), 4),
                     "event_recall_event_tolerant": round(tol / max(ev, 1), 4),
                     "false_movement_in_target_stable_periods": round(fls / max(st, 1), 4)}
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--git-head", type=str, default="UNKNOWN")
    args = ap.parse_args()
    prereg = json.loads(PREREG.read_text())

    ident_notes = [Note(0.5, 2.0, 60, 80), Note(1.0, 2.5, 64, 90), Note(3.0, 4.0, 67, 70)]
    ident = float(np.max(np.abs(
        AA.acoustic_activation_state(ident_notes, 200, np.ones(AA.K_MAX_HOPS + 1))["pc_mass"]
        - pitch_class_state(ident_notes, 200)["pc_mass"])))
    tree = ast.parse((C.ROOT / "src/edgeai/mir/acoustic_activation.py").read_text())
    mods = set()
    for nd in ast.walk(tree):
        if isinstance(nd, ast.Import):
            mods.update(a.name for a in nd.names)
        elif isinstance(nd, ast.ImportFrom):
            mods.add(nd.module or "")
    indep = not any(b in m for m in mods
                    for b in ("tonal_projection", "host_chroma", "chroma_power", "harmonic_visual"))

    z = np.load(CURVES)
    kb = AA.KernelBank([{"track": str(t), "family": str(f), "curve": c}
                        for t, f, c in zip(z["tracks"], z["families"], z["curves"])])
    rows = build(args.corpus, kb)

    old_arm_err = max(float(np.max(np.abs(r["M_old"][r["mask"]] - r["M_cached_oracle"][r["mask"]])))
                      for r in rows)
    controls = {
        "identity_kernel_reproduces_pitch_class_state": ident,
        "identity_kernel_ok": bool(ident == 0.0),
        "old_arm_reproduces_published_oracle_max_abs_diff": old_arm_err,
        "old_arm_ok": bool(old_arm_err <= 1e-9),
        "target_module_imports_no_representation": indep,
        "identical_frame_set_for_both_targets": True,
        "n_tracks": len(rows), "n_frames": int(sum(int(r["mask"].sum()) for r in rows)),
    }
    controls["all_blocking_pass"] = bool(controls["identity_kernel_ok"] and controls["old_arm_ok"] and indep)

    # ---- primary evidence: does the normalised mixture state change at all ----
    med, mean, p90, frac = [], [], [], []
    for r in rows:
        d = 0.5 * np.abs(r["state_new"][r["mask"]] - r["state_old"][r["mask"]]).sum(axis=1)
        med.append(float(np.median(d))); mean.append(float(d.mean()))
        p90.append(float(np.percentile(d, 90))); frac.append(float((d > 1e-9).mean()))
    state = {"median": round(float(np.median(med)), 5), "mean": round(float(np.median(mean)), 5),
             "p90": round(float(np.median(p90)), 5),
             "fraction_of_frames_that_differ_at_all": round(float(np.median(frac)), 4),
             "per_track_fraction_min": round(float(np.min(frac)), 4),
             "per_track_fraction_max": round(float(np.max(frac)), 4),
             "J3J_solo_reference": {"median": 0.0, "fraction_range": [0.0706, 0.1647]}}

    nf = np.concatenate([r["n_families_per_frame"][r["mask"]] for r in rows])
    poly = {"mean_distinct_tonal_families_active_per_frame": round(float(nf.mean()), 3),
            "fraction_of_frames_with_2_or_more_families": round(float((nf >= 2).mean()), 4),
            "fraction_of_frames_with_3_or_more_families": round(float((nf >= 3).mean()), 4),
            "mean_tonal_instruments_per_track": round(float(np.mean([r["n_tonal_instruments"] for r in rows])), 2)}

    old = metrics(rows, "M_old")
    new = metrics(rows, "M_new")
    delta = {k: {"framewise_r2_change_DIAGNOSTIC": round(new[k]["framewise_r2_DIAGNOSTIC"] - old[k]["framewise_r2_DIAGNOSTIC"], 4),
                 "event_tolerant_recall_old": old[k]["event_recall_event_tolerant"],
                 "event_tolerant_recall_new": new[k]["event_recall_event_tolerant"],
                 "event_tolerant_recall_change": round(new[k]["event_recall_event_tolerant"] - old[k]["event_recall_event_tolerant"], 4),
                 "consumer_time_recall_change": round(new[k]["event_recall_consumer_time"] - old[k]["event_recall_consumer_time"], 4),
                 "false_movement_old": old[k]["false_movement_in_target_stable_periods"],
                 "false_movement_new": new[k]["false_movement_in_target_stable_periods"],
                 "false_movement_change": round(new[k]["false_movement_in_target_stable_periods"] - old[k]["false_movement_in_target_stable_periods"], 4)}
             for k in ALL}

    p = delta["P0_CURRENT"]
    material = bool(abs(p["event_tolerant_recall_change"]) >= 0.10 or abs(p["false_movement_change"]) >= 0.10)
    if not controls["all_blocking_pass"]:
        outcome = "MIXTURE_TARGET_REPAIR_INCONCLUSIVE"
    elif material:
        outcome = "MIXTURE_TARGET_CORRECTION_MATERIAL"
    else:
        outcome = "MIXTURE_TARGET_CORRECTION_IMMATERIAL"

    receipt = {
        "schema": "spectrasynq.mixture_activation_result.v1", "job": "J3K",
        "git_head": args.git_head,
        "label": "MIXTURE-LEVEL TARGET REPAIR - representation-independent by construction. BabySlakh tracks remain consumed; nothing here is promotable.",
        "brief_provenance": prereg["BRIEF_PROVENANCE_DISCLOSURE"],
        "preregistration": str(PREREG.relative_to(C.ROOT)),
        "execution_environment": "Anthropic cloud container (HOST-class). BabySlakh 16 kHz, md5 verified against the publisher's checksum.",
        "controls": controls,
        "PRIMARY_EVIDENCE_state_level_change": state,
        "REPORTED_DIAGNOSTIC_polyphony_structure": poly,
        "kernel_levels_used_by_family": {r["track"]: r["kernel_levels"] for r in rows[:3]},
        "targets": {"old": "RECTANGULAR_MIXTURE_PC", "new": "ACOUSTIC_ACTIVATION_MIXTURE_PC"},
        "metrics_RECTANGULAR_MIXTURE_PC": old,
        "metrics_ACOUSTIC_ACTIVATION_MIXTURE_PC": new,
        "delta": delta,
        "decision": {"judged_on": "P0_CURRENT", "materiality_scale": 0.10,
                     "event_tolerant_recall_change": p["event_tolerant_recall_change"],
                     "false_movement_change": p["false_movement_change"], "material": material},
        "outcome": outcome,
        "J3J_mutated": False, "J3I_mutated": False, "J3G_mutated": False,
        "J3G2_mutated": False, "J3F_mutated": False,
        "new_tonal_representation": False, "cqt_run": False, "crp_repair": False, "nnls_run": False,
        "basic_pitch_run": False, "neural_model": False,
        "midi_pitch_or_identity_altered": False, "release_model_created": False, "velocity_weighting": False,
        "production_firmware_changed": False, "titan": False, "student_io_frozen": False,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(receipt, indent=2, sort_keys=False) + "\n")
    print(json.dumps({"outcome": outcome, "controls": controls, "state": state,
                      "polyphony": poly, "delta": delta}, indent=2))
    print(f"receipt -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
