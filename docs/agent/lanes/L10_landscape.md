---
abstract: "L10 docs-only: LANDSCAPE.md vs mir/registry.yaml mismatches. 4 landscape-only names, 7 registry-only ids, 1 licence-string drift. Titan: MERT/MuQ/MAEST/Demucs stay off. No USB."
---

STATUS: FAIL_MISMATCH (HOST-ONLY, docs-only)
CLAIM: LANDSCAPE’s “primary sources are cited in `mir/registry.yaml`; this page is the map” is false. Same-entity facts mostly agree (including Titan **no** for MERT/MuQ/MAEST/Demucs). Four landscape names have no `id:`. Seven registry ids are not on the map. One licence string disagrees. Folded names are not absences. CLAP is out-of-list by LANDSCAPE’s own sentence, not a hole.
EVIDENCE: `/Users/spectrasynq/SpectraSynq-EdgeAI-Lab/docs/mir/LANDSCAPE.md` (changelog 2026-08-30) · `/Users/spectrasynq/SpectraSynq-EdgeAI-Lab/mir/registry.yaml` (`schema_version: 1`, `updated: 2026-08-31`, 23 `id:` rows)
COMMAND: none (read both files; no fetch, no download, no USB, no song)
METHOD_RISK: string inventory only — licences not re-fetched from SPDX/cards; numbers not re-measured
TITAN: both files keep MERT / MuQ / MAEST / HT-Demucs off Titan / U55 (`unsuitable_mcu_npu` or `host_oracle` + “Do not put on Titan”). Do not reverse that from this lane.
ONTOLOGY: LANDSCAPE already forbids inventing BUILDING until Jamendo tags fail. This lane invents neither BUILDING nor DROPPING.

## Same-entity contradictions (load-bearing)

| Topic | LANDSCAPE | registry | Class |
| --- | --- | --- | --- |
| Completeness | “Primary sources are cited in `mir/registry.yaml`. This page is the map.” | 23 ids; 7 never appear as map rows | **false map claim** |
| `mir_eval` licence | `BSD` | `BSD-ish (check package)` | **licence-string drift** (only one) |
| `musicnn` Titan vs deploy | Titan column: “student-sized, **not this TF1 graph**” | `deployment: potential_embedded_student` + `status: blocked` | **soft stance** — blocked TF1 graph vs student-family enum |

No other same-entity number/licence fight: librosa ISC; Essentia AGPL + commercial; models NC-SA vs NC-ND **CONFLICT**; musicnn 3 s / ISC code / weights UNKNOWN / TF1 blocked; Jamendo 87/40/56; DEAM 1802 @ 2 Hz mixed/UNKNOWN; Discogs-EffNet EffNet-B0 / CC BY-NC-SA / teacher; MAEST 5–30 s / ~344 MB / CC BY-NC-SA / Titan **no**; MERT-v1-95M 5 s / 75 Hz / 95M / CC BY-NC 4.0 / Titan **no**; MuQ ~25 Hz / ~300M MIT code + NC weights / Titan **no**; MuQ-MuLan 512-d / ~700M / Titan **no**; MUSDB18 academic/NC; MoisesDB 240 / CC BY-NC-SA + NC-RCL; HT-Demucs MIT code / #327 weights UNKNOWN / not Titan; Banquet 24.9M MIT / UNKNOWN weights.

## LANDSCAPE names with no registry `id:` (first-class, not folded)

| LANDSCAPE name | Where | Notes |
| --- | --- | --- |
| madmom | §A libraries | “research-oriented”; no licence, no id |
| MERT-v1-330M | §D table | 5 s / 75 Hz / 330M / CC BY-NC 4.0 / Titan **no**; sibling `mert-v1-95m` exists |
| Open-Unmix | §F table | “BSD-3 typically”; “check per checkpoint” |
| QSCNet (2025) | §F table | “~40% of Banquet params”; “not a host default yet” |

## Named in LANDSCAPE, folded under a family id (not a hole)

| LANDSCAPE name | Registry home |
| --- | --- |
| VGGish / MusiCNN / `msd-musicnn` `.pb` | `essentia-models` (+ `musicnn` spectrasynq prefers the `.pb`) |
| `deam-msd-musicnn` / `deam-audioset-vggish` | `essentia-models` task text “DEAM VA” — no own ids; LANDSCAPE extra: range ~[1,9] |
| MuQ-MuLan | `muq` (one id covers both) |
| HT-Demucs 6s | `htdemucs` versions `htdemucs / htdemucs_ft / htdemucs_6s` |
| MedleyDB (as DEAM audio source) | own id `medleydb` exists; not a landscape **row** |

CLAP-class: LANDSCAPE §E “exist **outside this list**” — not a registry mismatch.

## Registry `id:` absent from the LANDSCAPE map (7)

`musdb-sample` · `medleydb` (row) · `slakh2100` · `parirset` · `crowdioset` · `msst` · `semantic-v0-experiment` (LANDSCAPE one-liner only: synthetic training “is not that evidence”; registry: toolchain witness, not architecture authority — meaning aligned, id unmapped)

Cause: registry `updated: 2026-08-31` after LANDSCAPE changelog 2026-08-30 (venue/synth/student rows).

## Extra LANDSCAPE numbers registry does not state (not conflicts)

Jamendo “55k CC tracks” · Discogs-EffNet “~1–3 s patches” · DEAM heads “~[1,9]”.

ALIGNED ids (16): `librosa`, `mir_eval` (licence wording aside), `mirdata`, `essentia`, `essentia-models`, `discogs-effnet`, `maest`, `musicnn`, `mtg-jamendo`, `deam`, `mert-v1-95m`, `muq`, `musdb18`, `moisesdb`, `htdemucs`, `banquet`.

NEXT: Do not treat LANDSCAPE as registry authority until an editor (not this lane) either adds ids for madmom / MERT-v1-330M / Open-Unmix / QSCNet or deletes those names from LANDSCAPE, and adds map rows for the seven registry-only ids. Keep DEAM heads / VGGish folded or give them ids — pick one. Do not put MERT/MuQ/MAEST/Demucs on Titan. Do not invent BUILDING/DROPPING.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:grok | L10 mismatch contract. LANDSCAPE vs registry. |
| 2026-08-31 | agent:grok-build | Re-derived: CLAP out-of-list; folded ≠ missing; 4 landscape-only; 7 registry-only; mir_eval BSD drift; Titan still no. |
