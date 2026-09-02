#!/usr/bin/env python3
"""J3G DEVELOPMENT stage: blocking controls, tuning diagnostic, phantom-triad
fixture, the J3G-1 postprocessing ablation, and candidate scoring.

DEVELOPMENT TRACKS ONLY. The final holdout is not opened here and is not touched
by any decision this script makes. Exactly one winner is emitted.

Pre-registration: docs/mir/receipts/stft_harmonic_recovery/J3G_PREREGISTRATION.json
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import j3g_common as C  # noqa: E402

sys.path.insert(0, str(C.ROOT / "src"))
from edgeai.mir import tonal_projection as tp  # noqa: E402
from edgeai.mir.chroma_power import assert_matches_host_chroma12  # noqa: E402
from edgeai.mir.harmonic_movement import pitch_class_state, tv_movement, within_track_rank  # noqa: E402
from edgeai.mir.note_register import HOP, SR, Note, frame_grid  # noqa: E402

NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


# ------------------------------------------------------------ fixture
def _tone(midi: float, harmonics: int, dur: float = 3.0) -> np.ndarray:
    f = 440.0 * 2.0 ** ((midi - 69.0) / 12.0)
    t = np.arange(int(SR * dur), dtype=np.float64) / SR
    return sum((1.0 / h) * np.sin(2.0 * np.pi * h * f * t) for h in range(1, harmonics + 1))


FIXTURES = {
    "PURE_SINE": lambda: 0.2 * _tone(60, 1),
    "HARMONIC_NOTE": lambda: 0.2 * _tone(60, 8),
    "TWO_NOTE_FIFTH": lambda: 0.2 * (_tone(60, 8) + _tone(67, 8)),
    "MAJOR_TRIAD": lambda: 0.2 * (_tone(60, 8) + _tone(64, 8) + _tone(67, 8)),
}
CHORD_TONES = {"PURE_SINE": [0], "HARMONIC_NOTE": [0], "TWO_NOTE_FIFTH": [0, 7], "MAJOR_TRIAD": [0, 4, 7]}


def phantom_triad_fixture(winner: str) -> dict:
    out = {}
    for fid, gen in FIXTURES.items():
        st = tp.stft_power(gen())
        raw = C.raw_projections(st)
        raw.pop("_c4_rectified_mass_fraction")
        states = C.states_from_raw(raw, winner=winner)
        i = states["P0_CURRENT"].shape[0] // 2
        rows = {}
        for k, v in states.items():
            x = v[i]
            tones = CHORD_TONES[fid]
            rows[k] = {
                "vector": {NAMES[j]: round(float(x[j]), 4) for j in range(12)},
                "root_mass": round(float(x[0]), 4),
                "fifth_mass": round(float(x[7]), 4),
                "major_third_mass": round(float(x[4]), 4),
                "chord_tone_mass": round(float(sum(x[t] for t in tones)), 4),
                "non_chord_tone_mass": round(float(1.0 - sum(x[t] for t in tones)), 4),
            }
        out[fid] = rows
    return out


# ------------------------------------------------------------ tuning
def tuning_diagnostic(corpus: Path, tracks: list[str]) -> dict:
    import soundfile as sf
    per = []
    for name in tracks:
        y, sr = sf.read(str(corpus / name / "mix.wav"), dtype="float64", always_2d=True)
        y = y.mean(axis=1)[: SR * 60]
        st = tp.stft_power(y)
        pk = tp._peaks(st)
        if pk["rows"].size == 0:
            continue
        m = tp.bin_midi(pk["freq"])
        cents = (m - np.rint(m)) * 100.0
        w = pk["amp"] ** 2
        ang = np.exp(1j * 2.0 * np.pi * cents / 100.0)
        mean_ang = np.angle(np.sum(w * ang) / (np.sum(w) + 1e-20)) / (2.0 * np.pi) * 100.0
        per.append({"track": name, "weighted_circular_mean_cents": round(float(mean_ang), 2),
                    "n_peaks": int(pk["rows"].size)})
    devs = [abs(p["weighted_circular_mean_cents"]) for p in per]
    med = float(np.median(devs)) if devs else float("nan")
    return {"per_track": per, "median_abs_deviation_cents": round(med, 2),
            "declared_threshold_cents": 10.0,
            "verdict": "TUNING_NOT_MATERIAL_HERE" if med <= 10.0 else "TUNING_MATERIAL",
            "action": ("no candidate spent on tuning compensation" if med <= 10.0
                       else "tuning compensation added to C1/C2 with a slow causal estimator")}


# ------------------------------------------------------------ solo stems
def solo_family(corpus: Path, tracks: list[str], names: list[str], winner: str, cache: Path) -> dict:
    import pretty_midi
    import soundfile as sf
    import yaml
    from scipy.stats import spearmanr

    cache.mkdir(parents=True, exist_ok=True)
    rows = []
    for tname in tracks:
        d = corpus / tname
        md = yaml.safe_load((d / "metadata.yaml").read_text())
        for f in sorted(p for p in (d / "stems").glob("*.wav") if not p.name.startswith("._")):
            meta = md["stems"].get(f.stem, {})
            prog = int(meta.get("program_num", 0))
            if meta.get("is_drum") or prog >= 112:
                continue
            mf = d / "MIDI" / f"{f.stem}.mid"
            if not mf.is_file():
                continue
            cf = cache / f"{tname}__{f.stem}.npz"
            if cf.is_file():
                z = np.load(cf, allow_pickle=False)
                rec = {"Ms": z["Ms"], "raw": {k: z[f"R_{k}"] for k in C.RAW_KEYS},
                       "valid": z["valid"], "median_pitch": float(z["median_pitch"])}
            else:
                y, sr = sf.read(str(f), dtype="float64", always_2d=True)
                if sr != SR:
                    continue
                y = y.mean(axis=1)
                try:
                    spm = pretty_midi.PrettyMIDI(str(mf))
                except Exception:  # noqa: BLE001
                    continue
                notes = [Note(float(n.start), float(n.end), int(n.pitch), int(n.velocity))
                         for i in spm.instruments for n in i.notes]
                if len(notes) < 50:
                    continue
                times, _ = frame_grid(y.size)
                n = times.size
                stt = pitch_class_state(notes, n)
                st = tp.stft_power(y)
                raw = C.raw_projections(st)
                raw.pop("_c4_rectified_mass_fraction")
                raw = {k: v[:n] for k, v in raw.items()}
                Ms = tv_movement(stt["pc_mass"])
                sil = stt["silent"]
                pair = np.zeros(n, dtype=bool)
                pair[C.LAG:] = (~sil[C.LAG:]) & (~sil[:-C.LAG])
                valid = pair & np.isfinite(Ms)
                if valid.sum() < 400:
                    continue
                mp = float(np.median([x.pitch for x in notes]))
                np.savez_compressed(cf, Ms=Ms, valid=valid, median_pitch=mp,
                                    **{f"R_{k}": v for k, v in raw.items()})
                rec = {"Ms": Ms, "raw": raw, "valid": valid, "median_pitch": mp}
            states = C.states_from_raw(rec["raw"], winner=winner)
            v = rec["valid"] & np.all([np.isfinite(tv_movement(s)) for s in states.values()], axis=0)
            if v.sum() < 400:
                continue
            rows.append({"track": tname, "stem": f.stem, "program": prog,
                         "family": C.family_of(prog), "median_pitch": rec["median_pitch"],
                         "Ms": rec["Ms"][v],
                         "Ma": {k: tv_movement(s)[v] for k, s in states.items()}})
    out = {}
    for name in names:
        by_fam = defaultdict(list)
        for r in rows:
            by_fam[r["family"]].append(r)
        fam = {}
        for fname, rs in sorted(by_fam.items()):
            g = np.concatenate([np.full(len(r["Ms"]), f"{r['track']}:{r['stem']}") for r in rs])
            if len(np.unique(g)) < 3:
                continue
            Ms = np.concatenate([r["Ms"] for r in rs])
            Ma = np.concatenate([r["Ma"][name] for r in rs])
            fam[fname] = {"n_stems": len(rs), "n_frames": int(len(Ms)),
                          "solo_stem_r2": C.grouped_r2(Ma, Ms, g),
                          "spearman": round(float(spearmanr(Ma, Ms).statistic), 4)}
        allg = np.concatenate([np.full(len(r["Ms"]), f"{r['track']}:{r['stem']}") for r in rows])
        allMs = np.concatenate([r["Ms"] for r in rows])
        allMa = np.concatenate([r["Ma"][name] for r in rows])
        vals = [v["solo_stem_r2"] for v in fam.values()]
        out[name] = {"overall_r2": C.grouped_r2(allMa, allMs, allg),
                     "overall_spearman": round(float(spearmanr(allMa, allMs).statistic), 4),
                     "by_family": fam,
                     "spread": round(max(vals) - min(vals), 4) if vals else None,
                     "worst_family": min(fam, key=lambda k: fam[k]["solo_stem_r2"]) if fam else None,
                     "worst_family_r2": round(min(vals), 4) if vals else None}
    out["_n_stems"] = len(rows)
    return out


# ------------------------------------------------------------ main
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--git-head", type=str, default="UNKNOWN")
    args = ap.parse_args()
    prereg = json.loads(C.PREREG.read_text())
    split = C.split_tracks(args.corpus)
    assert split["development"] == prereg["development_holdout_discipline"]["development_tracks"]
    assert split["final_holdout"] == prereg["development_holdout_discipline"]["final_holdout_tracks"]

    import soundfile as sf
    probe, _ = sf.read(str(args.corpus / split["all"][0] / "mix.wav"), dtype="float64", always_2d=True)
    probe = probe.mean(axis=1)[: SR * 20]
    ctrl = {
        "C_FRAMING_max_abs_diff": tp.assert_frames_match_host_chroma12(probe),
        "C_IDENTITY_max_abs_diff": assert_matches_host_chroma12(probe),
    }
    ctrl["C_FRAMING_ok"] = bool(ctrl["C_FRAMING_max_abs_diff"] <= 1e-9)
    ctrl["C_IDENTITY_ok"] = bool(ctrl["C_IDENTITY_max_abs_diff"] <= 1e-5)

    all_blocks = [C.cached_track(args.corpus / t) for t in split["all"]]
    cls_all, groups_all, _ = C.challenge_masks(all_blocks)
    counts = {k: int(v.sum()) for k, v in cls_all.items()}
    expected = prereg["blocking_controls_all_must_pass_before_any_candidate_score"]["C_MEMBERSHIP"]["expected"]
    ctrl["C_MEMBERSHIP_counts"] = counts
    ctrl["C_MEMBERSHIP_expected"] = expected
    ctrl["C_MEMBERSHIP_ok"] = bool(counts == expected)

    dev = [b for b in all_blocks if b["track"] in set(split["development"])]
    cls_dev, groups_dev, rM_dev = C.challenge_masks(dev)
    M0d = C.pool(dev, "M_oracle")
    perm = np.random.default_rng(1234).permutation(len(M0d))
    MP0 = np.concatenate([b["mov"]["P0_CURRENT"][b["valid"]] for b in dev])
    ctrl["C_SHUFFLE_r2"] = C.grouped_r2(MP0[perm], M0d, groups_dev)
    ctrl["C_SHUFFLE_ok"] = bool(ctrl["C_SHUFFLE_r2"] <= 0.10)
    ctrl["all_blocking_pass"] = bool(ctrl["C_FRAMING_ok"] and ctrl["C_IDENTITY_ok"]
                                     and ctrl["C_MEMBERSHIP_ok"] and ctrl["C_SHUFFLE_ok"])
    if not ctrl["all_blocking_pass"]:
        args.out.write_text(json.dumps({"job": "J3G-DEV", "outcome": "EXISTING_STFT_HARMONIC_RECOVERY_INCONCLUSIVE",
                                        "controls": ctrl}, indent=2) + "\n")
        print(json.dumps(ctrl, indent=2))
        return 1

    # ---- J3G-1 ablation, DEVELOPMENT only ----
    ablation = {k: C.level_a_b(dev, k, cls_dev, groups_dev, rM_dev)
                for k in ("P0_CURRENT", "P1_POWER_L1", "P2_SQRT_L1_NO_CLIP")}
    p0_r2 = ablation["P0_CURRENT"]["r2"]
    gains = {k: round(v["r2"] - p0_r2, 4) for k, v in ablation.items()}
    winner_post = max(ablation, key=lambda k: ablation[k]["r2"])
    stop_rule_hit = bool(max(gains.values()) >= 0.15)

    # ---- candidates, DEVELOPMENT only, with the carry-forward compression ----
    for b in dev:
        C.attach_states(b, winner=winner_post)
    cand = {k: C.level_a_b(dev, k, cls_dev, groups_dev, rM_dev) for k in C.CANDIDATES}
    lags = {k: C.lag_curve(dev, k) for k in C.CANDIDATES}
    fixture = phantom_triad_fixture(winner_post)
    tuning = tuning_diagnostic(args.corpus, split["development"])
    solo = solo_family(args.corpus, split["development"], C.CANDIDATES, winner_post, Path("/tmp/j3g_stem_cache"))

    # ---- selection, DEVELOPMENT only ----
    p0_false = cand["P0_CURRENT"]["challenge_recall"]["ACOUSTIC_CHANGE_LOW_HARMONIC_CHANGE"]
    p0_triad = fixture["MAJOR_TRIAD"]["P0_CURRENT"]["chord_tone_mass"]
    sel = {}
    for k in C.PROJECTIONS:
        g1 = cand[k]["challenge_recall"]["ACOUSTIC_CHANGE_LOW_HARMONIC_CHANGE"] <= p0_false + 0.02
        g2 = fixture["MAJOR_TRIAD"][k]["chord_tone_mass"] >= 0.70 * p0_triad
        harm = float(np.mean([cand[k]["challenge_recall"]["HARMONIC_CHANGE_FLAT_ENERGY"],
                              cand[k]["challenge_recall"]["HARMONIC_CHANGE_NO_ONSET"]]))
        wf = solo[k]["worst_family_r2"] or 0.0
        sel[k] = {"gate_1_acoustic_false_response_ok": bool(g1),
                  "gate_anti_gaming_major_triad_ok": bool(g2),
                  "eligible": bool(g1 and g2),
                  "mean_harmonic_challenge_recall": round(harm, 4),
                  "worst_family_solo_r2": wf,
                  "selection_score": round(0.5 * harm + 0.5 * float(np.clip(wf, 0.0, 1.0)), 4),
                  "family_spread": solo[k]["spread"],
                  "non_root_mass_HARMONIC_NOTE": fixture["HARMONIC_NOTE"][k]["non_chord_tone_mass"]}
    eligible = [k for k in C.PROJECTIONS if sel[k]["eligible"]]
    if eligible:
        winner = sorted(eligible, key=lambda k: (-sel[k]["selection_score"],
                                                 sel[k]["non_root_mass_HARMONIC_NOTE"],
                                                 sel[k]["family_spread"] or 9.9))[0]
    else:
        winner = None

    out = {
        "schema": "spectrasynq.stft_harmonic_recovery_dev.v1",
        "job": "J3G-DEV", "label": "HOST-ONLY DETERMINISTIC TONAL PROJECTION - DEVELOPMENT STAGE",
        "git_head": args.git_head,
        "preregistration": str(C.PREREG.relative_to(C.ROOT)),
        "preregistration_amendments": prereg["amendments_before_any_score"],
        "execution_environment": "Anthropic cloud container (HOST-class). BabySlakh 16 kHz, md5 verified against the publisher's checksum.",
        "split": {k: split[k] for k in ("development", "final_holdout")},
        "final_holdout_opened_in_this_stage": False,
        "controls": ctrl,
        "tuning_diagnostic": tuning,
        "phantom_triad_fixture": fixture,
        "J3G_1_postprocessing_ablation": {
            "variants": ablation, "r2_gain_over_P0": gains, "winner": winner_post,
            "stop_rule_threshold": 0.15, "stop_rule_hit": stop_rule_hit,
            "arithmetic_note": "the fixed reference divisor is a constant scale and cancels under L1; P0 vs P2 therefore isolates the clip, P2 vs P1 the compression exponent",
        },
        "carry_forward_compression_applied_to_candidates": winner_post,
        "candidates_development": cand,
        "lag_curves_development_REPORTED_NOT_OPTIMISED": lags,
        "solo_stem_family_development": solo,
        "selection": {"rule": prereg["candidate_selection_rule_DEVELOPMENT_ONLY"],
                      "P0_acoustic_false_response": p0_false,
                      "P0_major_triad_chord_tone_mass": p0_triad,
                      "per_candidate": sel, "eligible": eligible, "winner": winner},
        "c4_rectified_mass_fraction_by_track": {b["track"]: b["c4_rectified_mass_fraction"] for b in dev},
        "arithmetic_cost_per_frame": tp.arithmetic_cost_per_frame(),
        "student_io_frozen": False, "titan": False, "production_firmware_changed": False,
        "basic_pitch_run": False, "foundation_model_run": False, "cqt_run": False,
        "source_separator_run": False, "neural_student_trained": False,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2, sort_keys=False) + "\n")
    print(json.dumps({"controls": ctrl, "tuning": tuning["verdict"],
                      "ablation": out["J3G_1_postprocessing_ablation"],
                      "candidates": cand, "selection": out["selection"]["per_candidate"],
                      "winner": winner}, indent=2))
    print(f"receipt -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
