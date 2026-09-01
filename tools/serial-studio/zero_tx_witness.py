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
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


WRITE_CALL = re.compile(
    r"\b(?:write|writev|pwrite|pwritev)(?:_nocancel)?\b", re.IGNORECASE
)
FD_FIELD = re.compile(r"\bF=(\d+)\b")
BYTE_FIELD = re.compile(r"\bB=(0x[0-9a-f]+|\d+)\b", re.IGNORECASE)


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


def parse_trace(trace: str, target_fds: set[int]) -> dict[str, Any]:
    event_lines = [line for line in trace.splitlines() if line.strip()]
    writes: list[dict[str, Any]] = []
    target_writes: list[dict[str, Any]] = []
    for line in event_lines:
        if not WRITE_CALL.search(line):
            continue
        fd_match = FD_FIELD.search(line)
        byte_match = BYTE_FIELD.search(line)
        event = {
            "fd": int(fd_match.group(1)) if fd_match else None,
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
    }


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
) -> dict[str, Any]:
    parsed = parse_trace(trace, set(before.values()))
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
    return {
        "schema": "spectrasynq.serial-studio.zero-tx-witness.v1",
        "observed_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "status": "PASS" if not reasons else "FAIL",
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
        "trace_sha256": hashlib.sha256(trace.encode()).hexdigest(),
        "non_claim": "This receipt proves only bounded host-to-DUT syscall egress for the named process descriptors.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pid", type=int, required=True)
    parser.add_argument("--device", action="append", required=True)
    parser.add_argument("--duration-seconds", type=int, default=60)
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
        result = subprocess.run(
            [
                "/usr/bin/fs_usage",
                "-w",
                "-f",
                "filesys",
                "-t",
                str(args.duration_seconds),
                str(args.pid),
            ],
            check=False,
            capture_output=True,
            text=True,
            timeout=args.duration_seconds + 10,
        )
        after = resolve_device_fds(args.pid, args.device)
    except (OSError, RuntimeError, subprocess.TimeoutExpired) as error:
        print(f"ZERO_TX_WITNESS=FAIL REASON={error}")
        return 2

    trace = result.stdout + result.stderr
    receipt = build_receipt(
        pid=args.pid,
        devices=args.device,
        duration_s=args.duration_seconds,
        before=before,
        after=after,
        trace=trace,
        returncode=result.returncode,
        process=process,
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
