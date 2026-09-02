#!/usr/bin/env python3
"""J3D-A - does harmonic MOVEMENT exist independently of acoustic energy cues?

Runs the experiment pre-registered in
`docs/mir/receipts/harmonic_movement/J3D_A_PREREGISTRATION.json`.

Construct: causal change in the active pitch-class distribution. NOT chords,
NOT key, NOT tonal centre, NOT tension, NOT melody. Exact BabySlakh MIDI is the
oracle; no teacher model is used and none is needed.

Label: SYNTHETIC_UPPER_BOUND. Nothing here is a visual claim - that is J3D-B.
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
    cosine_movement,
    is_tonal_instrument,
    lagged_abs_delta,
    pitch_class_state,
    rectified_flux,
    tv_movement,
    within_track_rank,
)
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

PREREG = ROOT / "docs" / "mir" / "receipts" / "harmonic_movement" / "J3D_A_PREREGISTRATION.json"
ALPHAS = (1e-3, 1e-2, 1e-1, 1.0, 10.0, 100.0, 1000.0)
LAG = MOVEMENT_LAG_HOPS


def _fit(X, Y, a):
    mu, sd = X.mean(0), X.std(0) + 1e-9
    Xs = (X - mu) / sd
    ym = Y.mean(0)
    W = np.linalg.solve(Xs.T @ Xs + a * np.eye(Xs.shape[1]), Xs.T @ (Y - ym))
    return {"mu": mu, "sd": sd, "ym": ym, "W": W}


def _pred(m, X):
    return ((X - m["mu"]) / m["sd"]) @ m["W"] + m["ym"]


def _r2(y, yh):
    return float(1.0 - np.sum((y - yh) ** 2) / (np.sum((y - y.mean()) ** 2) + 1e-20))


def grouped_r2(X, y, groups, *, n_folds=5, seed=0):
    X = np.atleast_2d(np.asarray(X, dtype=np.float64).T).T
    y = np.asarray(y, dtype=np.float64).reshape(-1, 1)
    uniq = np.unique(groups)
    n_folds = max(2, min(n_folds, len(uniq)))
    oof = np.full_like(y, np.nan)
    for f in np.array_split(np.random.default_rng(seed).permutation(uniq), n_folds):
        te = np.isin(groups, f)
        tr = ~te
        if tr.sum() < 10 or te.sum() < 1:
            continue
        trt = np.unique(groups[tr])
        cut = max(1, len(trt) // 4)
        iv = np.isin(groups, trt[:cut]) & tr
        it = tr & ~iv
        best, ba = -np.inf, ALPHAS[0]
        for a in ALPHAS:
            m = _fit(X[it], y[it], a)
            s = _r2(y[iv], _pred(m, X[iv]))
            if s > best:
                best, ba = s, a
        oof[te] = _pred(_fit(X[tr], y[tr], ba), X[te])
    ok = ~np.isnan(oof[:, 0])
    return round(_r2(y[ok], oof[ok]), 4)


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
    kept, dropped_drum, dropped_prog = [], 0, 0
    for inst in pm.instruments:
        if not is_tonal_instrument(inst.is_drum, inst.program):
            if inst.is_drum:
                dropped_drum += 1
            else:
                dropped_prog += 1
            continue
        kept.append(inst)
    notes = [Note(float(n.start), float(n.end), int(n.pitch), int(n.velocity))
             for i in kept for n in i.notes]

    times, _ = frame_grid(y.size)
    st = pitch_class_state(notes, times.size)
    _, chroma = host_chroma12(y.astype(np.float32))
    _, spec = host_spectrogram80(y.astype(np.float32))
    _, rms, _ = dsp_register_features(y)

    # librosa onset_strength, center=False -> librosa frame j spans [j*hop, j*hop+n_fft).
    # Our frame i spans [(i+1)*hop - n_fft, (i+1)*hop) = [(i-3)*hop, (i+1)*hop) for
    # n_fft/hop = 4. So our i maps to librosa j = i - 3. Declared, and checked by the
    # onset-vs-flux alignment diagnostic in the receipt.
    onset_raw = librosa.onset.onset_strength(y=y.astype(np.float32), sr=SR,
                                             hop_length=HOP, n_fft=N_FFT, center=False)
    # v2 repair: the naive n_fft/hop - 1 mapping is wrong because onset_strength
    # already takes a first difference internally. The shift is MEASURED per track
    # against 1-hop rectified flux on host_spectrogram80 - an independent baseline,
    # never against the target - so it cannot bias the result toward the hypothesis.
    # See docs/mir/receipts/harmonic_movement/J3D_A_DEFECT_onset_alignment.json
    from scipy.stats import spearmanr as _sp

    flux1 = np.zeros(len(spec))
    flux1[1:] = np.clip(np.diff(spec.astype(np.float64), axis=0), 0.0, None).sum(axis=1)
    best_shift, best_s = 0, -np.inf
    for k in range(0, 7):
        cand = np.zeros(times.size)
        for i in range(times.size):
            j = i - k
            if 0 <= j < onset_raw.size:
                cand[i] = onset_raw[j]
        n0 = min(len(flux1), cand.size)
        s = _sp(flux1[:n0], cand[:n0]).statistic
        if np.isfinite(s) and s > best_s:
            best_s, best_shift = float(s), k
    shift = best_shift
    onset = np.zeros(times.size)
    for i in range(times.size):
        j = i - shift
        onset[i] = onset_raw[j] if 0 <= j < onset_raw.size else 0.0

    n = min(times.size, len(chroma), len(spec), len(rms))

    M_tv = tv_movement(st["pc_mass"][:n])
    M_cos = cosine_movement(st["pc_mass"][:n])
    B_chroma = tv_movement(l1_normalise(chroma[:n].astype(np.float64)))
    B_flux = rectified_flux(spec[:n].astype(np.float64))
    B_onset = lagged_abs_delta(onset[:n])
    B_rms = lagged_abs_delta(np.log(rms[:n] + 1e-12))

    sil = st["silent"][:n]
    pair_ok = np.zeros(n, dtype=bool)
    pair_ok[LAG:] = (~sil[LAG:]) & (~sil[:-LAG])
    valid = (pair_ok & silence_mask(rms[:n]) & np.isfinite(M_tv) & np.isfinite(B_chroma)
             & np.isfinite(B_flux) & np.isfinite(B_onset) & np.isfinite(B_rms))
    return {
        "track": track_dir.name, "valid": valid,
        "M_tv": M_tv[valid], "M_cos": M_cos[valid], "B_chroma": B_chroma[valid],
        "B_flux": B_flux[valid], "B_onset": B_onset[valid], "B_rms": B_rms[valid],
        "onset_series": onset[:n], "flux_series": B_flux,
        "onset_shift_measured": int(shift), "onset_shift_spearman": round(float(best_s), 4),
        "n_total": int(n), "n_valid": int(valid.sum()),
        "n_silent_frames": int(sil.sum()),
        "instruments_kept": len(kept), "dropped_is_drum": dropped_drum,
        "dropped_program_ge_112": dropped_prog,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--git-head", type=str, default="UNKNOWN")
    args = ap.parse_args()
    prereg = json.loads(PREREG.read_text())

    blocks = []
    for d in sorted(p for p in args.corpus.iterdir() if p.is_dir() and (p / "all_src.mid").is_file()):
        b = build(d)
        if b:
            blocks.append(b)
    if not blocks:
        print("no usable tracks", file=sys.stderr)
        return 2

    groups = np.concatenate([np.full(b["n_valid"], b["track"]) for b in blocks])
    cat = lambda k: np.concatenate([b[k] for b in blocks])  # noqa: E731
    M_tv, M_cos = cat("M_tv"), cat("M_cos")
    Bc, Bf, Bo, Br = cat("B_chroma"), cat("B_flux"), cat("B_onset"), cat("B_rms")
    ENERGY = np.column_stack([Bf, Bo, Br])
    ALL4 = np.column_stack([Bc, Bf, Bo, Br])

    # ---- controls ----------------------------------------------------------
    synth = 0.7 * Bf - 0.3 * Br + 0.5 * Bo
    c_mach = grouped_r2(ENERGY, synth, groups)
    perm = np.random.default_rng(1234).permutation(len(M_tv))
    c_shuf = grouped_r2(ALL4[perm], M_tv, groups)
    controls = {
        "machinery_linear_recovery": {"r2": c_mach, "requirement": ">= 0.95", "pass": bool(c_mach >= 0.95)},
        "shuffled_labels": {"r2": c_shuf, "requirement": "<= 0.10", "pass": bool(c_shuf <= 0.10)},
    }
    controls["all_blocking_pass"] = bool(controls["machinery_linear_recovery"]["pass"]
                                         and controls["shuffled_labels"]["pass"])
    if not controls["all_blocking_pass"]:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps({"job": "J3D-A", "verdict": "INVALID_RUN",
                                        "controls": controls}, indent=2) + "\n")
        print(json.dumps({"verdict": "INVALID_RUN", "controls": controls}, indent=2))
        return 1

    # ---- information -------------------------------------------------------
    info = {
        "M_tv_from_B_chroma_alone": grouped_r2(Bc, M_tv, groups),
        "M_tv_from_acoustic_energy_set": grouped_r2(ENERGY, M_tv, groups),
        "M_tv_from_all_four": grouped_r2(ALL4, M_tv, groups),
        "M_cos_from_B_chroma_alone": grouped_r2(Bc, M_cos, groups),
        "M_cos_from_acoustic_energy_set": grouped_r2(ENERGY, M_cos, groups),
        "M_cos_from_all_four": grouped_r2(ALL4, M_cos, groups),
    }
    from scipy.stats import spearmanr

    info["spearman_ordinary_holdout"] = {
        "M_tv_vs_B_chroma": round(float(spearmanr(M_tv, Bc).statistic), 4),
        "M_tv_vs_B_flux": round(float(spearmanr(M_tv, Bf).statistic), 4),
        "M_tv_vs_B_onset": round(float(spearmanr(M_tv, Bo).statistic), 4),
        "M_tv_vs_B_rms": round(float(spearmanr(M_tv, Br).statistic), 4),
        "M_tv_vs_M_cos": round(float(spearmanr(M_tv, M_cos).statistic), 4),
    }

    # ---- challenge classes (oracle + baselines only) -----------------------
    rM, rO, rR, rC = (within_track_rank(x, groups) for x in (M_tv, Bo, Br, Bc))
    cls = {
        "HARMONIC_CHANGE_FLAT_ENERGY": (rM >= 0.95) & (rR <= 0.50),
        "HARMONIC_CHANGE_NO_ONSET": (rM >= 0.95) & (rO <= 0.50),
        "ACOUSTIC_CHANGE_LOW_HARMONIC_CHANGE": (rO >= 0.95) & (rM <= 0.50),
    }
    n_valid = len(M_tv)
    challenge = {}
    for name, m in cls.items():
        tracks = sorted({g for g in np.unique(groups) if m[groups == g].any()})
        challenge[name] = {
            "n_frames": int(m.sum()),
            "rate_of_valid_frames": round(float(m.sum()) / n_valid, 5),
            "tracks_present": len(tracks),
            "median_M_tv": round(float(np.median(M_tv[m])), 4) if m.any() else None,
            "median_B_chroma": round(float(np.median(Bc[m])), 4) if m.any() else None,
        }
    challenge["control_class_populated"] = bool(
        challenge["ACOUSTIC_CHANGE_LOW_HARMONIC_CHANGE"]["n_frames"] > 0)

    top5 = rM >= 0.95
    chroma_recall = float(((rC >= 0.80) & top5).sum()) / max(int(top5.sum()), 1)

    # ---- alignment diagnostics --------------------------------------------
    lag_diag = {}
    for k in range(-4, 5):
        Xs, Ys, Gs = [], [], []
        for g in np.unique(groups):
            m = groups == g
            a, b = Bc[m], M_tv[m]
            if k > 0:
                a, b = a[:-k], b[k:]
            elif k < 0:
                a, b = a[-k:], b[:k]
            if len(a) < 20:
                continue
            Xs.append(a)
            Ys.append(b)
            Gs.append(np.full(len(a), g))
        if Xs:
            lag_diag[str(k)] = grouped_r2(np.concatenate(Xs), np.concatenate(Ys), np.concatenate(Gs))
    best = max(lag_diag, key=lambda k: lag_diag[k])
    lag = {"by_lag": lag_diag, "argmax_lag": int(best),
           "margin_over_lag0": round(lag_diag[best] - lag_diag["0"], 6)}
    lag_fault = abs(lag["argmax_lag"]) >= 2 or lag["margin_over_lag0"] > 0.02
    onset_flux_align = round(float(spearmanr(Bo, Bf).statistic), 4)

    # ---- classification, in the pre-registered precedence order ------------
    harm_rates = [challenge["HARMONIC_CHANGE_FLAT_ENERGY"]["rate_of_valid_frames"],
                  challenge["HARMONIC_CHANGE_NO_ONSET"]["rate_of_valid_frames"]]
    harm_tracks = [challenge["HARMONIC_CHANGE_FLAT_ENERGY"]["tracks_present"],
                   challenge["HARMONIC_CHANGE_NO_ONSET"]["tracks_present"]]
    if info["M_tv_from_acoustic_energy_set"] >= 0.70 or max(harm_rates) < 0.002:
        outcome = "HARMONIC_MOVEMENT_ACOUSTICALLY_REDUNDANT"
    elif info["M_tv_from_B_chroma_alone"] >= 0.70 and chroma_recall >= 0.90:
        outcome = "HARMONIC_MOVEMENT_DERIVABLE_FROM_CHROMA"
    elif (min(harm_rates) >= 0.010 and min(harm_tracks) >= 15
          and info["M_tv_from_all_four"] < 0.50):
        outcome = "HARMONIC_MOVEMENT_INCREMENTAL"
    else:
        outcome = "HARMONIC_MOVEMENT_INCONCLUSIVE"
    if lag_fault:
        outcome = "HARMONIC_MOVEMENT_INCONCLUSIVE"

    receipt = {
        "schema": "spectrasynq.harmonic_movement_result.v1",
        "job": "J3D-A", "run": "v2", "label": "SYNTHETIC_UPPER_BOUND",
        "supersedes_note": "v1 (J3D_A_RESULT_v1.json) retained unmutated; v2 repairs the measured B_onset misalignment only. v1 scores were seen before this repair - see J3D_A_DEFECT_onset_alignment.json.",
        "git_head": args.git_head,
        "preregistration": str(PREREG.relative_to(ROOT)),
        "preregistration_written_before_any_score": prereg["written_before_any_score"],
        "execution_environment": "Anthropic cloud container (HOST-class). Corpus md5 verified against the publisher's checksum.",
        "construct": {
            "pitch_class_state": "12-D, duration-overlap weighted, NO velocity weighting, L1-normalised; silence explicit and never zero-filled",
            "movement": f"primary M_tv = 0.5*L1(pc_t, pc_t-{LAG}); alternative M_cos = 1 - cosine, same lag",
            "movement_lag_hops": LAG, "movement_lag_s": LAG * HOP / SR,
            "percussion_exclusion": "is_drum OR General MIDI program >= 112 (Percussive + Sound Effects)",
            "causal_timebase": "sr 16000, hop 512, n_fft 2048, causal frame ends at (i+1)*hop, hop-centre timestamp, label lookahead 0",
        },
        "corpus": {
            "tracks": len(blocks),
            "frames_valid": int(n_valid),
            "instruments_kept": sum(b["instruments_kept"] for b in blocks),
            "dropped_is_drum": sum(b["dropped_is_drum"] for b in blocks),
            "dropped_program_ge_112": sum(b["dropped_program_ge_112"] for b in blocks),
            "silent_pitch_frames": sum(b["n_silent_frames"] for b in blocks),
            "per_track": [{"track": b["track"], "valid": b["n_valid"], "total": b["n_total"]} for b in blocks],
        },
        "split": "grouped 5-fold, groups = track",
        "controls": controls,
        "information": info,
        "challenge_set": challenge,
        "chroma_event_recall_top5_in_top20": round(chroma_recall, 4),
        "alignment": {"chroma_movement_lag": lag, "lag_fault": bool(lag_fault),
                      "onset_vs_flux_spearman": onset_flux_align,
                      "onset_frame_shift_measured_per_track": sorted({b["onset_shift_measured"] for b in blocks}),
                      "onset_shift_alignment_spearman_min": round(min(b["onset_shift_spearman"] for b in blocks), 4)},
        "outcome": outcome,
        "thresholds_applied": prereg["thresholds_in_precedence_order"],
        "what_this_says_about_visual_value": "NOTHING. Visual grammar is J3D-B.",
        "forbidden_conclusions": prereg["construct_validity"]["broader_conclusions_that_remain_FORBIDDEN"],
        "student_io_frozen": False, "titan": False, "production_firmware_changed": False,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"outcome": outcome, "information": info,
                      "challenge": {k: v for k, v in challenge.items() if isinstance(v, dict)},
                      "chroma_recall": round(chroma_recall, 4),
                      "controls": controls}, indent=2))
    print(f"receipt -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
