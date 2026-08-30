---
abstract: "Measured HOST-ONLY numbers from the 2026-08-30 bootstrap. Not silicon. Synthetic corpus, not MUSDB. Do not quote as product accuracy."
---

# Host receipts — 2026-08-30 bootstrap

All rows **HOST-ONLY**. Corpus **SYNTHETIC**. Titan was not present. Docker daemon was not running, so RUHMI/MERA did not compile.

## Probe

| Item | Value |
| --- | --- |
| Python | 3.12.11 (uv venv; system 3.14 unused) |
| torch | 2.13.0 |
| torchaudio | 2.11.0 |
| onnx | 1.22.0 |
| onnxruntime | 1.29.0 |
| device | MPS available and used |
| smoke | TRAIN→SAVE→LOAD→EXPORT **PASS** (load MAE 0, ONNX vs PyTorch MAE 0) |

## Semantic-v0 (synthetic)

| Item | Value |
| --- | --- |
| params | 153 283 |
| FP32 weights | 613 132 bytes |
| FP32 ONNX | 613 727 bytes |
| host ORT INT8 ONNX | 213 240 bytes |
| opset | 14 |
| graph | 15 Conv, 15 Relu, 1 ReduceMean, 1 Gemm, 1 Sigmoid |
| songs | 34 train / 6 val / 8 test (song-level) |
| train wall | 7.2 s |
| host infer | 1.33 ms / window on MPS — not U55 |

### Test (best val checkpoint, n=64 windows)

| class | MAE | F1 @ 0.5 |
| --- | --- | --- |
| vocals | 0.101 | 1.00 |
| drums | 0.229 | 0.67 |
| bass | 0.054 | 1.00 |
| macro | 0.128 | 0.89 |

Vocals/bass F1 = 1.0 on synthetic **because the generator is spectrally easy**. Drums are the only class that is not a toy. These numbers are a pipeline witness, not a product claim.

### Host ORT INT8 vs ONNX FP32 (n=48)

Quantization did **not** destroy the synthetic scores (macro MAE 0.137 → 0.134). This is still not MERA INT8 and not U55 INT8.

## Golden vectors

32 cases in `artifacts/golden/` (gitignored). Two copies under `test_vectors/smoke/` for the repo.

## Not measured

- RUHMI/MERA compile
- NPU vs CPU partition
- compiler RAM/Flash/MAC
- anything on RA8P1 silicon
