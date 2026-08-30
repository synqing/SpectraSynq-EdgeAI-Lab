"""Host port of K1 apply_brightness photons curve. Not a new effect.

Firmware: SPECTRASYNQ_K1_FIRMWARE/visual/led_utilities.h apply_brightness()
and system/constants.h PHOTONS_CURVE_MODE.

Shipping curve is mode 0: brightness *= PHOTONS². Bloom does not read PHOTONS;
the compositor does, after the mode. P3-C applies that compositor step on the
host LED bytes so A/B/D are not a no-op.

HOST-ONLY. MECHANISM for gamma/dither/incandescent (those stay on-device).
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

# constants.h — do not invent a nicer curve.
PHOTONS_CURVE_MODE = 0
LED_COUNT = 160


def photons_curve(photons: float | NDArray) -> float | NDArray:
    p = np.clip(np.asarray(photons, dtype=np.float64), 0.0, 2.0)
    if PHOTONS_CURVE_MODE == 0:
        y = p * p
    elif PHOTONS_CURVE_MODE == 1:
        y = p
    else:
        y = np.sqrt(p)
    if np.isscalar(photons) or getattr(photons, "shape", ()) == ():
        return float(np.asarray(y).reshape(-1)[0])
    return y


def apply_photons(leds: NDArray, photons: NDArray) -> NDArray[np.uint8]:
    """Scale (T, 160, 3) uint8 LED frames by the shipping photons curve.

    `photons` is one scalar per frame in the firmware knob range. MASTER_BRIGHTNESS
    and silent_scale are held at 1.0 (boot fade complete, not a silence test).
    """
    arr = np.asarray(leds, dtype=np.uint8)
    if arr.ndim != 3 or arr.shape[1] != LED_COUNT or arr.shape[2] != 3:
        raise ValueError(f"leds must be (T,{LED_COUNT},3), got {arr.shape}")
    p = np.asarray(photons, dtype=np.float64).reshape(-1)
    if p.size != arr.shape[0]:
        raise ValueError("photons length must match frame count")
    curve = np.asarray(photons_curve(p), dtype=np.float64).reshape(-1, 1, 1)
    scaled = np.clip(arr.astype(np.float64) * curve, 0.0, 255.0)
    return np.rint(scaled).astype(np.uint8)
