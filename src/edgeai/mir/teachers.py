"""Source-activity teachers. Host only. No U55. No separator training.

We want envelopes, not a leaderboard. Optional backends:
- ground-truth stems (MUSDB/MoisesDB)
- HT-Demucs if installed (weights licence UNKNOWN — research)
- other separators via a future MSST wrapper

Demucs is a HOST teacher probe, not architecture:
- Refuse Titan / U55 / PDM. SPECTRASYNQ_TITAN set → not allowed.
- Refuse auto-download. No torch.hub, no dl.fbaipublicfiles.com, no
  demucs.api.Separator with repo=None. Named weight GO + local repo first.
  SPECTRASYNQ_DEMUCS_NAMED_GO and SPECTRASYNQ_DEMUCS_LOCAL are not a
  licence to construct a separator this session.
- ImportError → None. demucs is not a pyproject extra.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Mapping, Protocol

import numpy as np
from numpy.typing import NDArray

from edgeai.mir.source_oracle import SOURCES, frame_mean_square, source_oracle


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


def share_from_stems(
    stems: Mapping[str, NDArray],
    sr: int,
    hop: int = 512,
) -> dict[str, NDArray[np.float32]]:
    """Four-way hop share (vocals/drums/bass/other). Wraps source_oracle.

    Missing stem → zeros. Silence → zeros, not 1/4. HOST-ONLY.
    """
    oracle = source_oracle(stems, sr=sr, hop=hop)
    return {name: oracle[f"{name}_share"] for name in SOURCES}


def envelopes_from_stems(
    stems: Mapping[str, NDArray],
    sr: int,
    hop: int = 512,
) -> dict[str, object]:
    """Hop mean-square powers + four-way share including other.

    Caller MUST discard stem waveforms after this returns. Teacher signal
    is envelopes, not PCM. Same four names as source_oracle. HOST-ONLY.
    """
    oracle = source_oracle(stems, sr=sr, hop=hop)
    n = int(oracle["times"].size)
    power: dict[str, NDArray[np.float32]] = {}
    for name in SOURCES:
        if name in stems:
            p = np.asarray(frame_mean_square(stems[name], hop), dtype=np.float32)
        else:
            p = np.zeros(n, dtype=np.float32)
        if p.size >= n:
            p = p[:n]
        else:
            pad = np.zeros(n, dtype=np.float32)
            pad[: p.size] = p
            p = pad
        power[name] = p
    return {
        "times": oracle["times"],
        "power": power,
        "share": {name: oracle[f"{name}_share"] for name in SOURCES},
    }


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
    SPECTRASYNQ_DEMUCS_NAMED_GO + local path still do not construct
    a separator this session.
    """
    # Refuse Titan before import, separator construction, or any hub fetch.
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
            # Never construct demucs.api.Separator this session — not with
            # repo=None, and not with named GO + SPECTRASYNQ_DEMUCS_LOCAL.
            raise RuntimeError(
                "Demucs HOST: not constructing Separator this session. "
                "Refuse auto-download. Named weight GO + local repo first."
            )

    return DemucsSep()


def local_htdemucs_checkpoint() -> Path | None:
    """Path from SPECTRASYNQ_DEMUCS_LOCAL if that file exists, else None.

    Existence only. Does not load tensors. Does not construct a separator.
    Inventory is not a named GO.
    """
    raw = os.environ.get("SPECTRASYNQ_DEMUCS_LOCAL", "").strip()
    if not raw:
        return None
    path = Path(raw).expanduser()
    if path.is_file():
        return path
    return None
