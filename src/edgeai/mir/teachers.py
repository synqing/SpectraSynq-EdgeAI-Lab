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
