---
abstract: "L24 PASS: Semantic-v0 remains experiment/toolchain, not architecture. D8 + AUTHORITY.md. I/O unfrozen."
---

# L24 — Semantic-v0 still experiment

STATUS: PASS
CLAIM: Semantic-v0 is still experiment / toolchain witness, not architecture authority, not the RA8P1 student contract, and not a selection-gate winner.
EVIDENCE: `experiments/semantic_v0/AUTHORITY.md`; AGENTS.md (hard rule + lane OPEN experiment-only); `docs/DECISIONS.md` D8; `docs/AMENDMENT_001_DELTA.md`; `mir/registry.yaml` id `semantic-v0-experiment` spectrasynq “Toolchain witness only. Not architecture authority.”; README.md; `docs/mir/SELECTION_GATE.md` “Do not freeze Student-v0 yet.”
COMMAND: docs-read only. No train. No room audio. No USB. `rg -n 'not architecture|toolchain witness' experiments/semantic_v0/AUTHORITY.md AGENTS.md docs/DECISIONS.md docs/AMENDMENT_001_DELTA.md README.md mir/registry.yaml`
METHOD_RISK: Registry `deployment: potential_embedded_student` and MODEL_CONTRACT name look product-shaped; AUTHORITY + D8 override. `docs/HOST_RECEIPTS.md` still says ReduceMean; live graph is `nn.AdaptiveAvgPool2d((1,1))` (D11). Synthetic F1 / r=0.99 is not Gate A. U55 metrics NOT_MEASURED.
NEXT: Do not train as the default programme. Do not freeze 16 kHz / 1 s / 3 sigmoids. Re-enter only if SELECTION_GATE picks source-activity with a real stem/separator teacher, not the sine/noise generator.
KEEP: `src/edgeai/semantic_v0.py` as U55-shaped toy (Conv/ReLU/AdaptiveAvgPool2d/Gemm/Sigmoid). ReduceMean banned. Golden-vector *format* only. Weights/ONNX stay gitignored.
GATE: Nine SELECTION_GATE questions not all closed. Share student is a different graph. Smoke C99 GHA 33319114336 is PRE-SILICON, not this net ON-SILICON.
HARD FAIL: `SAME_SONG_LOOP_MAX_15MIN`. Cadence CLOSED. No 8 s loop.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:grok | L24 contract: Semantic-v0 still experiment, not architecture. |
