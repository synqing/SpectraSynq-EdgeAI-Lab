---
abstract: "Amendment 001 delta: what stays, what is deferred, what is superseded. Read before treating Semantic-v0 as the product model."
---

# Amendment 001 — delta report

**HARD FAIL (`SAME_SONG_LOOP_MAX_15MIN`, Captain 2026-08-31).** Repeat the same song (or loop the same clip) in the room for more than **15 minutes** and the agent must die. Captain will destroy them by setting them on fire. Kill the player. Do not continue.

Date: 2026-08-30. Previous brief still in force except where this file says otherwise.

## Remains valid (keep, do not rebuild)

| Asset | Why it stays |
| --- | --- |
| Python 3.12 + uv + MPS host env | Toolchain, not a model choice |
| TRAIN→SAVE→LOAD→EXPORT smoke | Independent of MIR target |
| ONNX opset 14 + host ORT INT8 | Deployment lane |
| `deployment/ra8p1/` Docker/GHA RUHMI path | Still required. **PRE-SILICON C99 executed** on GHA 33319114336 (`ad01_int8.tflite` + `smoke.onnx`). Mac Docker daemon is still not the compile host. |
| Golden-vector *format* | Reuse when a real student is frozen |
| Song-level split rule | Still required for any training set |
| Licence ≠ technical suitability | Strengthened, not weakened |
| Additive ML: DSP must work if ML is absent | Unchanged |
| No K1 firmware contamination | Unchanged |

Semantic-v0 **code, checkpoint, ONNX, synthetic receipts** stay on disk as `experiments/semantic_v0_*`. They are **not** architecture authority. See [experiments/semantic_v0/AUTHORITY.md](../experiments/semantic_v0/AUTHORITY.md).

## Superseded assumptions

| Old | Now |
| --- | --- |
| First model = vocals/drums/bass activity CNN | Candidate **after** MIR oracle + selection gate |
| MUSDB18 as default starting dataset | One research/teacher asset among many; not the start |
| Pre-Titan success = any compiled semantic CNN | That pipeline is **necessary but not sufficient**. Need a host MIR oracle lab + evidence-backed descriptor shortlist + then a justified student |
| Freeze 16 kHz / 1 s / 64-mel now | Hypothetical frontend for the *experiment*, not a product lock |
| Custom ontology (BUILDING, DROPPING, …) | Hypotheses until existing MIR ontologies are inspected |

## Deferred (do not do yet)

- Further Semantic-v0 training / hyperparameter search
- MUSDB download as a blocker
- Inventing SpectraSynq custom labels and manufacturing GT
- Deploying MERT / MuQ / MAEST / Demucs onto Titan
- Elaborate user-research / visual A/B platform
- Large foundation-model downloads as a default path

## New work required (this amendment)

1. MIR landscape map (SpectraSynq visual utility, not a generic survey)
2. Structured registry with **split** code / weights / dataset licences
3. Host oracle lab: same audio → DSP + conventional MIR + (later) teachers
4. Time-aligned traces; redundancy vs existing DSP
5. Eval corpus manifests (no unlicensed audio in git)
6. Student-model **selection gate** before freezing v0 outputs
7. Distillation / teacher-student as a first-class path
8. Visual-utility hook schema (interface only)

## Status after this session

| Phase (amendment) | Status |
| --- | --- |
| 0A host toolchain | done (prior session) |
| 0B RUHMI/U55 compile | **PRE-SILICON C99 PASS** on GHA 33319114336 (ad01 + AdaptiveAvgPool2d smoke). Not ON-SILICON. |
| 1 landscape | done |
| 2 registry | seeded, not the entire field |
| 3 host oracle bring-up | conventional MIR + DEAM human vs DSP + Essentia heads **executed**; MERT/MuQ/Demucs researched, not executed |
| 4 eval corpus | synthetic contrast set + local DEAM + PaRIRset test RIRs |
| 5 aligned traces | conventional + DEAM human arousal + delay-aware PaRIRset |
| 6 shortlist | **not frozen** — candidates named, gate open |
| 7–8 student | deferred |

### Update — 2026-08-31

RUHMI compile is no longer “path wired / not run”. Amendment 001’s 0B row above is the current status. Semantic-v0 remains an experiment. Student gate still OPEN.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-30 | agent:edgeai | Created after Amendment 001. |
| 2026-08-31 | agent:edgeai | 0B compile is PRE-SILICON PASS, not “not run”. |
