#!/usr/bin/env python3
"""J3G shared build + metrics. One STFT per signal, every candidate downstream of it.

Pre-registration: docs/mir/receipts/stft_harmonic_recovery/J3G_PREREGISTRATION.json
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from edgeai.mir import tonal_projection as tp  # noqa: E402
from edgeai.mir.harmonic_movement import (  # noqa: E402
    MOVEMENT_LAG_HOPS, is_tonal_instrument, l1_rows, lagged_abs_delta,
    pitch_class_state, rectified_flux, tv_movement, within_track_rank,
)
from edgeai.mir.host_chroma import host_chroma12, host_spectrogram80  # noqa: E402
from edgeai.mir.note_register import (  # noqa: E402
    HOP, N_FFT, SR, Note, dsp_register_features, frame_grid, l1_normalise, silence_mask,
)

LAG = MOVEMENT_LAG_HOPS
ALPHAS = (1e-3, 1e-2, 1e-1, 1.0, 10.0, 100.0, 1000.0)
PREREG = ROOT / "docs" / "mir" / "receipts" / "stft_harmonic_recovery" / "J3G_PREREGISTRATION.json"
CACHE = Path("/tmp/j3g_cache")

CANDIDATES = ["P0_CURRENT", "P1_POWER_L1", "P2_SQRT_L1_NO_CLIP",
              "C1_SOFT_FILTERBANK", "C2_PEAK_HPCP", "C3_ROOT_SALIENCE", "C4_CRP"]
PROJECTIONS = ["C1_SOFT_FILTERBANK", "C2_PEAK_HPCP", "C3_ROOT_SALIENCE", "C4_CRP"]

FAMILIES = [("piano_keys", lambda p: p < 8 or 16 <= p < 24), ("chromatic_percussion", lambda p: 8 <= p < 16),
            ("guitar", lambda p: 24 <= p < 32), ("bass", lambda p: 32 <= p < 40),
            ("strings", lambda p: 40 <= p < 48), ("ensemble_voice", lambda p: 48 <= p < 56),
            ("brass", lambda p: 56 <= p < 64), ("reed_pipe", lambda p: 64 <= p < 80),
            ("synth_lead_pad", lambda p: 80 <= p < 96), ("synth_effects", lambda p: 96 <= p < 112)]


def family_of(program: int) -> str:
    for name, fn in FAMILIES:
        if fn(int(program)):
            return name
    return "other"


def split_tracks(corpus: Path) -> dict:
    """DECLARED BEFORE ANY SCORE: sorted names, even index -> DEV, odd -> FINAL."""
    dirs = sorted(p.name for p in corpus.iterdir() if p.is_dir() and (p / "all_src.mid").is_file())
    return {"all": dirs, "development": dirs[0::2], "final_holdout": dirs[1::2]}


# ---------------------------------------------------------------- regression
def _fit(X, Y, a):
    mu, sd = X.mean(0), X.std(0) + 1e-9
    Xs = (X - mu) / sd
    ym = Y.mean(0)
    return {"mu": mu, "sd": sd, "ym": ym,
            "W": np.linalg.solve(Xs.T @ Xs + a * np.eye(Xs.shape[1]), Xs.T @ (Y - ym))}


def _pred(m, X):
    return ((X - m["mu"]) / m["sd"]) @ m["W"] + m["ym"]


def _r2(y, yh):
    return float(1.0 - np.sum((y - yh) ** 2) / (np.sum((y - y.mean()) ** 2) + 1e-20))


def grouped_r2(x, y, groups, *, n_folds=5, seed=0):
    """Grouped 5-fold CV by track. Alpha chosen on TRAINING folds only."""
    X = np.atleast_2d(np.asarray(x, dtype=np.float64).T).T
    Y = np.asarray(y, dtype=np.float64).reshape(-1, 1)
    uniq = np.unique(groups)
    n_folds = max(2, min(n_folds, len(uniq)))
    oof = np.full_like(Y, np.nan)
    for f in np.array_split(np.random.default_rng(seed).permutation(uniq), n_folds):
        te = np.isin(groups, f)
        tr = ~te
        if tr.sum() < 10 or te.sum() < 1:
            continue
        trt = np.unique(groups[tr])
        cut = max(1, len(trt) // 4)
        iv = np.isin(groups, trt[:cut]) & tr
        it = tr & ~iv
        best, ba = -np.inf, ALPHAS[0]
        for a in ALPHAS:
            m = _fit(X[it], Y[it], a)
            s = _r2(Y[iv], _pred(m, X[iv]))
            if s > best:
                best, ba = s, a
        oof[te] = _pred(_fit(X[tr], Y[tr], ba), X[te])
    ok = ~np.isnan(oof[:, 0])
    return round(_r2(Y[ok], oof[ok]), 4)


# ---------------------------------------------------------------- per track
RAW_KEYS = ["PC_POWER", "C1_SOFT_FILTERBANK", "C2_PEAK_HPCP", "C3_ROOT_SALIENCE", "C4_CRP"]
RAW_DOMAIN = {"C1_SOFT_FILTERBANK": "power", "C2_PEAK_HPCP": "power",
              "C3_ROOT_SALIENCE": "amplitude", "C4_CRP": "log"}


def raw_projections(stft: dict) -> dict:
    """Candidate outputs BEFORE the carry-forward compression, so the J3G-1 winner
    can be applied afterwards without recomputing the STFT."""
    c4 = tp.c4_crp_chroma(stft)
    return {"PC_POWER": tp.pitch_class_power_from_stft(stft),
            "C1_SOFT_FILTERBANK": tp.c1_soft_chroma(stft),
            "C2_PEAK_HPCP": tp.c2_peak_hpcp(stft),
            "C3_ROOT_SALIENCE": tp.c3_root_salience(stft),
            "C4_CRP": c4["chroma"],
            "_c4_rectified_mass_fraction": c4["rectified_mass_fraction"]}


def states_from_raw(raw: dict, *, winner: str) -> dict:
    """Apply the declared postprocessing / carry-forward compression."""
    pcp = raw["PC_POWER"]
    out = {"P0_CURRENT": tp.l1(tp.post_P0(pcp)),
           "P1_POWER_L1": tp.l1(tp.post_P1(pcp)),
           "P2_SQRT_L1_NO_CLIP": tp.l1(tp.post_P2(pcp))}
    for k, dom in RAW_DOMAIN.items():
        out[k] = tp.l1(tp.apply_carry_forward(raw[k], native_domain=dom, winner=winner))
    return out


def attach_states(b: dict, *, winner: str) -> dict:
    b["states"] = states_from_raw(b["raw"], winner=winner)
    b["mov"] = {k: tv_movement(v) for k, v in b["states"].items()}
    b["mov"]["_HOST_CHROMA12"] = b["M__HOST_CHROMA12"]
    return b


def build_track(track_dir: Path, *, winner: str = "P0_CURRENT") -> dict | None:
    """One shared STFT; every candidate state derived from it. Validity is J3E's."""
    import librosa
    import pretty_midi
    import soundfile as sf
    from scipy.stats import spearmanr as _sp

    mix = track_dir / "mix.wav"
    mid = track_dir / "all_src.mid"
    if not mix.is_file() or not mid.is_file():
        return None
    y, sr = sf.read(str(mix), dtype="float64", always_2d=True)
    if sr != SR:
        return None
    y = y.mean(axis=1)

    pm = pretty_midi.PrettyMIDI(str(mid))
    notes = [Note(float(n.start), float(n.end), int(n.pitch), int(n.velocity))
             for inst in pm.instruments if is_tonal_instrument(inst.is_drum, inst.program)
             for n in inst.notes]
    times, _ = frame_grid(y.size)
    st_sym = pitch_class_state(notes, times.size)

    stft = tp.stft_power(y)                       # THE one STFT
    raw = raw_projections(stft)
    c4_rect = raw.pop("_c4_rectified_mass_fraction")

    _, chroma = host_chroma12(y.astype(np.float32))   # object under test, unmodified
    _, spec = host_spectrogram80(y.astype(np.float32))
    _, rms, _ = dsp_register_features(y)
    onset_raw = librosa.onset.onset_strength(y=y.astype(np.float32), sr=SR,
                                             hop_length=HOP, n_fft=N_FFT, center=False)
    n = min(times.size, len(chroma), len(spec), len(rms), stft["mag"].shape[0])
    flux1 = np.zeros(len(spec))
    flux1[1:] = np.clip(np.diff(spec.astype(np.float64), axis=0), 0.0, None).sum(axis=1)
    best_shift, best_s = 0, -np.inf
    for k in range(7):
        cand = np.zeros(times.size)
        for i in range(times.size):
            j = i - k
            if 0 <= j < onset_raw.size:
                cand[i] = onset_raw[j]
        s = _sp(flux1[:n], cand[:n]).statistic
        if np.isfinite(s) and s > best_s:
            best_s, best_shift = float(s), k
    onset = np.zeros(times.size)
    for i in range(times.size):
        j = i - best_shift
        onset[i] = onset_raw[j] if 0 <= j < onset_raw.size else 0.0

    chroma_state = l1_normalise(chroma[:n].astype(np.float64))     # J3E's CONTROL state
    M_chroma = tv_movement(chroma_state)
    M_oracle = tv_movement(st_sym["pc_mass"][:n])
    B_flux = rectified_flux(spec[:n].astype(np.float64))
    B_onset = lagged_abs_delta(onset[:n])
    B_rms = lagged_abs_delta(np.log(rms[:n] + 1e-12))

    sil = st_sym["silent"][:n]
    pair_ok = np.zeros(n, dtype=bool)
    pair_ok[LAG:] = (~sil[LAG:]) & (~sil[:-LAG])
    valid = (pair_ok & silence_mask(rms[:n]) & np.isfinite(M_oracle) & np.isfinite(M_chroma)
             & np.isfinite(B_flux) & np.isfinite(B_onset) & np.isfinite(B_rms))

    return {"track": track_dir.name, "n": n, "valid": valid,
            "oracle_state": l1_rows(st_sym["pc_mass"][:n]), "M_oracle": M_oracle,
            "B_onset": B_onset, "B_rms": B_rms, "chroma_state": chroma_state,
            "M__HOST_CHROMA12": M_chroma,
            "c4_rectified_mass_fraction": c4_rect,
            "raw": {k: v[:n] for k, v in raw.items()}}


def cached_track(track_dir: Path, *, winner: str = "P0_CURRENT") -> dict:
    CACHE.mkdir(parents=True, exist_ok=True)
    f = CACHE / f"{track_dir.name}.npz"
    if f.is_file():
        z = np.load(f, allow_pickle=False)
        b = {"track": track_dir.name, "n": int(z["n"]), "valid": z["valid"],
             "oracle_state": z["oracle_state"], "M_oracle": z["M_oracle"],
             "B_onset": z["B_onset"], "B_rms": z["B_rms"],
             "chroma_state": z["chroma_state"], "M__HOST_CHROMA12": z["M__HOST_CHROMA12"],
             "c4_rectified_mass_fraction": float(z["c4_rect"]),
             "raw": {k: z[f"R_{k}"] for k in RAW_KEYS}}
        return attach_states(b, winner=winner)
    b = build_track(track_dir)
    if b is None:
        raise RuntimeError(f"unusable track {track_dir}")
    np.savez_compressed(
        f, n=b["n"], valid=b["valid"], oracle_state=b["oracle_state"], M_oracle=b["M_oracle"],
        B_onset=b["B_onset"], B_rms=b["B_rms"], chroma_state=b["chroma_state"],
        M__HOST_CHROMA12=b["M__HOST_CHROMA12"], c4_rect=b["c4_rectified_mass_fraction"],
        **{f"R_{k}": v for k, v in b["raw"].items()})
    return attach_states(b, winner=winner)


# ------------------------------------------------------- challenge machinery
def pool(blocks: list[dict], key: str) -> np.ndarray:
    return np.concatenate([b[key][b["valid"]] for b in blocks])


def challenge_masks(blocks: list[dict]) -> tuple[dict, np.ndarray, np.ndarray]:
    groups = np.concatenate([np.full(int(b["valid"].sum()), b["track"]) for b in blocks])
    rM = within_track_rank(pool(blocks, "M_oracle"), groups)
    rO = within_track_rank(pool(blocks, "B_onset"), groups)
    rR = within_track_rank(pool(blocks, "B_rms"), groups)
    cls = {"HARMONIC_CHANGE_FLAT_ENERGY": (rM >= 0.95) & (rR <= 0.50),
           "HARMONIC_CHANGE_NO_ONSET": (rM >= 0.95) & (rO <= 0.50),
           "ACOUSTIC_CHANGE_LOW_HARMONIC_CHANGE": (rO >= 0.95) & (rM <= 0.50)}
    return cls, groups, rM


def level_a_b(blocks: list[dict], name: str, cls: dict, groups: np.ndarray, rM: np.ndarray) -> dict:
    from scipy.stats import spearmanr
    M0 = pool(blocks, "M_oracle")
    MC = np.concatenate([b["mov"][name][b["valid"]] for b in blocks])
    ok = np.isfinite(MC) & np.isfinite(M0)
    rC = within_track_rank(np.where(ok, MC, np.nan), groups)
    top5 = rM >= 0.95
    return {
        "r2": grouped_r2(MC[ok], M0[ok], groups[ok]),
        "spearman": round(float(spearmanr(MC[ok], M0[ok]).statistic), 4),
        "top5_event_recall_in_top20": round(float(((rC >= 0.80) & top5).sum() / max(int(top5.sum()), 1)), 4),
        "challenge_recall": {c: round(float(np.nanmean((rC[m] >= 0.80).astype(float))), 4) for c, m in cls.items()},
        "n_frames": int(ok.sum()),
    }


def lag_curve(blocks: list[dict], name: str, shifts=range(-4, 5)) -> dict:
    out = {}
    for k in shifts:
        Xs, Ys, Gs = [], [], []
        for b in blocks:
            x, y, v = b["mov"][name], b["M_oracle"], b["valid"]
            if k > 0:
                xs, ys, vs = x[:-k], y[k:], v[k:]
            elif k < 0:
                xs, ys, vs = x[-k:], y[:k], v[:k]
            else:
                xs, ys, vs = x, y, v
            keep = vs & np.isfinite(xs) & np.isfinite(ys)
            if keep.sum() < 20:
                continue
            Xs.append(xs[keep]); Ys.append(ys[keep]); Gs.append(np.full(int(keep.sum()), b["track"]))
        out[str(k)] = grouped_r2(np.concatenate(Xs), np.concatenate(Ys), np.concatenate(Gs))
    return out
