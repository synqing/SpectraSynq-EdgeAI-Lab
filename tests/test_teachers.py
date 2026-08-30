import numpy as np

from edgeai.mir.teachers import activity_envelope, envelope_vs_mixture, hpss_stems


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
