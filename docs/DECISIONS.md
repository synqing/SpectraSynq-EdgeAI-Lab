---
abstract: "Architectural choices for SpectraSynq-EdgeAI-Lab Semantic-v0. Read before changing the model graph, frontend, dataset split, or RUHMI path."
---

# Decisions

Each entry: chosen / why / rejected / revisit evidence.

## D1 — Separate research repo

**Chosen:** `SpectraSynq-EdgeAI-Lab`, not K1 firmware.
**Why:** experimental ML deps must not contaminate production firmware.
**Rejected:** a branch inside K1 Firmware.
**Revisit:** when a model has on-silicon evidence and a planned integration.

## D2 — Python 3.12 + uv for training; Python 3.10 x86 for RUHMI

**Chosen:** host venv is CPython 3.12 (Homebrew/uv). System Python 3.14 is not used.
**Why:** PyTorch/torchaudio/onnxruntime wheels trail the newest CPython. RUHMI/MERA ships `cp310` manylinux x86_64 and win_amd64 only (mera 2.6.0+pkg.4815).
**Rejected:** one environment for both lanes; native macOS RUHMI (does not exist).
**Revisit:** if Renesas ships an arm64 / cp312 wheel.

## D3 — CNN consumes log-mel, not PCM

**Chosen:** host frontend is 16 kHz mono, 1.0 s, 25 ms window, 10 ms hop, 64 mels, 100 frames. Exported NPU graph input is `(1, 1, 64, 100)` log-mel.
**Why:** FFT/STFT is cheap on M85 and hostile to U55. Golden tensors then isolate “did the NPU run this graph?” from “did we compute mel correctly?”
**Rejected:** exporting the STFT into the U55 graph; instance-max normalisation (silence becomes noise).
**Revisit:** if a measured frontend on M85 exceeds its budget, or a different rate (12.8 / 24 / 32 kHz) wins an A/B.

## D4 — Depthwise-separable CNN, ReLU, ReduceMean head, sigmoid

**Chosen:** MobileNet-like DS-CNN, ~100k–300k params, ReLU, mean over HxW, linear → 3 logits, sigmoid at export.
**Why:** RUHMI has compiled MobileNetV2 / MnasNet / EfficientNet / ResNet18 / INT8 KWS. Quantizer table: Conv2d, BatchNorm, ReLU, ReduceMean, Gemm, Sigmoid are A8 on MCU_ETHOS. ONNX Sigmoid is F32 on MCU_CPU — another reason to target `--npu`.
**Rejected:** transformers, foundation models, SiLU-only graphs, custom ops.
**Revisit:** if Vela/RUHMI reports material CPU fallback on this graph; then change the graph before squeezing desktop accuracy.

## D5 — ONNX opset 14, RUHMI quantizer flow

**Chosen:** `torch.onnx.export` opset 14, static batch=1. RUHMI compile uses `--npu --quantize` (ONNX frontend is documented as quantizer-flow only).
**Why:** RA8P1 zoo includes several opset-14 ONNX nets. Host ORT INT8 is a **different** quantizer than MERA — both are recorded, never treated as equivalent.
**Rejected:** waiting for a beautiful FP32 model before the first compile; TFLite-only path as a gate (RUHMI accepts ONNX).
**Revisit:** if ONNX→TFL lowering drops DepthwiseConv; then export TFLite or rewrite groups.

## D6 — Synthetic corpus now; MUSDB18 as optional research source

**Chosen:** always-on synthetic stem generator so TRAIN/EVAL/EXPORT work with zero Zenodo access. MUSDB18 adapter + official train/test folders + hashed val carve when `MUSDB_ROOT` exists.
**Why:** MUSDB requires an access request and is not a shipping licence. Blocking the lab on a 22 GB download is busywork.
**Rejected:** committing any audio corpus; treating synthetic F1 as product evidence.
**Revisit:** when MUSDB (or a cleared corpus) is on disk; then re-train and replace SYNTHETIC receipts.

## D7 — Activity is log-RMS of each stem, not mix share, not binary

**Chosen:** per-stem RMS mapped log-scale from silence `1e-4` to loud `0.15`, clipped to [0, 1]. Loss is `BCEWithLogits` on those soft targets.
**Why:** a quiet drum hit should still modulate lights; mix-share would hide it behind a loud vocal.
**Rejected:** hard 0/1 labels; softmax (sources coexist).
**Revisit:** if MUSDB labels from this mapping do not correlate with listening; then change the mapping, not the split rule.

## D8 — MIR-first; Semantic-v0 is an experiment (Amendment 001)

**Chosen:** Host MIR oracle + registry + selection gate **before** freezing any embedded student outputs. Semantic-v0 remains as a U55-shaped toolchain experiment only.
**Why:** vocals/drums/bass on synthetic stems skipped a mature field (MTG tagging, DEAM affect, MERT/MuQ teachers, separator-as-teacher).
**Rejected:** treating Semantic-v0 as architecture authority; inventing BUILDING/DROPPING labels first.
**Revisit:** when the eight gate questions in `docs/mir/SELECTION_GATE.md` have evidence.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-30 | agent:edgeai | Created with D1–D7 at lab bootstrap. |
| 2026-08-30 | agent:edgeai | D8 — Amendment 001 MIR-first. |
