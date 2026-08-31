---
abstract: "Host receipt index. 2026-08-30 Mac bootstrap is HOST-ONLY/SYNTHETIC. Live pooling AdaptiveAvgPool2d (D11); ReduceMean dump is stale. C0-v2 PASS ON_SILICON_PIXEL_VALIDATED. Cadence CLOSED. Demucs not installed. Not product accuracy."
---

# Host receipts

**HARD FAIL (`SAME_SONG_LOOP_MAX_15MIN`, Captain 2026-08-31).** Repeat the same song (or loop the same clip / 8 s holdout) in the room for more than **15 minutes** and the agent must die. Kill the player. Do not continue.

**Cadence silicon CLOSED (D20).** Do not run `scripts/gate_c0_cadence_silicon.py`. Do not open USB. Do not replay the 8 s loop.

| Field | Value |
| --- | --- |
| STATUS | **PASS as an index.** Mac bootstrap 2026-08-30 remains HOST-ONLY / SYNTHETIC. Live U55 witness pooling is **AdaptiveAvgPool2d**, not ReduceMean (D11). C0-v2 is **PASS** `ON_SILICON_PIXEL_VALIDATED` (not a host number). Cadence **CLOSED**. Demucs **not installed**. |
| CLAIM | Quote 2026-08-30 F1/MAE only as a pipeline witness on a sine/noise generator. Do **not** cite `docs/onnx_graph_semantic_v0.json` (`ReduceMean: 1`) as the live graph. Live code is `nn.AdaptiveAvgPool2d((1,1))` → ONNX GlobalAveragePool/AveragePool (`src/edgeai/semantic_v0.py`, `tests/test_shapes.py`). Host ORT INT8 ≠ MERA INT8 ≠ U55 INT8. Host 1.33 ms/window is MPS, not U55. C0-v2 PASS does not reopen cadence and does not freeze student I/O. |
| EVIDENCE | This file; `artifacts/host_probe.json`; `artifacts/smoke/receipt.json`; `experiments/semantic_v0_synth/receipt.json`; `artifacts/export/quant_report.json`; `src/edgeai/semantic_v0.py` `self.pool = nn.AdaptiveAvgPool2d((1, 1))`; `tests/test_shapes.py::test_onnx_export_avoids_reducemean`; D11 in `docs/DECISIONS.md`; GHA 33319114336 AdaptiveAvgPool C99 vs 33318864219 ReduceMean split; `artifacts/gate_c0v2/C0V2_RESULT.json` (`c0v2: PASS`); `docs/mir/GATE_C.md`; D20 cadence CLOSED; `pyproject.toml` / `uv.lock` (no `demucs`); `docs/mir/P3C_RECEIPT.json` `demucs_installed: false`. |
| COMMAND | No train, no USB, no Cadence, no `uv add demucs`, no torch.hub, no Bose. Source-read + existing receipts only. |
| METHOD_RISK | Bootstrap bytes/ops were not re-exported this write. `docs/onnx_graph_semantic_v0.json` is a **stale** 2026-08-30 dump and still says ReduceMean. C0V2_RESULT.json still contains the in-run string `cadence: OPEN — not this run` — that is the 2026-08-31 C0-v2 session, **not** live programme cadence (D20 CLOSED). INT8 MAE 0.137 → 0.134 is host ORT QDQ on synthetic n=48. |
| NEXT | C1 LGP (`docs/mir/GATE_C1.md`). Do not reopen cadence. Do not install Demucs. Do not compile the ReduceMean dump. Keep AdaptiveAvgPool. Student I/O stays unfrozen. |

## Live stamps (2026-08-31)

| Stamp | Label | Where |
| --- | --- | --- |
| C0-v2 **PASS** `source_share × WaveformTempo × head_position` | **ON-SILICON** `ON_SILICON_PIXEL_VALIDATED` | `artifacts/gate_c0v2/C0V2_RESULT.json` (`Q1`/`Q2`/`Q3` PASS, `lag_corrected: false`). Method `docs/mir/GATE_C0V2.md`. Probe `k1_main_rpl_rtrace_probe` @ `349d3cd4`. |
| Two-clock C0 | **FAIL** corpse `INVALID_TEMPORAL_EXECUTION` | `artifacts/gate_c0/` — not the live close |
| Cadence silicon | **CLOSED** | D20. Envelope only: slowest 0-delay PASS **5 Hz**; largest added delay PASS **50 ms** at 20 Hz; joint **5 Hz + 50 ms FAIL**. Runner retired. |
| Host cadence rehearsal | **HOST-ONLY** / `HOST_PIXEL_VALIDATED` | `artifacts/gate_c_cadence/receipt.json`. Not C0. Do not freeze I/O from host 20 Hz / host 50 ms FAIL. |
| Semantic-v0 train/export | **HOST-ONLY** / **SYNTHETIC** | tables below |
| Smoke C99 (AdaptiveAvgPool) | **PRE-SILICON** | `docs/ruhmi/COMPILE_RECEIPT.md` GHA 33319114336. Not Titan latency. |
| Demucs | **not installed** | No extra, no `uv.lock` pin, `try_demucs()` → `ImportError`. Weights UNKNOWN / scientific-use, not MIT. Not Titan. |

Holdout Q numbers for C0-v2 (ON-SILICON, n=10): Q1 median Spearman **0.83** PASS; Q2 Δ **0.69** 9/9 PASS; Q3 Δ **0.58** 9/9 PASS. Native P3-C-QUANT in the same JSON is HOST-ONLY reference, not the silicon close.

## Probe (HOST-ONLY, 2026-08-30)

| Item | Value |
| --- | --- |
| Python | 3.12.11 (uv venv; system 3.14 unused) |
| torch | 2.13.0 |
| torchaudio | 2.11.0 |
| onnx | 1.22.0 |
| onnxruntime | 1.29.0 |
| device | MPS available and used |
| smoke | TRAIN→SAVE→LOAD→EXPORT **PASS** (load MAE 0, ONNX vs PyTorch MAE 0) |

Re-probe: `uv run edgeai-host-probe`. Platform assumptions: `docs/HOST.md`.

## Semantic-v0 (HOST-ONLY, SYNTHETIC)

Experiment / toolchain witness. Not architecture. Not the RA8P1 student. I/O not frozen. `experiments/semantic_v0/AUTHORITY.md`.

| Item | Value | Live vs dump |
| --- | --- | --- |
| params | 153 283 | same |
| FP32 weights | 613 132 bytes | same |
| FP32 ONNX | 613 727 bytes | same |
| host ORT INT8 ONNX | 213 240 bytes | same; not MERA / not U55 |
| opset | 14 | same |
| **live graph** | 15 Conv, 15 Relu, **1 AdaptiveAvgPool2d**, 1 Gemm, 1 Sigmoid (BN folded) | D11. ONNX `GlobalAveragePool` or `AveragePool`. |
| **2026-08-30 dump** | 15 Conv, 15 Relu, **1 ReduceMean**, 1 Gemm, 1 Sigmoid | **STALE.** `docs/onnx_graph_semantic_v0.json`. Do not compile. Do not quote as live. |
| songs | 34 train / 6 val / 8 test (song-level) | SYNTHETIC generator |
| train wall | 7.2 s | HOST-ONLY |
| host infer | 1.33 ms / window on MPS | **not** U55 |

GHA **33318864219**: ReduceMean smoke quantized then Vela split (`More than one Ethos-U custom operator found in subgraph`). GHA **33319114336**: AdaptiveAvgPool2d smoke C99 **PASS** (PRE-SILICON: RAM 262,414 B, Flash 188,896 B, 35.56 M MACs, 88.9% node coverage). ReduceMean remains in the RUHMI quantizer table; it is still banned on **this** graph.

### Test (best val checkpoint, n=64 windows)

| class | MAE | F1 @ 0.5 |
| --- | --- | --- |
| vocals | 0.101 | 1.00 |
| drums | 0.229 | 0.67 |
| bass | 0.054 | 1.00 |
| macro | 0.128 | 0.89 |

Vocals/bass F1 = 1.0 on synthetic **because the generator is spectrally easy**. Drums are the only class that is not a toy. These numbers are a pipeline witness, not a product claim, not Gate A, not Gate C.

### Host ORT INT8 vs ONNX FP32 (n=48)

`artifacts/export/quant_report.json`: FP32 macro MAE **0.137** → INT8 **0.134**. Quantization did **not** destroy the synthetic scores. This is still not MERA INT8 and not U55 INT8.

## Other HOST receipts (pointers)

Do not treat this table as silicon. Full numbers live in the named files.

| Receipt | Stamp | Path |
| --- | --- | --- |
| Share student recoverability | HOST PASS; I/O **unfrozen**; four-source including `other` | `artifacts/share_student/receipt.json` · `docs/mir/SHARE_STUDENT.md` |
| P3-C visual engine | HOST PASS on Tempo head; Demucs **NO** | `docs/mir/P3C_RECEIPT.json` `demucs_installed: false` |
| DEAM arousal vs DSP | HOST-ONLY | `artifacts/deam_arousal/receipt.json` |
| Golden vectors | 32 HOST-ONLY cases | `artifacts/golden/` (gitignored); two copies under `test_vectors/smoke/` |
| Host cadence ladder | HOST_PIXEL_VALIDATED, `not_c0` | `artifacts/gate_c_cadence/receipt.json` |

## Demucs (HOST teacher probe — not this Mac install)

| Layer | Status |
| --- | --- |
| Code | MIT (Meta). PyPI MIT is **code**. |
| Weights | **UNKNOWN — not MIT** (scientific-use; issue #327). |
| This venv | **not installed.** No `demucs` extra. `uv.lock` has zero `demucs`. |
| Role if ever used | HOST envelopes from stems → tiny student. **Not** Titan / U55 / PDM. Teacher use does not clear a derived student. |
| This write | Did not `uv add demucs`. Did not fetch weights. |

## Not measured here

- U55 / Titan wall time, RAM in the running SoC, p50/p95
- MERA INT8 accuracy of semantic-v0 (smoke C99 is a different artefact)
- Anything that requires USB-CDC, Cadence cells, or Bose
- Demucs SDR or stem envelopes

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-30 | agent:edgeai | Mac bootstrap HOST-ONLY numbers. |
| 2026-08-31 | agent:edgeai | Note GHA C99; local Docker still not the compile host. |
| 2026-08-31 | agent:grok-ssa-w3-l35 | Index: D11 AdaptiveAvgPool live vs ReduceMean dump; C0-v2 PASS; cadence CLOSED; Demucs not installed. |
