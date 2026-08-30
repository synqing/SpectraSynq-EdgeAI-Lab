---
abstract: "PRE-SILICON RUHMI C99. GHA 33319114336 compiled ad01_int8.tflite and smoke.onnx. Compiler-reported RAM/Flash/MACs, not silicon."
---

# RUHMI compile receipt — PRE-SILICON

GitHub Actions run [33319114336](https://github.com/synqing/SpectraSynq-EdgeAI-Lab/actions/runs/33319114336) on `03d6352`.
Pin: ruhmi-framework-mcu `6c5aad901a1a41e28f6e306bfc35c44659e89502`, MERA `2.6.0+pkg.4815`.

These numbers come from `check_model_metrics.py`. They are **not** board measurements.

| Graph | RAM arena | Flash params | MACs | NPU node coverage | C99 |
| --- | --- | --- | --- | --- | --- |
| MLPerf Tiny `ad01_int8.tflite` | 768 B | 217,968 B | 0.26 M | 100% (32/32) | yes |
| lab `smoke.onnx` (AdaptiveAvgPool2d) | 262,414 B | 188,896 B | 35.56 M | 88.9% (64/72, 8 CPU fallback) | yes |

Prior fail (33318864219): same smoke graph with `ReduceMean` quantized (PSNR 27.8) then Vela `More than one Ethos-U custom operator`. D11.

Artifacts: GHA `ruhmi-c99` and `ruhmi-ad01`. Not committed (generated).

Not ON-SILICON. No latency claim.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-30 | agent:edgeai | First C99 from ad01 + smoke on GHA. |
