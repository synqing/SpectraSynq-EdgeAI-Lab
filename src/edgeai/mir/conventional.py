"""Deterministic MIR descriptors (librosa). HOST-ONLY. Not an NPU graph."""

from __future__ import annotations

from typing import Any

import numpy as np

try:
    import librosa
except ImportError as exc:  # pragma: no cover
    raise ImportError("uv sync --extra mir") from exc


def extract(pcm: np.ndarray, sr: int = 16_000, hop: int = 512) -> dict[str, Any]:
    """Return time-aligned traces. times is hop-centred, seconds."""
    y = np.asarray(pcm, dtype=np.float32).reshape(-1)
    n_fft = 2048
    S = np.abs(librosa.stft(y, n_fft=n_fft, hop_length=hop))
    times = librosa.frames_to_time(np.arange(S.shape[1]), sr=sr, hop_length=hop)
    rms = librosa.feature.rms(S=S)[0]
    centroid = librosa.feature.spectral_centroid(S=S, sr=sr)[0]
    flux = np.sqrt(np.sum(np.diff(S, axis=1, prepend=S[:, :1]) ** 2, axis=0))
    onset_env = librosa.onset.onset_strength(S=librosa.amplitude_to_db(S, ref=np.max), sr=sr)
    freqs = librosa.fft_frequencies(sr=sr, n_fft=n_fft)
    band = _band_energy(S, freqs)
    chroma = librosa.feature.chroma_stft(S=S, sr=sr)
    chroma_var = chroma.var(axis=0)
    novelty = _novelty(S)
    tempo, beats = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr, hop_length=hop)
    beat_times = librosa.frames_to_time(beats, sr=sr, hop_length=hop)
    return {
        "sr": sr,
        "hop": hop,
        "times": times.astype(np.float32),
        "rms": _unit(rms),
        "spectral_centroid_hz": centroid.astype(np.float32),
        "spectral_flux": _unit(flux),
        "onset_env": _unit(onset_env),
        "band_low": _unit(band["low"]),
        "band_mid": _unit(band["mid"]),
        "band_high": _unit(band["high"]),
        "chroma_var": chroma_var.astype(np.float32),
        "novelty": _unit(novelty),
        "tempo_bpm": float(np.asarray(tempo).reshape(-1)[0]),
        "beat_times": beat_times.astype(np.float32),
        "provenance": {
            "extractor": "librosa",
            "task": "conventional MIR",
            "label": "HOST-ONLY",
        },
    }


def _band_energy(S: np.ndarray, freqs: np.ndarray) -> dict[str, np.ndarray]:
    def e(lo: float, hi: float) -> np.ndarray:
        m = (freqs >= lo) & (freqs < hi)
        if not np.any(m):
            return np.zeros(S.shape[1], dtype=np.float32)
        return np.sum(S[m, :] ** 2, axis=0).astype(np.float32)

    return {"low": e(40, 200), "mid": e(200, 2000), "high": e(2000, 8000)}


def _novelty(S: np.ndarray, lag: int = 4) -> np.ndarray:
    """Cheap spectral self-similarity novelty (not Foote checkerboard)."""
    v = S / (np.linalg.norm(S, axis=0, keepdims=True) + 1e-8)
    sim = np.sum(v * np.roll(v, lag, axis=1), axis=0)
    return np.maximum(0.0, 1.0 - sim).astype(np.float32)


def _unit(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=np.float32)
    peak = float(np.max(x) + 1e-8)
    return (x / peak).astype(np.float32)
