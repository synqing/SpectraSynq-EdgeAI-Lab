#!/usr/bin/env python3
"""Gate C0 silicon inject + rtrace dump + P3-C head-position score.

Named GO: K1-C0-RTRACE-FLASH-GO. Main RPL only. Perfect oracle, not the student.
Captain is not the LED validator.
"""

from __future__ import annotations

import argparse
import json
import re
import struct
import sys
import time
from pathlib import Path

import numpy as np
import serial
from serial.tools import list_ports

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from edgeai.mir.host_chroma import extra_gain  # noqa: E402
from edgeai.mir.p3c_quant import (  # noqa: E402
    HOP_S,
    cache_path,
    score_clip,
    slice_oracle,
    summarise,
)
from edgeai.mir.p3c_score import head_position_upper  # noqa: E402
from edgeai.mir.visual_hook import apply_frozen_map  # noqa: E402

BINDING = "source_share × WaveformTempo × head_position"
NATIVE_HZ = 16_000.0 / 512.0
WARMUP_S = 1.0
DELTA_FLOOR = 0.15
NATIVE_KEEP_FRACTION = 0.70


def delay_hops(delay_s: float, hop_s: float = HOP_S) -> int:
    if delay_s <= 0.0:
        return 0
    return int(round(float(delay_s) / float(hop_s)))


def actual_delay_s(delay_s: float, hop_s: float = HOP_S) -> float:
    return float(delay_hops(delay_s, hop_s)) * float(hop_s)


def apply_cadence(x: np.ndarray, *, hop_s: float, rate_hz: float, delay_s: float) -> np.ndarray:
    """Zero-order hold then causal delay. Same law as gate_c_cadence (no torch)."""
    x = np.asarray(x, dtype=np.float64).reshape(-1)
    n = int(x.size)
    rate = float(rate_hz)
    hop = float(hop_s)
    t = np.arange(n, dtype=np.float64) * hop
    tick = np.floor(t * rate + 1e-12)
    t_emit = tick / rate
    src = np.rint(t_emit / hop).astype(np.int64)
    src = np.clip(src, 0, n - 1)
    src = np.minimum(src, np.arange(n, dtype=np.int64))
    held = x[src]
    d = delay_hops(delay_s, hop)
    if d <= 0:
        return held
    y = np.empty_like(held)
    y[: min(d, held.size)] = held[0] if held.size else 0.0
    if d < held.size:
        y[d:] = held[:-d]
    return y


def cell_passes(median_delta: float, native_median: float) -> bool:
    if median_delta != median_delta or native_median != native_median:
        return False
    return float(median_delta) >= DELTA_FLOOR and float(median_delta) >= NATIVE_KEEP_FRACTION * float(
        native_median
    )

EXPECT_CHIP = "9087A500"
EXPECT_USB = "B4:3A:45:A5:87:90"
MODE_ORDINAL = 18  # LIGHT_MODE_WAVEFORM_TEMPO
PALETTE_INDEX = 43  # K1_Ultraviolet_Bright
MOOD = 0.65
PACKET_HZ = 62
PRSM_HZ_FIELD = 62
WARMUP_S_RUN = float(WARMUP_S)
SEGMENT_S = 8.0
RTRACE_EVERY = 4
GAIN_LO = 0.62
BEGIN_RE = re.compile(r"^\[RTRACE-BEGIN\b(?P<body>[^\]]*)\]\s*$")
F_RE = re.compile(r"^F,(?P<idx>\d+),(?P<ms>\d+),(?P<mode>\d+),(?P<hex>[0-9a-fA-F]+)\s*$")
END_MARK = "[RTRACE-END]"


def find_port(prefer: str | None = None) -> str:
    ports = list(list_ports.comports())
    for p in ports:
        ser = (p.serial_number or "").upper()
        if ser.replace(":", "") == EXPECT_USB.replace(":", ""):
            return p.device
    if prefer and Path(prefer).exists():
        return prefer
    raise SystemExit(
        f"Main RPL USB {EXPECT_USB} not found. saw="
        + ",".join(f"{p.device}:{p.serial_number}" for p in ports)
    )


def prsm(hz: int, seq: int, t_us: int, prim8: list[int]) -> bytes:
    buf = bytearray(34)
    buf[0:4] = b"PRSM"
    buf[4] = 1
    buf[5] = hz & 0xFF
    struct.pack_into("<I", buf, 6, seq & 0xFFFFFFFF)
    struct.pack_into("<Q", buf, 10, t_us & 0xFFFFFFFFFFFFFFFF)
    off = 18
    for i in range(8):
        struct.pack_into("<H", buf, off, int(prim8[i]) & 0xFFFF)
        off += 2
    return bytes(buf)


def open_ser(port: str) -> serial.Serial:
    s = serial.Serial()
    s.port = port
    s.baudrate = 115200
    s.timeout = 0.2
    s.write_timeout = 1.0
    s.dtr = True
    s.rts = False
    s.open()
    time.sleep(0.35)
    s.reset_input_buffer()
    return s


def read_for(ser: serial.Serial, seconds: float) -> str:
    end = time.time() + seconds
    buf = bytearray()
    while time.time() < end:
        chunk = ser.read(8192)
        if chunk:
            buf.extend(chunk)
    return buf.decode("utf-8", "replace")


def cmd(ser: serial.Serial, line: str, wait: float = 0.45) -> str:
    if not line.startswith(":"):
        raise ValueError(line)
    ser.reset_input_buffer()
    ser.write((line.strip() + "\n").encode("ascii"))
    ser.flush()
    return read_for(ser, wait)


def identity_text(ser: serial.Serial) -> str:
    return cmd(ser, ":dump", 1.2) + cmd(ser, ":build", 0.8)


def parse_identity(text: str) -> dict[str, str]:
    out = {"chip": "", "git": "", "env": "", "epoch": ""}
    for line in text.splitlines():
        if "CHIP ID:" in line:
            out["chip"] = line.split(":", 1)[-1].strip()
        if line.strip().startswith("BUILD:") or "BUILD:" in line:
            for part in line.replace(",", " ").split():
                if part.startswith("git="):
                    out["git"] = part.split("=", 1)[1]
                if part.startswith("env="):
                    out["env"] = part.split("=", 1)[1]
                if part.startswith("epoch="):
                    out["epoch"] = part.split("=", 1)[1]
        if "IDENTITY OK:" in line:
            for part in line.split():
                if part.startswith("git="):
                    out["git"] = part.split("=", 1)[1]
                if part.startswith("env="):
                    out["env"] = part.split("=", 1)[1]
                if part.startswith("epoch="):
                    out["epoch"] = part.split("=", 1)[1]
    return out


def require_identity(text: str, *, expect_env: str | None = None) -> dict[str, str]:
    ident = parse_identity(text)
    if ident["chip"] and ident["chip"] != EXPECT_CHIP:
        raise SystemExit(f"chip mismatch {ident['chip']} != {EXPECT_CHIP}")
    if expect_env and ident["env"] and ident["env"] != expect_env:
        raise SystemExit(f"env mismatch {ident['env']} != {expect_env}")
    if expect_env and not ident["env"]:
        raise SystemExit(f"no BUILD env in identity text (expected {expect_env})")
    return ident


def pin_waveform_tempo(ser: serial.Serial) -> dict[str, str]:
    """set_mode is dense-index. Hunt until persisted ordinal is 18."""
    cmd(ser, ":ap_stream=off", 0.25)
    cmd(ser, ":smart_assist=off", 0.25)
    cmd(ser, ":smart_switching=off", 0.25)
    cmd(ser, ":palette_mode=on", 0.25)
    cmd(ser, f":palette_index={PALETTE_INDEX}", 0.35)
    cmd(ser, f":mood={MOOD}", 0.25)
    found = ""
    dense = None
    # Dense 17 is Waveform Tempo on this registry; still hunt if the map drifts.
    for i in [17, *range(0, 17), *range(18, 36)]:
        text = cmd(ser, f":set_mode={i}", 0.55)
        hit = bool(re.search(rf"CONFIG\.LIGHTSHOW_MODE:\s*{MODE_ORDINAL}\b", text))
        if not hit and "WAVEFORM TEMPO" in text.upper():
            hit = True
        if hit:
            dense = i
            found = text
            break
    if dense is None:
        raise SystemExit("failed to pin Waveform Tempo (ordinal 18)\n" + found[-2000:])
    verify = cmd(ser, f":set_mode={dense}", 0.6)
    blob = found + verify + cmd(ser, ":dump", 1.0)
    if "WAVEFORM TEMPO" not in blob.upper() and not re.search(
        rf"LIGHTSHOW_MODE:\s*{MODE_ORDINAL}\b", blob
    ):
        raise SystemExit("failed to confirm Waveform Tempo pin\n" + blob[-2000:])
    return {"dense_index": str(dense), "pin_echo": blob[-1500:]}


def prim8_from_gain(gain: float) -> list[int]:
    g = float(np.clip(gain, GAIN_LO, 1.0))
    pressure = int(round(g * 65535.0))
    # Non-zero mass so the all-zero silence latch cannot fire.
    return [pressure, 0, 8192, 0, 0, 0, 0, 0]


def stream_gains(ser: serial.Serial, gains: np.ndarray, *, seq0: int) -> dict[str, float]:
    """ZOH extra_gain on the hop grid; repeat PRSM at PACKET_HZ. hz field stays ≥30."""
    gains = np.asarray(gains, dtype=np.float64).reshape(-1)
    n = int(gains.size)
    packet_dt = 1.0 / float(PACKET_HZ)
    total_s = n * HOP_S
    t0 = time.perf_counter()
    seq = int(seq0)
    sent = 0
    next_t = t0
    while True:
        elapsed = time.perf_counter() - t0
        if elapsed >= total_s:
            break
        hop = min(n - 1, int(elapsed / HOP_S))
        pkt = prsm(PRSM_HZ_FIELD, seq, int(elapsed * 1e6), prim8_from_gain(float(gains[hop])))
        ser.write(pkt)
        seq += 1
        sent += 1
        next_t += packet_dt
        sleep = next_t - time.perf_counter()
        if sleep > 0:
            time.sleep(sleep)
    ser.flush()
    return {"sent": float(sent), "duration_s": time.perf_counter() - t0, "seq_end": float(seq)}


def arm_rtrace(ser: serial.Serial, seconds: int, every: int) -> str:
    return cmd(ser, f":rtrace_arm={int(seconds)},{int(every)}", 0.4)


def dump_rtrace(ser: serial.Serial, path: Path, timeout_s: float = 90.0) -> dict[str, int]:
    ser.reset_input_buffer()
    ser.write(b":rtrace_dump=1\n")
    ser.flush()
    buf = bytearray()
    t_end = time.time() + timeout_s
    while time.time() < t_end:
        chunk = ser.read(65536)
        if chunk:
            buf.extend(chunk)
            if END_MARK.encode("ascii") in buf:
                # drain a little more for trailing AP
                extra = time.time() + 0.4
                while time.time() < extra:
                    c = ser.read(65536)
                    if c:
                        buf.extend(c)
                break
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(buf)
    text = buf.decode("utf-8", "replace")
    return {
        "bytes": len(buf),
        "has_begin": int("[RTRACE-BEGIN" in text),
        "has_end": int(END_MARK in text),
        "n_f_lines": int(sum(1 for ln in text.splitlines() if ln.startswith("F,"))),
    }


def decode_rgb8(path: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray, dict[str, object]]:
    fmt = "unknown"
    dropped = 0
    frames_u8 = []
    ms = []
    modes = []
    begin = ""
    with path.open("r", errors="replace") as fh:
        for line in fh:
            s = line.strip()
            bm = BEGIN_RE.match(s)
            if bm:
                begin = bm.group("body")
                m = re.search(r"\bfmt=(\w+)", begin)
                fmt = m.group(1) if m else "unknown"
                continue
            m = F_RE.match(s)
            if not m:
                continue
            hexs = m.group("hex")
            if fmt != "rgb16hex":
                dropped += 1
                continue
            if len(hexs) == 0 or len(hexs) % 12 != 0:
                dropped += 1
                continue
            raw = bytes.fromhex(hexs)
            rgb16 = np.frombuffer(raw, dtype=">u2").reshape(-1, 3).copy()
            if rgb16.shape[0] != 160:
                dropped += 1
                continue
            frames_u8.append((rgb16 >> 8).astype(np.uint8))
            ms.append(int(m.group("ms")))
            modes.append(int(m.group("mode")))
    meta = {
        "fmt": fmt,
        "begin": begin,
        "dropped": dropped,
        "n_frames": len(frames_u8),
        "mode_set": sorted(set(modes)),
    }
    if not frames_u8:
        return (
            np.zeros((0, 160, 3), dtype=np.uint8),
            np.zeros((0,), dtype=np.float64),
            np.zeros((0,), dtype=np.int32),
            meta,
        )
    leds = np.stack(frames_u8, axis=0)
    t_ms = np.asarray(ms, dtype=np.float64)
    return leds, t_ms, np.asarray(modes, dtype=np.int32), meta


def resample_leds(leds: np.ndarray, t_ms: np.ndarray, n: int, *, warmup_s: float) -> np.ndarray:
    """Map dump frames onto the n-hop oracle grid after dropping warmup."""
    if leds.shape[0] < 8:
        raise RuntimeError(f"too few rtrace frames: {leds.shape[0]}")
    t = (t_ms - t_ms[0]) / 1000.0
    keep = t >= float(warmup_s) - 1e-6
    if int(keep.sum()) < 8:
        keep = np.ones(t.shape[0], dtype=bool)
    tt = t[keep]
    ll = leds[keep]
    t_rel = tt - tt[0]
    grid = np.arange(n, dtype=np.float64) * HOP_S
    t_max = float(t_rel[-1])
    if t_max <= 0:
        raise RuntimeError("rtrace timestamps collapsed")
    idx = np.clip(np.searchsorted(t_rel, grid, side="left"), 0, ll.shape[0] - 1)
    # nearest previous sample (causal)
    idx = np.where(t_rel[idx] > grid, np.maximum(idx - 1, 0), idx)
    return ll[idx]


def load_holdout(receipt_path: Path) -> list[dict]:
    raw = json.loads(receipt_path.read_text())
    return [r for r in raw["scores"] if r.get("set") == "holdout"]


def load_frozen(path: Path) -> dict:
    return json.loads(path.read_text())["map"]


def gains_for(oracle: dict, fmap: dict, share_name: str) -> dict[str, np.ndarray]:
    mix_f = np.asarray(apply_frozen_map(oracle["mix_rms"], fmap["mix_rms"]))
    share_f = np.asarray(apply_frozen_map(oracle[share_name], fmap[share_name]))
    mid = float(extra_gain(np.array([0.5]))[0])
    n = int(np.asarray(oracle["mix_rms"]).shape[0])
    return {
        "A": np.full(n, mid, dtype=np.float64),
        "B": extra_gain(mix_f),
        "D": extra_gain(share_f),
    }


def ap_peak_stats(text: str) -> dict[str, float]:
    peaks = []
    for line in text.splitlines():
        if "peak_scaled=" not in line:
            continue
        m = re.search(r"peak_scaled=([0-9.]+)", line)
        if m:
            peaks.append(float(m.group(1)))
    if not peaks:
        return {"n": 0, "median": float("nan"), "max": float("nan")}
    a = np.asarray(peaks, dtype=np.float64)
    return {"n": float(a.size), "median": float(np.median(a)), "max": float(np.max(a))}


def capture_condition(
    ser: serial.Serial,
    *,
    out_dir: Path,
    tag: str,
    gain: np.ndarray,
    seq0: int,
) -> dict[str, object]:
    n = int(gain.shape[0])
    warmup = np.full(max(1, int(round(WARMUP_S_RUN / HOP_S))), float(gain[0]), dtype=np.float64)
    series = np.concatenate([warmup, gain])
    arm_s = int(np.ceil(series.size * HOP_S + 1.0))
    arm_s = max(3, min(arm_s, 20))
    arm_echo = arm_rtrace(ser, arm_s, RTRACE_EVERY)
    stream = stream_gains(ser, series, seq0=seq0)
    # let the arm window close
    remain = arm_s - float(stream["duration_s"]) + 0.3
    if remain > 0:
        time.sleep(remain)
    dump_path = out_dir / f"{tag}.rtrace.log"
    dump_meta = dump_rtrace(ser, dump_path)
    leds, t_ms, modes, dec = decode_rgb8(dump_path)
    aligned = resample_leds(leds, t_ms, n, warmup_s=WARMUP_S_RUN) if leds.shape[0] else leds
    npz_path = out_dir / f"{tag}.npz"
    np.savez_compressed(
        npz_path,
        leds=aligned.astype(np.uint8),
        gain=gain.astype(np.float32),
        t_ms=t_ms.astype(np.float64),
        modes=modes.astype(np.int32),
    )
    return {
        "tag": tag,
        "arm_echo": arm_echo[-400:],
        "stream": stream,
        "dump": dump_meta,
        "decode": dec,
        "aligned_shape": list(aligned.shape),
        "npz": str(npz_path),
        "log": str(dump_path),
        "n_scorable": int(aligned.shape[0]),
        "rtrace_modes": dec.get("mode_set"),
        "head_finite": int(np.isfinite(head_position_upper(aligned)).sum()) if aligned.shape[0] else 0,
    }


def run_clip(
    ser: serial.Serial,
    row: dict,
    *,
    fmap: dict,
    cache_dir: Path,
    out_dir: Path,
    rate_hz: float,
    delay_s: float,
    seq0: int,
) -> tuple[dict, dict]:
    track = str(row["track"])
    share = str(row["share_driver"])
    n = int(row["n"])
    start_s = float(row["start_s"])
    oracle_full = dict(np.load(cache_path(cache_dir, track)))
    oracle = slice_oracle(oracle_full, start_s, n)
    n = min(n, int(np.asarray(oracle["mix_rms"]).shape[0]))
    for k, v in list(oracle.items()):
        a = np.asarray(v)
        if a.shape[:1] == (np.asarray(oracle["times"]).shape[0],):
            oracle[k] = a[:n]
    native = gains_for(oracle, fmap, share)
    gains = {
        cond: apply_cadence(native[cond], hop_s=HOP_S, rate_hz=rate_hz, delay_s=delay_s)
        for cond in ("A", "B", "D")
    }
    safe = "".join(ch if ch.isalnum() or ch in "-_." else "_" for ch in track)
    rate_tag = f"r{rate_hz:g}_d{int(round(actual_delay_s(delay_s)*1000))}ms"
    leds_map: dict[str, np.ndarray] = {}
    captures = {}
    seq = seq0
    for cond in ("A", "B", "D"):
        tag = f"{safe}_{rate_tag}_{cond}"
        cap = capture_condition(ser, out_dir=out_dir, tag=tag, gain=gains[cond], seq0=seq)
        seq = int(cap["stream"]["seq_end"]) + 8
        captures[cond] = cap
        npz = np.load(cap["npz"])
        leds_map[cond] = np.asarray(npz["leds"])
        leds_map[f"gain_{cond}"] = np.asarray(gains[cond])
    # C0 does not re-run Comet. score_clip still indexes control/mir for Q5.
    leds_map["control"] = leds_map["A"]
    leds_map["mir"] = leds_map["A"]
    rec = score_clip(leds_map, oracle, row)
    rec["rate_hz"] = float(rate_hz)
    rec["delay_s_requested"] = float(delay_s)
    rec["delay_s_actual"] = float(actual_delay_s(delay_s))
    rec["captures"] = {k: {kk: vv for kk, vv in v.items() if kk != "pin_echo"} for k, v in captures.items()}
    return rec, captures


def write_json(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, default=str) + "\n")


def main() -> int:
    raise SystemExit(
        "RETIRED: the two-clock C0 runner is dead. Original FAIL is preserved at "
        "artifacts/gate_c0/C0_RESULT.json (INVALID_TEMPORAL_EXECUTION). "
        "Use scripts/gate_c0v2_silicon.py. Do not overwrite artifacts/gate_c0/."
    )
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", default="")
    ap.add_argument("--out", type=Path, default=ROOT / "artifacts" / "gate_c0")
    ap.add_argument("--expect-env", default="k1_main_rpl_rtrace_probe")
    ap.add_argument("--cadence-n", type=int, default=3)
    args = ap.parse_args()

    port = find_port(args.port or None)
    out = args.out
    dumps = out / "dumps"
    dumps.mkdir(parents=True, exist_ok=True)
    receipt = ROOT / "artifacts" / "source_activity" / "p3c" / "receipt_musdb18_p3c.json"
    cache_dir = ROOT / "artifacts" / "source_activity" / "musdb18_oracle_cache"
    fmap = load_frozen(ROOT / "artifacts" / "source_activity" / "frozen_map_p3b.json")
    holdout = load_holdout(receipt)

    ser = open_ser(port)
    try:
        ident_text = identity_text(ser)
        ident = require_identity(ident_text, expect_env=args.expect_env)
        if not ident["chip"]:
            # :dump sometimes starves chip line; try again
            ident_text = identity_text(ser)
            ident = require_identity(ident_text, expect_env=args.expect_env)
        pin = pin_waveform_tempo(ser)
        ap_before = ap_peak_stats(ident_text)
        write_json(
            out / "session_identity.json",
            {
                "port": port,
                "usb_serial": EXPECT_USB,
                "identity": ident,
                "pin": {"dense_index": pin["dense_index"]},
                "ap_peak_before": ap_before,
                "binding": BINDING,
                "go": "K1-C0-RTRACE-FLASH-GO",
            },
        )

        native_rows = []
        seq = 1
        for i, row in enumerate(holdout):
            print(f"C0 native {i+1}/{len(holdout)} {row['track']}", flush=True)
            rec, _ = run_clip(
                ser,
                row,
                fmap=fmap,
                cache_dir=cache_dir,
                out_dir=dumps,
                rate_hz=NATIVE_HZ,
                delay_s=0.0,
                seq0=seq,
            )
            seq += 40000
            native_rows.append(rec)
            write_json(out / "native_partial.json", native_rows)

        native_summary = summarise(native_rows)
        ho = native_summary["holdout"]
        q1 = ho["Q1_knob_is_head_position"]
        q2 = ho["Q2_share_increment_in_pixels"]
        q3 = ho["Q3_source_abs_after_mix"]
        c0_pass = q1 == "PASS" and q2 == "PASS" and q3 == "PASS"
        native_delta = float(ho["median_delta_pos_share"])

        cadence_rows = []
        cadence_n = max(0, min(int(args.cadence_n), len(holdout)))
        cadence_plan = [
            {"rate_hz": 20.0, "delay_s": 0.0},
            {"rate_hz": 10.0, "delay_s": 0.0},
            {"rate_hz": float(NATIVE_HZ), "delay_s": 0.050},
        ]
        for cell in cadence_plan:
            cell_recs = []
            for row in holdout[:cadence_n]:
                print(
                    f"C0 cadence rate={cell['rate_hz']} delay={cell['delay_s']} {row['track']}",
                    flush=True,
                )
                rec, _ = run_clip(
                    ser,
                    row,
                    fmap=fmap,
                    cache_dir=cache_dir,
                    out_dir=dumps,
                    rate_hz=float(cell["rate_hz"]),
                    delay_s=float(cell["delay_s"]),
                    seq0=seq,
                )
                seq += 40000
                cell_recs.append(rec)
            deltas = [float(r["delta_pos_share"]) for r in cell_recs]
            med = float(np.nanmedian(np.asarray(deltas, dtype=np.float64))) if deltas else float("nan")
            cadence_rows.append(
                {
                    "rate_hz": cell["rate_hz"],
                    "delay_s_requested": cell["delay_s"],
                    "delay_s_actual": actual_delay_s(cell["delay_s"]),
                    "n": len(cell_recs),
                    "median_delta_pos_share": med,
                    "pass": bool(cell_passes(med, native_delta)),
                    "rows": cell_recs,
                }
            )

        ident_after = parse_identity(identity_text(ser))
        result = {
            "go": "K1-C0-RTRACE-FLASH-GO",
            "label": "ON_SILICON_PIXEL_VALIDATED" if c0_pass else "ON_SILICON_PIXEL_FAIL",
            "c0": "PASS" if c0_pass else "FAIL",
            "binding": BINDING,
            "device": {
                "chip": EXPECT_CHIP,
                "usb_serial": EXPECT_USB,
                "port": port,
                "identity": ident,
                "identity_after": ident_after,
            },
            "pin": {"mode_ordinal": MODE_ORDINAL, "dense_index": pin["dense_index"], "palette": PALETTE_INDEX, "mood": MOOD},
            "native": native_summary,
            "native_rows": native_rows,
            "cadence": cadence_rows,
            "ap_peak_before": ap_before,
            "non_claims": [
                "no Gate C perceptual verdict",
                "no student freeze",
                "no deployment candidate",
                "no Titan result",
                "no product firmware change",
            ],
            "ce_probe_mismatch": "k1_main_rpl_ce_probe does not exist; authorised env is k1_main_rpl_rtrace_probe",
        }
        write_json(out / "C0_RESULT.json", result)
        print(json.dumps({"c0": result["c0"], "Q1": q1, "Q2": q2, "Q3": q3, "delta": native_delta}, indent=2))
        return 0 if c0_pass else 2
    finally:
        try:
            ser.close()
        except Exception:
            pass


if __name__ == "__main__":
    raise SystemExit(main())
