#!/usr/bin/env python3
"""J3C - register frontend sufficiency.

ONE question: how much register information is already recoverable from the
EXISTING SpectraSynq HOST frontend (`host_spectrogram80`)?

It does NOT ask whether register is valuable. See
`docs/mir/receipts/note_register/J3C_PREREGISTRATION.json` for the construct
validity statement, the thresholds, and what a PASS/FAIL is and is not allowed
to conclude.

Stage 1 is deterministic transforms of the frontend's own output. Stage 2 runs
only if Stage 1 leaves the question open, and its models are INFORMATION PROBES,
never product architecture.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from edgeai.mir.host_chroma import host_spectrogram80  # noqa: E402
from edgeai.mir.note_register import (  # noqa: E402
    HOP,
    N_FFT,
    SR,
    Note,
    dsp_register_features,
    frame_grid,
    harmonic_sum_spectrum,
    midi_targets,
    silence_mask,
    spec80_decompress,
    spec80_midi_positions,
    weighted_centroid,
    weighted_quantile,
)

PREREG = ROOT / "docs" / "mir" / "receipts" / "note_register" / "J3C_PREREGISTRATION.json"
ALPHAS = (1e-3, 1e-2, 1e-1, 1.0, 10.0, 100.0, 1000.0)


# ------------------------------------------------------------ ridge + CV ----
def _fit(X, Y, alpha):
    mu, sd = X.mean(0), X.std(0) + 1e-9
    Xs = (X - mu) / sd
    ym = Y.mean(0)
    W = np.linalg.solve(Xs.T @ Xs + alpha * np.eye(Xs.shape[1]), Xs.T @ (Y - ym))
    return {"mu": mu, "sd": sd, "ym": ym, "W": W}


def _pred(m, X):
    return ((X - m["mu"]) / m["sd"]) @ m["W"] + m["ym"]


def _r2(y, yhat):
    ss_res = np.sum((y - yhat) ** 2, axis=0)
    ss_tot = np.sum((y - y.mean(0)) ** 2, axis=0) + 1e-20
    return 1.0 - ss_res / ss_tot


def grouped_oof(X, Y, groups, *, n_folds=5, seed=0, model="ridge"):
    """Out-of-fold predictions, grouped by track. Returns metrics + predictions."""
    X = np.atleast_2d(X.T).T.astype(np.float64)
    Y = Y.reshape(-1, 1).astype(np.float64)
    uniq = np.unique(groups)
    n_folds = max(2, min(n_folds, len(uniq)))
    order = np.random.default_rng(seed).permutation(uniq)
    oof = np.full_like(Y, np.nan)
    for f in np.array_split(order, n_folds):
        te = np.isin(groups, f)
        tr = ~te
        if tr.sum() < 10 or te.sum() < 1:
            continue
        if model == "ridge":
            tr_tracks = np.unique(groups[tr])
            cut = max(1, len(tr_tracks) // 4)
            iv = np.isin(groups, tr_tracks[:cut]) & tr
            it = tr & ~iv
            best, best_a = -np.inf, ALPHAS[0]
            for a in ALPHAS:
                m = _fit(X[it], Y[it], a)
                s = float(_r2(Y[iv], _pred(m, X[iv]))[0])
                if s > best:
                    best, best_a = s, a
            m = _fit(X[tr], Y[tr], best_a)
            oof[te] = _pred(m, X[te])
        elif model == "gbm":
            from sklearn.ensemble import HistGradientBoostingRegressor

            g = HistGradientBoostingRegressor(max_iter=200, max_depth=6, random_state=0)
            g.fit(X[tr], Y[tr].ravel())
            oof[te] = g.predict(X[te]).reshape(-1, 1)
        elif model == "mlp":
            from sklearn.neural_network import MLPRegressor
            from sklearn.preprocessing import StandardScaler

            sc = StandardScaler().fit(X[tr])
            n = MLPRegressor(hidden_layer_sizes=(32, 16), max_iter=120, random_state=0,
                             early_stopping=True, n_iter_no_change=8)
            n.fit(sc.transform(X[tr]), Y[tr].ravel())
            oof[te] = n.predict(sc.transform(X[te])).reshape(-1, 1)
    ok = ~np.isnan(oof[:, 0])
    err = np.abs(Y[ok, 0] - oof[ok, 0])
    return {
        "r2": float(_r2(Y[ok], oof[ok])[0]),
        "mae_semitones": float(err.mean()),
        "median_abs_err_semitones": float(np.median(err)),
        "n_scored": int(ok.sum()),
        "_oof": oof[:, 0],
        "_ok": ok,
    }


def strip(d):
    return {k: v for k, v in d.items() if not k.startswith("_")}


def lag_sweep(x, y, groups):
    out = {}
    for k in range(-4, 5):
        Xs, Ys, Gs = [], [], []
        for g in np.unique(groups):
            m = groups == g
            a, b = x[m], y[m]
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
            r = grouped_oof(np.concatenate(Xs), np.concatenate(Ys), np.concatenate(Gs))
            out[str(k)] = round(r["r2"], 6)
    best = max(out, key=lambda k: out[k]) if out else "0"
    return {"by_lag": out, "argmax_lag": int(best),
            "margin_over_lag0": round(out.get(best, 0.0) - out.get("0", 0.0), 6)}


def lag_ok(d):
    return abs(d["argmax_lag"]) < 2 and d["margin_over_lag0"] <= 0.02


# ----------------------------------------------------------------- data -----
def build(track_dir: Path):
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
    notes = [
        Note(float(n.start), float(n.end), int(n.pitch), int(n.velocity))
        for inst in pretty_midi.PrettyMIDI(str(mid)).instruments
        if not inst.is_drum
        for n in inst.notes
    ]
    times, _ = frame_grid(y.size)
    tg = midi_targets(notes, times.size)
    _, spec = host_spectrogram80(y.astype(np.float32))
    dsp, rms, _ = dsp_register_features(y)
    m = min(times.size, len(spec), len(dsp))
    valid = (tg["weight_total"][:m] > 0) & silence_mask(rms[:m]) & np.isfinite(tg["register_centroid"][:m])
    return {
        "track": track_dir.name,
        "spec01": spec[:m][valid].astype(np.float64),
        "reg": tg["register_centroid"][:m][valid],
        "dsp6": dsp[:m][valid],
        "n_total": int(m),
        "n_valid": int(valid.sum()),
    }


def estimators(spec01, positions):
    """All Stage-1 deterministic scalars, under both declared weightings."""
    out = {}
    for wname, W in (("frozen", spec01), ("decompressed", spec80_decompress(spec01))):
        S, mgrid = harmonic_sum_spectrum(W, positions)
        out[f"E1_midi_energy_centroid__{wname}"] = weighted_centroid(W, positions)
        out[f"E2_weighted_median__{wname}"] = weighted_quantile(W, positions, 0.50)
        out[f"E3_q25__{wname}"] = weighted_quantile(W, positions, 0.25)
        out[f"E3_q75__{wname}"] = weighted_quantile(W, positions, 0.75)
        out[f"E4_harmonic_sum_centroid__{wname}"] = weighted_centroid(S, mgrid)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--git-head", type=str, default="UNKNOWN")
    args = ap.parse_args()

    prereg = json.loads(PREREG.read_text())
    positions = spec80_midi_positions()

    blocks = []
    for d in sorted(p for p in args.corpus.iterdir() if p.is_dir() and (p / "all_src.mid").is_file()):
        b = build(d)
        if b:
            blocks.append(b)
    if not blocks:
        print("no usable tracks", file=sys.stderr)
        return 2

    groups = np.concatenate([np.full(len(b["reg"]), b["track"]) for b in blocks])
    reg = np.concatenate([b["reg"] for b in blocks])
    spec01 = np.vstack([b["spec01"] for b in blocks])
    dsp6 = np.vstack([b["dsp6"] for b in blocks])
    est = estimators(spec01, positions)

    # --- controls first -----------------------------------------------------
    synth = 0.7 * dsp6[:, 0] - 0.3 * dsp6[:, 3] + 0.5 * dsp6[:, 1]
    c_machinery = grouped_oof(dsp6, synth, groups)
    perm = np.random.default_rng(1234).permutation(len(reg))
    c_shuffle = grouped_oof(np.column_stack(list(est.values()))[perm], reg, groups)
    controls = {
        "machinery_linear_recovery": {"r2": c_machinery["r2"], "requirement": ">= 0.95",
                                      "pass": bool(c_machinery["r2"] >= 0.95)},
        "shuffled_labels": {"r2": c_shuffle["r2"], "requirement": "<= 0.10",
                            "pass": bool(c_shuffle["r2"] <= 0.10)},
    }
    controls["all_pass"] = bool(controls["machinery_linear_recovery"]["pass"]
                                and controls["shuffled_labels"]["pass"])
    if not controls["all_pass"]:
        args.out.write_text(json.dumps({"job": "J3C", "verdict": "INVALID_RUN",
                                        "controls": controls}, indent=2) + "\n")
        print(json.dumps({"verdict": "INVALID_RUN", "controls": controls}, indent=2))
        return 1

    # --- Stage 1 ------------------------------------------------------------
    stage1 = {}
    for name, vals in est.items():
        raw_mae = float(np.mean(np.abs(reg - vals)))
        cal = grouped_oof(vals, reg, groups)
        per_track = {}
        for b in blocks:
            m = groups == b["track"]
            e = np.abs(reg[m] - cal["_oof"][m])
            per_track[b["track"]] = round(float(np.nanmean(e)), 3)
        stage1[name] = {
            "raw_mae_semitones_uncalibrated": round(raw_mae, 3),
            "oof_r2_after_affine_calibration": round(cal["r2"], 4),
            "oof_mae_semitones": round(cal["mae_semitones"], 3),
            "oof_median_abs_err_semitones": round(cal["median_abs_err_semitones"], 3),
            "per_track_mae": per_track,
            "n_scored": cal["n_scored"],
        }

    for wname in ("frozen", "decompressed"):
        cols = [est[f"{k}__{wname}"] for k in
                ("E1_midi_energy_centroid", "E2_weighted_median", "E3_q25", "E3_q75",
                 "E4_harmonic_sum_centroid")]
        r = grouped_oof(np.column_stack(cols), reg, groups)
        stage1[f"DETERMINISTIC_FEATURE_SET__{wname}"] = {
            "features": ["E1", "E2", "q25", "q75", "E4"],
            "oof_r2": round(r["r2"], 4),
            "oof_mae_semitones": round(r["mae_semitones"], 3),
            "oof_median_abs_err_semitones": round(r["median_abs_err_semitones"], 3),
            "n_scored": r["n_scored"],
        }

    best_name = max(stage1, key=lambda k: stage1[k]["oof_r2_after_affine_calibration"]
                    if "oof_r2_after_affine_calibration" in stage1[k] else stage1[k]["oof_r2"])
    bb = stage1[best_name]
    best_r2 = bb.get("oof_r2_after_affine_calibration", bb.get("oof_r2"))
    best_mae = bb["oof_mae_semitones"]

    lag = lag_sweep(est[f"E4_harmonic_sum_centroid__decompressed"], reg, groups)

    sufficient = best_r2 >= 0.70 and best_mae <= 3.0
    clearly_insufficient = best_r2 < 0.40 or best_mae > 4.5

    receipt = {
        "schema": "spectrasynq.register_frontend_result.v1",
        "job": "J3C",
        "label": "SYNTHETIC_UPPER_BOUND",
        "git_head": args.git_head,
        "preregistration": str(PREREG.relative_to(ROOT)),
        "preregistration_written_before_any_score": prereg["written_before_any_score"],
        "execution_environment": "Anthropic cloud container (HOST-class). Corpus md5 verified against the publisher's checksum.",
        "corpus": {"tracks": len(blocks), "frames_valid": int(len(reg)),
                   "target_mean_midi": round(float(reg.mean()), 2),
                   "target_sd_semitones": round(float(reg.std()), 2)},
        "grid": {"sr_hz": SR, "hop": HOP, "n_fft": N_FFT},
        "split": "grouped 5-fold, groups = track",
        "controls": controls,
        "stage_1_deterministic": stage1,
        "stage_1_best": {"estimator": best_name, "oof_r2": best_r2, "oof_mae_semitones": best_mae},
        "lag_diagnostic": lag,
        "lag_ok": bool(lag_ok(lag)),
        "student_io_frozen": False,
        "titan": False,
        "production_firmware_changed": False,
    }

    # --- Stage 2 (only if Stage 1 left the question open) -------------------
    if sufficient:
        receipt["stage_2_nonlinear"] = {"ran": False, "reason": "Stage 1 reached SUFFICIENT"}
        outcome = "REGISTER_FRONTEND_DSP"
    else:
        X2 = np.column_stack([np.log(spec80_decompress(spec01) + 1e-8)] +
                             [est[k] for k in est])
        s2 = {}
        for mname in ("gbm", "mlp"):
            r = grouped_oof(X2, reg, groups, model=mname)
            s2[mname] = {"oof_r2": round(r["r2"], 4),
                         "oof_mae_semitones": round(r["mae_semitones"], 3),
                         "oof_median_abs_err_semitones": round(r["median_abs_err_semitones"], 3)}
        r_sh = grouped_oof(X2[perm], reg, groups, model="gbm")
        s2["shuffled_label_control_gbm"] = {"oof_r2": round(r_sh["r2"], 4),
                                            "requirement": "<= 0.10",
                                            "pass": bool(r_sh["r2"] <= 0.10)}
        s2["ran"] = True
        s2["status"] = "INFORMATION PROBES ONLY - not product architecture"
        receipt["stage_2_nonlinear"] = s2
        best2_r2 = max(s2["gbm"]["oof_r2"], s2["mlp"]["oof_r2"])
        best2_mae = min(s2["gbm"]["oof_mae_semitones"], s2["mlp"]["oof_mae_semitones"])
        if best2_r2 >= 0.70 and best2_mae <= 3.0:
            outcome = "REGISTER_FRONTEND_LATENT"
        elif max(best_r2, best2_r2) < 0.55 and min(best_mae, best2_mae) > 3.5:
            outcome = "REGISTER_FRONTEND_INSUFFICIENT"
        else:
            outcome = "REGISTER_INCONCLUSIVE"

    if not lag_ok(lag):
        outcome = "REGISTER_INCONCLUSIVE"
        receipt["lag_note"] = "alignment fault under the inherited J3A amendment-2 rule"

    receipt["outcome"] = outcome
    receipt["thresholds_applied"] = prereg["thresholds"]
    receipt["what_this_says_about_visual_value"] = (
        "NOTHING. J3C measures recoverability from the existing frontend only. "
        "VALUE != RECOVERABILITY != COMPUTE COST."
    )
    receipt["forbidden_conclusions"] = prereg["construct_validity"][
        "broader_conclusions_that_remain_FORBIDDEN"]

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"outcome": outcome, "stage_1_best": receipt["stage_1_best"],
                      "stage_2": receipt.get("stage_2_nonlinear", {}).get("ran", False),
                      "controls": {k: v for k, v in controls.items() if k != "all_pass"}},
                     indent=2))
    print(f"receipt -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
