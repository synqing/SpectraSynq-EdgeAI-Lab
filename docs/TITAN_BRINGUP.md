---
abstract: "Arrival-day sequence for Titan Mini. Golden tensor first, PDM last. Hardware numbers do not exist until this runs on silicon."
---

# Titan Mini bring-up (designed, not run)

**Status: PRE-SILICON.** No RA8P1 is on the desk. Do not quote latency from this file.

Board: Titan Mini, RA8P1, Cortex-M85 + M33, Ethos-U55, external SDRAM, PDM mic.
BSP reference projects exist for PDM capture and Ethos-U55 face-detection.

## Sequence

```
Titan boots
    → known NPU example from the BSP works
    → our golden log-mel tensor → U55 → compare expected_int8_output.json
    → our WAV → host-equivalent frontend on M85 → U55 → compare
    → Titan PDM example works
    → PDM → our frontend
    → PDM → our NPU model
    → live inference as an additive semantic lane
```

Do **not** start with the microphone. That mixes PDM, sample rate, endianness,
normalisation, FFT, mel, model, NPU, cache, and memory into one failure.

## Golden tensor protocol

For each `artifacts/golden/test_XXX/`:

1. Load `expected_preprocessed_tensor.npy` as the model input (NCHW float decoded
   to the quantized input the compiled graph expects — see RUHMI `io_desc.json`).
2. Invoke the generated C graph once.
3. Compare `activity[3]` to `expected_int8_output.json`.
4. Pass band: **HOST-ONLY until the first board run fills `ON-SILICON`**.

Suggested first tolerances (to be replaced by measured noise):

| Check | Start-here band | Replace when |
| --- | --- | --- |
| Host ORT INT8 vs PyTorch FP32 | recorded in `quant_report.json` | already measured on host |
| U55 vs host ORT INT8 | unknown | first silicon capture |
| U55 vs RUHMI `--ref-data` | unknown | first silicon capture |

## Benchmark harness (design)

When the board exists, record **on-silicon** (not host):

- inference p50 / p95 / p99 / max (µs)
- update rate actually achieved
- SRAM / SDRAM / Flash from RUHMI metrics **and** from the running image
- NPU busy vs M85 busy vs both
- whether the deterministic DSP lane's deadlines still hold with the NPU running

The semantic lane is allowed to be slower than the audio callback. Target
update rate is a measured quantity, not 1 kHz by default.

## Visual experiment (after live inference)

One existing visual mode, one new degree of freedom:

- `drum_activity` → spatial attack
- `vocal_activity` → palette persistence / cohesion
- `bass_activity` → low-frequency visual mass

A/B: engine vs engine+semantic. If it does not look more musically intelligent,
the F1 score is irrelevant.

## Remaining ship path (Titan not here)

1. Already in this repo: host train/export/quantize/golden **pipeline** (once Phase 1–6 scripts have been run on this Mac).
2. Remaining: x86 RUHMI compile producing C99; Titan on desk; BSP NPU example; golden tensor on U55; WAV path; PDM; one visual A/B.
3. Who acts: this lab for compile/golden; whoever flashes the Titan for on-silicon; Captain for the visual A/B judgement.
4. Shipped on silicon means: a flashed Titan image whose U55 outputs match golden `expected_int8_output.json` within the measured band, with a receipt labelled `ON-SILICON`.
