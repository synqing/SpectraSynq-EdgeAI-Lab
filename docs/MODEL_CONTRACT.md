---
abstract: "Model Contract fields Semantic-v0 must fill before it is called more than a throwaway experiment. Values come from receipts, not from hope."
---

# Model Contract — Semantic-v0

Fill from `experiments/*/receipt.json` and `artifacts/export/quant_report.json`.
Blank / `NOT_MEASURED` is honest. Invented numbers are not.

## Identity

| Field | Value |
| --- | --- |
| name | SpectraSynq Audio Semantic Model |
| version | v0 |
| purpose | Estimate vocal, drum, bass activity from a short mixed-audio window, as a modulation signal for a visual engine |

## Input

| Field | Value |
| --- | --- |
| sample_rate | 16000 Hz (hypothesis, not product lock) |
| channels | 1 |
| PCM | float32 host / int16 WAV golden |
| context | 1.0 s |
| stride | not locked; semantic lane is slower than the audio callback |
| frontend | log-mel, 25 ms window, 10 ms hop, 64 bins, 100 frames, HTK mel, log(power+1e-6), clip [-12, 6] |
| tensor | `(1, 1, 64, 100)` NCHW float32 (quantized later) |

## Output

| Field | Value |
| --- | --- |
| classes | `vocals`, `drums`, `bass` |
| range | `[0, 1]` sigmoid activity |
| interpretation | log-RMS presence of that stem in the window, not mix share, not a one-shot event |
| smoothing | none in v0; add only with evidence |

## Performance

| Field | Value |
| --- | --- |
| train corpus | SYNTHETIC (MUSDB_ROOT absent). See datasets/README.md |
| val/test | song-level 34 / 6 / 8, `datasets/manifests/synthetic_v0.json` |
| FP32 metrics | HOST-ONLY synthetic test n=64: vocals MAE 0.101 F1 1.00; drums MAE 0.229 F1 0.67; bass MAE 0.054 F1 1.00. **Not product evidence.** |
| host INT8 metrics | HOST-ONLY ORT QDQ, n=48, macro MAE 0.137 → 0.134. Not MERA. |
| U55 metrics | NOT_MEASURED |

## Deployment

| Field | Value |
| --- | --- |
| param_count | 153 283 |
| FP32 size | 613 132 B weights; 613 727 B ONNX |
| host INT8 ONNX | 213 240 B |
| graph | Conv×15 Relu×15 ReduceMean×1 Gemm×1 Sigmoid×1 (BN folded) |
| NPU coverage | PRE-SILICON / NOT_MEASURED — Docker daemon was down; `deployment/ra8p1/compile.sh` is the path |
| CPU fallback | NOT_MEASURED |
| RAM / scratch | NOT_MEASURED on silicon |
| host infer | 1.33 ms / 1 s window on M4 Pro MPS — not U55 |

## Failure behaviour

If the semantic model is absent, corrupt, delayed, or disabled:
**deterministic SpectraSynq DSP and the visual engine remain functional.**
v0 is an additive lane.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-30 | agent:edgeai | Created; filled first HOST-ONLY synthetic measurements. |
