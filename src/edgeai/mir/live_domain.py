"""Venue-domain degradation: CLEAN vs PA/ROOM vs PA/ROOM+CROWD.

PaRIRset (CC0) supplies real PA-through-FOH impulse responses.
Held-out venues are the `test` split — do not train on them.
CrowdioSet may add audience noise; record per-file licence before ingest.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from numpy.typing import NDArray


def convolve_rir(pcm: NDArray[np.float32], rir: NDArray[np.float32], mix: float = 1.0) -> NDArray[np.float32]:
    """pcm mono, rir mono or (N, 2). mix=1 is fully wet."""
    pcm = np.asarray(pcm, dtype=np.float32).reshape(-1)
    rir = np.asarray(rir, dtype=np.float32)
    if rir.ndim == 2:
        rir = rir.mean(axis=1)
    wet = np.convolve(pcm, rir, mode="full")[: len(pcm)]
    peak = float(np.max(np.abs(wet)) + 1e-8)
    wet = wet / peak * float(np.max(np.abs(pcm)) + 1e-8)
    out = (1.0 - mix) * pcm + mix * wet
    p = float(np.max(np.abs(out)) + 1e-8)
    return (out / p * 0.89).astype(np.float32)


def synthetic_room_ir(sr: int = 16_000, rt60: float = 1.4) -> NDArray[np.float32]:
    """NOT PaRIRset. Placeholder decay for plumbing tests only."""
    n = int(sr * min(2.5, rt60 * 2))
    t = np.arange(n, dtype=np.float32) / sr
    env = np.exp(-t * 6.91 / rt60)
    noise = np.random.default_rng(0).normal(0, 1, n).astype(np.float32)
    ir = noise * env
    ir[0] = 1.0
    return (ir / (np.max(np.abs(ir)) + 1e-8)).astype(np.float32)


def acoustic_path_delay_s(rir: NDArray[np.float32], sr: int) -> float:
    """Direct-path / propagation delay of an RIR, in seconds.

    This is ACOUSTIC latency — how long sound took to reach the microphone —
    not algorithm latency, not model context, not LED output latency.
    Keep it as its own measured variable. Do not fold it into "the model is slow".
    """
    from edgeai.mir.onset_align import direct_path_lag_samples

    _, lag_s = direct_path_lag_samples(rir, sr)
    return float(lag_s)


DOMAINS = ("CLEAN_STUDIO", "PA_ROOM", "PA_ROOM_CROWD")

# Hugging Face dataset tree. Test split = 8 held-out venues. Do not train on these.
PARIRSET_HF = "https://huggingface.co/datasets/enricguso/parirset/resolve/main"


def load_rir_wav(path: Path, sr: int = 16_000) -> NDArray[np.float32]:
    """Load a PaRIRset (or any) stereo/mono WAV, mix to mono, resample."""
    import soundfile as sf
    from math import gcd
    from scipy.signal import resample_poly

    y, file_sr = sf.read(str(path), always_2d=True)
    y = y.mean(axis=1).astype(np.float32)
    if int(file_sr) != int(sr) and y.size:
        g = gcd(int(sr), int(file_sr))
        y = resample_poly(y, int(sr) // g, int(file_sr) // g).astype(np.float32)
    peak = float(np.max(np.abs(y)) + 1e-8)
    return (y / peak).astype(np.float32)


def venue_from_parirset_name(name: str) -> str:
    """test/0000_01_olivenzaOutdoors_test.wav -> olivenzaOutdoors"""
    stem = Path(name).stem
    parts = stem.split("_")
    if len(parts) >= 3:
        return parts[2]
    return stem
