#!/usr/bin/env python3
"""Delay-aware PaRIRset onset scoring.

HOST-ONLY. Held-out test venues only. Does not ingest CrowdioSet.
Does not train. Replaces zero-lag-on-2Hz as the onset authority.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from edgeai.mir.conventional import extract_onset_bundle
from edgeai.mir.deam import audio_path, load_arousal
from edgeai.mir.live_domain import load_rir_wav, venue_from_parirset_name, convolve_rir
from edgeai.mir.onset_align import (
    advance_pcm,
    direct_path_lag_samples,
    downsample_to_times,
    onset_prf,
    pearson,
    pick_onset_times,
    xcorr_lag_frames,
)
from edgeai.mir.semantic_trace import write_trace

CACHE = Path("datasets/parirset/test")
OUT = Path("artifacts/parirset_probe")
SONG_IDS = (2030, 2034, 2041)
SR = 16_000
HOP = 512
MAX_LAG_S = 0.5


def _load_mono(path: Path, sr: int = SR) -> np.ndarray:
    import librosa

    y, _ = librosa.load(str(path), sr=sr, mono=True)
    return y.astype(np.float32)


def _legacy_2hz_r(clean_f: dict, wet_f: dict, t_gt: np.ndarray) -> float:
    c = downsample_to_times(clean_f["times"], clean_f["onset_env"], t_gt)
    w = downsample_to_times(wet_f["times"], wet_f["onset_env"], t_gt)
    return pearson(c, w)


def _score_pair(clean_f: dict, other_f: dict, window_s: float) -> dict:
    ref = pick_onset_times(clean_f["onset_env"], clean_f["times"])
    est = pick_onset_times(other_f["onset_env"], other_f["times"])
    prf = onset_prf(ref, est, window_s=window_s)
    return {
        f"f1_{int(window_s * 1000)}": prf["f1"],
        f"precision_{int(window_s * 1000)}": prf["precision"],
        f"recall_{int(window_s * 1000)}": prf["recall"],
        f"n_ref": prf["n_ref"],
        f"n_est": prf["n_est"],
        f"mean_jitter_s_{int(window_s * 1000)}": prf["mean_jitter_s"],
    }


def _classify(row: dict) -> str:
    f1_u = row["f1_50_unaligned"]
    f1_a = row["f1_50_aligned"]
    rec_a = row["recall_50_aligned"]
    prec_a = row["precision_50_aligned"]
    if f1_a >= 0.7 and f1_u < 0.4:
        return "onset_delayed"
    if f1_a >= 0.7:
        return "onset_preserved"
    if rec_a < 0.4 and prec_a >= 0.5:
        return "onset_events_missed"
    if prec_a < 0.4 and rec_a >= 0.5:
        return "false_onsets_introduced"
    if f1_a < 0.4:
        return "onset_smeared_or_collapsed"
    return "onset_degraded_partial"


def main() -> int:
    rir_paths = sorted(CACHE.glob("*_test.wav"))
    if not rir_paths:
        print(f"no PaRIRset test WAVs in {CACHE}")
        return 2

    arousal = load_arousal()
    OUT.mkdir(parents=True, exist_ok=True)
    traces = OUT / "traces_aligned"
    traces.mkdir(exist_ok=True)

    rirs = []
    for path in rir_paths:
        rir = load_rir_wav(path, sr=SR)
        lag, lag_s = direct_path_lag_samples(rir, SR)
        rec = {
            "file": path.name,
            "venue": venue_from_parirset_name(path.name),
            "split": "test",
            "n_samples": int(rir.size),
            "rir": rir,
            "direct_path_samples": lag,
            "direct_path_s": lag_s,
        }
        rirs.append(rec)
        print(
            f"rir {path.name} venue={rec['venue']} dur={rir.size / SR:.3f}s "
            f"direct_path={lag_s * 1000:.1f}ms",
            flush=True,
        )

    hop_s = HOP / SR
    max_lag_frames = int(round(MAX_LAG_S / hop_s))
    rows = []
    for sid in SONG_IDS:
        try:
            wav = audio_path(sid)
        except FileNotFoundError:
            print(f"skip missing audio {sid}", flush=True)
            continue
        if sid not in arousal:
            print(f"skip missing arousal {sid}", flush=True)
            continue
        t_gt, a_gt = arousal[sid]
        clean = _load_mono(wav)
        clean_f = extract_onset_bundle(clean, sr=SR, hop=HOP)
        print(f"song {sid} n={clean.size} clean_frames={clean_f['times'].size}", flush=True)
        for r in rirs:
            wet = convolve_rir(clean, r["rir"], mix=1.0)
            wet_f = extract_onset_bundle(wet, sr=SR, hop=HOP)
            aligned = advance_pcm(wet, r["direct_path_samples"])
            al_f = extract_onset_bundle(aligned, sr=SR, hop=HOP)
            xlag = xcorr_lag_frames(
                clean_f["onset_env"], wet_f["onset_env"], max_lag_frames=max_lag_frames
            )
            u50 = _score_pair(clean_f, wet_f, 0.05)
            a50 = _score_pair(clean_f, al_f, 0.05)
            u100 = _score_pair(clean_f, wet_f, 0.10)
            a100 = _score_pair(clean_f, al_f, 0.10)
            rec = {
                "song_id": sid,
                "venue": r["venue"],
                "rir_file": r["file"],
                "split": "test",
                "direct_path_s": r["direct_path_s"],
                "xcorr_lag_s": float(xlag) * hop_s,
                "r_rms_zero_lag": pearson(clean_f["rms"], wet_f["rms"]),
                "r_rms_aligned": pearson(clean_f["rms"], al_f["rms"]),
                "r_onset_native_zero_lag": pearson(clean_f["onset_env"], wet_f["onset_env"]),
                "r_onset_native_aligned": pearson(clean_f["onset_env"], al_f["onset_env"]),
                "r_onset_legacy_2hz_zero_lag": _legacy_2hz_r(clean_f, wet_f, t_gt),
                "r_onset_legacy_2hz_aligned": _legacy_2hz_r(clean_f, al_f, t_gt),
                "r_flux_native_zero_lag": pearson(clean_f["spectral_flux"], wet_f["spectral_flux"]),
                "r_flux_native_aligned": pearson(clean_f["spectral_flux"], al_f["spectral_flux"]),
                "f1_50_unaligned": u50["f1_50"],
                "precision_50_unaligned": u50["precision_50"],
                "recall_50_unaligned": u50["recall_50"],
                "jitter_50_unaligned_s": u50["mean_jitter_s_50"],
                "f1_50_aligned": a50["f1_50"],
                "precision_50_aligned": a50["precision_50"],
                "recall_50_aligned": a50["recall_50"],
                "jitter_50_aligned_s": a50["mean_jitter_s_50"],
                "f1_100_unaligned": u100["f1_100"],
                "f1_100_aligned": a100["f1_100"],
                "n_ref_onsets": u50["n_ref"],
                "n_est_unaligned": u50["n_est"],
                "n_est_aligned": a50["n_est"],
                "label": "HOST-ONLY",
                "domain": "PA_ROOM",
            }
            rec["verdict"] = _classify(rec)
            print(json.dumps({k: v for k, v in rec.items() if k != "label"}), flush=True)
            rows.append(rec)
            frames = []
            # Native hop is too dense for a 2 Hz visual trace; store 2 Hz RMS/onset.
            c_on = downsample_to_times(clean_f["times"], clean_f["onset_env"], t_gt)
            w_on = downsample_to_times(wet_f["times"], wet_f["onset_env"], t_gt)
            a_on = downsample_to_times(al_f["times"], al_f["onset_env"], t_gt)
            c_rms = downsample_to_times(clean_f["times"], clean_f["rms"], t_gt)
            w_rms = downsample_to_times(wet_f["times"], wet_f["rms"], t_gt)
            for i, t in enumerate(t_gt):
                frames.append(
                    {
                        "t": float(t),
                        "arousal": float(a_gt[i]),
                        "rms_clean": float(c_rms[i]),
                        "rms_wet": float(w_rms[i]),
                        "onset_clean": float(c_on[i]),
                        "onset_wet": float(w_on[i]),
                        "onset_wet_aligned": float(a_on[i]),
                    }
                )
            write_trace(
                traces / f"deam_{sid}_{r['venue']}_aligned.jsonl",
                audio=str(wav),
                provenance=[
                    "deam_human_arousal_2Hz",
                    "parirset_test",
                    r["file"],
                    "delay_compensated_onset",
                ],
                frames=frames,
                extra_header={
                    "song_id": sid,
                    "venue": r["venue"],
                    "split": "test",
                    "direct_path_s": r["direct_path_s"],
                    "verdict": rec["verdict"],
                    "signals": {
                        "arousal": {
                            "range": "DEAM human, typically about -1 to 1 on this export",
                            "cadence_hz": 2,
                            "provenance": "DEAM human annotations",
                        },
                        "onset_wet_aligned": {
                            "range": "[0,1] peak-normalised envelope",
                            "cadence_hz": 2,
                            "smoothing": "none",
                            "provenance": "librosa onset_strength after RIR direct-path advance",
                        },
                    },
                },
            )

    n = len(rows)
    def _mean(key: str) -> float:
        xs = [row[key] for row in rows if np.isfinite(row[key])]
        return float(np.mean(xs)) if xs else float("nan")

    receipt = {
        "label": "HOST-ONLY",
        "dataset": "PaRIRset test split + DEAM",
        "licence": "PaRIRset CC0; DEAM research/UNKNOWN commercial",
        "held_out_venues_intact": True,
        "crowdioset_ingested": False,
        "method": {
            "convolve": "causal numpy.convolve full, truncated to original length",
            "direct_path": "argmax |RIR| after resample to 16 kHz",
            "align": "advance wet PCM by direct-path samples, re-extract",
            "onset_grid": "native hop 512 @ 16 kHz (~32 ms); legacy 2 Hz kept only as a trap metric",
            "events": "scipy find_peaks on unit onset envelope; greedy F1 at 50 ms and 100 ms",
        },
        "n_comparisons": n,
        "summary": {
            "mean_direct_path_s": _mean("direct_path_s"),
            "mean_r_onset_legacy_2hz_zero_lag": _mean("r_onset_legacy_2hz_zero_lag"),
            "mean_r_onset_native_zero_lag": _mean("r_onset_native_zero_lag"),
            "mean_r_onset_native_aligned": _mean("r_onset_native_aligned"),
            "mean_f1_50_unaligned": _mean("f1_50_unaligned"),
            "mean_f1_50_aligned": _mean("f1_50_aligned"),
            "mean_f1_100_unaligned": _mean("f1_100_unaligned"),
            "mean_f1_100_aligned": _mean("f1_100_aligned"),
            "mean_r_rms_zero_lag": _mean("r_rms_zero_lag"),
            "mean_r_rms_aligned": _mean("r_rms_aligned"),
        },
        "verdict_counts": {},
        "rows": rows,
    }
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["verdict"]] = counts.get(row["verdict"], 0) + 1
    receipt["verdict_counts"] = counts
    out_path = OUT / "receipt_aligned.json"
    out_path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(f"wrote {out_path}")
    print(json.dumps(receipt["summary"], indent=2))
    print("verdicts", counts)
    return 0 if rows else 2


if __name__ == "__main__":
    raise SystemExit(main())
