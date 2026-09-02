#!/usr/bin/env python3
"""J3N - cache the shared pitch-energy surface so FB_LOG_CHROMA and CRP are
byte-identical upstream of the DCT. 128 ms window, the J3M primary surface."""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np, soundfile as sf, yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import j3g_common as C
sys.path.insert(0, str(C.ROOT / "src"))
from edgeai.mir import crp as K
from edgeai.mir.note_register import SR

OUT = Path("/tmp/j3n_pitch"); CORPUS = Path("/tmp/bs/babyslakh_16k")
FAMS = {"bass", "piano_keys", "synth_lead_pad", "reed_pipe", "chromatic_percussion"}


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    for d in sorted(p for p in CORPUS.iterdir() if p.is_dir() and (p / "all_src.mid").is_file()):
        md = yaml.safe_load((d / "metadata.yaml").read_text())
        for s in sorted(p for p in (d / "stems").glob("*.wav") if not p.name.startswith("._")):
            sc = Path("/tmp/j3g_stem_cache") / f"{d.name}__{s.stem}.npz"
            if not sc.is_file():
                continue
            if C.family_of(int(md["stems"][s.stem].get("program_num", 0))) not in FAMS:
                continue
            f = OUT / f"{d.name}__{s.stem}.npz"
            if f.is_file():
                continue
            n = int(np.load(sc)["R_PC_POWER"].shape[0])
            y, sr = sf.read(str(s), dtype="float64", always_2d=True)
            assert sr == SR
            np.savez_compressed(f, pitch=K.pitch_energy(y.mean(axis=1))[:n].astype(np.float32))
            print(d.name, s.stem, flush=True)
    print("DONE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
