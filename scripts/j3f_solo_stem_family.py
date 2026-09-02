#!/usr/bin/env python3
"""J3F addendum - SOLO-STEM observability by instrument family.

The purest frontend test available: for ONE pitched stem in isolation, how well
does host_chroma12's harmonic movement track that stem's OWN MIDI? No mixing at
all, no percussion, no other instrument. Any loss here is the frontend meeting
that timbre.

This fills the second clause of the pre-registered TIMBRE_FRONTEND_DOMINANT
condition ("the spread across families is material"), which the main J3F run
reported only as a timing spread.
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
sys.path.insert(0, str(ROOT / "scripts"))

from edgeai.mir.chroma_power import pitch_class_power, power_to_chroma12  # noqa: E402
from edgeai.mir.harmonic_movement import MOVEMENT_LAG_HOPS, pitch_class_state, tv_movement  # noqa: E402
from edgeai.mir.note_register import SR, Note, frame_grid  # noqa: E402
from j3f_observability import family_of, grouped_r2, stem_files  # noqa: E402

LAG = MOVEMENT_LAG_HOPS


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    import pretty_midi
    import soundfile as sf
    import yaml
    from scipy.stats import spearmanr

    rows = []
    for d in sorted(p for p in args.corpus.iterdir() if p.is_dir() and (p / "all_src.mid").is_file()):
        md = yaml.safe_load((d / "metadata.yaml").read_text())
        for f in stem_files(d):
            meta = md["stems"].get(f.stem, {})
            prog = int(meta.get("program_num", 0))
            if meta.get("is_drum") or prog >= 112:
                continue
            mf = d / "MIDI" / f"{f.stem}.mid"
            if not mf.is_file():
                continue
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
            st = pitch_class_state(notes, n)
            ch = power_to_chroma12(pitch_class_power(y)[:n]).astype(np.float64)
            Ms = tv_movement(st["pc_mass"])
            Ma = tv_movement(ch)
            sil = st["silent"]
            pair = np.zeros(n, dtype=bool)
            pair[LAG:] = (~sil[LAG:]) & (~sil[:-LAG])
            v = pair & np.isfinite(Ms) & np.isfinite(Ma)
            if v.sum() < 400:
                continue
            rows.append({"track": d.name, "stem": f.stem, "program": prog,
                         "instrument": meta.get("midi_program_name", "?"),
                         "family": family_of(prog),
                         "median_pitch": float(np.median([x.pitch for x in notes])),
                         "n_frames": int(v.sum()),
                         "Ms": Ms[v], "Ma": Ma[v]})

    by_fam = defaultdict(list)
    for r in rows:
        by_fam[r["family"]].append(r)

    fam = {}
    for name, rs in sorted(by_fam.items()):
        Ms = np.concatenate([r["Ms"] for r in rs])
        Ma = np.concatenate([r["Ma"] for r in rs])
        g = np.concatenate([np.full(len(r["Ms"]), f"{r['track']}:{r['stem']}") for r in rs])
        if len(np.unique(g)) < 3:
            continue
        fam[name] = {
            "n_stems": len(rs), "n_frames": int(len(Ms)),
            "solo_stem_r2": grouped_r2(Ma, Ms, g),
            "spearman": round(float(spearmanr(Ma, Ms).statistic), 4),
            "median_pitch": round(float(np.median([r["median_pitch"] for r in rs])), 1),
        }

    allMs = np.concatenate([r["Ms"] for r in rows])
    allMa = np.concatenate([r["Ma"] for r in rows])
    allg = np.concatenate([np.full(len(r["Ms"]), f"{r['track']}:{r['stem']}") for r in rows])
    overall = {"n_stems": len(rows), "n_frames": int(len(allMs)),
               "solo_stem_r2": grouped_r2(allMa, allMs, allg),
               "spearman": round(float(spearmanr(allMa, allMs).statistic), 4)}

    vals = [v["solo_stem_r2"] for v in fam.values()]
    spread = round(max(vals) - min(vals), 4) if vals else None
    # register split at the analytical resolution limit (MIDI 49, one bin per semitone)
    lo = [r for r in rows if r["median_pitch"] < 49]
    hi = [r for r in rows if r["median_pitch"] >= 49]
    reg = {}
    for lbl, rs in (("below_midi_49_unresolvable", lo), ("at_or_above_midi_49", hi)):
        if len(rs) >= 3:
            Ms = np.concatenate([r["Ms"] for r in rs])
            Ma = np.concatenate([r["Ma"] for r in rs])
            g = np.concatenate([np.full(len(r["Ms"]), f"{r['track']}:{r['stem']}") for r in rs])
            reg[lbl] = {"n_stems": len(rs), "solo_stem_r2": grouped_r2(Ma, Ms, g)}

    out = {
        "schema": "spectrasynq.solo_stem_family.v1", "job": "J3F-addendum",
        "label": "HOST-ONLY AUDIO-INFORMATION FORENSIC",
        "question": "with NO mixing at all, how well does host_chroma12 track a single pitched stem's own harmonic movement?",
        "overall": overall, "by_family": fam,
        "family_r2_spread": spread,
        "spread_clause_of_TIMBRE_FRONTEND_DOMINANT": {
            "requirement": ">= 0.20", "met": bool(spread is not None and spread >= 0.20)},
        "by_register_split_at_the_analytical_resolution_limit": reg,
        "student_io_frozen": False, "titan": False, "production_firmware_changed": False,
    }
    args.out.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: out[k] for k in
                      ("overall", "by_family", "family_r2_spread",
                       "spread_clause_of_TIMBRE_FRONTEND_DOMINANT",
                       "by_register_split_at_the_analytical_resolution_limit")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
