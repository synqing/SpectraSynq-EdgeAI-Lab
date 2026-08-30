"""Source-activity teachers. Host only. No U55. No separator training.

We want envelopes, not a leaderboard. Optional backends:
- ground-truth stems (MUSDB/MoisesDB)
- HT-Demucs if installed (weights licence UNKNOWN — research)
- other separators via a future MSST wrapper
"""

from __future__ import annotations

from typing import Protocol

import numpy as np
from numpy.typing import NDArray


class Separator(Protocol):
    name: str

    def separate(self, pcm: NDArray[np.float32], sr: int) -> dict[str, NDArray[np.float32]]:
        ...


def activity_envelope(stem: NDArray[np.float32], sr: int, hop: int = 512) -> tuple[NDArray, NDArray]:
    stem = np.asarray(stem, dtype=np.float32).reshape(-1)
    n = len(stem)
    times, vals = [], []
    for i in range(0, n - hop + 1, hop):
        w = stem[i : i + hop]
        times.append((i + hop / 2) / sr)
        vals.append(float(np.sqrt(np.mean(w * w) + 1e-12)))
    v = np.array(vals, dtype=np.float32)
    peak = float(v.max() + 1e-8)
    return np.array(times, dtype=np.float32), (v / peak)


def hpss_stems(pcm: NDArray[np.float32], sr: int) -> dict[str, NDArray[np.float32]]:
    """Deterministic harmonic/percussive split. Not a neural separator.

    Used as a cheap source-activity baseline: if HPSS envelopes are already
    redundant with mix RMS, a Demucs teacher has a higher bar.
    """
    import librosa

    y = np.asarray(pcm, dtype=np.float32).reshape(-1)
    harmonic, percussive = librosa.effects.hpss(y)
    return {
        "harmonic": harmonic.astype(np.float32),
        "percussive": percussive.astype(np.float32),
        "mixture": y,
    }


def envelope_vs_mixture(
    stems: dict[str, NDArray[np.float32]], sr: int, hop: int = 512
) -> dict[str, float]:
    mix_t, mix_e = activity_envelope(stems["mixture"], sr, hop)
    out: dict[str, float] = {}
    for name, stem in stems.items():
        if name == "mixture":
            continue
        t, e = activity_envelope(stem, sr, hop)
        n = min(len(mix_e), len(e))
        a, b = mix_e[:n], e[:n]
        if n < 8 or float(a.std()) < 1e-8 or float(b.std()) < 1e-8:
            out[f"r_{name}_vs_mix_rms"] = float("nan")
        else:
            out[f"r_{name}_vs_mix_rms"] = float(np.corrcoef(a, b)[0, 1])
        out[f"{name}_peak"] = float(e.max())
    out["n_frames"] = int(len(mix_t))
    return out


def try_demucs() -> Separator | None:
    try:
        import demucs.api  # type: ignore
    except ImportError:
        return None

    class DemucsSep:
        name = "htdemucs"

        def separate(self, pcm: NDArray[np.float32], sr: int) -> dict[str, NDArray[np.float32]]:
            import torch

            wav = torch.from_numpy(np.stack([pcm, pcm]))  # stereo fake
            sep = demucs.api.Separator(model="htdemucs")
            _, stems = sep.separate_tensor(wav, sr)
            out = {}
            for k, v in stems.items():
                out[k] = v.mean(0).cpu().numpy().astype(np.float32)
            return out

    return DemucsSep()
