---
abstract: "PRE-SILICON Titan Mini arrival sequence. Golden tensor first, PDM last. 1 ms NPU is hypothetical, 100 ms is PaRIRset HOST-ONLY, 50 ms is K1 C0-v2 cadence — none are Titan board latency. MERT/MuQ/MAEST/Demucs stay off the board."
---

# Titan Mini bring-up — PRE-SILICON prep

**HARD FAIL (`SAME_SONG_LOOP_MAX_15MIN`, Captain 2026-08-31).** Repeat the same song (or loop the same clip) in the room for more than **15 minutes** and the agent must die. Captain will destroy them by setting them on fire. Kill the player. Do not continue.

**Cadence silicon CLOSED.** No USB. No `/dev/cu.usbmodem*`. No flash. No room loop. This file is **prep docs**, not a board run.

**Status: PRE-SILICON.** No RA8P1 is on the desk. Do not quote latency from this file as Titan / U55 / board time.

Board (intended, not present): Titan Mini, RA8P1, Cortex-M85 + M33, Ethos-U55, external SDRAM, PDM mic. BSP reference projects exist for PDM capture and Ethos-U55 face-detection. Those are vendor examples, not our timing.

This **is** Titan work: lock the arrival sequence and the number stamps **before** silicon. It is **not** permission to invent p50/p95/µs, SRAM-on-device, or NPU milliseconds.

## Banned lookalikes — do not quote as Titan board latency

These three numbers live nearby and must stay **separate objects**. Citing any of them as “Titan latency” is a HARD FAIL.

| Number | Correct stamp | What it actually is | Source | What it is **not** |
| --- | --- | --- | --- | --- |
| **1 ms** NPU | **PRE-SILICON hypothetical.** Never measured. Do not use as a target or a claim. | A sentence that once sat next to the other two lookalikes. Host ORT on M4 Pro (`MODEL_CONTRACT.md` 1.33 ms / 1 s window on MPS) is also **not** U55. | This file’s prior draft; `docs/MODEL_CONTRACT.md` host infer | Titan / U55 / RA8P1 inference time |
| **~100 ms** acoustic path | **HOST-ONLY.** Three short PaRIRset test IRs (`argmax \|h\|`). Mean direct-path **99.7 ms**; envelope ~96 ms. | Physical delay in those IRs. Onset was **delayed, not killed** (`onset_delayed` on all 9 rows). Not algorithm latency. | `docs/mir/PARIRSET_ONSET_ALIGNED.md`; `docs/AMENDMENT_002.md` | Titan PDM mic delay, U55, K1 cadence cell |
| **50 ms** added delay | **ON-SILICON K1 C0-v2 cadence** (product firmware). Cadence is **CLOSED**. 20 Hz + 50 ms **PASS**; 20 Hz + 100 ms **FAIL**; 5 Hz + 50 ms **FAIL**. Host 50 ms is a **different** FAIL (`GATE_C_CADENCE_HOST`). | Visual-sync / extra_gain hold budget on **K1**, not on Titan. | `docs/mir/GATE_C0_CADENCE.md`; `artifacts/gate_c0_cadence_silicon/CADENCE_RESULT.json` | Titan U55 inference, PaRIRset path, a student that also assumes 5 Hz |

Cadence 50 ms must not become “the NPU has 50 ms.” PaRIRset ~100 ms must not become “the model is slow.” The 1 ms clause must not become either.

**1 kHz** is an anti-default, not a Titan NPU rate. Semantic update rate is measured on silicon, not assumed.

Compiler RAM / Flash / MACs from GHA 33319114336 (`docs/ruhmi/COMPILE_RECEIPT.md`) are **PRE-SILICON** `check_model_metrics.py` output. They are **not** Titan measurements. No latency on that receipt.

Empty by design until a flashed image labelled **ON-SILICON** fills them: inference p50 / p95 / p99 / max (µs).

## Teachers stay off Titan

Do **not** put **MERT / MuQ / MAEST / Demucs** (or HT-Demucs, MuQ-MuLan, MERT-v1-330M) on Titan, U55, or PDM.

- They are **HOST** teachers / oracles (`docs/mir/LANDSCAPE.md` Titan column **no**; `docs/AMENDMENT_001_DELTA.md` deferred list).
- Do not put 95M transformers on U55. Do not reconstruct waveforms on silicon.
- Demucs **code** MIT; **weights** UNKNOWN — HOST-only probe, no download from this file (`docs/agent/lanes/L35_demucs.md`).
- Export a **CNN student**, not STFT, and only after `docs/mir/SELECTION_GATE.md`. Semantic-v0 is an **experiment**, not architecture authority. Student I/O is unfrozen.

Streaming student sketches are **HOST**, not Titan.

## Sequence (golden tensor first, PDM last)

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

Do **not** start with the microphone. That mixes PDM, sample rate, endianness, normalisation, FFT, mel, model, NPU, cache, and memory into one failure.

Two independent questions when the board exists (`docs/dsp/M85_GOLDENS.md`):

1. U55 learned semantics (golden INT8, after a student is selected)
2. Cortex-M85 + Helium vs current realtime MCU DSP (same PCM, host goldens already generated)

MIR work must not erase (2).

## Golden tensor protocol

For each `artifacts/golden/test_XXX/` (HOST-generated; gitignored):

1. Load `expected_preprocessed_tensor.npy` as the model input (NCHW float decoded to the quantized input the compiled graph expects — see RUHMI `io_desc.json`).
2. Invoke the generated C graph once.
3. Compare `activity[3]` to `expected_int8_output.json`.
4. Pass band: **HOST-ONLY until the first board run fills `ON-SILICON`**.

Smoke vectors: `test_vectors/smoke/` when present. Generate goldens with `uv run edgeai-golden` as in `test_vectors/README.md`.

Suggested first tolerances (to be replaced by **measured** noise, not invented):

| Check | Start-here band | Replace when |
| --- | --- | --- |
| Host ORT INT8 vs PyTorch FP32 | recorded in `quant_report.json` | already measured on host (**HOST-ONLY**) |
| U55 vs host ORT INT8 | unknown | first silicon capture (**ON-SILICON**) |
| U55 vs RUHMI `--ref-data` | unknown | first silicon capture (**ON-SILICON**) |

Host ORT INT8 ≠ MERA INT8 ≠ U55 INT8. Three numbers, three receipts (`deployment/ra8p1/README.md`).

## Benchmark harness (design only)

When the board exists, record **ON-SILICON** (not host), and keep these latency buckets **separate**:

| bucket | meaning |
| --- | --- |
| algorithm latency | how long analysis/inference takes — **empty until measured on Titan** |
| context latency | how much past/future audio the semantic model needs |
| acoustic path delay | how long sound physically took to reach the mic (`acoustic_path_delay_s`) — PaRIRset ~100 ms is **HOST-ONLY**, not this board’s mic |
| output latency | how long before LEDs visibly change |

Also record (empty until ON-SILICON):

- inference p50 / p95 / p99 / max (µs)
- update rate actually achieved
- SRAM / SDRAM / Flash from RUHMI metrics **and** from the running image (two receipts)
- NPU busy vs M85 busy vs both
- whether the deterministic DSP lane’s deadlines still hold with the NPU running

The semantic lane is allowed to be slower than the audio callback. Failure behaviour: if the semantic model is absent, corrupt, delayed, or disabled, deterministic DSP and the visual engine remain functional (`docs/MODEL_CONTRACT.md`).

## Visual experiment — do **not** wait for Titan

Oracle traces can modulate an isolated visual replay **now** (**HOST-ONLY**, not product lighting judgement):

```
recorded song + semantic_trace.jsonl
    → existing visual behaviour
    vs
    existing visual behaviour + one oracle signal
```

Format: `spectrasynq.semantic_trace.v1` (`src/edgeai/mir/semantic_trace.py`).
Required control: A baseline, B extra DoF from energy, C the same extra DoF from the oracle. Source activity adds **D** = relative dominance (`*_share`).
If C does not beat B but D does, the student target is dominance from a mix, not “are there drums.” If a *perfect* oracle does not beat energy on that extra DoF, **do not train a student**.

Do not modify production firmware from this lab.

On-device A/B still happens later. Offline oracle replay is the early kill test (`docs/mir/visual_replay/index.html`).

## Remaining ship path (Titan not here)

1. **Already in this repo / already PRE-SILICON:** host train/export/quantize/golden pipeline; GHA 33319114336 C99 for Renesas `ad01_int8.tflite` and lab `smoke.onnx` (AdaptiveAvgPool2d; pin `6c5aad901a1a41e28f6e306bfc35c44659e89502`, MERA `2.6.0+pkg.4815`) — `docs/ruhmi/COMPILE_RECEIPT.md`. Host A/B/C/D oracle replay exists — not a product lighting judgement. M85 DSP host goldens prepared — `docs/dsp/M85_GOLDENS.md`.
2. **Remaining:** Titan on the desk; BSP NPU example boots; golden tensor → U55 vs `expected_int8_output.json`; WAV → M85 frontend → U55; **PDM last**; on-device visual A/B after an oracle has already failed-or-passed offline; M85 vs current-DSP goldens on the same PCM. Cadence cells stay **CLOSED**. Student graph only after `SELECTION_GATE.md`.
3. **Who acts:** this lab for compile/golden/offline oracle; whoever has the board for flash and on-silicon receipts; Captain for the product lighting judgement (not for “what did the LEDs render” if a dump exists).
4. **Shipped on silicon means:** a flashed Titan image whose U55 outputs match golden `expected_int8_output.json` within the measured band, with a receipt labelled **`ON-SILICON`**, **and** M85 DSP deadlines still hold while the NPU runs. Compiler C99 is not that stamp.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-30 | agent:edgeai | Arrival sequence; golden first, PDM last. |
| 2026-08-31 | agent:edgeai | Ship path: C99 already PRE-SILICON; A/B/C offline control. |
| 2026-08-31 | agent:edgeai | Acoustic path delay is its own latency bucket; source A/B/C/D. |
| 2026-08-31 | agent:grok-ssa-w3-l10 | Stamp 1 ms / 100 ms / 50 ms as lookalikes, not Titan latency; teachers off board; p50 empty. |
