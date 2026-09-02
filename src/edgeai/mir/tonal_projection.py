"""J3G - deterministic tonal projections over the EXISTING SpectraSynq STFT.

Every projection in this module consumes the SAME complex rfft frames that
`host_chroma12` computes: 16 kHz, n_fft 2048, hop 512, Hann, causal frame ending
at (i+1)*hop, head zero-padded. No CQT, no second STFT, no alternate rate, no
learned parameter, no per-track tuning.

`stft_power` is computed ONCE per signal and passed by reference to every
candidate, so a candidate cannot silently change the frontend it is supposed to
be improving. `assert_frames_match_host_chroma12` is the blocking control.

Pre-registration: docs/mir/receipts/stft_harmonic_recovery/J3G_PREREGISTRATION.json
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from .host_chroma import chroma_ref_amp

SR = 16_000
HOP = 512
N_FFT = 2048
FREQ_FLOOR_HZ = 40.0

# ---- C1 ---------------------------------------------------------------
C1_SIGMA_SEMITONES = 0.55
# ---- C2 ---------------------------------------------------------------
C2_DELTA_SEMITONES = 2.0 / 3.0
C2_PEAK_REL_THRESHOLD = 0.01
C2_N_HARMONICS = 1
# ---- C3 ---------------------------------------------------------------
C3_MIDI_LOW, C3_MIDI_HIGH = 28, 96
C3_H = 8
C3_HALF_WIDTH_SEMITONES = 0.5
C3_RHO = 0.767  # odd-harmonic fraction of an ideal 1/h series: 1.1716 / 1.5274
# ---- C5 (J3G.2 hybrid) ------------------------------------------------
C5_MIDI_LOW, C5_MIDI_HIGH = 28, 96
C5_H = 8
C5_HALF_WIDTH_SEMITONES = 0.5
C5_RHO = 0.767  # identical analytic derivation to C3_RHO
# ---- C4 ---------------------------------------------------------------
C4_MIDI_LOW, C4_MIDI_HIGH = 28, 96
C4_LOG_C = 1000.0
C4_DCT_CUTOFF = 32  # round(69 * 55/120)

_CACHE: dict = {}


# ======================================================================
# shared STFT
# ======================================================================
def frame_signal(pcm: NDArray, *, sr: int = SR, hop: int = HOP, n_fft: int = N_FFT) -> NDArray[np.float64]:
    """(T, n_fft) causal windowed frames - byte-identical to host_chroma12's."""
    y = np.asarray(pcm, dtype=np.float64).reshape(-1)
    n = max(1, int(y.size // hop)) if y.size >= hop else 1
    out = np.zeros((n, n_fft), dtype=np.float64)
    for i in range(n):
        end = min(y.size, (i + 1) * hop)
        start = end - n_fft
        if start < 0:
            take = y[:end]
            if take.size:
                out[i, -take.size:] = take
        else:
            out[i] = y[start:end]
    return out


def stft_power(
    pcm: NDArray, *, sr: int = SR, hop: int = HOP, n_fft: int = N_FFT, block: int = 2048
) -> dict:
    """THE single STFT. Returns magnitude and power on the causal host grid."""
    y = np.asarray(pcm, dtype=np.float64).reshape(-1)
    n = max(1, int(y.size // hop)) if y.size >= hop else 1
    window = np.hanning(n_fft).astype(np.float64)
    K = n_fft // 2 + 1
    mag = np.zeros((n, K), dtype=np.float64)
    for s in range(0, n, block):
        e = min(s + block, n)
        frames = np.zeros((e - s, n_fft), dtype=np.float64)
        for j, i in enumerate(range(s, e)):
            end = min(y.size, (i + 1) * hop)
            start = end - n_fft
            if start < 0:
                take = y[:end]
                if take.size:
                    frames[j, -take.size:] = take
            else:
                frames[j] = y[start:end]
        mag[s:e] = np.abs(np.fft.rfft(frames * window[None, :], axis=1))
    times = ((np.arange(n, dtype=np.float64) * hop) + hop * 0.5) / float(sr)
    return {"times": times, "mag": mag, "power": mag**2,
            "freqs": np.fft.rfftfreq(n_fft, d=1.0 / float(sr)), "sr": sr, "hop": hop, "n_fft": n_fft}


def assert_frames_match_host_chroma12(pcm: NDArray, *, atol: float = 1e-9) -> float:
    """Blocking control C_FRAMING: the shared framing IS host_chroma12's framing."""
    y = np.asarray(pcm, dtype=np.float64).reshape(-1)
    n = max(1, int(y.size // HOP)) if y.size >= HOP else 1
    ref = np.zeros((n, N_FFT), dtype=np.float64)
    for i in range(n):
        end = min(y.size, (i + 1) * HOP)
        start = end - N_FFT
        frame = np.zeros(N_FFT, dtype=np.float64)
        if start < 0:
            take = y[:end]
            frame[-take.size:] = take
        else:
            frame[:] = y[start:end]
        ref[i] = frame
    err = float(np.max(np.abs(ref - frame_signal(y))))
    if err > atol:
        raise AssertionError(f"shared framing diverges from host_chroma12 by {err:.3g}")
    return err


# ======================================================================
# bin geometry
# ======================================================================
def bin_midi(freqs: NDArray) -> NDArray[np.float64]:
    with np.errstate(divide="ignore", invalid="ignore"):
        return 69.0 + 12.0 * np.log2(np.maximum(np.asarray(freqs, dtype=np.float64), 1e-12) / 440.0)


def nearest_pitch_class_map(freqs: NDArray) -> NDArray[np.int64]:
    """The CURRENT frontend's rule: nearest equal-tempered pitch class, -1 below 40 Hz."""
    pc = np.mod(np.rint(bin_midi(freqs)).astype(np.int64), 12)
    pc[np.asarray(freqs) < FREQ_FLOOR_HZ] = -1
    return pc


def _hard_fold(freqs: NDArray) -> NDArray[np.float64]:
    key = ("hard", freqs.size)
    if key not in _CACHE:
        pc = nearest_pitch_class_map(freqs)
        f = np.zeros((12, freqs.size), dtype=np.float64)
        for b in range(12):
            f[b, pc == b] = 1.0
        _CACHE[key] = f
    return _CACHE[key]


def pitch_class_power_from_stft(st: dict) -> NDArray[np.float64]:
    """(T,12) nearest-bin pitch-class POWER - the current mapping, exactly."""
    return st["power"] @ _hard_fold(st["freqs"]).T


# ======================================================================
# J3G-1 postprocessing variants (mapping held constant)
# ======================================================================
def l1(x: NDArray, *, eps: float = 1e-12) -> NDArray[np.float64]:
    a = np.asarray(x, dtype=np.float64)
    s = np.sum(np.abs(a), axis=1, keepdims=True)
    return np.divide(a, s, out=np.zeros_like(a), where=s > eps)


def post_P0(pc_power: NDArray) -> NDArray[np.float64]:
    """host_chroma12 exactly: sqrt, /frozen reference, clip to [0,1]."""
    ref = chroma_ref_amp(sr=SR, hop=HOP, n_fft=N_FFT)
    return np.clip(np.sqrt(np.asarray(pc_power, dtype=np.float64)) / ref, 0.0, 1.0)


def post_P1(pc_power: NDArray) -> NDArray[np.float64]:
    """Power, no sqrt, no reference, no clip."""
    return np.asarray(pc_power, dtype=np.float64)


def post_P2(pc_power: NDArray) -> NDArray[np.float64]:
    """sqrt(power), no reference, no clip."""
    return np.sqrt(np.asarray(pc_power, dtype=np.float64))


POSTPROCESSORS = {"P0_CURRENT": post_P0, "P1_POWER_L1": post_P1, "P2_SQRT_L1_NO_CLIP": post_P2}
# exponent applied to a POWER-domain quantity by each variant (P0 also clips)
POST_POWER_EXPONENT = {"P0_CURRENT": 0.5, "P1_POWER_L1": 1.0, "P2_SQRT_L1_NO_CLIP": 0.5}


def apply_carry_forward(x: NDArray, *, native_domain: str, winner: str) -> NDArray[np.float64]:
    """Apply the J3G-1 winning compression in the candidate's native domain.

    power-domain     -> exponent g
    amplitude-domain -> exponent 2g  (equivalent compression of the same energy)
    log-domain (C4)  -> exempt, returned unchanged
    """
    a = np.asarray(x, dtype=np.float64)
    if native_domain == "log":
        return a
    g = POST_POWER_EXPONENT[winner]
    e = g if native_domain == "power" else 2.0 * g
    return np.power(np.clip(a, 0.0, None), e)


# ======================================================================
# C1 - soft STFT chroma filterbank
# ======================================================================
def c1_filterbank(freqs: NDArray, *, sigma: float = C1_SIGMA_SEMITONES) -> NDArray[np.float64]:
    key = ("c1", freqs.size, sigma)
    if key not in _CACHE:
        f = np.asarray(freqs, dtype=np.float64)
        p = np.mod(bin_midi(f), 12.0)                       # (K,)
        b = np.arange(12, dtype=np.float64)[:, None]        # (12,1)
        d = np.mod(p[None, :] - b + 6.0, 12.0) - 6.0        # circular, (12,K)
        w = np.exp(-0.5 * (d / sigma) ** 2)
        w[:, f < FREQ_FLOOR_HZ] = 0.0
        col = w.sum(axis=0, keepdims=True)
        w = np.divide(w, col, out=np.zeros_like(w), where=col > 1e-12)
        _CACHE[key] = w
    return _CACHE[key]


def c1_soft_chroma(st: dict) -> NDArray[np.float64]:
    """(T,12) power-domain. Smooth pitch-class assignment, columns sum to 1."""
    return st["power"] @ c1_filterbank(st["freqs"]).T


# ======================================================================
# C2 - peak-weighted HPCP-class projection
# ======================================================================
def _peaks(st: dict) -> dict:
    """Interpolated spectral peaks from the SAME STFT. No new transform."""
    m = st["mag"]
    T, K = m.shape
    left, cen, right = m[:, :-2], m[:, 1:-1], m[:, 2:]
    is_peak = (cen > left) & (cen >= right)
    f = st["freqs"]
    is_peak &= (f[1:-1] >= FREQ_FLOOR_HZ)[None, :]
    rows, cols = np.nonzero(is_peak)
    if rows.size == 0:
        return {"rows": rows, "freq": np.zeros(0), "amp": np.zeros(0)}
    eps = 1e-20
    la = np.log(left[rows, cols] + eps)
    lb = np.log(cen[rows, cols] + eps)
    lg = np.log(right[rows, cols] + eps)
    den = la - 2.0 * lb + lg
    delta = np.where(np.abs(den) > 1e-12, 0.5 * (la - lg) / np.where(np.abs(den) > 1e-12, den, 1.0), 0.0)
    delta = np.clip(delta, -0.5, 0.5)
    k = cols + 1
    freq = (k + delta) * (st["sr"] / st["n_fft"])
    amp = np.exp(lb - 0.25 * (la - lg) * delta)
    # relative threshold against the frame's largest peak
    frame_max = np.zeros(T)
    np.maximum.at(frame_max, rows, amp)
    keep = amp >= C2_PEAK_REL_THRESHOLD * frame_max[rows]
    return {"rows": rows[keep], "freq": freq[keep], "amp": amp[keep]}


def c2_peak_hpcp(st: dict, *, delta_st: float = C2_DELTA_SEMITONES) -> NDArray[np.float64]:
    """(T,12) power-domain. Only stable interpolated peaks vote. n_harmonics = 1."""
    T = st["mag"].shape[0]
    out = np.zeros((T, 12), dtype=np.float64)
    pk = _peaks(st)
    if pk["rows"].size == 0:
        return out
    p = np.mod(bin_midi(pk["freq"]), 12.0)
    contrib = pk["amp"] ** 2
    lo = np.floor(p)
    d_lo = p - lo
    for b_off, d in ((0.0, d_lo), (1.0, 1.0 - d_lo)):
        b = np.mod(lo + b_off, 12.0).astype(np.int64)
        w = np.where(d <= delta_st, np.cos(0.5 * np.pi * d / delta_st) ** 2, 0.0)
        flat = np.bincount(pk["rows"] * 12 + b, weights=contrib * w, minlength=T * 12)
        out += flat.reshape(T, 12)
    return out


# ======================================================================
# C3 - fundamental / root-salience projection
# ======================================================================
def _window_bins(freqs: NDArray, target_hz: float, half_st: float) -> tuple[int, int]:
    lo = target_hz * 2.0 ** (-half_st / 12.0)
    hi = target_hz * 2.0 ** (half_st / 12.0)
    s = int(np.searchsorted(freqs, lo, side="left"))
    e = int(np.searchsorted(freqs, hi, side="right"))
    if e <= s:  # declared empty-window rule: single nearest bin
        j = int(np.argmin(np.abs(freqs - target_hz)))
        return j, j + 1
    return s, e


def _c3_ranges(freqs: NDArray) -> list[list[tuple[int, int]]]:
    key = ("c3", freqs.size)
    if key not in _CACHE:
        out = []
        for m in range(C3_MIDI_LOW, C3_MIDI_HIGH + 1):
            f0 = 440.0 * 2.0 ** ((m - 69) / 12.0)
            rs = []
            for h in range(1, C3_H + 1):
                fh = h * f0
                rs.append((-1, -1) if fh >= freqs[-1] else _window_bins(freqs, fh, C3_HALF_WIDTH_SEMITONES))
            out.append(rs)
        _CACHE[key] = out
    return _CACHE[key]


def c3_root_salience(st: dict) -> NDArray[np.float64]:
    """(T,12) amplitude-domain. Harmonic stacks become evidence for their ROOT."""
    P = st["power"]
    T = P.shape[0]
    ranges = _c3_ranges(st["freqs"])
    n_c = C3_MIDI_HIGH - C3_MIDI_LOW + 1
    A = np.zeros((T, n_c, C3_H), dtype=np.float64)
    for ci, rs in enumerate(ranges):
        for h, (s, e) in enumerate(rs):
            if s >= 0:
                A[:, ci, h] = np.sqrt(P[:, s:e].max(axis=1))
    w = 1.0 / np.arange(1, C3_H + 1, dtype=np.float64)
    tot = (A * w[None, None, :]).sum(axis=2)
    odd = np.arange(C3_H) % 2 == 0  # h = 1,3,5,7
    odd_sum = (A[:, :, odd] * w[None, None, odd]).sum(axis=2)
    odd_frac = np.divide(odd_sum, tot + 1e-12, out=np.zeros_like(tot), where=True)
    sal = tot * np.minimum(1.0, odd_frac / C3_RHO)
    out = np.zeros((T, 12), dtype=np.float64)
    for ci in range(n_c):
        out[:, (C3_MIDI_LOW + ci) % 12] += sal[:, ci]
    return out


# ======================================================================
# C5 - J3G.2 peak-to-root hybrid
# ======================================================================
def _c5_targets() -> tuple[NDArray, NDArray]:
    """(n_c, H) target frequencies in MIDI, and the candidates' pitch classes."""
    key = ("c5t",)
    if key not in _CACHE:
        m = np.arange(C5_MIDI_LOW, C5_MIDI_HIGH + 1, dtype=np.float64)
        f0 = 440.0 * 2.0 ** ((m - 69.0) / 12.0)
        h = np.arange(1, C5_H + 1, dtype=np.float64)
        fh = f0[:, None] * h[None, :]
        _CACHE[key] = (69.0 + 12.0 * np.log2(fh / 440.0), np.mod(m.astype(np.int64), 12))
    return _CACHE[key]


def c5_peak_root(st: dict) -> NDArray[np.float64]:
    """(T,12) amplitude-domain. C3's root inference fed by C2's interpolated peaks.

    Single variable changed from the corrected C3: the evidence source. Candidate
    grid, harmonic count, 1/h weights, +/-0.5 semitone tolerance and the saturating
    octave gate min(1, odd_frac/rho) are inherited unchanged.
    """
    T = st["mag"].shape[0]
    out = np.zeros((T, 12), dtype=np.float64)
    pk = _peaks(st)                      # EXACTLY C2's peak set
    if pk["rows"].size == 0:
        return out
    tgt_midi, cand_pc = _c5_targets()
    n_c = tgt_midi.shape[0]
    pk_midi = bin_midi(pk["freq"])
    w = 1.0 / np.arange(1, C5_H + 1, dtype=np.float64)

    # A[t, c, h] = amplitude of the LARGEST peak within +/- 0.5 semitone of h*f0(c)
    A = np.zeros((T, n_c, C5_H), dtype=np.float64)
    flat = tgt_midi.reshape(-1)
    order = np.argsort(flat)
    lo = np.searchsorted(flat[order], pk_midi - C5_HALF_WIDTH_SEMITONES, side="left")
    hi = np.searchsorted(flat[order], pk_midi + C5_HALF_WIDTH_SEMITONES, side="right")
    for j in range(int(pk["rows"].size)):
        s, e = lo[j], hi[j]
        if e <= s:
            continue
        idx = order[s:e]
        np.maximum.at(A[pk["rows"][j]].reshape(-1), idx, pk["amp"][j])

    tot = (A * w[None, None, :]).sum(axis=2)
    odd = np.arange(C5_H) % 2 == 0                      # h = 1, 3, 5, 7
    odd_sum = (A[:, :, odd] * w[None, None, odd]).sum(axis=2)
    odd_frac = np.divide(odd_sum, tot + 1e-12, out=np.zeros_like(tot), where=True)
    sal = tot * np.minimum(1.0, odd_frac / C5_RHO)
    for ci in range(n_c):
        out[:, cand_pc[ci]] += sal[:, ci]
    return out


# ======================================================================
# C4 - timbre-robust CRP-class projection
# ======================================================================
def _pitch_pool(freqs: NDArray, midi_low: int, midi_high: int) -> NDArray[np.float64]:
    key = ("pool", freqs.size, midi_low, midi_high)
    if key not in _CACHE:
        n = midi_high - midi_low + 1
        M = np.zeros((n, freqs.size), dtype=np.float64)
        for i, m in enumerate(range(midi_low, midi_high + 1)):
            f = 440.0 * 2.0 ** ((m - 69) / 12.0)
            s, e = _window_bins(freqs, f, 0.5)
            M[i, s:e] = 1.0
        _CACHE[key] = M
    return _CACHE[key]


def _crp_projection(n: int, cutoff: int) -> NDArray[np.float64]:
    """One fixed n x n matrix: DCT-II -> zero low coefficients -> inverse DCT."""
    key = ("crp", n, cutoff)
    if key not in _CACHE:
        from scipy.fftpack import dct, idct
        D = dct(np.eye(n), type=2, norm="ortho", axis=0)     # rows = coefficients
        D[:cutoff, :] = 0.0
        _CACHE[key] = idct(D, type=2, norm="ortho", axis=0)
    return _CACHE[key]


def c4_crp_chroma(st: dict) -> dict:
    """(T,12) log-domain, half-wave rectified. Reports the rectified mass fraction."""
    v = st["power"] @ _pitch_pool(st["freqs"], C4_MIDI_LOW, C4_MIDI_HIGH).T
    u = np.log(1.0 + C4_LOG_C * v)
    n = u.shape[1]
    y = u @ _crp_projection(n, C4_DCT_CUTOFF).T
    neg = float(np.abs(np.clip(y, None, 0.0)).sum() / (np.abs(y).sum() + 1e-20))
    y = np.clip(y, 0.0, None)
    out = np.zeros((u.shape[0], 12), dtype=np.float64)
    for i in range(n):
        out[:, (C4_MIDI_LOW + i) % 12] += y[:, i]
    return {"chroma": out, "rectified_mass_fraction": round(neg, 4)}


# ======================================================================
# candidate registry
# ======================================================================
def candidate_states(st: dict, *, winner: str) -> dict:
    """All candidates from ONE shared STFT, each L1-normalised for the movement metric."""
    pcp = pitch_class_power_from_stft(st)
    out = {
        "P0_CURRENT": l1(post_P0(pcp)),
        "P1_POWER_L1": l1(post_P1(pcp)),
        "P2_SQRT_L1_NO_CLIP": l1(post_P2(pcp)),
        "C1_SOFT_FILTERBANK": l1(apply_carry_forward(c1_soft_chroma(st), native_domain="power", winner=winner)),
        "C2_PEAK_HPCP": l1(apply_carry_forward(c2_peak_hpcp(st), native_domain="power", winner=winner)),
        "C3_ROOT_SALIENCE": l1(apply_carry_forward(c3_root_salience(st), native_domain="amplitude", winner=winner)),
    }
    c4 = c4_crp_chroma(st)
    out["C4_CRP"] = l1(c4["chroma"])
    out["_c4_rectified_mass_fraction"] = c4["rectified_mass_fraction"]
    return out


def arithmetic_cost_per_frame(n_fft: int = N_FFT) -> dict:
    """Declared marginal cost, EXCLUDING the STFT every candidate shares."""
    K = n_fft // 2 + 1
    n_c3 = C3_MIDI_HIGH - C3_MIDI_LOW + 1
    n_c4 = C4_MIDI_HIGH - C4_MIDI_LOW + 1
    return {
        "shared_stft_excluded": True,
        "P0_P1_P2_nearest_bin": {"mac": K, "note": "one accumulate per bin"},
        "C1_SOFT_FILTERBANK": {"mac": 12 * K, "note": "dense 12xK matrix-vector; a 3-nonzero-per-column sparse form costs ~3K"},
        "C2_PEAK_HPCP": {"mac": "~3K compares + ~2 x n_peaks", "note": "peak picking dominates; n_peaks is typically << K"},
        "C3_ROOT_SALIENCE": {"mac": n_c3 * C3_H * 2, "note": f"{n_c3} candidates x {C3_H} harmonics, max+accumulate"},
        "C4_CRP": {"mac": n_c4 * K + n_c4 * n_c4, "note": "pitch pooling then ONE fixed 69x69 projection"},
    }
