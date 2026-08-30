"""Host-side golden vectors for later M85/Helium comparison. HOST-ONLY.

No M85 numbers. Titan arrival uses these as the DSP programme, independent
of the U55 semantic lane.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np


def goertzel(pcm: np.ndarray, sr: int, freq: float) -> complex:
    n = len(pcm)
    k = int(0.5 + (n * freq) / sr)
    w = 2.0 * np.pi * k / n
    coeff = 2.0 * np.cos(w)
    s0 = s1 = s2 = 0.0
    for x in pcm:
        s0 = x + coeff * s1 - s2
        s2, s1 = s1, s0
    return complex(s1 - s2 * np.cos(w), s2 * np.sin(w))


def make_vectors(out_dir: Path, sr: int = 16_000, n: int = 2048, seed: int = 0) -> dict:
    rng = np.random.default_rng(seed)
    t = np.arange(n) / sr
    pcm = (0.4 * np.sin(2 * np.pi * 440 * t) + 0.2 * np.sin(2 * np.pi * 880 * t) + 0.05 * rng.normal(0, 1, n)).astype(
        np.float32
    )
    spec = np.fft.rfft(pcm.astype(np.float64))
    mag = np.abs(spec).astype(np.float32)
    g440 = goertzel(pcm.astype(np.float64), sr, 440.0)
    window = np.hanning(n)
    spec_w = np.fft.rfft(pcm * window)
    out_dir.mkdir(parents=True, exist_ok=True)
    np.save(out_dir / "pcm.npy", pcm)
    np.save(out_dir / "rfft_mag.npy", mag)
    meta = {
        "label": "HOST-ONLY",
        "not": "M85 silicon",
        "sr": sr,
        "n": n,
        "seed": seed,
        "goertzel_440_abs": float(abs(g440)),
        "rfft_peak_bin": int(np.argmax(mag)),
        "rfft_peak_hz": float(np.argmax(mag) * sr / n),
        "kernels": ["rfft", "goertzel_440", "hann_rfft"],
        "purpose": "When Titan arrives, run the same PCM through M85/Helium kernels and diff.",
    }
    (out_dir / "meta.json").write_text(json.dumps(meta, indent=2) + "\n")
    np.save(out_dir / "hann_rfft_mag.npy", np.abs(spec_w).astype(np.float32))
    return meta
