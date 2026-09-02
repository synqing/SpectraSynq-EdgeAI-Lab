#!/usr/bin/env python3
"""J3M - CRP feature cache for the 20 mixes and the five named solo families."""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np, soundfile as sf, yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import j3g_common as C
sys.path.insert(0, str(C.ROOT / "src"))
from edgeai.mir import crp as K
from edgeai.mir.note_register import SR

OUT = Path("/tmp/j3m_cache"); CORPUS = Path("/tmp/bs/babyslakh_16k")
FAMS = {"synth_lead_pad", "reed_pipe", "piano_keys", "bass", "chromatic_percussion"}


def run(path: Path, key: str, n: int | None = None):
    f = OUT / f"{key}.npz"
    if f.is_file():
        return
    y, sr = sf.read(str(path), dtype="float64", always_2d=True)
    assert sr == SR
    c = K.crp(K.pitch_energy(y.mean(axis=1)))
    np.savez_compressed(f, crp=(c if n is None else c[:n]))
    print(key, flush=True)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    for d in sorted(p for p in CORPUS.iterdir() if p.is_dir() and (p / "all_src.mid").is_file()):
        run(d / "mix.wav", f"mix__{d.name}", int(np.load(C.CACHE / f"{d.name}.npz")["n"]))
        md = yaml.safe_load((d / "metadata.yaml").read_text())
        for s in sorted(p for p in (d / "stems").glob("*.wav") if not p.name.startswith("._")):
            sc = Path("/tmp/j3g_stem_cache") / f"{d.name}__{s.stem}.npz"
            if not sc.is_file():
                continue
            meta = md["stems"].get(s.stem, {})
            if C.family_of(int(meta.get("program_num", 0))) not in FAMS:
                continue
            run(s, f"stem__{d.name}__{s.stem}", int(np.load(sc)["R_PC_POWER"].shape[0]))
    print("DONE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
