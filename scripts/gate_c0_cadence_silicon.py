#!/usr/bin/env python3
"""Gate C cadence/latency on Main RPL using the C0-v2 device-epoch harness.

HARD FAIL SAME_SONG_LOOP_MAX_15MIN (Captain 2026-08-31): loop the same song
in the room > 15 minutes and the agent must die. BoseSession kills the player.

Named GO: K1-C0-CADENCE-LATENCY-FLASH-GO. Cadence is CLOSED. Do not reopen
C0-v2. Do not train a net. Restore product firmware after capture.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from edgeai.mir.gate_c_cadence import (  # noqa: E402
    BINDING,
    HOLD_POLICY,
    HOP_S,
    NATIVE_HZ,
    SHARE_SOURCES,
    SILICON_DELAY_S,
    SILICON_RATE_HZ,
    actual_delay_s,
    apply_cadence,
    delay_hops,
    honest_delay_bracket,
    honest_rate_bracket,
    largest_passing_delay_s,
    q_binding_from_summary,
    require_four_source_share,
    slowest_passing_rate_hz,
)
from edgeai.mir.gate_c0v2 import (  # noqa: E402
    decode_c0_dump,
    hop_join,
    lag_disagreement,
    score_nominal,
    step_trace,
    timing_selftest,
    verdict,
)
from edgeai.serial_studio import (  # noqa: E402
    SerialStudioError,
    holder_is_serial_studio,
    refuse_if_serial_studio_owns_usb,
)
from edgeai.mir.p3c_quant import cache_path, slice_oracle, summarise  # noqa: E402
from edgeai.mir.p3c_score import head_position_upper  # noqa: E402
from gate_c0_silicon import (  # noqa: E402
    EXPECT_CHIP,
    EXPECT_USB,
    MODE_ORDINAL,
    MOOD,
    PALETTE_INDEX,
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
from gate_c0v2_silicon import (  # noqa: E402
    BoseSession,
    capture_samples,
    cmd,
    current_output,
    find_stem,
    gain_to_u16,
    osascript_volume,
    require_bose,
    write_json,
)

FW_ROOT = Path("/Users/spectrasynq/SpectraSynq_K1_Firmware/.worktrees/effect-response-atlas")
FLASH_SH = FW_ROOT / "scripts" / "agent" / "k1-flash-verified.sh"
PROBE_ENV = "k1_main_rpl_rtrace_probe"
PRODUCT_ENV = "k1_main_rpl_im69d"
PRODUCT_GIT = "acaecaa8"
PROBE_BRANCH = "probe/c0-epoch-v2"
OUT_DEFAULT = ROOT / "artifacts" / "gate_c0_cadence_silicon"
C0V2_RECEIPT = ROOT / "artifacts" / "gate_c0v2" / "C0V2_RESULT.json"
C0V2_DELTA = 0.6902070639445945
C0V2_Q1 = 0.8318621417942687
FFMPEG = "/opt/homebrew/bin/ffmpeg"
SLICE_S = 8.0
RTRACE_EVERY = 1  # every=4 produced INVALID dumps; audio length is the 8 s loop, not dump decimation


def cell_key(rate_hz: float, delay_s: float) -> str:
    return f"r{rate_hz:g}_d{int(round(delay_s * 1000))}"


def extract_holdout_slices(holdout: list[dict], dest: Path) -> list[Path]:
    """Loop the scored 8 s windows, not the full stems."""
    dest.mkdir(parents=True, exist_ok=True)
    out: list[Path] = []
    for i, row in enumerate(holdout):
        stem = find_stem(str(row["track"]))
        start = float(row["start_s"])
        safe = "".join(ch if ch.isalnum() or ch in "-_." else "_" for ch in str(row["track"]))
        wav = dest / f"{i:02d}_{safe}.wav"
        if wav.is_file() and wav.stat().st_size > 1000:
            out.append(wav)
            continue
        subprocess.run(
            [
                FFMPEG,
                "-y",
                "-ss",
                f"{start:.3f}",
                "-t",
                f"{SLICE_S:.3f}",
                "-i",
                str(stem),
                "-vn",
                "-ac",
                "2",
                "-ar",
                "44100",
                "-loglevel",
                "error",
                str(wav),
            ],
            check=True,
            timeout=30,
        )
        if wav.stat().st_size < 1000:
            raise RuntimeError(f"slice extract empty: {wav}")
        out.append(wav)
    concat = dest / "holdout_8s_loop.wav"
    listing = dest / "concat.txt"
    listing.write_text("".join(f"file '{p.resolve()}'\n" for p in out))
    subprocess.run(
        [
            FFMPEG,
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(listing),
            "-c",
            "copy",
            "-loglevel",
            "error",
            str(concat),
        ],
        check=True,
        timeout=30,
    )
    if concat.stat().st_size < 1000:
        raise RuntimeError("concat slice loop empty")
    return [concat]


def load_c0v2_reference() -> dict:
    d = json.loads(C0V2_RECEIPT.read_text())
    if d.get("c0v2") != "PASS":
        raise SystemExit("REFUSING: C0-v2 receipt is not PASS; cadence is not authorised on a failed carrier")
    ho = d["native"]["holdout"]
    qb = q_binding_from_summary(ho)
    return {
        "family": "rate",
        "rate_hz": float(NATIVE_HZ),
        "delay_s": 0.0,
        "requested_delay_ms": 0,
        "actual_delay_ms": 0,
        "actual_delay_hops": 0,
        "source": "c0v2_receipt",
        "hold_policy": HOLD_POLICY,
        "lag_corrected": False,
        "status": "PASS",
        "Q1": qb["Q1"],
        "Q2": qb["Q2"],
        "Q3": qb["Q3"],
        "verdict": qb["verdict"],
        "summary": ho,
        "fraction_of_c0v2": 1.0,
        "n_clips": int(ho.get("n_clips") or 0),
        "wins_delta_pos_share": ho.get("wins_delta_pos_share"),
        "median_delta_pos_share": ho.get("median_delta_pos_share"),
        "median_spearman_pos_gain": ho.get("median_spearman_pos_gain"),
        "identity": d.get("identity"),
    }


def flash_env(env: str, port: str) -> None:
    if not FLASH_SH.is_file():
        raise SystemExit(f"missing flash script {FLASH_SH}")
    print(f"FLASH {env} port={port}", flush=True)
    subprocess.run(
        ["bash", str(FLASH_SH), env, "--port", port],
        cwd=str(FW_ROOT),
        check=True,
    )


def git_checkout(ref: str) -> None:
    subprocess.run(["git", "checkout", ref], cwd=str(FW_ROOT), check=True)


def wait_port(timeout_s: float = 40.0) -> str:
    deadline = time.time() + timeout_s
    last = ""
    while time.time() < deadline:
        try:
            return find_port()
        except SystemExit as e:
            last = str(e)
            time.sleep(1.0)
    raise SystemExit(f"Main RPL USB {EXPECT_USB} did not reappear: {last}")


def restore_product(port: str) -> dict[str, str]:
    """Checkout product SHA, flash im69d, return to probe branch. Never flash im69d from probe HEAD."""
    print("RESTORE product firmware", flush=True)
    git_checkout(PRODUCT_GIT)
    try:
        port = wait_port()
        flash_env(PRODUCT_ENV, port)
    finally:
        git_checkout(PROBE_BRANCH)
    time.sleep(2.0)
    port = wait_port()
    ser = open_ser(port)
    try:
        ident = parse_identity(identity_text(ser))
    finally:
        ser.close()
    if ident.get("git") != PRODUCT_GIT or ident.get("env") != PRODUCT_ENV:
        raise SystemExit(f"RESTORE FAILED identity={ident}")
    if ident.get("chip") != EXPECT_CHIP:
        raise SystemExit(f"RESTORE FAILED chip={ident}")
    print(
        f"RESTORE OK git={ident.get('git')} env={ident.get('env')} "
        f"epoch={ident.get('epoch')} chip={ident.get('chip')}",
        flush=True,
    )
    return ident


def score_cell_rows(rows: list[dict]) -> dict:
    summary = summarise(rows)
    ho = summary.get("holdout") or summary.get("all") or next(iter(summary.values()))
    qb = q_binding_from_summary(ho)
    integ_ok = all(not r.get("timing_invalid") for r in rows)
    lag_invalid = any(
        (r.get("lag") or {}).get(c, {}).get("invalid") for r in rows for c in ("A", "B", "D")
    )
    status = verdict(integ_ok, qb["Q1"], qb["Q2"], qb["Q3"], bool(lag_invalid))
    delta = float(ho.get("median_delta_pos_share") or float("nan"))
    frac = float(delta / C0V2_DELTA) if delta == delta and C0V2_DELTA else float("nan")
    by_src: dict[str, list[float]] = {}
    for r in rows:
        src = str(r.get("share_driver") or "?")
        by_src.setdefault(src, []).append(float(r.get("delta_pos_share") or float("nan")))
    src_med = {
        k: float(np.nanmedian(np.asarray(v, dtype=np.float64))) for k, v in sorted(by_src.items())
    }
    binding_verdict = qb["verdict"] if status != "INVALID_RUN" else "INVALID_RUN"
    return {
        "status": status,
        "verdict": binding_verdict if status != "BINDING_FAIL" else "FAIL",
        "Q1": qb["Q1"],
        "Q2": qb["Q2"],
        "Q3": qb["Q3"],
        "summary": ho,
        "n_clips": len(rows),
        "n_timing_invalid": int(sum(bool(r.get("timing_invalid")) for r in rows)),
        "wins_delta_pos_share": ho.get("wins_delta_pos_share"),
        "median_delta_pos_share": ho.get("median_delta_pos_share"),
        "median_delta_pos_abs": ho.get("median_delta_pos_abs"),
        "median_spearman_pos_gain": ho.get("median_spearman_pos_gain"),
        "fraction_of_c0v2": frac,
        "source_delta_medians": src_med,
        "lag_corrected": False,
    }


def run_one_cell(
    *,
    ser,
    bose: BoseSession,
    holdout: list[dict],
    fmap: dict,
    cache_dir: Path,
    dumps: Path,
    cells_dir: Path,
    rate_hz: float,
    delay_s: float,
    family: str,
    ident: dict,
    epoch_id_start: int,
    resume: bool,
) -> tuple[dict, int]:
    key = cell_key(rate_hz, delay_s)
    out_path = cells_dir / f"{key}.json"
    if resume and out_path.is_file():
        prev = json.loads(out_path.read_text())
        if prev.get("status") != "INVALID_RUN" and prev.get("verdict") in ("PASS", "FAIL"):
            print(f"RESUME skip {key} verdict={prev.get('verdict')}", flush=True)
            return prev, epoch_id_start
    actual_ms = actual_delay_s(delay_s) * 1000.0
    print(
        f"CELL {family} rate={rate_hz:g} Hz delay={delay_s*1000:.0f} ms "
        f"(actual {actual_ms:.0f} ms / {delay_hops(delay_s)} hops) policy=ZOH",
        flush=True,
    )
    rows = []
    epoch_id = epoch_id_start
    cell_dumps = dumps / key
    cell_dumps.mkdir(parents=True, exist_ok=True)
    for i, row in enumerate(holdout):
        track = str(row["track"])
        print(f"  {key} {i + 1}/{len(holdout)} {track}", flush=True)
        oracle_full = dict(np.load(cache_path(cache_dir, track)))
        n = int(row["n"])
        start_s = float(row["start_s"])
        oracle = slice_oracle(oracle_full, start_s, n)
        n = min(n, int(np.asarray(oracle["mix_rms"]).shape[0]))
        for k, v in list(oracle.items()):
            a = np.asarray(v)
            if a.shape[:1] == (np.asarray(oracle["times"]).shape[0],):
                oracle[k] = a[:n]
        require_four_source_share(oracle)
        native = gains_for(oracle, fmap, str(row["share_driver"]))
        injected = {
            cond: apply_cadence(native[cond], hop_s=HOP_S, rate_hz=rate_hz, delay_s=delay_s)
            for cond in ("A", "B", "D")
        }
        safe = "".join(ch if ch.isalnum() or ch in "-_." else "_" for ch in track)
        leds_map: dict[str, np.ndarray] = {}
        native_gain_map: dict[str, np.ndarray] = {}
        lag_rows: dict[str, dict] = {}
        caps: dict[str, dict] = {}
        any_invalid = False
        for cond in ("A", "B", "D"):
            epoch_id += 1
            samples = gain_to_u16(injected[cond])
            tag = f"{safe}_{cond}"
            cap = None
            for attempt in range(2):
                cap = capture_samples(
                    ser,
                    out_dir=cell_dumps,
                    tag=tag,
                    cond=cond,
                    epoch_id=epoch_id,
                    samples=samples,
                    every=RTRACE_EVERY,
                    bose=bose,
                )
                if not cap.get("invalid"):
                    break
                print(f"    retry {tag} attempt={attempt + 1} invalid={cap.get('invalid')}", flush=True)
            assert cap is not None
            caps[cond] = {k: v for k, v in cap.items() if k not in ("load_echo_tail", "run_echo_tail")}
            npz = np.load(cap["npz"])
            leds_map[cond] = np.asarray(npz["leds"])
            native_gain_map[cond] = np.asarray(native[cond], dtype=np.float64)
            applied = np.asarray(npz["gain"], dtype=np.float64)
            pos = head_position_upper(leds_map[cond])
            lag_rows[cond] = lag_disagreement(pos, applied)
            if cap["invalid"] or lag_rows[cond].get("invalid"):
                any_invalid = True
        rec = score_nominal(leds_map, native_gain_map, oracle, row, lag_rows)
        rec["captures"] = caps
        rec["timing_invalid"] = bool(any_invalid or rec.get("timing_invalid"))
        rec["rate_hz"] = rate_hz
        rec["delay_s"] = delay_s
        rows.append(rec)
        write_json(cells_dir / f"{key}_partial.json", rows)

    scored = score_cell_rows(rows)
    result = {
        "family": family,
        "rate_hz": float(rate_hz),
        "delay_s": float(delay_s),
        "requested_delay_ms": int(round(delay_s * 1000.0)),
        "actual_delay_ms": float(actual_ms),
        "actual_delay_hops": int(delay_hops(delay_s)),
        "source": "silicon",
        "hold_policy": HOLD_POLICY,
        "lag_corrected": False,
        "identity": ident,
        "pin": {"mode_ordinal": MODE_ORDINAL, "palette": PALETTE_INDEX, "mood": MOOD},
        "binding": BINDING,
        **scored,
        "rows": [
            {
                "track": r.get("track"),
                "share_driver": r.get("share_driver"),
                "timing_invalid": r.get("timing_invalid"),
                "delta_pos_share": r.get("delta_pos_share"),
                "delta_pos_abs": r.get("delta_pos_abs"),
                "spearman_B_pos_gain": r.get("spearman_B_pos_gain"),
                "spearman_D_pos_gain": r.get("spearman_D_pos_gain"),
                "lag": r.get("lag"),
            }
            for r in rows
        ],
    }
    write_json(out_path, result)
    print(
        f"CELL {key} {result['status']} Q1={result['Q1']} Q2={result['Q2']} Q3={result['Q3']} "
        f"Δ={result.get('median_delta_pos_share')} frac={result.get('fraction_of_c0v2')}",
        flush=True,
    )
    return result, epoch_id


def maybe_extra_rate(rate_rows: list[dict]) -> float | None:
    """One intermediate rate only if the PASS/FAIL boundary is tight on Q2."""
    valid = [r for r in rate_rows if r.get("status") != "INVALID_RUN"]
    by = {float(r["rate_hz"]): r for r in valid}
    if 15.0 in by and 10.0 in by:
        a, b = by[15.0], by[10.0]
        if a.get("verdict") == "PASS" and b.get("verdict") != "PASS":
            d15 = float(a.get("median_delta_pos_share") or 0.0)
            if 0.15 <= d15 <= 0.18:
                return 12.5
    if 20.0 in by and 15.0 in by:
        a, b = by[20.0], by[15.0]
        if a.get("verdict") == "PASS" and b.get("verdict") != "PASS":
            d20 = float(a.get("median_delta_pos_share") or 0.0)
            if 0.15 <= d20 <= 0.18:
                return 17.5
    return None


def maybe_extra_delay(delay_rows: list[dict]) -> float | None:
    valid = [r for r in delay_rows if r.get("status") != "INVALID_RUN"]
    by = {float(r["delay_s"]): r for r in valid}
    pairs = [(0.025, 0.050, 0.0375), (0.050, 0.100, 0.075)]
    for lo, hi, mid in pairs:
        if lo in by and hi in by:
            a, b = by[lo], by[hi]
            if a.get("verdict") == "PASS" and b.get("verdict") != "PASS":
                dlo = float(a.get("median_delta_pos_share") or 0.0)
                if 0.15 <= dlo <= 0.18:
                    return mid
    return None


def pick_delay_test_rate(rate_rows: list[dict]) -> float:
    """Comfortably passing rate. 20 Hz if it PASSes; else native C0-v2 cadence."""
    by = {float(r["rate_hz"]): r for r in rate_rows if r.get("status") != "INVALID_RUN"}
    r20 = by.get(20.0)
    if r20 is not None and r20.get("verdict") == "PASS":
        return 20.0
    r15 = by.get(15.0)
    if r15 is not None and r15.get("verdict") == "PASS":
        return 15.0
    return float(NATIVE_HZ)


def write_contract(out: Path, payload: dict) -> None:
    write_json(out / "SEMANTIC_TRANSPORT_CONTRACT.json", payload)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", default="")
    ap.add_argument("--out", type=Path, default=OUT_DEFAULT)
    ap.add_argument("--expect-env", default=PROBE_ENV)
    ap.add_argument("--skip-flash", action="store_true")
    ap.add_argument("--skip-selftest", action="store_true")
    ap.add_argument("--skip-restore", action="store_true")
    ap.add_argument("--resume", action="store_true", default=True)
    ap.add_argument("--no-resume", action="store_true")
    args = ap.parse_args()
    resume = bool(args.resume) and not bool(args.no_resume)

    out = args.out
    dumps = out / "dumps"
    cells_dir = out / "cells"
    dumps.mkdir(parents=True, exist_ok=True)
    cells_dir.mkdir(parents=True, exist_ok=True)

    print(
        "DURATION: remaining cells only (20 Hz and 15 Hz already scored). "
        "Bose loops the scored 8-second windows, not whole songs. "
        "About 8–12 min per remaining cell. Restore at the end.",
        flush=True,
    )

    ref = load_c0v2_reference()
    write_json(cells_dir / f"{cell_key(NATIVE_HZ, 0.0)}.json", ref)
    bose_info = require_bose()
    print(f"AUDIO: {bose_info['output']} volume={bose_info['volume'].get('output volume')}", flush=True)

    port = find_port(args.port or None)
    try:
        refuse_if_serial_studio_owns_usb(port)
    except SerialStudioError as e:
        raise SystemExit(str(e)) from e
    restored: dict[str, str] | None = None
    bose = None
    ser = None
    try:
        if not args.skip_flash:
            if holder_is_serial_studio(port):
                raise SystemExit(
                    "REFUSING flash while Serial Studio holds USB. "
                    "Close Serial Studio first."
                )
            flash_env(PROBE_ENV, port)
            time.sleep(2.0)
            port = wait_port()
            try:
                refuse_if_serial_studio_owns_usb(port)
            except SerialStudioError as e:
                raise SystemExit(str(e)) from e
        ser = open_ser(port)
        print(f"I/O: pyserial {port}", flush=True)
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
                "hold_policy": HOLD_POLICY,
                "authorisation": "K1-C0-CADENCE-LATENCY-FLASH-GO",
                "c0v2_untouched": True,
            },
        )

        receipt = ROOT / "artifacts" / "source_activity" / "p3c" / "receipt_musdb18_p3c.json"
        holdout = load_holdout(receipt)
        for row in holdout:
            oracle_full = dict(
                np.load(cache_path(ROOT / "artifacts" / "source_activity" / "musdb18_oracle_cache", str(row["track"])))
            )
            require_four_source_share(oracle_full)
        playlist = extract_holdout_slices(holdout, out / "bose_slices")
        bose = BoseSession(playlist, loop_one=True)
        bose_receipt = bose.start()
        bose_receipt["slice_s"] = SLICE_S
        bose_receipt["whole_songs"] = False
        print(
            f"BOSE PLAYING 8 s scored windows looping ({len(playlist)} slices), not full tracks",
            flush=True,
        )
        write_json(out / "bose_session.json", bose_receipt)

        selftest = None
        selftest_path = out / "timing_selftest.json"
        if args.skip_selftest and selftest_path.is_file():
            selftest = json.loads(selftest_path.read_text())
        elif not args.skip_selftest:
            samples, changes = step_trace(n_seg=16)
            print(f"timing self-test: {samples.size} hops, Bose already playing", flush=True)
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
            write_json(selftest_path, selftest)
            print(f"timing self-test {selftest['status']}: {selftest.get('reasons')}", flush=True)
            if selftest["status"] != "PASS":
                write_json(
                    out / "CADENCE_RESULT.json",
                    {
                        "cadence": "INVALID_RUN",
                        "reason": "timing_selftest_failed",
                        "selftest": selftest,
                        "c0v2": "ON_SILICON_PIXEL_VALIDATED (untouched)",
                    },
                )
                return 2

        fmap = load_frozen(ROOT / "artifacts" / "source_activity" / "frozen_map_p3b.json")
        cache_dir = ROOT / "artifacts" / "source_activity" / "musdb18_oracle_cache"
        epoch_id = 200
        rate_rows = [ref]
        for rate in SILICON_RATE_HZ:
            cell, epoch_id = run_one_cell(
                ser=ser,
                bose=bose,
                holdout=holdout,
                fmap=fmap,
                cache_dir=cache_dir,
                dumps=dumps,
                cells_dir=cells_dir,
                rate_hz=rate,
                delay_s=0.0,
                family="rate",
                ident=ident,
                epoch_id_start=epoch_id,
                resume=resume,
            )
            rate_rows.append(cell)

        extra_rate = maybe_extra_rate(rate_rows)
        if extra_rate is not None:
            print(f"EXTRA RATE {extra_rate:g} Hz — PASS/FAIL boundary is tight", flush=True)
            cell, epoch_id = run_one_cell(
                ser=ser,
                bose=bose,
                holdout=holdout,
                fmap=fmap,
                cache_dir=cache_dir,
                dumps=dumps,
                cells_dir=cells_dir,
                rate_hz=extra_rate,
                delay_s=0.0,
                family="rate",
                ident=ident,
                epoch_id_start=epoch_id,
                resume=resume,
            )
            rate_rows.append(cell)

        delay_rate = pick_delay_test_rate(rate_rows)
        print(f"DELAY SWEEP at {delay_rate:g} Hz (cadence held fixed)", flush=True)
        delay_rows: list[dict] = []
        zero_at_rate = next(
            (r for r in rate_rows if abs(float(r["rate_hz"]) - delay_rate) < 1e-9 and float(r["delay_s"]) == 0.0),
            None,
        )
        if zero_at_rate is not None:
            copied = dict(zero_at_rate)
            copied["family"] = "delay"
            delay_rows.append(copied)

        for delay in SILICON_DELAY_S:
            if delay <= 0.0:
                continue
            if abs(delay_rate - NATIVE_HZ) < 1e-9 and delay == 0.0:
                continue
            cell, epoch_id = run_one_cell(
                ser=ser,
                bose=bose,
                holdout=holdout,
                fmap=fmap,
                cache_dir=cache_dir,
                dumps=dumps,
                cells_dir=cells_dir,
                rate_hz=delay_rate,
                delay_s=delay,
                family="delay",
                ident=ident,
                epoch_id_start=epoch_id,
                resume=resume,
            )
            delay_rows.append(cell)

        extra_delay = maybe_extra_delay(delay_rows)
        if extra_delay is not None:
            print(f"EXTRA DELAY {extra_delay*1000:.1f} ms — boundary is tight", flush=True)
            cell, epoch_id = run_one_cell(
                ser=ser,
                bose=bose,
                holdout=holdout,
                fmap=fmap,
                cache_dir=cache_dir,
                dumps=dumps,
                cells_dir=cells_dir,
                rate_hz=delay_rate,
                delay_s=extra_delay,
                family="delay",
                ident=ident,
                epoch_id_start=epoch_id,
                resume=resume,
            )
            delay_rows.append(cell)

        slow = slowest_passing_rate_hz(rate_rows)
        big = largest_passing_delay_s(delay_rows)
        corner = None
        if slow is None or big is None:
            corner = {
                "status": "NOT_RUN",
                "reason": "no jointly proposed corner; a 1-D sweep had no PASS",
                "verdict": "FAIL",
            }
        else:
            already = next(
                (
                    r
                    for r in rate_rows + delay_rows
                    if abs(float(r["rate_hz"]) - slow) < 1e-9 and abs(float(r["delay_s"]) - big) < 1e-9
                ),
                None,
            )
            if already is not None:
                corner = dict(already)
                corner["family"] = "corner"
                corner["source"] = already.get("source") or "existing_cell"
                print(
                    f"CORNER {slow:g} Hz + {big*1000:.0f} ms already captured as {already.get('family')}",
                    flush=True,
                )
            else:
                print(f"CORNER {slow:g} Hz + {big*1000:.0f} ms", flush=True)
                corner, epoch_id = run_one_cell(
                    ser=ser,
                    bose=bose,
                    holdout=holdout,
                    fmap=fmap,
                    cache_dir=cache_dir,
                    dumps=dumps,
                    cells_dir=cells_dir,
                    rate_hz=slow,
                    delay_s=big,
                    family="corner",
                    ident=ident,
                    epoch_id_start=epoch_id,
                    resume=resume,
                )
            if corner.get("verdict") != "PASS" and slow is not None:
                # Tighten once: faster rate at the same delay, or same rate at smaller delay.
                faster = sorted(
                    {float(r["rate_hz"]) for r in rate_rows if float(r["rate_hz"]) > slow and r.get("verdict") == "PASS"}
                )
                smaller = sorted(
                    {float(r["delay_s"]) for r in delay_rows if float(r["delay_s"]) < big and r.get("verdict") == "PASS"},
                    reverse=True,
                )
                tight_rate = faster[0] if faster else slow
                tight_delay = smaller[0] if smaller else 0.0
                if abs(tight_rate - slow) > 1e-9 or abs(tight_delay - big) > 1e-9:
                    print(
                        f"CORNER FAIL — tighten once to {tight_rate:g} Hz + {tight_delay*1000:.0f} ms",
                        flush=True,
                    )
                    corner2, epoch_id = run_one_cell(
                        ser=ser,
                        bose=bose,
                        holdout=holdout,
                        fmap=fmap,
                        cache_dir=cache_dir,
                        dumps=dumps,
                        cells_dir=cells_dir,
                        rate_hz=tight_rate,
                        delay_s=tight_delay,
                        family="corner",
                        ident=ident,
                        epoch_id_start=epoch_id,
                        resume=resume,
                    )
                    corner = {
                        "first": {k: v for k, v in corner.items() if k != "rows"},
                        **{k: v for k, v in corner2.items() if k != "rows"},
                        "tightened_from": {"rate_hz": slow, "delay_s": big},
                        "rows": corner2.get("rows"),
                    }

        rate_bracket = honest_rate_bracket(rate_rows)
        delay_bracket = honest_delay_bracket(delay_rows)
        corner_pass = str(corner.get("verdict")) == "PASS" if isinstance(corner, dict) else False
        contract = {
            "name": "Source Ownership Semantic Transport Contract",
            "status": "PROPOSED — silicon cadence evidence; student I/O unfrozen",
            "semantics": "four source powers/shares",
            "channels": list(SHARE_SOURCES),
            "ordering": list(SHARE_SOURCES),
            "range": {"extra_gain": [0.62, 1.0], "share": "simplex over vocals/drums/bass/other"},
            "update_rate": rate_bracket,
            "slowest_passing_rate_hz": slow,
            "added_semantic_delay": delay_bracket,
            "largest_passing_delay_s": big,
            "hold_policy": HOLD_POLICY,
            "interpolation": "none — sample-and-hold only",
            "silence": "no invented equal shares; extra_gain stays in [0.62, 1.0]; all-zero PRSM latch is not used",
            "timestamp_semantics": "device-side C0 epoch; hop_us=32000; applied PRSM recorded per rendered frame",
            "causality": "zero lookahead; hold then delay; no future samples",
            "lookahead": 0,
            "corner": {
                "rate_hz": corner.get("rate_hz") if isinstance(corner, dict) else None,
                "delay_s": corner.get("delay_s") if isinstance(corner, dict) else None,
                "verdict": corner.get("verdict") if isinstance(corner, dict) else None,
            },
            "corner_survived": corner_pass,
            "provenance": {
                "c0v2": "ON_SILICON_PIXEL_VALIDATED",
                "c0v2_receipt": str(C0V2_RECEIPT),
                "cadence_receipt": str(out / "CADENCE_RESULT.json"),
                "authorisation": "K1-C0-CADENCE-LATENCY-FLASH-GO",
            },
            "unfrozen": [
                "neural-network architecture",
                "student I/O freeze",
                "Gate C",
                "C1",
                "production Waveform Tempo",
            ],
        }
        write_contract(out, contract)

        result = {
            "authorisation": "K1-C0-CADENCE-LATENCY-FLASH-GO",
            "binding": BINDING,
            "hold_policy": HOLD_POLICY,
            "lag_corrected": False,
            "c0v2": "ON_SILICON_PIXEL_VALIDATED",
            "c0v2_q": {"Q1": C0V2_Q1, "Q2_delta": C0V2_DELTA, "wins": [9, 9]},
            "selftest": {k: selftest.get(k) for k in ("status", "integrity", "reasons", "details") if selftest},
            "identity": ident,
            "rate": {
                "cells": [{k: v for k, v in r.items() if k != "rows"} for r in rate_rows],
                "bracket": rate_bracket,
                "slowest_passing_rate_hz": slow,
            },
            "delay": {
                "test_rate_hz": delay_rate,
                "cells": [{k: v for k, v in r.items() if k != "rows"} for r in delay_rows],
                "bracket": delay_bracket,
                "largest_passing_delay_s": big,
            },
            "corner": {k: v for k, v in corner.items() if k != "rows"} if isinstance(corner, dict) else corner,
            "contract": contract,
            "gate_c": "OPEN",
            "c1": "blocked",
            "student_freeze": False,
            "new_network": False,
            "interpolation_study": "not run",
            "non_claims": [
                "C0-v2 remains ON_SILICON_PIXEL_VALIDATED",
                "Gate C still OPEN",
                "C1 not taken",
                "no student freeze",
                "no new network",
                "no product firmware change until restore",
            ],
        }
        write_json(out / "CADENCE_RESULT.json", result)
        print(
            f"CADENCE rate[{rate_bracket}] delay[{delay_bracket}] "
            f"corner={corner.get('verdict') if isinstance(corner, dict) else corner}",
            flush=True,
        )
        return 0
    finally:
        if bose is not None:
            try:
                bose.stop()
            except Exception:
                pass
        subprocess.run(["pkill", "-x", "ffplay"], check=False)
        if ser is not None:
            try:
                ser.close()
            except Exception:
                pass
            ser = None
            time.sleep(2.0)
        if not args.skip_restore:
            try:
                port = wait_port(timeout_s=15.0)
            except SystemExit:
                port = args.port or ""
            try:
                restored = restore_product(port or wait_port())
                write_json(out / "restore_identity.json", restored)
            except Exception as e:
                print(f"RESTORE ERROR: {e}", flush=True)
                raise


if __name__ == "__main__":
    raise SystemExit(main())
