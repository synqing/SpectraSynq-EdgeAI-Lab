"""License-clean engineering comparison corpus.

Synthetic clips only in-git. Real datasets are manifest slots, never audio.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Callable

import numpy as np
import soundfile as sf

SR = 16_000
DURATION = 8.0


def _t(n: int) -> np.ndarray:
    return np.arange(n, dtype=np.float32) / SR


def sparse_ambient(n: int, rng: np.random.Generator) -> np.ndarray:
    t = _t(n)
    x = 0.08 * np.sin(2 * np.pi * 220 * t)
    x += 0.04 * np.sin(2 * np.pi * 330 * t)
    return x.astype(np.float32)


def percussion_dense(n: int, rng: np.random.Generator) -> np.ndarray:
    x = np.zeros(n, dtype=np.float32)
    step = int(0.12 * SR)
    for i, t0 in enumerate(range(0, n - 200, step)):
        length = min(int(0.08 * SR), n - t0)
        burst = rng.normal(0, 1, length).astype(np.float32)
        decay = np.exp(-np.linspace(0, 10, length)).astype(np.float32)
        x[t0 : t0 + length] += burst * decay * (0.9 if i % 4 == 0 else 0.45)
    peak = np.max(np.abs(x)) + 1e-8
    return (x / peak * 0.8).astype(np.float32)


def bass_drone(n: int, rng: np.random.Generator) -> np.ndarray:
    t = _t(n)
    return (0.6 * np.sin(2 * np.pi * 55 * t) + 0.2 * np.sin(2 * np.pi * 110 * t)).astype(
        np.float32
    )


def vocal_like(n: int, rng: np.random.Generator) -> np.ndarray:
    t = _t(n)
    f0 = 220.0
    vib = 3.0 * np.sin(2 * np.pi * 5.5 * t)
    x = np.zeros(n, dtype=np.float32)
    for k, a in enumerate((1.0, 0.5, 0.25, 0.12), start=1):
        x += a * np.sin(2 * np.pi * (k * f0) * t + vib)
    env = 0.3 + 0.7 * (0.5 + 0.5 * np.sin(2 * np.pi * 0.4 * t))
    return (x * env * 0.25).astype(np.float32)


def drop(n: int, rng: np.random.Generator) -> np.ndarray:
    x = sparse_ambient(n, rng) * 0.4
    cut = int(4.0 * SR)
    x[cut:] = percussion_dense(n - cut, rng) * 0.9
    return x.astype(np.float32)


def quiet_loud(n: int, rng: np.random.Generator) -> np.ndarray:
    t = _t(n)
    tone = 0.5 * np.sin(2 * np.pi * 330 * t)
    env = np.linspace(0.05, 1.0, n).astype(np.float32)
    return (tone * env).astype(np.float32)


def irregular_hits(n: int, rng: np.random.Generator) -> np.ndarray:
    x = np.zeros(n, dtype=np.float32)
    t0 = 0
    while t0 < n - 1000:
        length = int(rng.integers(int(0.04 * SR), int(0.15 * SR)))
        length = min(length, n - t0)
        burst = rng.normal(0, 1, length).astype(np.float32)
        decay = np.exp(-np.linspace(0, 8, length)).astype(np.float32)
        x[t0 : t0 + length] += burst * decay * 0.7
        t0 += int(rng.integers(int(0.2 * SR), int(1.4 * SR)))
    peak = np.max(np.abs(x)) + 1e-8
    return (x / peak * 0.75).astype(np.float32)


def mixed_full(n: int, rng: np.random.Generator) -> np.ndarray:
    x = 0.35 * bass_drone(n, rng) + 0.45 * percussion_dense(n, rng) + 0.35 * vocal_like(n, rng)
    peak = np.max(np.abs(x)) + 1e-8
    return (x / peak * 0.85).astype(np.float32)


CLIPS: dict[str, tuple[str, Callable]] = {
    "sparse_ambient": ("sparse / low energy / little percussion", sparse_ambient),
    "percussion_dense": ("dense regular hits", percussion_dense),
    "bass_drone": ("low-frequency mass, almost no transients", bass_drone),
    "vocal_like": ("harmonic midband with vibrato", vocal_like),
    "drop": ("quiet pad then percussion at t=4s", drop),
    "quiet_loud": ("slow amplitude ramp", quiet_loud),
    "irregular_hits": ("rhythmically complex / irregular onsets", irregular_hits),
    "mixed_full": ("bass + percussion + vocal-like together", mixed_full),
}

EXTERNAL_SLOTS = [
    {
        "id": "fma_cc_placeholder",
        "role": "real CC music diversity",
        "source": "FMA small / DEAM CC subset",
        "status": "not_downloaded",
        "licence": "per-track CC; do not commit unless permitted",
    },
    {
        "id": "musdb_sample_placeholder",
        "role": "stem-oracle comparison",
        "source": "musdb 7s excerpts or MUSDB_ROOT",
        "status": "not_downloaded",
        "licence": "MUSDB research/NC — see datasets/README.md",
    },
    {
        "id": "deam_placeholder",
        "role": "dynamic arousal/valence GT",
        "source": "https://cvml.unige.ch/databases/DEAM",
        "status": "not_downloaded",
        "licence": "UNKNOWN commercial; research likely ok with citation",
    },
]


def write_corpus(out_dir: Path, seed: int = 0) -> Path:
    rng = np.random.default_rng(seed)
    out_dir.mkdir(parents=True, exist_ok=True)
    n = int(SR * DURATION)
    items = []
    for cid, (desc, fn) in CLIPS.items():
        wav = fn(n, rng)
        path = out_dir / f"{cid}.wav"
        sf.write(path, wav, SR, subtype="PCM_16")
        items.append(
            {
                "id": cid,
                "path": str(path),
                "sr": SR,
                "duration_s": DURATION,
                "description": desc,
                "source": "synthetic",
                "licence": "generated in this repo; not a musical work",
            }
        )
    manifest = {
        "version": 1,
        "note": "Engineering comparison only. Not a training set. No third-party audio.",
        "clips": items,
        "external_slots": EXTERNAL_SLOTS,
    }
    mpath = out_dir / "manifest.json"
    mpath.write_text(json.dumps(manifest, indent=2) + "\n")
    return mpath
