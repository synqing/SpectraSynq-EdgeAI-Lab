"""Call the firmware host renderer. Do not modify production firmware.

Palette mode is the product colour path. Chromatic HSV is not.

Waveform Tempo is a HOST-ONLY registry entry. The firmware harness parks
bloom/river/comet and does not list mode 18. This module injects the mode
plus tempo/snapshot stubs into the generated harness TU. Shipping effect
TUs and Palettes.cpp are not edited.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Parked modes (spectrum_river, comet, waveform_tempo, …) are compiled only
# when this is set before render_replay is imported.
os.environ.setdefault("K1_RENDER_REPLAY_ALL_MODES", "1")

import numpy as np
from numpy.typing import NDArray

LED_COUNT = 160
BYTE_COUNT = LED_COUNT * 3
NUM_FREQS = 80
# Palettes.h playlist: 43 = K1_Ultraviolet_Bright (product palette, not chroma HSV).
PALETTE_INDEX_K1_ULTRAVIOLET_BRIGHT = 43
PALETTE_RENDER_PARAMS = {
    "mood": 0.65,
    "saturation": 1.0,
    "square_iter": 0.0,  # square_iter crushes host linear dumps to black
    "chroma": 1.0,
    "palette_mode": True,
    "palette_index": PALETTE_INDEX_K1_ULTRAVIOLET_BRIGHT,
    "chromatic_mode": False,
    "auto_color_shift": True,
}

# HOST-ONLY. Matches firmware dispatch for LIGHT_MODE_WAVEFORM_TEMPO:
# memcpy history → light_mode_waveform_tempo(effect_state_primary) → memcpy back.
# Tempo/snapshot are not in the harness stdin schema; the frame_apply stub
# synthesises a locked 120 BPM phase from frame ms so A/B/D share one clock.
WAVEFORM_TEMPO_MODE = {
    "sources": ["effects/light_mode_waveform_tempo.cpp"],
    "fixture_keys": ["chromagram", "waveform_peak_scaled"],
    "decls": r"""
#include "k1_tempo.h"
#include "k1_audio_snapshot.h"
static K1TempoEvent g_host_tempo_event = {};
static K1AudioSnapshot g_host_audio_snapshot = {};
K1TempoEvent k1_tempo_read() { return g_host_tempo_event; }
K1AudioSnapshot k1_audio_snapshot_read() { return g_host_audio_snapshot; }
static CRGB16 g_leds_prev[NATIVE_RESOLUTION];
static void mode_reset() {
  std::memset(g_leds_prev, 0, sizeof(g_leds_prev));
  std::memset(&effect_state_primary, 0, sizeof(effect_state_primary));
  effect_state_primary.vu_dot_max_level = SQ15x16(0.01);
  std::memset(&g_host_tempo_event, 0, sizeof(g_host_tempo_event));
  std::memset(&g_host_audio_snapshot, 0, sizeof(g_host_audio_snapshot));
}
""",
    "frame_apply": r"""
    for (int i = 0; i < 12; i++) chromagram_smooth[i] = SQ15x16(fr.chroma[i]);
    waveform_peak_scaled = fr.waveform_peak_scaled;
    max_waveform_val_raw = fr.max_waveform_val_raw;
    g_host_audio_snapshot = K1AudioSnapshot{};
    g_host_audio_snapshot.frame_ms = fr.ms;
    g_host_audio_snapshot.peak_scaled = fr.waveform_peak_scaled;
    g_host_audio_snapshot.vu_level = fr.waveform_peak_scaled;
    g_host_audio_snapshot.novelty = 0.45f;
    g_host_audio_snapshot.spectral_energy = 0.50f;
    g_host_audio_snapshot.low_energy = 0.45f;
    g_host_audio_snapshot.mid_energy = 0.45f;
    g_host_audio_snapshot.high_energy = 0.45f;
    g_host_audio_snapshot.chroma_strength = 0.50f;
    g_host_audio_snapshot.silence = (fr.silence != 0) && (fr.waveform_peak_scaled < 0.02f);
    g_host_tempo_event = K1TempoEvent{};
    g_host_tempo_event.bpm = 120.0f;
    {
      float beats = (float)fr.ms * 0.002f;
      int whole = (int)beats;
      float ph = beats - (float)whole;
      if (ph < 0.0f) ph += 1.0f;
      g_host_tempo_event.phase01 = ph;
    }
    g_host_tempo_event.confidence = 1.0f;
    g_host_tempo_event.locked = true;
    g_host_tempo_event.beat_tick = g_host_tempo_event.phase01 < 0.06f;
    g_host_tempo_event.beat_strength = 1.0f;
""",
    "entry": r"""
    std::memcpy(leds_16, g_leds_prev, sizeof(CRGB16) * NATIVE_RESOLUTION);
    light_mode_waveform_tempo(effect_state_primary);
    std::memcpy(g_leds_prev, leds_16, sizeof(CRGB16) * NATIVE_RESOLUTION);
""",
}


def firmware_root() -> Path:
    env = os.environ.get("SPECTRASYNQ_K1_FIRMWARE")
    if env:
        p = Path(env)
        if (p / "scripts" / "regression-harness" / "render_replay.py").is_file():
            return p
        raise FileNotFoundError(f"SPECTRASYNQ_K1_FIRMWARE={env} has no render_replay.py")
    here = Path("/Users/spectrasynq/SpectraSynq_K1_Firmware")
    if (here / "scripts" / "regression-harness" / "render_replay.py").is_file():
        return here
    raise FileNotFoundError(
        "K1 firmware render_replay.py not found. Set SPECTRASYNQ_K1_FIRMWARE."
    )


def firmware_sha(root: Path | None = None) -> str:
    import subprocess

    r = root or firmware_root()
    p = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=r,
        text=True,
        capture_output=True,
        check=False,
    )
    return (p.stdout or "").strip() or "UNKNOWN"


def _register_waveform_tempo(rr) -> None:
    """Inject Waveform Tempo into the host harness without editing firmware git."""
    spec = WAVEFORM_TEMPO_MODE
    rr.ALL_MODES["waveform_tempo"] = spec
    rr.MODES["waveform_tempo"] = spec


def _rr():
    harness = firmware_root() / "scripts" / "regression-harness"
    path = str(harness)
    if path not in sys.path:
        sys.path.insert(0, path)
    import render_replay as render_replay

    _register_waveform_tempo(render_replay)
    return render_replay


def compile_mode(workdir: Path, mode: str = "bloom", compiler: str | None = None) -> tuple[Path, dict]:
    workdir = Path(workdir).resolve()
    workdir.mkdir(parents=True, exist_ok=True)
    rr = _rr()
    if mode not in rr.MODES:
        raise RuntimeError(f"mode {mode!r} not in host registry {sorted(rr.MODES)}")
    ok, binary, meta = rr.build_binary(workdir, mode=mode, compiler=compiler)
    if not ok:
        err = meta.get("stderr") or ""
        (workdir / "compile.stderr").write_text(err)
        raise RuntimeError(f"{mode} host compile failed:\n" + err[-2500:])
    return Path(binary), meta


def compile_bloom(workdir: Path, compiler: str | None = None) -> tuple[Path, dict]:
    return compile_mode(workdir, mode="bloom", compiler=compiler)


def hexes_to_leds(hexes: list[str]) -> NDArray[np.uint8]:
    n = len(hexes)
    out = np.zeros((n, LED_COUNT, 3), dtype=np.uint8)
    for i, h in enumerate(hexes):
        raw = bytes.fromhex(h.strip())
        if len(raw) != BYTE_COUNT:
            raise ValueError(f"frame {i} has {len(raw)} bytes, expected {BYTE_COUNT}")
        out[i] = np.frombuffer(raw, dtype=np.uint8).reshape(LED_COUNT, 3)
    return out


def render_mode(
    binary: Path,
    *,
    times_s: NDArray,
    chroma: NDArray | None = None,
    spectro: NDArray | None = None,
    bass_onset: NDArray | None = None,
    bass_strength: NDArray | None = None,
    waveform_peak: NDArray | None = None,
    params: dict | None = None,
) -> NDArray[np.uint8]:
    """Drive a compiled host mode. Default params are the product palette path."""
    rr = _rr()
    t = np.asarray(times_s, dtype=np.float64).reshape(-1)
    n = int(t.size)
    if chroma is None:
        c = np.zeros((n, 12), dtype=np.float64)
    else:
        c = np.asarray(chroma, dtype=np.float64)
        if c.shape != (n, 12):
            raise ValueError(f"chroma must be ({n},12), got {c.shape}")
    if spectro is None:
        s = np.zeros((n, NUM_FREQS), dtype=np.float64)
    else:
        s = np.asarray(spectro, dtype=np.float64)
        if s.shape != (n, NUM_FREQS):
            raise ValueError(f"spectro must be ({n},{NUM_FREQS}), got {s.shape}")
    onset = np.zeros(n, dtype=np.int32) if bass_onset is None else np.asarray(bass_onset).astype(np.int32).reshape(-1)
    strength = (
        np.zeros(n, dtype=np.float64)
        if bass_strength is None
        else np.asarray(bass_strength, dtype=np.float64).reshape(-1)
    )
    wf = (
        np.zeros(n, dtype=np.float64)
        if waveform_peak is None
        else np.asarray(waveform_peak, dtype=np.float64).reshape(-1)
    )
    if onset.size != n or strength.size != n or wf.size != n:
        raise ValueError("onset/strength/waveform length must match times")
    frames = []
    for i in range(n):
        frames.append(
            {
                "ms": int(round(float(t[i]) * 1000.0)),
                "chromagram": [float(x) for x in c[i]],
                "spectrogram": [float(x) for x in s[i]],
                "waveform_peak_scaled": float(wf[i]),
                "max_waveform_val_raw": max(0.35, float(wf[i]) * 2.0),
                "bass_onset": int(onset[i]),
                "bass_onset_strength": float(strength[i]),
                "silence": float(c[i].sum() + s[i].sum()) < 1e-8,
            }
        )
    p = dict(PALETTE_RENDER_PARAMS)
    if params:
        p.update(params)
    ok, hexes, meta = rr.replay_frames(binary, frames, params=p)
    if not ok or len(hexes) != len(frames):
        raise RuntimeError(
            f"replay failed ok={ok} frames={len(hexes)}/{len(frames)} "
            f"stderr={(meta.get('stderr') or '')[:800]}"
        )
    return hexes_to_leds(hexes)


def render_bloom(
    binary: Path,
    *,
    chroma: NDArray,
    times_s: NDArray,
    params: dict | None = None,
) -> NDArray[np.uint8]:
    return render_mode(binary, chroma=chroma, times_s=times_s, params=params)
