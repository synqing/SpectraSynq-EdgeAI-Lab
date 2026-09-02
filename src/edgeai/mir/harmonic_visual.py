"""J3E - HOST_ORACLE_VISUAL_FEASIBILITY sandbox for the HARMONIC COLOUR TRANSITION verb.

NOT a production effect. NOT a compatibility row. NOT Gate B or Gate C. NOT firmware.

The verb is: `tonal state changes -> colour state transitions`. Harmonic movement
controls ONLY the transition rate between successive tonal colour states; it never
touches brightness and never spawns anything. Photons are held fixed so luminance
carries no information and the metric cannot degenerate into a brightness test.

State -> colour reuses the documented firmware bloom chromagram semantics (pitch-class
bin b -> hue b/12, weighted by the SQUARED chromagram drive) rather than inventing a
colour theory.
"""

from __future__ import annotations

import colorsys

import numpy as np
from numpy.typing import NDArray

from .host_chroma import bloom_chromagram, preview_encode
from .k1_photons import LED_COUNT, apply_photons

A_MIN = 0.02
A_MAX = 0.60
M_REF = 0.35
SATURATION = 1.0
VALUE = 1.0
EXPOSURE = 2.2

# 12 pitch-class hues, frozen. hue = b/12 on the wheel.
BIN_RGB = np.array(
    [colorsys.hsv_to_rgb(b / 12.0, SATURATION, VALUE) for b in range(12)],
    dtype=np.float64,
)


def bin_weights(state_l1: NDArray, *, with_floor: bool) -> NDArray[np.float64]:
    """Squared chromagram drive per bin - the firmware bin^2 path.

    with_floor reproduces bloom_chromagram's [0.65, 1.0] compression, which exists
    so a sparse one-hot does not render black in the bloom ENGINE. It is a
    brightness accommodation, not a colour-mix rule, so the primary variant omits it.
    """
    s = np.asarray(state_l1, dtype=np.float64)
    if with_floor:
        drive = np.asarray(bloom_chromagram(s.astype(np.float32), np.ones(len(s))), dtype=np.float64)
    else:
        peak = s.max(axis=1, keepdims=True)
        drive = np.divide(s, peak, out=np.zeros_like(s), where=peak > 1e-9)
    return drive**2


def target_colour(state_l1: NDArray, *, with_floor: bool) -> NDArray[np.float64]:
    """(T,3) linear RGB in [0,1]: the weight-normalised mix of the 12 bin hues."""
    w = bin_weights(state_l1, with_floor=with_floor)
    tot = w.sum(axis=1, keepdims=True)
    mix = np.divide(w @ BIN_RGB, tot, out=np.zeros((len(w), 3)), where=tot > 1e-12)
    return np.clip(mix, 0.0, 1.0)


def transition(target: NDArray, movement: NDArray) -> NDArray[np.float64]:
    """Exponential smoother whose rate is set by harmonic movement, nothing else.

    alpha = A_MIN + (A_MAX - A_MIN) * clip(M / M_REF, 0, 1)
    """
    tg = np.asarray(target, dtype=np.float64)
    m = np.nan_to_num(np.asarray(movement, dtype=np.float64).reshape(-1), nan=0.0)
    alpha = A_MIN + (A_MAX - A_MIN) * np.clip(m / M_REF, 0.0, 1.0)
    out = np.empty_like(tg)
    cur = tg[0].copy()
    for i in range(len(tg)):
        a = alpha[i]
        cur = (1.0 - a) * cur + a * tg[i]
        out[i] = cur
    return out


def render_strip(colour: NDArray) -> NDArray[np.uint8]:
    """(T,160,3) uint8. Uniform strip - no new spatial verb is invented here."""
    c = np.clip(np.asarray(colour, dtype=np.float64), 0.0, 1.0)
    leds = np.rint(c[:, None, :] * 255.0).astype(np.uint8)
    leds = np.repeat(leds, LED_COUNT, axis=1)
    return apply_photons(leds, np.ones(len(leds)))  # photons fixed at 1.0


def srgb_to_lab(rgb_u8: NDArray) -> NDArray[np.float64]:
    """sRGB uint8 -> CIELAB (D65). Implemented here to avoid a new dependency."""
    c = np.asarray(rgb_u8, dtype=np.float64) / 255.0
    lin = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    m = np.array([[0.4124564, 0.3575761, 0.1804375],
                  [0.2126729, 0.7151522, 0.0721750],
                  [0.0193339, 0.1191920, 0.9503041]])
    xyz = lin @ m.T
    white = np.array([0.95047, 1.0, 1.08883])
    t = xyz / white
    d = 6.0 / 29.0
    f = np.where(t > d**3, np.cbrt(t), t / (3 * d**2) + 4.0 / 29.0)
    return np.stack([116 * f[..., 1] - 16,
                     500 * (f[..., 0] - f[..., 1]),
                     200 * (f[..., 1] - f[..., 2])], axis=-1)


def frame_delta_e(colour: NDArray) -> NDArray[np.float64]:
    """CIELAB Delta-E between consecutive rendered frames. NaN on the first frame."""
    leds = render_strip(colour)
    shown = preview_encode(leds[:, :1, :], exposure=EXPOSURE)[:, 0, :]
    lab = srgb_to_lab(shown)
    out = np.full(len(lab), np.nan)
    out[1:] = np.linalg.norm(lab[1:] - lab[:-1], axis=1)
    return out


def pipeline(state_l1: NDArray, movement: NDArray, *, with_floor: bool) -> dict:
    tg = target_colour(state_l1, with_floor=with_floor)
    col = transition(tg, movement)
    return {"target": tg, "colour": col, "delta_e": frame_delta_e(col)}
