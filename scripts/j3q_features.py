#!/usr/bin/env python3
"""J3Q - build the frozen 53-dimensional CAUSAL feature matrix.

Every feature is derivable from the existing 16 kHz / n_fft 2048 / hop 512 STFT
path and looks only backwards. No FB_LOG, no CRP, no NNLS, no family ID, no
track ID, no future frame.

Pre-registration: docs/mir/receipts/learned_restraint/J3Q_PREREGISTRATION.json
"""
from __future__ import annotations

import argparse
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import j3g_common as C  # noqa: E402

sys.path.insert(0, str(C.ROOT / "src"))
from edgeai.mir.harmonic_movement import (  # noqa: E402
    MOVEMENT_LAG_HOPS as LAG, lagged_abs_delta, rectified_flux, tv_movement,
)
from edgeai.mir.host_chroma import host_spectrogram80  # noqa: E402
from edgeai.mir.note_register import HOP, N_FFT, SR, dsp_register_features  # noqa: E402
from edgeai.mir.restraint_head import FEATURE_BLOCKS, N_FEATURES  # noqa: E402

STEMS = Path("/tmp/j3g_stem_cache")
FAMS = ["bass", "piano_keys", "synth_lead_pad", "reed_pipe", "chromatic_percussion"]

ONSET_SHIFT = 0
ONSET_SHIFT_NOTE = (
    "the programme's existing B_onset descriptor picks a per-track backward shift in 0..6 by "
    "maximising Spearman against flux over the WHOLE track. That is a whole-track calibration and "
    "J3Q is a causal-feasibility probe, so J3Q uses shift 0 and NO fitted alignment. The shift the "
    "existing method would have chosen is measured and reported as a control."
)


def audio_descriptors(y: np.ndarray, n: int) -> dict:
    """Spectral flux, onset descriptor and delta-log-RMS. All backward-looking."""
    import librosa

    _, spec = host_spectrogram80(y.astype(np.float32))
    _, rms, _ = dsp_register_features(y)
    onset_raw = librosa.onset.onset_strength(y=y.astype(np.float32), sr=SR,
                                             hop_length=HOP, n_fft=N_FFT, center=False)
    onset = np.zeros(n)
    m = min(n, onset_raw.size)
    onset[:m] = onset_raw[:m]                      # shift 0, no fitted alignment
    return {"flux": rectified_flux(np.asarray(spec[:n], dtype=np.float64)),
            "onset": lagged_abs_delta(onset),
            "dlogrms": lagged_abs_delta(np.log(np.asarray(rms[:n], dtype=np.float64) + 1e-12)),
            "_onset_raw": onset_raw, "_flux_for_shift": spec[:n]}


def measured_existing_shift(flux_spec, onset_raw, n) -> int:
    """CONTROL ONLY - what the existing whole-track method would have chosen."""
    from scipy.stats import spearmanr

    f1 = np.zeros(flux_spec.shape[0])
    f1[1:] = np.clip(np.diff(np.asarray(flux_spec, dtype=np.float64), axis=0), 0.0, None).sum(axis=1)
    best_k, best_s = 0, -np.inf
    for k in range(7):
        cand = np.zeros(n)
        for i in range(n):
            j = i - k
            if 0 <= j < onset_raw.size:
                cand[i] = onset_raw[j]
        s = spearmanr(f1[:n], cand[:n]).statistic
        if np.isfinite(s) and s > best_s:
            best_s, best_k = float(s), k
    return best_k


def features_from(states: dict, desc: dict, n: int) -> np.ndarray:
    """The frozen 53-D vector. Column order is FEATURE_BLOCKS, exactly."""
    c3, p0 = states["C3_ROOT_SALIENCE"][:n], states["P0_CURRENT"][:n]
    c3_lag = np.full_like(c3, np.nan)
    p0_lag = np.full_like(p0, np.nan)
    c3_lag[LAG:] = c3[:-LAG]
    p0_lag[LAG:] = p0[:-LAG]
    cols = [c3, c3_lag, p0, p0_lag,
            tv_movement(c3).reshape(-1, 1), tv_movement(p0).reshape(-1, 1),
            desc["flux"].reshape(-1, 1), desc["onset"].reshape(-1, 1),
            desc["dlogrms"].reshape(-1, 1)]
    x = np.hstack(cols)
    assert x.shape[1] == N_FEATURES, f"{x.shape[1]} != {N_FEATURES}"
    return x


def main() -> int:
    import soundfile as sf
    import yaml

    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", type=Path, required=True)
    ap.add_argument("--out", type=Path, default=Path("/tmp/j3q_feat"))
    ap.add_argument("--mixes", action="store_true")
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    shifts, done = [], 0
    for d in sorted(p for p in args.corpus.iterdir() if p.is_dir() and (p / "all_src.mid").is_file()):
        md = yaml.safe_load((d / "metadata.yaml").read_text())
        jobs = []
        for f in sorted(p for p in (d / "stems").glob("*.wav") if not p.name.startswith("._")):
            if C.family_of(int(md["stems"][f.stem]["program_num"])) in FAMS:
                jobs.append((f"{d.name}__{f.stem}", f, STEMS / f"{d.name}__{f.stem}.npz"))
        if args.mixes and (d / "mix.wav").is_file():
            jobs.append((f"mix__{d.name}", d / "mix.wav", C.CACHE / f"{d.name}.npz"))
        for name, path, cache in jobs:
            of = args.out / f"{name}.npz"
            if of.is_file() or not cache.is_file():
                continue
            y, sr = sf.read(str(path), dtype="float64", always_2d=True)
            y = y.mean(axis=1)
            assert sr == SR
            z = np.load(cache, allow_pickle=False)
            raw = {k: z[f"R_{k}"] for k in C.RAW_KEYS}
            n = raw["PC_POWER"].shape[0]
            states = C.states_from_raw(raw, winner="P0_CURRENT")
            desc = audio_descriptors(y, n)
            shifts.append(measured_existing_shift(desc["_flux_for_shift"], desc["_onset_raw"], n))
            x = features_from(states, desc, n)
            np.savez_compressed(of, x=x.astype(np.float32), n=n)
            done += 1
            print(f"{name}  n={n}", flush=True)
    if shifts:
        u, c = np.unique(shifts, return_counts=True)
        print(f"CONTROL existing-method shift distribution: {dict(zip(u.tolist(), c.tolist()))}")
    print(f"cached {done}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
