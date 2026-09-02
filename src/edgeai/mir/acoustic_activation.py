"""J3J - acoustic-activation attack kernels and the ACOUSTIC_ACTIVATION_PC target.

REPRESENTATION-INDEPENDENT BY CONSTRUCTION. This module imports nothing from
`tonal_projection`, `host_chroma` or any chroma path. Its only inputs are MIDI
note identity and timing, the General MIDI program family, and attack-envelope
statistics learned from isolated rendered audio.

Attack only. J3I found the release side sound across every family, so the note
still drops to zero at MIDI note-off using the existing rectangular gate.

Pre-registration: docs/mir/receipts/acoustic_activation/J3J_PREREGISTRATION.json
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from .note_register import HOP, N_FFT, SR, Note

K_MAX_HOPS = 32
MIN_EPISODES = 20
WINDOW_HOPS = N_FFT // HOP  # 4 - the analysis window the overlap already spans

# Declared A PRIORI by organology, never by measured attack time.
ATTACK_CLASS_GROUPS = {
    "PLUCKED_STRUCK": ("piano_keys", "chromatic_percussion", "guitar", "bass"),
    "BLOWN_BOWED": ("brass", "reed_pipe", "strings", "ensemble_voice"),
    "SYNTHETIC": ("synth_lead_pad", "synth_effects"),
}
GROUP_OF = {f: g for g, fams in ATTACK_CLASS_GROUPS.items() for f in fams}


def episode_curve(env: NDArray, i0: int, i1: int, peak: float,
                  k_max: int = K_MAX_HOPS) -> NDArray[np.float64] | None:
    """Monotone normalised rise a(tau) for one isolated episode, tau = 0..k_max.

    Running maximum, so vibrato or tremolo dips during the rise are not modelled
    as de-activation. Episodes shorter than k_max hold their last observed value.
    """
    if peak <= 0.0 or i1 <= i0:
        return None
    seg = np.asarray(env[i0:min(i0 + k_max + 1, i1)], dtype=np.float64) / peak
    if seg.size == 0:
        return None
    seg = np.clip(np.maximum.accumulate(seg), 0.0, 1.0)
    out = np.full(k_max + 1, seg[-1], dtype=np.float64)
    out[: seg.size] = seg
    return out


def kernel_from_curves(curves: list[NDArray]) -> NDArray[np.float64] | None:
    """k(tau) = median curve normalised so k(K_MAX) = 1.0 exactly."""
    if not curves:
        return None
    k = np.median(np.vstack(curves), axis=0)
    k = np.maximum.accumulate(np.clip(k, 0.0, 1.0))
    last = float(k[-1])
    if last <= 1e-9:
        return None
    return np.clip(k / last, 0.0, 1.0)


class KernelBank:
    """Cross-fitted attack kernels. A track never supplies its own correction."""

    def __init__(self, episodes: list[dict]):
        # episodes: [{"track": str, "family": str, "curve": (K_MAX+1,)}]
        self.eps = episodes
        self._cache: dict[tuple[str, str], tuple[NDArray, dict]] = {}

    def _pool(self, held_out_track: str, keys: tuple[str, ...], by: str) -> list[dict]:
        return [e for e in self.eps if e["track"] != held_out_track and e[by] in keys]

    def for_stem(self, family: str, held_out_track: str) -> tuple[NDArray, dict]:
        """Declared fallback: exact family -> attack-class group -> global."""
        key = (family, held_out_track)
        if key in self._cache:
            return self._cache[key]
        levels = [("exact_family", self._pool(held_out_track, (family,), "family"))]
        g = GROUP_OF.get(family)
        if g:
            levels.append(("attack_class_group",
                           self._pool(held_out_track, ATTACK_CLASS_GROUPS[g], "family")))
        levels.append(("global", [e for e in self.eps if e["track"] != held_out_track]))
        for name, pool in levels:
            if len(pool) >= MIN_EPISODES:
                k = kernel_from_curves([e["curve"] for e in pool])
                if k is not None:
                    meta = {"level": name, "n_episodes": len(pool),
                            "n_source_tracks": len({e["track"] for e in pool}),
                            "attack_class_group": g}
                    self._cache[key] = (k, meta)
                    return self._cache[key]
        k = np.ones(K_MAX_HOPS + 1, dtype=np.float64)
        self._cache[key] = (k, {"level": "identity_no_correction", "n_episodes": 0,
                                "n_source_tracks": 0, "attack_class_group": g})
        return self._cache[key]


def box_filtered(kernel: NDArray, taps: int = WINDOW_HOPS) -> NDArray[np.float64]:
    """Mean of k over the `taps` hops the analysis window covers.

    The existing state already integrates each note's overlap across that window,
    so the activation weight is smeared identically rather than sampled at one edge.
    """
    k = np.asarray(kernel, dtype=np.float64)
    pad = np.concatenate([np.full(taps - 1, k[0]), k])
    return np.convolve(pad, np.ones(taps) / taps, mode="valid")


def acoustic_activation_state(
    notes: list[Note], n_frames: int, kernel: NDArray,
    *, sr: int = SR, hop: int = HOP, n_fft: int = N_FFT,
) -> dict:
    """ACOUSTIC_ACTIVATION_PC: duration-overlap state with a causal attack ramp.

    Identical to `pitch_class_state` except that each note's contribution during
    its attack is multiplied by the cross-fitted family kernel. Pitch, pitch class,
    note identity, note-off, polyphony and instrumentation are untouched, and
    velocity is still excluded.
    """
    win_s = n_fft / float(sr)
    hop_s = hop / float(sr)
    starts = (np.arange(n_frames, dtype=np.float64) + 1.0) * hop_s - win_s
    ends = (np.arange(n_frames, dtype=np.float64) + 1.0) * hop_s
    kb = box_filtered(kernel)
    kb_last = float(kb[-1])

    mass = np.zeros((n_frames, 12), dtype=np.float64)
    wtot = np.zeros(n_frames, dtype=np.float64)

    for nt in notes:
        if nt.end_s <= nt.start_s:
            continue
        lo = max(int(np.floor((nt.start_s / hop_s) - 1.0)), 0)
        hi = min(int(np.ceil((nt.end_s + win_s) / hop_s)), n_frames)
        if hi <= lo:
            continue
        ov = np.minimum(ends[lo:hi], nt.end_s) - np.maximum(starts[lo:hi], nt.start_s)
        np.clip(ov, 0.0, None, out=ov)
        hit = ov > 0.0
        if not hit.any():
            continue
        idx = np.arange(lo, hi)[hit]
        tau = np.rint((ends[lo:hi][hit] - nt.start_s) / hop_s).astype(np.int64)
        act = np.where(tau < 0, 0.0,
                       np.where(tau > K_MAX_HOPS, kb_last, kb[np.clip(tau, 0, K_MAX_HOPS)]))
        w = ov[hit] * act          # duration overlap x activation - no velocity
        np.add.at(mass, (idx, nt.pitch % 12), w)
        np.add.at(wtot, idx, w)

    return {"pc_mass": mass, "weight_total": wtot, "silent": wtot <= 0.0}
