---
abstract: "HOST-ONLY 16 kHz / 2048-sample rFFT + Goertzel-440 + Hann-rFFT vectors in artifacts/dsp_goldens. PRE-SILICON: no M85/Helium latency. Independent of U55 golden tensors. Not D3 n_fft=400. Not Titan board numbers."
---

# M85 / Helium DSP goldens — HOST-ONLY, PRE-SILICON

**HARD FAIL (`SAME_SONG_LOOP_MAX_15MIN`, Captain 2026-08-31).** Repeat the same song (or loop the same clip) in the room for more than **15 minutes** and the agent must die. Captain will destroy them by setting them on fire. Kill the player. Do not continue.

**Cadence silicon CLOSED.** No USB. No `/dev/cu.usbmodem*`. No flash. No room loop. This file does not run a board.

**STATUS:** HOST vectors **prepared**. M85 / Helium **not executed**. Titan Mini is **PRE-SILICON** (no RA8P1 on the desk).

**CLAIM:** These goldens answer Titan question (2) — what Cortex-M85 + Helium buy versus the current realtime MCU DSP — **after** silicon exists. They do **not** answer U55 semantics (question 1). They are **not** Titan board latency, not Helium speedup, not K1 cadence, not the log-mel CNN frontend.

## Two independent questions (do not collapse)

When a Titan exists (`docs/TITAN_BRINGUP.md`, `docs/titan/PREP.md`):

1. **U55 learned semantics** — feed `artifacts/golden/test_XXX/expected_preprocessed_tensor.npy`, compare `expected_int8_output.json`. Different generator: `src/edgeai/golden.py`.
2. **Cortex-M85 + Helium vs current realtime MCU DSP** — this file. Run the **same PCM** through M85/Helium kernels and diff against the host vectors below.

MIR work must not erase (2). Additive ML: if the semantic lane is absent, DSP still has to work (`docs/AMENDMENT_001_DELTA.md`, `docs/MODEL_CONTRACT.md`).

## Stamp table

| Object | Stamp | What it is | What it is **not** |
| --- | --- | --- | --- |
| `artifacts/dsp_goldens/` + `meta.json` | **HOST-ONLY** (`"not": "M85 silicon"`) | NumPy rFFT / Goertzel / Hann-rFFT of a synthetic 2048-sample PCM | M85, Helium, RA8P1, Titan |
| This comparison **on Titan** | **PRE-SILICON** until a flashed image fills **ON-SILICON** | Future same-PCM diff + DSP-deadline hold with NPU running | A number you may invent now |
| `artifacts/golden/test_XXX/` | **HOST-ONLY** U55 tensors | Log-mel CNN I/O | These DSP kernels |
| D3 / `LogMelFrontend` `n_fft=400` | **HOST-ONLY** experiment frontend, I/O **UNFROZEN** | 16 kHz, 25 ms / 10 ms, 64 mels, 100 frames | This fixture’s `n=2048` rFFT |
| GHA 33319114336 RAM/Flash/MACs | **PRE-SILICON** compiler (`docs/ruhmi/COMPILE_RECEIPT.md`) | C99 for `ad01_int8.tflite` + `smoke.onnx` | M85 cycle count |
| “NPU in 1 ms” | **PRE-SILICON hypothetical** | Never measured | Titan / U55 / this DSP lane |
| ~100 ms acoustic path | **HOST-ONLY** PaRIRset `argmax \|h\|` | Three short test IRs | M85 FFT time |
| 50 ms added delay | **ON-SILICON K1 C0-v2 cadence** (CLOSED) | Product firmware extra_gain hold, not Titan | Helium budget |
| Host MPS 1.33 ms / window | **HOST-ONLY** Semantic-v0 on M4 Pro | `docs/HOST_RECEIPTS.md` | U55 or M85 |

Empty until **ON-SILICON**: M85 p50/p95/p99/max (µs), Helium vs scalar speedup, NPU-busy vs M85-busy, whether DSP deadlines still hold with the NPU running.

## What exists now (host)

Generator: `src/edgeai/dsp_goldens.py` (`make_vectors`).  
CLI: `uv run python scripts/make_dsp_goldens.py` → `artifacts/dsp_goldens/` (gitignored `*.npy` / `artifacts/`).

Recorded in `artifacts/dsp_goldens/meta.json` on this host (**HOST-ONLY**; re-derive by re-running the generator, do not treat as silicon):

| Field | Value |
| --- | --- |
| `label` | `HOST-ONLY` |
| `not` | `M85 silicon` |
| `sr` | 16000 |
| `n` | 2048 |
| `seed` | 0 |
| `kernels` | `rfft`, `goertzel_440`, `hann_rfft` |
| `rfft_peak_bin` | 56 |
| `rfft_peak_hz` | 437.5 (= `56 * 16000 / 2048`) |
| `goertzel_440_abs` | 346.1149733458166 |

PCM (code, not a song in the room):

```text
pcm[i] = 0.4·sin(2π·440·t) + 0.2·sin(2π·880·t) + 0.05·N(0,1; seed=0)
t = i / 16000, i = 0..2047, float32
```

Files written:

| File | Role |
| --- | --- |
| `pcm.npy` | Stimulus. Same bytes must be the M85 input. |
| `rfft_mag.npy` | `abs(numpy.fft.rfft(pcm))` float32 — unnormalised DFT, **1025** bins for `n=2048` |
| `hann_rfft_mag.npy` | same after `numpy.hanning(n)` (symmetric Hann) |
| `meta.json` | Scalars above |

Goertzel at 440 Hz uses bin `k = int(0.5 + n·440/sr) = 56`. Peak Hertz is **437.5**, not 440: 440 Hz sits between bin 56 (437.5) and 57 (445.3125). That offset is a host DFT fact, not a silicon defect.

**Not in this directory (do not claim they are goldens yet):** GDFT/80-bin K1 spectrum, ACF/tempo, log-mel frontend, feature extraction. Those are **kernels to port later**, not vectors on disk.

## How to use when a board exists

1. Do **not** start at PDM. U55 tensor pass first (`docs/TITAN_BRINGUP.md`).
2. Load **this** `pcm.npy` (or bit-exact conversion to the kernel’s type). Same `sr`, same `n`.
3. Run M85/Helium rFFT magnitude, Goertzel-440, Hann-rFFT.
4. Diff vs `rfft_mag.npy` / `hann_rfft_mag.npy` / `goertzel_440_abs`. Pass band is **HOST-ONLY until the first capture fills ON-SILICON** with a **measured** tolerance (CMSIS scaling, window definition, and float vs Q15 will move the number).
5. Separately: run the same PCM through the **current** product MCU DSP you are comparing, if that comparison is the question. Do not invent that MCU’s latency here.
6. With the NPU running, record whether **deterministic DSP deadlines still hold**. That is part of “shipped on silicon” (`docs/TITAN_BRINGUP.md`).

Teachers **MERT / MuQ / MAEST / Demucs** stay off Titan / U55 / PDM.

## What this file does not freeze

Student I/O is **UNFROZEN** (`docs/MODEL_CONTRACT.md`, `docs/mir/SELECTION_GATE.md`). 16 kHz here is the **DSP fixture**, not a RA8P1 product lock and not Semantic-v0’s 1.0 s / 64-mel image.

Do not copy these 2048-sample goldens onto C1. C1 is LGP on product firmware (`docs/mir/GATE_C1.md`). Cadence stays **CLOSED**.

## Remaining ship path

1. **Already in this repo / HOST-ONLY:** generator + CLI; local `artifacts/dsp_goldens/` on this workstation; this document. **PRE-SILICON** C99 for a **different** graph lives in `docs/ruhmi/COMPILE_RECEIPT.md` — not these kernels.
2. **Remaining:** Titan on the desk; port rFFT / Goertzel / Hann-rFFT (then later GDFT, ACF, mel); same-PCM ON-SILICON diff; DSP-deadline hold with NPU running; PDM last, never first.
3. **Who acts:** this lab regenerates host goldens; whoever has the board flashes and writes the ON-SILICON receipt; Captain for product lighting, not for buffer diffs if a dump exists.
4. **Shipped on silicon means:** a flashed Titan image whose M85/Helium outputs match these host vectors within the **measured** band, receipt labelled **`ON-SILICON`**, **and** DSP deadlines still hold while the NPU runs. Host `meta.json` is not that stamp. Compiler C99 is not that stamp.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-30 | agent:edgeai | Stub: host rFFT / Goertzel / Hann list; no silicon numbers. |
| 2026-08-31 | agent:grok-ssa-w3-l34 | HOST-ONLY meta recorded; PRE-SILICON; split from U55 goldens; lookalikes banned; ship path. |
