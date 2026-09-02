"""J3A — causal pitch-class / register representations on the HOST oracle grid.

Exact MIDI is the authority here. No teacher, no transcription model: BabySlakh
ships aligned symbolic truth, so introducing Basic Pitch would only add teacher
error to a question that has a closed-form answer.

Everything shares ONE convention with the repo's existing `host_chroma12` and
`source_oracle`:
    frame i uses samples [ (i+1)*hop - n_fft , (i+1)*hop )
    timestamp of frame i is the hop CENTRE, ((i*hop) + hop/2)/sr
so the analysis window ends +hop/2 samples after the stated timestamp. That is
disclosed, identical on both the audio and the label side, and therefore fair.

Labels never see the future: a note may only influence frames whose window has
already begun when the note sounds.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

SR = 16_000
HOP = 512
N_FFT = 2048
SILENCE_FLOOR_DBFS = -60.0


def frame_grid(n_samples: int, *, sr: int = SR, hop: int = HOP) -> tuple[NDArray, NDArray]:
    """(hop-centre times in seconds, frame end sample indices)."""
    n = max(1, int(n_samples // hop)) if n_samples >= hop else 1
    idx = np.arange(n, dtype=np.int64)
    times = ((idx * hop) + hop * 0.5) / float(sr)
    ends = (idx + 1) * hop
    return times.astype(np.float64), ends.astype(np.int64)


@dataclass(frozen=True)
class Note:
    start_s: float
    end_s: float
    pitch: int
    velocity: int


def midi_targets(
    notes: list[Note],
    n_frames: int,
    *,
    sr: int = SR,
    hop: int = HOP,
    n_fft: int = N_FFT,
) -> dict[str, NDArray]:
    """Exact symbolic targets on the causal grid.

    Returns
      pitch_class_mass (T,12)  velocity x in-window sounding seconds, per pitch class
      register_centroid (T,)   velocity x seconds weighted mean MIDI note number
      n_active (T,)            number of distinct notes sounding in the window
      weight_total (T,)        total weight (0 => label UNDEFINED, never zero-filled)
    """
    win_s = n_fft / float(sr)
    hop_s = hop / float(sr)
    # frame i window = [ (i+1)*hop_s - win_s , (i+1)*hop_s )
    starts = (np.arange(n_frames, dtype=np.float64) + 1.0) * hop_s - win_s
    ends = (np.arange(n_frames, dtype=np.float64) + 1.0) * hop_s

    mass = np.zeros((n_frames, 12), dtype=np.float64)
    reg_num = np.zeros(n_frames, dtype=np.float64)
    wtot = np.zeros(n_frames, dtype=np.float64)
    nact = np.zeros(n_frames, dtype=np.int64)

    for nt in notes:
        if nt.end_s <= nt.start_s:
            continue
        # frames whose window overlaps [start, end)
        lo = int(np.floor((nt.start_s / hop_s) - 1.0))
        hi = int(np.ceil((nt.end_s + win_s) / hop_s))
        lo = max(lo, 0)
        hi = min(hi, n_frames)
        if hi <= lo:
            continue
        fs = starts[lo:hi]
        fe = ends[lo:hi]
        ov = np.minimum(fe, nt.end_s) - np.maximum(fs, nt.start_s)
        np.clip(ov, 0.0, None, out=ov)
        hit = ov > 0.0
        if not hit.any():
            continue
        w = ov * float(max(nt.velocity, 1))
        idx = np.arange(lo, hi)[hit]
        wv = w[hit]
        np.add.at(mass, (idx, nt.pitch % 12), wv)
        np.add.at(reg_num, idx, wv * float(nt.pitch))
        np.add.at(wtot, idx, wv)
        np.add.at(nact, idx, 1)

    with np.errstate(invalid="ignore", divide="ignore"):
        reg = np.divide(reg_num, wtot, out=np.full(n_frames, np.nan), where=wtot > 0)
    return {
        "pitch_class_mass": mass,
        "register_centroid": reg,
        "n_active": nact,
        "weight_total": wtot,
    }


def l1_normalise(x: NDArray, *, eps: float = 1e-12) -> NDArray:
    s = np.sum(np.abs(x), axis=1, keepdims=True)
    return np.divide(x, s, out=np.zeros_like(x, dtype=np.float64), where=s > eps)


def dsp_register_features(
    pcm: NDArray,
    *,
    sr: int = SR,
    hop: int = HOP,
    n_fft: int = N_FFT,
) -> tuple[NDArray, NDArray, list[str]]:
    """B1 for H2: the register-relevant features a lighting DSP already computes.

    spectral centroid (log Hz), rolloff85 (log Hz), 3 log band energies, plus
    log frame RMS. Same causal framing as host_chroma12. NOT chroma - chroma is
    octave-folded and cannot represent register by construction.
    """
    y = np.asarray(pcm, dtype=np.float64).reshape(-1)
    times, ends = frame_grid(y.size, sr=sr, hop=hop)
    n = times.size
    window = np.hanning(n_fft)
    freqs = np.fft.rfftfreq(n_fft, d=1.0 / float(sr))
    bands = [(40.0, 250.0), (250.0, 2000.0), (2000.0, sr / 2.0)]
    masks = [(freqs >= lo) & (freqs < hi) for lo, hi in bands]

    out = np.zeros((n, 6), dtype=np.float64)
    rms = np.zeros(n, dtype=np.float64)
    for i in range(n):
        end = int(min(y.size, ends[i]))
        start = end - n_fft
        frame = np.zeros(n_fft, dtype=np.float64)
        if start < 0:
            take = y[:end]
            if take.size:
                frame[-take.size :] = take
        else:
            frame[:] = y[start:end]
        rms[i] = float(np.sqrt(np.mean(frame**2)) + 1e-12)
        mag = np.abs(np.fft.rfft(frame * window))
        p = mag**2
        tot = float(p.sum()) + 1e-20
        centroid = float((freqs * p).sum() / tot)
        csum = np.cumsum(p)
        roll_i = int(np.searchsorted(csum, 0.85 * csum[-1]))
        rolloff = float(freqs[min(roll_i, freqs.size - 1)])
        out[i, 0] = np.log(max(centroid, 20.0))
        out[i, 1] = np.log(max(rolloff, 20.0))
        for b, m in enumerate(masks):
            out[i, 2 + b] = np.log(float(p[m].sum()) + 1e-20)
        out[i, 5] = np.log(rms[i])
    names = ["log_centroid", "log_rolloff85", "log_band_low", "log_band_mid", "log_band_high", "log_rms"]
    return out, rms, names


def silence_mask(rms: NDArray, *, floor_dbfs: float = SILENCE_FLOOR_DBFS) -> NDArray:
    return 20.0 * np.log10(np.asarray(rms, dtype=np.float64) + 1e-12) > floor_dbfs


# --------------------------------------------------------------------------
# J3C - deterministic register estimators over the EXISTING host_spectrogram80.
# No second FFT, no CQT, no alternate sample rate, no new frontend. Every
# function below is arithmetic on the frontend's own output.
# --------------------------------------------------------------------------

SPEC80_FMIN = 40.0
SPEC80_N_BINS = 80


def spec80_midi_positions(*, sr: int = SR, n_bins: int = SPEC80_N_BINS) -> NDArray[np.float64]:
    """MIDI position of each host_spectrogram80 bin (geometric bin centre)."""
    edges = np.geomspace(SPEC80_FMIN, max(80.0, sr * 0.5), n_bins + 1)
    centres = np.sqrt(edges[:-1] * edges[1:])
    return 69.0 + 12.0 * np.log2(centres / 440.0)


def spec80_decompress(spec01: NDArray) -> NDArray[np.float64]:
    """Invert the frontend's own compression: clip(log1p(mag)/4,0,1) -> mag.

    Arithmetic on the emitted frame, not a new transform. Bins the frontend
    clipped at 1.0 remain saturated and unrecoverable.
    """
    return np.expm1(4.0 * np.asarray(spec01, dtype=np.float64))


def weighted_centroid(weights: NDArray, positions: NDArray) -> NDArray[np.float64]:
    w = np.asarray(weights, dtype=np.float64)
    tot = w.sum(axis=1) + 1e-20
    return (w * positions[None, :]).sum(axis=1) / tot


def weighted_quantile(weights: NDArray, positions: NDArray, q: float) -> NDArray[np.float64]:
    """MIDI position where the cumulative weight distribution crosses q."""
    w = np.asarray(weights, dtype=np.float64)
    c = np.cumsum(w, axis=1)
    tot = c[:, -1:] + 1e-20
    c = c / tot
    idx = np.argmax(c >= q, axis=1)
    lo = np.maximum(idx - 1, 0)
    c_hi = np.take_along_axis(c, idx[:, None], 1)[:, 0]
    c_lo = np.take_along_axis(c, lo[:, None], 1)[:, 0]
    p_hi, p_lo = positions[idx], positions[lo]
    span = np.where(c_hi - c_lo > 1e-12, c_hi - c_lo, 1.0)
    frac = np.clip((q - c_lo) / span, 0.0, 1.0)
    return p_lo + frac * (p_hi - p_lo)


def harmonic_sum_spectrum(
    weights: NDArray,
    positions: NDArray,
    *,
    n_harmonics: int = 5,
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Subharmonic summation on the MIDI-position axis.

    S(m) = sum_{k=1..K} (1/k) * P(m + 12*log2(k)), linearly interpolated.
    Suppresses the upward harmonic bias that makes a plain spectral centroid a
    poor estimate of fundamental register. Evaluated only where every harmonic
    position falls inside the axis.
    """
    w = np.asarray(weights, dtype=np.float64)
    offsets = 12.0 * np.log2(np.arange(1, n_harmonics + 1, dtype=np.float64))
    keep = positions + offsets[-1] <= positions[-1] + 1e-9
    m_grid = positions[keep]
    S = np.zeros((w.shape[0], m_grid.size), dtype=np.float64)
    for k, off in enumerate(offsets, start=1):
        tgt = m_grid + off
        lo = np.searchsorted(positions, tgt) - 1
        lo = np.clip(lo, 0, positions.size - 2)
        hi = lo + 1
        span = positions[hi] - positions[lo]
        frac = np.clip((tgt - positions[lo]) / np.where(span > 1e-12, span, 1.0), 0.0, 1.0)
        S += (1.0 / k) * (w[:, lo] * (1.0 - frac)[None, :] + w[:, hi] * frac[None, :])
    return S, m_grid
