"""Call the firmware host bloom renderer. Do not modify production firmware.

Uses SpectraSynq_K1_Firmware/scripts/regression-harness/render_replay.py
to compile the real light_mode_bloom.cpp and dump 160 RGB8 frames.

PHOTONS is applied afterwards via k1_photons.apply_photons — bloom itself
does not read the knob; apply_brightness does.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

LED_COUNT = 160
BYTE_COUNT = LED_COUNT * 3


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


def _rr():
    harness = firmware_root() / "scripts" / "regression-harness"
    path = str(harness)
    if path not in sys.path:
        sys.path.insert(0, path)
    import render_replay as render_replay

    return render_replay


def compile_bloom(workdir: Path, compiler: str | None = None) -> tuple[Path, dict]:
    workdir = Path(workdir).resolve()
    workdir.mkdir(parents=True, exist_ok=True)
    rr = _rr()
    ok, binary, meta = rr.build_binary(workdir, mode="bloom", compiler=compiler)
    if not ok:
        err = meta.get("stderr") or ""
        (workdir / "compile.stderr").write_text(err)
        raise RuntimeError("bloom host compile failed:\n" + err[-2500:])
    return Path(binary), meta


def hexes_to_leds(hexes: list[str]) -> NDArray[np.uint8]:
    n = len(hexes)
    out = np.zeros((n, LED_COUNT, 3), dtype=np.uint8)
    for i, h in enumerate(hexes):
        raw = bytes.fromhex(h.strip())
        if len(raw) != BYTE_COUNT:
            raise ValueError(f"frame {i} has {len(raw)} bytes, expected {BYTE_COUNT}")
        out[i] = np.frombuffer(raw, dtype=np.uint8).reshape(LED_COUNT, 3)
    return out


def render_bloom(
    binary: Path,
    *,
    chroma: NDArray,
    times_s: NDArray,
    params: dict | None = None,
) -> NDArray[np.uint8]:
    """Drive bloom with a 12-bin chroma series. Same drive for every P3-C condition."""
    rr = _rr()
    frames = []
    c = np.asarray(chroma, dtype=np.float64)
    t = np.asarray(times_s, dtype=np.float64)
    if c.ndim != 2 or c.shape[1] != 12:
        raise ValueError(f"chroma must be (T,12), got {c.shape}")
    if t.size != c.shape[0]:
        raise ValueError("times and chroma length differ")
    for i in range(c.shape[0]):
        energy = float(c[i].sum())
        frames.append(
            {
                "ms": int(round(float(t[i]) * 1000.0)),
                "chromagram": [float(x) for x in c[i]],
                "silence": energy < 1e-8,
            }
        )
    ok, hexes, meta = rr.replay_frames(binary, frames, params=params or rr.DEFAULT_PARAMS)
    if not ok or len(hexes) != len(frames):
        raise RuntimeError(
            f"bloom replay failed ok={ok} frames={len(hexes)}/{len(frames)} "
            f"stderr={(meta.get('stderr') or '')[:800]}"
        )
    return hexes_to_leds(hexes)
