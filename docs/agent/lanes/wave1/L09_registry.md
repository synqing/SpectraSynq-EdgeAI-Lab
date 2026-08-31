---
abstract: "L09 MIR registry holes. 23 entries in mir/registry.yaml (schema 1, updated 2026-08-31). One blocked. Licence keys present; many values UNKNOWN/check/conflict. commercial_training_lineage missing on 19/23. HOST docs only. No USB."
---

# L09 — MIR registry holes

**Lane:** L09 (MIR registry holes). **Write-only this file.** Cadence CLOSED. No USB. No 8 s loop.

**Source:** `/Users/spectrasynq/SpectraSynq-EdgeAI-Lab/mir/registry.yaml` (`schema_version: 1`, `updated: 2026-08-31`). 23 `entries`. Header: code / weights / dataset licences are independent; `UNKNOWN` is allowed; `commercial_training_lineage: false` means never mix that audio/weights into a shipping student.

**Method:** Read YAML only. Counted `id:` keys and licence-related fields. Did not fetch GitHub/HF licences. Did not download corpora. Did not open USB.

## Contract (10 lines)

STATUS: PASS (holes enumerated; registry readable; no USB)
CLAIM: 23 entries; 1 blocked (`musicnn`); 19 missing `commercial_training_lineage`; 5 `code_licence` check/UNKNOWN; 1 weight-licence CONFLICT; CrowdioSet fully UNKNOWN; several derived-weight LEGAL REVIEW
EVIDENCE: `mir/registry.yaml` + this file
COMMAND: none (read-only YAML inventory)
METHOD_RISK: values transcribed, not re-fetched from upstream SPDX/cards
NEXT: pin `check repo` SPDX (L26 UNKNOWN list); do not ingest CrowdioSet; do not treat teacher NC as student clearance

## Blocked entries (status ≠ researched/executed)

| id | status | why (registry text) |
| --- | --- | --- |
| `musicnn` | **blocked** | TF1 + numpy&lt;1.17. Prefer Essentia `msd-musicnn.pb`. Weight licence UNKNOWN (MTT/MSD). Commercial UNKNOWN/LEGAL REVIEW. |

No other entry has `status: blocked`. Executed: `librosa`, `deam`, `musdb18`, `musdb-sample`, `semantic-v0-experiment`, `parirset`. Rest: `researched`.

## Missing / incomplete licence fields

All 23 entries have the nine keys (`code_licence`, `weight_licence`, `dataset_licence`, `research_use`, `commercial_use`, `teacher_use`, `derived_weight_status`, `attribution`, `redistribution`). Holes are **values**, plus the extra header field.

### `commercial_training_lineage` (header-defined, not on schema row)

Present on 4/23: `musdb18` false, `musdb-sample` false, `medleydb` false, `slakh2100` candidate-synth-only.

**Missing on 19:** `librosa`, `mir_eval`, `mirdata`, `essentia`, `essentia-models`, `discogs-effnet`, `maest`, `musicnn`, `mtg-jamendo`, `deam`, `mert-v1-95m`, `muq`, `moisesdb`, `htdemucs`, `banquet`, `semantic-v0-experiment`, `parirset`, `crowdioset`, `msst`.

NC / no-commercial entries that still lack the flag (should be `false` if we follow the header): `essentia-models`, `discogs-effnet`, `maest`, `mert-v1-95m`, `muq`, `mtg-jamendo`, `deam`, `moisesdb`, `htdemucs`, `banquet`, `musicnn`, `crowdioset`, `msst`.

### `code_licence` not pinned

| id | value |
| --- | --- |
| `mir_eval` | BSD-ish (check package) |
| `maest` | check repo |
| `medleydb` | medleydb loader (check repo) |
| `slakh2100` | generation repo (check) |
| `moisesdb` | library (check repo) |
| `msst` | UNKNOWN until repo pin |

### Weight / dataset / commercial UNKNOWN or conflict

| id | field | value |
| --- | --- | --- |
| `essentia-models` | `weight_licence` | **CONFLICT** — models.html CC BY-NC-SA 4.0 vs licensing_information.html CC BY-NC-ND 4.0 |
| `essentia-models` | `redistribution` | NC-SA/ND conflict |
| `essentia-models` | `derived_weight_status` | UNKNOWN/LEGAL REVIEW |
| `discogs-effnet` | `derived_weight_status` | UNKNOWN/LEGAL REVIEW |
| `maest` | `derived_weight_status` | UNKNOWN/LEGAL REVIEW |
| `musicnn` | `weight_licence` | UNKNOWN (repo weights; MTT/MSD) |
| `musicnn` | `commercial_use` | UNKNOWN/LEGAL REVIEW |
| `musicnn` | `derived_weight_status` | UNKNOWN/LEGAL REVIEW |
| `mtg-jamendo` | `dataset_licence` / `commercial_use` | Jamendo CC mix + metadata NC-SA; commercial UNKNOWN |
| `deam` | `dataset_licence` / `commercial_use` | mixed BY-NC; commercial UNKNOWN |
| `mert-v1-95m` | `derived_weight_status` | UNKNOWN/LEGAL REVIEW |
| `muq` | `derived_weight_status` | UNKNOWN/LEGAL REVIEW |
| `htdemucs` | `weight_licence` | UNKNOWN — not MIT; maintainer scientific-use only |
| `htdemucs` | `derived_weight_status` | UNKNOWN/LEGAL REVIEW |
| `htdemucs` | `redistribution` | weights unclear |
| `banquet` | `weight_licence` | UNKNOWN (not verified) |
| `banquet` | `commercial_use` / `redistribution` | UNKNOWN |
| `banquet` | `derived_weight_status` | UNKNOWN/LEGAL REVIEW |
| `crowdioset` | `dataset_licence` | UNKNOWN until per-file provenance |
| `crowdioset` | `research_use` / `commercial_use` / `redistribution` | UNKNOWN |
| `msst` | `commercial_use` / `redistribution` | UNKNOWN |
| `msst` | `derived_weight_status` | UNKNOWN/LEGAL REVIEW |

### Not holes (explicit n/a or clean grant)

`librosa` ISC / commercial yes. `essentia` AGPLv3 (product not free-by-default — filled, not missing). `parirset` CC0. `semantic-v0-experiment` proprietary experiment. `musdb18` / `musdb-sample` educational NC + lineage false.

## Bound (this lane)

Do not ingest CrowdioSet. Do not mix NC teachers into a shipping student. Teacher use ≠ derived-weight clearance. L26 owns the UNKNOWN licence list; this file owns the hole census vs the YAML.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:grok-ssa-l09 | Created. 23 entries, 1 blocked, licence holes from mir/registry.yaml. |
