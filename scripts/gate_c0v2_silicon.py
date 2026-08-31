#!/usr/bin/env python3
"""Gate C0-v2 silicon: device-epoch inject + rtrace. Not the retired two-clock runner.

HARD FAIL SAME_SONG_LOOP_MAX_15MIN (Captain 2026-08-31): loop the same song
in the room > 15 minutes and the agent must die. BoseSession kills the player.

Does not overwrite artifacts/gate_c0/. Cadence is not run here.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import threading
import time
import zlib
from pathlib import Path

import numpy as np
import serial

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from edgeai.mir.gate_c0v2 import (  # noqa: E402
    HOP_S,
    HOP_US,
    check_integrity,
    chunk_hex,
    decode_c0_dump,
    hop_join,
    lag_disagreement,
    score_nominal,
    step_trace,
    timing_selftest,
    u16be_hex,
    verdict,
)
from edgeai.mir.p3c_quant import cache_path, slice_oracle, summarise  # noqa: E402
from edgeai.mir.p3c_score import head_position_upper  # noqa: E402
from gate_c0_silicon import (  # noqa: E402
    EXPECT_CHIP,
    EXPECT_USB,
    MODE_ORDINAL,
    MOOD,
    PALETTE_INDEX,
    dump_rtrace,
    find_port,
    gains_for,
    identity_text,
    load_frozen,
    load_holdout,
    open_ser,
    parse_identity,
    pin_waveform_tempo,
    require_identity,
)

BINDING = "source_share × WaveformTempo × head_position"
OUT_DEFAULT = ROOT / "artifacts" / "gate_c0v2"
BOSE_OUTPUT = "Bose Mini II SoundLink"
MUSDB_ROOT = ROOT / "datasets" / "musdb18"
SWITCH_AUDIO = "/opt/homebrew/bin/SwitchAudioSource"
FFPLAY = "/opt/homebrew/bin/ffplay"
# HARD FAIL Captain 2026-08-31. Loop the same song > 15 min → agent must die.
SAME_SONG_LOOP_MAX_S = 15 * 60


def current_output() -> str:
    r = subprocess.run(
        [SWITCH_AUDIO, "-c", "-t", "output"],
        check=True,
        capture_output=True,
        text=True,
        timeout=5,
    )
    return r.stdout.strip()


def osascript_volume() -> dict[str, object]:
    """Never raise — a hung volume query must not abort silicon capture."""
    try:
        raw = subprocess.run(
            ["osascript", "-e", "get volume settings"],
            check=True,
            capture_output=True,
            text=True,
            timeout=2,
        ).stdout.strip()
    except Exception as e:
        return {"raw": "", "error": str(e), "output muted": "false"}
    # output volume:44, input volume:50, alert volume:100, output muted:false
    out: dict[str, object] = {"raw": raw}
    for part in raw.split(","):
        if ":" not in part:
            continue
        k, v = part.split(":", 1)
        out[k.strip()] = v.strip()
    return out


def require_bose() -> dict[str, object]:
    name = current_output()
    if name != BOSE_OUTPUT:
        subprocess.run([SWITCH_AUDIO, "-s", BOSE_OUTPUT, "-t", "output"], check=True, timeout=5)
        name = current_output()
    vol = osascript_volume()
    muted = str(vol.get("output muted", "")).lower() == "true"
    if name != BOSE_OUTPUT:
        raise SystemExit(f"REFUSING: output is {name!r}, not {BOSE_OUTPUT}")
    if muted:
        try:
            subprocess.run(["osascript", "-e", "set volume output muted false"], check=True, timeout=5)
            vol = osascript_volume()
        except Exception:
            pass
    try:
        level = int(vol.get("output volume", "0"))
    except (TypeError, ValueError):
        level = 50
    if vol.get("error"):
        return {"output": name, "volume": vol}
    if level < 20:
        raise SystemExit(f"REFUSING: output volume {level} is too low for Bose C0")
    return {"output": name, "volume": vol}


def find_stem(track: str) -> Path:
    for split in ("test", "train"):
        p = MUSDB_ROOT / split / f"{track}.stem.mp4"
        if p.is_file():
            return p
    raise FileNotFoundError(f"MUSDB stem missing for {track}")


class BoseSession:
    """Continuous Bose playback for a silicon session.

    HARD FAIL SAME_SONG_LOOP_MAX_15MIN: wall clock cap 15 minutes, then kill
    the player. Repeat the same song longer and the agent must die.

    Pass one file and loop_one=True to loop it without gaps (cadence 8 s
    windows). A list of files is played in order and repeated.
    """

    def __init__(self, tracks: list[Path], *, loop_one: bool = False) -> None:
        if not tracks:
            raise ValueError("BoseSession needs tracks")
        self.tracks = [Path(t) for t in tracks]
        self.loop_one = bool(loop_one)
        self._stop = threading.Event()
        self._proc: subprocess.Popen | None = None
        self._now = ""
        self._thread: threading.Thread | None = None
        self._t0 = 0.0

    def start(self) -> dict[str, object]:
        receipt = require_bose()
        self._stop.clear()
        self._t0 = time.time()
        self._thread = threading.Thread(target=self._run, name="bose-session", daemon=True)
        self._thread.start()
        deadline = time.time() + 8.0
        while time.time() < deadline:
            if self.alive:
                break
            time.sleep(0.1)
        if not self.alive:
            raise RuntimeError("Bose playlist failed to start")
        if current_output() != BOSE_OUTPUT:
            self.stop()
            raise RuntimeError("output left Bose after playlist start")
        receipt["tracks"] = [str(t) for t in self.tracks]
        receipt["now"] = self._now
        return receipt

    @property
    def alive(self) -> bool:
        t = self._thread
        p = self._proc
        return t is not None and t.is_alive() and p is not None and p.poll() is None

    def assert_alive(self) -> None:
        if self._t0 and (time.time() - self._t0) >= SAME_SONG_LOOP_MAX_S:
            self.stop()
            raise RuntimeError("SAME_SONG_LOOP_MAX_15MIN: agent must die")
        if not self.alive:
            raise RuntimeError(f"Bose playlist died (last={self._now!r})")
        if current_output() != BOSE_OUTPUT:
            raise RuntimeError(f"output left Bose: {current_output()!r}")

    def _expired(self) -> bool:
        return bool(self._t0) and (time.time() - self._t0) >= SAME_SONG_LOOP_MAX_S

    def _run(self) -> None:
        deadline = (self._t0 or time.time()) + SAME_SONG_LOOP_MAX_S
        if self.loop_one:
            path = self.tracks[0]
            self._now = str(path)
            require_bose()
            self._proc = subprocess.Popen(
                [FFPLAY, "-nodisp", "-loop", "0", "-loglevel", "error", "-i", str(path)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            while not self._stop.is_set() and self._proc.poll() is None:
                if time.time() >= deadline:
                    print("SAME_SONG_LOOP_MAX_15MIN: killing player — agent must die", flush=True)
                    break
                time.sleep(0.2)
            self._kill_player()
            return
        i = 0
        while not self._stop.is_set():
            if time.time() >= deadline:
                print("SAME_SONG_LOOP_MAX_15MIN: killing player — agent must die", flush=True)
                break
            path = self.tracks[i % len(self.tracks)]
            self._now = str(path)
            require_bose()
            self._proc = subprocess.Popen(
                [FFPLAY, "-nodisp", "-autoexit", "-loglevel", "error", "-i", str(path)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            while not self._stop.is_set() and self._proc.poll() is None:
                if time.time() >= deadline:
                    print("SAME_SONG_LOOP_MAX_15MIN: killing player — agent must die", flush=True)
                    break
                time.sleep(0.2)
            if self._stop.is_set():
                break
            i += 1
        self._kill_player()

    def _kill_player(self) -> None:
        p = self._proc
        if p is None or p.poll() is not None:
            return
        p.terminate()
        try:
            p.wait(timeout=2)
        except subprocess.TimeoutExpired:
            p.kill()

    def stop(self) -> None:
        self._stop.set()
        self._kill_player()
        t = self._thread
        if t is not None:
            t.join(timeout=3)


def write_json(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, default=str) + "\n")


def cmd(ser: serial.Serial, line: str, wait: float = 0.45) -> str:
    if not line.startswith(":"):
        raise ValueError(line)
    ser.reset_input_buffer()
    ser.write((line.strip() + "\n").encode("ascii"))
    ser.flush()
    end = time.time() + wait
    buf = bytearray()
    while time.time() < end:
        chunk = ser.read(8192)
        if chunk:
            buf.extend(chunk)
    return buf.decode("utf-8", "replace")


def wait_done(ser: serial.Serial, timeout_s: float) -> str:
    end = time.time() + timeout_s
    buf = bytearray()
    while time.time() < end:
        chunk = ser.read(8192)
        if chunk:
            buf.extend(chunk)
            if b"[C0_DONE" in buf:
                extra = time.time() + 0.4
                while time.time() < extra:
                    c = ser.read(8192)
                    if c:
                        buf.extend(c)
                break
    return buf.decode("utf-8", "replace")


def load_trace(ser: serial.Serial, *, cond: str, epoch_id: int, samples: np.ndarray) -> str:
    samples = np.asarray(samples, dtype=np.uint16).reshape(-1)
    n = int(samples.size)
    echo = []
    echo.append(cmd(ser, ":c0_clear=1", 0.3))
    echo.append(cmd(ser, f":c0_cfg={cond},{HOP_US},{epoch_id},{n}", 0.4))
    hx = u16be_hex(samples)
    for part in chunk_hex(hx, 32):
        echo.append(cmd(ser, f":c0_hex={part}", 0.35))
    echo.append(cmd(ser, ":c0_status=1", 0.35))
    crc_host = zlib.crc32(samples.astype("<u2").tobytes()) & 0xFFFFFFFF
    blob = "\n".join(echo)
    if f"loaded={n}/{n}" not in blob:
        raise RuntimeError("C0 load incomplete\n" + blob[-2000:])
    return blob + f"\nhost_crc32={crc_host:08x}\n"


def run_loaded(ser: serial.Serial, *, preroll: int, postroll: int, every: int = 1) -> str:
    n_hops_guess = 512
    every = max(1, int(every))
    timeout = preroll * 0.015 + n_hops_guess * 0.032 + postroll * 0.015 + 8.0
    ser.reset_input_buffer()
    ser.write(f":c0_run={preroll},{postroll},{every}\n".encode("ascii"))
    ser.flush()
    return wait_done(ser, timeout)


def capture_samples(
    ser: serial.Serial,
    *,
    out_dir: Path,
    tag: str,
    cond: str,
    epoch_id: int,
    samples: np.ndarray,
    preroll: int = 40,
    postroll: int = 40,
    every: int = 1,
    bose: BoseSession | None = None,
) -> dict:
    if bose is None:
        raise SystemExit("REFUSING: C0-v2 will not run silent. Bose playlist must already be playing.")
    bose.assert_alive()
    load_echo = load_trace(ser, cond=cond, epoch_id=epoch_id, samples=samples)
    bose.assert_alive()
    audio_receipt: dict[str, object] = {
        "continuous": True,
        "now": bose._now,
        "output": current_output(),
        "volume": osascript_volume(),
    }
    run_echo = run_loaded(ser, preroll=preroll, postroll=postroll, every=every)
    bose.assert_alive()
    dump_path = out_dir / f"{tag}.rtrace.log"
    dump_meta = dump_rtrace(ser, dump_path, timeout_s=180.0)
    text = dump_path.read_text(errors="replace")
    dump = decode_c0_dump(text)
    integ = check_integrity(dump, samples)
    hops, gain, present = hop_join(dump, int(samples.size))
    pos = head_position_upper(hops) if hops.shape[0] else np.zeros((0,), dtype=np.float64)
    lag = lag_disagreement(pos, gain)
    npz_path = out_dir / f"{tag}.npz"
    np.savez_compressed(
        npz_path,
        leds=hops.astype(np.uint8),
        gain=gain.astype(np.float32),
        present=present.astype(np.int8),
        samples_u16=np.asarray(samples, dtype=np.uint16),
        t_ms=dump.t_ms,
        applied_u16=dump.applied_u16,
        sem_idx=dump.sem_idx,
        inj=dump.inj,
        marker=dump.marker,
        tick=dump.tick,
        device_us=dump.device_us,
    )
    invalid = (not integ.ok) or bool(lag.get("invalid"))
    return {
        "tag": tag,
        "log": str(dump_path),
        "npz": str(npz_path),
        "load_echo_tail": load_echo[-800:],
        "run_echo_tail": run_echo[-800:],
        "dump": dump_meta,
        "integrity": {"status": integ.status, "reasons": integ.reasons, "details": integ.details},
        "lag": lag,
        "epoch": dump.epoch,
        "n_frames": int(dump.leds.shape[0]),
        "n_hops_present": int(present.sum()),
        "invalid": bool(invalid),
        "pipeline_lat": dump.pipeline_lat,
        "has_c0_done": int("[C0_DONE" in run_echo),
        "audio": audio_receipt,
    }


def gain_to_u16(gain: np.ndarray) -> np.ndarray:
    g = np.clip(np.asarray(gain, dtype=np.float64).reshape(-1), 0.0, 1.0)
    return np.rint(g * 65535.0).astype(np.uint16)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", default="")
    ap.add_argument("--out", type=Path, default=OUT_DEFAULT)
    ap.add_argument("--expect-env", default="k1_main_rpl_rtrace_probe")
    ap.add_argument("--selftest-only", action="store_true")
    ap.add_argument("--skip-selftest", action="store_true")
    args = ap.parse_args()

    out = args.out
    dumps = out / "dumps"
    dumps.mkdir(parents=True, exist_ok=True)

    # Duration first — Captain standing order after the 9-minute silent wait.
    print(
        "DURATION: start continuous Bose playlist, then timing self-test ~1 min, "
        "then nominal C0-v2 ~18 min. Music stays on the whole time — full tracks, "
        "no start/stop slices. Restore after. Cadence is NOT in this run.",
        flush=True,
    )
    bose_info = require_bose()
    print(f"AUDIO: {bose_info['output']} volume={bose_info['volume'].get('output volume')}", flush=True)

    port = find_port(args.port or None)
    ser = open_ser(port)
    bose = None
    try:
        ident_text = identity_text(ser)
        ident = require_identity(ident_text, expect_env=args.expect_env)
        pin = pin_waveform_tempo(ser)
        cmd(ser, ":show_skip=off", 0.3)
        cmd(ser, ":ap_stream=off", 0.25)
        write_json(
            out / "session_identity.json",
            {
                "port": port,
                "usb_serial": EXPECT_USB,
                "chip": EXPECT_CHIP,
                "identity": ident,
                "pin": {
                    "dense_index": pin["dense_index"],
                    "mode_ordinal": MODE_ORDINAL,
                    "palette": PALETTE_INDEX,
                    "mood": MOOD,
                },
                "binding": BINDING,
                "retired_c0": "artifacts/gate_c0/C0_RESULT.json remains FAIL INVALID_TEMPORAL_EXECUTION",
            },
        )

        receipt = ROOT / "artifacts" / "source_activity" / "p3c" / "receipt_musdb18_p3c.json"
        holdout = load_holdout(receipt)
        playlist = [find_stem(str(r["track"])) for r in holdout]
        bose = BoseSession(playlist)
        bose_receipt = bose.start()
        print(f"BOSE PLAYING continuously: {len(playlist)} full holdout tracks, looping", flush=True)
        write_json(out / "bose_session.json", bose_receipt)
        selftest = None
        if not args.skip_selftest:
            samples, changes = step_trace(n_seg=16)
            print(
                f"C0-v2 timing self-test: {samples.size} hops, changes at {changes}; "
                "Bose already playing",
                flush=True,
            )
            cap = capture_samples(
                ser,
                out_dir=dumps,
                tag="timing_selftest",
                cond="T",
                epoch_id=1,
                samples=samples,
                preroll=40,
                postroll=40,
                bose=bose,
            )
            text = Path(cap["log"]).read_text(errors="replace")
            dump = decode_c0_dump(text)
            selftest = timing_selftest(dump, samples, expected_change_at=changes)
            selftest["capture"] = {k: v for k, v in cap.items() if k != "load_echo_tail"}
            write_json(out / "timing_selftest.json", selftest)
            print(f"timing self-test {selftest['status']}: {selftest.get('reasons')}", flush=True)
            if selftest["status"] != "PASS":
                write_json(
                    out / "C0V2_RESULT.json",
                    {
                        "c0v2": "INVALID_RUN",
                        "reason": "timing_selftest_failed",
                        "selftest": selftest,
                        "nominal": "NOT_RUN",
                        "cadence": "OPEN — not this run",
                        "bose": bose_receipt,
                    },
                )
                return 2

        if args.selftest_only:
            write_json(
                out / "C0V2_RESULT.json",
                {
                    "c0v2": "SELFTEST_PASS",
                    "nominal": "NOT_RUN",
                    "cadence": "OPEN — not this run",
                    "selftest": selftest,
                    "bose": bose_receipt,
                },
            )
            return 0

        cache_dir = ROOT / "artifacts" / "source_activity" / "musdb18_oracle_cache"
        fmap = load_frozen(ROOT / "artifacts" / "source_activity" / "frozen_map_p3b.json")
        rows = []
        epoch_id = 100
        for i, row in enumerate(holdout):
            track = str(row["track"])
            print(f"C0-v2 nominal {i + 1}/{len(holdout)} {track}", flush=True)
            oracle_full = dict(np.load(cache_path(cache_dir, track)))
            n = int(row["n"])
            start_s = float(row["start_s"])
            oracle = slice_oracle(oracle_full, start_s, n)
            n = min(n, int(np.asarray(oracle["mix_rms"]).shape[0]))
            for k, v in list(oracle.items()):
                a = np.asarray(v)
                if a.shape[:1] == (np.asarray(oracle["times"]).shape[0],):
                    oracle[k] = a[:n]
            native = gains_for(oracle, fmap, str(row["share_driver"]))
            safe = "".join(ch if ch.isalnum() or ch in "-_." else "_" for ch in track)
            leds_map: dict[str, np.ndarray] = {}
            gain_map: dict[str, np.ndarray] = {}
            lag_rows: dict[str, dict] = {}
            caps = {}
            any_invalid = False
            for cond in ("A", "B", "D"):
                epoch_id += 1
                samples = gain_to_u16(native[cond])
                cap = capture_samples(
                    ser,
                    out_dir=dumps,
                    tag=f"{safe}_{cond}",
                    cond=cond,
                    epoch_id=epoch_id,
                    samples=samples,
                    bose=bose,
                )
                caps[cond] = cap
                npz = np.load(cap["npz"])
                leds_map[cond] = np.asarray(npz["leds"])
                gain_map[cond] = np.asarray(npz["gain"], dtype=np.float64)
                pos = head_position_upper(leds_map[cond])
                lag_rows[cond] = lag_disagreement(pos, gain_map[cond])
                if cap["invalid"] or lag_rows[cond].get("invalid"):
                    any_invalid = True
            rec = score_nominal(leds_map, gain_map, oracle, row, lag_rows)
            rec["captures"] = caps
            rec["timing_invalid"] = bool(any_invalid or rec.get("timing_invalid"))
            rows.append(rec)
            write_json(out / "nominal_partial.json", rows)

        summary = summarise(rows)
        ho = summary.get("holdout") or summary.get("all") or next(iter(summary.values()))
        q1 = ho["Q1_knob_is_head_position"]
        q2 = ho["Q2_share_increment_in_pixels"]
        q3 = ho["Q3_source_abs_after_mix"]
        integ_ok = all(not r.get("timing_invalid") for r in rows)
        lag_invalid = any(
            (r.get("lag") or {}).get(c, {}).get("invalid") for r in rows for c in ("A", "B", "D")
        )
        stamp = verdict(integ_ok, q1, q2, q3, bool(lag_invalid))
        result = {
            "c0v2": stamp,
            "binding": BINDING,
            "lag_corrected": False,
            "selftest": selftest,
            "identity": ident,
            "pin": {"dense_index": pin["dense_index"], "mode_ordinal": MODE_ORDINAL},
            "native": summary,
            "Q1": q1,
            "Q2": q2,
            "Q3": q3,
            "cadence": "OPEN — not this run",
            "c1": "blocked until ON_SILICON_PIXEL_VALIDATED",
            "bose": bose_receipt,
            "retired_c0_untouched": True,
            "non_claims": [
                "previous C0 is still FAIL INVALID_TEMPORAL_EXECUTION",
                "no Gate C perceptual verdict",
                "no student freeze",
                "no cadence freeze",
                "no Titan",
                "no product firmware change until restore",
            ],
        }
        if stamp == "PASS":
            result["stamp"] = "source_share × WaveformTempo × head_position = ON_SILICON_PIXEL_VALIDATED"
        write_json(out / "C0V2_RESULT.json", result)
        write_json(out / "nominal_rows.json", rows)
        print(f"C0-v2 {stamp} Q1={q1} Q2={q2} Q3={q3}", flush=True)
        return 0 if stamp != "INVALID_RUN" else 2
    finally:
        if bose is not None:
            try:
                bose.stop()
            except Exception:
                pass
        ser.close()


if __name__ == "__main__":
    raise SystemExit(main())
