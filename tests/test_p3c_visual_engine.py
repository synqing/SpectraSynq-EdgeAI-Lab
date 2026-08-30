"""P3-C: isolated host replay of actual K1 visual behaviour.

These tests must go RED if we fall back to the P3-B scalar stand-in,
if PHOTONS is a no-op, if holdout is oracle-ranked, or if the HTML leaks labels.
"""

from __future__ import annotations

import json

import numpy as np
import pytest

from edgeai.mir.k1_photons import PHOTONS_CURVE_MODE, apply_photons, photons_curve
from edgeai.mir.k1_visual_hooks import DEFAULT_HOOK_CONFIG, VisualHooks
from edgeai.mir.p3c_blind import permute_conditions, sealed_key, version_labels
from edgeai.mir.p3c_sets import challenge_ten, holdout_ten
from edgeai.mir.trigger_budget import local_peaks, match_thresholds


def test_photons_curve_is_shipping_quadratic():
    # constants.h: PHOTONS_CURVE_MODE 0 → PHOTONS²
    assert PHOTONS_CURVE_MODE == 0
    assert photons_curve(0.0) == 0.0
    assert photons_curve(1.0) == pytest.approx(1.0)
    assert photons_curve(0.5) == pytest.approx(0.25)


def test_apply_photons_scales_leds_and_is_not_a_noop():
    leds = np.full((3, 160, 3), 200, dtype=np.uint8)
    dark = apply_photons(leds, np.array([0.25, 0.25, 0.25]))
    bright = apply_photons(leds, np.array([1.0, 1.0, 1.0]))
    assert dark.dtype == np.uint8
    assert dark.shape == (3, 160, 3)
    assert int(dark.mean()) < int(bright.mean())
    assert np.array_equal(bright[0], leds[0])


def test_apply_photons_is_per_frame_not_clip_constant():
    leds = np.full((4, 160, 3), 180, dtype=np.uint8)
    p = np.array([0.2, 0.8, 0.2, 0.8])
    out = apply_photons(leds, p)
    assert int(out[0].mean()) < int(out[1].mean())
    assert int(out[2].mean()) < int(out[3].mean())


def test_visual_hooks_idle_scalar_is_one():
    h = VisualHooks(DEFAULT_HOOK_CONFIG)
    out = h.tick(now_ms=10, onset=False, onset_strength=0.0, event_id=0, event_age_ms=0)
    assert out.photon_scalar == pytest.approx(1.0)


def test_visual_hooks_onset_matches_firmware_gain():
    h = VisualHooks(DEFAULT_HOOK_CONFIG)
    out = h.tick(
        now_ms=10,
        onset=True,
        onset_strength=1.0,
        event_id=1,
        event_age_ms=0,
    )
    # 1 + 1.0 * 0.16 = 1.16
    assert out.photon_scalar == pytest.approx(1.16, abs=1e-6)


def test_visual_hooks_decay_clears_after_one_tau():
    h = VisualHooks(DEFAULT_HOOK_CONFIG)
    h.tick(now_ms=10, onset=True, onset_strength=1.0, event_id=1, event_age_ms=0)
    later = h.tick(now_ms=10 + 100, onset=False, onset_strength=0.0, event_id=1, event_age_ms=100)
    assert later.photon_scalar == pytest.approx(1.0, abs=1e-4)


def test_visual_hooks_same_event_id_does_not_retrigger():
    h = VisualHooks(DEFAULT_HOOK_CONFIG)
    a = h.tick(now_ms=10, onset=True, onset_strength=1.0, event_id=7, event_age_ms=0)
    b = h.tick(now_ms=20, onset=True, onset_strength=1.0, event_id=7, event_age_ms=10)
    assert a.photon_scalar == pytest.approx(1.16)
    assert b.photon_scalar < a.photon_scalar  # decaying, not re-armed


def test_local_peaks_respect_refractory():
    x = np.array([0, 0, 1, 0, 1, 0, 0], dtype=np.float64)
    ev = local_peaks(x, thresh=0.5, refractory=3)
    assert ev == [2]


def test_match_thresholds_equalises_event_counts():
    rng = np.random.default_rng(0)
    loud = rng.random(2000) ** 2
    rare = rng.random(2000) ** 6
    ta, tb, na, nb = match_thresholds(loud, rare, hop_s=0.032, refractory_s=0.25)
    assert na > 0 and nb > 0
    # Within 25% — quantity must not decide the taste test.
    assert abs(na - nb) / max(na, nb) < 0.25


def test_holdout_is_test_partition_and_not_oracle_ranked():
    challenge = [
        {"track": "Actions - Devil's Words", "subset": "train", "select_class": "vocals_ownership_change", "t": 10.0},
        {"track": "Bobby Nobody - Stitch Up", "subset": "test", "select_class": "composition_without_loudness", "t": 1.0},
    ]
    test_tracks = [
        {"track": "Al James - Schoolboy Facination", "subset": "test", "duration_s": 180.0},
        {"track": "AM Contra - Heart Peripheral", "subset": "test", "duration_s": 200.0},
        {"track": "Angels In Amplifiers - I'm Alright", "subset": "test", "duration_s": 210.0},
        {"track": "Arise - Run Run Run", "subset": "test", "duration_s": 190.0},
        {"track": "Ben Carrigan - We'll Talk About It All Tonight", "subset": "test", "duration_s": 240.0},
        {"track": "BKS - Bulldozer", "subset": "test", "duration_s": 175.0},
        {"track": "BKS - Too Much", "subset": "test", "duration_s": 160.0},
        {"track": "Buitraker - Revo X", "subset": "test", "duration_s": 155.0},
        {"track": "Carlos Gonzalez - A Place For Us", "subset": "test", "duration_s": 230.0},
        {"track": "Cristina Vane - So Easy", "subset": "test", "duration_s": 170.0},
        {"track": "Bobby Nobody - Stitch Up", "subset": "test", "duration_s": 140.0},
        {"track": "Hollow Ground - Ill Fate", "subset": "test", "duration_s": 250.0},
    ]
    held = holdout_ten(test_tracks, challenge, n=10, seed=20260831)
    names = {r["track"] for r in held}
    assert "Bobby Nobody - Stitch Up" not in names
    assert all(r["subset"] == "test" for r in held)
    assert len(held) == 10
    assert all("select_class" not in r for r in held)
    assert all(r.get("ranked_by") == "duration_quartile+name" for r in held)


def test_challenge_ten_is_balanced_not_the_whole_twenty():
    selected = []
    classes = (
        "vocals_ownership_change",
        "drums_ownership_change",
        "bass_dominance",
        "composition_without_loudness",
        "loudness_without_composition",
    )
    for cls in classes:
        for i in range(4):
            selected.append({"track": f"{cls}-{i}", "select_class": cls, "t": float(i), "source": "vocals"})
    ten = challenge_ten(selected, k_per=2)
    assert len(ten) == 10
    from collections import Counter

    counts = Counter(r["select_class"] for r in ten)
    assert set(counts) == set(classes)
    assert set(counts.values()) == {2}


def test_blinding_hides_condition_names():
    order, key = permute_conditions(("A", "B", "D"), clip_id="clip-1", salt="p3c-v1")
    assert set(order) == {"A", "B", "D"}
    labels = version_labels(order)
    assert labels == ["Version 1", "Version 2", "Version 3"]
    dumped = json.dumps(key)
    assert "Version 1" in dumped
    # The public labels must not be the engine names.
    assert labels[0] != order[0] or labels[1] != order[1]  # permutation may identity; key still sealed
    sealed = sealed_key({"clip-1": key})
    assert "A" in json.dumps(sealed)


def test_blind_html_must_not_name_engines_on_versions():
    from edgeai.mir.p3c_html import forbidden_version_leaks, scan_blind_html

    html = """
    <h1>P3-C1 visual engine</h1>
    <div class="ver">Version 1</div>
    <div class="ver">Version 2</div>
    <div class="ver">Version 3</div>
    """
    leaks = scan_blind_html(html)
    assert leaks == []
    dirty = html + "<div class='ver'>Version 1 · ownership / SHARE</div>"
    assert scan_blind_html(dirty)
    assert "SHARE" in forbidden_version_leaks()


def test_continuous_photons_share_the_same_mix_weight():
    from edgeai.mir.visual_hook import MODULATION_WEIGHT, modulate

    base = [0.675, 0.675, 0.675]
    rms = [0.1, 0.5, 0.9]
    share = [0.9, 0.2, 0.1]
    b = modulate(base, rms, weight=MODULATION_WEIGHT)
    d = modulate(base, share, weight=MODULATION_WEIGHT)
    w_b = (b[2] - base[2]) / (rms[2] - base[2])
    w_d = (d[0] - base[0]) / (share[0] - base[0])
    assert abs(w_b - MODULATION_WEIGHT) < 1e-9
    assert abs(w_d - MODULATION_WEIGHT) < 1e-9
    assert b != d


def test_host_chroma_is_causal_and_hop_aligned():
    from edgeai.mir.host_chroma import host_chroma12

    sr, hop = 16_000, 512
    n = sr * 2
    t = np.arange(n) / sr
    y = np.sin(2 * np.pi * 440.0 * t).astype(np.float32)
    times, chroma = host_chroma12(y, sr=sr, hop=hop)
    oracle_times = ((np.arange(len(times)) * hop) + hop * 0.5) / sr
    assert np.allclose(times, oracle_times, atol=1e-6)
    assert chroma.shape[1] == 12
    assert chroma.shape[0] == len(times)
    # A4 (440 Hz) should dominate pitch class 9 (A).
    assert int(np.argmax(chroma[len(chroma) // 2])) == 9
    # Not an L1 simplex — bloom squares bin values, so 0.08-range chroma renders black.
    assert float(np.max(chroma[len(chroma) // 2])) > 0.5
    noise = (0.35 * np.random.default_rng(0).normal(size=n)).astype(np.float32)
    _, cn = host_chroma12(noise, sr=sr, hop=hop)
    assert float(np.mean(cn.sum(axis=1))) > 1.2


def test_bloom_chromagram_is_broadband_enough_to_light():
    from edgeai.mir.host_chroma import bloom_chromagram

    sparse = np.zeros((4, 12), dtype=np.float32)
    sparse[:, 9] = 0.4
    mix = np.array([1.0, 1.0, 0.0, 0.2], dtype=np.float32)
    d = bloom_chromagram(sparse, mix)
    assert d.shape == (4, 12)
    assert float(d[0].min()) >= 0.6  # floor on a loud frame
    assert float(d[0, 9]) > float(d[0, 0])
    assert float(d[2].max()) < 0.2  # silence stays dim
