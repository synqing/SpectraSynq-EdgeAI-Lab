#!/usr/bin/env python3
"""J3J - repair the TARGET only, then rerun the existing representations.

No new representation. No tonal candidate. No visual grammar. No CQT/CRP/NNLS.
The target is representation-independent by construction.

Pre-registration: docs/mir/receipts/acoustic_activation/J3J_PREREGISTRATION.json
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
from edgeai.mir import acoustic_activation as AA  # noqa: E402
from edgeai.mir import tonal_projection as tp  # noqa: E402
from edgeai.mir.harmonic_movement import MOVEMENT_LAG_HOPS, pitch_class_state, tv_movement  # noqa: E402
from edgeai.mir.note_register import Note, frame_grid  # noqa: E402

LAG = MOVEMENT_LAG_HOPS
PREREG = C.ROOT / "docs/mir/receipts/acoustic_activation/J3J_PREREGISTRATION.json"
STEMS, SIDE_C5, SIDE_A = Path("/tmp/j3g_stem_cache"), Path("/tmp/j3g2_cache"), Path("/tmp/j3i_cache")
CURVES = Path("/tmp/j3j_curves.npz")
PRIMARY = ["P0_CURRENT", "C3_ROOT_SALIENCE"]
ALL = PRIMARY + ["C2_PEAK_HPCP", "C5_PEAK_ROOT_HYBRID"]
WEAK = ["synth_lead_pad", "reed_pipe", "ensemble_voice", "chromatic_percussion"]
REPORTED = ["piano_keys", "guitar", "bass", "ensemble_voice", "reed_pipe",
            "synth_lead_pad", "chromatic_percussion"]
EVENT_RANK, DETECT_RANK, STABLE_RANK, TOL = 0.95, 0.80, 0.50, 2


def rank(x: np.ndarray) -> np.ndarray:
    return C.within_track_rank(x, np.zeros(x.size))


def build(corpus: Path, kb: AA.KernelBank) -> list[dict]:
    import pretty_midi
    rows = []
    for d in sorted(p for p in corpus.iterdir() if p.is_dir() and (p / "all_src.mid").is_file()):
        md = yaml.safe_load((d / "metadata.yaml").read_text())
        for f in sorted(p for p in (d / "stems").glob("*.wav") if not p.name.startswith("._")):
            cf, c5f, af = (STEMS / f"{d.name}__{f.stem}.npz", SIDE_C5 / f"stem__{d.name}__{f.stem}.npz",
                           SIDE_A / f"{d.name}__{f.stem}.npz")
            mf = d / "MIDI" / f"{f.stem}.mid"
            if not (cf.is_file() and c5f.is_file() and af.is_file() and mf.is_file()):
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
            fam = C.family_of(int(za["program"]))
            try:
                pm = pretty_midi.PrettyMIDI(str(mf))
            except Exception:  # noqa: BLE001
                continue
            notes = [Note(float(x.start), float(x.end), int(x.pitch), int(x.velocity))
                     for i in pm.instruments for x in i.notes]
            if len(notes) < 50:
                continue
            kern, meta = kb.for_stem(fam, d.name)
            new = AA.acoustic_activation_state(notes, n, kern)
            old = pitch_class_state(notes, n)
            m = z["valid"][:n] & pair & np.isfinite(z["Ms"][:n])
            Msn = tv_movement(new["pc_mass"])
            m = m & np.isfinite(Msn) & np.all([np.isfinite(tv_movement(v)) for v in st.values()], axis=0)
            if m.sum() < 400:
                continue
            from edgeai.mir.harmonic_movement import l1_rows as _l1r
            rows.append({"id": f"{d.name}:{f.stem}", "track": d.name, "family": fam, "mask": m,
                         "state_old_l1": _l1r(old["pc_mass"]), "state_new_l1": _l1r(new["pc_mass"]),
                         "Ms_old": z["Ms"][:n], "Ms_new": Msn, "kernel_meta": meta,
                         "silent_old": int(old["silent"].sum()), "silent_new": int(new["silent"].sum()),
                         "mov": {k: tv_movement(v) for k, v in st.items()}})
    return rows


def target_effect(rows: list[dict]) -> dict:
    from scipy.stats import pearsonr, spearmanr
    by = defaultdict(list)
    for r in rows:
        by[r["family"]].append(r)
    out = {}
    for fam, rs in sorted(by.items()):
        po, pn, disp, added, removed, agree, ev_o, l1d = [], [], [], 0, 0, [], 0, []
        for r in rs:
            m = r["mask"]
            a, b = r["Ms_old"][m], r["Ms_new"][m]
            if a.size < 50:
                continue
            pr, sp = float(pearsonr(a, b).statistic), float(spearmanr(a, b).statistic)
            if np.isfinite(pr):
                po.append(pr)
            if np.isfinite(sp):
                pn.append(sp)
            _dd = 0.5 * np.abs(r["state_new_l1"][m] - r["state_old_l1"][m]).sum(axis=1)
            l1d.append((float(np.median(_dd)), float(_dd.mean()),
                        float(np.percentile(_dd, 90)), float((_dd > 1e-9).mean())))
            ra, rb = rank(a), rank(b)
            eo, en = ra >= EVENT_RANK, rb >= EVENT_RANK
            ev_o += int(eo.sum())
            added += int((en & ~eo).sum()); removed += int((eo & ~en).sum())
            idx = np.nonzero(m)[0]
            pos = {int(i): j for j, i in enumerate(idx)}
            for j in np.nonzero(eo)[0]:
                d = None
                for k in range(0, 9):
                    for s in ((0,) if k == 0 else (-k, k)):
                        q = pos.get(int(idx[j]) + s)
                        if q is not None and en[q]:
                            d = s
                            break
                    if d is not None:
                        break
                disp.append(d if d is not None else np.nan)
            so, sn = ra <= STABLE_RANK, rb <= STABLE_RANK
            agree.append(float((so == sn).mean()))
        dv = np.array(disp, dtype=np.float64)
        finite = dv[np.isfinite(dv)]
        out[fam] = {
            "n_stems": len(rs), "n_old_events": ev_o,
            "pearson_old_vs_new_movement": round(float(np.median(po)), 4) if po else None,
            "spearman_old_vs_new_movement": round(float(np.median(pn)), 4) if pn else None,
            "fraction_of_top5_events_whose_timing_changes": round(float((finite != 0).mean()), 4) if finite.size else None,
            "fraction_of_top5_events_with_no_match_within_8_hops": round(float(np.mean(~np.isfinite(dv))), 4) if dv.size else None,
            "event_displacement_median_hops": round(float(np.median(finite)), 3) if finite.size else None,
            "event_displacement_iqr_hops": round(float(np.percentile(finite, 75) - np.percentile(finite, 25)), 3) if finite.size else None,
            "events_added": added, "events_removed": removed,
            "stable_period_agreement": round(float(np.median(agree)), 4) if agree else None,
            "REPORTED_DIAGNOSTIC_state_L1_distance_old_vs_new": ({
                "median": round(float(np.median([x[0] for x in l1d])), 5),
                "mean": round(float(np.median([x[1] for x in l1d])), 5),
                "p90": round(float(np.median([x[2] for x in l1d])), 5),
                "fraction_of_frames_that_differ_at_all": round(float(np.median([x[3] for x in l1d])), 4),
            } if l1d else None),
        }
    return out


def family_metrics(rows: list[dict], target: str) -> dict:
    from scipy.stats import spearmanr
    key = "Ms_old" if target == "RECTANGULAR_MIDI_PC" else "Ms_new"
    by = defaultdict(list)
    for r in rows:
        by[r["family"]].append(r)
    out = {}
    for name in ALL:
        fam = {}
        for fname, rs in sorted(by.items()):
            g = np.concatenate([np.full(int(r["mask"].sum()), r["id"]) for r in rs])
            if len(np.unique(g)) < 3:
                continue
            Ms = np.concatenate([r[key][r["mask"]] for r in rs])
            Ma = np.concatenate([r["mov"][name][r["mask"]] for r in rs])
            ev = hit = tol = st = fls = 0
            for r in rs:
                m = r["mask"]
                idx = np.nonzero(m)[0]
                rs_ = rank(r[key][m]); rc = rank(r["mov"][name][m])
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
            fam[fname] = {"n_stems": len(rs), "n_frames": int(len(Ms)), "n_events": ev,
                          "framewise_r2_DIAGNOSTIC": C.grouped_r2(Ma, Ms, g),
                          "spearman": round(float(spearmanr(Ma, Ms).statistic), 4),
                          "event_recall_consumer_time": round(hit / max(ev, 1), 4),
                          "event_recall_event_tolerant": round(tol / max(ev, 1), 4),
                          "false_movement_in_target_stable_periods": round(fls / max(st, 1), 4)}
        vals = [v["framewise_r2_DIAGNOSTIC"] for v in fam.values()]
        rec = [v["event_recall_event_tolerant"] for v in fam.values()]
        out[name] = {"by_family": fam,
                     "r2_spread": round(max(vals) - min(vals), 4) if vals else None,
                     "event_tolerant_recall_spread": round(max(rec) - min(rec), 4) if rec else None,
                     "worst_family_event_tolerant": min(fam, key=lambda k: fam[k]["event_recall_event_tolerant"]) if fam else None}
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--git-head", type=str, default="UNKNOWN")
    args = ap.parse_args()
    prereg = json.loads(PREREG.read_text())

    # ---- controls ----
    ident_notes = [Note(0.5, 2.0, 60, 80), Note(1.0, 2.5, 64, 90), Note(3.0, 4.0, 67, 70)]
    ident = float(np.max(np.abs(
        AA.acoustic_activation_state(ident_notes, 200, np.ones(AA.K_MAX_HOPS + 1))["pc_mass"]
        - pitch_class_state(ident_notes, 200)["pc_mass"])))
    # AST import audit - the previous substring grep tripped on the module's own
    # docstring, which NAMES the modules it does not import.
    import ast as _ast
    _tree = _ast.parse((C.ROOT / "src/edgeai/mir/acoustic_activation.py").read_text())
    _imports = set()
    for _n in _ast.walk(_tree):
        if isinstance(_n, _ast.Import):
            _imports.update(a.name for a in _n.names)
        elif isinstance(_n, _ast.ImportFrom):
            _imports.add(_n.module or "")
            _imports.update(f"{_n.module or ''}.{a.name}" for a in _n.names)
    _banned = ("tonal_projection", "host_chroma", "chroma_power", "harmonic_visual")
    indep = not any(b in m for m in _imports for b in _banned)

    z = np.load(CURVES)
    eps = [{"track": str(t), "family": str(f), "curve": c}
           for t, f, c in zip(z["tracks"], z["families"], z["curves"])]
    kb = AA.KernelBank(eps)
    rows = build(args.corpus, kb)

    kern_report = {}
    for r in rows:
        kern_report.setdefault(r["family"], {}).setdefault(r["kernel_meta"]["level"], set()).add(r["track"])
    kern_report = {f: {lvl: {"n_held_out_tracks": len(v)} for lvl, v in d.items()} for f, d in kern_report.items()}
    kern_detail = {}
    for fam in sorted({r["family"] for r in rows}):
        tr = sorted({r["track"] for r in rows if r["family"] == fam})
        k, m = kb.for_stem(fam, tr[0])
        kern_detail[fam] = {"example_held_out_track": tr[0], **m,
                            "k_at_hops": {str(t): round(float(k[t]), 4) for t in (0, 1, 2, 4, 8, 16, 32)}}

    controls = {"identity_kernel_reproduces_pitch_class_state_max_abs_diff": ident,
                "identity_kernel_ok": bool(ident == 0.0),
                "target_module_imports_no_representation": indep,
                "identical_frame_set_for_both_targets": True,
                "n_stems": len(rows),
                "n_frames": int(sum(int(r["mask"].sum()) for r in rows)),
                "all_blocking_pass": bool(ident == 0.0 and indep)}

    eff = target_effect(rows)
    old = family_metrics(rows, "RECTANGULAR_MIDI_PC")
    new = family_metrics(rows, "ACOUSTIC_ACTIVATION_PC")

    # ---- J3J-E attribution ----
    attrib = {}
    for name in ALL:
        rowsm = {}
        for fam in old[name]["by_family"]:
            if fam not in new[name]["by_family"]:
                continue
            o, n = old[name]["by_family"][fam], new[name]["by_family"][fam]
            om, nm = 1.0 - o["event_recall_event_tolerant"], 1.0 - n["event_recall_event_tolerant"]
            rowsm[fam] = {
                "event_tolerant_recall_old": o["event_recall_event_tolerant"],
                "event_tolerant_recall_new": n["event_recall_event_tolerant"],
                "event_miss_reduction": round(om - nm, 4),
                "fraction_of_old_miss_removed": round((om - nm) / om, 4) if om >= 0.10 else None,
                "false_movement_old": o["false_movement_in_target_stable_periods"],
                "false_movement_new": n["false_movement_in_target_stable_periods"],
                "false_movement_reduction": round(o["false_movement_in_target_stable_periods"]
                                                  - n["false_movement_in_target_stable_periods"], 4),
                "framewise_r2_change_SECONDARY": round(n["framewise_r2_DIAGNOSTIC"] - o["framewise_r2_DIAGNOSTIC"], 4),
            }
        attrib[name] = rowsm

    # ---- outcome, 0.10 scale only ----
    A = attrib["P0_CURRENT"]
    improved = {f: bool(A[f]["event_miss_reduction"] >= 0.10 or A[f]["false_movement_reduction"] >= 0.10)
                for f in WEAK if f in A}
    rec_new = {f: new["P0_CURRENT"]["by_family"][f]["event_recall_event_tolerant"]
               for f in REPORTED if f in new["P0_CURRENT"]["by_family"]}
    best = max(rec_new.values()) if rec_new else 0.0
    residual = {f: round(best - v, 4) for f, v in rec_new.items()}
    substantial_residual = any(v >= 0.10 for v in residual.values())
    any_improved = any(improved.values())
    if not controls["all_blocking_pass"]:
        outcome = "TARGET_REPAIR_INCONCLUSIVE"
    elif not any_improved:
        outcome = "TARGET_CORRECTION_IMMATERIAL"
    elif not substantial_residual:
        outcome = "TARGET_CORRECTION_DOMINANT"
    else:
        outcome = "TARGET_CORRECTION_PARTIAL_REPRESENTATION_REMAINS"

    cp = A.get("chromatic_percussion", {})
    red_flag = bool(cp.get("event_miss_reduction", 0.0) >= 0.10)

    receipt = {
        "schema": "spectrasynq.acoustic_activation_result.v1", "job": "J3J",
        "git_head": args.git_head,
        "label": "TARGET REPAIR ONLY - representation-independent by construction. BabySlakh tracks remain consumed; nothing here is promotable.",
        "preregistration": str(PREREG.relative_to(C.ROOT)),
        "execution_environment": "Anthropic cloud container (HOST-class). BabySlakh 16 kHz, md5 verified against the publisher's checksum.",
        "controls": controls,
        "J3J_A_kernels": {
            "construction": prereg["J3J_A_CROSS_FITTED_ATTACK_KERNEL"],
            "fallback_level_used_by_family": kern_report,
            "example_cross_fitted_kernels": kern_detail,
            "total_source_episodes": len(eps),
        },
        "J3J_B_target": {"new": "ACOUSTIC_ACTIVATION_PC", "old": "RECTANGULAR_MIDI_PC",
                         "velocity_weighting": False, "release_model_created": False,
                         "REPORTED_DIAGNOSTIC_silent_frames": {
                             "old": int(sum(r["silent_old"] for r in rows)),
                             "new": int(sum(r["silent_new"] for r in rows))}},
        "J3J_C_target_effect_measured_before_any_candidate": eff,
        "J3J_D_representations": {"RECTANGULAR_MIDI_PC": old, "ACOUSTIC_ACTIVATION_PC": new},
        "J3J_E_attribution": attrib,
        "decision": {"weak_families": WEAK, "materially_improved_under_new_target_P0": improved,
                     "new_target_event_tolerant_recall_P0": rec_new,
                     "residual_gap_to_best_family": residual,
                     "substantial_residual_disparity": substantial_residual},
        "chromatic_percussion_red_flag": {
            "rule": "J3I found no attack/gate mismatch for this family, so a large improvement would indicate a target-construction problem, not a win",
            "event_miss_reduction": cp.get("event_miss_reduction"),
            "flag_raised": red_flag},
        "outcome": outcome,
        "J3I_mutated": False, "J3G_mutated": False, "J3G2_mutated": False, "J3F_mutated": False,
        "new_tonal_representation": False, "cqt_run": False, "crp_repair": False, "nnls_run": False,
        "basic_pitch_run": False, "neural_model": False,
        "production_firmware_changed": False, "titan": False, "student_io_frozen": False,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(receipt, indent=2, sort_keys=False) + "\n")
    print(json.dumps({"outcome": outcome, "controls": controls,
                      "state_distance": {f: v["REPORTED_DIAGNOSTIC_state_L1_distance_old_vs_new"]
                                         for f, v in eff.items()},
                      "decision": receipt["decision"],
                      "red_flag": receipt["chromatic_percussion_red_flag"]}, indent=2))
    print(f"receipt -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
