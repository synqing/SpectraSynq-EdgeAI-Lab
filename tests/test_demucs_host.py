"""HOST Demucs. SPECTRASYNQ_TITAN → not allowed. Missing package → None. No USB."""

from __future__ import annotations

import importlib.util
import inspect
import json
import subprocess
import sys
import types
from pathlib import Path

import numpy as np
import pytest

from edgeai.mir import teachers

ROOT = Path(__file__).resolve().parents[1]
J2_RECEIPT = ROOT / "docs/mir/receipts/demucs/J2_LOCAL_LOAD.json"


def _install_fake_demucs(monkeypatch) -> None:
    """Make `import demucs.api` succeed without the real package or a hub fetch."""
    fake_api = types.ModuleType("demucs.api")
    fake_pkg = types.ModuleType("demucs")
    fake_pkg.api = fake_api
    monkeypatch.setitem(sys.modules, "demucs", fake_pkg)
    monkeypatch.setitem(sys.modules, "demucs.api", fake_api)


def test_try_demucs_none_without_package(monkeypatch) -> None:
    monkeypatch.delenv("SPECTRASYNQ_TITAN", raising=False)
    assert importlib.util.find_spec("demucs") is None
    assert teachers.try_demucs() is None


def test_demucs_host_allowed_false_when_titan_set(monkeypatch) -> None:
    # Fake import so False cannot be ImportError in disguise.
    _install_fake_demucs(monkeypatch)
    monkeypatch.delenv("SPECTRASYNQ_TITAN", raising=False)
    assert teachers.demucs_host_allowed() is True

    monkeypatch.setenv("SPECTRASYNQ_TITAN", "1")
    assert teachers.demucs_host_allowed() is False
    assert teachers.try_demucs() is None


def test_demucs_host_opens_no_usb(monkeypatch) -> None:
    def _forbid(name: str):
        def _inner(*_a, **_k):
            raise AssertionError(f"{name} must not run in demucs HOST tests")

        return _inner

    monkeypatch.setattr(subprocess, "Popen", _forbid("subprocess.Popen"))
    monkeypatch.setattr(subprocess, "run", _forbid("subprocess.run"))
    monkeypatch.setattr(subprocess, "call", _forbid("subprocess.call"))
    monkeypatch.setattr(subprocess, "check_output", _forbid("subprocess.check_output"))

    src = (
        inspect.getsource(teachers.demucs_host_allowed)
        + inspect.getsource(teachers.try_demucs)
    ).lower()
    assert "usbmodem" not in src
    assert "/dev/cu" not in src
    assert "/dev/tty" not in src
    assert "ffplay" not in src
    assert "serial.serial" not in src

    monkeypatch.delenv("SPECTRASYNQ_TITAN", raising=False)
    assert teachers.try_demucs() is None
    monkeypatch.setenv("SPECTRASYNQ_TITAN", "1")
    assert teachers.demucs_host_allowed() is False


def test_j5_no_go_still_refuses_after_useful_local_load(monkeypatch) -> None:
    receipt = json.loads(J2_RECEIPT.read_text(encoding="utf-8"))
    assert receipt["verdict"] == "LOCAL_CHECKPOINT_LOAD_PASS"
    assert receipt["network_fetch"] is False

    _install_fake_demucs(monkeypatch)
    monkeypatch.delenv("SPECTRASYNQ_TITAN", raising=False)
    monkeypatch.delenv("SPECTRASYNQ_DEMUCS_NAMED_GO", raising=False)
    handle = teachers.try_demucs()
    assert handle is not None
    with pytest.raises(RuntimeError, match="not constructing Separator"):
        handle.separate(np.zeros(32, dtype=np.float32), 44_100)


def test_j5_titan_still_refuses_after_useful_local_load(monkeypatch) -> None:
    receipt = json.loads(J2_RECEIPT.read_text(encoding="utf-8"))
    assert receipt["model_constructed"] is True
    _install_fake_demucs(monkeypatch)
    monkeypatch.setenv("SPECTRASYNQ_TITAN", "1")
    monkeypatch.setenv("SPECTRASYNQ_DEMUCS_NAMED_GO", "D26_HOST_BLITZ_2026-09-01")
    assert teachers.demucs_host_allowed() is False
    assert teachers.try_demucs() is None
