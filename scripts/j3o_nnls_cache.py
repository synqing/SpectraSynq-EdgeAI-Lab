#!/usr/bin/env python3
"""J3O - cache the pinned NNLS Chroma plugin outputs on the host analysis grid.

Two arms from ONE frontend, ONE binary, differing in useNNLS only.
Pre-registration: docs/mir/receipts/nnls_probe/J3O_PREREGISTRATION.json
"""
from __future__ import annotations

import argparse
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
sys.path.insert(0, "/tmp/vampsrc/vamp-1.1.0")

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import j3g_common as C  # noqa: E402

sys.path.insert(0, str(C.ROOT / "src"))
from edgeai.mir.note_register import HOP, SR  # noqa: E402

KEY = "nnls-chroma:nnls-chroma"
BLOCK = 2048
SHIFT = BLOCK // HOP - 1          # pre-registered deterministic alignment: +3
FAMS = ["bass", "piano_keys", "synth_lead_pad", "reed_pipe", "chromatic_percussion"]
BASE = dict(rollon=0.0, tuningmode=0.0, whitening=1.0, s=0.7, chromanormalize=0.0)
ARMS = {"NNLS_FRONTEND_ONLY": 0.0, "NNLS_NOTES": 1.0}


def params(use_nnls: float) -> dict:
    return dict(BASE, useNNLS=float(use_nnls))


def run(y: np.ndarray, use_nnls: float, output: str) -> np.ndarray:
    import vamp  # imported lazily so the pure helpers below stay testable without it

    r = vamp.collect(y, SR, KEY, output=output, parameters=params(use_nnls),
                     block_size=BLOCK, step_size=HOP)
    return np.asarray(r["matrix"][1], dtype=np.float64)


def fold12(semitone: np.ndarray) -> np.ndarray:
    """Uniform mod-12 fold of the 84-bin semitone spectrum; bin k <-> MIDI k+21."""
    out = np.zeros((semitone.shape[0], 12), dtype=np.float64)
    for k in range(semitone.shape[1]):
        out[:, (k + 21) % 12] += semitone[:, k]
    return out


def align(x: np.ndarray, n: int) -> np.ndarray:
    """host_frame = plugin_frame + SHIFT. Leading frames have no plugin frame."""
    out = np.full((n, x.shape[1]), np.nan, dtype=np.float64)
    m = min(n - SHIFT, x.shape[0])
    if m > 0:
        out[SHIFT:SHIFT + m] = x[:m]
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", type=Path, required=True)
    ap.add_argument("--out", type=Path, default=Path("/tmp/j3o_cache"))
    ap.add_argument("--mixes", action="store_true", help="cache the 20 mixes too")
    args = ap.parse_args()
    import soundfile as sf
    import yaml

    args.out.mkdir(parents=True, exist_ok=True)

    assert set(params(0.0)) - {"useNNLS"} == set(params(1.0)) - {"useNNLS"}
    assert all(params(0.0)[k] == params(1.0)[k] for k in BASE), "arms differ beyond useNNLS"

    done = 0
    for d in sorted(p for p in args.corpus.iterdir() if p.is_dir() and (p / "all_src.mid").is_file()):
        md = yaml.safe_load((d / "metadata.yaml").read_text())
        jobs = []
        for f in sorted(p for p in (d / "stems").glob("*.wav") if not p.name.startswith("._")):
            fam = C.family_of(int(md["stems"][f.stem]["program_num"]))
            if fam in FAMS:
                jobs.append((f"{d.name}__{f.stem}", f))
        if args.mixes and (d / "mix.wav").is_file():
            jobs.append((f"mix__{d.name}", d / "mix.wav"))
        for name, path in jobs:
            of = args.out / f"{name}.npz"
            if of.is_file():
                continue
            y, sr = sf.read(str(path), dtype="float64")
            if y.ndim > 1:
                y = y.mean(axis=1)
            assert sr == SR, f"{path} sample rate {sr}"
            n = 1 + len(y) // HOP
            payload = {}
            for arm, u in ARMS.items():
                payload[arm] = align(fold12(run(y, u, "semitonespectrum")), n).astype(np.float32)
            # secondary descriptive arm: the plugin's own treble chroma, NNLS on
            payload["NNLS_PUBLISHED_CHROMA"] = align(run(y, 1.0, "chroma"), n).astype(np.float32)
            np.savez_compressed(of, n=n, **payload)
            done += 1
            print(f"{name}  n={n}", flush=True)
    print(f"cached {done}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
