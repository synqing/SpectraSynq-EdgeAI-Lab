---
abstract: "L35 Demucs HOST teacher, docs/licence only. Code MIT; weights UNKNOWN (not MIT; #327 scientific-use). No download. Not Titan. Derived student UNKNOWN/LEGAL REVIEW."
---

# L35 — Demucs HOST teacher (licence contract)

**Lane:** L35. **Write-only this file.** Cadence CLOSED. No USB. No 8 s loop. No `pip`/`uv add demucs`. No weight fetch. No Titan.

**HARD FAIL (`SAME_SONG_LOOP_MAX_15MIN`).** Same song/clip looped >15 min → agent dies.

## Contract (10 lines)

1. **STATUS:** OPEN as HOST-only teacher *probe* in `AGENTS.md`; **this lane PASS** as licence/docs lock. Weights **not installed**. `pyproject.toml` has no `demucs` extra. Receipts already stamp `demucs_installed: false`.
2. **CLAIM:** HT-Demucs (`htdemucs` / `_ft` / `_6s`) is a possible **HOST separator-as-teacher** (stem envelopes, not SDR, not waveforms on silicon). It is **not** architecture, **not** Gate C, **not** C1, **not** a student I/O freeze. D14 / SOURCE_ACTIVITY: Demucs **NO** until after recoverability and an explicit later GO.
3. **CODE LICENCE [FACT]:** MIT. `https://raw.githubusercontent.com/facebookresearch/demucs/main/LICENSE` — “MIT License / Copyright (c) Meta Platforms, Inc. and affiliates.” Repo archived 2025-01-01; maintained fork `adefossez/demucs`. PyPI MIT covers **code**, not checkpoints.
4. **WEIGHT LICENCE [FACT]:** **UNKNOWN — not MIT.** Maintainer `adefossez`, 2022-05-23, facebookresearch/demucs#327: “The model weights are not covered by the MIT license, and are provided only for scientific purposes.” Commercial **no**. Research **yes** if we accept that statement. No later superseding grant found. Intel/HF “MIT weights” mirrors are **not** authority.
5. **TRAINING DATA:** MUSDB-HQ + ~800 internal songs (registry). MUSDB is already `commercial_training_lineage: false`. Do not mix Demucs teacher outputs into a **shipping** student.
6. **DERIVED STUDENT:** `derived_weight_status: UNKNOWN/LEGAL REVIEW`. Teacher use ≠ clearance. `redistribution: weights unclear`. Do not freeze student I/O on Demucs stems.
7. **HOST vs TITAN:** HOST oracle only (`deployment: host_oracle`). **Do not put Demucs on Titan / U55 / PDM.** Do not reconstruct waveforms on silicon. Optional hook `src/edgeai/mir/teachers.py::try_demucs` returns `None` if uninstalled — leave it that way.
8. **EVIDENCE:** `mir/registry.yaml` `id: htdemucs`; `docs/mir/LANDSCAPE.md` §F; `docs/mir/SOURCE_ACTIVITY.md` (Demucs **NO**); `AGENTS.md` hard rule + Demucs lane; `docs/DECISIONS.md` D14; `pyproject.toml`; this file.
9. **COMMAND:** none. Docs/licence only. **Do not download.** No `demucs.api.Separator`. No torch.hub / dl.fbaipublicfiles. No USB, no flash, no Cadence reopen.
10. **NEXT / METHOD_RISK:** Keep `weight_licence` UNKNOWN until counsel. Do not block C1. L09/L26 own the UNKNOWN census. Later HOST probe (not this lane) would need an explicit GO, still not Titan. **Risk:** treating PyPI MIT or third-party “MIT weights” as a grant; distilling Demucs into a product net without legal review.

## Bound (this lane)

| Act | Bound |
| --- | --- |
| Download weights / `uv add demucs` | **NO** |
| Titan / U55 / PDM | **NO** |
| Block C1 / freeze student I/O | **NO** |
| Treat MIT code as MIT weights | **NO** |
| Derived student from Demucs teacher | **UNKNOWN/LEGAL REVIEW** |
| Role if ever used | HOST envelopes from stems, then tiny student — not the separator on-device |

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:grok-ssa-l35 | Created. HOST-teacher licence contract; no download; not Titan. |
