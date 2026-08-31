---
abstract: "Arrival-day sequence for Titan Mini. Golden tensor first, PDM last. Hardware numbers do not exist until this runs on silicon."
---

# Titan Mini bring-up (designed, not run)

**HARD FAIL (`SAME_SONG_LOOP_MAX_15MIN`, Captain 2026-08-31).** Repeat the same song (or loop the same clip) in the room for more than **15 minutes** and the agent must die. Captain will destroy them by setting them on fire. Kill the player. Do not continue.

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

When the board exists, record **on-silicon** (not host), and keep these
latency buckets **separate**:

| bucket | meaning |
| --- | --- |
| algorithm latency | how long analysis/inference takes |
| context latency | how much past/future audio the semantic model needs |
| acoustic path delay | how long sound physically took to reach the mic (`acoustic_path_delay_s`) |
| output latency | how long before LEDs visibly change |

PaRIRset on three short test IRs: acoustic path delay ≈ **100 ms**. That can
wreck a 50 ms visual sync budget even if the NPU runs in 1 ms. Do not fold
it into “the model is slow.”

Also record:

- inference p50 / p95 / p99 / max (µs)
- update rate actually achieved
- SRAM / SDRAM / Flash from RUHMI metrics **and** from the running image
- NPU busy vs M85 busy vs both
- whether the deterministic DSP lane's deadlines still hold with the NPU running

The semantic lane is allowed to be slower than the audio callback. Target
update rate is a measured quantity, not 1 kHz by default.

## Visual experiment — do **not** wait for Titan

Oracle traces can modulate an isolated visual replay **now**:

```
recorded song + semantic_trace.jsonl
    → existing visual behaviour
    vs
    existing visual behaviour + one oracle signal
```

Format: `spectrasynq.semantic_trace.v1` (`src/edgeai/mir/semantic_trace.py`).
Required control: A baseline, B extra DoF from energy, C the same extra DoF
from the oracle. Source activity adds **D** = relative dominance (`*_share`).
If C does not beat B but D does, the student target is dominance from a mix,
not “are there drums.” If a *perfect* oracle does not beat energy on that
extra DoF, **do not train a student**.

Do not modify production firmware from this lab.

On-device A/B still happens later. Offline oracle replay is the early kill test.

## Remaining ship path (Titan not here)

1. Already in this repo / already PRE-SILICON: host train/export/quantize/golden pipeline; GHA 33319114336 C99 for `ad01_int8.tflite` and lab `smoke.onnx` (`docs/ruhmi/COMPILE_RECEIPT.md`). Host A/B/C oracle replay exists (`docs/mir/visual_replay/index.html`) — not a product lighting judgement.
2. Remaining: Titan on the desk; BSP NPU example boots; golden tensor → U55 vs `expected_int8_output.json`; WAV → M85 frontend → U55; PDM last; on-device visual A/B after an oracle has already failed-or-passed offline; M85 vs current-DSP goldens on the same PCM.
3. Who acts: this lab for compile/golden/offline oracle; whoever has the board for flash and on-silicon receipts; Captain for the product lighting judgement (not for “what did the LEDs render” if a dump exists).
4. Shipped on silicon means: a flashed Titan image whose U55 outputs match golden `expected_int8_output.json` within the measured band, with a receipt labelled `ON-SILICON`, **and** M85 DSP deadlines still hold while the NPU runs.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-30 | agent:edgeai | Arrival sequence; golden first, PDM last. |
| 2026-08-31 | agent:edgeai | Ship path: C99 already PRE-SILICON; A/B/C offline control. |
| 2026-08-31 | agent:edgeai | Acoustic path delay is its own latency bucket; source A/B/C/D. |
