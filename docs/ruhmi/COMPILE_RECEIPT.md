---
abstract: "PRE-SILICON RUHMI C99 receipt. GHA 33319114336 compiled ad01_int8.tflite then AdaptiveAvgPool2d smoke.onnx. Compiler RAM/Flash/MACs are not Titan latency. Board prep: docs/titan/PREP.md."
---

# RUHMI compile receipt — PRE-SILICON

**HARD FAIL (`SAME_SONG_LOOP_MAX_15MIN`, Captain 2026-08-31).** Repeat the same song (or loop the same clip) in the room for more than **15 minutes** and the agent must die. Kill the player. Do not continue.

Cadence silicon **CLOSED**. No USB. No board. No Titan clock.

| Field | Value |
| --- | --- |
| STATUS | **PASS (PRE-SILICON C99).** Not ON-SILICON. |
| CLAIM | GitHub Actions [33319114336](https://github.com/synqing/SpectraSynq-EdgeAI-Lab/actions/runs/33319114336) on `03d6352` emitted C99 for Renesas `ad01_int8.tflite` then lab `smoke.onnx`. Pooling **must** be `nn.AdaptiveAvgPool2d((1,1))` (D11). `tensor.mean` / ONNX ReduceMean is banned on this graph. RAM / Flash / MACs below are `check_model_metrics.py` compiler reports. They are **not** Titan latency, not RA8P1 wall time, not p50/p95. |
| EVIDENCE | This file; `docs/DECISIONS.md` D9 + D11; `.github/workflows/ruhmi-compile.yml` `RUHMI_REF`; `deployment/ra8p1/Dockerfile` same SHA + gcc-13/libstdc++; `src/edgeai/semantic_v0.py` `self.pool = nn.AdaptiveAvgPool2d((1, 1))`; `tests/test_shapes.py` forbids `ReduceMean`, requires `GlobalAveragePool` or `AveragePool`; public GHA 33319114336 Success (3m1s, artefacts `ruhmi-ad01` 701 KB, `ruhmi-c99` 3.73 MB, `smoke-onnx` 1.09 MB); prior fail [33318864219](https://github.com/synqing/SpectraSynq-EdgeAI-Lab/actions/runs/33318864219). Titan board sequence is **not** this receipt — see `docs/titan/PREP.md`. |
| COMMAND | No MERA re-run this write. Cadence CLOSED. No USB. Public run page read for 33319114336 (Success, `03d6352`, three artefacts). Source: `rg AdaptiveAvgPool2d src/edgeai/semantic_v0.py`; workflow `RUHMI_REF=6c5aad901a1a41e28f6e306bfc35c44659e89502`. |
| METHOD_RISK | Byte counts are restated from the 2026-08-30 receipt / D11, not re-parsed from downloaded `*_metrics.txt`. Artefacts are generated, not in git. This Mac is not the compile host. Host ORT INT8 ≠ MERA INT8 ≠ U55 INT8. |
| NEXT | Do not quote 768 B or 262,414 B RAM as Titan. Do not quote 35.56 M MACs as milliseconds. Keep AdaptiveAvgPool. Do not reopen Cadence. Board work starts at `docs/titan/PREP.md` when a RA8P1 exists — golden tensor first, PDM last, stamp `ON-SILICON` only from a flashed image. |

## Stamp

**PRE-SILICON.** Compiler SRAM / flash / MAC counts are **not** Titan latency.

| Lookalike | Correct stamp | Not |
| --- | --- | --- |
| RAM 768 B / 262,414 B, Flash 217,968 B / 188,896 B, 0.26 M / 35.56 M MACs | **PRE-SILICON** compiler (`check_model_metrics.py`) | Titan / U55 board latency |
| Host 1.33 ms / window (`docs/HOST_RECEIPTS.md`) | **HOST-ONLY** MPS | U55 |
| “NPU in 1 ms” | **PRE-SILICON hypothetical** | Measured board |
| PaRIRset ~100 ms | **HOST-ONLY** acoustic path | This graph |
| K1 50 ms cadence | **ON-SILICON K1 C0-v2**, Cadence **CLOSED** | U55 student |

## Pin (D9)

| Item | Value |
| --- | --- |
| GHA | [33319114336](https://github.com/synqing/SpectraSynq-EdgeAI-Lab/actions/runs/33319114336) Success on `03d6352` (“Replace ReduceMean with AdaptiveAvgPool2d so U55 C99 is one subgraph.”) |
| ruhmi-framework-mcu | `6c5aad901a1a41e28f6e306bfc35c44659e89502` (Release-2026-06-19). Short `6c5aad9` is docs-only. |
| MERA | `2.6.0+pkg.4815` (`cp310` manylinux x86_64) |
| Host | ubuntu-22.04 GHA, Python 3.10 for MERA. Mac Docker is not this receipt. |
| libstdc++ | `ppa:ubuntu-toolchain-r/test` + `libstdc++6`/`libgcc-s1` + gcc-13 (run 33317047371 died on `GLIBCXX_3.4.31`/`3.4.32`) |
| Order | `ad01_int8.tflite --npu --ref-data` **then** `smoke.onnx --npu --quantize --ref-data` |

## Graphs

| Graph | RAM arena | Flash params | MACs | NPU node coverage | C99 |
| --- | --- | --- | --- | --- | --- |
| MLPerf Tiny `ad01_int8.tflite` | 768 B | 217,968 B | 0.26 M | 100% (32/32) | yes |
| lab `smoke.onnx` (**AdaptiveAvgPool2d required**) | 262,414 B | 188,896 B | 35.56 M | 88.9% (64/72, 8 CPU fallback) | yes |

**AdaptiveAvgPool2d is required** on the U55 witness graph (D11). Export is ONNX `GlobalAveragePool` / `AveragePool`, not a node named AdaptiveAvgPool. Banned: `x.mean(dim=(2,3))` → ReduceMean (Vela splits Ethos-U ops). Banned: STFT inside the NPU graph (D3 — export CNN on log-mel).

Prior fail (33318864219): same smoke graph with ReduceMean quantized (PSNR 27.8, 94.7% NPU ops) then Vela `More than one Ethos-U custom operator found in subgraph`. Compiler-reported on that fail (still PRE-SILICON, **not** a pass): SRAM 250 KiB, flash 186.92 KiB, 35.6 M MACs/batch, MEAN unsupported.

Artefacts: GHA `ruhmi-c99`, `ruhmi-ad01`, `smoke-onnx`. Not committed (generated).

## Titan

This file does not measure a board. **Point:** [`docs/titan/PREP.md`](../titan/PREP.md) — PRE-SILICON arrival sequence (golden tensor → U55 before PDM). Until that path exists as a file, the living sequence is `docs/TITAN_BRINGUP.md`. Neither document may quote the table above as Titan latency.

Not ON-SILICON. No latency claim. MERT / MuQ / MAEST / Demucs stay off Titan.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-30 | agent:edgeai | First C99 from ad01 + smoke on GHA. |
| 2026-08-31 | agent:grok-ssa-w3-l30 | Contract fields. AdaptiveAvgPool required. Compiler RAM/Flash/MACs ≠ Titan latency. Point `docs/titan/PREP.md`. |
