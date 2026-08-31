"""HOST Demucs. SPECTRASYNQ_TITAN → not allowed. Missing package → None. No USB."""

from __future__ import annotations

import importlib.util
import inspect
import subprocess
import sys
import types

from edgeai.mir import teachers


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
