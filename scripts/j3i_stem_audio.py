#!/usr/bin/env python3
"""J3I - per-stem audio support and attack/decay envelope cache.

Sidecar only. No existing cache is rewritten. No chroma, no candidate
representation, no pitch estimator, no model.

Pre-registration: docs/mir/receipts/timbre_diagnostic/J3I_PREREGISTRATION.json
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pretty_midi
import soundfile as sf
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import j3g_common as C  # noqa: E402

sys.path.insert(0, str(C.ROOT / "src"))
from edgeai.mir.note_register import (  # noqa: E402
    HOP, N_FFT, SILENCE_FLOOR_DBFS, SR, dsp_register_features, frame_grid, silence_mask,
)

SIDE = Path("/tmp/j3i_cache")
CORPUS = Path("/tmp/bs/babyslakh_16k")
GUARD_S = 0.10
GUARD_SENS_S = 0.30
MIN_DUR_S = 0.2
TAIL_S = 0.2
REL = (0.10, 0.50)


def rms_2048(y: np.ndarray) -> np.ndarray:
    """Vectorised copy of dsp_register_features' per-frame RMS. Asserted equal."""
    n = max(1, int(y.size // HOP)) if y.size >= HOP else 1
    _, ends = frame_grid(y.size)
    out = np.zeros(n, dtype=np.float64)
    for i in range(n):
        end = int(min(y.size, ends[i]))
        start = end - N_FFT
        f = np.zeros(N_FFT, dtype=np.float64)
        if start < 0:
            take = y[:end]
            if take.size:
                f[-take.size:] = take
        else:
            f[:] = y[start:end]
        out[i] = float(np.sqrt(np.mean(f**2)) + 1e-12)
    return out


def env_512(y: np.ndarray, n: int) -> np.ndarray:
    """Declared timing envelope: RMS over a 512-sample rectangular window on the
    analysis hop grid, causal, hop-centre timestamps."""
    out = np.zeros(n, dtype=np.float64)
    for i in range(n):
        end = min(y.size, (i + 1) * HOP)
        start = max(0, end - HOP)
        seg = y[start:end]
        out[i] = float(np.sqrt(np.mean(seg**2))) if seg.size else 0.0
    return out


def episodes(mid: Path, guard: float = GUARD_S) -> list[tuple[float, float, int]]:
    """Isolated monophonic MIDI episodes: no other note in the stem overlaps
    [on - G, off + G]. Declared before measurement."""
    pm = pretty_midi.PrettyMIDI(str(mid))
    notes = sorted(((float(n.start), float(n.end), int(n.pitch))
                    for i in pm.instruments for n in i.notes), key=lambda t: t[0])
    if not notes:
        return []
    starts = np.array([n[0] for n in notes])
    ends = np.array([n[1] for n in notes])
    out = []
    for k, (s, e, p) in enumerate(notes):
        if e - s < MIN_DUR_S:
            continue
        lo, hi = s - guard, e + guard
        overlap = (starts < hi) & (ends > lo)
        overlap[k] = False
        if not overlap.any():
            out.append((s, e, p))
    return out


def main() -> int:
    SIDE.mkdir(parents=True, exist_ok=True)
    checked = False
    for d in sorted(p for p in CORPUS.iterdir() if p.is_dir() and (p / "all_src.mid").is_file()):
        md = yaml.safe_load((d / "metadata.yaml").read_text())
        for f in sorted(p for p in (d / "stems").glob("*.wav") if not p.name.startswith("._")):
            if not (Path("/tmp/j3g_stem_cache") / f"{d.name}__{f.stem}.npz").is_file():
                continue
            out = SIDE / f"{d.name}__{f.stem}.npz"
            if out.is_file():
                continue
            meta = md["stems"].get(f.stem, {})
            if meta.get("is_drum") or int(meta.get("program_num", 0)) >= 112:
                continue
            y, sr = sf.read(str(f), dtype="float64", always_2d=True)
            if sr != SR:
                continue
            y = y.mean(axis=1)
            r = rms_2048(y)
            if not checked:
                _, ref, _ = dsp_register_features(y[: SR * 20])
                err = float(np.max(np.abs(ref - r[: len(ref)])))
                assert err <= 1e-12, f"instrumented RMS diverges by {err:.3g}"
                print(f"CONTROL instrumented_rms_max_abs_diff={err:.3g}", flush=True)
                checked = True
            n = r.size
            e512 = env_512(y, n)
            ok = silence_mask(r, floor_dbfs=SILENCE_FLOOR_DBFS)
            mf = d / "MIDI" / f"{f.stem}.mid"
            eps = episodes(mf) if mf.is_file() else []
            sens = set(episodes(mf, GUARD_SENS_S)) if mf.is_file() else set()
            rows = []
            for s, e, p in eps:
                i0 = int(np.floor(s * SR / HOP))
                i1 = int(np.ceil(e * SR / HOP))
                it = min(int(np.ceil((e + TAIL_S) * SR / HOP)), n)
                if i0 < 0 or i1 >= n or it <= i0 + 1:
                    continue
                peak = float(e512[i0:it].max())
                if peak <= 0 or not ok[i0:i1].any():
                    continue
                seg = e512[i0:it]
                a = {}
                for t in REL:
                    idx = np.nonzero(seg >= t * peak)[0]
                    a[t] = float(idx[0]) if idx.size else float("nan")
                rel = {}
                after = e512[i1:it]
                for t in REL:
                    below = np.nonzero(after < t * peak)[0]
                    if below.size:
                        rel[t] = float(below[0])
                    else:  # already decayed before the gate closed - search backwards
                        pre = np.nonzero(e512[i0:i1] >= t * peak)[0]
                        rel[t] = float(pre[-1] - (i1 - i0)) if pre.size else float("nan")
                cov = float(((e512[i0:i1] >= REL[0] * peak) & ok[i0:i1]).mean())
                rows.append([a[0.10], a[0.50], rel[0.10], rel[0.50], cov, float(p),
                             float(i1 - i0), peak, 1.0 if (s, e, p) in sens else 0.0])
            np.savez_compressed(out, audio_ok=ok, episodes=np.array(rows, dtype=np.float64)
                                if rows else np.zeros((0, 9)),
                                program=int(meta.get("program_num", 0)))
            print(d.name, f.stem, len(rows), flush=True)
    print("DONE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
