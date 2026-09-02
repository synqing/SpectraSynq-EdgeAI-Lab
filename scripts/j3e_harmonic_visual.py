#!/usr/bin/env python3
"""J3E - perfect-information harmonic visual value.

Question: IF SpectraSynq possessed correct harmonic information, would that enable
a visual behaviour worth pursuing? Deliberately independent of whether the current
frontend can recover it. VALUE != RECOVERABILITY != COMPUTE COST.

Label: HOST_ORACLE_VISUAL_FEASIBILITY. Not a product effect, not a compatibility
row, not Gate B, not Gate C, not firmware.

Pre-registration: docs/mir/receipts/harmonic_visual/J3E_PREREGISTRATION.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from edgeai.mir.harmonic_movement import (  # noqa: E402
    MOVEMENT_LAG_HOPS,
    is_tonal_instrument,
    l1_rows,
    lagged_abs_delta,
    pitch_class_state,
    rectified_flux,
    tv_movement,
    within_track_rank,
)
from edgeai.mir.harmonic_visual import pipeline  # noqa: E402
from edgeai.mir.host_chroma import host_chroma12, host_spectrogram80  # noqa: E402
from edgeai.mir.note_register import (  # noqa: E402
    HOP,
    N_FFT,
    SR,
    Note,
    dsp_register_features,
    frame_grid,
    l1_normalise,
    silence_mask,
)

PREREG = ROOT / "docs" / "mir" / "receipts" / "harmonic_visual" / "J3E_PREREGISTRATION.json"
TOL_HOPS = 2
LAG = MOVEMENT_LAG_HOPS


def build(track_dir: Path):
    import librosa
    import pretty_midi
    import soundfile as sf

    mix = next((track_dir / c for c in ("mix.flac", "mix.wav") if (track_dir / c).is_file()), None)
    mid = track_dir / "all_src.mid"
    if mix is None or not mid.is_file():
        return None
    y, sr = sf.read(str(mix), dtype="float64", always_2d=True)
    if sr != SR:
        return None
    y = y.mean(axis=1)
    pm = pretty_midi.PrettyMIDI(str(mid))
    notes = [Note(float(n.start), float(n.end), int(n.pitch), int(n.velocity))
             for inst in pm.instruments if is_tonal_instrument(inst.is_drum, inst.program)
             for n in inst.notes]

    times, _ = frame_grid(y.size)
    st = pitch_class_state(notes, times.size)
    _, chroma = host_chroma12(y.astype(np.float32))
    _, spec = host_spectrogram80(y.astype(np.float32))
    _, rms, _ = dsp_register_features(y)
    onset_raw = librosa.onset.onset_strength(y=y.astype(np.float32), sr=SR,
                                             hop_length=HOP, n_fft=N_FFT, center=False)
    n = min(times.size, len(chroma), len(spec), len(rms))
    flux1 = np.zeros(len(spec))
    flux1[1:] = np.clip(np.diff(spec.astype(np.float64), axis=0), 0.0, None).sum(axis=1)
    from scipy.stats import spearmanr as _sp
    best_shift, best_s = 0, -np.inf
    for k in range(7):
        cand = np.zeros(times.size)
        for i in range(times.size):
            j = i - k
            if 0 <= j < onset_raw.size:
                cand[i] = onset_raw[j]
        s = _sp(flux1[:n], cand[:n]).statistic
        if np.isfinite(s) and s > best_s:
            best_s, best_shift = float(s), k
    onset = np.zeros(times.size)
    for i in range(times.size):
        j = i - best_shift
        onset[i] = onset_raw[j] if 0 <= j < onset_raw.size else 0.0

    oracle_state = l1_rows(st["pc_mass"][:n])
    chroma_state = l1_normalise(chroma[:n].astype(np.float64))
    M_oracle = tv_movement(st["pc_mass"][:n])
    M_chroma = tv_movement(chroma_state)
    B_flux = rectified_flux(spec[:n].astype(np.float64))
    B_onset = lagged_abs_delta(onset[:n])
    B_rms = lagged_abs_delta(np.log(rms[:n] + 1e-12))

    sil = st["silent"][:n]
    pair_ok = np.zeros(n, dtype=bool)
    pair_ok[LAG:] = (~sil[LAG:]) & (~sil[:-LAG])
    valid = (pair_ok & silence_mask(rms[:n]) & np.isfinite(M_oracle) & np.isfinite(M_chroma)
             & np.isfinite(B_flux) & np.isfinite(B_onset) & np.isfinite(B_rms))
    return {"track": track_dir.name, "n": n, "valid": valid,
            "oracle_state": oracle_state, "chroma_state": chroma_state,
            "M_oracle": M_oracle, "M_chroma": M_chroma,
            "B_onset": B_onset, "B_rms": B_rms}


def reversal_rate(colour: np.ndarray, mask: np.ndarray) -> float:
    d = np.diff(colour, axis=0)
    if len(d) < 2:
        return float("nan")
    dot = (d[1:] * d[:-1]).sum(axis=1)
    m = mask[2:]
    if m.sum() == 0:
        return float("nan")
    return float((dot[m[: len(dot)]] < 0).mean()) if len(dot) >= len(m) else float((dot < 0).mean())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--artefact-dir", type=Path, default=None)
    ap.add_argument("--git-head", type=str, default="UNKNOWN")
    args = ap.parse_args()
    prereg = json.loads(PREREG.read_text())

    blocks = [b for b in (build(d) for d in sorted(
        p for p in args.corpus.iterdir() if p.is_dir() and (p / "all_src.mid").is_file())) if b]
    if not blocks:
        print("no usable tracks", file=sys.stderr)
        return 2

    # --- challenge membership, recomputed by the J3D code path -------------
    groups = np.concatenate([np.full(int(b["valid"].sum()), b["track"]) for b in blocks])
    vM = np.concatenate([b["M_oracle"][b["valid"]] for b in blocks])
    vO = np.concatenate([b["B_onset"][b["valid"]] for b in blocks])
    vR = np.concatenate([b["B_rms"][b["valid"]] for b in blocks])
    rM, rO, rR = (within_track_rank(x, groups) for x in (vM, vO, vR))
    cls = {
        "HARMONIC_CHANGE_FLAT_ENERGY": (rM >= 0.95) & (rR <= 0.50),
        "HARMONIC_CHANGE_NO_ONSET": (rM >= 0.95) & (rO <= 0.50),
        "ACOUSTIC_CHANGE_LOW_HARMONIC_CHANGE": (rO >= 0.95) & (rM <= 0.50),
    }
    counts = {k: int(v.sum()) for k, v in cls.items()}
    expected = prereg["challenge_set"]["expected_counts_from_J3D_A_v2"]
    membership_ok = counts == expected
    if not membership_ok:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps({"job": "J3E", "outcome": "INVALID_RUN",
                                        "reason": "challenge membership does not match J3D-A v2",
                                        "got": counts, "expected": expected}, indent=2) + "\n")
        print(json.dumps({"outcome": "INVALID_RUN", "got": counts, "expected": expected}, indent=2))
        return 1
    holdout = ~(cls["HARMONIC_CHANGE_FLAT_ENERGY"] | cls["HARMONIC_CHANGE_NO_ONSET"]
                | cls["ACOUSTIC_CHANGE_LOW_HARMONIC_CHANGE"])

    results = {}
    per_track_colour = {}
    for floor_id, with_floor in (("without_floor", False), ("with_floor", True)):
        cond_out = {}
        for cond, s_key, m_key in (("CONTROL", "chroma_state", "M_chroma"),
                                   ("TREATMENT", "oracle_state", "M_oracle")):
            de_valid, rev_track, colours = [], [], {}
            for b in blocks:
                r = pipeline(b[s_key], b[m_key], with_floor=with_floor)
                colours[b["track"]] = r["colour"]
                de = r["delta_e"]
                # event-tolerant max over +/- TOL hops, computed on the CONTIGUOUS series
                pad = np.nan_to_num(de, nan=0.0)
                tol = np.copy(pad)
                for k in range(1, TOL_HOPS + 1):
                    tol[:-k] = np.maximum(tol[:-k], pad[k:])
                    tol[k:] = np.maximum(tol[k:], pad[:-k])
                de_valid.append(np.column_stack([pad[b["valid"]], tol[b["valid"]]]))
                d = np.diff(r["colour"], axis=0)
                dot = (d[1:] * d[:-1]).sum(axis=1)
                m = b["valid"][2:]
                rev_track.append(dot[m] < 0 if m.sum() else np.zeros(0, dtype=bool))
            arr = np.vstack(de_valid)
            de_now, de_tol = arr[:, 0], arr[:, 1]
            rev = np.concatenate(rev_track)
            thr = float(np.percentile(de_now[holdout], 90))
            resp_now, resp_tol = de_now >= thr, de_tol >= thr
            cond_out[cond] = {
                "threshold_deltaE_p90_of_own_holdout": round(thr, 4),
                "consumer_time": {k: round(float(resp_now[m].mean()), 4) for k, m in cls.items()},
                "event_tolerant": {k: round(float(resp_tol[m].mean()), 4) for k, m in cls.items()},
                "holdout": {
                    "above_threshold_rate_VACUOUS_BY_CONSTRUCTION": round(float(resp_now[holdout].mean()), 4),
                    "median_deltaE": round(float(np.median(de_now[holdout])), 4),
                    "direction_reversal_rate": round(float(rev.mean()), 4) if rev.size else None,
                },
                "n_frames": int(len(de_now)),
            }
            if floor_id == "without_floor":
                per_track_colour[cond] = colours
        results[floor_id] = cond_out

    # --- classification on the primary variant -----------------------------
    P = results["without_floor"]
    T, C = P["TREATMENT"], P["CONTROL"]
    harm = ["HARMONIC_CHANGE_FLAT_ENERGY", "HARMONIC_CHANGE_NO_ONSET"]
    t_recall = float(np.mean([T["event_tolerant"][k] for k in harm]))
    c_recall = float(np.mean([C["event_tolerant"][k] for k in harm]))
    recall_gain_both = all(T["event_tolerant"][k] - C["event_tolerant"][k] >= 0.10 for k in harm)
    false_gain = (C["event_tolerant"]["ACOUSTIC_CHANGE_LOW_HARMONIC_CHANGE"]
                  - T["event_tolerant"]["ACOUSTIC_CHANGE_LOW_HARMONIC_CHANGE"]) >= 0.10
    t_rev = T["holdout"]["direction_reversal_rate"] or 0.0
    c_rev = C["holdout"]["direction_reversal_rate"] or 1e-9
    chatter_ok = t_rev <= 1.5 * c_rev

    if t_recall < 0.50:
        outcome = "HARMONIC_VISUAL_CARRIER_FAIL"
    elif (recall_gain_both or false_gain) and chatter_ok:
        outcome = "HARMONIC_VISUAL_INFORMATION_GAIN"
    elif recall_gain_both or false_gain:
        outcome = "HARMONIC_VISUAL_INCONCLUSIVE"
    else:
        outcome = "HARMONIC_VISUAL_NO_INCREMENT"

    receipt = {
        "schema": "spectrasynq.harmonic_visual_result.v1",
        "job": "J3E", "label": "HOST_ORACLE_VISUAL_FEASIBILITY",
        "git_head": args.git_head,
        "preregistration": str(PREREG.relative_to(ROOT)),
        "preregistration_written_before_any_score": prereg["written_before_any_score"],
        "execution_environment": "Anthropic cloud container (HOST-class). Corpus md5 verified against the publisher's checksum.",
        "oracle": prereg["oracle"], "visual_verb": prereg["visual_verb"],
        "conditions": prereg["conditions"],
        "challenge_membership": {"counts": counts, "expected_from_J3D_A_v2": expected,
                                 "matches": membership_ok, "holdout_frames": int(holdout.sum())},
        "temporal_views": {"consumer_time": "no correction", "event_tolerant_hops": TOL_HOPS},
        "results": results,
        "primary_variant": "without_floor",
        "decision_inputs": {
            "treatment_harmonic_recall_event_tolerant": round(t_recall, 4),
            "control_harmonic_recall_event_tolerant": round(c_recall, 4),
            "recall_gain_on_both_harmonic_classes": bool(recall_gain_both),
            "acoustic_false_response_gain": bool(false_gain),
            "chatter_guard_reversal_rate_ok": bool(chatter_ok),
        },
        "outcome": outcome,
        "thresholds_applied": prereg["outcome_thresholds"],
        "what_this_is_not": prereg["this_is_not"],
        "student_io_frozen": False, "titan": False,
        "production_firmware_changed": False, "compatibility_pin_changed": False,
        "product_mode_created": False,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    if args.artefact_dir and outcome == "HARMONIC_VISUAL_INFORMATION_GAIN":
        np.savez_compressed(args.artefact_dir / "colours.npz",
                            **{f"{c}__{t}": v for c, d in per_track_colour.items()
                               for t, v in d.items()})
    print(json.dumps({"outcome": outcome, "decision_inputs": receipt["decision_inputs"],
                      "results": results}, indent=2))
    print(f"receipt -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
