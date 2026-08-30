"""Run extractors over the eval corpus; write aligned JSON+NPZ."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import soundfile as sf
import torch

from edgeai.mir.conventional import extract as extract_conventional


def _resample(pcm: np.ndarray, sr: int, target: int) -> np.ndarray:
    if sr == target:
        return pcm.astype(np.float32)
    import torchaudio

    t = torch.from_numpy(pcm.astype(np.float32)).unsqueeze(0)
    y = torchaudio.functional.resample(t, sr, target).squeeze(0).numpy()
    return y.astype(np.float32)


def maybe_semantic_v0(pcm16k: np.ndarray, ckpt: Path | None) -> dict[str, Any] | None:
    if ckpt is None or not ckpt.is_file():
        return None
    from edgeai.config import LabConfig
    from edgeai.export import load_backbone
    from edgeai.frontend import LogMelFrontend

    model, lab = load_backbone(ckpt)
    fe = LogMelFrontend(lab.frontend)
    fe.eval()
    model.eval()
    n = lab.frontend.n_samples
    hop = n // 2  # 50% overlap, HOST-ONLY experiment
    times, vocals, drums, bass = [], [], [], []
    with torch.no_grad():
        for start in range(0, max(1, len(pcm16k) - n + 1), hop):
            w = pcm16k[start : start + n]
            if len(w) < n:
                w = np.pad(w, (0, n - len(w)))
            logmel = fe(torch.from_numpy(w).unsqueeze(0))
            p = torch.sigmoid(model(logmel)).numpy()[0]
            times.append((start + n / 2) / lab.frontend.sample_rate)
            vocals.append(float(p[0]))
            drums.append(float(p[1]))
            bass.append(float(p[2]))
    return {
        "times": np.array(times, dtype=np.float32),
        "vocals": np.array(vocals, dtype=np.float32),
        "drums": np.array(drums, dtype=np.float32),
        "bass": np.array(bass, dtype=np.float32),
        "provenance": {
            "extractor": "semantic_v0_experiment",
            "checkpoint": str(ckpt),
            "label": "HOST-ONLY",
            "authority": "experiment — not product",
        },
    }


def run_clip(wav_path: Path, ckpt: Path | None = None) -> dict[str, Any]:
    pcm, sr = sf.read(wav_path, always_2d=False)
    if pcm.ndim > 1:
        pcm = pcm.mean(axis=1)
    pcm = pcm.astype(np.float32)
    pcm16 = _resample(pcm, sr, 16_000)
    conv = extract_conventional(pcm16, sr=16_000)
    sem = maybe_semantic_v0(pcm16, ckpt)
    return {
        "clip": wav_path.stem,
        "path": str(wav_path),
        "conventional": _to_jsonable(conv),
        "semantic_v0_experiment": _to_jsonable(sem) if sem else None,
        "dsp_vs_ml_note": (
            "band_low is a deterministic bass-energy proxy. If it tracks "
            "semantic_v0 bass, the CNN is redundant with DSP on this clip."
        ),
    }


def _to_jsonable(obj: Any) -> Any:
    if obj is None:
        return None
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, dict):
        return {k: _to_jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (np.floating, np.integer)):
        return float(obj)
    return obj


def correlation_report(trace: dict[str, Any]) -> dict[str, float]:
    sem = trace.get("semantic_v0_experiment")
    conv = trace["conventional"]
    if not sem:
        return {}
    t_c = np.array(conv["times"])
    t_s = np.array(sem["times"])

    def interp(name_c: str, name_s: str) -> float:
        yc = np.interp(t_s, t_c, np.array(conv[name_c]))
        ys = np.array(sem[name_s])
        if ys.std() < 1e-8 or yc.std() < 1e-8:
            return float("nan")
        return float(np.corrcoef(yc, ys)[0, 1])

    return {
        "bass_vs_band_low": interp("band_low", "bass"),
        "drums_vs_onset_env": interp("onset_env", "drums"),
        "drums_vs_spectral_flux": interp("spectral_flux", "drums"),
        "vocals_vs_band_mid": interp("band_mid", "vocals"),
        "any_vs_rms_drums": interp("rms", "drums"),
    }
