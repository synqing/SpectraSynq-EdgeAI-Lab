"""CLI HOST probe: missing demucs → HOST-NOT-INSTALLED exit 2. No USB. No ffplay."""

from __future__ import annotations

import ast
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "demucs_host_probe.py"

# Receipt may stamp ffplay/usb False. These tokens mean a real open/fetch.
FORBIDDEN_IO = (
    "usbmodem",
    "/dev/cu",
    "/dev/tty",
    "torch.hub",
    "fbaipublicfiles",
)


def _load_probe():
    spec = importlib.util.spec_from_file_location("demucs_host_probe", SCRIPT)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_probe_script_source_has_no_usb_ffplay_or_separator() -> None:
    src = SCRIPT.read_text(encoding="utf-8")
    lower = src.lower()
    for token in FORBIDDEN_IO:
        assert token not in lower
    assert "import subprocess" not in src
    assert "import serial" not in src
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Attribute):
            attr = func.attr
        elif isinstance(func, ast.Name):
            attr = func.id
        else:
            attr = ""
        assert attr not in {
            "Popen",
            "Serial",
            "run",
            "check_output",
            "call",
            "Separator",
        }


def test_demucs_host_probe_prints_host_not_installed_and_exits_2() -> None:
    assert importlib.util.find_spec("demucs") is None
    proc = subprocess.run(
        [sys.executable, str(SCRIPT)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    text = proc.stdout + proc.stderr
    # argparse also uses exit 2; the status line is the real oracle.
    assert proc.returncode == 2, text
    lines = [ln for ln in proc.stdout.splitlines() if ln.strip()]
    assert lines, text
    assert lines[0] == "HOST-NOT-INSTALLED"
    receipt = json.loads(lines[1])
    assert receipt["status"] == "HOST-NOT-INSTALLED"
    assert receipt["label"] == "HOST-ONLY"
    assert receipt["demucs_installed"] is False
    assert receipt["named_go"] is False
    assert receipt["download"] is False
    assert receipt["separator_constructed"] is False
    assert receipt["usb"] is False
    assert receipt["ffplay"] is False
    assert receipt["titan"] is False
    lower = text.lower()
    for token in FORBIDDEN_IO:
        assert token not in lower
    assert "ffplay" not in lower.replace('"ffplay": false', "")


def test_probe_install_state_is_not_installed_without_package() -> None:
    assert importlib.util.find_spec("demucs") is None
    mod = _load_probe()
    status, code = mod.probe_install_state()
    assert status == "HOST-NOT-INSTALLED"
    assert code == mod.EXIT_NOT_INSTALLED == 2
    assert mod.demucs_package_present() is False
    assert mod.main([]) == 2
