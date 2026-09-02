"""J3G - deterministic unit fixtures for the same-STFT tonal projections.

The phantom-triad fixture is PERMANENT: J3F Q0b showed the current frontend
deposits a major-triad-plus-seventh pattern for a single note, and any future
change to the tonal frontend must show what it does to that pattern - including
what it does to a REAL triad, so nobody 'fixes' single notes by destroying chords.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from edgeai.mir import tonal_projection as tp
from edgeai.mir.host_chroma import host_chroma12

SR = 16_000


def tone(midi: float, harmonics: int, dur: float = 3.0) -> np.ndarray:
    f = 440.0 * 2.0 ** ((midi - 69.0) / 12.0)
    t = np.arange(int(SR * dur), dtype=np.float64) / SR
    return sum((1.0 / h) * np.sin(2.0 * np.pi * h * f * t) for h in range(1, harmonics + 1))


def states(y: np.ndarray, winner: str = "P0_CURRENT") -> dict:
    st = tp.stft_power(y)
    pcp = tp.pitch_class_power_from_stft(st)
    out = {"P0_CURRENT": tp.l1(tp.post_P0(pcp)),
           "P1_POWER_L1": tp.l1(tp.post_P1(pcp)),
           "P2_SQRT_L1_NO_CLIP": tp.l1(tp.post_P2(pcp)),
           "C1_SOFT_FILTERBANK": tp.l1(tp.apply_carry_forward(tp.c1_soft_chroma(st), native_domain="power", winner=winner)),
           "C2_PEAK_HPCP": tp.l1(tp.apply_carry_forward(tp.c2_peak_hpcp(st), native_domain="power", winner=winner)),
           "C3_ROOT_SALIENCE": tp.l1(tp.apply_carry_forward(tp.c3_root_salience(st), native_domain="amplitude", winner=winner))}
    out["C4_CRP"] = tp.l1(tp.c4_crp_chroma(st)["chroma"])
    return {k: v[v.shape[0] // 2] for k, v in out.items()}


ALL = ["P0_CURRENT", "P1_POWER_L1", "P2_SQRT_L1_NO_CLIP", "C1_SOFT_FILTERBANK",
       "C2_PEAK_HPCP", "C3_ROOT_SALIENCE", "C4_CRP"]


# ---------------------------------------------------------------- controls
def test_shared_framing_is_host_chroma12_framing():
    y = 0.2 * tone(60, 4, dur=2.0)
    assert tp.assert_frames_match_host_chroma12(y) == 0.0


def test_P0_reproduces_host_chroma12():
    """The object under test must survive being routed through the shared STFT."""
    rng = np.random.default_rng(0)
    y = 0.2 * tone(57, 6, dur=2.0) + 0.01 * rng.standard_normal(int(SR * 2.0))
    _, ref = host_chroma12(y.astype(np.float32))
    st = tp.stft_power(y)
    got = tp.post_P0(tp.pitch_class_power_from_stft(st))
    n = min(len(ref), len(got))
    assert np.max(np.abs(ref[:n].astype(np.float64) - got[:n])) <= 1e-5


def test_reference_divisor_cancels_under_l1_and_clip_is_inactive():
    """P0 and P2 differ only by a constant scale and a clip that never fires here."""
    y = 0.2 * tone(64, 8, dur=2.0)
    s = states(y)
    assert np.max(np.abs(s["P0_CURRENT"] - s["P2_SQRT_L1_NO_CLIP"])) < 1e-9


@pytest.mark.parametrize("name", ALL)
def test_every_candidate_is_non_negative_and_l1(name):
    s = states(0.2 * tone(60, 8, dur=2.0))[name]
    assert s.shape == (12,)
    assert (s >= 0.0).all()
    assert abs(float(s.sum()) - 1.0) < 1e-9


# ------------------------------------------------- phantom-triad fixture
def test_pure_sine_puts_its_mass_on_its_own_pitch_class():
    s = states(0.2 * tone(60, 1, dur=2.0))
    for name, v in s.items():
        assert int(np.argmax(v)) == 0, f"{name} lost a pure sine"


def test_single_note_leakage_is_recorded_not_asserted_to_zero():
    """J3F Q0b: ONE note already deposits root + fifth + third. Zero leakage is
    NOT required; the fixture exists so every candidate's pattern is visible."""
    s = states(0.2 * tone(60, 8, dur=2.0))
    for name, v in s.items():
        assert int(np.argmax(v)) == 0, f"{name} does not put a single note's peak on its root"
        assert v[7] > 0.0 or v[4] > 0.0 or name == "C2_PEAK_HPCP", f"{name} unexpectedly leak-free"


def test_C2_is_the_cleanest_projection_on_a_single_note():
    """Recorded behaviour, not a target: peak-only voting suppresses broadband mass."""
    s = states(0.2 * tone(60, 8, dur=2.0))
    assert 1.0 - s["C2_PEAK_HPCP"][0] < 1.0 - s["P0_CURRENT"][0]


def test_no_candidate_destroys_a_real_major_triad():
    """The Captain's anti-gaming clause: chord-tone mass must stay within 0.70 of
    the current frontend's. C1_SOFT_FILTERBANK fails this and is excluded."""
    s = states(0.2 * (tone(60, 8) + tone(64, 8) + tone(67, 8)))
    tones = [0, 4, 7]
    p0 = float(sum(s["P0_CURRENT"][t] for t in tones))
    for name in ("C2_PEAK_HPCP", "C3_ROOT_SALIENCE", "C4_CRP"):
        assert float(sum(s[name][t] for t in tones)) >= 0.70 * p0, f"{name} collapses a real triad"
    assert float(sum(s["C1_SOFT_FILTERBANK"][t] for t in tones)) < 0.70 * p0


def test_two_note_fifth_keeps_both_notes():
    s = states(0.2 * (tone(60, 8) + tone(67, 8)))
    for name in ("P0_CURRENT", "C2_PEAK_HPCP", "C3_ROOT_SALIENCE"):
        top2 = set(np.argsort(-s[name])[:2].tolist())
        assert top2 == {0, 7}, f"{name} lost one voice of a fifth: {top2}"


# --------------------------------------------------- documented properties
def test_C3_octave_gate_is_not_degenerate():
    """The first pre-registered form, S * odd_frac, reduced identically to odd_sum
    and silently discarded every even harmonic. The gate must saturate at 1 so a
    clean fundamental keeps its FULL harmonic sum."""
    st = tp.stft_power(0.2 * tone(60, 8, dur=2.0))
    gated = tp.c3_root_salience(st)
    assert tp.C3_RHO == pytest.approx(0.767, abs=1e-3)
    assert gated.sum() > 0.0
    # a pure sine has no odd harmonics above h=1, so the gate must still pass it
    sine = tp.c3_root_salience(tp.stft_power(0.2 * tone(60, 1, dur=2.0)))
    assert int(np.argmax(sine[sine.shape[0] // 2])) == 0


def test_C4_rectification_discards_exactly_half_the_mass():
    """Zeroing DCT coefficient 0 removes the mean by construction, so positive and
    negative mass are exactly equal. C4 as implemented is NOT a faithful CRP test
    and this test exists so that stays visible."""
    st = tp.stft_power(0.2 * tone(60, 8, dur=2.0))
    assert tp.c4_crp_chroma(st)["rectified_mass_fraction"] == pytest.approx(0.5, abs=1e-3)


def test_declared_constants_are_the_pre_registered_ones():
    assert (tp.SR, tp.N_FFT, tp.HOP) == (16_000, 2048, 512)
    assert tp.C1_SIGMA_SEMITONES == 0.55
    assert tp.C2_DELTA_SEMITONES == pytest.approx(2.0 / 3.0)
    assert tp.C2_N_HARMONICS == 1
    assert (tp.C3_MIDI_LOW, tp.C3_MIDI_HIGH, tp.C3_H) == (28, 96, 8)
    assert (tp.C4_MIDI_LOW, tp.C4_MIDI_HIGH, tp.C4_LOG_C, tp.C4_DCT_CUTOFF) == (28, 96, 1000.0, 32)


# ------------------------------------------------- J3G.2 peak-to-root hybrid
def hybrid(y: np.ndarray) -> np.ndarray:
    st = tp.stft_power(y)
    v = tp.l1(tp.apply_carry_forward(tp.c5_peak_root(st), native_domain="amplitude", winner="P0_CURRENT"))
    return v[v.shape[0] // 2]


def test_hybrid_meets_all_four_stated_fixture_requirements():
    """The Captain's blocking set for J3G.2: fifth preserved, triad preserved,
    not root-only, no gross phantom-chord mass."""
    p0_triad = states(0.2 * (tone(60, 8) + tone(64, 8) + tone(67, 8)))["P0_CURRENT"]
    fifth = hybrid(0.2 * (tone(60, 8) + tone(67, 8)))
    triad = hybrid(0.2 * (tone(60, 8) + tone(64, 8) + tone(67, 8)))
    note = hybrid(0.2 * tone(60, 8))
    assert sorted(np.argsort(-fifth)[:2].tolist()) == [0, 7]
    assert min(fifth[0], fifth[7]) / max(fifth[0], fifth[7]) >= 0.50
    assert sorted(np.argsort(-triad)[:3].tolist()) == [0, 4, 7]
    assert float(triad[[0, 4, 7]].sum()) >= 0.70 * float(p0_triad[[0, 4, 7]].sum())
    assert min(triad[[0, 4, 7]]) / max(triad[[0, 4, 7]]) >= 0.50
    for v, tones in ((note, [0]), (fifth, [0, 7]), (triad, [0, 4, 7])):
        assert max(v[j] for j in range(12) if j not in tones) <= 0.25


def test_hybrid_removes_the_mainlobe_leakage_candidates_C3_accumulated():
    """The mechanism the hybrid was built to test: semitone-adjacent classes fed
    only by the Hann mainlobe skirt have no local maximum, so they vote nothing."""
    h = hybrid(0.2 * tone(60, 8))
    c3 = states(0.2 * tone(60, 8))["C3_ROOT_SALIENCE"]
    assert h[1] == 0.0 and h[11] == 0.0          # C# and B
    assert c3[1] > 0.0 and c3[11] > 0.0
    assert h[0] > c3[0]


def test_hybrid_retains_the_subharmonic_ambiguity_documented_not_repaired():
    """A real peak at f0 IS an odd harmonic of f0/3 and f0/5, so the odd-harmonic
    gate cannot suppress them. Recorded so the limitation stays visible."""
    h = hybrid(0.2 * tone(60, 8))
    assert h[5] > 0.05, "f0/3 subharmonic (F) should still carry mass"
    assert 1.0 - h[0] > 1.0 - states(0.2 * tone(60, 8))["P0_CURRENT"][0]


def test_hybrid_gate_constant_is_the_analytic_one():
    assert tp.C5_RHO == pytest.approx(0.767, abs=1e-3)
    assert (tp.C5_MIDI_LOW, tp.C5_MIDI_HIGH, tp.C5_H) == (28, 96, 8)
    assert tp.C5_HALF_WIDTH_SEMITONES == 0.5


def test_hybrid_uses_exactly_C2s_peak_set():
    """Shared code, not a reimplementation - the hypothesis is about the evidence
    source only, so the peaks must be bit-identical to C2's."""
    st = tp.stft_power(0.2 * (tone(60, 8) + tone(67, 8)))
    a, b = tp._peaks(st), tp._peaks(st)
    assert np.array_equal(a["rows"], b["rows"]) and np.array_equal(a["freq"], b["freq"])
    assert tp.C2_PEAK_REL_THRESHOLD == 0.01


# ------------------------------------------- J3J acoustic-activation target
def test_identity_kernel_reproduces_the_rectangular_target_exactly():
    """The activation state must be a strict generalisation of pitch_class_state."""
    from edgeai.mir.acoustic_activation import K_MAX_HOPS, acoustic_activation_state
    from edgeai.mir.harmonic_movement import Note, pitch_class_state
    notes = [Note(0.5, 2.0, 60, 80), Note(1.0, 2.5, 64, 90), Note(3.0, 4.0, 67, 70)]
    a = acoustic_activation_state(notes, 200, np.ones(K_MAX_HOPS + 1))
    b = pitch_class_state(notes, 200)
    assert np.max(np.abs(a["pc_mass"] - b["pc_mass"])) == 0.0


def test_attack_kernel_is_monotone_and_reaches_one():
    from edgeai.mir.acoustic_activation import K_MAX_HOPS, episode_curve, kernel_from_curves
    env = np.concatenate([np.linspace(0.0, 1.0, 12), np.full(40, 1.0)])
    c = episode_curve(env, 0, 52, 1.0)
    assert c is not None and c.size == K_MAX_HOPS + 1
    assert np.all(np.diff(c) >= -1e-12)
    k = kernel_from_curves([c, c])
    assert k[-1] == pytest.approx(1.0)
    assert np.all(np.diff(k) >= -1e-12)


def test_running_max_prevents_tremolo_being_modelled_as_deactivation():
    from edgeai.mir.acoustic_activation import episode_curve
    env = np.array([0.2, 0.9, 0.3, 1.0] + [1.0] * 40)
    c = episode_curve(env, 0, 44, 1.0)
    assert c[1] == pytest.approx(0.9) and c[2] == pytest.approx(0.9)


def test_cross_fitting_never_uses_the_held_out_track():
    from edgeai.mir.acoustic_activation import K_MAX_HOPS, KernelBank
    fast = np.ones(K_MAX_HOPS + 1)
    slow = np.clip(np.arange(K_MAX_HOPS + 1) / K_MAX_HOPS, 0, 1)
    eps = ([{"track": "T1", "family": "bass", "curve": slow} for _ in range(40)]
           + [{"track": "T2", "family": "bass", "curve": fast} for _ in range(40)])
    kb = KernelBank(eps)
    k1, m1 = kb.for_stem("bass", "T1")     # must see only T2's fast curves
    k2, m2 = kb.for_stem("bass", "T2")     # must see only T1's slow curves
    assert m1["n_source_tracks"] == 1 and m2["n_source_tracks"] == 1
    assert k1[0] == pytest.approx(1.0)
    assert k2[0] < 0.1


def test_fallback_hierarchy_is_organological_not_measured():
    from edgeai.mir.acoustic_activation import ATTACK_CLASS_GROUPS, GROUP_OF
    assert GROUP_OF["synth_lead_pad"] == "SYNTHETIC"
    assert GROUP_OF["piano_keys"] == "PLUCKED_STRUCK"
    assert GROUP_OF["ensemble_voice"] == "BLOWN_BOWED"
    assert set().union(*ATTACK_CLASS_GROUPS.values()).isdisjoint({"drums"})


def test_target_module_imports_no_representation():
    """Construct boundary: the target may not see any chroma path."""
    import ast
    from edgeai.mir import acoustic_activation as AA
    tree = ast.parse(Path(AA.__file__).read_text())
    mods = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            mods.update(a.name for a in n.names)
        elif isinstance(n, ast.ImportFrom):
            mods.add(n.module or "")
    assert not any(b in m for m in mods
                   for b in ("tonal_projection", "host_chroma", "chroma_power", "harmonic_visual"))


def test_pitch_class_mass_is_additive_over_instruments():
    """J3K control: summing per-instrument states must equal the single all-notes
    state, so the old mixture arm IS the published oracle, not a lookalike."""
    from edgeai.mir.harmonic_movement import Note, pitch_class_state
    a = [Note(0.5, 2.0, 60, 80), Note(1.0, 2.5, 64, 90)]
    b = [Note(1.2, 3.0, 67, 70), Note(2.0, 2.4, 71, 60)]
    s = pitch_class_state(a, 200)["pc_mass"] + pitch_class_state(b, 200)["pc_mass"]
    assert np.max(np.abs(s - pitch_class_state(a + b, 200)["pc_mass"])) == 0.0


def test_mixture_activation_differs_when_families_differ():
    """The J3K premise: different simultaneous kernels do NOT cancel under L1."""
    from edgeai.mir.acoustic_activation import K_MAX_HOPS, acoustic_activation_state
    from edgeai.mir.harmonic_movement import Note, l1_rows
    fast = np.ones(K_MAX_HOPS + 1)
    slow = np.clip(np.arange(K_MAX_HOPS + 1) / 16.0, 0, 1)
    a = [Note(1.0, 3.0, 60, 80)]
    b = [Note(1.0, 3.0, 67, 80)]
    same = l1_rows(acoustic_activation_state(a, 200, slow)["pc_mass"]
                   + acoustic_activation_state(b, 200, slow)["pc_mass"])
    mixed = l1_rows(acoustic_activation_state(a, 200, fast)["pc_mass"]
                    + acoustic_activation_state(b, 200, slow)["pc_mass"])
    rect = l1_rows(acoustic_activation_state(a + b, 200, fast)["pc_mass"])
    assert np.max(np.abs(same - rect)) < 1e-12, "one shared kernel must cancel under L1"
    assert np.max(np.abs(mixed - rect)) > 0.05, "two different kernels must NOT cancel"


# --------------------------------------------- J3N pitch-filterbank ablation
def test_fb_log_chroma_shares_the_exact_crp_upstream():
    """The ablation's single-variable claim: only the liftering is removed."""
    from edgeai.mir import crp as CRP
    rng = np.random.default_rng(0)
    pe = np.abs(rng.standard_normal((40, 120))) * 1e-4
    assert np.max(np.abs(CRP.crp(pe) - CRP.crp_from_log(CRP.log_pitch(pe)))) == 0.0
    assert np.max(np.abs(CRP.fb_log_chroma(pe)
                         - CRP.fb_log_chroma_from_log(CRP.log_pitch(pe)))) == 0.0


def test_fb_log_chroma_is_non_negative_and_l1():
    from edgeai.mir import crp as CRP
    rng = np.random.default_rng(1)
    v = CRP.fb_log_chroma(np.abs(rng.standard_normal((40, 120))) * 1e-4)
    assert (v >= 0.0).all()
    assert np.allclose(v.sum(axis=1), 1.0)


def test_crp_stays_signed_and_fb_log_does_not():
    """CRP must keep negative entries; the ablation arm must not have them."""
    from edgeai.mir import crp as CRP
    rng = np.random.default_rng(2)
    pe = np.abs(rng.standard_normal((60, 120))) * 1e-4
    assert CRP.crp(pe).min() < 0.0
    assert CRP.fb_log_chroma(pe).min() >= 0.0


def test_pitch_filterbank_meets_its_published_behavioural_claims():
    from edgeai.mir import crp as CRP
    f = CRP.filterbank_fidelity()
    assert f["n_filters"] == 88
    assert f["passband_min_gain_within_pm25_cents_dB"]["worst"] >= -1.0
    assert f["adjacent_semitone_rejection_dB"]["worst"] <= -40.0


# ---------------------------------------------------------------- J3O
def _j3o():
    """Import the J3O cache module from wherever the repo root is."""
    import sys

    here = Path(__file__).resolve()
    for base in (here.parent, *here.parents):
        d = base / "scripts"
        if (d / "j3o_nnls_cache.py").is_file():
            sys.path.insert(0, str(d))
            break
    else:
        pytest.skip("scripts/j3o_nnls_cache.py not found")
    import j3o_nnls_cache as m

    return m


def test_j3o_fold12_maps_bin_k_to_midi_k_plus_21_and_preserves_mass():
    fold12 = _j3o().fold12
    x = np.zeros((3, 84))
    x[0, 39] = 1.0          # MIDI 60 -> pitch class 0
    x[1, 0] = 1.0           # MIDI 21 -> pitch class 9
    x[2, :] = 1.0
    f = fold12(x)
    assert int(np.argmax(f[0])) == 0
    assert int(np.argmax(f[1])) == 9
    assert np.isclose(f.sum(), x.sum())


def test_j3o_alignment_is_integer_and_leading_frames_are_not_zero_filled():
    m = _j3o()
    assert m.SHIFT == 3                      # block 2048 / hop 512 - 1
    x = np.arange(20 * 12, dtype=float).reshape(20, 12) + 1.0
    out = m.align(x, 25)
    assert out.shape == (25, 12)
    assert np.isnan(out[:m.SHIFT]).all()     # no plugin frame -> NaN, never zero
    assert np.allclose(out[m.SHIFT:m.SHIFT + 20], x)


def test_j3o_two_arms_differ_only_in_use_nnls():
    params = _j3o().params
    a, b = params(0.0), params(1.0)
    assert set(a) == set(b)
    assert [k for k in a if a[k] != b[k]] == ["useNNLS"]


# ---------------------------------------------------------------- J3P
def test_j3p_identity_witness_reproduces_c3_movement_exactly():
    from edgeai.mir.cross_view import endpoint_agreement, gated_movement, transition_confidence

    rng = np.random.default_rng(0)
    s = np.abs(rng.normal(size=(64, 12)))
    s /= s.sum(axis=1, keepdims=True)
    conf = transition_confidence(endpoint_agreement(s, s))
    assert np.isnan(conf[:8]).all()            # no earlier endpoint, never filled
    assert np.allclose(conf[8:], 1.0)
    mv = rng.random(64)
    assert float(np.nanmax(np.abs(gated_movement(mv, conf) - mv))) == 0.0


def test_j3p_confidence_is_bounded_and_gate_is_pure_attenuation():
    from edgeai.mir.cross_view import endpoint_agreement, gated_movement, transition_confidence

    rng = np.random.default_rng(1)
    a = np.abs(rng.normal(size=(200, 12)))
    a /= a.sum(axis=1, keepdims=True)
    b = np.abs(rng.normal(size=(200, 12)))
    b /= b.sum(axis=1, keepdims=True)
    agree = endpoint_agreement(a, b)
    assert agree.min() >= 0.0 and agree.max() <= 1.0
    conf = transition_confidence(agree)
    mv = rng.random(200)
    g = gated_movement(mv, conf)
    ok = np.isfinite(conf)
    assert np.all(g[ok] <= mv[ok] + 1e-12)     # C in [0,1] => pure attenuation


def test_j3p_disjoint_states_give_zero_agreement():
    from edgeai.mir.cross_view import endpoint_agreement

    a = np.zeros((1, 12)); a[0, 0] = 1.0
    b = np.zeros((1, 12)); b[0, 6] = 1.0
    assert float(endpoint_agreement(a, b)[0]) == 0.0
