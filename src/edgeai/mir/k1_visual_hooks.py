"""Host port of k1_visual_hooks.cpp onset→PHOTONS accent.

This is the existing structural-accent mechanism. P3-C2 fires the SAME pulse
from either |Δ mix| or composition_change. Strength, tau, and ceiling stay frozen.

Firmware: SPECTRASYNQ_K1_FIRMWARE/director/k1_visual_hooks.cpp
HOST-ONLY. Do not edit production firmware from this lab.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HookConfig:
    enabled: bool = True
    event_window_ms: int = 80
    onset_tau_ms: int = 100
    bass_tau_ms: int = 180
    beat_tau_ms: int = 250
    onset_to_photons: float = 0.16
    bass_to_edge: float = 0.20
    beat_to_chroma: float = 0.12
    scalar_ceiling: float = 2.0


DEFAULT_HOOK_CONFIG = HookConfig()


@dataclass
class HookOutput:
    photon_scalar: float
    chroma_scalar: float
    edge_scalar: float
    confirm_switch_boundary: bool


def _clamp(value: float, low: float, high: float) -> float:
    if value != value:  # NaN
        return low
    if value < low:
        return low
    if value > high:
        return high
    return value


class VisualHooks:
    def __init__(self, config: HookConfig = DEFAULT_HOOK_CONFIG) -> None:
        self.config = config
        self._last_ms = 0
        self._onset_pulse = 0.0
        self._bass_pulse = 0.0
        self._beat_pulse = 0.0
        self._last_onset_id = 0
        self._last_bass_id = 0
        self._last_beat_id = 0

    def reset(self) -> None:
        self._last_ms = 0
        self._onset_pulse = 0.0
        self._bass_pulse = 0.0
        self._beat_pulse = 0.0
        self._last_onset_id = 0
        self._last_bass_id = 0
        self._last_beat_id = 0

    def _decay(self, pulse: float, dt_ms: int, tau_ms: int) -> float:
        safe_tau = 1 if tau_ms == 0 else tau_ms
        decay = _clamp(float(dt_ms) / float(safe_tau), 0.0, 1.0)
        pulse *= 1.0 - decay
        if pulse < 0.0001:
            return 0.0
        return pulse

    def tick(
        self,
        *,
        now_ms: int,
        onset: bool,
        onset_strength: float,
        event_id: int,
        event_age_ms: int,
        bass_onset: bool = False,
        bass_onset_strength: float = 0.0,
        beat: bool = False,
        beat_confidence: float = 0.0,
    ) -> HookOutput:
        cfg = self.config
        output = HookOutput(
            photon_scalar=1.0,
            chroma_scalar=1.0,
            edge_scalar=1.0,
            confirm_switch_boundary=False,
        )
        dt_ms = 0 if self._last_ms == 0 or now_ms < self._last_ms else now_ms - self._last_ms
        self._last_ms = now_ms
        self._onset_pulse = self._decay(self._onset_pulse, dt_ms, cfg.onset_tau_ms)
        self._bass_pulse = self._decay(self._bass_pulse, dt_ms, cfg.bass_tau_ms)
        self._beat_pulse = self._decay(self._beat_pulse, dt_ms, cfg.beat_tau_ms)

        if not cfg.enabled:
            return output

        eligible = event_id != 0 and event_age_ms <= cfg.event_window_ms
        if eligible and onset and event_id != self._last_onset_id:
            strength = _clamp(float(onset_strength), 0.0, 1.0)
            if strength > self._onset_pulse:
                self._onset_pulse = strength
            self._last_onset_id = event_id
        if eligible and bass_onset and event_id != self._last_bass_id:
            strength = _clamp(float(bass_onset_strength), 0.0, 1.0)
            if strength > self._bass_pulse:
                self._bass_pulse = strength
            self._last_bass_id = event_id
        if eligible and beat and event_id != self._last_beat_id:
            strength = _clamp(float(beat_confidence), 0.0, 1.0)
            if strength > self._beat_pulse:
                self._beat_pulse = strength
            self._last_beat_id = event_id
            output.confirm_switch_boundary = True

        output.photon_scalar = _clamp(1.0 + (self._onset_pulse * cfg.onset_to_photons), 1.0, cfg.scalar_ceiling)
        output.chroma_scalar = _clamp(1.0 + (self._beat_pulse * cfg.beat_to_chroma), 1.0, cfg.scalar_ceiling)
        output.edge_scalar = _clamp(1.0 + (self._bass_pulse * cfg.bass_to_edge), 1.0, cfg.scalar_ceiling)
        return output

    def apply_photons_knob(self, photons: float, scalar: float) -> float:
        return _clamp(float(photons) * float(scalar), 0.0, 2.0)
