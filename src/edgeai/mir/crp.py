"""J3M - faithful CRP-class timbre-invariant chroma (Mueller & Ewert).

HOST INFORMATION PROBE ONLY. This is NOT a product frontend, NOT a proposal for
firmware, and NOT a same-STFT approximation. It exists to answer one question:
does the information we want exist under the CRP hypothesis?

Published algorithm (Chroma Toolbox 2.0, `audio_to_pitch_via_FB` + `pitch_to_CRP`):
  * 88-band multirate elliptic pitch filterbank, MIDI 21..108, zero-phase filtfilt
  * short-time mean-square energy per pitch
  * log compression  log10(1 + 1000 * v)
  * 120x120 orthonormal DCT-II  M[m,n] = sqrt(2/120) * cos(m*(n+0.5)*pi/120),
    first row scaled by 1/sqrt(2)
  * keep DCT coefficient rows 55..120 (1-indexed) - CRP(55) - zero the rest
  * inverse transform, fold to 12 pitch classes by mod 12
  * l2 normalisation, threshold 1e-6
  * CRP vectors MAY HAVE NEGATIVE ENTRIES and are kept signed here

Deviations from the published implementation are enumerated in DEVIATIONS and
reproduced verbatim into the J3M receipt.

Pre-registration: docs/mir/receipts/crp_probe/J3M_PREREGISTRATION.json
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray
from scipy.signal import decimate, ellip, sosfiltfilt

from .note_register import HOP, N_FFT, SR

MIDI_MIN, MIDI_MAX = 21, 108
N_PITCH_DIMS = 120
COEFFS_TO_KEEP = (54, 120)      # 0-indexed [54, 120) == MATLAB [55:120]
LOG_FACTOR, LOG_ADD = 1000.0, 1.0
NORM_P, NORM_THRESH = 2.0, 1e-6
ELLIP_ORDER, ELLIP_RP_DB, ELLIP_RS_DB = 4, 1.0, 50.0
Q_FACTOR = 25.0                 # from the toolbox filterbank naming, "..._Q25"
GROUPS = ((21, 59), (60, 95), (96, 108))     # published pitch groups, unchanged

DEVIATIONS = [
    "input sample rate is 16 kHz, not the published 22050 Hz, so the multirate "
    "decimation factors are re-derived. Published: 882 / 4410 / 22050 for MIDI "
    "21-59 / 60-95 / 96-108. Here: 800 / 8000 / 16000 (decimate 20 / 2 / 1). The "
    "published pitch-group BOUNDARIES are preserved; only the rate each group is "
    "computed at changes, chosen as the lowest of the available rates whose Nyquist "
    "exceeds 1.15x the group's highest centre frequency. Multirate is a "
    "computational device, not part of the feature definition, so this does not "
    "alter the intended filter responses.",
    "short-time energy is computed on the SpectraSynq analysis grid - 2048-sample "
    "window, 512 hop, causal frame ending at (i+1)*hop - instead of the published "
    "4410-sample window with 50% overlap at 22050 Hz (200 ms, 10 Hz feature rate). "
    "This is required so CRP movement is comparable with C3 movement at the same "
    "lag of 8 hops. Our window is SHORTER and therefore LESS smoothed than the "
    "published one, which if anything makes CRP more responsive - a bias AGAINST "
    "the restraint hypothesis under test, not for it.",
    "the published filterbank uses filtfilt, which is ZERO-PHASE and therefore "
    "NON-CAUSAL. That is retained here for fidelity. It is a hard blocker for any "
    "product path and is the reason this is labelled a HOST information probe.",
    "the filter coefficients are designed here with scipy.signal.ellip rather than "
    "loaded from the toolbox's precomputed .mat files, which were not available. "
    "Order, ripple, attenuation and band edges are declared below and the ACHIEVED "
    "responses are measured and reported as a fidelity control.",
    "movement is computed on the sum(|x|)-normalised CRP vector as specified by the "
    "brief. The published normalisation is l2; it is applied to the feature and is "
    "then superseded for the movement metric by the brief's rule.",
]

_CACHE: dict = {}


def _rate_for_group(hi_midi: int, rates=(800, 8000, 16000)) -> int:
    f_hi = 440.0 * 2.0 ** ((hi_midi - 69) / 12.0)
    for r in rates:
        if r / 2.0 > 1.15 * f_hi:
            return r
    return rates[-1]


def filterbank() -> list[dict]:
    """88 elliptic pitch filters with their computation rate. Declared, not tuned."""
    if "fb" not in _CACHE:
        out = []
        for lo, hi in GROUPS:
            rate = _rate_for_group(hi)
            for p in range(lo, hi + 1):
                f = 440.0 * 2.0 ** ((p - 69) / 12.0)
                half = f / (2.0 * Q_FACTOR)                       # Q = 25 passband
                wp = [(f - half) / (rate / 2.0), (f + half) / (rate / 2.0)]
                ws_lo = f * 2.0 ** (-1.0 / 12.0) / (rate / 2.0)   # adjacent semitone
                ws_hi = f * 2.0 ** (1.0 / 12.0) / (rate / 2.0)
                sos = ellip(ELLIP_ORDER, ELLIP_RP_DB, ELLIP_RS_DB, wp,
                            btype="bandpass", output="sos")
                out.append({"midi": p, "f_hz": f, "rate": rate, "sos": sos,
                            "wp": wp, "ws": [ws_lo, ws_hi]})
        _CACHE["fb"] = out
    return _CACHE["fb"]


def filterbank_fidelity() -> dict:
    """Measured response: passband ripple at +/-25 cents, adjacent-semitone rejection."""
    from scipy.signal import sosfreqz
    rip, adj = [], []
    for h in filterbank():
        f0, rate = h["f_hz"], h["rate"]
        probe = np.array([f0 * 2.0 ** (c / 1200.0) for c in (-25, 0, 25)]
                         + [f0 * 2.0 ** (s / 12.0) for s in (-1, 1)])
        w = 2.0 * np.pi * probe / rate
        keep = w < np.pi
        _, hh = sosfreqz(h["sos"], worN=w[keep])
        mag = np.abs(hh)
        peak = float(mag[: min(3, len(mag))].max())
        if peak <= 0:
            continue
        rip.append(20.0 * np.log10(mag[: min(3, len(mag))].min() / peak))
        if len(mag) > 3:
            adj.append(20.0 * np.log10(max(mag[3:].max(), 1e-12) / peak))
    return {"n_filters": len(filterbank()),
            "passband_min_gain_within_pm25_cents_dB": {
                "median": round(float(np.median(rip)), 2),
                "worst": round(float(np.min(rip)), 2)},
            "adjacent_semitone_rejection_dB": {
                "median": round(float(np.median(adj)), 2),
                "worst": round(float(np.max(adj)), 2)},
            "declared": {"order": ELLIP_ORDER, "passband_ripple_dB": ELLIP_RP_DB,
                         "stopband_attenuation_dB": ELLIP_RS_DB, "Q": Q_FACTOR,
                         "passband_edges": "f0 * (1 -+ 1/(2Q))",
                         "stopband_reference": "adjacent semitone centres"},
            "rates_used": {f"{lo}-{hi}": _rate_for_group(hi) for lo, hi in GROUPS}}


def pitch_energy(pcm: NDArray, *, sr: int = SR, hop: int = HOP,
                 n_fft: int = N_FFT) -> NDArray[np.float64]:
    """(T, 120) short-time mean-square energy per MIDI pitch on the analysis grid."""
    y = np.asarray(pcm, dtype=np.float64).reshape(-1)
    n = max(1, int(y.size // hop)) if y.size >= hop else 1
    out = np.zeros((n, N_PITCH_DIMS), dtype=np.float64)
    ds: dict[int, np.ndarray] = {}
    for rate in sorted({h["rate"] for h in filterbank()}):
        if rate == sr:
            ds[rate] = y
        else:
            q = int(round(sr / rate))
            ds[rate] = decimate(y, q, ftype="fir", zero_phase=True)
    for h in filterbank():
        rate = h["rate"]
        x = ds[rate]
        v = sosfiltfilt(h["sos"], x) ** 2
        k = rate / float(sr)
        w = max(1, int(round(n_fft * k)))
        ends = np.rint((np.arange(n) + 1) * hop * k).astype(np.int64)
        c = np.concatenate([[0.0], np.cumsum(v)])
        e = np.clip(ends, 0, v.size)
        s = np.clip(ends - w, 0, v.size)
        out[:, h["midi"]] = (c[e] - c[s]) / np.maximum(e - s, 1)
    return out


def _dct_filter() -> NDArray[np.float64]:
    """Mueller's 120x120 orthonormal DCT-II with rows 0..53 zeroed, then inverted."""
    if "dctf" not in _CACHE:
        m = np.arange(N_PITCH_DIMS)[:, None]
        nn = np.arange(N_PITCH_DIMS)[None, :]
        D = np.sqrt(2.0 / N_PITCH_DIMS) * np.cos(m * (nn + 0.5) * np.pi / N_PITCH_DIMS)
        D[0, :] /= np.sqrt(2.0)
        cut = D.copy()
        cut[: COEFFS_TO_KEEP[0], :] = 0.0
        _CACHE["dctf"] = D.T @ cut
    return _CACHE["dctf"]


def log_pitch(pitch: NDArray) -> NDArray[np.float64]:
    """The shared upstream: published log compression log10(1 + 1000 * v).

    J3N requires the FB_LOG_CHROMA arm and the CRP arm to be byte-identical
    upstream of the DCT, so both derive from this one function.
    """
    return np.log10(LOG_ADD + LOG_FACTOR * np.asarray(pitch, dtype=np.float64))


def fb_log_chroma_from_log(lg: NDArray) -> NDArray[np.float64]:
    """J3N ablation arm: CRP with the cepstral liftering DELETED and nothing else.

    pitch filterbank -> log compression -> NO DCT, NO coefficient deletion,
    NO inverse DCT -> fold mod 12 -> L1. Non-negative by construction.
    """
    a = np.asarray(lg, dtype=np.float64)
    out = np.zeros((a.shape[0], 12), dtype=np.float64)
    for p in range(N_PITCH_DIMS):
        out[:, p % 12] += a[:, p]
    s = np.sum(np.abs(out), axis=1, keepdims=True)
    return np.divide(out, s, out=np.zeros_like(out), where=s > 1e-12)


def fb_log_chroma(pitch: NDArray) -> NDArray[np.float64]:
    return fb_log_chroma_from_log(log_pitch(pitch))


def crp_from_log(lg: NDArray) -> NDArray[np.float64]:
    """CRP(55) from the shared log-compressed pitch surface."""
    red = np.asarray(lg, dtype=np.float64) @ _dct_filter().T
    v = np.asarray(lg)
    out = np.zeros((v.shape[0], 12), dtype=np.float64)
    for p in range(N_PITCH_DIMS):
        out[:, p % 12] += red[:, p]
    nrm = np.power(np.sum(np.abs(out) ** NORM_P, axis=1, keepdims=True), 1.0 / NORM_P)
    return np.divide(out, nrm, out=np.zeros_like(out), where=nrm > NORM_THRESH)


def crp(pitch: NDArray) -> NDArray[np.float64]:
    """(T,12) SIGNED CRP(55). No rectification, no absolute value, no floor."""
    return crp_from_log(log_pitch(pitch))


def crp_movement(c: NDArray, *, lag: int = 8) -> NDArray[np.float64]:
    """Brief's rule: normalise by sum(|x|) where non-zero, then 0.5 * L1 at the lag."""
    a = np.asarray(c, dtype=np.float64)
    s = np.sum(np.abs(a), axis=1, keepdims=True)
    p = np.divide(a, s, out=np.zeros_like(a), where=s > 1e-12)
    out = np.full(p.shape[0], np.nan)
    if p.shape[0] > lag:
        out[lag:] = 0.5 * np.abs(p[lag:] - p[:-lag]).sum(axis=1)
    return out
