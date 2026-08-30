---
abstract: "Semantic-v0 is an experiment from the pre-amendment brief. It is not the SpectraSynq embedded model contract."
---

# Semantic-v0 — not architecture authority

This directory documents the vocals/drums/bass DS-CNN trained on **synthetic** stems on 2026-08-30.

**Status:** experiment / toolchain witness.  
**Not:** product model, ontology, or student-selection winner.

Keep:

- `src/edgeai/semantic_v0.py` (graph used for export smoke)
- `experiments/semantic_v0_synth/` receipts (gitignored weights)
- `artifacts/export/semantic_v0_*.onnx` (gitignored)
- golden-vector *format*

Do not:

- train it further as the default programme
- freeze 16 kHz / 1 s / 3 sigmoids as the RA8P1 contract
- quote synthetic F1 as musical intelligence

Re-enter this graph only if the MIR selection gate (docs/mir/SELECTION_GATE.md) independently picks source-activity as the first student, and then only with a real teacher/oracle (stems or separator), not the synthetic sine/noise generator.

The graph (Conv / ReLU / AdaptiveAvgPool2d / Gemm / Sigmoid) remains a **valid U55-shaped toy** for the deployment smoke lane. ReduceMean is banned on this graph (D11).

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-30 | agent:edgeai | Semantic-v0 demoted; not architecture authority. |
| 2026-08-31 | agent:edgeai | Witness graph pooling is AdaptiveAvgPool2d (D11). |
