"""Human DEAM arousal vs deterministic DSP. No student training.

Question: does perceived arousal add information beyond energy?
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from edgeai.mir.conventional import extract as extract_conventional
from edgeai.mir.deam import AUDIO_DIR, cohort, load_arousal, audio_path
from edgeai.mir.semantic_trace import write_trace


def _load_mono(path: Path, sr: int = 16_000) -> np.ndarray:
    import librosa

    y, _ = librosa.load(str(path), sr=sr, mono=True)
    return y.astype(np.float32)


def _interp(times_src: np.ndarray, y: np.ndarray, times_dst: np.ndarray) -> np.ndarray:
    return np.interp(times_dst, times_src, y).astype(np.float32)


def _pearson(a: np.ndarray, b: np.ndarray) -> float:
    if a.size < 8 or a.std() < 1e-8 or b.std() < 1e-8:
        return float("nan")
    return float(np.corrcoef(a, b)[0, 1])


def _r2_ols(y: np.ndarray, X: np.ndarray) -> float:
    """Unregularised linear R². X is (n, f) already including intercept column."""
    if y.size < X.shape[1] + 2:
        return float("nan")
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    pred = X @ beta
    ss_res = float(np.sum((y - pred) ** 2))
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    if ss_tot < 1e-12:
        return float("nan")
    return 1.0 - ss_res / ss_tot


def analyse_song(song_id: int, audio_dir: Path | None = None) -> dict[str, Any] | None:
    try:
        wav = audio_path(song_id, audio_dir)
    except FileNotFoundError:
        return None
    arousal = load_arousal()
    if song_id not in arousal:
        return None
    t_gt, a_gt = arousal[song_id]
    pcm = _load_mono(wav)
    conv = extract_conventional(pcm, sr=16_000)
    t = conv["times"]
    feats = {
        "rms": _interp(t, conv["rms"], t_gt),
        "onset_env": _interp(t, conv["onset_env"], t_gt),
        "spectral_flux": _interp(t, conv["spectral_flux"], t_gt),
        "novelty": _interp(t, conv["novelty"], t_gt),
        "band_low": _interp(t, conv["band_low"], t_gt),
        "band_mid": _interp(t, conv["band_mid"], t_gt),
        "band_high": _interp(t, conv["band_high"], t_gt),
        "centroid": _interp(t, conv["spectral_centroid_hz"], t_gt),
    }
    # centroid to 0-1 by song for OLS
    c = feats["centroid"]
    feats["centroid_u"] = (c - c.min()) / (c.max() - c.min() + 1e-8)
    r = {k: _pearson(a_gt, v) for k, v in feats.items() if k != "centroid"}
    names = ["rms", "onset_env", "spectral_flux", "novelty", "band_low", "band_mid", "band_high"]
    X = np.column_stack([np.ones(len(a_gt))] + [feats[n] for n in names])
    r2 = _r2_ols(a_gt, X)
    # energy-only
    Xe = np.column_stack([np.ones(len(a_gt)), feats["rms"], feats["band_low"], feats["band_mid"], feats["band_high"]])
    r2_energy = _r2_ols(a_gt, Xe)
    residual = a_gt - (Xe @ np.linalg.lstsq(Xe, a_gt, rcond=None)[0])
    return {
        "song_id": song_id,
        "cohort": cohort(song_id),
        "n": int(len(a_gt)),
        "duration_s": float(t_gt[-1]),
        "pearson": r,
        "r2_energy": r2_energy,
        "r2_dsp_full": r2,
        "residual_std": float(np.std(residual)),
        "arousal_std": float(np.std(a_gt)),
        "t_gt": t_gt,
        "arousal": a_gt,
        "feats": feats,
        "audio": str(wav),
    }


def run_corpus(
    song_ids: list[int] | None = None,
    out_dir: Path | None = None,
    audio_dir: Path | None = None,
) -> dict[str, Any]:
    audio_dir = audio_dir or AUDIO_DIR
    if song_ids is None:
        song_ids = sorted(int(p.stem) for p in audio_dir.glob("*.mp3"))
    rows = []
    traces_dir = None
    if out_dir:
        traces_dir = out_dir / "traces"
        traces_dir.mkdir(parents=True, exist_ok=True)
    for sid in song_ids:
        rec = analyse_song(sid, audio_dir=audio_dir)
        if rec is None:
            continue
        slim = {k: rec[k] for k in ("song_id", "cohort", "n", "duration_s", "pearson", "r2_energy", "r2_dsp_full", "residual_std", "arousal_std")}
        rows.append(slim)
        if traces_dir:
            frames = []
            for i, t in enumerate(rec["t_gt"]):
                frames.append(
                    {
                        "t": float(t),
                        "arousal": float(rec["arousal"][i]),
                        "rms": float(rec["feats"]["rms"][i]),
                        "onset": float(rec["feats"]["onset_env"][i]),
                        "novelty": float(rec["feats"]["novelty"][i]),
                        "band_low": float(rec["feats"]["band_low"][i]),
                    }
                )
            write_trace(
                traces_dir / f"deam_{sid}.jsonl",
                audio=rec["audio"],
                provenance=["deam_human_arousal_2Hz", "librosa_conventional"],
                frames=frames,
                extra_header={"song_id": sid, "cohort": rec["cohort"]},
            )
        print(
            f"deam {sid:4d} {rec['cohort']:10s} r2_energy={rec['r2_energy']:.3f} "
            f"r2_dsp={rec['r2_dsp_full']:.3f} r_rms={rec['pearson']['rms']:.3f}",
            flush=True,
        )

    def _nanmean(xs):
        a = np.array(xs, dtype=np.float64)
        a = a[np.isfinite(a)]
        return float(np.mean(a)) if a.size else float("nan")

    by = {}
    for c in ("2013_clip", "2014_clip", "2015_full"):
        sub = [r for r in rows if r["cohort"] == c]
        if not sub:
            continue
        by[c] = {
            "n_songs": len(sub),
            "mean_r_rms": _nanmean([r["pearson"]["rms"] for r in sub]),
            "mean_r_flux": _nanmean([r["pearson"]["spectral_flux"] for r in sub]),
            "mean_r_onset": _nanmean([r["pearson"]["onset_env"] for r in sub]),
            "mean_r_novelty": _nanmean([r["pearson"]["novelty"] for r in sub]),
            "mean_r2_energy": _nanmean([r["r2_energy"] for r in sub]),
            "mean_r2_dsp_full": _nanmean([r["r2_dsp_full"] for r in sub]),
        }
    high_residual = sorted(rows, key=lambda r: r["r2_energy"] if np.isfinite(r["r2_energy"]) else 1.0)[:8]
    summary = {
        "label": "HOST-ONLY",
        "dataset": "DEAM",
        "note": (
            "Human 2 Hz arousal vs DSP. Annotations start ~15 s. "
            "2015_full has more reliable dynamic arousal (DEAM manual). "
            "r≈1 with RMS would mean NPU does not deserve this job."
        ),
        "n_songs": len(rows),
        "by_cohort": by,
        "high_residual_vs_energy": [
            {"song_id": r["song_id"], "cohort": r["cohort"], "r2_energy": r["r2_energy"], "r_rms": r["pearson"]["rms"]}
            for r in high_residual
        ],
        "songs": rows,
    }
    if out_dir:
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "receipt.json").write_text(json.dumps(summary, indent=2) + "\n")
    return summary
