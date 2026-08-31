#!/usr/bin/env python3
"""PRE-SILICON Titan prep checklist printer.

Checks whether the host golden directory exists and whether
docs/ruhmi/COMPILE_RECEIPT.md carries the full RUHMI pin. Refuses invented
Titan latency. Does not flash, open USB, play audio, or invoke the retired
cadence silicon runner.

Always exits 0 with a PRE-SILICON report. Not ON-SILICON.

HARD FAIL SAME_SONG_LOOP_MAX_15MIN (Captain 2026-08-31): this printer
plays nothing. Cadence silicon is CLOSED.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# D9 full SHA. Short "6c5aad9" is documentation only.
RUHMI_PIN = "6c5aad901a1a41e28f6e306bfc35c44659e89502"
GHA_RUN = "33319114336"

GOLDEN_REL = Path("artifacts") / "golden"
RECEIPT_REL = Path("docs") / "ruhmi" / "COMPILE_RECEIPT.md"
WORKFLOW_REL = Path(".github") / "workflows" / "ruhmi-compile.yml"
DOCKERFILE_REL = Path("deployment") / "ra8p1" / "Dockerfile"
PREP_REL = Path("docs") / "titan" / "PREP.md"

CASE_FILES = (
    "expected_preprocessed_tensor.npy",
    "expected_int8_output.json",
    "expected_fp32_output.json",
    "input.wav",
    "metadata.json",
)

_PIN_RE = re.compile(r"RUHMI_REF(?::|=)\s*([0-9a-f]{40})")

# Silicon / audio / invented-latency flags this printer will not honour.
_BANNED_NEEDLES = (
    "--flash",
    "--skip-flash",
    "--usb",
    "--port",
    "--serial",
    "usbmodem",
    "k1-flash",
    "k1_flash",
    "/dev/cu.",
    "/dev/tty.",
    "--resume",
    "ffplay",
    "--play",
    "--bose",
    "--latency",
    "--p50",
    "--p95",
    "--p99",
    "--max-us",
    "--ms",
)

LOOKALIKES = (
    ("1 ms NPU", "PRE-SILICON hypothetical", "never measured; not U55"),
    ("~100 ms acoustic path", "HOST-ONLY PaRIRset", "not Titan mic, not algorithm latency"),
    ("50 ms added delay", "ON-SILICON K1 C0-v2 cadence (CLOSED)", "not U55"),
    ("1.33 ms host ORT/MPS", "HOST-ONLY", "not U55"),
    ("35.56 M MACs / RAM / Flash from GHA", "PRE-SILICON compiler", "not milliseconds, not Titan SRAM"),
)


@dataclass(frozen=True)
class Check:
    name: str
    present: bool
    stamp: str
    detail: str


def _banned(tokens: list[str]) -> list[str]:
    hits: list[str] = []
    for tok in tokens:
        low = tok.lower()
        if any(needle in low for needle in _BANNED_NEEDLES):
            hits.append(tok)
    return hits


def _read(path: Path) -> str | None:
    if not path.is_file():
        return None
    return path.read_text(encoding="utf-8")


def _extract_pin(text: str | None) -> str | None:
    if not text:
        return None
    m = _PIN_RE.search(text)
    return m.group(1) if m else None


def check_golden(root: Path) -> Check:
    golden = root / GOLDEN_REL
    if not golden.is_dir():
        return Check(
            name="golden_dir",
            present=False,
            stamp="HOST-MISSING",
            detail=(
                f"{GOLDEN_REL} is not a directory. Gitignored; regenerate with "
                "uv run edgeai-golden. test_vectors/smoke/ is two fixtures, "
                "not the Titan 32-set. Do not invent vectors."
            ),
        )

    cases = sorted(
        p for p in golden.iterdir() if p.is_dir() and p.name.startswith("test_")
    )
    index_path = golden / "index.json"
    index_n: int | None = None
    if index_path.is_file():
        try:
            payload = json.loads(index_path.read_text(encoding="utf-8"))
            index_n = int(payload["n"]) if "n" in payload else None
        except (OSError, json.JSONDecodeError, TypeError, ValueError, KeyError):
            index_n = None

    host_only = 0
    on_silicon_labels = 0
    complete = 0
    missing_files: list[str] = []
    for case in cases:
        files_ok = True
        for name in CASE_FILES:
            if not (case / name).is_file():
                files_ok = False
                if len(missing_files) < 8:
                    missing_files.append(f"{case.name}/{name}")
        if files_ok:
            complete += 1
        meta_path = case / "metadata.json"
        if meta_path.is_file():
            try:
                label = json.loads(meta_path.read_text(encoding="utf-8")).get("label")
            except (OSError, json.JSONDecodeError):
                label = None
            if label == "HOST-ONLY":
                host_only += 1
            elif label == "ON-SILICON":
                on_silicon_labels += 1

    bits = [
        f"{GOLDEN_REL} exists",
        f"{len(cases)} test_* dirs",
        f"{complete} complete five-file cases",
        f"index.json n={index_n!s}",
        f"{host_only} metadata label=HOST-ONLY",
    ]
    if on_silicon_labels:
        bits.append(
            f"{on_silicon_labels} metadata label=ON-SILICON "
            "(host tree label is not a board measurement)"
        )
    if missing_files:
        bits.append("missing: " + ", ".join(missing_files))
    if index_n is not None and index_n != len(cases):
        bits.append(f"index n mismatch vs {len(cases)} dirs")
    bits.append("tensors not loaded; not U55; not ON-SILICON")

    return Check(
        name="golden_dir",
        present=True,
        stamp="HOST-ONLY",
        detail="; ".join(bits),
    )


def check_pin(root: Path) -> Check:
    receipt_path = root / RECEIPT_REL
    workflow_path = root / WORKFLOW_REL
    docker_path = root / DOCKERFILE_REL
    receipt = _read(receipt_path)
    workflow = _read(workflow_path)
    docker = _read(docker_path)

    parts: list[str] = []
    ok = True

    if receipt is None:
        ok = False
        parts.append(f"{RECEIPT_REL} ABSENT")
    elif RUHMI_PIN not in receipt:
        ok = False
        parts.append(f"{RECEIPT_REL} lacks full pin {RUHMI_PIN}")
    else:
        parts.append(f"{RECEIPT_REL} has full pin")

    wf_pin = _extract_pin(workflow)
    if wf_pin is None:
        ok = False
        parts.append(f"{WORKFLOW_REL} RUHMI_REF missing")
    elif wf_pin != RUHMI_PIN:
        ok = False
        parts.append(f"{WORKFLOW_REL} RUHMI_REF={wf_pin} ≠ pin")
    else:
        parts.append("workflow RUHMI_REF matches")

    dk_pin = _extract_pin(docker)
    if dk_pin is None:
        ok = False
        parts.append(f"{DOCKERFILE_REL} RUHMI_REF missing")
    elif dk_pin != RUHMI_PIN:
        ok = False
        parts.append(f"{DOCKERFILE_REL} RUHMI_REF={dk_pin} ≠ pin")
    else:
        parts.append("Dockerfile RUHMI_REF matches")

    if receipt is not None and GHA_RUN not in receipt:
        parts.append(f"GHA {GHA_RUN} not cited in receipt (still PRE-SILICON)")

    parts.append("short 6c5aad9 is docs-only")
    parts.append("compiler RAM/Flash/MACs are not Titan latency")

    return Check(
        name="compile_receipt_pin",
        present=ok,
        stamp="PRE-SILICON",
        detail=f"{RUHMI_PIN}; " + "; ".join(parts),
    )


def refuse_invented_latency() -> Check:
    empty = "p50/p95/p99/max_us empty; achieved_update_hz empty"
    banned = "; ".join(f"{n} = {stamp} ({why})" for n, stamp, why in LOOKALIKES)
    return Check(
        name="latency",
        present=True,
        stamp="PRE-SILICON",
        detail=f"REFUSED invented Titan latency. {empty}. Lookalikes: {banned}",
    )


def refuse_flash_usb(ignored_args: list[str]) -> Check:
    extra = f" ignored argv {ignored_args!r}." if ignored_args else ""
    hits = _banned(ignored_args)
    hits_bit = f" silicon/latency needles: {hits!r}." if hits else ""
    return Check(
        name="flash_usb",
        present=True,
        stamp="PRE-SILICON",
        detail=(
            "REFUSED. This printer does not flash, open USB-CDC, glob "
            "/dev/cu.usbmodem*, or run scripts/gate_c0_cadence_silicon.py "
            f"(RETIRED, Cadence CLOSED). Extra argv is not a measurement."
            f"{extra}{hits_bit}"
        ),
    )


def _status(golden: Check, pin: Check) -> str:
    g = "PRESENT" if golden.present else "HOST-MISSING"
    p = "PRESENT" if pin.present else "ABSENT"
    golden_bit = g if g == golden.stamp else f"{g} ({golden.stamp})"
    return (
        f"PRE-SILICON. Not ON-SILICON. golden_dir={golden_bit}; "
        f"COMPILE_RECEIPT pin={p}; latency=REFUSED/empty; flash=REFUSED; "
        "usb=REFUSED. Cadence CLOSED."
    )


def _claim(golden: Check, pin: Check) -> str:
    return (
        "Host checklist only: golden tensors for a later U55 compare, and the "
        f"RUHMI pin {RUHMI_PIN} (GHA {GHA_RUN} C99). Golden={golden.stamp}. "
        "Pin check is PRE-SILICON compiler identity, not a board clock. "
        "No Titan p50/p95/p99/µs is printed. 1 ms NPU, PaRIRset ~100 ms, "
        "K1 50 ms cadence, host ORT 1.33 ms, and GHA MACs are not U55 latency. "
        "MERT/MuQ/MAEST/Demucs stay off Titan."
    )


def format_report(
    *,
    root: Path,
    golden: Check,
    pin: Check,
    latency: Check,
    flash_usb: Check,
) -> str:
    evidence = (
        f"{GOLDEN_REL} ({'dir' if golden.present else 'missing'}); "
        f"{RECEIPT_REL}; {WORKFLOW_REL} RUHMI_REF; {DOCKERFILE_REL} RUHMI_REF; "
        f"{PREP_REL}; docs/TITAN_BRINGUP.md; docs/titan/GOLDEN_TENSORS.md; "
        "this script (stdlib, no pyserial, no ffplay, no cadence runner)."
    )
    command = (
        "python scripts/titan_prep_check.py   "
        "# or: uv run python scripts/titan_prep_check.py. "
        "Cadence CLOSED. No USB. No flash. No MERA re-run. No room audio."
    )
    method_risk = (
        "Did not np.load golden tensors. Did not re-parse GHA *_metrics.txt. "
        "Did not clone ruhmi-framework-mcu. Pin match is full-SHA string "
        "presence plus workflow/Dockerfile RUHMI_REF equality. "
        f"{GOLDEN_REL} is gitignored — another clone may be HOST-MISSING. "
        "test_vectors/smoke/ is not the 32-set. Host ORT INT8 ≠ MERA INT8 "
        "≠ U55 INT8. Empty latency cells are policy, not a measured zero."
    )
    nxt = (
        "Do not invent p50/p95/µs. Do not quote compiler RAM/Flash/MACs as "
        "Titan. Keep AdaptiveAvgPool. Do not reopen Cadence. When a RA8P1 "
        f"exists, follow {PREP_REL}: BSP NPU example, then golden tensor → "
        "U55 vs expected_int8_output.json, WAV frontend, PDM last. Stamp "
        "ON-SILICON only from a flashed image. This printer is not that stamp."
    )

    lines = [
        "=== PRE-SILICON Titan prep checklist ===",
        "HARD FAIL SAME_SONG_LOOP_MAX_15MIN: this printer plays nothing.",
        "Cadence silicon CLOSED. No USB. No flash. No invented board latency.",
        "",
        "CHECKLIST",
        f"  golden_dir:           {'PRESENT' if golden.present else 'MISSING'}  [{golden.stamp}]",
        f"                        {golden.detail}",
        f"  compile_receipt_pin:  {'PRESENT' if pin.present else 'ABSENT'}  [{pin.stamp}]",
        f"                        {pin.detail}",
        f"  latency:              REFUSED  [{latency.stamp}]",
        f"                        {latency.detail}",
        f"  flash_usb:            REFUSED  [{flash_usb.stamp}]",
        f"                        {flash_usb.detail}",
        "",
        "| Field | Value |",
        "| --- | --- |",
        f"| STATUS | {_status(golden, pin)} |",
        f"| CLAIM | {_claim(golden, pin)} |",
        f"| EVIDENCE | {evidence} |",
        f"| COMMAND | {command} |",
        f"| METHOD_RISK | {method_risk} |",
        f"| NEXT | {nxt} |",
        "",
        "LATENCY CELLS (empty until ON-SILICON)",
        "  inference_p50_us:      (empty)",
        "  inference_p95_us:      (empty)",
        "  inference_p99_us:      (empty)",
        "  inference_max_us:      (empty)",
        "  achieved_update_hz:    (empty)",
        "  npu_busy:              (empty)",
        "  m85_busy:              (empty)",
        "",
        f"root: {root}",
        "label: PRE-SILICON",
        "exit: 0",
    ]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    raw = list(sys.argv[1:] if argv is None else argv)
    parser = argparse.ArgumentParser(
        prog="titan_prep_check",
        description=(
            "PRE-SILICON Titan prep checklist printer. "
            "No flash, no USB, no invented latency. Always exits 0."
        ),
        add_help=True,
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repo root (default: parent of scripts/)",
    )
    known, leftovers = parser.parse_known_args(raw)
    # Extra argv is listed, never parsed as a port, flash target, or latency.

    root = known.root.resolve()
    golden = check_golden(root)
    pin = check_pin(root)
    latency = refuse_invented_latency()
    flash_usb = refuse_flash_usb(leftovers)
    sys.stdout.write(
        format_report(
            root=root,
            golden=golden,
            pin=pin,
            latency=latency,
            flash_usb=flash_usb,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
