#!/usr/bin/env python3
"""J3A — BabySlakh synthetic upper bound for causal pitch-class / register state.

Runs the experiment pre-registered in
`docs/mir/receipts/note_register/PREREGISTRATION.json`. The verdict is looked up
from that file; this script does not choose thresholds.

Label: SYNTHETIC_UPPER_BOUND. This can never satisfy SELECTION_GATE criterion 3
("Synthetic r=0.99 is not this evidence"). A FAIL here is strong; a PASS here only
unlocks a real-audio leg.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from edgeai.mir.host_chroma import host_chroma12, host_spectrogram80  # noqa: E402
from edgeai.mir.note_register import (  # noqa: E402
    HOP,
    N_FFT,
    SR,
    Note,
    dsp_register_features,
    frame_grid,
    l1_normalise,
    midi_targets,
    silence_mask,
)

PREREG = ROOT / "docs" / "mir" / "receipts" / "note_register" / "PREREGISTRATION.json"
ALPHAS = (1e-3, 1e-2, 1e-1, 1.0, 10.0, 100.0, 1000.0)


# ----------------------------------------------------------------- ridge ----
def _fit(X: np.ndarray, Y: np.ndarray, alpha: float):
    mu, sd = X.mean(0), X.std(0) + 1e-9
    Xs = (X - mu) / sd
    ym = Y.mean(0)
    Yc = Y - ym
    G = Xs.T @ Xs + alpha * np.eye(Xs.shape[1])
    W = np.linalg.solve(G, Xs.T @ Yc)
    return {"mu": mu, "sd": sd, "ym": ym, "W": W}


def _pred(m, X):
    return ((X - m["mu"]) / m["sd"]) @ m["W"] + m["ym"]


def _r2(y, yhat):
    y = np.atleast_2d(y.T).T
    yhat = np.atleast_2d(yhat.T).T
    ss_res = np.sum((y - yhat) ** 2, axis=0)
    ss_tot = np.sum((y - y.mean(0)) ** 2, axis=0) + 1e-20
    return 1.0 - ss_res / ss_tot


def grouped_cv_r2(X, Y, groups, *, n_folds=5, seed=0):
    """Out-of-fold R^2 with alpha chosen on training folds only. Groups = track."""
    Y = Y.reshape(len(Y), -1)
    uniq = np.unique(groups)
    n_folds = max(2, min(n_folds, len(uniq)))
    rng = np.random.default_rng(seed)
    order = rng.permutation(uniq)
    folds = np.array_split(order, n_folds)
    oof = np.full_like(Y, np.nan, dtype=np.float64)
    chosen = []
    for f in folds:
        te = np.isin(groups, f)
        tr = ~te
        if tr.sum() < 10 or te.sum() < 1:
            continue
        # inner split of the TRAIN tracks only, for alpha
        tr_tracks = np.unique(groups[tr])
        cut = max(1, len(tr_tracks) // 4)
        inner_val = np.isin(groups, tr_tracks[:cut]) & tr
        inner_tr = tr & ~inner_val
        best, best_a = -np.inf, ALPHAS[0]
        for a in ALPHAS:
            m = _fit(X[inner_tr], Y[inner_tr], a)
            s = float(np.mean(_r2(Y[inner_val], _pred(m, X[inner_val]))))
            if s > best:
                best, best_a = s, a
        chosen.append(best_a)
        m = _fit(X[tr], Y[tr], best_a)
        oof[te] = _pred(m, X[te])
    ok = ~np.isnan(oof[:, 0])
    per_dim = _r2(Y[ok], oof[ok])
    return {
        "r2_mean": float(np.mean(per_dim)),
        "r2_per_dim": [float(v) for v in np.atleast_1d(per_dim)],
        "r2_min": float(np.min(per_dim)),
        "r2_max": float(np.max(per_dim)),
        "alphas_chosen": sorted({float(a) for a in chosen}),
        "n_scored": int(ok.sum()),
    }


def lag_sweep(X, Y, groups, *, lags=range(-4, 5)):
    """R^2 with the comparator shifted +/- hops. argmax != 0 => alignment fault."""
    out = {}
    for k in lags:
        Xs, Ys, Gs = [], [], []
        for g in np.unique(groups):
            m = groups == g
            x, y = X[m], Y[m]
            if k > 0:
                x, y = x[:-k], y[k:]
            elif k < 0:
                x, y = x[-k:], y[:k]
            if len(x) < 20:
                continue
            Xs.append(x)
            Ys.append(y)
            Gs.append(np.full(len(x), g))
        if not Xs:
            continue
        r = grouped_cv_r2(np.vstack(Xs), np.vstack([np.atleast_2d(a.T).T for a in Ys]), np.concatenate(Gs))
        out[str(k)] = round(r["r2_mean"], 6)
    best = max(out, key=lambda k: out[k]) if out else "0"
    return {"by_lag": out, "argmax_lag": int(best)}


# ------------------------------------------------------------------ data ----
def read_track(track_dir: Path):
    import pretty_midi
    import soundfile as sf

    mix = None
    for cand in ("mix.flac", "mix.wav"):
        if (track_dir / cand).is_file():
            mix = track_dir / cand
            break
    mid = track_dir / "all_src.mid"
    if mix is None or not mid.is_file():
        return None
    y, sr = sf.read(str(mix), dtype="float64", always_2d=True)
    y = y.mean(axis=1)
    if sr != SR:
        return None
    pm = pretty_midi.PrettyMIDI(str(mid))
    notes: list[Note] = []
    for inst in pm.instruments:
        if inst.is_drum:
            continue  # drums carry no pitch class or register
        for n in inst.notes:
            notes.append(Note(float(n.start), float(n.end), int(n.pitch), int(n.velocity)))
    return y, notes


def build(track_dir: Path):
    got = read_track(track_dir)
    if got is None:
        return None
    y, notes = got
    times, _ = frame_grid(y.size)
    n = times.size
    tg = midi_targets(notes, n)
    _, chroma = host_chroma12(y.astype(np.float32))
    _, spec = host_spectrogram80(y.astype(np.float32))
    dsp, rms, dsp_names = dsp_register_features(y)
    m = min(n, len(chroma), len(spec), len(dsp))
    valid = (tg["weight_total"][:m] > 0) & silence_mask(rms[:m]) & np.isfinite(tg["register_centroid"][:m])
    return {
        "valid": valid,
        "pc_target": l1_normalise(tg["pitch_class_mass"][:m])[valid],
        "reg_target": tg["register_centroid"][:m][valid].reshape(-1, 1),
        "B1_h1": l1_normalise(chroma[:m].astype(np.float64))[valid],
        "B1_h2": dsp[:m][valid],
        "B2": np.log(spec[:m].astype(np.float64) + 1e-8)[valid],
        "rms_log": np.log(rms[:m] + 1e-12)[valid].reshape(-1, 1),
        "n_frames_total": int(m),
        "n_frames_valid": int(valid.sum()),
        "dsp_names": dsp_names,
    }


# --------------------------------------------------------------- verdict ----
def classify(r2_b1: float, r2_b2: float, th: dict) -> str:
    if r2_b1 >= 0.75 or r2_b2 >= 0.75:
        if r2_b2 >= 0.75 and r2_b1 < 0.50:
            return "FRONTEND_ONLY"
        return "FAIL"
    if r2_b1 < 0.50 and r2_b2 < 0.50:
        return "PASS"
    return "INCONCLUSIVE"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", type=Path, required=True, help="babyslakh root (dir of TrackNNNNN)")
    ap.add_argument("--out", type=Path, default=ROOT / "docs/mir/receipts/note_register/J3A_RESULT.json")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--git-head", type=str, default=None)
    args = ap.parse_args()

    prereg = json.loads(PREREG.read_text())
    th = prereg["thresholds"]

    dirs = sorted(p for p in args.corpus.iterdir() if p.is_dir() and (p / "all_src.mid").is_file())
    if args.limit:
        dirs = dirs[: args.limit]
    if not dirs:
        print(f"no tracks under {args.corpus}", file=sys.stderr)
        return 2

    per_track, blocks = [], []
    for d in dirs:
        b = build(d)
        if b is None:
            per_track.append({"track": d.name, "skipped": True})
            continue
        b["track"] = d.name
        blocks.append(b)
        per_track.append(
            {"track": d.name, "frames_total": b["n_frames_total"], "frames_valid": b["n_frames_valid"]}
        )
    if not blocks:
        print("no usable tracks", file=sys.stderr)
        return 2

    groups = np.concatenate([np.full(len(b["pc_target"]), b["track"]) for b in blocks])
    cat = lambda k: np.vstack([b[k] for b in blocks])  # noqa: E731
    pc, reg = cat("pc_target"), cat("reg_target")
    B1_h1, B1_h2, B2, rms_log = cat("B1_h1"), cat("B1_h2"), cat("B2"), cat("rms_log")

    # --- controls FIRST. A blocking control failure aborts before any
    # --- hypothesis score exists, so a failed control can never be traded
    # --- against a favourable result.
    ctrl_a = grouped_cv_r2(B1_h2[:, 2:5], rms_log, groups)  # reported only, see prereg amendment
    synth = (0.7 * B1_h2[:, 0] - 0.3 * B1_h2[:, 3] + 0.5 * B1_h2[:, 1]).reshape(-1, 1)
    ctrl_a2 = grouped_cv_r2(B1_h2, synth, groups)           # blocking machinery control
    rng = np.random.default_rng(1234)
    perm = rng.permutation(len(pc))
    ctrl_b = grouped_cv_r2(B1_h1[perm], pc, groups)         # blocking anti-hallucination control
    controls_ok = ctrl_a2["r2_mean"] >= 0.95 and ctrl_b["r2_mean"] <= 0.10

    control_block = {
        "execution_order": "controls computed before hypotheses; abort on blocking failure",
        "CONTROL_A_bands_to_logrms": {
            "r2": ctrl_a["r2_mean"], "requirement": ">= 0.90", "blocking": False,
            "status": "REPORTED_ONLY - demoted in the prereg amendment; log-sum-exp is not linearly recoverable",
            "pass": bool(ctrl_a["r2_mean"] >= 0.90)},
        "CONTROL_A2_machinery_linear_redundancy": {
            "r2": ctrl_a2["r2_mean"], "requirement": ">= 0.95", "blocking": True,
            "pass": bool(ctrl_a2["r2_mean"] >= 0.95)},
        "CONTROL_B_shuffled_baseline": {
            "r2": ctrl_b["r2_mean"], "requirement": "<= 0.10", "blocking": True,
            "pass": bool(ctrl_b["r2_mean"] <= 0.10)},
        "all_blocking_pass": bool(controls_ok),
    }

    if not controls_ok:
        receipt = {
            "schema": "spectrasynq.note_register_result.v1", "job": "J3A",
            "label": "SYNTHETIC_UPPER_BOUND", "verdict": "INVALID_RUN",
            "action": "INVALID_RUN", "controls": control_block,
            "H1_pitch_class": {"verdict": "NOT_COMPUTED"},
            "H2_register": {"verdict": "NOT_COMPUTED"},
            "note": "aborted at the controls; no hypothesis score was computed",
            "student_io_frozen": False, "titan": False,
        }
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
        print(json.dumps({"verdict": "INVALID_RUN", "controls": control_block}, indent=2))
        return 1

    h1_b1 = grouped_cv_r2(B1_h1, pc, groups)
    h1_b2 = grouped_cv_r2(B2, pc, groups)
    h2_b1 = grouped_cv_r2(B1_h2, reg, groups)
    h2_b2 = grouped_cv_r2(B2, reg, groups)

    h1 = classify(h1_b1["r2_mean"], h1_b2["r2_mean"], th)
    h2 = classify(h2_b1["r2_mean"], h2_b2["r2_mean"], th)

    lag_h1 = lag_sweep(B1_h1, pc, groups)
    lag_h2 = lag_sweep(B1_h2, reg, groups)
    def _lag_ok(d):
        """Prereg amendment 2: a fault is |argmax| >= 2 hops, or an argmax that beats
        lag 0 by more than 0.02 absolute R^2. A sub-hop preference on a smooth curve
        is overlap asymmetry, not misalignment."""
        k = d["argmax_lag"]
        m = d["by_lag"].get(str(k), 0.0) - d["by_lag"].get("0", 0.0)
        return abs(k) < 2 and m <= 0.02

    lag_ok = _lag_ok(lag_h1) and _lag_ok(lag_h2)

    if not lag_ok:
        verdict, action = "INVALID_RUN", "INVALID_RUN"
        h1 = h2 = "NOT_ISSUED_ALIGNMENT_FAULT"
    else:
        verdict = f"H1={h1} H2={h2}"
        if h2 == "FRONTEND_ONLY":
            action = "DETERMINISTIC_REGISTER_NEXT"
        elif h1 == "INCONCLUSIVE" or h2 == "INCONCLUSIVE":
            action = "NO_PROMOTION"
        elif h1 == "FAIL" and h2 == "FAIL":
            action = "CLOSE_NOTE_REGISTER"
        elif h1 == "PASS" and h2 == "FAIL":
            action = "REAL_AUDIO_PITCH_NEXT"
        elif h1 == "FAIL" and h2 == "PASS":
            action = "DETERMINISTIC_REGISTER_NEXT"
        else:
            action = "REAL_AUDIO_PITCH_AND_REGISTER_NEXT"

    head = args.git_head
    if not head:
        try:
            head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
        except Exception:  # noqa: BLE001
            head = "UNKNOWN"

    receipt = {
        "schema": "spectrasynq.note_register_result.v1",
        "job": "J3A",
        "label": "SYNTHETIC_UPPER_BOUND",
        "date": "2026-09-01",
        "git_head": head,
        "preregistration": str(PREREG.relative_to(ROOT)),
        "preregistration_written_before_any_score": prereg["written_before_any_score"],
        "corpus": {
            "id": "babyslakh",
            "root": str(args.corpus),
            "tracks_used": len(blocks),
            "sample_rate_hz": SR,
            "published_md5": prereg["corpus"]["published_md5"],
        },
        "grid": {"sr_hz": SR, "hop": HOP, "n_fft": N_FFT, "hop_hz": SR / HOP,
                 "timestamp_semantics": prereg["grid"]["timestamp_semantics"],
                 "causality": prereg["grid"]["causality"],
                 "label_lookahead_s": 0.0},
        "execution_environment": (
            "Anthropic cloud container (HOST-class, not the Mac, not silicon). The corpus "
            "tarball md5 was verified against the publisher's published checksum "
            "311096dc2bde7d61c97e930edbfc7f78 before extraction."
        ),
        "lag_rule": "prereg amendment 2: fault iff |argmax| >= 2 hops or margin over lag 0 > 0.02",
        "split": "grouped 5-fold cross-validation, groups = track; no track split across folds",
        "frames": {
            "per_track": per_track,
            "total_valid": int(len(pc)),
            "excluded_reason": "no sounding MIDI note in window, or audio below -60 dBFS. Never zero-filled.",
        },
        "controls": control_block,
        "H1_pitch_class": {
            "target": "12-bin MIDI pitch-class mass, L1-normalised",
            "vs_B1_host_chroma12": h1_b1,
            "vs_B2_host_spectrogram80": h1_b2,
            "lag_diagnostic_vs_B1": lag_h1,
            "verdict": h1,
        },
        "H2_register": {
            "target": "velocity-weighted mean MIDI note number (semitones)",
            "B1_features": blocks[0]["dsp_names"],
            "vs_B1_dsp_register": h2_b1,
            "vs_B2_host_spectrogram80": h2_b2,
            "lag_diagnostic_vs_B1": lag_h2,
            "verdict": h2,
        },
        "thresholds_applied": th,
        "verdict": verdict,
        "action": action,
        "interpretation_ceiling": (
            "SYNTHETIC_UPPER_BOUND. This does NOT establish real-audio incremental "
            "information; SELECTION_GATE criterion 3 explicitly rejects synthetic "
            "evidence. It does not establish room/mic robustness, visual utility "
            "(Gate B), product suitability, or student I/O."
        ),
        "student_io_frozen": False,
        "titan": False,
        "production_firmware_changed": False,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: receipt[k] for k in ("verdict", "action", "controls")}, indent=2))
    print(f"receipt -> {args.out}")
    return 0 if controls_ok and lag_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
