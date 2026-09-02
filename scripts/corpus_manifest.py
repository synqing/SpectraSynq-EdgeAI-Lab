#!/usr/bin/env python3
"""MIR-CORPUS-01 - build the corpus authority manifest.

Consumes the extracted Slakh2100 metadata (MIDI + metadata.yaml) and the
consumed-BabySlakh fingerprint record, and produces the machine-readable
authority manifest: identity, provenance, official split, exclusion status and
pool assignment for every song.

Freshness is decided on MUSICAL CONTENT, not Track ID, using three keys that are
cross-checked rather than trusted individually:
  1. Track ID           - weakest; the brief states it is insufficient on its own
  2. UUID / lmd_midi_dir - Slakh's own provenance key for the source Lakh MIDI
  3. symbolic fingerprint - independent canonical event-content hash

This is DATA GOVERNANCE. It runs no representation, scores no model and tests no
hypothesis.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import j3g_common as C  # noqa: E402
from corpus_fingerprint import fingerprint, provenance  # noqa: E402

POOL = {"train": "DEVELOPMENT_AVAILABLE", "validation": "VALIDATION_SEALED", "test": "TEST_SEALED"}
EXCLUDED = "EXCLUDED_CONSUMED_OR_DUPLICATE"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus-root", type=Path, required=True,
                    help="extracted Slakh2100 tree containing train/ validation/ test/")
    ap.add_argument("--consumed", type=Path, required=True,
                    help="CONSUMED_BABYSLAKH_FINGERPRINTS.json")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--archive-md5", type=str, default="NOT_VERIFIED")
    args = ap.parse_args()

    consumed = json.loads(args.consumed.read_text())
    consumed_fp = {s["fingerprint_sha256"]: s["track_id"] for s in consumed["songs"]}
    consumed_uuid = {s["uuid"]: s["track_id"] for s in consumed["songs"] if s.get("uuid")}

    rows = []
    for d in sorted(p for p in args.corpus_root.rglob("*")
                    if p.is_dir() and (p / "all_src.mid").is_file()):
        split = next((s for s in ("train", "validation", "test") if s in d.parts), None)
        prov = provenance(d)
        fp = fingerprint(d / "all_src.mid")
        fams = Counter(C.family_of(p) for p in prov.get("programs_rendered", []))
        rows.append({"track_id": d.name, "official_split": split, **prov, **fp,
                     "family_counts": dict(sorted(fams.items()))})

    by_fp, by_uuid = defaultdict(list), defaultdict(list)
    for r in rows:
        by_fp[r["fingerprint_sha256"]].append(r["track_id"])
        if r.get("uuid"):
            by_uuid[r["uuid"]].append(r["track_id"])
    fp_dupes = {k: v for k, v in by_fp.items() if len(v) > 1}
    uuid_dupes = {k: v for k, v in by_uuid.items() if len(v) > 1}

    # cross-check the two independent keys before either is used to exclude anything
    disagree = []
    for u, ids in by_uuid.items():
        fps = {r["fingerprint_sha256"] for r in rows if r["track_id"] in ids}
        if len(fps) > 1:
            disagree.append({"uuid": u, "track_ids": ids, "distinct_fingerprints": len(fps)})

    # exclusion: consumed overlap by EITHER key, plus all but one member of each
    # internal duplicate group (the survivor is the lexicographically first Track ID)
    keep_of_group = {}
    for k, ids in {**fp_dupes}.items():
        keep_of_group[k] = sorted(ids)[0]

    n_by_status = Counter()
    for r in rows:
        why = []
        if r["fingerprint_sha256"] in consumed_fp:
            why.append(f"fingerprint matches consumed {consumed_fp[r['fingerprint_sha256']]}")
        if r.get("uuid") in consumed_uuid:
            why.append(f"UUID matches consumed {consumed_uuid[r['uuid']]}")
        grp = by_fp[r["fingerprint_sha256"]]
        if len(grp) > 1 and r["track_id"] != keep_of_group[r["fingerprint_sha256"]]:
            why.append(f"internal duplicate of {keep_of_group[r['fingerprint_sha256']]}")
        r["exclusion_reasons"] = why
        r["overlaps_consumed_babyslakh"] = bool(
            r["fingerprint_sha256"] in consumed_fp or r.get("uuid") in consumed_uuid)
        r["status"] = EXCLUDED if why else POOL.get(r["official_split"], "UNASSIGNED")
        n_by_status[r["status"]] += 1

    fam_totals = defaultdict(Counter)
    for r in rows:
        for fam, n in r["family_counts"].items():
            fam_totals[r["status"]][fam] += n

    payload = {
        "schema": "spectrasynq.corpus_authority.v1",
        "job": "MIR-CORPUS-01",
        "label": "CORPUS AUTHORITY MANIFEST. Data governance. No representation run, no model scored, no hypothesis tested.",
        "dataset": {
            "name": "Slakh2100-16k (slakh2100_redux_16k)",
            "zenodo_record": "7708270",
            "doi": "10.5281/zenodo.7708270",
            "licence": "CC BY 4.0",
            "published_md5": "66a2301ed7b4d5f4f6d3383474e546c6",
            "archive_md5_as_received": args.archive_md5,
            "md5_verified": args.archive_md5 == "66a2301ed7b4d5f4f6d3383474e546c6",
            "local_corpus_root": str(args.corpus_root),
        },
        "freshness_method": {
            "keys": ["Track ID (insufficient alone)",
                     "UUID / lmd_midi_dir (Slakh's own provenance for the source Lakh MIDI)",
                     "symbolic content fingerprint (independent canonical event hash)"],
            "cross_checked": True,
            "uuid_and_fingerprint_disagreements": disagree,
            "note": "any disagreement between the two independent keys is reported, not silently resolved",
        },
        "totals": {
            "n_songs_indexed": len(rows),
            "n_distinct_fingerprints": len(by_fp),
            "n_distinct_uuids": len(by_uuid),
            "n_duplicate_fingerprint_groups": len(fp_dupes),
            "n_duplicate_uuid_groups": len(uuid_dupes),
            "by_status": dict(n_by_status),
        },
        "duplicate_fingerprint_groups": fp_dupes,
        "duplicate_uuid_groups": uuid_dupes,
        "family_inventory_by_status": {k: dict(sorted(v.items())) for k, v in fam_totals.items()},
        "pool_definitions": {
            "DEVELOPMENT_AVAILABLE": "eligible official TRAIN tracks; allocate to future exploratory jobs in explicitly recorded batches",
            "VALIDATION_SEALED": "eligible official VALIDATION tracks; pre-registered confirmation only, for a candidate that has already earned validation",
            "TEST_SEALED": "eligible official TEST tracks; do not inspect outcome metrics, tune against, or select examples from during normal development",
            EXCLUDED: "overlaps consumed BabySlakh content, or is an internal duplicate",
        },
        "official_splits_preserved": True,
        "new_random_split_created": False,
        "songs": rows,
        "analysis_run": False, "model_scored": False, "representation_run": False,
        "audio_committed": False, "feature_caches_committed": False,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps({"indexed": len(rows), "by_status": dict(n_by_status),
                      "fp_dupe_groups": len(fp_dupes), "uuid_dupe_groups": len(uuid_dupes),
                      "disagreements": len(disagree),
                      "md5_verified": payload["dataset"]["md5_verified"]}, indent=2))
    print(f"-> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
