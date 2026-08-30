"""Canonical DEAM files. Not mirdata."""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

ROOT_DEFAULT = Path(__file__).resolve().parents[3] / "datasets" / "deam"
AROUSAL = ROOT_DEFAULT / "annotations" / "annotations averaged per song" / "dynamic (per second annotations)" / "arousal.csv"
VALENCE = ROOT_DEFAULT / "annotations" / "annotations averaged per song" / "dynamic (per second annotations)" / "valence.csv"
AUDIO_DIR = ROOT_DEFAULT / "MEMD_audio"


def _parse_dynamic(path: Path) -> dict[int, tuple[np.ndarray, np.ndarray]]:
    """song_id -> (times_s, values). Columns are sample_<ms>ms starting ~15000."""
    out: dict[int, tuple[np.ndarray, np.ndarray]] = {}
    with path.open(newline="") as f:
        reader = csv.reader(f)
        header = next(reader)
        ms = []
        for col in header[1:]:
            # sample_15000ms
            num = "".join(ch for ch in col if ch.isdigit())
            ms.append(int(num) / 1000.0 if num else None)
        for row in reader:
            if not row or not row[0]:
                continue
            sid = int(float(row[0]))
            times, vals = [], []
            for t, cell in zip(ms, row[1:]):
                if t is None or cell == "" or cell.lower() == "nan":
                    continue
                times.append(t)
                vals.append(float(cell))
            if times:
                out[sid] = (np.array(times, dtype=np.float32), np.array(vals, dtype=np.float32))
    return out


def load_arousal(path: Path | None = None) -> dict[int, tuple[np.ndarray, np.ndarray]]:
    return _parse_dynamic(path or AROUSAL)


def load_valence(path: Path | None = None) -> dict[int, tuple[np.ndarray, np.ndarray]]:
    return _parse_dynamic(path or VALENCE)


def audio_path(song_id: int, audio_dir: Path | None = None) -> Path:
    p = (audio_dir or AUDIO_DIR) / f"{song_id}.mp3"
    if not p.is_file():
        raise FileNotFoundError(p)
    return p


def cohort(song_id: int) -> str:
    if song_id >= 2000:
        return "2015_full"  # higher dynamic-arousal reliability per DEAM manual
    if song_id >= 1000:
        return "2014_clip"
    return "2013_clip"
