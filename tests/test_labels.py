import numpy as np

from edgeai.dataset import activities_from_stems, apply_gain, maybe_mute, stem_rms


def test_muted_stem_is_zero_activity():
    n = 16000
    t = np.linspace(0, 1, n, dtype=np.float32)
    vocals = np.sin(2 * np.pi * 220 * t).astype(np.float32) * 0.4
    drums = np.zeros(n, dtype=np.float32)
    bass = np.sin(2 * np.pi * 55 * t).astype(np.float32) * 0.4
    stems = {
        "vocals": maybe_mute(vocals, True),
        "drums": drums,
        "bass": bass,
        "other": np.zeros(n, dtype=np.float32),
    }
    act = activities_from_stems(stems)
    assert act[0] == 0.0  # vocals muted
    assert act[1] == 0.0  # drums silent
    assert act[2] > 0.5  # bass present


def test_gain_changes_rms():
    x = np.ones(1000, dtype=np.float32) * 0.1
    loud = apply_gain(x, 6.0)
    assert stem_rms(loud) > stem_rms(x)
