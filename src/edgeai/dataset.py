"""Stem mixing, synthetic songs, optional MUSDB, song-level splits.

Windows are NEVER the split unit. A song id is wholly train, val, or test.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

import numpy as np
import torch
from torch.utils.data import Dataset

from edgeai.config import CLASSES, FrontendConfig, LabConfig, TrainConfig
from edgeai.frontend import LogMelFrontend

SILENCE_RMS = 1.0e-4
LOUD_RMS = 0.15


def _rng(seed: int) -> np.random.Generator:
    return np.random.default_rng(seed)


def stem_rms(x: np.ndarray) -> float:
    return float(np.sqrt(np.mean(np.square(x), dtype=np.float64) + 1e-12))


def activity_from_rms(rms: float) -> float:
    lo = math.log10(SILENCE_RMS)
    hi = math.log10(LOUD_RMS)
    v = (math.log10(rms + 1e-12) - lo) / (hi - lo)
    return float(min(1.0, max(0.0, v)))


def activities_from_stems(stems: dict[str, np.ndarray]) -> np.ndarray:
    return np.array(
        [activity_from_rms(stem_rms(stems[name])) for name in CLASSES],
        dtype=np.float32,
    )


def apply_gain(x: np.ndarray, gain_db: float) -> np.ndarray:
    return (x * (10.0 ** (gain_db / 20.0))).astype(np.float32)


def maybe_mute(x: np.ndarray, mute: bool) -> np.ndarray:
    return np.zeros_like(x) if mute else x


def random_eq(x: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Tiny random FIR — cheap channel colour, not a production EQ."""
    taps = rng.normal(0.0, 0.25, size=5).astype(np.float32)
    taps[2] += 1.0
    taps /= np.linalg.norm(taps) + 1e-8
    y = np.convolve(x, taps, mode="same").astype(np.float32)
    return y


def add_noise(x: np.ndarray, rng: np.random.Generator, snr_db: float) -> np.ndarray:
    sig = stem_rms(x)
    if sig < 1e-8:
        return x
    noise = rng.normal(0.0, 1.0, size=x.shape).astype(np.float32)
    n_rms = stem_rms(noise)
    target = sig / (10.0 ** (snr_db / 20.0))
    return (x + noise * (target / (n_rms + 1e-8))).astype(np.float32)


# ---------------------------------------------------------------------------
# Synthetic stems. These prove the pipeline. They are NOT musical ground truth.
# A model that scores well here may be using band energy, not "drum-ness".
# MUSDB (or a cleared corpus) is required before any product claim.
# ---------------------------------------------------------------------------

def synth_drums(n: int, sr: int, rng: np.random.Generator) -> np.ndarray:
    x = np.zeros(n, dtype=np.float32)
    n_hits = int(rng.integers(1, 9))
    for _ in range(n_hits):
        t0 = int(rng.integers(0, max(1, n - 200)))
        length = int(rng.integers(int(0.02 * sr), int(0.22 * sr)))
        length = min(length, n - t0)
        burst = rng.normal(0.0, 1.0, size=length).astype(np.float32)
        decay = np.exp(-np.linspace(0.0, float(rng.uniform(4.0, 14.0)), length)).astype(
            np.float32
        )
        x[t0 : t0 + length] += burst * decay * float(rng.uniform(0.25, 0.95))
    peak = np.max(np.abs(x)) + 1e-8
    return (x / peak * float(rng.uniform(0.3, 0.9))).astype(np.float32)


def synth_bass(n: int, sr: int, rng: np.random.Generator) -> np.ndarray:
    t = np.arange(n, dtype=np.float32) / float(sr)
    f0 = float(rng.uniform(41.0, 110.0))
    shape = rng.choice(["sine", "saw"])
    phase = 2.0 * np.pi * f0 * t
    if shape == "sine":
        osc = np.sin(phase)
    else:
        osc = 2.0 * (t * f0 - np.floor(0.5 + t * f0))
    n_notes = int(rng.integers(1, 5))
    env = np.zeros(n, dtype=np.float32)
    for _ in range(n_notes):
        a = int(rng.integers(0, n))
        b = min(n, a + int(rng.uniform(0.12, 0.6) * sr))
        env[a:b] = np.maximum(env[a:b], np.hanning(b - a).astype(np.float32))
    if env.max() < 1e-6:
        env[:] = 0.4
    x = (osc * env * float(rng.uniform(0.25, 0.8))).astype(np.float32)
    return x


def synth_vocals(n: int, sr: int, rng: np.random.Generator) -> np.ndarray:
    t = np.arange(n, dtype=np.float32) / float(sr)
    f0 = float(rng.uniform(140.0, 420.0))
    vibrato = np.sin(2.0 * np.pi * float(rng.uniform(4.0, 6.5)) * t) * float(
        rng.uniform(1.5, 4.5)
    )
    x = np.zeros(n, dtype=np.float32)
    for k, amp in enumerate((1.0, 0.55, 0.28, 0.14, 0.08), start=1):
        x += amp * np.sin(2.0 * np.pi * (k * f0 + vibrato) * t).astype(np.float32)
    on = int(rng.uniform(0.0, 0.25) * n)
    off = int(rng.uniform(0.55, 1.0) * n)
    env = np.zeros(n, dtype=np.float32)
    env[on:off] = np.hanning(off - on).astype(np.float32)
    x *= env * float(rng.uniform(0.2, 0.7))
    return x.astype(np.float32)


def synth_other(n: int, sr: int, rng: np.random.Generator) -> np.ndarray:
    t = np.arange(n, dtype=np.float32) / float(sr)
    f = float(rng.uniform(220.0, 1500.0))
    pad = np.sin(2.0 * np.pi * f * t).astype(np.float32) * float(rng.uniform(0.05, 0.25))
    noise = rng.normal(0.0, 0.04, size=n).astype(np.float32)
    return pad + noise


SYNTH_BUILDERS = {
    "vocals": synth_vocals,
    "drums": synth_drums,
    "bass": synth_bass,
    "other": synth_other,
}


def mix_stems(
    stems: dict[str, np.ndarray],
    rng: np.random.Generator,
    train: TrainConfig,
    augment: bool,
) -> tuple[np.ndarray, dict[str, np.ndarray], np.ndarray]:
    mixed_stems: dict[str, np.ndarray] = {}
    for name, audio in stems.items():
        y = audio.astype(np.float32, copy=True)
        if augment:
            mute = bool(rng.random() < train.mute_prob)
            y = maybe_mute(y, mute)
            if not mute:
                gain = float(rng.uniform(train.gain_db_min, train.gain_db_max))
                y = apply_gain(y, gain)
                if name != "other" and rng.random() < train.eq_prob:
                    y = random_eq(y, rng)
        mixed_stems[name] = y
    mixture = np.zeros_like(next(iter(mixed_stems.values())))
    for y in mixed_stems.values():
        mixture = mixture + y
    if augment and rng.random() < train.noise_prob:
        snr = float(rng.uniform(train.noise_snr_db_min, train.noise_snr_db_max))
        mixture = add_noise(mixture, rng, snr)
    peak = float(np.max(np.abs(mixture)) + 1e-8)
    if peak > 1.0:
        scale = 0.99 / peak
        mixture = mixture * scale
        mixed_stems = {k: v * scale for k, v in mixed_stems.items()}
    target = activities_from_stems(mixed_stems)
    return mixture.astype(np.float32), mixed_stems, target


@dataclass(frozen=True)
class SongRef:
    song_id: str
    split: str
    source: str  # "synthetic" | "musdb18"


def hash_split(song_id: str, seed: int, val_frac: float, n_train_pool: int, index: int) -> str:
    """Deterministic val carve from a train pool. Test is assigned externally."""
    digest = hashlib.sha256(f"{seed}:{song_id}".encode()).hexdigest()
    bucket = int(digest[:8], 16) / 0xFFFFFFFF
    # Only used when we own the pool (synthetic). MUSDB test is the official folder.
    if bucket < val_frac:
        return "val"
    return "train"


def synthetic_songs(n: int = 48, seed: int = 0, val_frac: float = 0.2, n_test: int = 8) -> list[SongRef]:
    songs: list[SongRef] = []
    for i in range(n):
        song_id = f"synth_{i:03d}"
        if i >= n - n_test:
            split = "test"
        else:
            split = hash_split(song_id, seed, val_frac, n - n_test, i)
        songs.append(SongRef(song_id=song_id, split=split, source="synthetic"))
    return songs


def write_manifest(songs: Sequence[SongRef], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": 1,
        "note": "Split is by song_id. Never re-split by window.",
        "songs": [s.__dict__ for s in songs],
        "counts": {
            "train": sum(1 for s in songs if s.split == "train"),
            "val": sum(1 for s in songs if s.split == "val"),
            "test": sum(1 for s in songs if s.split == "test"),
        },
    }
    path.write_text(json.dumps(payload, indent=2) + "\n")


def read_manifest(path: Path) -> list[SongRef]:
    raw = json.loads(Path(path).read_text())
    return [SongRef(**row) for row in raw["songs"]]


class StemWindowDataset(Dataset):
    """On-the-fly 1 s windows from synthetic songs, or MUSDB if configured."""

    def __init__(
        self,
        songs: Sequence[SongRef],
        split: str,
        lab: LabConfig,
        n_windows: int,
        augment: bool,
        base_seed: int = 0,
        musdb_root: Path | None = None,
    ):
        self.songs = [s for s in songs if s.split == split]
        if not self.songs:
            raise ValueError(f"no songs in split={split}")
        self.lab = lab
        self.n_windows = n_windows
        self.augment = augment
        self.base_seed = base_seed
        self.musdb_root = musdb_root
        self.frontend = LogMelFrontend(lab.frontend)
        self.frontend.eval()

    def __len__(self) -> int:
        return self.n_windows

    def _song_for_index(self, idx: int) -> SongRef:
        return self.songs[idx % len(self.songs)]

    def _stems_for(self, song: SongRef, rng: np.random.Generator) -> dict[str, np.ndarray]:
        n = self.lab.frontend.n_samples
        sr = self.lab.frontend.sample_rate
        if song.source == "synthetic":
            return {name: builder(n, sr, rng) for name, builder in SYNTH_BUILDERS.items()}
        return load_musdb_window(song.song_id, n, sr, rng, self.musdb_root)

    def __getitem__(self, idx: int) -> dict[str, torch.Tensor | str]:
        song = self._song_for_index(idx)
        rng = _rng(self.base_seed + 10007 * idx + 17 * (0 if song.split == "train" else 1))
        stems = self._stems_for(song, rng)
        mixture, mixed_stems, target = mix_stems(
            stems, rng, self.lab.train, augment=self.augment
        )
        pcm = torch.from_numpy(mixture)
        with torch.no_grad():
            logmel = self.frontend(pcm.unsqueeze(0)).squeeze(0)
        return {
            "logmel": logmel,
            "target": torch.from_numpy(target),
            "pcm": pcm,
            "song_id": song.song_id,
            "split": song.split,
        }


def collate(batch: list[dict]) -> dict[str, torch.Tensor | list[str]]:
    return {
        "logmel": torch.stack([b["logmel"] for b in batch], dim=0),
        "target": torch.stack([b["target"] for b in batch], dim=0),
        "pcm": torch.stack([b["pcm"] for b in batch], dim=0),
        "song_id": [b["song_id"] for b in batch],
        "split": [b["split"] for b in batch],
    }


def load_musdb_window(
    song_id: str,
    n_samples: int,
    sr: int,
    rng: np.random.Generator,
    musdb_root: Path | None,
) -> dict[str, np.ndarray]:
    if musdb_root is None or not Path(musdb_root).exists():
        raise FileNotFoundError(
            "MUSDB requested but MUSDB_ROOT is missing. "
            "See datasets/README.md — research licence, access request required."
        )
    try:
        import musdb  # type: ignore
        import stempeg  # noqa: F401
    except ImportError as exc:
        raise ImportError("pip install -e '.[musdb]' to enable MUSDB loading") from exc

    # song_id format: "musdb18/{split}/{track_name}"
    parts = song_id.split("/", 2)
    if len(parts) != 3:
        raise ValueError(f"bad musdb song_id: {song_id}")
    _, split_folder, track_name = parts
    is_train = split_folder == "train"
    db = musdb.DB(root=str(musdb_root), subsets="train" if is_train else "test", is_wav=_is_hq(musdb_root))
    track = next((t for t in db.tracks if t.name == track_name), None)
    if track is None:
        raise FileNotFoundError(f"MUSDB track not found: {track_name}")
    # 44.1 kHz stereo stems → 16 kHz mono window
    audio = {name: _to_mono(track.targets[name].audio) for name in ("vocals", "drums", "bass", "other")}
    total = audio["vocals"].shape[0]
    src_sr = int(track.rate)
    n_src = int(round(n_samples * src_sr / sr))
    max_start = max(1, total - n_src)
    start = int(rng.integers(0, max_start))
    window = {k: v[start : start + n_src] for k, v in audio.items()}
    return {k: _resample_np(v, src_sr, sr, n_samples) for k, v in window.items()}


def _is_hq(root: Path) -> bool:
    # HQ is WAV stems; default MUSDB is STEM mp4.
    return any(Path(root).rglob("*.wav"))


def _to_mono(x: np.ndarray) -> np.ndarray:
    if x.ndim == 1:
        return x.astype(np.float32)
    return x.mean(axis=1).astype(np.float32)


def _resample_np(x: np.ndarray, src_sr: int, dst_sr: int, n_out: int) -> np.ndarray:
    if src_sr == dst_sr and len(x) == n_out:
        return x.astype(np.float32)
    import torchaudio

    t = torch.from_numpy(x.astype(np.float32)).unsqueeze(0)
    y = torchaudio.functional.resample(t, src_sr, dst_sr).squeeze(0).numpy()
    if len(y) < n_out:
        y = np.pad(y, (0, n_out - len(y)))
    return y[:n_out].astype(np.float32)


def assert_no_song_leak(songs: Sequence[SongRef]) -> None:
    by_split: dict[str, set[str]] = {"train": set(), "val": set(), "test": set()}
    for s in songs:
        by_split[s.split].add(s.song_id)
    leaked = (by_split["train"] & by_split["val"]) | (by_split["train"] & by_split["test"]) | (
        by_split["val"] & by_split["test"]
    )
    if leaked:
        raise RuntimeError(f"song-level leak: {sorted(leaked)[:8]}")


def scan_musdb(root: Path, seed: int = 0, val_frac: float = 0.15) -> list[SongRef]:
    """Official train/test folders, then carve val from train by hashed song id."""
    train_dir = root / "train"
    test_dir = root / "test"
    if not train_dir.is_dir() or not test_dir.is_dir():
        raise FileNotFoundError(f"expected {train_dir} and {test_dir}")
    def names(folder: Path) -> list[str]:
        found = sorted(p.name for p in folder.iterdir() if p.is_dir() or p.suffix in {".stem.mp4", ".mp4"})
        if not found:
            found = sorted({p.parent.name for p in folder.rglob("*.wav") if p.parent != folder})
        return found

    songs: list[SongRef] = []
    for name in names(train_dir):
        song_id = f"musdb18/train/{name}"
        split = hash_split(song_id, seed, val_frac, 100, 0)
        songs.append(SongRef(song_id=song_id, split=split, source="musdb18"))
    for name in names(test_dir):
        songs.append(SongRef(song_id=f"musdb18/test/{name}", split="test", source="musdb18"))
    assert_no_song_leak(songs)
    return songs
