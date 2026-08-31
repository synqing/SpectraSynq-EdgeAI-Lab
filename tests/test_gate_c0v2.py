"""C0-v2 harness: metadata join, epoch required, lag search cannot hide a race."""

from __future__ import annotations

import re
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from edgeai.mir.gate_c0v2 import (  # noqa: E402
    check_integrity,
    decode_c0_dump,
    hop_join,
    lag_disagreement,
    step_trace,
    timing_selftest,
    u16be_hex,
    verdict,
)
from edgeai.mir.p3c_score import head_position_upper  # noqa: E402


def _pixel_at(pos: int) -> bytes:
    """One bright TRUE16-looking packed dump pixel at upper-half `pos` (0..79)."""
    rgb16 = np.zeros((160, 3), dtype=np.uint16)
    idx = 80 + int(np.clip(pos, 0, 79))
    rgb16[idx] = (40000, 8000, 50000)
    # dump is R16BE G16BE B16BE
    return rgb16.astype(">u2").tobytes()


def _synth_dump(
    samples: np.ndarray,
    *,
    frames_per_hop: int = 3,
    preroll: int = 4,
    postroll: int = 3,
    shift_pixels: int = 0,
    drop_epoch: bool = False,
    mismatch_prsm: bool = False,
    skip_m: bool = False,
) -> str:
    samples = np.asarray(samples, dtype=np.uint16).reshape(-1)
    lines = []
    n_frames = preroll + samples.size * frames_per_hop + postroll
    epoch_frame = preroll
    epoch_us = 1_000_000
    lines.append(
        f"[RTRACE-BEGIN frames={n_frames} every=1 px=160 fmt=rgb16hex bpp=16 "
        f"crc32=00000000 c0=1 epoch_id=7 hop_us=32000 cond=3 n_sem={samples.size} "
        f"pipeline_lat=0]"
    )
    if drop_epoch:
        lines.append("[C0_EPOCH missing]")
    else:
        lines.append(
            f"[C0_EPOCH frame={epoch_frame} device_us={epoch_us} semantic_idx=0 "
            f"cond=3 epoch_id=7 tick={epoch_frame + 1}]"
        )
    f = 0
    us = epoch_us - preroll * 10000
    for _ in range(preroll):
        pos = int(round(samples[0] / 65535.0 * 79))
        hx = _pixel_at(pos).hex()
        lines.append(f"F,{f},{1000 + f},18,{hx}")
        if not skip_m:
            lines.append(
                f"M,{f},{f + 1},{us},7,65535,3,65535,{int(samples[0])},0,0"
            )
        f += 1
        us += 10000
    for sem, val in enumerate(samples):
        src_sem = sem - shift_pixels
        src_val = samples[src_sem] if 0 <= src_sem < samples.size else samples[0]
        for k in range(frames_per_hop):
            pos = int(round(int(src_val) / 65535.0 * 79))
            hx = _pixel_at(pos).hex()
            marker = 1 if (sem == 0 and k == 0) else 0
            prsm = int(val) + (99 if mismatch_prsm and k == 0 else 0)
            lines.append(f"F,{f},{1000 + f},18,{hx}")
            if not skip_m:
                lines.append(
                    f"M,{f},{f + 1},{us},7,{f - epoch_frame},3,{sem},{prsm},1,{marker}"
                )
            f += 1
            us += 10000
    last = int(samples[-1])
    for _ in range(postroll):
        pos = int(round(last / 65535.0 * 79))
        hx = _pixel_at(pos).hex()
        lines.append(f"F,{f},{1000 + f},18,{hx}")
        if not skip_m:
            lines.append(
                f"M,{f},{f + 1},{us},7,{f - epoch_frame},3,{samples.size - 1},{last},0,0"
            )
        f += 1
        us += 10000
    lines.append("[RTRACE-END]")
    return "\n".join(lines) + "\n"


def _decode_independent(text: str) -> dict:
    """Second implementation: split on commas, no shared regex module."""
    f_rows = []
    m_rows = []
    epoch = None
    for line in text.splitlines():
        if line.startswith("[C0_EPOCH "):
            body = line[len("[C0_EPOCH ") :].rstrip("]")
            kv = {}
            for part in body.split():
                if "=" in part:
                    k, v = part.split("=", 1)
                    kv[k] = int(v)
            epoch = kv
        elif line.startswith("F,"):
            bits = line.split(",", 4)
            f_rows.append((int(bits[1]), bits[4].strip()))
        elif line.startswith("M,"):
            bits = line.strip().split(",")
            m_rows.append(tuple(int(x) for x in bits[1:]))
    return {"epoch": epoch, "n_f": len(f_rows), "n_m": len(m_rows), "f0": f_rows[0][0] if f_rows else None}


def test_u16be_hex_roundtrip():
    samples, _ = step_trace(n_seg=2)
    hx = u16be_hex(samples)
    got = np.array([int(hx[i : i + 4], 16) for i in range(0, len(hx), 4)], dtype=np.uint16)
    assert np.array_equal(got, samples)


def test_good_dump_integrity_and_independent_decoder():
    samples, changes = step_trace(n_seg=4)
    text = _synth_dump(samples)
    dump = decode_c0_dump(text)
    alt = _decode_independent(text)
    assert alt["n_f"] == dump.leds.shape[0]
    assert alt["n_m"] == dump.leds.shape[0]
    assert alt["epoch"]["frame"] == dump.epoch["frame"]
    integ = check_integrity(dump, samples)
    assert integ.ok, integ.reasons
    hops, gain, present = hop_join(dump, samples.size)
    assert int(present.sum()) == samples.size
    pos = head_position_upper(hops)
    assert np.isfinite(pos).all()
    result = timing_selftest(dump, samples, expected_change_at=changes)
    assert result["status"] == "PASS", result
    assert result["lag"]["best_lag_hops"] == 0 or not result["lag"]["invalid"]


def test_missing_epoch_is_invalid():
    samples, _ = step_trace(n_seg=4)
    text = _synth_dump(samples, drop_epoch=True)
    dump = decode_c0_dump(text)
    integ = check_integrity(dump, samples)
    assert not integ.ok
    assert "epoch_marker_absent" in integ.reasons
    assert verdict(False, "PASS", "PASS", "PASS", False) == "INVALID_RUN"


def test_applied_mismatch_is_invalid():
    samples, _ = step_trace(n_seg=4)
    text = _synth_dump(samples, mismatch_prsm=True)
    dump = decode_c0_dump(text)
    integ = check_integrity(dump, samples)
    assert not integ.ok
    assert "applied_prsm_mismatch" in integ.reasons


def test_no_m_lines_is_invalid():
    samples, _ = step_trace(n_seg=4)
    text = _synth_dump(samples, skip_m=True)
    dump = decode_c0_dump(text)
    integ = check_integrity(dump, samples)
    assert not integ.ok


def test_plus_14_hop_pixel_shift_is_rejected_not_rescored():
    """The previous C0 class of failure: pixels lag the declared input.

    Metadata still claims the unshifted semantic index. The lag detector must
    mark INVALID. The scorer must not silently adopt +14.
    """
    samples, changes = step_trace(n_seg=16)
    text = _synth_dump(samples, shift_pixels=14)
    dump = decode_c0_dump(text)
    integ = check_integrity(dump, samples)
    assert integ.ok, integ.reasons  # metadata still honest
    hops, gain, _ = hop_join(dump, samples.size)
    pos = head_position_upper(hops)
    lag = lag_disagreement(pos, gain)
    assert lag["invalid"] is True
    assert abs(int(lag["best_lag_hops"])) >= 3
    result = timing_selftest(dump, samples, expected_change_at=changes)
    assert result["status"] == "INVALID_RUN"
    assert "lag_detector_disagrees_with_declared_timing" in result["reasons"]
    # Must not look like a PASS of the binding just because a shift exists.
    assert verdict(True, "PASS", "PASS", "PASS", True) == "INVALID_RUN"


def test_verdict_splits_binding_fail_from_invalid():
    assert verdict(True, "FAIL", "PASS", "PASS", False) == "BINDING_FAIL"
    assert verdict(True, "PASS", "PASS", "PASS", False) == "PASS"
    assert verdict(False, "FAIL", "FAIL", "FAIL", False) == "INVALID_RUN"


def test_retired_c0_runner_refuses():
    src = (ROOT / "scripts" / "gate_c0_silicon.py").read_text(encoding="utf-8")
    assert "RETIRED" in src
    assert "gate_c0v2" in src


def test_same_song_loop_max_is_fifteen_minutes():
    sys.path.insert(0, str(ROOT / "scripts"))
    from gate_c0v2_silicon import SAME_SONG_LOOP_MAX_S

    assert SAME_SONG_LOOP_MAX_S == 15 * 60
