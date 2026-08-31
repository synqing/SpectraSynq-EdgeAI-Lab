---
abstract: "L26 UNKNOWN licence list from mir/registry.yaml. 13/23 entries, 28 UNKNOWN-bearing fields. No clearances invented. Not legal advice. HOST docs only."
---

# L26 — registry licence UNKNOWN list

**Lane:** L26. **Write-only this file.** Cadence CLOSED. No USB. No playback. No 8 s loop.

**Source:** `/Users/spectrasynq/SpectraSynq-EdgeAI-Lab/mir/registry.yaml` (`schema_version: 1`, `updated: 2026-08-31`). 23 `entries`. Header: code / weights / dataset licences are independent; **UNKNOWN is allowed**; not legal advice.

**Method:** Grep `UNKNOWN` in that YAML. Transcribe field values. Did not fetch SPDX, GitHub, HF cards, or vendor terms. Did not invent a clearance.

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

## UNKNOWN fields (28)

| id | field | registry value (verbatim sense) |
| --- | --- | --- |
| `mirdata` | `commercial_use` | library yes; datasets UNKNOWN per set |
| `essentia-models` | `teacher_use` | research yes; derived student UNKNOWN/LEGAL REVIEW |
| `essentia-models` | `derived_weight_status` | UNKNOWN/LEGAL REVIEW |
| `discogs-effnet` | `derived_weight_status` | UNKNOWN/LEGAL REVIEW |
| `maest` | `derived_weight_status` | UNKNOWN/LEGAL REVIEW |
| `musicnn` | `weight_licence` | UNKNOWN (repo weights; MTT/MSD; MSD not a clean commercial audio grant) |
| `musicnn` | `commercial_use` | UNKNOWN/LEGAL REVIEW (code ISC ≠ MSD audio) |
| `musicnn` | `derived_weight_status` | UNKNOWN/LEGAL REVIEW |
| `mtg-jamendo` | `dataset_licence` | Jamendo CC mix (some NC); metadata NC-SA — treat commercial as mixed/UNKNOWN |
| `mtg-jamendo` | `commercial_use` | UNKNOWN (per-track CC) |
| `deam` | `dataset_licence` | CC sources (FMA/Jamendo/MedleyDB); pages list BY-NC and mixed — UNKNOWN commercial |
| `deam` | `commercial_use` | UNKNOWN |
| `mert-v1-95m` | `derived_weight_status` | UNKNOWN/LEGAL REVIEW |
| `muq` | `derived_weight_status` | UNKNOWN/LEGAL REVIEW |
| `htdemucs` | `weight_licence` | UNKNOWN — not MIT. Maintainer 2022-05-23 (#327): scientific purposes only. Conservative: research-only |
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

## Not this lane

Ten entries have **no** UNKNOWN token: `librosa`, `mir_eval`, `essentia`, `musdb18`, `musdb-sample`, `medleydb`, `slakh2100`, `moisesdb`, `semantic-v0-experiment`, `parirset`. That is not a clearance. `essentia-models` `weight_licence` is CONFLICT (CC BY-NC-SA vs CC BY-NC-ND), not UNKNOWN.

Teacher use does not clear derived student weights. Do not mix UNKNOWN/NC into a shipping corpus.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:grok-ssa-l26 | Created. 13/23 entries, 28 UNKNOWN fields from mir/registry.yaml. No clearances. |
