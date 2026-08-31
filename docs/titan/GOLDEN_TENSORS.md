---
abstract: "HOST-ONLY inventory of artifacts/golden/ (32 cases, gitignored). CNN on log-mel into U55, not STFT. Export AdaptiveAvgPool2d, not ReduceMean. Pass band HOST-ONLY until a flashed receipt labelled ON-SILICON. Not a board clock."
---

# Golden tensors — HOST-ONLY inventory

**HARD FAIL (`SAME_SONG_LOOP_MAX_15MIN`, Captain 2026-08-31).** Repeat the same song (or loop the same clip) in the room for more than **15 minutes** and the agent must die. Captain will destroy them by setting them on fire. Kill the player. Do not continue.

Cadence silicon **CLOSED**. No USB. No flash. No PDM. No room audio.

| Field | Value |
| --- | --- |
| STATUS | **PRESENT (HOST-ONLY)** — not HOST-MISSING. 32 cases on this Mac under `artifacts/golden/`. Gitignored. Not ON-SILICON. |
| CLAIM | U55 consumes a **CNN** on a precomputed log-mel tensor, **not STFT**. Pooling export is `nn.AdaptiveAvgPool2d((1,1))` → ONNX GlobalAveragePool/AveragePool. **ReduceMean is banned** (D11; Vela split GHA 33318864219). Compare `activity[]` to `expected_int8_output.json`. The pass band stays **HOST-ONLY** until a flashed Titan run fills a receipt labelled **ON-SILICON**. |
| EVIDENCE | This inventory; `artifacts/golden/index.json` (`n: 32`, every case `"label": "HOST-ONLY"`, 32 `int8_host_ort` maps); `test_000/`…`test_031/` each with five files; `src/edgeai/golden.py`; `src/edgeai/frontend.py` (STFT/mel off U55); `src/edgeai/semantic_v0.py` AdaptiveAvgPool2d; `tests/test_shapes.py` forbids ONNX ReduceMean; D3 + D11 in `docs/DECISIONS.md`; `docs/TITAN_BRINGUP.md` golden protocol; `.gitignore` `artifacts/` + `*.npy` / `*.wav`. |
| COMMAND | not executed this SSA (tree read only). Generator (already used, do not re-run unless regenerating): `uv run edgeai-golden --ckpt experiments/semantic_v0_synth/semantic_v0_best.pt --int8-onnx artifacts/export/semantic_v0_int8.onnx --out artifacts/golden --n 32`. Cadence CLOSED. No USB. |
| METHOD_RISK | Did not `np.load` the `.npy` (binary). Shape taken from `metadata.json` / index `input_shape` `[1,1,64,100]` and the generator (`logmel.unsqueeze(0)`). Did not re-export ONNX. Did not load `artifacts/smoke/smoke.onnx`. Semantic-v0 remains an experiment (Amendment 001); these vectors witness the **format** and the **HOST** pipeline, not a frozen student. Host ORT INT8 ≠ RUHMI INT8 ≠ U55 INT8. |
| NEXT | Keep the band HOST-ONLY. On first board: load `expected_preprocessed_tensor.npy` into the compiled CNN, compare to `expected_int8_output.json`, write the measured U55 band under **ON-SILICON**. Do not export STFT onto U55. Do not reintroduce `tensor.mean` / ReduceMean. PDM last. |

Arrival sequence: [TITAN_BRINGUP.md](../TITAN_BRINGUP.md). Prep without a board: [PREP.md](PREP.md). Compiler C99 (not this compare): [COMPILE_RECEIPT.md](../ruhmi/COMPILE_RECEIPT.md).

## Verdict

`artifacts/golden/` **exists on this host**. It is **not** HOST-MISSING.

Every recorded case is labelled **HOST-ONLY**. There is **no** `ON-SILICON` stamp in the tree. Suggested numeric U55 tolerances in TITAN_BRINGUP stay **unknown** until silicon capture.

These tensors are the Titan step **after** the BSP NPU example and **before** WAV-through-M85 and **before** PDM (`TITAN_BRINGUP.md`). They isolate “did this CNN run on U55?” from “did we compute mel / capture PDM correctly?” (D3).

Semantic-v0 checkpoint used here is a **toolchain witness**, not architecture authority (`experiments/semantic_v0/AUTHORITY.md`). Golden-vector **format** is what Amendment 001 keeps.

## Inventory (this Mac, 2026-08-31)

Generator: `src/edgeai/golden.py` → CLI `edgeai-golden` (`pyproject.toml`). Default `--out artifacts/golden`, `--n 32`.

| Item | On disk | Stamp |
| --- | --- | --- |
| `artifacts/golden/index.json` | yes | HOST-ONLY |
| `artifacts/golden/test_000/` … `test_031/` | **32** directories | HOST-ONLY |
| Per-case files | `input.wav`, `expected_preprocessed_tensor.npy`, `expected_fp32_output.json`, `expected_int8_output.json`, `metadata.json` | HOST-ONLY |
| `index.json` `"n"` | 32 | matches 32 dirs |
| `index.json` `"label"` | 32× `HOST-ONLY` | no ON-SILICON |
| `int8_host_ort` in index | 32 maps (not null) | host ORT INT8, not U55 |
| Checkpoint recorded | `experiments/semantic_v0_synth/semantic_v0_best.pt` | gitignored weights |
| Git | whole `artifacts/` gitignored | regenerate, do not commit corpus/checkpoints |
| Committed smoke copies | `test_vectors/smoke/test_000/`, `test_001/` (same five-file layout) | tiny fixtures, not the 32-set |

If this directory is absent on another machine, stamp **HOST-MISSING** and regenerate with the command above. Do not invent vectors. Do not treat smoke fixtures as the Titan set.

### Index frontend (experiment I/O, not a product freeze)

From `artifacts/golden/index.json`:

| Field | Value |
| --- | --- |
| sample_rate | 16000 |
| duration_s | 1.0 |
| n_fft / win / hop | 400 / 400 / 160 |
| n_mels × n_frames | 64 × 100 |
| tensor `input_shape` | `(1, 1, 64, 100)` NCHW log-mel |
| f_min / f_max | 20 / 8000 |
| log_offset, clip | 1e-6, [−12, 6] |
| classes | `vocals`, `drums`, `bass` |
| split | `test` (synthetic song-level; `synth_040`…`synth_047`, four windows each) |
| WAV | PCM_16, 16000 samples (`n_samples`) |

`how_to_use_on_titan` in the index: do **not** start with the PDM mic. Load `expected_preprocessed_tensor.npy` into the U55 input arena and compare `activity[]` to `expected_int8_output.json`.

## What goes on U55 vs what stays off it

| Piece | Where it runs | Rule |
| --- | --- | --- |
| STFT / MelSpectrogram / log / clip | host today; Cortex-M85 later | **Not the U55 graph.** FFT is hostile to Ethos-U55 (`src/edgeai/frontend.py`, D3). |
| CNN on log-mel `(1,1,64,100)` | U55 (when flashed) | **Export the CNN, not the STFT** (`Agents.md`). |
| Pooling | `AdaptiveAvgPool2d((1,1))` then flatten → Gemm | **Required** (D11). ONNX must be GlobalAveragePool or AveragePool. |
| `tensor.mean(dim=(2,3))` / ONNX **ReduceMean** | banned on this graph | Vela parks MEAN on CPU and splits Ethos-U ops (GHA **33318864219** FAIL). |
| Live PDM | last | After tensor-only pass and after WAV→frontend. |

Witness graph (BN folded): Conv / ReLU / AdaptiveAvgPool2d / Gemm / Sigmoid. Smoke C99 on that pool: GHA **33319114336**, **PRE-SILICON** compiler metrics — not this golden compare, not a board clock.

Gate in-repo: `tests/test_shapes.py::test_onnx_export_avoids_reducemean` asserts `"ReduceMean" not in ops` and requires `GlobalAveragePool` or `AveragePool`.

Stale dumps still say ReduceMean (`docs/onnx_graph_semantic_v0.json`, 2026-08-30 table in `docs/HOST_RECEIPTS.md`). Live source is AdaptiveAvgPool2d. Do not compile the stale dump.

## Pass band (do not fill U55 numbers from host)

Protocol when a board exists (`docs/TITAN_BRINGUP.md`):

1. Load `expected_preprocessed_tensor.npy` as model input (NCHW float decoded to the quantized input the compiled graph expects — RUHMI `io_desc.json`).
2. Invoke the generated C graph **once**.
3. Compare `activity[3]` to `expected_int8_output.json`.
4. Pass band: **HOST-ONLY until the first board run fills `ON-SILICON`.**

| Check | What exists now | Stamp |
| --- | --- | --- |
| Host ORT INT8 vs PyTorch FP32 | `artifacts/export/quant_report.json`: `pytorch_vs_onnx_fp32_mae` ≈ 1.25e-7; INT8 vs FP32 macro MAE 0.137 → 0.134 (n=48, **not** the n=32 golden set). Host ORT is **not** MERA. | **HOST-ONLY** |
| U55 vs host ORT INT8 | unknown | fill **ON-SILICON** |
| U55 vs RUHMI `--ref-data` | unknown | fill **ON-SILICON** |
| Suggested start-here numeric band in TITAN_BRINGUP | “to be replaced by measured noise” | not a board measurement |

Do not copy host MAE / F1 / MPS 1.33 ms / GHA RAM-Flash-MACs into the U55 pass band.

`metadata.json` records `fp32`, `int8_host_ort`, and `"label": "HOST-ONLY"`. Example `test_000` `expected_int8_output.json`: vocals 0.87193, drums 0.77809, bass 0.96186 (host ORT dequantized activity, not raw int8 lanes).

## Not these goldens

| Tree | Role |
| --- | --- |
| `artifacts/dsp_goldens/` + [M85_GOLDENS.md](../dsp/M85_GOLDENS.md) | rFFT / Goertzel / Hann — Cortex-M85 vs current DSP, **independent** of U55 |
| `artifacts/smoke/` | compile-smoke ONNX, not the 32-case Titan set |
| `test_vectors/smoke/` | two committed copies of the five-file layout |
| MERT / MuQ / MAEST / Demucs | HOST teachers. Do not put on Titan / U55 / PDM |

## Remaining ship path

1. **Already on this host / in source:** 32 HOST-ONLY golden cases; generator; AdaptiveAvgPool CNN export (ReduceMean banned); STFT/mel off the NPU graph; PRE-SILICON C99 for a related smoke graph (GHA 33319114336).
2. **Remaining:** Titan on the desk; BSP NPU example boots; load these tensors into the compiled CNN; measure U55 vs `expected_int8_output.json`; write **ON-SILICON** band; then WAV→M85 frontend; PDM last; M85 DSP goldens on the same PCM with NPU running.
3. **Who acts:** this lab owns the host tree and this file. Whoever has the board flashes and writes the ON-SILICON receipt. Captain judges product lighting, not “did the tensor match” when a dump exists.
4. **Shipped** means a flashed image whose U55 `activity[]` matches these `expected_int8_output.json` files within the **measured** ON-SILICON band, **and** M85 DSP deadlines still hold. Host presence of `artifacts/golden/` is not that stamp.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:grok-ssa-w3-l28 | Created. Inventories artifacts/golden/ (32 HOST-ONLY). CNN not STFT. AdaptiveAvgPool not ReduceMean. Band HOST-ONLY until ON-SILICON. |
