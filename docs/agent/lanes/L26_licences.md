---
abstract: "L26 UNKNOWN licence list from mir/registry.yaml. 13/23 entries, 28 UNKNOWN-bearing fields. Code ≠ weights ≠ dataset. Teacher use does not clear student weights. No clearances. Not legal advice. HOST docs only."
---

# L26 — registry licence UNKNOWN list

**Lane:** L26. **Write-only this file.** Cadence CLOSED. No USB. No download. No playback. No 8 s loop.

**Source:** `/Users/spectrasynq/SpectraSynq-EdgeAI-Lab/mir/registry.yaml` (`schema_version: 1`, `updated: 2026-08-31`). 23 `entries`. Header: **code licence ≠ weight licence ≠ dataset licence**; **UNKNOWN is allowed**; not legal advice.

**Method:** Read the YAML. Count `id:` keys. Transcribe every field whose value contains the token `UNKNOWN`. Did not fetch SPDX, GitHub, HF cards, or vendor terms. Did not invent a clearance.

## Contract (10 lines)

STATUS: PASS (UNKNOWN inventory complete; zero fields cleared this lane)
CLAIM: 13 of 23 entries carry ≥1 UNKNOWN; 28 UNKNOWN-bearing field values; 0 SPDX pins; 0 product grants
EVIDENCE: `mir/registry.yaml` + this file
COMMAND: none (read-only YAML; no download, no USB, no playback)
METHOD_RISK: strings copied from registry, not re-verified upstream; not legal advice
NEXT: leave UNKNOWN as UNKNOWN; do not ingest CrowdioSet; do not freeze student I/O on teacher NC
HARD FAIL: `SAME_SONG_LOOP_MAX_15MIN` — no audio this lane
BOUND: code licence ≠ weight licence ≠ dataset licence; teacher_use ≠ derived_weight_status
CLEARANCES: none invented; essentia-models CC-SA vs CC-ND is CONFLICT, not UNKNOWN, not cleared
COUNTS: code 1 · weights 3 · dataset 3 · research 1 · commercial 7 · teacher 1 · derived 9 · redistribution 3

## Bound (this lane)

| Act | Bound |
| --- | --- |
| Treat code licence as weight licence | **NO** |
| Treat weight licence as dataset licence | **NO** |
| Treat teacher_use as derived-student clearance | **NO** |
| Ingest CrowdioSet | **NO** until per-file provenance |
| Invent a product grant from UNKNOWN | **NO** |
| Mix UNKNOWN/NC into a shipping student | **NO** |

## UNKNOWN entries (13 of 23)

`mirdata`, `essentia-models`, `discogs-effnet`, `maest`, `musicnn`, `mtg-jamendo`, `deam`, `mert-v1-95m`, `muq`, `htdemucs`, `banquet`, `crowdioset`, `msst`.

Split licence columns on those ids (verbatim registry sense). Empty cells mean that field is **not** UNKNOWN.

| id | code_licence | weight_licence | dataset_licence |
| --- | --- | --- | --- |
| `mirdata` | BSD-3-Clause | n/a | per-dataset (do not inherit BSD onto audio) |
| `essentia-models` | AGPLv3 for library | CONFLICT (SA vs ND), not UNKNOWN | mixed Discogs20 / Jamendo / DEAM |
| `discogs-effnet` | Essentia AGPLv3 | CC BY-NC-SA 4.0 | Discogs20 in-house |
| `maest` | check repo (not UNKNOWN) | CC BY-NC-SA 4.0 | Discogs20 |
| `musicnn` | ISC | **UNKNOWN** (repo weights; MTT/MSD) | MTT / MSD (MSD not freely redistributable) |
| `mtg-jamendo` | metadata repo CC BY-NC-SA 4.0 | n/a | **UNKNOWN** commercial (Jamendo CC mix, some NC; metadata NC-SA) |
| `deam` | n/a | n/a | **UNKNOWN** commercial (FMA/Jamendo/MedleyDB; pages mix BY-NC) |
| `mert-v1-95m` | Apache-2.0 | CC BY-NC 4.0 | 20k hours (not public dump) |
| `muq` | MIT | CC BY-NC 4.0 | MSD-scale proprietary |
| `htdemucs` | MIT | **UNKNOWN** — not MIT; #327 scientific-use only | MUSDB-HQ + 800 internal |
| `banquet` | MIT | **UNKNOWN** (not verified this session) | MoisesDB NC-SA |
| `crowdioset` | n/a | n/a | **UNKNOWN** until per-file provenance |
| `msst` | **UNKNOWN** until repo pin | per backend | per backend training set |

Worked examples of the three-way split: Demucs **code MIT ≠ weights UNKNOWN**; musicnn **code ISC ≠ weights UNKNOWN ≠ MSD audio**; MuQ **code MIT ≠ weights CC BY-NC**.

## UNKNOWN fields (28)

| id | field | registry value (verbatim sense) |
| --- | --- | --- |
| `mirdata` | `commercial_use` | library yes; datasets UNKNOWN per set |
| `essentia-models` | `teacher_use` | research yes; derived student UNKNOWN/LEGAL REVIEW |
| `essentia-models` | `derived_weight_status` | UNKNOWN/LEGAL REVIEW |
| `discogs-effnet` | `derived_weight_status` | UNKNOWN/LEGAL REVIEW |
| `maest` | `derived_weight_status` | UNKNOWN/LEGAL REVIEW |
| `musicnn` | `weight_licence` | UNKNOWN (weights shipped in repo; trained on MTT/MSD — MSD is not a clean commercial audio grant) |
| `musicnn` | `commercial_use` | UNKNOWN/LEGAL REVIEW (code ISC ≠ MSD audio) |
| `musicnn` | `derived_weight_status` | UNKNOWN/LEGAL REVIEW |
| `mtg-jamendo` | `dataset_licence` | audio from Jamendo CC mix (some NC); metadata NC-SA — treat commercial as mixed/UNKNOWN |
| `mtg-jamendo` | `commercial_use` | UNKNOWN (per-track CC) |
| `deam` | `dataset_licence` | CC audio sources (FMA/Jamendo/MedleyDB); pages list BY-NC and mixed — UNKNOWN commercial |
| `deam` | `commercial_use` | UNKNOWN |
| `mert-v1-95m` | `derived_weight_status` | UNKNOWN/LEGAL REVIEW |
| `muq` | `derived_weight_status` | UNKNOWN/LEGAL REVIEW |
| `htdemucs` | `weight_licence` | UNKNOWN — not MIT. Maintainer 2022-05-23 (#327): weights not covered by MIT, scientific purposes only. Conservative: research-only. |
| `htdemucs` | `derived_weight_status` | UNKNOWN/LEGAL REVIEW |
| `banquet` | `weight_licence` | UNKNOWN (not verified in this session) |
| `banquet` | `commercial_use` | UNKNOWN |
| `banquet` | `derived_weight_status` | UNKNOWN/LEGAL REVIEW |
| `banquet` | `redistribution` | UNKNOWN |
| `crowdioset` | `dataset_licence` | UNKNOWN until per-file provenance recorded |
| `crowdioset` | `research_use` | UNKNOWN |
| `crowdioset` | `commercial_use` | UNKNOWN |
| `crowdioset` | `redistribution` | UNKNOWN |
| `msst` | `code_licence` | UNKNOWN until repo pin |
| `msst` | `commercial_use` | UNKNOWN |
| `msst` | `derived_weight_status` | UNKNOWN/LEGAL REVIEW |
| `msst` | `redistribution` | UNKNOWN |

**Teacher use does not clear derived student weights.** Nine `derived_weight_status` values are `UNKNOWN/LEGAL REVIEW` even where `teacher_use` is research-yes: `essentia-models`, `discogs-effnet`, `maest`, `musicnn`, `mert-v1-95m`, `muq`, `htdemucs`, `banquet`, `msst`. Distillation from an NC or UNKNOWN teacher does not mint a product net.

## Not this lane

Ten entries have **no** UNKNOWN token: `librosa`, `mir_eval`, `essentia`, `musdb18`, `musdb-sample`, `medleydb`, `slakh2100`, `moisesdb`, `semantic-v0-experiment`, `parirset`. That is not a clearance. Several of those are still NC / educational / AGPL / check-repo.

`essentia-models` `weight_licence` is **CONFLICT** (models.html CC BY-NC-SA 4.0 vs licensing_information.html CC BY-NC-ND 4.0), not UNKNOWN. `maest` `code_licence` is `check repo`, not UNKNOWN.

Do not mix UNKNOWN/NC into a shipping corpus.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:grok-ssa-l26 | Created. 13/23 entries, 28 UNKNOWN fields from mir/registry.yaml. No clearances. |
| 2026-08-31 | agent:grok-ssa-l26 | Re-derived. Added UNKNOWN entry list + three-licence split table; teacher ≠ student bound. Counts unchanged. |
