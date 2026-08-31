---
abstract: "L24 PASS: Semantic-v0 remains D22 HOST experiment/toolchain, not architecture. D8 + AUTHORITY.md. Student I/O not frozen from 16 kHz/1 s/3 sigmoids."
---

# L24 — Semantic-v0 still experiment

STATUS: PASS
CLAIM: Semantic-v0 is still an **experiment / toolchain witness**, not architecture authority, not the RA8P1 student contract, and not a selection-gate winner. D22 unblocked this HOST experiment; it did **not** promote the graph. Student I/O is **not** frozen from it (not 16 kHz / 1 s / 64×100 log-mel / 3 unconstrained sigmoids vocals-drums-bass).
EVIDENCE: `experiments/semantic_v0/AUTHORITY.md` (“not the SpectraSynq embedded model contract”; “Do not freeze 16 kHz / 1 s / 3 sigmoids as the RA8P1 contract”); AGENTS.md hard rule + lane “OPEN as experiment/toolchain only, not architecture authority”; `docs/DECISIONS.md` D8 (MIR-first before freezing any embedded student outputs) and D22 (HOST lanes open, cadence CLOSED); `docs/AMENDMENT_001_DELTA.md` (“not architecture authority”; freeze 16 kHz/1 s/64-mel superseded as hypothetical frontend); `mir/registry.yaml` id `semantic-v0-experiment` spectrasynq “Toolchain witness only. Not architecture authority.”; README.md; `docs/mir/SELECTION_GATE.md` “Do not freeze Student-v0 yet.”; `docs/mir/SHARE_STUDENT.md` four-source including `other`, I/O unfrozen; L06 transport frozen for C1, student I/O unfrozen, Semantic-v0 3-class is a different experiment.
COMMAND: docs-read only. No train. No room audio. No USB. `rg -n 'not architecture|toolchain witness|Do not freeze 16 kHz' experiments/semantic_v0/AUTHORITY.md AGENTS.md docs/DECISIONS.md docs/AMENDMENT_001_DELTA.md README.md mir/registry.yaml docs/mir/SELECTION_GATE.md`
METHOD_RISK: Registry `deployment: potential_embedded_student` and `docs/MODEL_CONTRACT.md` title “SpectraSynq Audio Semantic Model” look product-shaped; AUTHORITY + D8 override. D3/D4 host-frontend numbers are experiment graph, not a freeze (D3 revisit + Amendment 001). `docs/HOST_RECEIPTS.md` still says ReduceMean; live graph is `nn.AdaptiveAvgPool2d((1,1))` (D11). Synthetic F1 / r=0.99 is not Gate A. U55 metrics NOT_MEASURED. Copying Semantic-v0 I/O would drop `other` and swap share for abs-activity.
NEXT: Do not train as the default programme. Do not freeze 16 kHz / 1 s / 3 sigmoids. Re-enter only if SELECTION_GATE independently picks source-activity with a real stem/separator teacher, not the sine/noise generator. Share-student 21k CNN is a different graph; freeze I/O only after Gate C / C1, never from this experiment.
KEEP: `src/edgeai/semantic_v0.py` as U55-shaped toy (Conv/ReLU/AdaptiveAvgPool2d/Gemm/Sigmoid). ReduceMean banned. Golden-vector *format* only. Weights/ONNX stay gitignored.
GATE: Nine SELECTION_GATE questions not all closed. Share student is a different graph. Smoke C99 GHA 33319114336 is PRE-SILICON, not this net ON-SILICON.
HARD FAIL: `SAME_SONG_LOOP_MAX_15MIN`. Cadence CLOSED. No 8 s loop. No USB.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:grok | L24 contract: Semantic-v0 still experiment, not architecture. |
| 2026-08-31 | agent:grok | Explicit: D22 HOST-open ≠ architecture; student I/O not frozen from 3-class 1 s graph. |
