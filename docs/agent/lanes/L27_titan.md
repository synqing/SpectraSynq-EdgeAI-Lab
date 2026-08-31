---
abstract: "L27: no Titan board numbers. 1 ms NPU is PRE-SILICON hypothetical. 100 ms is PaRIRset HOST-ONLY. 50 ms is K1 C0-v2 cadence, not U55. MERT/MuQ/MAEST/Demucs stay off Titan."
---

# L27 — TITAN_BRINGUP, no invented numbers

**Lane:** L27. **Write-only this file.** Cadence silicon **CLOSED**. No USB. No `/dev/cu.usbmodem*`. No flash. No room audio. No 8 s loop.

**HARD FAIL (`SAME_SONG_LOOP_MAX_15MIN`, Captain 2026-08-31).** This lane played nothing.

## Contract

STATUS: **PASS (audit)** — no ON-SILICON Titan stamp exists; three lookalike numbers are labelled and banned as board latency; teacher nets stay off Titan.
CLAIM: Titan Mini is **PRE-SILICON**. No RA8P1 on the desk. Do not quote latency from `docs/TITAN_BRINGUP.md`. Golden pass-band is **HOST-ONLY** until a board run fills **ON-SILICON**. GHA 33319114336 C99 is **PRE-SILICON**, not a board clock. p50/p95/p99/µs cells are empty by design.
CLAIM: Ban quoting **1 ms NPU**, **100 ms PaRIRset**, **50 ms K1 cadence** as Titan board latency. They are three different objects (see stamp table).
CLAIM: Do not put **MERT / MuQ / MAEST / Demucs** on Titan / U55 / PDM. Teachers are HOST oracle only. Export a CNN student, not the teacher, and only after `docs/mir/SELECTION_GATE.md`.
EVIDENCE: `docs/TITAN_BRINGUP.md`; `docs/ruhmi/COMPILE_RECEIPT.md`; `docs/AMENDMENT_002.md`; `docs/mir/PARIRSET_ONSET_ALIGNED.md`; `docs/mir/GATE_C0_CADENCE.md`; `docs/AMENDMENT_001_DELTA.md`; `docs/mir/LANDSCAPE.md`; `Agents.md`; this file.
COMMAND: none (HOST grep/read only). Cadence CLOSED. No USB. No flash. No room audio. Did not re-run PaRIRset, RUHMI, or cadence.
METHOD_RISK: `TITAN_BRINGUP.md` already forbids quoting latency, then writes “even if the NPU runs in 1 ms” next to 100 ms and 50 ms. That sentence is the lookalike. Compiler RAM/Flash/MACs from GHA are also not Titan. Cadence 50 ms is K1 ON-SILICON pixels, not U55.
NEXT: Do not cite 1 ms as U55. If L60–61 is edited, stamp 100 ms `HOST-ONLY` and 1 ms `PRE-SILICON hypothetical`. Fill p50/p95 only from a flashed image labelled `ON-SILICON`. Keep MERT/MuQ/MAEST/Demucs off the board.

## Stamp table (the three lookalikes)

| Number | Where it lives | Correct stamp | What it is **not** |
| --- | --- | --- | --- |
| **1 ms** NPU | `docs/TITAN_BRINGUP.md` L61: “even if the NPU runs in 1 ms” | **PRE-SILICON hypothetical.** Never measured. File L9: do not quote latency. | Titan / U55 / RA8P1 board latency |
| **100 ms** acoustic path | `docs/TITAN_BRINGUP.md` L60; AMENDMENT_002; PARIRSET_ONSET_ALIGNED (mean direct-path **99.7 ms**, envelope ~96 ms) | **HOST-ONLY.** Three short PaRIRset test IRs (`argmax \|h\|`). Not algorithm latency. | Titan mic delay, U55, K1 cadence cell |
| **50 ms** visual-sync / added delay | `docs/TITAN_BRINGUP.md` L61 “50 ms visual sync budget”; `docs/mir/GATE_C0_CADENCE.md` 20 Hz + 50 ms **PASS**, 20 Hz + 100 ms **FAIL**, 5 Hz + 50 ms **FAIL** | **ON-SILICON K1 C0-v2 cadence** (product firmware, Cadence **CLOSED**). Host 50 ms is a **different** FAIL (`GATE_C_CADENCE_HOST`). | Titan U55 inference, PaRIRset path, a student that also assumes 5 Hz |
| **1 kHz** | `docs/TITAN_BRINGUP.md` L73 | Anti-default. Semantic update rate is measured, not 1 kHz. | A Titan NPU rate |

Cadence 50 ms must not be folded into “the NPU has 50 ms.” PaRIRset 100 ms must not be folded into “the model is slow.” The 1 ms clause must not be folded into either.

## What is already true (not a board)

- **PRE-SILICON C99:** GHA 33319114336 compiled `ad01_int8.tflite` and lab `smoke.onnx` (AdaptiveAvgPool2d). Pin `6c5aad901a1a41e28f6e306bfc35c44659e89502`, MERA `2.6.0+pkg.4815`. Receipt: `docs/ruhmi/COMPILE_RECEIPT.md`. Compiler RAM/Flash/MACs (768 B / 262,414 B, …) are **not** Titan measurements. L13 owns pin vs D9/D11.
- **HOST-ONLY golden band:** `artifacts/golden/test_XXX/` vs `expected_int8_output.json` until first board fills `ON-SILICON` (`TITAN_BRINGUP.md` L39).
- **HOST oracle replay:** `docs/mir/visual_replay/index.html` — not a product lighting judgement, not on-device A/B.
- **Ship path** already in `TITAN_BRINGUP.md` L97–102: golden first, PDM last; who acts; shipped = flashed image matching golden within a measured band, labelled `ON-SILICON`, and M85 DSP deadlines still hold with NPU running.

## Banned on Titan (teachers)

`Agents.md`, Amendment 001 deferred list, LANDSCAPE: **MERT / MuQ / MAEST / Demucs** are HOST teachers / oracles. Do not put 95M transformers on U55. Do not reconstruct waveforms on silicon. Demucs lane is HOST-only (`docs/agent/lanes/L35_demucs.md`). Streaming student sketches are HOST, not Titan (`Agents.md` share-student lane).

## Not this lane

Cadence cells (L18/L33/L40). RUHMI pin (L13). Demucs licence (L35). MODEL_CONTRACT blanks (L25). USB ownership (L38). Serial Studio (L17). No invented p50. No invented NPU ms.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:grok | L27 contract. 1 ms NPU is PRE-SILICON lookalike. |
| 2026-08-31 | agent:grok-ssa-l27 | Re-derived stamps; ban 1 ms / 100 ms / 50 ms as Titan; teachers off board. |
