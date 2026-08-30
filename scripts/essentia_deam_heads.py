#!/usr/bin/env python3
"""P2: MusiCNN embeddings + DEAM VA head on a few real DEAM files. HOST-ONLY."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from edgeai.mir.deam import audio_path, load_arousal
from edgeai.mir.semantic_trace import write_trace

MODELS = Path("artifacts/essentia_models")
OUT = Path("artifacts/essentia_oracle")


def run_song(song_id: int) -> dict:
    from essentia.standard import MonoLoader, TensorflowPredict2D, TensorflowPredictMusiCNN

    wav = str(audio_path(song_id))
    audio = MonoLoader(filename=wav, sampleRate=16000, resampleQuality=4)()
    embedder = TensorflowPredictMusiCNN(
        graphFilename=str(MODELS / "msd-musicnn-1.pb"),
        output="model/dense/BiasAdd",
    )
    tagger = TensorflowPredictMusiCNN(graphFilename=str(MODELS / "msd-musicnn-1.pb"))
    embeddings = embedder(audio)
    tags = tagger(audio)
    head = TensorflowPredict2D(
        graphFilename=str(MODELS / "deam-msd-musicnn-2.pb"),
        output="model/Identity",
    )
    va = np.array(head(embeddings))  # frames x 2  valence, arousal  ~[1,9]
    # hop of MusiCNN is typically 1s-ish; use linspace over audio duration
    dur = len(audio) / 16000.0
    n = va.shape[0] if va.ndim == 2 else 1
    times = np.linspace(0.0, dur, n, endpoint=False) + (dur / max(n, 1) / 2)
    if va.ndim == 1:
        va = va.reshape(1, -1)
    arousal_m = (va[:, 1] - 1.0) / 8.0  # crude map [1,9] -> [0,1]
    gt = load_arousal().get(song_id)
    r = None
    if gt:
        t_gt, a_gt = gt
        pred = np.interp(t_gt, times, arousal_m)
        if a_gt.std() > 1e-8 and pred.std() > 1e-8:
            r = float(np.corrcoef(a_gt, pred)[0, 1])
    frames = [{"t": float(t), "arousal_essentia": float(a)} for t, a in zip(times, arousal_m)]
    write_trace(
        OUT / f"essentia_deam_{song_id}.jsonl",
        audio=wav,
        provenance=["essentia_msd-musicnn", "deam-msd-musicnn-2", "CC-BY-NC-SA-weights"],
        frames=frames,
        extra_header={"song_id": song_id, "r_vs_human_arousal": r},
    )
    tag_mean = np.mean(np.array(tags), axis=0).tolist() if len(np.array(tags).shape) else []
    return {
        "song_id": song_id,
        "n_frames": int(n),
        "r_vs_human_arousal": r,
        "va_mean": [float(va[:, 0].mean()), float(va[:, 1].mean())],
        "n_tag_frames": int(np.array(tags).shape[0]) if np.array(tags).ndim else 0,
        "tag_mean_first8": tag_mean[:8],
    }


def main() -> int:
    if not (MODELS / "msd-musicnn-1.pb").is_file():
        print("missing models in artifacts/essentia_models")
        return 2
    OUT.mkdir(parents=True, exist_ok=True)
    # 2030 ≈ energy-like; 2034 ≈ high residual vs energy
    ids = [2030, 2034]
    rows = []
    for sid in ids:
        try:
            rec = run_song(sid)
        except FileNotFoundError:
            continue
        print(json.dumps(rec))
        rows.append(rec)
    (OUT / "receipt.json").write_text(
        json.dumps({"label": "HOST-ONLY", "weights": "CC BY-NC-SA", "songs": rows}, indent=2)
        + "\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
