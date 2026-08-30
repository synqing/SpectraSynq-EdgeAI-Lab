#!/usr/bin/env python3
"""P2: Jamendo mood/theme via Discogs-EffNet + head. HOST-ONLY. CC BY-NC-SA weights."""

from __future__ import annotations

import json
import urllib.request
from pathlib import Path

import numpy as np

from edgeai.mir.deam import audio_path
from edgeai.mir.semantic_trace import write_trace

MODELS = Path("artifacts/essentia_models")
OUT = Path("artifacts/essentia_oracle")
SONG_IDS = (2030, 2034)
EFFNET = (
    "https://essentia.upf.edu/models/feature-extractors/discogs-effnet/discogs-effnet-bs64-1.pb",
    "discogs-effnet-bs64-1.pb",
)
HEAD = (
    "https://essentia.upf.edu/models/classification-heads/mtg_jamendo_moodtheme/"
    "mtg_jamendo_moodtheme-discogs-effnet-1.pb",
    "mtg_jamendo_moodtheme-discogs-effnet-1.pb",
)
HEAD_JSON = (
    "https://essentia.upf.edu/models/classification-heads/mtg_jamendo_moodtheme/"
    "mtg_jamendo_moodtheme-discogs-effnet-1.json",
    "mtg_jamendo_moodtheme-discogs-effnet-1.json",
)
# From MTG-Jamendo mood/theme subset (56). Lighting-relevant slice only.
WATCH = ("energetic", "dark", "relaxing", "dramatic", "dream", "party", "sad", "happy")


def _fetch(url: str, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.is_file() and dest.stat().st_size > 1000:
        return dest
    urllib.request.urlretrieve(url, dest)
    return dest


def main() -> int:
    _fetch(EFFNET[0], MODELS / EFFNET[1])
    _fetch(HEAD[0], MODELS / HEAD[1])
    meta_path = _fetch(HEAD_JSON[0], MODELS / HEAD_JSON[1])
    classes = json.loads(meta_path.read_text()).get("classes", [])
    watch_idx = {c: classes.index(c) for c in WATCH if c in classes}

    from essentia.standard import MonoLoader, TensorflowPredict2D, TensorflowPredictEffnetDiscogs

    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for sid in SONG_IDS:
        try:
            wav = str(audio_path(sid))
        except FileNotFoundError:
            continue
        audio = MonoLoader(filename=wav, sampleRate=16000, resampleQuality=4)()
        embedder = TensorflowPredictEffnetDiscogs(
            graphFilename=str(MODELS / EFFNET[1]),
            output="PartitionedCall:1",
        )
        embeddings = embedder(audio)
        model = TensorflowPredict2D(graphFilename=str(MODELS / HEAD[1]))
        pred = np.array(model(embeddings))
        n = pred.shape[0]
        dur = len(audio) / 16000.0
        times = np.linspace(0.0, dur, n, endpoint=False) + (dur / max(n, 1) / 2)
        means = {c: float(pred[:, i].mean()) for c, i in watch_idx.items()}
        stds = {c: float(pred[:, i].std()) for c, i in watch_idx.items()}
        rec = {
            "song_id": sid,
            "n_frames": int(n),
            "duration_s": dur,
            "watch_mean": means,
            "watch_std": stds,
            "weights": "CC BY-NC-SA",
        }
        print(json.dumps(rec), flush=True)
        rows.append(rec)
        frames = []
        for ti, row in zip(times, pred):
            fr = {"t": float(ti)}
            for c, i in watch_idx.items():
                fr[c] = float(row[i])
            frames.append(fr)
        write_trace(
            OUT / f"jamendo_mood_{sid}.jsonl",
            audio=wav,
            provenance=["discogs-effnet-bs64", "mtg_jamendo_moodtheme-discogs-effnet-1", "CC-BY-NC-SA"],
            frames=frames,
            extra_header={"song_id": sid, "classes_watch": list(watch_idx)},
        )

    receipt_path = OUT / "jamendo_receipt.json"
    receipt_path.write_text(
        json.dumps({"label": "HOST-ONLY", "weights": "CC BY-NC-SA", "songs": rows}, indent=2) + "\n"
    )
    print(f"wrote {receipt_path}")
    return 0 if rows else 2


if __name__ == "__main__":
    raise SystemExit(main())
