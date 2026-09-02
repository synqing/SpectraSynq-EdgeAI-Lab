#!/usr/bin/env python3
"""J3J - extract per-episode monotone attack curves from isolated rendered audio.

Representation-independent: MIDI timing + waveform envelope only.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import soundfile as sf
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import j3g_common as C  # noqa: E402
import j3i_stem_audio as J  # noqa: E402

sys.path.insert(0, str(C.ROOT / "src"))
from edgeai.mir.acoustic_activation import K_MAX_HOPS, episode_curve  # noqa: E402
from edgeai.mir.note_register import HOP, SR  # noqa: E402

OUT = Path("/tmp/j3j_curves.npz")
CORPUS = Path("/tmp/bs/babyslakh_16k")


def main() -> int:
    tracks, fams, curves = [], [], []
    for d in sorted(p for p in CORPUS.iterdir() if p.is_dir() and (p / "all_src.mid").is_file()):
        md = yaml.safe_load((d / "metadata.yaml").read_text())
        for f in sorted(p for p in (d / "stems").glob("*.wav") if not p.name.startswith("._")):
            if not (Path("/tmp/j3i_cache") / f"{d.name}__{f.stem}.npz").is_file():
                continue
            meta = md["stems"].get(f.stem, {})
            prog = int(meta.get("program_num", 0))
            mf = d / "MIDI" / f"{f.stem}.mid"
            if not mf.is_file():
                continue
            y, sr = sf.read(str(f), dtype="float64", always_2d=True)
            if sr != SR:
                continue
            y = y.mean(axis=1)
            n = max(1, int(y.size // HOP))
            env = J.env_512(y, n)
            ok = np.load(Path("/tmp/j3i_cache") / f"{d.name}__{f.stem}.npz")["audio_ok"][:n]
            got = 0
            for s, e, _p in J.episodes(mf):
                i0 = int(np.floor(s * SR / HOP))
                i1 = int(np.ceil(e * SR / HOP))
                it = min(int(np.ceil((e + J.TAIL_S) * SR / HOP)), n)
                if i0 < 0 or i1 >= n or it <= i0 + 1:
                    continue
                peak = float(env[i0:it].max())
                if peak <= 0 or not ok[i0:i1].any():
                    continue
                c = episode_curve(env, i0, i1, peak)
                if c is None:
                    continue
                tracks.append(d.name); fams.append(C.family_of(prog)); curves.append(c); got += 1
            print(d.name, f.stem, got, flush=True)
    np.savez_compressed(OUT, tracks=np.array(tracks), families=np.array(fams),
                        curves=np.vstack(curves) if curves else np.zeros((0, K_MAX_HOPS + 1)))
    print("DONE", len(curves))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
