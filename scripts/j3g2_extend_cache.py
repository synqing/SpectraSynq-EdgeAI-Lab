#!/usr/bin/env python3
"""J3G.2 - add the C5 peak-to-root projection to the existing J3G caches.

Sidecar files only. The J3G caches are never rewritten.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import soundfile as sf
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import j3g_common as C  # noqa: E402

sys.path.insert(0, str(C.ROOT / "src"))
from edgeai.mir import tonal_projection as tp  # noqa: E402
from edgeai.mir.note_register import SR  # noqa: E402

SIDE = Path("/tmp/j3g2_cache")
CORPUS = Path("/tmp/bs/babyslakh_16k")


def c5_for(path: Path, n: int | None = None) -> np.ndarray:
    y, sr = sf.read(str(path), dtype="float64", always_2d=True)
    assert sr == SR
    v = tp.c5_peak_root(tp.stft_power(y.mean(axis=1)))
    return v if n is None else v[:n]


def main() -> int:
    SIDE.mkdir(parents=True, exist_ok=True)
    for d in sorted(p for p in CORPUS.iterdir() if p.is_dir() and (p / "all_src.mid").is_file()):
        f = SIDE / f"track__{d.name}.npz"
        if f.is_file():
            continue
        n = int(np.load(C.CACHE / f"{d.name}.npz")["n"])
        np.savez_compressed(f, C5=c5_for(d / "mix.wav", n))
        print("track", d.name, flush=True)
    for d in sorted(p for p in CORPUS.iterdir() if p.is_dir() and (p / "all_src.mid").is_file()):
        md = yaml.safe_load((d / "metadata.yaml").read_text())
        for s in sorted(p for p in (d / "stems").glob("*.wav") if not p.name.startswith("._")):
            stem_cache = Path("/tmp/j3g_stem_cache") / f"{d.name}__{s.stem}.npz"
            if not stem_cache.is_file():
                continue
            f = SIDE / f"stem__{d.name}__{s.stem}.npz"
            if f.is_file():
                continue
            meta = md["stems"].get(s.stem, {})
            if meta.get("is_drum") or int(meta.get("program_num", 0)) >= 112:
                continue
            n = int(np.load(stem_cache)["R_PC_POWER"].shape[0])
            np.savez_compressed(f, C5=c5_for(s, n))
            print("stem", d.name, s.stem, flush=True)
    print("DONE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
