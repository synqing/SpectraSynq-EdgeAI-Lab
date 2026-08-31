import importlib.util
import sys
import types

import numpy as np

from edgeai.mir.teachers import (
    activity_envelope,
    demucs_host_allowed,
    envelope_vs_mixture,
    hpss_stems,
    try_demucs,
)


def test_hpss_click_vs_sine_not_identical_to_mix():
    sr = 16_000
    t = np.arange(sr * 2, dtype=np.float32) / sr
    sine = 0.2 * np.sin(2 * np.pi * 440 * t).astype(np.float32)
    click = np.zeros_like(sine)
    click[:: sr // 4] = 1.0
    mix = sine + click
    stems = hpss_stems(mix, sr)
    stats = envelope_vs_mixture(stems, sr)
    # Percussive should not be a 0.99 copy of mix RMS on this fixture.
    r_p = stats["r_percussive_vs_mix_rms"]
    r_h = stats["r_harmonic_vs_mix_rms"]
    assert np.isfinite(r_p) and np.isfinite(r_h)
    assert r_p < 0.99
    assert r_h < 0.99


def test_activity_envelope_length():
    sr = 8000
    x = np.zeros(sr, dtype=np.float32)
    x[1000:1200] = 1.0
    times, env = activity_envelope(x, sr, hop=256)
    assert times.shape == env.shape
    assert env.max() == 1.0 or env.max() > 0.9


def test_demucs_host_allowed():
    # HOST-ONLY. Uninstalled package is not a download. Not Titan.
    assert importlib.util.find_spec("demucs") is None
    assert callable(demucs_host_allowed)
    assert demucs_host_allowed() is False


def test_try_demucs_none():
    # ImportError → None. Does not construct Separator. Does not fetch weights.
    assert importlib.util.find_spec("demucs") is None
    assert try_demucs() is None


def test_titan_env_refuse(monkeypatch):
    """SPECTRASYNQ_TITAN refuses even if demucs.api is present. No download."""
    constructed = {"n": 0}

    def _separator(*_a, **_k):
        constructed["n"] += 1
        raise AssertionError("Separator must not run; no weight download")

    fake_api = types.ModuleType("demucs.api")
    fake_api.Separator = _separator
    fake_pkg = types.ModuleType("demucs")
    fake_pkg.api = fake_api
    monkeypatch.setitem(sys.modules, "demucs", fake_pkg)
    monkeypatch.setitem(sys.modules, "demucs.api", fake_api)
    monkeypatch.delenv("SPECTRASYNQ_TITAN", raising=False)

    # Positive control: fake import is enough to allow a HOST handle,
    # still without constructing Separator / hitting the hub.
    assert demucs_host_allowed() is True
    handle = try_demucs()
    assert handle is not None
    assert constructed["n"] == 0

    monkeypatch.setenv("SPECTRASYNQ_TITAN", "1")
    assert demucs_host_allowed() is False
    assert try_demucs() is None
    assert constructed["n"] == 0
