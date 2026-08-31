"""Tiny causal mixture→share student. HOST-ONLY experiment. I/O not frozen.

Four sources (vocals, drums, bass, other). Not Semantic-v0's three CLASSES.
Share matches `source_oracle`: hop stem power / sum, silence → zeros not 1/4.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from numpy.typing import NDArray
from torch.utils.data import Dataset

from edgeai.dataset import SongRef, assert_no_song_leak, hash_split, stem_rms
from edgeai.frontend import LogMelFrontend
from edgeai.mir.source_oracle import SOURCES, frame_mean_square, log_rms_activity
from edgeai.semantic_v0 import count_parameters, fp32_nbytes

SILENCE_POWER = 1.0e-10
STEM_INDEX = ("mix", "drums", "bass", "other", "vocals")


def shares_from_powers(
    powers: NDArray | torch.Tensor,
    *,
    silent_thresh: float = SILENCE_POWER,
) -> NDArray | torch.Tensor:
    """Non-negative powers → share. Silence does not invent equal shares."""
    if isinstance(powers, torch.Tensor):
        total = powers.sum(dim=-1, keepdim=True)
        silent = total <= silent_thresh
        share = powers / total.clamp_min(silent_thresh)
        return torch.where(silent, torch.zeros_like(share), share)
    p = np.asarray(powers, dtype=np.float64)
    if p.ndim == 1:
        total = float(p.sum())
        if total <= silent_thresh:
            return np.zeros_like(p, dtype=np.float32)
        return (p / total).astype(np.float32)
    total = p.sum(axis=-1, keepdims=True)
    silent = total <= silent_thresh
    share = np.divide(p, np.clip(total, silent_thresh, None), dtype=np.float64)
    share = np.where(silent, 0.0, share)
    return share.astype(np.float32)


def window_powers_and_share(
    stems: Mapping[str, NDArray],
    *,
    hop: int = 512,
) -> tuple[np.ndarray, np.ndarray]:
    """Tiled hop mean-square → share. Same formula as source_oracle."""
    powers = np.array(
        [float(np.sum(frame_mean_square(stems[name], hop))) for name in SOURCES],
        dtype=np.float64,
    )
    return powers.astype(np.float32), shares_from_powers(powers)


def window_mix_rms(mix: NDArray) -> float:
    return float(log_rms_activity(np.array([stem_rms(mix)], dtype=np.float32))[0])


def pearson(a: NDArray, b: NDArray) -> float:
    n = min(int(np.asarray(a).size), int(np.asarray(b).size))
    if n < 8:
        return float("nan")
    x = np.asarray(a, dtype=np.float64).reshape(-1)[:n]
    y = np.asarray(b, dtype=np.float64).reshape(-1)[:n]
    if x.std() < 1e-12 or y.std() < 1e-12:
        return float("nan")
    return float(np.corrcoef(x, y)[0, 1])


# ---------------------------------------------------------------------------
# Model — causal DS-CNN, AdaptiveAvgPool2d (D11). Experiment graph, not a lock.
# ---------------------------------------------------------------------------


class CausalConvBNReLU(nn.Module):
    """Conv2d with left-only time pad. Freq is symmetric."""

    def __init__(
        self,
        cin: int,
        cout: int,
        k_f: int = 3,
        k_t: int = 3,
        stride_t: int = 1,
        groups: int = 1,
    ):
        super().__init__()
        self.pad_f = k_f // 2
        self.left = k_t - 1
        self.conv = nn.Conv2d(
            cin,
            cout,
            kernel_size=(k_f, k_t),
            stride=(1, stride_t),
            padding=0,
            groups=groups,
            bias=False,
        )
        self.bn = nn.BatchNorm2d(cout)
        self.act = nn.ReLU(inplace=False)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = F.pad(x, (self.left, 0, self.pad_f, self.pad_f))
        return self.act(self.bn(self.conv(x)))


class CausalDS(nn.Module):
    def __init__(self, cin: int, cout: int, stride_t: int = 1):
        super().__init__()
        self.dw = CausalConvBNReLU(cin, cin, stride_t=stride_t, groups=cin)
        self.pw = nn.Sequential(
            nn.Conv2d(cin, cout, kernel_size=1, bias=False),
            nn.BatchNorm2d(cout),
            nn.ReLU(inplace=False),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.pw(self.dw(x))


@dataclass
class ShareStudentConfig:
    stem_channels: int = 24
    blocks: tuple[tuple[int, int], ...] = (
        (48, 2),
        (48, 1),
        (64, 2),
        (64, 1),
        (96, 1),
    )
    n_sources: int = 4
    dropout: float = 0.1


class ShareStudent(nn.Module):
    """Log-mel → 4 non-negative powers → share. Not a product I/O contract."""

    def __init__(self, cfg: ShareStudentConfig | None = None):
        super().__init__()
        cfg = cfg or ShareStudentConfig()
        if cfg.n_sources != len(SOURCES):
            raise ValueError(f"n_sources must be {len(SOURCES)}, got {cfg.n_sources}")
        self.cfg = cfg
        layers: list[nn.Module] = [CausalConvBNReLU(1, cfg.stem_channels)]
        cin = cfg.stem_channels
        for cout, stride_t in cfg.blocks:
            layers.append(CausalDS(cin, cout, stride_t=stride_t))
            cin = cout
        self.features = nn.Sequential(*layers)
        self.pool = nn.AdaptiveAvgPool2d((1, 1))
        self.dropout = nn.Dropout(cfg.dropout) if cfg.dropout > 0 else nn.Identity()
        self.head = nn.Linear(cin, cfg.n_sources)

    def forward(self, logmel: torch.Tensor) -> dict[str, torch.Tensor]:
        x = self.features(logmel)
        x = self.pool(x)
        x = torch.flatten(x, 1)
        x = self.dropout(x)
        logits = self.head(x)
        # softplus so the head is trainable (relu+negative bias is a dead silent region).
        # Threshold matches source_oracle: only ~zero total power becomes all-zero share.
        powers = F.softplus(logits)
        shares = shares_from_powers(powers, silent_thresh=SILENCE_POWER)
        return {"logits": logits, "powers": powers, "shares": shares}


def share_loss(pred: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
    """MSE on share. Silent frames (target all-zero) stay in the loss."""
    return F.mse_loss(pred, target)


# ---------------------------------------------------------------------------
# MUSDB resolve + window bank. Song is the split unit.
# ---------------------------------------------------------------------------


def resolve_musdb_root(explicit: Path | str | None = None) -> Path | None:
    candidates: list[Path] = []
    if explicit:
        candidates.append(Path(explicit))
    env = os.environ.get("MUSDB_ROOT")
    if env:
        candidates.append(Path(env))
    candidates.append(Path("datasets/musdb18"))
    seen: set[Path] = set()
    for raw in candidates:
        for c in (raw, raw / "musdb18"):
            try:
                c = c.resolve()
            except OSError:
                continue
            if c in seen:
                continue
            seen.add(c)
            if (c / "train").is_dir() and (c / "test").is_dir():
                return c
    return None


def assert_full_musdb(root: Path) -> None:
    """Reject 7 s excerpts. Feasibility close needs full STEMS songs."""
    files = sorted(p for p in (root / "train").iterdir() if p.suffix == ".mp4")[:3]
    if not files:
        raise FileNotFoundError(f"no .mp4 stems under {root / 'train'}")
    sizes = [f.stat().st_size for f in files]
    if min(sizes) < 5_000_000:
        raise RuntimeError(
            f"MUSDB at {root} looks like 7s excerpts "
            f"(smallest train mp4 {min(sizes)} bytes). "
            "datasets/musdb_sample is screening only, not this close."
        )


def musdb_song_split(root: Path, seed: int = 0, val_frac: float = 0.15) -> list[SongRef]:
    """Official train/test folders; val carved from train by hashed song id."""
    train_dir = root / "train"
    test_dir = root / "test"
    if not train_dir.is_dir() or not test_dir.is_dir():
        raise FileNotFoundError(f"expected {train_dir} and {test_dir}")

    def names(folder: Path) -> list[str]:
        return sorted(
            p.name for p in folder.iterdir() if p.is_dir() or p.suffix in {".mp4"}
        )

    songs: list[SongRef] = []
    for name in names(train_dir):
        song_id = f"musdb18/train/{name}"
        split = hash_split(song_id, seed, val_frac, 100, 0)
        songs.append(SongRef(song_id=song_id, split=split, source="musdb18"))
    for name in names(test_dir):
        songs.append(SongRef(song_id=f"musdb18/test/{name}", split="test", source="musdb18"))
    assert_no_song_leak(songs)
    return songs


def song_mp4(root: Path, song: SongRef) -> Path:
    parts = song.song_id.split("/", 2)
    if len(parts) != 3:
        raise ValueError(f"bad musdb song_id: {song.song_id}")
    path = root / parts[1] / parts[2]
    if not path.is_file():
        raise FileNotFoundError(path)
    return path


def _mono_16k(x: np.ndarray, src_sr: int, dst_sr: int) -> np.ndarray:
    y = np.asarray(x, dtype=np.float32)
    if y.ndim == 2:
        y = y.mean(axis=-1)
    if src_sr != dst_sr:
        import torchaudio

        t = torch.from_numpy(np.ascontiguousarray(y)).unsqueeze(0)
        y = torchaudio.functional.resample(t, src_sr, dst_sr).squeeze(0).numpy()
    return y.astype(np.float32)


def load_song_stems_16k(path: Path, dst_sr: int = 16_000) -> dict[str, np.ndarray]:
    import stempeg

    audio, rate = stempeg.read_stems(str(path))
    src_sr = int(rate)
    if not isinstance(audio, np.ndarray) or audio.ndim < 2:
        raise RuntimeError(f"unexpected stems shape from {path}")
    if audio.shape[0] < 5:
        raise RuntimeError(f"expected 5 stem streams, got {audio.shape} at {path}")
    out: dict[str, np.ndarray] = {}
    for i, name in enumerate(STEM_INDEX):
        out[name] = _mono_16k(audio[i], src_sr, dst_sr)
    return out


def safe_name(song: SongRef) -> str:
    raw = song.song_id.replace("/", "__")
    return "".join(ch if ch.isalnum() or ch in "-_." else "_" for ch in raw)


def take_songs(songs: Sequence[SongRef], split: str, n: int | None, seed: int) -> list[SongRef]:
    xs = [s for s in songs if s.split == split]
    if n is None or n >= len(xs):
        return xs
    rng = np.random.default_rng(seed)
    pick = rng.choice(len(xs), size=int(n), replace=False)
    return [xs[i] for i in sorted(int(i) for i in pick)]


@dataclass
class WindowBank:
    logmel: np.ndarray
    share: np.ndarray
    mix_rms: np.ndarray
    powers: np.ndarray
    song_ids: list[str]

    def __len__(self) -> int:
        return int(self.share.shape[0])


class ShareWindowDataset(Dataset):
    def __init__(self, bank: WindowBank):
        self.bank = bank

    def __len__(self) -> int:
        return len(self.bank)

    def __getitem__(self, idx: int) -> dict[str, torch.Tensor | str]:
        return {
            "logmel": torch.from_numpy(self.bank.logmel[idx]),
            "share": torch.from_numpy(self.bank.share[idx]),
            "mix_rms": torch.tensor(self.bank.mix_rms[idx], dtype=torch.float32),
            "powers": torch.from_numpy(self.bank.powers[idx]),
            "song_id": self.bank.song_ids[idx],
        }


def slice_window(
    stems: Mapping[str, np.ndarray],
    mix: np.ndarray,
    start: int,
    n_samples: int,
    hop: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, float]:
    sl = slice(start, start + n_samples)
    mix_w = mix[sl]
    stem_w = {name: stems[name][sl] for name in SOURCES}
    powers, share = window_powers_and_share(stem_w, hop=hop)
    return mix_w, powers, share, window_mix_rms(mix_w)


def featurize_starts(
    stems: Mapping[str, np.ndarray],
    mix: np.ndarray,
    starts: Sequence[int],
    frontend: LogMelFrontend,
    hop: int,
    *,
    mel_batch: int = 32,
) -> WindowBank:
    n_samples = frontend.cfg.n_samples
    mixes: list[np.ndarray] = []
    shares: list[np.ndarray] = []
    mix_rms: list[float] = []
    powers: list[np.ndarray] = []
    for start in starts:
        mix_w, pwr, share, mrms = slice_window(stems, mix, int(start), n_samples, hop)
        mixes.append(np.ascontiguousarray(mix_w))
        shares.append(share)
        mix_rms.append(mrms)
        powers.append(pwr)
    logmels: list[np.ndarray] = []
    with torch.no_grad():
        for i in range(0, len(mixes), mel_batch):
            pcm = torch.from_numpy(np.stack(mixes[i : i + mel_batch]))
            logmels.append(frontend(pcm).cpu().numpy())
    return WindowBank(
        logmel=np.concatenate(logmels, axis=0).astype(np.float32),
        share=np.stack(shares, axis=0).astype(np.float32),
        mix_rms=np.asarray(mix_rms, dtype=np.float32),
        powers=np.stack(powers, axis=0).astype(np.float32),
        song_ids=[""] * len(shares),
    )


def concat_banks(banks: Sequence[WindowBank]) -> WindowBank:
    if not banks:
        raise ValueError("no windows")
    return WindowBank(
        logmel=np.concatenate([b.logmel for b in banks], axis=0),
        share=np.concatenate([b.share for b in banks], axis=0),
        mix_rms=np.concatenate([b.mix_rms for b in banks], axis=0),
        powers=np.concatenate([b.powers for b in banks], axis=0),
        song_ids=[sid for b in banks for sid in b.song_ids],
    )


def random_starts(n_audio: int, n_samples: int, n_windows: int, rng: np.random.Generator) -> list[int]:
    max_start = n_audio - n_samples
    if max_start < 0:
        return []
    if max_start == 0:
        return [0] * n_windows
    return [int(x) for x in rng.integers(0, max_start + 1, size=n_windows)]


def grid_starts(n_audio: int, n_samples: int, hop_samples: int) -> list[int]:
    max_start = n_audio - n_samples
    if max_start < 0:
        return []
    return list(range(0, max_start + 1, hop_samples))


def fit_mix_linear_baseline(
    mix_rms: np.ndarray,
    share: np.ndarray,
) -> np.ndarray:
    """4 independent affine maps mix_rms → share_k, then renormalise.

    This is the mix-energy baseline a student must beat. It cannot see spectrum.
    """
    mix = np.asarray(mix_rms, dtype=np.float64).reshape(-1)
    y = np.asarray(share, dtype=np.float64)
    coef = np.zeros((4, 2), dtype=np.float64)
    for k in range(4):
        if mix.std() < 1e-12:
            coef[k, 0] = 0.0
            coef[k, 1] = float(np.mean(y[:, k]))
        else:
            a, b = np.polyfit(mix, y[:, k], 1)
            coef[k, 0], coef[k, 1] = float(a), float(b)
    return coef


def apply_mix_linear_baseline(mix_rms: np.ndarray, coef: np.ndarray) -> np.ndarray:
    mix = np.asarray(mix_rms, dtype=np.float64).reshape(-1, 1)
    raw = np.clip(mix * coef[:, 0] + coef[:, 1], 0.0, None)
    return shares_from_powers(raw)


def within_track_rows(
    share_true: np.ndarray,
    share_pred: np.ndarray,
    mix_rms: np.ndarray,
    song_ids: Sequence[str],
) -> dict[str, dict[str, float]]:
    """Per-source mean within-track Pearson. Songs with <8 windows dropped."""
    songs = list(dict.fromkeys(song_ids))
    out: dict[str, dict[str, float]] = {}
    for i, name in enumerate(SOURCES):
        r_pt: list[float] = []
        r_pm: list[float] = []
        r_tm: list[float] = []
        n_ok = 0
        for sid in songs:
            idx = np.array([j for j, s in enumerate(song_ids) if s == sid], dtype=np.int64)
            if idx.size < 8:
                continue
            n_ok += 1
            t = share_true[idx, i]
            p = share_pred[idx, i]
            m = mix_rms[idx]
            r_pt.append(pearson(p, t))
            r_pm.append(pearson(p, m))
            r_tm.append(pearson(t, m))
        def _mean(xs: list[float]) -> float:
            ys = [x for x in xs if np.isfinite(x)]
            return float(np.mean(ys)) if ys else float("nan")

        out[name] = {
            "r_pred_true": _mean(r_pt),
            "r_pred_mix": _mean(r_pm),
            "r_true_mix": _mean(r_tm),
            "n_songs": float(n_ok),
        }
    return out


def verdict_from_metrics(
    student: dict[str, dict[str, float]],
    linear: dict[str, dict[str, float]],
    n_test_songs: int,
) -> str:
    """Pre-registered recoverability call. Not a student-I/O freeze."""
    if n_test_songs < 8:
        return "INCONCLUSIVE"
    core = ("vocals", "drums", "bass")
    beats_mix = []
    beats_lin = []
    copies_mix = []
    for name in core:
        s, lin = student[name], linear[name]
        rt, rm = s["r_pred_true"], s["r_true_mix"]
        rp = s["r_pred_mix"]
        if not np.isfinite(rt) or not np.isfinite(rm):
            return "INCONCLUSIVE"
        beats_mix.append(rt >= max(0.30, rm + 0.15))
        copies_mix.append(np.isfinite(rp) and rp > rm + 0.20)
        lr = lin["r_pred_true"]
        beats_lin.append(np.isfinite(lr) and rt > lr + 0.05)
    if all(beats_mix) and all(beats_lin) and not any(copies_mix):
        return "PASS"
    deltas = [student[k]["r_pred_true"] - student[k]["r_true_mix"] for k in core]
    if all((not np.isfinite(d)) or d < 0.08 for d in deltas):
        return "FAIL"
    return "INCONCLUSIVE"


__all__ = [
    "SOURCES",
    "SILENCE_POWER",
    "ShareStudent",
    "ShareStudentConfig",
    "ShareWindowDataset",
    "WindowBank",
    "assert_full_musdb",
    "assert_no_song_leak",
    "count_parameters",
    "fp32_nbytes",
    "shares_from_powers",
    "window_powers_and_share",
    "resolve_musdb_root",
    "musdb_song_split",
]
