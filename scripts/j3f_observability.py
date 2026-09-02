#!/usr/bin/env python3
"""J3F - harmonic observability decomposition.

Where between symbolic truth and mixed audio is harmonic information lost?

Ladder:  S0 symbolic  ->  S1 individual pitched stems  ->  S1_aggregate (power sum,
no cross terms)  ->  S2 pitched waveform mix  ->  S3 full mix incl. percussion.

host_chroma12 is the OBJECT UNDER TEST and is never substituted. The vectorised
power path is instrumentation and is asserted equal to it before use.

Pre-registration: docs/mir/receipts/harmonic_observability/J3F_PREREGISTRATION.json
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from edgeai.mir.chroma_power import (  # noqa: E402
    assert_matches_host_chroma12,
    pitch_class_power,
    power_to_chroma12,
)
from edgeai.mir.harmonic_movement import (  # noqa: E402
    MOVEMENT_LAG_HOPS,
    is_tonal_instrument,
    l1_rows,
    lagged_abs_delta,
    pitch_class_state,
    rectified_flux,
    tv_movement,
    within_track_rank,
)
from edgeai.mir.host_chroma import host_spectrogram80  # noqa: E402
from edgeai.mir.note_register import (  # noqa: E402
    HOP,
    N_FFT,
    SR,
    Note,
    dsp_register_features,
    frame_grid,
    silence_mask,
)

PREREG = ROOT / "docs" / "mir" / "receipts" / "harmonic_observability" / "J3F_PREREGISTRATION.json"
LAG = MOVEMENT_LAG_HOPS
ALPHAS = (1e-3, 1e-2, 1e-1, 1.0, 10.0, 100.0, 1000.0)
FAMILIES = [("piano_keys", lambda p: p < 8 or 16 <= p < 24), ("chromatic_percussion", lambda p: 8 <= p < 16),
            ("guitar", lambda p: 24 <= p < 32), ("bass", lambda p: 32 <= p < 40),
            ("strings", lambda p: 40 <= p < 48), ("ensemble_voice", lambda p: 48 <= p < 56),
            ("brass", lambda p: 56 <= p < 64), ("reed_pipe", lambda p: 64 <= p < 80),
            ("synth_lead_pad", lambda p: 80 <= p < 96), ("synth_effects", lambda p: 96 <= p < 112)]


def family_of(program: int) -> str:
    for name, fn in FAMILIES:
        if fn(int(program)):
            return name
    return "other"


def _fit(X, Y, a):
    mu, sd = X.mean(0), X.std(0) + 1e-9
    Xs = (X - mu) / sd
    ym = Y.mean(0)
    return {"mu": mu, "sd": sd, "ym": ym,
            "W": np.linalg.solve(Xs.T @ Xs + a * np.eye(Xs.shape[1]), Xs.T @ (Y - ym))}


def _pred(m, X):
    return ((X - m["mu"]) / m["sd"]) @ m["W"] + m["ym"]


def _r2(y, yh):
    return float(1.0 - np.sum((y - yh) ** 2) / (np.sum((y - y.mean()) ** 2) + 1e-20))


def grouped_r2(x, y, groups, *, n_folds=5, seed=0):
    X = np.atleast_2d(np.asarray(x, dtype=np.float64).T).T
    Y = np.asarray(y, dtype=np.float64).reshape(-1, 1)
    uniq = np.unique(groups)
    n_folds = max(2, min(n_folds, len(uniq)))
    oof = np.full_like(Y, np.nan)
    for f in np.array_split(np.random.default_rng(seed).permutation(uniq), n_folds):
        te = np.isin(groups, f)
        tr = ~te
        if tr.sum() < 10 or te.sum() < 1:
            continue
        trt = np.unique(groups[tr])
        cut = max(1, len(trt) // 4)
        iv = np.isin(groups, trt[:cut]) & tr
        it = tr & ~iv
        best, ba = -np.inf, ALPHAS[0]
        for a in ALPHAS:
            m = _fit(X[it], Y[it], a)
            s = _r2(Y[iv], _pred(m, X[iv]))
            if s > best:
                best, ba = s, a
        oof[te] = _pred(_fit(X[tr], Y[tr], ba), X[te])
    ok = ~np.isnan(oof[:, 0])
    return round(_r2(Y[ok], oof[ok]), 4)


def half_rise(state: np.ndarray, ref: int, centre: int, half: int = 24) -> float:
    p = l1_rows(state)
    if ref >= len(p) or centre >= len(p):
        return float("nan")
    d = 0.5 * np.abs(p - p[ref][None, :]).sum(axis=1)
    lo, hi = max(centre - half, 0), min(centre + half, d.size)
    seg = d[lo:hi]
    if seg.size < 8:
        return float("nan")
    k = max(half // 3, 1)
    start, final = float(np.median(seg[:k])), float(np.median(seg[-k:]))
    if final - start < 1e-6:
        return float("nan")
    tgt = start + 0.5 * (final - start)
    above = np.nonzero(seg >= tgt)[0]
    if above.size == 0 or above[0] == 0:
        return float("nan")
    j = int(above[0])
    y0, y1 = seg[j - 1], seg[j]
    return float(lo + (j - 1) + (0.0 if y1 == y0 else (tgt - y0) / (y1 - y0)))


def stem_files(d: Path) -> list[Path]:
    return sorted(p for p in (d / "stems").glob("*.wav") if not p.name.startswith("._"))


def build(track_dir: Path, *, max_onsets_per_stem: int = 40):
    import librosa
    import pretty_midi
    import soundfile as sf
    import yaml

    md = yaml.safe_load((track_dir / "metadata.yaml").read_text())
    mix, sr = sf.read(str(track_dir / "mix.wav"), dtype="float64", always_2d=True)
    if sr != SR:
        return None
    mix = mix.mean(axis=1)
    L = mix.size
    times, _ = frame_grid(L)

    pm = pretty_midi.PrettyMIDI(str(track_dir / "all_src.mid"))
    notes = [Note(float(n.start), float(n.end), int(n.pitch), int(n.velocity))
             for i in pm.instruments if is_tonal_instrument(i.is_drum, i.program) for n in i.notes]
    st = pitch_class_state(notes, times.size)

    pitched_sum = np.zeros(L)
    pitched_power = None
    q1_rows: list[dict] = []
    n_pitched = 0
    for f in stem_files(track_dir):
        meta = md["stems"].get(f.stem, {})
        prog = int(meta.get("program_num", 0))
        if meta.get("is_drum") or prog >= 112:
            continue
        y, _ = sf.read(str(f), dtype="float64", always_2d=True)
        y = y.mean(axis=1)
        y = np.pad(y, (0, max(0, L - y.size)))[:L]
        pitched_sum += y
        p = pitch_class_power(y)[: times.size]
        pitched_power = p if pitched_power is None else pitched_power + p
        n_pitched += 1

        mf = track_dir / "MIDI" / f"{f.stem}.mid"
        if not mf.is_file():
            continue
        try:
            spm = pretty_midi.PrettyMIDI(str(mf))
        except Exception:  # noqa: BLE001
            continue
        snotes = [Note(float(n.start), float(n.end), int(n.pitch), int(n.velocity))
                  for i in spm.instruments for n in i.notes]
        if not snotes:
            continue
        sst = pitch_class_state(snotes, times.size)
        schroma = power_to_chroma12(p).astype(np.float64)
        # isolated onsets: no other onset in this stem within +/- 8 hops
        onset_f = np.array(sorted({int(round(n.start_s * SR / HOP)) for n in snotes}))
        iso = [f0 for k, f0 in enumerate(onset_f)
               if (k == 0 or f0 - onset_f[k - 1] > 8) and (k == len(onset_f) - 1 or onset_f[k + 1] - f0 > 8)]
        iso = [f0 for f0 in iso if 40 <= f0 < times.size - 40]
        if len(iso) > max_onsets_per_stem:
            iso = list(np.array(iso)[np.linspace(0, len(iso) - 1, max_onsets_per_stem).astype(int)])
        reg = float(np.median([n.pitch for n in snotes]))
        for f0 in iso:
            hs = half_rise(sst["pc_mass"], max(f0 - 30, 0), f0)
            ha = half_rise(schroma, max(f0 - 30, 0), f0)
            if np.isfinite(hs) and np.isfinite(ha):
                q1_rows.append({"track": track_dir.name, "stem": f.stem, "program": prog,
                                "family": family_of(prog), "median_pitch": reg,
                                "offset_hops": round(ha - hs, 3)})

    if pitched_power is None:
        return None

    n = times.size
    ch_s1 = power_to_chroma12(pitched_power).astype(np.float64)
    ch_s2 = power_to_chroma12(pitch_class_power(pitched_sum)[:n]).astype(np.float64)
    ch_s3 = power_to_chroma12(pitch_class_power(mix)[:n]).astype(np.float64)

    _, spec = host_spectrogram80(mix.astype(np.float32))
    _, rms, _ = dsp_register_features(mix)
    onset_raw = librosa.onset.onset_strength(y=mix.astype(np.float32), sr=SR,
                                             hop_length=HOP, n_fft=N_FFT, center=False)
    m = min(n, len(spec), len(rms))
    flux1 = np.zeros(len(spec))
    flux1[1:] = np.clip(np.diff(spec.astype(np.float64), axis=0), 0.0, None).sum(axis=1)
    from scipy.stats import spearmanr as _sp
    best_shift, best_s = 0, -np.inf
    for k in range(7):
        cand = np.zeros(n)
        for i in range(n):
            j = i - k
            if 0 <= j < onset_raw.size:
                cand[i] = onset_raw[j]
        s = _sp(flux1[:m], cand[:m]).statistic
        if np.isfinite(s) and s > best_s:
            best_s, best_shift = float(s), k
    onset = np.zeros(n)
    for i in range(n):
        j = i - best_shift
        onset[i] = onset_raw[j] if 0 <= j < onset_raw.size else 0.0

    sil = st["silent"][:m]
    pair_ok = np.zeros(m, dtype=bool)
    pair_ok[LAG:] = (~sil[LAG:]) & (~sil[:-LAG])
    M0 = tv_movement(st["pc_mass"][:m])
    mov = {k: tv_movement(v[:m]) for k, v in
           (("S1_aggregate", ch_s1), ("S2_pitched_mix", ch_s2), ("S3_full_mix", ch_s3))}
    B_flux = rectified_flux(spec[:m].astype(np.float64))
    B_onset = lagged_abs_delta(onset[:m])
    B_rms = lagged_abs_delta(np.log(rms[:m] + 1e-12))
    valid = (pair_ok & silence_mask(rms[:m]) & np.isfinite(M0)
             & np.all([np.isfinite(v) for v in mov.values()], axis=0)
             & np.isfinite(B_flux) & np.isfinite(B_onset) & np.isfinite(B_rms))
    return {"track": track_dir.name, "n": m, "valid": valid, "M0": M0, "mov": mov,
            "B_onset": B_onset, "B_rms": B_rms, "q1": q1_rows, "n_pitched": n_pitched,
            "chroma": {"S1_aggregate": ch_s1[:m], "S3_full_mix": ch_s3[:m]},
            "state": st["pc_mass"][:m], "flux": B_flux}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--git-head", type=str, default="UNKNOWN")
    args = ap.parse_args()
    prereg = json.loads(PREREG.read_text())
    from scipy.stats import spearmanr

    dirs = sorted(p for p in args.corpus.iterdir() if p.is_dir() and (p / "all_src.mid").is_file())
    import soundfile as sf
    probe, _ = sf.read(str(dirs[0] / "mix.wav"), dtype="float64", always_2d=True)
    instr_err = assert_matches_host_chroma12(probe.mean(axis=1)[: SR * 20])

    blocks = [b for b in (build(d) for d in dirs) if b]
    groups = np.concatenate([np.full(int(b["valid"].sum()), b["track"]) for b in blocks])
    M0 = np.concatenate([b["M0"][b["valid"]] for b in blocks])
    rungs = ["S1_aggregate", "S2_pitched_mix", "S3_full_mix"]
    MV = {k: np.concatenate([b["mov"][k][b["valid"]] for b in blocks]) for k in rungs}
    vO = np.concatenate([b["B_onset"][b["valid"]] for b in blocks])
    vR = np.concatenate([b["B_rms"][b["valid"]] for b in blocks])

    perm = np.random.default_rng(1234).permutation(len(M0))
    shuffle_r2 = grouped_r2(MV["S3_full_mix"][perm], M0, groups)
    controls = {
        "instrumented_chroma_max_abs_diff_vs_host_chroma12": instr_err,
        "instrumented_chroma_ok": bool(instr_err <= 1e-5),
        "shuffled_baseline_r2": shuffle_r2,
        "shuffle_ok": bool(shuffle_r2 <= 0.10),
        "stem_sum_reconstruction": prereg["preflight_controls"]["stem_sum_reconstructs_the_mix"]["measured"],
    }
    controls["all_blocking_pass"] = bool(controls["instrumented_chroma_ok"] and controls["shuffle_ok"])

    rM, rO, rR = (within_track_rank(x, groups) for x in (M0, vO, vR))
    cls = {"HARMONIC_CHANGE_FLAT_ENERGY": (rM >= 0.95) & (rR <= 0.50),
           "HARMONIC_CHANGE_NO_ONSET": (rM >= 0.95) & (rO <= 0.50),
           "ACOUSTIC_CHANGE_LOW_HARMONIC_CHANGE": (rO >= 0.95) & (rM <= 0.50)}
    top5 = rM >= 0.95

    ladder = {}
    for k in rungs:
        rC = within_track_rank(MV[k], groups)
        ladder[k] = {
            "r2": grouped_r2(MV[k], M0, groups),
            "spearman": round(float(spearmanr(MV[k], M0).statistic), 4),
            "top5_event_recall_in_top20": round(float(((rC >= 0.80) & top5).sum() / max(int(top5.sum()), 1)), 4),
            "challenge_recall": {c: round(float((rC[m] >= 0.80).mean()), 4) for c, m in cls.items()},
        }

    q1 = [r for b in blocks for r in b["q1"]]
    offs = np.array([r["offset_hops"] for r in q1], dtype=np.float64)
    by_fam: dict[str, list[float]] = defaultdict(list)
    for r in q1:
        by_fam[r["family"]].append(r["offset_hops"])
    timing = {
        "n_isolated_onsets": int(offs.size),
        "median_offset_hops": round(float(np.median(offs)), 3) if offs.size else None,
        "iqr_hops": round(float(np.percentile(offs, 75) - np.percentile(offs, 25)), 3) if offs.size else None,
        "by_family": {f: {"n": len(v), "median": round(float(np.median(v)), 3)}
                      for f, v in sorted(by_fam.items()) if len(v) >= 20},
    }
    med_shift = int(round(timing["median_offset_hops"])) if timing["median_offset_hops"] is not None else 0

    def shifted_r2(key, k):
        Xs, Ys, Gs = [], [], []
        for b in blocks:
            x, y = b["mov"][key], b["M0"]
            v = b["valid"]
            if k > 0:
                xs, ys, vs = x[:-k], y[k:], v[k:]
            elif k < 0:
                xs, ys, vs = x[-k:], y[:k], v[:k]
            else:
                xs, ys, vs = x, y, v
            keep = vs & np.isfinite(xs) & np.isfinite(ys)
            if keep.sum() < 20:
                continue
            Xs.append(xs[keep])
            Ys.append(ys[keep])
            Gs.append(np.full(int(keep.sum()), b["track"]))
        return grouped_r2(np.concatenate(Xs), np.concatenate(Ys), np.concatenate(Gs))

    aligned = {k: shifted_r2(k, med_shift) for k in rungs}

    # family-level single-stem observability, using each stem's own aggregate contribution
    fam_r2 = {}
    for fam in sorted({r["family"] for r in q1}):
        v = [r["offset_hops"] for r in q1 if r["family"] == fam]
        if len(v) >= 20:
            fam_r2[fam] = {"n_onsets": len(v), "median_offset_hops": round(float(np.median(v)), 3)}

    q3 = {"A_power_sum_no_cross_terms_r2": ladder["S1_aggregate"]["r2"],
          "B_waveform_sum_r2": ladder["S2_pitched_mix"]["r2"],
          "A_minus_B": round(ladder["S1_aggregate"]["r2"] - ladder["S2_pitched_mix"]["r2"], 4)}
    q3["implication"] = ("MIXTURE_INTERFERENCE" if q3["A_minus_B"] >= 0.15
                         else ("RENDERER_OR_FRONTEND" if max(q3["A_power_sum_no_cross_terms_r2"],
                                                             q3["B_waveform_sum_r2"]) < 0.50 else "NEITHER_CLEARLY"))

    # --- error typology on a bounded sample -------------------------------
    rC3 = within_track_rank(MV["S3_full_mix"], groups)
    missed = np.nonzero(top5 & (rC3 < 0.80))[0]
    sample = missed[np.linspace(0, len(missed) - 1, min(200, len(missed))).astype(int)] if missed.size else []
    typo: dict[str, int] = defaultdict(int)
    off = 0
    index_map = {}
    for b in blocks:
        nv = int(b["valid"].sum())
        for j, gi in enumerate(np.nonzero(b["valid"])[0]):
            index_map[off + j] = (b, int(gi))
        off += nv
    for gi in sample:
        b, i = index_map[int(gi)]
        S = l1_rows(b["state"])
        C3 = l1_rows(b["chroma"]["S3_full_mix"])
        C1 = l1_rows(b["chroma"]["S1_aggregate"])
        if i - LAG < 0 or i + LAG >= len(S):
            continue
        d_now = 0.5 * np.abs(C3[i] - S[i]).sum()
        d_prev = 0.5 * np.abs(C3[i] - S[i - LAG]).sum()
        d_next = 0.5 * np.abs(C3[i] - S[i + LAG]).sum()
        pc_contam = 0.5 * np.abs(C3[i] - C1[i]).sum()
        if int((S[i] > 1e-6).sum()) >= 5:
            typo["ambiguous_overlapping_voices"] += 1
        elif pc_contam > 0.20:
            typo["percussion_contamination"] += 1
        elif d_prev < d_now - 0.05:
            typo["residual_previous_chord"] += 1
        elif d_next < d_now - 0.05:
            typo["premature_next_state"] += 1
        elif b["mov"]["S3_full_mix"][i] < np.nanpercentile(b["mov"]["S3_full_mix"], 20):
            typo["false_stable"] += 1
        elif int(np.argmax(C3[i])) != int(np.argmax(S[i])):
            typo["wrong_pitch_class_emphasis"] += 1
        else:
            typo["broadband_transient_contamination"] += 1

    # --- attribution, in the pre-registered precedence order --------------
    R1, R2, R3 = (ladder[k]["r2"] for k in rungs)
    A1 = aligned["S1_aggregate"]
    D = max(R1 - R3, 1e-9)
    fam_meds = [v["median"] for v in timing["by_family"].values()]
    timing_systematic = (timing["median_offset_hops"] is not None
                         and 0.5 <= abs(timing["median_offset_hops"]) <= 1.5
                         and timing["iqr_hops"] is not None and timing["iqr_hops"] <= 1.0
                         and len(fam_meds) > 0 and (all(x < 0 for x in fam_meds) or all(x > 0 for x in fam_meds)))
    if not controls["all_blocking_pass"]:
        outcome = "HARMONIC_OBSERVABILITY_INCONCLUSIVE"
    elif timing_systematic and A1 >= 0.70 and R1 < 0.50:
        outcome = "RENDERER_TIMING_DOMINANT"
    elif max(R1, A1) < 0.50:
        outcome = "TIMBRE_FRONTEND_DOMINANT"
    elif R1 >= 0.70 and (R1 - R2) >= 0.5 * D:
        outcome = "PITCHED_MIXTURE_INTERFERENCE_DOMINANT"
    elif (R2 - R3) >= 0.5 * D and R2 >= 0.60:
        outcome = "PERCUSSION_OR_FULL_MIX_INTERFERENCE_DOMINANT"
    else:
        outcome = "MULTIFACTOR_HARMONIC_LOSS"

    receipt = {
        "schema": "spectrasynq.harmonic_observability_result.v1",
        "job": "J3F", "label": "HOST-ONLY AUDIO-INFORMATION FORENSIC",
        "git_head": args.git_head,
        "preregistration": str(PREREG.relative_to(ROOT)),
        "preregistration_written_before_any_ladder_metric": prereg["written_before_any_ladder_metric"],
        "execution_environment": "Anthropic cloud container (HOST-class). Corpus md5 verified against the publisher's checksum.",
        "Q0_analytical_frontend_audit": prereg["Q0_ANALYTICAL_FRONTEND_AUDIT"],
        "corpus": {"tracks": len(blocks), "valid_frames": int(len(M0)),
                   "pitched_stems_used": sum(b["n_pitched"] for b in blocks)},
        "controls": controls,
        "Q1_renderer_stem_timing": timing,
        "Q2_ladder": ladder,
        "Q2_ladder_at_measured_alignment": {"applied_shift_hops": med_shift, "r2": aligned},
        "Q2_degradation": {"S1_aggregate_minus_S2": round(R1 - R2, 4),
                           "S2_minus_S3": round(R2 - R3, 4),
                           "total_S1_minus_S3": round(R1 - R3, 4)},
        "Q3_nonlinear_mixing": q3,
        "family_diagnosis": fam_r2,
        "error_typology": {"sample_size": int(len(sample)), "counts": dict(sorted(typo.items()))},
        "outcome": outcome,
        "thresholds_applied": prereg["outcome_taxonomy_in_precedence_order"],
        "product_grammar_wording": prereg["product_grammar_wording"],
        "student_io_frozen": False, "titan": False, "production_firmware_changed": False,
        "basic_pitch_run": False, "foundation_model_run": False,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"outcome": outcome, "controls": controls, "Q2_ladder": ladder,
                      "aligned": receipt["Q2_ladder_at_measured_alignment"],
                      "Q1": timing, "Q3": q3,
                      "typology": receipt["error_typology"]}, indent=2))
    print(f"receipt -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
