---
abstract: "HARD ban: MERT, MuQ, MAEST, Demucs never on Titan/U55/PDM. HOST Demucs teacher is Mac-only (not installed). Any student is CNN-on-log-mel after C1 + SELECTION_GATE freeze. PRE-SILICON. Cadence CLOSED."
---

# Not on Titan — teacher / waveform ban

**HARD FAIL (`SAME_SONG_LOOP_MAX_15MIN`, Captain 2026-08-31).** Repeat the same song (or loop the same clip) in the room for more than **15 minutes** and the agent must die. Captain will destroy them by setting them on fire. Kill the player. Do not continue.

**Cadence silicon CLOSED.** No USB. No `/dev/cu.usbmodem*`. No flash. No room loop. This file is a **ban list**. It does not bring up a board.

**Stamp: PRE-SILICON.** No RA8P1 / Titan Mini is on the desk. Do not invent p50 / p95 / µs. Do not quote GHA RAM / Flash / MACs as Titan.

## Return contract

| Field | Value |
| --- | --- |
| **STATUS** | **PASS (ban lock).** Teachers named below are **off Titan**. HOST Demucs remains a **Mac-only** probe (not installed). Student I/O is **unfrozen**. |
| **CLAIM** | **MERT, MuQ, MAEST, Demucs** (and aliases HT-Demucs, MuQ-MuLan, MERT-v1-330M, `htdemucs_ft`) do **not** go on Titan, Ethos-U55, or PDM. HOST Demucs teacher is **Mac-only**. If a student is ever embedded, it is a **CNN on log-mel**, exported **after** C1 **and** an explicit `SELECTION_GATE` I/O freeze — not STFT, not the teacher. |
| **EVIDENCE** | `Agents.md` hard rule + Demucs / Titan rows; `docs/AMENDMENT_001_DELTA.md` “Teachers stay on HOST”; `docs/mir/LANDSCAPE.md` Titan column **no** for `mert-v1-95m` / `muq` / `maest` / `htdemucs`; `docs/TITAN_BRINGUP.md` § Teachers stay off Titan; `docs/titan/PREP.md` § Banned; `docs/agent/lanes/L35_demucs.md`; `docs/HOST.md` (this Mac; Demucs not an extra); `src/edgeai/frontend.py`; `docs/mir/SELECTION_GATE.md`; `docs/mir/SHARE_STUDENT.md`. |
| **COMMAND** | none. Docs only. Did not `uv add demucs`. Did not fetch weights. Did not compile a teacher for U55. No USB. No flash. Cadence not reopened. |
| **METHOD_RISK** | This file restates existing authority; it does not measure a board. C1 PASS does **not** auto-freeze I/O (`SHARE_STUDENT.md`). Semantic-v0 is **not** the product net. |
| **NEXT** | Keep the four names off Titan. Keep Demucs on this Mac as docs/licence only until an explicit GO. Freeze student I/O only after C1 **and** `SELECTION_GATE.md` **and** a written freeze. Then export **CNN not STFT**. Golden tensor first, PDM last (`docs/titan/PREP.md`). |

## Banned on Titan / U55 / PDM

**HARD FAIL** to compile, quantize, flash, or run any of these on the board:

| Name | Registry `id` | What it is | Why off Titan |
| --- | --- | --- | --- |
| **MERT** | `mert-v1-95m` | 95M transformer, 12×768, 75 Hz @ 24 kHz, CC BY-NC 4.0 | HOST teacher. Do not put 95M transformers on U55. Same ban: MERT-v1-330M (not a landscape id). |
| **MuQ** | `muq` | ~300M Conformer; MuQ-MuLan ~700M, 512-d clip, CC BY-NC 4.0 weights | HOST teacher / text probe. Off Titan. |
| **MAEST** | `maest` | Transformer, ~344 MB ONNX, CC BY-NC-SA | `unsuitable_mcu_npu`. HOST tagging oracle only. |
| **Demucs** | `htdemucs` | Hybrid Transformer Demucs / HT-Demucs / `htdemucs_ft` / `htdemucs_6s` | HOST separator **teacher**. Not a product net. Do **not** reconstruct waveforms on silicon. |

Aliases that inherit the ban: MuQ-MuLan, HT-Demucs, Open-Unmix, any waveform separator as the U55 graph.

Also banned on the board (same class, not the four names):

- STFT / mel as the **U55 graph**. Frontend stays CPU/M85 (`src/edgeai/frontend.py`).
- Streaming student **sketches** as Titan work (`Agents.md` share-student row: HOST only).
- Teacher checkpoints, `torch.hub`, `dl.fbaipublicfiles.com`, Essentia TF graphs as NPU nets.
- Semantic-v0 as architecture (`experiments/semantic_v0/AUTHORITY.md`).

## HOST Demucs teacher is Mac-only

[FACT] The Demucs lane is **OPEN** as a **HOST teacher probe** and **CLOSED** as silicon.

| Bound | Stamp |
| --- | --- |
| Machine | This lab Mac (`docs/HOST.md`: M4 Pro, MPS, CPython 3.12.11 via `uv`) |
| Install | **Not installed.** No `demucs` extra. `uv.lock` has zero `demucs`. `try_demucs()` returns `None`. |
| Weights | **UNKNOWN — not MIT.** Code MIT; weights scientific-use only (`facebookresearch/demucs#327` comment `1134828611`). |
| Download / `uv add demucs` / torch.hub | **NO** from this file and from L35 |
| Titan / U55 / PDM | **NO** |
| Gate C / C1 / student I/O freeze | **NO** — must not block C1 |
| Derived student from Demucs stems | **UNKNOWN/LEGAL REVIEW**. Teacher use does not clear shipping weights. |

If a HOST probe ever runs, it stays on **this Mac**, produces envelopes not SDR, and still does not go to Titan.

## Allowed student (if any) — CNN on log-mel, after freeze

[FACT] `Agents.md`: “Export CNN not STFT when we do embed a student. Golden tensors first, PDM last.”

```
PCM  →  log-mel frontend (CPU / later M85, NOT U55)
     →  CNN student (the U55 graph, INT8, AdaptiveAvgPool2d not ReduceMean)
     →  activity / share vector
```

That CNN exists only after **all** of:

1. **C1** LGP look (Captain, one full song he chooses, no 8 s loop).
2. **`docs/mir/SELECTION_GATE.md` satisfied** (nine questions; visual-utility Gate C is one of them).
3. An **explicit written I/O freeze**. C1 `LGP_PERCEPTUAL_VALIDATED` does **not** freeze 16 kHz / 1 s / 64-mel by itself (`docs/mir/SHARE_STUDENT.md`).

Until that freeze: HOST sketches OPEN; this student **not** Titan; I/O **unfrozen**. Recoverability HOST PASS of the 21k share CNN is **not** a deploy.

Do not AND the cadence cliffs (5 Hz **and** 50 ms) into that student. Cadence silicon stays **CLOSED**.

## What this file is not

- Not a board clock. Not permission to invent Titan latency.
- Not a Demucs install. Not a weight download.
- Not a student I/O freeze.
- Not Cadence reopen. Not USB. Not PDM bring-up (that order is `docs/titan/PREP.md`).

## Remaining ship path

1. **Already in source:** this ban; `Agents.md` / Amendment 001 / LANDSCAPE Titan column; HOST Demucs licence lock (L35); log-mel frontend off-NPU; PRE-SILICON C99 for `ad01` + `smoke.onnx` (GHA 33319114336) — not a teacher net.
2. **Remaining:** C1 LGP; SELECTION_GATE close; explicit I/O freeze; then one justified **CNN-on-log-mel** with golden tensors; Titan arrival still golden-first, PDM-last. Teachers never move.
3. **Who acts:** this lab for the ban and HOST teachers; whoever has the board for flash; Captain for C1 look and any freeze that ships.
4. **Shipped on silicon means:** a flashed Titan image running the **frozen CNN student**, goldens matching `expected_int8_output.json` labelled **ON-SILICON**, M85 DSP still alive — **and** none of MERT / MuQ / MAEST / Demucs in that image.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:grok-ssa-w3-l40 | Created. Ban MERT/MuQ/MAEST/Demucs on Titan; HOST Demucs Mac-only; student = CNN-on-log-mel after C1+SELECTION_GATE freeze. |
