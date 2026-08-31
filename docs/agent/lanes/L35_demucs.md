---
abstract: "L35 Demucs HOST teacher, docs/licence only. Code MIT; weights UNKNOWN (not MIT; #327 scientific-use, comment 1134828611). No download. Not Titan. Derived student UNKNOWN/LEGAL REVIEW."
---

# L35 — Demucs HOST teacher (licence contract)

**Lane:** L35. **Write-only this file.** Cadence CLOSED. No USB. No 8 s loop. No `pip`/`uv add demucs`. No weight fetch. No `torch.hub`. No Titan.

**HARD FAIL (`SAME_SONG_LOOP_MAX_15MIN`).** Same song/clip looped >15 min → agent dies. Unused this lane (no audio).

## Return contract

**STATUS:** PASS (docs/licence lock). Programme lane remains **OPEN** as HOST-only teacher *probe* (`AGENTS.md`). Weights **not installed**. This lane did **not** run a separator.

**CLAIM:** Code MIT ≠ weight licence. HT-Demucs weights are **UNKNOWN — not MIT** (scientific-use only, not a product grant). Teacher use does **not** clear a derived student. Demucs is **not** architecture, **not** Gate C, **not** C1, **not** a student I/O freeze, **not** Titan/U55/PDM. D14 still says Demucs **NO** until after recoverability and an explicit later GO; D22/AGENTS allow HOST probe **docs** now — not install.

**EVIDENCE:** this file + `mir/registry.yaml` `id: htdemucs` + `docs/mir/LANDSCAPE.md` §F + `docs/mir/SOURCE_ACTIVITY.md` + `docs/DECISIONS.md` D14 + `AGENTS.md` + `pyproject.toml` + `uv.lock` (no `demucs`) + `src/edgeai/mir/teachers.py::try_demucs` + `docs/mir/P3C_RECEIPT.json` `demucs_installed: false` + GitHub LICENSE + issue #327 comment 1134828611.

**COMMAND:** none. Docs/licence only. Did not `uv add demucs`. Did not call `demucs.api.Separator`. Did not hit torch.hub / `dl.fbaipublicfiles.com`. No USB, no flash, no Cadence reopen.

**METHOD_RISK:** Licence facts re-fetched from public GitHub (LICENSE raw + issues API). Not legal advice. PyPI “MIT” and Intel/HF “MIT weights” mirrors are **not** a Meta grant. A later HOST probe would still need an explicit GO and still would not go to Titan.

**NEXT:** Keep `weight_licence` UNKNOWN until counsel. Do not block C1. L09/L26 own the UNKNOWN census. Do not distill Demucs into a shipping net.

## Code vs weights [FACT]

| Layer | Status | Authority |
| --- | --- | --- |
| Code | **MIT** | `https://raw.githubusercontent.com/facebookresearch/demucs/main/LICENSE` — “MIT License / Copyright (c) Meta Platforms, Inc. and affiliates.” Repo **archived 2025-01-01**. Maintained fork `adefossez/demucs`. PyPI MIT covers **code**, not checkpoints. |
| Weights | **UNKNOWN — not MIT** | Maintainer `adefossez`, **2022-05-23T15:36:04Z**, `facebookresearch/demucs#327` comment `1134828611`: “The model weights are not covered by the MIT license, and are provided only for scientific purposes.” Issue still **Open**. No later maintainer superseding grant in that thread. |
| Intel/HF “MIT weights” | **not authority** | Same issue, 2024-06-08/09: third-party asked whether Intel OpenVINO MIT labels match “scientific purposes.” Maintainer did **not** re-grant. Do not treat those mirrors as clearance. |
| Training data | MUSDB-HQ + ~800 internal songs (registry) | MUSDB already `commercial_training_lineage: false`. Do not mix Demucs teacher outputs into a **shipping** student. |
| Derived student | `UNKNOWN/LEGAL REVIEW` | Teacher use ≠ clearance. `redistribution: weights unclear`. Do not freeze student I/O on Demucs stems. |

## Install state [FACT]

- `pyproject.toml` extras: `{musdb, mir, dev, silicon}` only. No `demucs`.
- `uv.lock`: **zero** `demucs` hits.
- `try_demucs()`: `import demucs.api` → `ImportError` → `None`. Leave it that way.
- `tests/test_teachers.py`: HPSS only; does not import Demucs.
- Receipts stamp `demucs_installed: false` (`docs/mir/P3C_RECEIPT.json`; P3-B/P3-C/sample scripts).
- `p3c_quant` stamp `"demucs": "NO"`.

## Role if ever used (not this lane)

HOST envelopes from stems → tiny student. Not SDR. Not waveforms on silicon. Not the separator on-device.

## Bound (this lane)

| Act | Bound |
| --- | --- |
| Download weights / `uv add demucs` / torch.hub | **NO** |
| Titan / U55 / PDM | **NO** |
| Block C1 / freeze student I/O | **NO** |
| Treat MIT code as MIT weights | **NO** |
| Derived student from Demucs teacher | **UNKNOWN/LEGAL REVIEW** |

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:grok-ssa-l35 | Created. HOST-teacher licence contract; no download; not Titan. |
| 2026-08-31 | agent:grok-ssa-l35 | Re-fetched LICENSE + #327 comment 1134828611; uv.lock/pyproject have no demucs; return contract STATUS/CLAIM/EVIDENCE/COMMAND/METHOD_RISK/NEXT. |
