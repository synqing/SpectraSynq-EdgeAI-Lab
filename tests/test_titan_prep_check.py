"""PRE-SILICON titan_prep_check printer. Exit 0. No USB. No invented latency."""

from __future__ import annotations

import ast
import re
import subprocess
import sys
from pathlib import Path
from types import CodeType

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "titan_prep_check.py"

EMPTY_CELLS = (
    "inference_p50_us",
    "inference_p95_us",
    "inference_p99_us",
    "inference_max_us",
    "achieved_update_hz",
    "npu_busy",
    "m85_busy",
)

# Names that would mean this printer opened a board, a port, or a player.
BANNED_CODE_NAMES = (
    "serial",
    "glob",
    "subprocess",
    "Popen",
    "Serial",
    "ffplay",
    "usbmodem",
    "termios",
    "fcntl",
    "socket",
    "k1_flash",
)

FORBIDDEN_CALLS = {"open", "glob", "Popen", "Serial", "listdir", "iglob"}

LEFTOVER_SILICON = (
    "--flash",
    "--skip-flash",
    "--usb",
    "--serial",
    "--port",
    "not-a-tty",
    "--resume",
    "--play",
    "--bose",
    "--latency",
    "--p50",
    "1330",
    "--p95",
    "2000",
    "--p99",
    "3000",
    "--max-us",
    "4000",
)


def _run(*extra: str, root: Path | None = None) -> subprocess.CompletedProcess[str]:
    cmd = [sys.executable, str(SCRIPT)]
    if root is not None:
        cmd.extend(["--root", str(root)])
    cmd.extend(extra)
    return subprocess.run(
        cmd,
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )


def _code_names(code: CodeType) -> set[str]:
    names: set[str] = set()
    stack: list[CodeType] = [code]
    while stack:
        cur = stack.pop()
        names.update(cur.co_names)
        stack.extend(c for c in cur.co_consts if isinstance(c, CodeType))
    return names


def _assert_prep_contract(proc: subprocess.CompletedProcess[str]) -> str:
    out = proc.stdout
    assert proc.returncode == 0, proc.stderr
    assert proc.stderr == ""
    assert "label: PRE-SILICON" in out
    assert "PRE-SILICON. Not ON-SILICON." in out
    assert "latency=REFUSED/empty" in out
    assert "flash=REFUSED" in out
    assert "usb=REFUSED" in out
    assert "Cadence CLOSED" in out
    assert "REFUSED invented Titan latency" in out
    assert "does not flash, open USB-CDC" in out
    assert "gate_c0_cadence_silicon.py" in out
    assert "RETIRED" in out
    assert "exit: 0" in out
    for cell in EMPTY_CELLS:
        match = re.search(rf"^\s*{re.escape(cell)}:\s+(\S+)\s*$", out, re.M)
        assert match is not None, cell
        assert match.group(1) == "(empty)", (cell, match.group(1))
    return out


def test_titan_prep_check_exits_0_pre_silicon() -> None:
    proc = _run()
    out = _assert_prep_contract(proc)
    assert "=== PRE-SILICON Titan prep checklist ===" in out
    assert "this printer plays nothing" in out
    assert "compile_receipt_pin:" in out and "PRESENT" in out
    assert "1 ms NPU = PRE-SILICON hypothetical" in out
    assert "~100 ms acoustic path = HOST-ONLY PaRIRset" in out
    assert "50 ms added delay = ON-SILICON K1 C0-v2 cadence (CLOSED)" in out
    assert "MERT/MuQ/MAEST/Demucs stay off Titan" in out
    assert "stdlib, no pyserial, no ffplay, no cadence runner" in out


def test_titan_prep_check_leftovers_do_not_invent_latency_or_open_usb() -> None:
    proc = _run(*LEFTOVER_SILICON)
    out = _assert_prep_contract(proc)
    assert "ignored argv" in out
    assert "silicon/latency needles:" in out
    assert "Extra argv is not a measurement" in out
    # Leftover 1330/2000/3000/4000 must not land in latency cells.
    for cell in EMPTY_CELLS:
        assert re.search(rf"^\s*{re.escape(cell)}:\s+\d", out, re.M) is None
    assert "inference_p50_us:      (empty)" in out


def test_titan_prep_check_missing_root_still_pre_silicon(tmp_path: Path) -> None:
    proc = _run(root=tmp_path)
    out = _assert_prep_contract(proc)
    assert "HOST-MISSING" in out
    assert "golden_dir:" in out
    assert "ABSENT" in out
    assert "label: ON-SILICON" not in out


def test_titan_prep_check_source_does_not_open_usbmodem() -> None:
    src = SCRIPT.read_text(encoding="utf-8")
    tree = ast.parse(src)
    imports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.append(node.module.split(".")[0])
        elif isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name):
                attr = func.id
            elif isinstance(func, ast.Attribute):
                attr = func.attr
            else:
                attr = ""
            assert attr not in FORBIDDEN_CALLS, attr
            assert attr not in {"run", "check_output", "call", "Popen"}
    for banned in ("serial", "glob", "subprocess", "socket", "termios"):
        assert banned not in imports, banned

    names = _code_names(compile(src, str(SCRIPT), "exec"))
    for banned in BANNED_CODE_NAMES:
        assert banned not in names, banned

    # Refuse-string names usbmodem; that is not an open of a CDC device.
    assert "/dev/cu.usbmodem*" in src
    assert "does not flash, open USB-CDC" in src
    assert "import serial" not in src
    assert "from serial" not in src
    assert "serial.Serial" not in src
    assert "scripts/gate_c0_cadence_silicon.py" in src
    assert "Cadence CLOSED" in src
