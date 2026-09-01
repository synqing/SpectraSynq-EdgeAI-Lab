#!/usr/bin/env python3
"""Independent macOS syscall witness for Serial Studio UART egress.

Run this as root while a bounded PASSIVE_OBSERVE session is active. The tool
uses Apple's kernel-backed fs_usage trace, resolves the exact UART file
descriptors before and after the trace, and fails closed on any target write or
descriptor drift. It never opens either DUT device itself.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sqlite3
import subprocess
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


WRITE_CALL = re.compile(
    r"\b(?:write|writev|pwrite|pwritev)(?:_nocancel)?\b", re.IGNORECASE
)
FD_FIELD = re.compile(r"\bF=(\d+)\b")
BYTE_FIELD = re.compile(r"\bB=(0x[0-9a-f]+|\d+)\b", re.IGNORECASE)
LIFECYCLE_CALL = re.compile(
    r"\b(open|openat|close|dup|dup2|dup3)\b", re.IGNORECASE
)


def resolve_device_fds(pid: int, devices: list[str]) -> dict[str, int]:
    resolved: dict[str, int] = {}
    for device in devices:
        result = subprocess.run(
            ["/usr/sbin/lsof", "-a", "-p", str(pid), "-Fn", "--", device],
            check=False,
            capture_output=True,
            text=True,
        )
        current_fd: int | None = None
        for line in result.stdout.splitlines():
            if line.startswith("f"):
                digits = re.match(r"f(\d+)", line)
                current_fd = int(digits.group(1)) if digits else None
            elif line == f"n{device}" and current_fd is not None:
                resolved[device] = current_fd
        if device not in resolved:
            raise RuntimeError(f"DEVICE_FD_NOT_OPEN:{device}")
    if len(set(resolved.values())) != len(resolved):
        raise RuntimeError("DEVICE_FD_COLLISION")
    return resolved


def process_identity(pid: int) -> dict[str, Any]:
    result = subprocess.run(
        ["/usr/sbin/lsof", "-a", "-p", str(pid), "-d", "txt", "-Fn"],
        check=False,
        capture_output=True,
        text=True,
    )
    candidates = [Path(line[1:]) for line in result.stdout.splitlines() if line.startswith("n")]
    executable = next(
        (path for path in candidates if path.name == "Serial-Studio-Pro"), None
    )
    if executable is None or not executable.is_file():
        raise RuntimeError("SERIAL_STUDIO_EXECUTABLE_IDENTITY_UNRESOLVED")
    return {"pid": pid, "path": str(executable), "sha256": sha256_file(executable)}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_trace(
    trace: str, target_fds: set[int], target_paths: set[str] | None = None
) -> dict[str, Any]:
    event_lines = [line for line in trace.splitlines() if line.strip()]
    writes: list[dict[str, Any]] = []
    target_writes: list[dict[str, Any]] = []
    target_lifecycle_events: list[dict[str, Any]] = []
    target_paths = target_paths or set()
    for line in event_lines:
        fd_match = FD_FIELD.search(line)
        fd = int(fd_match.group(1)) if fd_match else None
        lifecycle_match = LIFECYCLE_CALL.search(line)
        path_match = any(path in line for path in target_paths)
        if lifecycle_match and (fd in target_fds or path_match):
            target_lifecycle_events.append(
                {
                    "call": lifecycle_match.group(1).lower(),
                    "fd": fd,
                    "target_path_observed": path_match,
                    "line_sha256": hashlib.sha256(line.encode()).hexdigest(),
                }
            )
        if not WRITE_CALL.search(line):
            continue
        byte_match = BYTE_FIELD.search(line)
        event = {
            "fd": fd,
            "bytes": int(byte_match.group(1), 0) if byte_match else None,
            "line_sha256": hashlib.sha256(line.encode()).hexdigest(),
        }
        writes.append(event)
        if event["fd"] in target_fds:
            target_writes.append(event)
    return {
        "trace_event_lines": len(event_lines),
        "write_events_any_fd": len(writes),
        "target_write_events": target_writes,
        "target_write_bytes": sum(
            int(event["bytes"] or 0) for event in target_writes
        ),
        "target_descriptor_lifecycle_events": target_lifecycle_events,
    }


def historian_snapshot(database: Path) -> dict[str, Any]:
    if not database.is_file():
        raise RuntimeError(f"HISTORIAN_DATABASE_MISSING:{database}")
    with sqlite3.connect(f"file:{database}?mode=ro", uri=True, timeout=1.0) as connection:
        session = connection.execute(
            "SELECT session_id FROM sessions WHERE ended_at IS NULL "
            "ORDER BY session_id DESC LIMIT 1"
        ).fetchone()
        if session is None:
            raise RuntimeError("HISTORIAN_HAS_NO_OPEN_SESSION")
        session_id = int(session[0])
        rows = connection.execute(
            "SELECT device_id,COUNT(*),COALESCE(SUM(length(data)),0) "
            "FROM raw_bytes WHERE session_id=? GROUP BY device_id",
            (session_id,),
        ).fetchall()
    return {
        "sampled_at_unix_ms": int(time.time() * 1000),
        "session_id": session_id,
        "sources": {
            str(int(device_id)): {"raw_rows": int(count), "raw_bytes": int(size)}
            for device_id, count, size in rows
        },
    }


def historian_progress(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    sources: dict[str, Any] = {}
    for source_id in ("0", "1"):
        first = before.get("sources", {}).get(source_id, {})
        last = after.get("sources", {}).get(source_id, {})
        sources[source_id] = {
            "raw_rows_delta": int(last.get("raw_rows", 0)) - int(first.get("raw_rows", 0)),
            "raw_bytes_delta": int(last.get("raw_bytes", 0)) - int(first.get("raw_bytes", 0)),
        }
    same_session = before.get("session_id") == after.get("session_id")
    return {
        "session_id_before": before.get("session_id"),
        "session_id_after": after.get("session_id"),
        "same_open_session": same_session,
        "sources": sources,
        "progressed": same_session
        and all(item["raw_rows_delta"] > 0 and item["raw_bytes_delta"] > 0 for item in sources.values()),
    }


def historian_continuity(samples: list[dict[str, Any]]) -> dict[str, Any]:
    intervals = [
        historian_progress(before, after)
        for before, after in zip(samples, samples[1:])
    ]
    return {
        "sample_count": len(samples),
        "interval_count": len(intervals),
        "session_id": samples[0].get("session_id") if samples else None,
        "intervals": intervals,
        "continuous": len(intervals) >= 2
        and all(interval["progressed"] for interval in intervals),
    }


def run_trace_with_historian(
    pid: int, duration_s: int, database: Path, sample_interval_s: float = 5.0
) -> tuple[str, int, list[dict[str, Any]]]:
    samples = [historian_snapshot(database)]
    command = [
        "/usr/bin/fs_usage",
        "-w",
        "-f",
        "filesys",
        "-t",
        str(duration_s),
        str(pid),
    ]
    with tempfile.TemporaryFile(mode="w+", encoding="utf-8") as trace_file:
        process = subprocess.Popen(
            command,
            stdout=trace_file,
            stderr=subprocess.STDOUT,
            text=True,
        )
        deadline = time.monotonic() + duration_s + 10
        while process.poll() is None:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                process.kill()
                process.wait()
                raise subprocess.TimeoutExpired(command, duration_s + 10)
            try:
                process.wait(timeout=min(sample_interval_s, remaining))
            except subprocess.TimeoutExpired:
                samples.append(historian_snapshot(database))
        samples.append(historian_snapshot(database))
        trace_file.seek(0)
        trace = trace_file.read()
    return trace, int(process.returncode or 0), samples


def build_receipt(
    *,
    pid: int,
    devices: list[str],
    duration_s: int,
    before: dict[str, int],
    after: dict[str, int],
    trace: str,
    returncode: int,
    process: dict[str, Any] | None = None,
    historian_before: dict[str, Any] | None = None,
    historian_after: dict[str, Any] | None = None,
    historian_samples: list[dict[str, Any]] | None = None,
    require_historian_progress: bool = False,
) -> dict[str, Any]:
    parsed = parse_trace(trace, set(before.values()), set(devices))
    if historian_samples is not None:
        progress = historian_continuity(historian_samples)
        historian_ok = progress["continuous"]
    elif historian_before is not None and historian_after is not None:
        progress = historian_progress(historian_before, historian_after)
        historian_ok = progress["progressed"]
    else:
        progress = None
        historian_ok = False
    reasons: list[str] = []
    if returncode != 0:
        reasons.append(f"FS_USAGE_EXITED_NONZERO:{returncode}")
    if before != after:
        reasons.append("UART_DESCRIPTOR_DRIFT")
    if parsed["trace_event_lines"] <= 0:
        reasons.append("TRACE_COVERAGE_EMPTY")
    if parsed["write_events_any_fd"] <= 0:
        reasons.append("WRITE_SYSCALL_COVERAGE_UNPROVEN")
    if parsed["target_write_events"]:
        reasons.append("HOST_TO_DUT_WRITE_OBSERVED")
    if parsed["target_descriptor_lifecycle_events"]:
        reasons.append("UART_DESCRIPTOR_LIFECYCLE_CHURN")
    if require_historian_progress and not historian_ok:
        reasons.append("DUAL_UART_HISTORIAN_PROGRESS_UNPROVEN")
    return {
        "schema": "spectrasynq.serial-studio.zero-tx-witness.v1",
        "observed_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "status": "PASS" if not reasons else "FAIL",
        "claim": "STEADY_STATE_UART_DATA_TX=ZERO_BYTES" if not reasons else "NO_ZERO_TX_CLAIM",
        "reasons": reasons,
        "authority": "MACOS_KERNEL_SYSCALL_TRACE",
        "process": process or {"pid": pid},
        "duration_s": duration_s,
        "devices": [
            {
                "path": device,
                "fd_before": before.get(device),
                "fd_after": after.get(device),
            }
            for device in devices
        ],
        "measurement": parsed,
        "historian_progress": progress,
        "trace_sha256": hashlib.sha256(trace.encode()).hexdigest(),
        "non_claim": (
            "This receipt proves only bounded steady-state host-to-DUT data syscall egress "
            "for continuously stable named process descriptors. It does not prove absence "
            "of connect-time line-state or USB control effects."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pid", type=int, required=True)
    parser.add_argument("--device", action="append", required=True)
    parser.add_argument("--duration-seconds", type=int, default=60)
    parser.add_argument("--historian-db", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    if os.geteuid() != 0:
        print("ZERO_TX_WITNESS=BLOCKED REASON=ROOT_REQUIRED_FOR_MACOS_KERNEL_TRACE")
        return 3
    if len(args.device) != 2 or len(set(args.device)) != 2:
        print("ZERO_TX_WITNESS=FAIL REASON=EXACTLY_TWO_UNIQUE_DEVICES_REQUIRED")
        return 2
    if args.duration_seconds < 10:
        print("ZERO_TX_WITNESS=FAIL REASON=DURATION_MUST_BE_AT_LEAST_10_SECONDS")
        return 2

    try:
        process = process_identity(args.pid)
        before = resolve_device_fds(args.pid, args.device)
        trace, returncode, historian_samples = run_trace_with_historian(
            args.pid,
            args.duration_seconds,
            args.historian_db,
        )
        after = resolve_device_fds(args.pid, args.device)
    except (OSError, RuntimeError, subprocess.TimeoutExpired) as error:
        print(f"ZERO_TX_WITNESS=FAIL REASON={error}")
        return 2

    receipt = build_receipt(
        pid=args.pid,
        devices=args.device,
        duration_s=args.duration_seconds,
        before=before,
        after=after,
        trace=trace,
        returncode=returncode,
        process=process,
        historian_samples=historian_samples,
        require_historian_progress=True,
    )
    payload = json.dumps(receipt, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
        sudo_uid = os.environ.get("SUDO_UID")
        sudo_gid = os.environ.get("SUDO_GID")
        if sudo_uid and sudo_gid:
            os.chown(args.output, int(sudo_uid), int(sudo_gid))
    print(
        f"ZERO_TX_WITNESS={receipt['status']} "
        f"TARGET_WRITES={len(receipt['measurement']['target_write_events'])} "
        f"TRACE_SHA256={receipt['trace_sha256']}"
    )
    return 0 if receipt["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
