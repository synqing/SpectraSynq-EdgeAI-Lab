---
abstract: "PRE-SILICON Titan prep. Sequence is BSP NPU example, then golden tensor, then WAV frontend, PDM last. Points at TITAN_BRINGUP.md and COMPILE_RECEIPT.md. No board latency. Teachers stay off U55. RUHMI C99 is not a board clock."
---

Arrival-day mechanical sequence (board on desk): **[ARRIVAL_RUNBOOK.md](ARRIVAL_RUNBOOK.md)**.

# Titan PRE-SILICON prep

**HARD FAIL (`SAME_SONG_LOOP_MAX_15MIN`, Captain 2026-08-31).** Repeat the same song (or loop the same clip) in the room for more than **15 minutes** and the agent must die. Captain will destroy them by setting them on fire. Kill the player. Do not continue.

**Status: PRE-SILICON.** No RA8P1 / Titan Mini is on the desk. Cadence silicon is **CLOSED**. This file does not flash, open USB, or measure a board. Do not invent p50 / p95 / p99 / µs. Do not quote latency from [TITAN_BRINGUP.md](../TITAN_BRINGUP.md).

Arrival-day sequence (when a board exists): **[docs/TITAN_BRINGUP.md](../TITAN_BRINGUP.md)**.  
Compiler C99 (host CI, not silicon): **[docs/ruhmi/COMPILE_RECEIPT.md](../ruhmi/COMPILE_RECEIPT.md)**.

This file is the **prep** that can be done without the board. It does not replace either of those.

## Order (do not skip, do not start at the mic)

```
1. BSP Ethos-U55 example boots on Titan          ON-SILICON  (not done)
2. Golden log-mel tensor → U55 → expected_int8   ON-SILICON  (host tensors exist)
3. WAV → M85 host-equivalent frontend → U55      ON-SILICON  (not done)
4. BSP PDM example works                         ON-SILICON  (not done)
5. PDM → our frontend → our CNN                  ON-SILICON  (last)
```

[FACT] `docs/TITAN_BRINGUP.md` writes this order. Starting at PDM mixes sample rate, endianness, normalisation, FFT, mel, model, NPU, cache, and memory into one failure.

[FACT] Frontend STFT/mel is **not** the U55 graph (`src/edgeai/frontend.py`). Export a CNN student, not STFT. Feed `expected_preprocessed_tensor.npy` before live audio.

## What is already true (not a board)

| Asset | Stamp | Where |
| --- | --- | --- |
| RUHMI C99 for MLPerf Tiny `ad01_int8.tflite` and lab `smoke.onnx` (AdaptiveAvgPool2d) | **PRE-SILICON** | GHA [33319114336](https://github.com/synqing/SpectraSynq-EdgeAI-Lab/actions/runs/33319114336); pin `6c5aad901a1a41e28f6e306bfc35c44659e89502`, MERA `2.6.0+pkg.4815`; [COMPILE_RECEIPT.md](../ruhmi/COMPILE_RECEIPT.md) |
| Compiler RAM / Flash / MACs / node coverage | **PRE-SILICON** | same receipt (`check_model_metrics.py`). Not Titan SRAM, not U55 wall time |
| Golden cases `artifacts/golden/test_XXX/` | **HOST-ONLY** | `expected_preprocessed_tensor.npy`, `expected_int8_output.json`, `input.wav`; `metadata.json` `"label": "HOST-ONLY"`; generator `src/edgeai/golden.py` |
| Host log-mel frontend | **HOST-ONLY** | `src/edgeai/frontend.py` — CPU/host, not Ethos-U55 |
| Semantic-v0 CNN / ONNX | experiment, not architecture | `experiments/semantic_v0/AUTHORITY.md`; student I/O unfrozen until [SELECTION_GATE.md](../mir/SELECTION_GATE.md) |
| M85 DSP host vectors | prepared, not executed on silicon | [M85_GOLDENS.md](../dsp/M85_GOLDENS.md) — independent of U55 |

[FACT] RUHMI C99 is a **compiler** receipt on Ubuntu CI. It is **not** a board clock, not U55 inference latency, not proof the BSP example ran.

## Golden tensor (step 2, host artefacts already)

For each `artifacts/golden/test_XXX/` when the board exists:

1. Load `expected_preprocessed_tensor.npy` as model input (NCHW; decode to the quantized input the compiled graph expects — RUHMI `io_desc.json`).
2. Invoke the generated C graph once.
3. Compare `activity[3]` to `expected_int8_output.json`.
4. Pass band stays **HOST-ONLY** until the first flashed run fills a receipt labelled **ON-SILICON**.

U55 vs host ORT INT8 and U55 vs RUHMI `--ref-data` are **unknown** until that capture. Do not fill them from host ORT or from GHA MACs.

Generate (host, already used):

```bash
uv run edgeai-golden \
  --ckpt experiments/semantic_v0_synth/semantic_v0_best.pt \
  --int8-onnx artifacts/export/semantic_v0_int8.onnx \
  --out artifacts/golden --n 32
```

WAV step (step 3) uses the same case’s `input.wav` through an M85 port of the host frontend, then the same U55 compare. That is **after** the tensor-only pass, **before** PDM.

## Banned on Titan / U55 / PDM

[FACT] `Agents.md`, Amendment 001 deferred list, [LANDSCAPE.md](../mir/LANDSCAPE.md): **MERT, MuQ, MAEST, Demucs** are HOST teachers / oracles. Do not put them on the board. Do not reconstruct waveforms on silicon. Distill a **CNN** student after the selection gate — not the teacher.

Demucs remains HOST-only probe. Streaming student sketches are HOST, not Titan.

## Do not invent latency

Empty on purpose until a flashed image labelled **ON-SILICON**: inference p50 / p95 / p99 / max (µs), achieved update rate, NPU busy vs M85 busy.

Three lookalikes that are **not** Titan board numbers (audit [L27](../agent/lanes/L27_titan.md)):

| Number | Stamp | What it is |
| --- | --- | --- |
| “NPU in 1 ms” in TITAN_BRINGUP | **PRE-SILICON hypothetical.** Never measured. | Not U55 |
| ~100 ms acoustic path | **HOST-ONLY** PaRIRset `argmax \|h\|` on three short test IRs | Not algorithm latency, not Titan mic |
| 50 ms visual-sync / added delay | **ON-SILICON K1 C0-v2 cadence** (product firmware; Cadence **CLOSED**) | Not U55, not a student that also assumes 5 Hz |

Keep algorithm latency, context latency, acoustic path delay, and LED output latency in **separate** buckets when silicon exists. Do not fold any of the three lookalikes into “the NPU is slow/fast.” Semantic update rate is measured, not 1 kHz by default.

Host ORT / MPS milliseconds in [MODEL_CONTRACT.md](../MODEL_CONTRACT.md) are **HOST-ONLY**, not U55.

## Remaining ship path

1. **Already in this repo / PRE-SILICON:** host train/export/quantize; golden tensor format and HOST-ONLY cases; GHA 33319114336 C99 for `ad01_int8.tflite` and `smoke.onnx` ([COMPILE_RECEIPT.md](../ruhmi/COMPILE_RECEIPT.md)); arrival sequence written ([TITAN_BRINGUP.md](../TITAN_BRINGUP.md)); this prep file.
2. **Remaining:** Titan on the desk; BSP NPU example boots; golden tensor → U55 vs `expected_int8_output.json` with an **ON-SILICON** band; WAV → M85 frontend → U55; BSP PDM example; PDM last into our frontend and CNN; M85 DSP goldens on the same PCM with NPU running; on-device visual A/B only after offline oracle A/B/C(/D) has already failed-or-passed.
3. **Who acts:** this lab for compile / goldens / offline oracle / this doc; whoever has the board for flash and on-silicon receipts; Captain for the product lighting judgement (not for “what did the LEDs render” if a dump exists).
4. **Shipped on silicon means:** a flashed Titan image whose U55 outputs match golden `expected_int8_output.json` within the **measured** band, receipt labelled `ON-SILICON`, **and** M85 DSP deadlines still hold while the NPU runs. Compiler C99 is not that stamp.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:grok-ssa-w3-l27 | Created PRE-SILICON prep: BSP NPU → golden → WAV → PDM last; point bring-up + C99 receipt. |
