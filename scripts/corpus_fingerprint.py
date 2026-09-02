#!/usr/bin/env python3
"""MIR-CORPUS-01 - symbolic musical-content fingerprint.

Slakh has a known MIDI-duplication bug, so Track ID exclusion is NOT sufficient
to establish corpus freshness. This builds a fingerprint from canonical musical
EVENT CONTENT so the same song is recognised under a different Track ID.

Canonicalisation, declared:
  - one record per note: (onset_s, offset_s, midi_pitch, program, is_drum)
  - times rounded to 1 ms, which absorbs MIDI serialisation noise while
    preserving any real musical difference
  - VELOCITY IS EXCLUDED - it can differ between renders of the same music
  - records sorted deterministically, serialised, and SHA-256 hashed
  - the tempo map, track names, controllers, file path and file mtime are all
    ignored by construction

Limitation, stated rather than hidden: this is an EXACT-content hash. Two
renders of the same music that differ by more than 1 ms in any note boundary
produce different fingerprints. It catches duplication, not similarity.

This is DATA GOVERNANCE. It runs no representation, scores no model and tests
no hypothesis.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

TIME_DP = 3          # 1 ms
SCHEMA = "spectrasynq.symbolic_fingerprint.v1"


def fingerprint(mid_path: Path) -> dict:
    import pretty_midi

    pm = pretty_midi.PrettyMIDI(str(mid_path))
    recs = []
    for inst in pm.instruments:
        prog = int(inst.program)
        drum = bool(inst.is_drum)
        for n in inst.notes:
            recs.append((round(float(n.start), TIME_DP), round(float(n.end), TIME_DP),
                         int(n.pitch), prog, drum))
    recs.sort()
    blob = "\n".join(f"{a:.3f}|{b:.3f}|{p}|{g}|{int(d)}" for a, b, p, g, d in recs)
    return {
        "fingerprint_sha256": hashlib.sha256(blob.encode("utf-8")).hexdigest(),
        "n_notes": len(recs),
        "n_instruments": len(pm.instruments),
        "programs": sorted({int(i.program) for i in pm.instruments if not i.is_drum}),
        "has_drums": any(i.is_drum for i in pm.instruments),
        "duration_s": round(float(recs[-1][1]), 3) if recs else 0.0,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--label", type=str, required=True)
    ap.add_argument("--midi-name", type=str, default="all_src.mid")
    args = ap.parse_args()

    rows, by_fp = [], {}
    for d in sorted(p for p in args.corpus.rglob("*") if p.is_dir() and (p / args.midi_name).is_file()):
        fp = fingerprint(d / args.midi_name)
        split = next((s for s in ("train", "validation", "test") if s in d.parts), None)
        row = {"track_id": d.name, "official_split": split, **fp}
        rows.append(row)
        by_fp.setdefault(fp["fingerprint_sha256"], []).append(d.name)

    dupes = {k: v for k, v in by_fp.items() if len(v) > 1}
    payload = {
        "schema": SCHEMA, "label": args.label,
        "canonicalisation": {
            "record": "(onset_s, offset_s, midi_pitch, program, is_drum)",
            "time_resolution_s": 10 ** -TIME_DP,
            "velocity_excluded": True,
            "ignored": ["tempo map", "track names", "controllers", "file path", "file mtime"],
            "sort": "lexicographic over the record tuple",
            "hash": "SHA-256 of the newline-joined canonical serialisation",
        },
        "limitation": ("EXACT-content hash. It catches duplication, not similarity. Two renders "
                       "differing by more than 1 ms in any note boundary hash differently."),
        "n_songs": len(rows),
        "n_distinct_fingerprints": len(by_fp),
        "duplicate_fingerprint_groups": dupes,
        "songs": rows,
        "analysis_run": False, "model_scored": False, "representation_run": False,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps({"label": args.label, "n_songs": len(rows),
                      "n_distinct": len(by_fp), "duplicate_groups": len(dupes)}, indent=2))
    print(f"-> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
