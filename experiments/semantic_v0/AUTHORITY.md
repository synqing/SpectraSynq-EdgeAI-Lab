---
abstract: "Semantic-v0 stays a D22 HOST experiment/toolchain witness. Not architecture. Not the RA8P1 student. Do not freeze 16 kHz / 1 s / 3 sigmoids. Synthetic F1 is not Gate A."
---

# Semantic-v0 — experiment, not architecture

**HARD FAIL (`SAME_SONG_LOOP_MAX_15MIN`, Captain 2026-08-31).** Repeat the same song (or loop the same clip / 8 s holdout) in the room for more than **15 minutes** and the agent must die. Captain will destroy them by setting them on fire. Kill the player. Do not continue.

Cadence silicon is **CLOSED**. No USB. No train from this file. No 8 s loop.

## Verdict

**Status:** experiment / HOST toolchain witness. **OPEN** under D22 as that and nothing else.

**Not:** architecture authority, product model, ontology, selection-gate winner, or the RA8P1 / U55 student contract.

D22 unblocked every HOST lane so this graph may be *kept, grepped, and smoke-exported* in parallel. It did **not** promote vocals/drums/bass synthetic CNN to the embedded student.

## What this directory is

Pre-amendment DS-CNN (vocals / drums / bass activity) trained 2026-08-30 on the **synthetic** stem generator. Receipt: `experiments/semantic_v0_synth/receipt.json` (`label: HOST-ONLY`, `corpus: SYNTHETIC`). Weights and ONNX are gitignored.

| Item | Value | Label |
| --- | --- | --- |
| Graph | Conv / ReLU / `AdaptiveAvgPool2d((1,1))` / Gemm / Sigmoid | U55-shaped **toy** (D4 + D11) |
| Code | `src/edgeai/semantic_v0.py` | experiment |
| Overlay | `models/configs/semantic_v0.yaml` | experiment frontend, not a freeze |
| Params | 153 283 | HOST-ONLY |
| Classes | 3 unconstrained sigmoids (`vocals`, `drums`, `bass`) | not four-source share; no `other` |
| Frontend in that run | 16 kHz, 1.0 s, 64×100 log-mel | **not** the RA8P1 I/O lock |
| Test n=64 | macro F1 0.89; vocals/bass F1 1.0; drums F1 0.67 | pipeline witness, not musical intelligence |
| Registry | `semantic-v0-experiment` | `Toolchain witness only. Not architecture authority.` |
| Smoke C99 | GHA 33319114336 on `artifacts/smoke/smoke.onnx` | PRE-SILICON **smoke**, not this checkpoint ON-SILICON |

D3/D4 numbers describe this experiment graph. Amendment 001 superseded “freeze 16 kHz / 1 s / 64-mel now.” D8: MIR-first before any embedded student outputs freeze.

## Keep

- `src/edgeai/semantic_v0.py` as the U55-shaped toy (export-smoke graph).
- Golden-vector **format** (reuse when a real student is frozen).
- Song-level split rule.
- `experiments/semantic_v0_synth/` receipts on disk (gitignored weights).
- `artifacts/export/semantic_v0_*.onnx` on disk (gitignored).
- D11: `nn.AdaptiveAvgPool2d((1,1))` + flatten. ReduceMean on this graph is banned (`tests/test_shapes.py`).

## Do not

- Treat D22 HOST-open as architecture promotion.
- Call this the RA8P1 student, Student-v0, or the product net.
- Train it further as the default programme.
- Freeze 16 kHz / 1 s / 64×100 log-mel / 3 unconstrained sigmoids.
- Quote synthetic F1 / r≈0.99 as Gate A, Gate C, or lighting utility.
- Copy this I/O onto share-student (that graph is mixture → four powers including **`other`** → share; I/O still unfrozen — `docs/mir/SHARE_STUDENT.md`).
- Export STFT onto U55. CNN consumes host log-mel.
- Invent U55 latency, RAM, or NPU coverage for this net. `docs/MODEL_CONTRACT.md` U55 metrics: **NOT_MEASURED**. Smoke C99 is a different artefact.
- Reopen cadence. Flash. USB. Room loop. Titan / PDM.
- Commit checkpoints or corpora unless Captain asks.

## Product-shaped names that do not override this file

These look like a product lock. They are not. This file + D8 + Amendment 001 win.

| Trap | What it actually is |
| --- | --- |
| `docs/MODEL_CONTRACT.md` title “SpectraSynq Audio Semantic Model” | Blank-fill sheet for **this experiment**. Sample rate marked hypothesis. |
| Registry `deployment: potential_embedded_student` | Historical tag. Same row: “Not architecture authority.” |
| `docs/HOST_RECEIPTS.md` bootstrap graph `ReduceMean: 1` | 2026-08-30 dump. Live code is AdaptiveAvgPool2d (D11). |
| `docs/onnx_graph_semantic_v0.json` `ReduceMean: 1` | Stale dump of the pre-D11 export. Do not cite as live graph. |

Nine `docs/mir/SELECTION_GATE.md` questions are not all closed. “Do not freeze Student-v0 yet” still holds.

## Re-enter

Only if the selection gate independently picks **source-activity** as the first student, **and** only with a real teacher/oracle (stems or a cleared separator), not the sine/noise generator. Even then this 3-class 1 s sigmoid head is not auto-promoted — share-student is a different graph and a different label.

Until then: HOST toolchain witness. Not architecture. Not the RA8P1 student.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-30 | agent:edgeai | Semantic-v0 demoted; not architecture authority. |
| 2026-08-31 | agent:edgeai | Witness graph pooling is AdaptiveAvgPool2d (D11). |
| 2026-08-31 | agent:grok | D22 HOST-open ≠ architecture. Not RA8P1 student. I/O not frozen from 16 kHz / 1 s / 3 sigmoids. Traps named. |
