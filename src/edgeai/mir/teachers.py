"""Source-activity teachers. Host only. No U55. No separator training.

We want envelopes, not a leaderboard. Optional backends:
- ground-truth stems (MUSDB/MoisesDB)
- HT-Demucs if installed (weights licence UNKNOWN — research)
- other separators via a future MSST wrapper

Demucs is a HOST teacher probe, not architecture:
- Refuse Titan / U55 / PDM. SPECTRASYNQ_TITAN set → not allowed.
- Refuse auto-download. No torch.hub, no dl.fbaipublicfiles.com, no
  demucs.api.Separator(repo=None). Named weight GO + local repo first.
- ImportError → None. demucs is not a pyproject extra.
"""

from __future__ import annotations

import os
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


def demucs_host_allowed() -> bool:
    """True only when demucs.api imports and SPECTRASYNQ_TITAN is unset.

    HOST-ONLY. Refuse Titan. Refuse auto-download of weights.
    """
    if "SPECTRASYNQ_TITAN" in os.environ:
        return False
    try:
        import demucs.api  # type: ignore  # noqa: F401
    except ImportError:
        return False
    return True


def try_demucs() -> Separator | None:
    """Optional HT-Demucs handle. ImportError → None.

    Does not construct demucs.api.Separator. Does not download weights.
    SPECTRASYNQ_TITAN → None even if the package is present.
    """
    # Refuse Titan before import, Separator, or any hub fetch.
    if "SPECTRASYNQ_TITAN" in os.environ:
        return None
    try:
        import demucs.api  # type: ignore
    except ImportError:
        return None
    if not demucs_host_allowed():
        return None

    class DemucsSep:
        name = "htdemucs"
        _api = demucs.api  # imported; Separator is not constructed here

        def separate(self, pcm: NDArray[np.float32], sr: int) -> dict[str, NDArray[np.float32]]:
            # pcm/sr unused: refuse-auto-download returns before any tensor work.
            # Refuse Titan on every call, not only at handle creation.
            if not demucs_host_allowed():
                raise RuntimeError("Demucs HOST: refuse Titan")
            # Refuse auto-download. Do not call Separator unless import
            # succeeded — it has — and never with repo=None (torch.hub /
            # dl.fbaipublicfiles.com). Named weight GO + local repo first.
            raise RuntimeError(
                "Demucs HOST: refuse auto-download. Do not call "
                "demucs.api.Separator without a named weight GO and a local repo."
            )

    return DemucsSep()
