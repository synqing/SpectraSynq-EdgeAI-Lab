from edgeai.mir.visual_hook import MODULATION_WEIGHT, modulate, per_song_norm


def test_modulate_weight_one_is_the_extra():
    base = [0.0, 0.2, 1.0]
    extra = [1.0, 0.5, 0.0]
    assert modulate(base, extra, weight=1.0) == extra


def test_modulate_weight_zero_is_the_base():
    base = [0.0, 0.2, 1.0]
    extra = [1.0, 0.5, 0.0]
    assert modulate(base, extra, weight=0.0) == base


def test_energy_and_oracle_share_the_same_mix():
    base = [0.1, 0.4, 0.8]
    rms = [0.2, 0.3, 0.9]
    arousal = [0.9, 0.1, 0.2]
    b = modulate(base, rms, weight=MODULATION_WEIGHT)
    c = modulate(base, arousal, weight=MODULATION_WEIGHT)
    # Same weight is the control. Different extras must be allowed to differ.
    assert b != c
    # Reconstruct weight from an interior sample.
    w = (b[2] - base[2]) / (rms[2] - base[2])
    w2 = (c[0] - base[0]) / (arousal[0] - base[0])
    assert abs(w - MODULATION_WEIGHT) < 1e-9
    assert abs(w2 - MODULATION_WEIGHT) < 1e-9


def test_per_song_norm_is_01():
    out = per_song_norm([2.0, 4.0, 6.0])
    assert out[0] == 0.0
    assert out[-1] == 1.0
    assert abs(out[1] - 0.5) < 1e-9
