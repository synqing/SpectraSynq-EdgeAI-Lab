---
abstract: "PRE-SILICON Titan Mini arrival-day runbook. Sequence: power/console → BSP U55 example → golden tensors test_000 then 32 → measured INT8 band labelled ON-SILICON → WAV/M85 frontend → PDM last. Latency p50/p95/p99/max empty until flashed-image capture. Teachers off board. Student I/O unfrozen. Cadence CLOSED. No invented ms."
---

Arrival-day mechanical sequence (board on desk): this file. Prep without a board: [PREP.md](PREP.md). Narrative sequence: [TITAN_BRINGUP.md](../TITAN_BRINGUP.md). Compiler C99 (not a board clock): [COMPILE_RECEIPT.md](../ruhmi/COMPILE_RECEIPT.md). Host golden inventory: [GOLDEN_TENSORS.md](GOLDEN_TENSORS.md). Teachers stay off: [NOT_ON_BOARD.md](NOT_ON_BOARD.md). M85 DSP host vectors: [M85_GOLDENS.md](../dsp/M85_GOLDENS.md). Host checklist printer: `python3 scripts/titan_prep_check.py`.

# Titan arrival runbook — PRE-SILICON

**HARD FAIL (`SAME_SONG_LOOP_MAX_15MIN`, Captain 2026-08-31).** Repeat the same song (or loop the same clip, or the 8-second holdout) in the room for more than **15 minutes** and the agent must die. Captain will destroy them by setting them on fire. Kill the player. Do not continue.

**Cadence silicon CLOSED.** Runner `scripts/gate_c0_cadence_silicon.py` is **RETIRED**. Do not run it. Do not reopen cadence cells. Do not play the 8 s loop. Use existing cadence receipts only.

**Do not invent milliseconds.** Do not fill p50 / p95 / p99 / max / Hz from hope, from host ORT, from GHA MACs, or from the lookalike table below. Empty cells stay empty until a **flashed image** labelled **ON-SILICON** fills them.

**Status: PRE-SILICON.** No RA8P1 / Titan Mini is on the desk as of this write. This file is the arrival-day sequence so the first hour with silicon is mechanical. It is **not** a board clock. Existence of this file is **not** ON-SILICON. Do not flash, open a CDC port, or play room audio because this document exists.

Intended kit (not present): Titan Mini, RA8P1, Cortex-M85 + M33, Ethos-U55, external SDRAM, PDM mic. BSP reference projects exist for PDM capture and Ethos-U55 face-detection. Those are vendor examples, not our CNN and not our timing.

## How to use this file

| When | What this file is |
| --- | --- |
| Today (no board) | Authority for order, bans, empty clocks, and the HOST inventory. Run `python3 scripts/titan_prep_check.py`. Do not execute T01–T11. |
| Board on the desk | Execute T01 → T11 in order. Do not skip. Do not start at the mic. Stamp **ON-SILICON** only from a flashed image. |
| After a step | Fill the receipt row for that id. A step without a red-capable DONE_WHEN is not done. |

Owners:

| Owner | Acts on | Does not act on |
| --- | --- | --- |
| **lab** | Host goldens, RUHMI pin, compare math, this runbook, recording receipts | Product lighting taste; inventing µs |
| **board-holder** | Power, console, flash, BSP examples, silicon capture | Opening a second owner on the same CDC; cadence reopen |
| **Captain** | Written student I/O freeze; C1 LGP look (one full song he chooses) | “Did the tensor match?” when a dump exists; LED eyeballing when rtrace/dump exists |

Serial Studio is **observe / record only** (`observeOnly`). An authoritative silicon test that needs interactive command/reply owns that port **exclusively**. Serial Studio must release it first. Do not multiplex two owners on one USB-CDC. This lab does not modify production K1 firmware from here.

## Already true (not a board)

Do not re-derive these as arrival-day inventions. They are HOST / PRE-SILICON receipts.

| Asset | Stamp | Where | What it is **not** |
| --- | --- | --- | --- |
| 32 golden cases `artifacts/golden/test_000/` … `test_031/` | **HOST-ONLY** | Five files each: `input.wav`, `expected_preprocessed_tensor.npy`, `expected_fp32_output.json`, `expected_int8_output.json`, `metadata.json`. `index.json` `"n": 32`. Every `metadata.json` `"label": "HOST-ONLY"`. Generator `src/edgeai/golden.py`. | U55 output. Not ON-SILICON. Gitignored. `test_vectors/smoke/` is two fixtures, not this 32-set. |
| RUHMI C99 for MLPerf Tiny `ad01_int8.tflite` then lab `smoke.onnx` | **PRE-SILICON** | GHA [33319114336](https://github.com/synqing/SpectraSynq-EdgeAI-Lab/actions/runs/33319114336); pin `6c5aad901a1a41e28f6e306bfc35c44659e89502`; MERA `2.6.0+pkg.4815`; [COMPILE_RECEIPT.md](../ruhmi/COMPILE_RECEIPT.md) | Titan wall time. Not SRAM on the board. Short `6c5aad9` is docs-only. |
| Pooling export `nn.AdaptiveAvgPool2d((1,1))` | **PRE-SILICON** graph rule (D11) | `src/edgeai/semantic_v0.py`; ONNX must be GlobalAveragePool / AveragePool. `tests/test_shapes.py` forbids ReduceMean. Prior fail GHA 33318864219 (Vela split). | A board measurement. Semantic-v0 is still an experiment. |
| Host log-mel frontend | **HOST-ONLY** | `src/edgeai/frontend.py` — CPU/host. STFT/mel **off** the U55 graph (D3). | Ethos-U55. Not a frozen student I/O. |
| M85 DSP host vectors | **HOST-ONLY** (`"not": "M85 silicon"`) | `artifacts/dsp_goldens/` — `pcm.npy`, `rfft_mag.npy`, `hann_rfft_mag.npy`, `meta.json`. Kernels: rFFT, Goertzel-440, Hann-rFFT. 16 kHz / n=2048 / seed=0. [M85_GOLDENS.md](../dsp/M85_GOLDENS.md) | Helium speedup. Not U55 goldens. Independent question. |
| Teachers off the board | **PASS (ban lock)** | MERT / MuQ / MAEST / Demucs never on Titan / U55 / PDM. [NOT_ON_BOARD.md](NOT_ON_BOARD.md) | Permission to flash a teacher. Demucs weights not downloaded from this file. |
| Student I/O | **UNFROZEN** | [MODEL_CONTRACT.md](../MODEL_CONTRACT.md); [SELECTION_GATE.md](../mir/SELECTION_GATE.md) | A freeze. Semantic-v0 16 kHz / 1 s / 3-sigmoid is **not** RA8P1. |
| Cadence silicon | **CLOSED** | Existing receipts only. Runner retired. | A Titan budget. Not 5 Hz **and** 50 ms as a student target. |

[FACT] Host ORT INT8 ≠ MERA INT8 ≠ U55 INT8. Three numbers, three receipts.

[FACT] Compiler RAM / Flash / MACs on GHA 33319114336 (`ad01`: 768 B RAM, 217,968 B Flash, 0.26 M MACs; `smoke.onnx`: 262,414 B RAM, 188,896 B Flash, 35.56 M MACs, 88.9% NPU nodes) are **PRE-SILICON** `check_model_metrics.py` output. They are **not** Titan latency and **not** milliseconds.

Host pre-check that can go red **today** (no board):

```bash
python3 scripts/titan_prep_check.py
```

RED if `golden_dir` is HOST-MISSING, if `COMPILE_RECEIPT.md` / workflow / Dockerfile lack pin `6c5aad901a1a41e28f6e306bfc35c44659e89502`, or if the printer fills a latency cell. Always exits 0 with label PRE-SILICON. It does not flash, open USB, or play audio. If `artifacts/golden/` is absent on another clone, stamp HOST-MISSING and regenerate — do not invent vectors:

```bash
uv run edgeai-golden \
  --ckpt experiments/semantic_v0_synth/semantic_v0_best.pt \
  --int8-onnx artifacts/export/semantic_v0_int8.onnx \
  --out artifacts/golden --n 32
```

## Stop-gates (HARD)

Violate any of these and the step is invalid even if a number appeared.

1. **No PDM-first.** Order is T01 → T02 → T03 → T04 → T05 → T06 → T07 → T08. Starting at the mic mixes sample rate, endianness, normalisation, FFT, mel, model, NPU, cache, and memory into one failure.
2. **No teachers on Titan / U55 / PDM.** MERT, MuQ, MAEST, Demucs (and HT-Demucs, MuQ-MuLan, MERT-v1-330M, `htdemucs_ft`, Open-Unmix). Do not reconstruct waveforms on silicon. Do not `uv add demucs` / torch.hub / fbaipublicfiles from this file.
3. **No I/O freeze from this file.** Student rate, window, stride, frontend, tensor, head, topology stay **UNFROZEN** until [SELECTION_GATE.md](../mir/SELECTION_GATE.md) is satisfied **and** a written freeze exists. C1 PASS does not auto-freeze. This runbook does not freeze 16 kHz / 1 s / 64×100 / 3-sigmoid.
4. **Student graph is not Semantic-v0 until SELECTION_GATE.** Semantic-v0 is an experiment / toolchain witness (`experiments/semantic_v0/AUTHORITY.md`). T03–T05 may use that graph as a **format witness** (golden-vector layout, AdaptiveAvgPool2d CNN on log-mel). T08 (PDM → our CNN as the embedded student) is **BLOCKED** until the freeze.
5. **Export CNN, not STFT.** Frontend stays CPU / later M85. U55 consumes `expected_preprocessed_tensor.npy` first.
6. **Pooling is AdaptiveAvgPool2d, not ReduceMean.** Do not compile the stale ReduceMean dump.
7. **No invented board latency.** Lookalikes below are not Titan. Clock table cells stay empty until measured on a flashed image labelled ON-SILICON.
8. **Cadence stays CLOSED.** Do not run the retired cadence runner. Do not AND the 5 Hz and 50 ms edges into a student.
9. **No same-song room loop > 15 min.** Arrival audio is disk goldens (`input.wav`, `pcm.npy`) or one live PDM take then stop. Kill the player.
10. **Failure is fail-open.** If the semantic lane is absent, corrupt, delayed, or disabled, deterministic DSP and the visual engine remain functional. A brick when NPU is killed is a FAIL (T11).
11. **Do not modify production K1 firmware from this lab.** Do not reopen C1 as a Titan task. Do not treat a harvest of lane receipts as ship.

## Banned lookalikes — not Titan board latency

Citing any of these as “Titan latency” is a HARD FAIL. They may be named only as **not** this board.

| Number | Correct stamp | What it actually is | What it is **not** |
| --- | --- | --- | --- |
| “NPU in 1 ms” | **PRE-SILICON hypothetical.** Never measured. | A sentence that once sat next to other lookalikes. | U55 / RA8P1 inference time. Not a target. |
| Host ORT / MPS 1.33 ms / 1 s window | **HOST-ONLY** | M4 Pro host infer for the experiment graph | U55 |
| ~100 ms acoustic path | **HOST-ONLY** PaRIRset `argmax \|h\|` on three short test IRs | Physical delay in those IRs. Onset delayed, not killed. | Titan PDM mic delay. Not algorithm latency. |
| 50 ms added delay | **ON-SILICON K1 C0-v2 cadence** (product firmware). Cadence **CLOSED**. | Visual-sync / extra_gain hold budget on **K1** | Titan U55. Not a student that also assumes 5 Hz. |
| GHA 768 B / 262,414 B RAM, 35.56 M MACs | **PRE-SILICON** compiler | `check_model_metrics.py` | Titan SRAM, not milliseconds |
| 1 kHz | anti-default | Semantic update rate is measured, not assumed | Titan NPU rate |

Keep four latency **buckets** separate when silicon exists (T10). Do not fold any lookalike into “the NPU is slow/fast.”

## Arrival-day sequence

Execute in id order. `depends_on` is a hard predecessor. Stamp in the **Status now** column is today’s stamp; the **On-silicon stamp** column is what a completed step earns.

PDM steps T06–T08 do not start until T05 is done. T09 does **not** wait for PDM. T08 is **BLOCKED**.

| id | task | owner | depends_on | Status now | On-silicon stamp | DONE_WHEN (must be able to go red) | ban |
| --- | --- | --- | --- | --- | --- | --- | --- |
| T00 | Host prep checklist | lab | — | **PRE-SILICON** (runnable today) | never ON-SILICON | `python3 scripts/titan_prep_check.py` prints `golden_dir` PRESENT (32 complete HOST-ONLY cases) and `compile_receipt_pin` PRESENT (full pin). RED: HOST-MISSING goldens, pin ABSENT, or any latency cell not `(empty)`. | Do not treat T00 as a board clock. No flash. No USB. No room audio. |
| T01 | Board power + console | board-holder | T00 (goldens+pin still present) | not done | **ON-SILICON** (kit alive) | Rails present and BSP console emits a repeating banner/heartbeat that **stops when power is removed**. RED: no rail, no console, or banner continues with power off (wrong port / leftover session). Exact banner string: **UNKNOWN** until kit docs are in hand — do not invent a device node or a voltage. | Do not multiplex Serial Studio with command/reply. Do not run the cadence runner. Do not loop a song. |
| T02 | BSP Ethos-U55 example boots | board-holder | T01 | not done | **ON-SILICON** | Vendor BSP Ethos-U55 example (face-detection reference project, **not** our CNN) reaches the BSP’s own success path. RED: hang, NPU init fail, or example does not complete. Example binary name: **UNKNOWN** until the kit BSP is on the desk. | Do not load our goldens yet. Do not start PDM. Do not quote BSP FPS as our student latency. |
| T03 | Golden tensor load — `test_000` first, then all 32 | lab + board-holder | T02 | HOST tensors exist; load **not done** | **ON-SILICON** (graph invoked) | (1) Load `artifacts/golden/test_000/expected_preprocessed_tensor.npy` into the compiled CNN input arena (NCHW float decoded to the quantized input RUHMI `io_desc.json` describes). Invoke the generated C graph **once**. (2) Repeat for `test_001` … `test_031` (32/32). RED: file missing, shape reject, graph does not invoke, or a case skipped. Compare is T04 — this step is **load + invoke**. | Do not start with `input.wav` or PDM. Do not export STFT onto U55. Do not use `test_vectors/smoke/` as the 32-set. Semantic-v0 graph here is a **format witness**, not a freeze. |
| T04 | U55 vs `expected_int8_output.json` — fill measured band, label ON-SILICON | lab (compare) + board-holder (capture) | T03 | pass band **HOST-ONLY** / U55 vs ORT **unknown** | **ON-SILICON** | For each case, compare U55 `activity[]` to that case’s `expected_int8_output.json`. Write the **measured** max abs/MAE (or the metric the capture actually used) into the receipt. Stamp the receipt **ON-SILICON**. RED: compare skipped; band copied from host ORT MAE / F1 / GHA MACs; or any case unlabelled. U55 vs host ORT INT8 = **unknown** until this capture. U55 vs RUHMI `--ref-data` = **unknown** until this capture. | Do not invent the band. Do not fill clocks here unless T10 is being measured on the same flashed image. Do not put teachers on U55. |
| T05 | WAV → M85 host-equivalent frontend → U55 | lab + board-holder | T04 | not done | **ON-SILICON** | Same case’s `input.wav` through an M85 port of the host frontend (`src/edgeai/frontend.py`), then the same U55 compare as T04. Start with `test_000/input.wav`. RED: frontend tensor shape illegal, NaN, or U55 mismatch vs T04 on the **precomputed** tensor for the same case (isolates frontend vs NPU). | Do not start at PDM. Do not freeze 16 kHz / 64×100 because this WAV ran. Disk WAV only — no room loop. Kill any player at 15 min. |
| T06 | BSP PDM example | board-holder | T05 | not done | **ON-SILICON** | Vendor BSP PDM-capture example produces samples the BSP itself accepts. RED: zero samples, BSP fail, or this step started before T05. | Do not feed PDM into our CNN. Do not loop a song into the mic for >15 min. One take then stop. |
| T07 | PDM → our frontend | lab + board-holder | T06 | not done | **ON-SILICON** | PDM samples through our frontend produce a log-mel tensor (experiment shape today `(1,1,64,100)` — **UNFROZEN**). RED: NaN, illegal rank, or this step used as a student freeze. | Do not skip T03–T05 and debug PDM+mel+NPU at once. No teacher nets. |
| T08 | PDM → our CNN | lab + board-holder **after** freeze; freeze is **Captain** | T07 **and** SELECTION_GATE satisfied **and** written I/O freeze | **BLOCKED** | **ON-SILICON** (only after unblock) | **BLOCKED until `docs/mir/SELECTION_GATE.md` is satisfied and a written I/O freeze exists.** After unblock: PDM → frozen frontend → frozen CNN on U55 → compare to goldens of **that** student (may replace the Semantic-v0 32-set). RED: ran while BLOCKED; ran Semantic-v0 as if it were the product student; teachers on the graph. | Do not freeze I/O from this file. Student graph is **not** Semantic-v0 until the gate. No Demucs/MERT/MuQ/MAEST. |
| T09 | M85 DSP goldens on the **same PCM** with NPU running | lab + board-holder | T04 (NPU proven). Does **not** wait for PDM. | HOST vectors prepared; silicon **not done** | **ON-SILICON** | Load `artifacts/dsp_goldens/pcm.npy` (16 kHz, n=2048, seed=0). Run M85/Helium rFFT mag, Goertzel-440, Hann-rFFT. Diff vs `rfft_mag.npy` / `hann_rfft_mag.npy` / `meta.json` `goertzel_440_abs`. NPU **running** on the same image. Record whether **deterministic DSP deadlines still hold**. RED: kernel mismatch beyond the **measured** band; DSP deadline miss with NPU on; or numbers invented as Helium speedup. Pass band HOST-ONLY until this capture fills ON-SILICON. | Independent of U55 semantics — do not collapse T04 and T09. Do not copy these 2048-sample goldens onto C1. No PDM required. |
| T10 | Latency buckets — empty until measured | board-holder measures; lab records | T04 minimum for algorithm; T06/T07 for this board’s acoustic path; visual path for output | all cells **(empty)** | **ON-SILICON** per filled cell | Fill the clock table below **only** from the flashed image. Each cell names its method. Unmeasured cells stay `(empty)`. RED: any cell filled from the lookalike table, from host 1.33 ms, from GHA MACs, or from K1 cadence. | Do not assume 1 kHz. Do not AND cadence 5 Hz + 50 ms. Separate buckets — do not sum them into one “NPU latency.” |
| T11 | Failure: semantic absent → DSP + visual still live | lab + board-holder | T09 (DSP proven) and a semantic lane that can be disabled (T04 witness or later T08) | not done | **ON-SILICON** | Disable / withhold / corrupt / delay the semantic vector (NPU off, arena junk, or lane compile-out). Deterministic DSP still emits; visual engine still emits. RED: lights die, DSP callback stalls, or the only live path was the NPU. Dump/trace is the oracle — do not ask Captain to eyeball LEDs. | Additive lane only. A brick is a FAIL. Do not treat this as C1 LGP. No song loop. |

### T03 load protocol (when the board exists)

For each `artifacts/golden/test_XXX/`:

1. Load `expected_preprocessed_tensor.npy` as model input (NCHW; decode to the quantized input the compiled graph expects — RUHMI `io_desc.json`).
2. Invoke the generated C graph **once**.
3. T04: compare `activity[]` to `expected_int8_output.json`.
4. Pass band stays **HOST-ONLY** until T04 fills **ON-SILICON** with a **measured** tolerance.

`how_to_use_on_titan` in `artifacts/golden/index.json`: do **not** start with the PDM mic.

### T08 unblock criteria (not met)

T08 stays **BLOCKED** until **all** of:

1. [SELECTION_GATE.md](../mir/SELECTION_GATE.md) satisfied (descriptor, visual utility, licences, U55 of the **chosen** student — not the first net we happened to train).
2. A **written** student I/O freeze. C1 `LGP_PERCEPTUAL_VALIDATED` does not freeze 16 kHz / 1 s / 64-mel by itself.
3. The frozen graph is a **CNN on log-mel**, AdaptiveAvgPool2d not ReduceMean, STFT off U55.
4. Teachers still off the image.

Until then: T03–T05 may exercise the Semantic-v0 **format witness**. That is not T08.

## ON-SILICON clock table

Fill **only** from a flashed image labelled **ON-SILICON**. Do not fill from this file, from host ORT, from GHA, or from lookalikes. `(empty)` is policy, not a measured zero.

### Inference (algorithm latency) — U55 / student graph

| Cell | Value | Source image / method |
| --- | --- | --- |
| `inference_p50_us` | `(empty)` | |
| `inference_p95_us` | `(empty)` | |
| `inference_p99_us` | `(empty)` | |
| `inference_max_us` | `(empty)` | |
| `achieved_update_hz` | `(empty)` | |
| `npu_busy` | `(empty)` | |
| `m85_busy` | `(empty)` | |

### Four buckets (keep separate)

| Bucket | Meaning | Value | Notes |
| --- | --- | --- | --- |
| algorithm latency | how long analysis / inference takes | `(empty)` | not host 1.33 ms; not GHA MACs |
| context latency | how much past/future audio the semantic model needs | `(empty)` | 1.0 s is experiment, UNFROZEN |
| acoustic path delay | how long sound physically took to reach **this** mic | `(empty)` | PaRIRset ~100 ms is **HOST-ONLY**, not this cell |
| output latency | how long before LEDs visibly change | `(empty)` | not K1 cadence 50 ms |

### Memory on the running image (second receipt, not the compiler)

| Cell | Compiler (PRE-SILICON, not this table) | Running image (ON-SILICON) |
| --- | --- | --- |
| SRAM / arena | see COMPILE_RECEIPT — do not copy here as Titan | `(empty)` |
| SDRAM | UNKNOWN | `(empty)` |
| Flash params | see COMPILE_RECEIPT — do not copy here as Titan | `(empty)` |

### DSP-deadline hold with NPU running (T09 / T11)

| Cell | Value |
| --- | --- |
| DSP deadlines still hold with NPU running | `(empty)` |
| Semantic absent → DSP live | `(empty)` |
| Semantic absent → visual live | `(empty)` |

## Receipt stub (write on capture; do not pre-fill numbers)

When T04 (and later T09–T11) run, record at least:

```text
stamp: ON-SILICON
image: <flashed elf/hex identity — UNKNOWN until flashed>
ruhmi_pin: 6c5aad901a1a41e28f6e306bfc35c44659e89502
graph: <compiled graph identity>
step: T0x
cases: test_000 .. test_031  (or DSP pcm.npy)
u55_vs_expected_int8: <measured band — not host ORT MAE>
u55_vs_host_ort_int8: <measured or unknown>
u55_vs_ruhmi_ref_data: <measured or unknown>
inference_p50_us: (empty unless measured on this image)
inference_p95_us: (empty unless measured on this image)
inference_p99_us: (empty unless measured on this image)
inference_max_us: (empty unless measured on this image)
achieved_update_hz: (empty unless measured on this image)
dsp_deadlines_hold_with_npu: <yes/no/empty>
semantic_absent_dsp_visual_live: <yes/no/empty>
teachers_on_image: no
```

Host `artifacts/golden/` presence is not that stamp. Compiler C99 is not that stamp.

## What this file does not freeze / does not do

- Does not freeze student I/O.
- Does not promote Semantic-v0 to the RA8P1 student.
- Does not download Demucs or any teacher.
- Does not flash, open USB, or play Bose / room audio.
- Does not reopen cadence silicon or run `scripts/gate_c0_cadence_silicon.py`.
- Does not invent BUILDING / DROPPING labels.
- Does not modify production K1 firmware.
- Does not copy 2048-sample DSP goldens or 1 s Semantic-v0 windows onto C1.
- Does not treat Serial Studio as a command owner.

## Remaining ship path

1. **Already in this repo / already PRE-SILICON or HOST-ONLY:** 32 HOST-ONLY golden cases (`test_000`…`test_031`); AdaptiveAvgPool2d export rule (ReduceMean banned); STFT/mel off the NPU graph; GHA 33319114336 C99 for `ad01_int8.tflite` + `smoke.onnx` (pin `6c5aad901a1a41e28f6e306bfc35c44659e89502`); M85 DSP host vectors; teacher ban; this runbook; `python3 scripts/titan_prep_check.py`.
2. **Remaining:** Titan on the desk; T01 power/console; T02 BSP U55 example; T03 golden load; T04 measured INT8 band labelled **ON-SILICON**; T05 WAV→M85 frontend→U55; T06 BSP PDM; T07 PDM→frontend; T08 **BLOCKED** until SELECTION_GATE + written freeze, then PDM→CNN; T09 M85 DSP goldens on the same PCM with NPU running; T10 fill clocks from the flashed image; T11 semantic-absent fail-open. Cadence stays **CLOSED**.
3. **Who acts:** lab — goldens, pin, compare, this file, T00. Board-holder — T01–T07, T09–T11 flash and capture. Captain — written I/O freeze and C1 look; not tensor match when a dump exists.
4. **Shipped on silicon means:** a flashed Titan image whose U55 outputs match golden `expected_int8_output.json` within the **measured** band, receipt labelled **`ON-SILICON`**, **and** M85 DSP deadlines still hold while the NPU runs, **and** if the semantic lane is absent the DSP + visual engine remain live, **and** none of MERT / MuQ / MAEST / Demucs are in that image. Compiler C99 is not that stamp. Host goldens on disk are not that stamp. This runbook is not that stamp.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-09-01 | agent:grok-ssa-titan-runbook | Created PRE-SILICON arrival-day sequence T00–T11; empty ON-SILICON clock table; stop-gates; owners. |
