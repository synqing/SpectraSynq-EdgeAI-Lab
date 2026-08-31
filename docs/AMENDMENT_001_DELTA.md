---
abstract: "Amendment 001 still owns model selection. Sequence now: C0-v2 ON_SILICON_PIXEL_VALIDATED, cadence CLOSED, C1 next Gate-C action. HOST Demucs/Titan-prep OPEN. Semantic-v0 not product. I/O unfrozen until SELECTION_GATE."
---

# Amendment 001 — delta report

**HARD FAIL (`SAME_SONG_LOOP_MAX_15MIN`, Captain 2026-08-31).** Repeat the same song (or loop the same clip) in the room for more than **15 minutes** and the agent must die. Captain will destroy them by setting them on fire. Kill the player. Do not continue.

Amendment 001 remains in force for **research sequence and model-selection authority**. This file records what later silicon/HOST stamps changed, and what they did **not** change.

Date of original delta: 2026-08-30. Live programme stamp: 2026-08-31 (D20–D22).

## Model-selection authority (unchanged)

These Amendment 001 rules still win. Gate C progress does not override them.

| Rule | Meaning |
| --- | --- |
| MIR-first | Host oracle + registry + `docs/mir/SELECTION_GATE.md` before freezing any embedded student I/O |
| Semantic-v0 | Experiment / U55-shaped toolchain witness. Not architecture. Not the product net. |
| One justified student | Pre-Titan finish is a **selected** student with golden vectors — not the first CNN we trained |
| Teachers stay on HOST | Do **not** put MERT / MuQ / MAEST / Demucs on Titan / U55 / PDM |
| Licence split | Code licence ≠ weight licence ≠ dataset licence. `UNKNOWN` is allowed. Teacher use does not clear derived student weights |
| Additive ML | DSP and the visual engine must still work if ML is absent |
| No firmware contamination | Do not modify production K1 firmware from this repo |
| Song-level splits | If/when we train, split by song, never by window |

Freeze trigger: `docs/mir/SELECTION_GATE.md` satisfied. C1 LGP is **necessary** for visual-utility (Gate C), not a substitute for the nine gate questions, and **not** a lock that stops HOST research.

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
| Serialise all student / Demucs / Titan work behind C1 | **HOST** Demucs teacher probe and Titan **prep docs** are OPEN in parallel (D22). C1 remains the next **Gate-C** action. Cadence silicon stays CLOSED. Demucs/MERT still do not go to Titan |

## Deferred (do not do yet)

- Further Semantic-v0 training / hyperparameter search
- Inventing SpectraSynq custom labels and manufacturing GT
- Deploying MERT / MuQ / MAEST / Demucs onto Titan (HOST teacher probe is **not** this)
- Elaborate user-research / visual A/B platform
- Large foundation-model downloads as a default path
- Reopening cadence silicon cells / 8 s holdout loops
- Freezing student I/O from host 31.25 Hz, from Semantic-v0 16 kHz/1 s/3-sigmoid, or from a student that assumes **5 Hz and 50 ms together**
- Treating the two-clock C0 corpse as a PASS (including +14 hop rescore)

> **Superseded** — “MUSDB download as a blocker” is no longer a deferral. Official MUSDB18 song splits were used for Gate A/B HOST and share-student recoverability. It is still not the default product corpus.

## New work required (this amendment)

Original 2026-08-30 list. Status of each is in the tables below — do not restart a done row.

1. MIR landscape map (SpectraSynq visual utility, not a generic survey)
2. Structured registry with **split** code / weights / dataset licences
3. Host oracle lab: same audio → DSP + conventional MIR + (later) teachers
4. Time-aligned traces; redundancy vs existing DSP
5. Eval corpus manifests (no unlicensed audio in git)
6. Student-model **selection gate** before freezing v0 outputs
7. Distillation / teacher-student as a first-class path
8. Visual-utility hook schema (interface only)

## Status after original session (2026-08-30)

> **Superseded** as a live programme table — see 2026-08-31 sequence below. Kept as history of the MIR-first bootstrap.

| Phase (amendment) | Status (as of 2026-08-30 / 0B update) |
| --- | --- |
| 0A host toolchain | done (prior session) |
| 0B RUHMI/U55 compile | **PRE-SILICON C99 PASS** on GHA 33319114336 (ad01 + AdaptiveAvgPool2d smoke). Not ON-SILICON. |
| 1 landscape | done |
| 2 registry | seeded, not the entire field |
| 3 host oracle bring-up | conventional MIR + DEAM human vs DSP + Essentia heads **executed**; MERT/MuQ/Demucs researched, not executed |
| 4 eval corpus | synthetic contrast set + local DEAM + PaRIRset test RIRs |
| 5 aligned traces | conventional + DEAM human arousal + delay-aware PaRIRset |
| 6 shortlist | **not frozen** — candidates named, gate open |
| 7–8 student | deferred (I/O unfrozen; Semantic-v0 not the freeze) |

### Update — 2026-08-31 (0B)

RUHMI compile is no longer “path wired / not run”. Amendment 001’s 0B row above is the current compile status. Semantic-v0 remains an experiment. Student gate still OPEN.

### Update — 2026-08-31: live research sequence

Amendment 001 still says **MIR-first, then a justified student**. Gate C is the **visual-utility** half of that gate (SELECTION_GATE question 8), not a new model-selection doctrine.

**Live Gate-C sequence (do not invert):**

```text
two-clock C0         FAIL corpse  artifacts/gate_c0/     INVALID_TEMPORAL_EXECUTION
C0-v2                DONE         ON_SILICON_PIXEL_VALIDATED
cadence / latency    CLOSED       Captain 2026-08-31     do not reopen
transport contract   FROZEN_FOR_C1  5 Hz / 50 ms; joint 5 Hz+50 ms FAIL
C1 LGP               NEXT Gate-C action   OPEN           one full song Captain chooses
student I/O freeze   not yet      SELECTION_GATE + C1 if contract holds
```

| Stamp | Status | Authority |
| --- | --- | --- |
| Gate A (share vs mix) | PASS | `docs/mir/SELECTION_GATE.md` / P3-B |
| Gate B HOST (`source_share × Waveform Tempo × head_position`) | PASS | P3-C |
| Share-student recoverability | HOST PASS (21k, four-source including `other`) | `docs/mir/SHARE_STUDENT.md` |
| C0 two-clock silicon | **FAIL corpse** — do not rescore | `artifacts/gate_c0/C0_RESULT.json` |
| C0-v2 | **DONE** — `ON_SILICON_PIXEL_VALIDATED` | `artifacts/gate_c0v2/C0V2_RESULT.json` (Q1 0.83; Q2 Δ 0.69 9/9; Q3 Δ 0.58 9/9; `lag_corrected: false`) |
| Cadence silicon | **CLOSED** | D20; `docs/mir/GATE_C0_CADENCE.md` |
| C1 LGP | **OPEN — next Gate-C action** | D20; `docs/mir/GATE_C1.md` |
| Demucs on Titan | still **NO** | Amendment 001 + AGENTS.md |
| Demucs HOST teacher probe | **UNBLOCKED** (docs/licence; no download; do not block C1) | D22; `docs/agent/lanes/L35_demucs.md` |
| Titan / PDM / U55 board numbers | **UNBLOCKED for prep docs only.** PRE-SILICON. No invented board numbers | D22; `docs/TITAN_BRINGUP.md` |
| HOST streaming / I/O sketches | **UNBLOCKED** for sketches/tests. Not Titan. I/O unfrozen | D22; AGENTS.md |

C0-v2 scores are not C1. Dumps do not answer LGP. Captain is the C1 viewer. Product firmware (`k1_main_rpl_im69d` @ `acaecaa8`). No probe flash. No 8 s holdout. No USB multiplex.

Cadence envelope already measured (do not re-run):

```text
5 Hz @ 0 ms PASS (slowest useful 0-delay)
50 ms extra at 20 Hz PASS
100 ms at 20 Hz FAIL
200 ms at 20 Hz FAIL
5 Hz + 50 ms FAIL (keep; do not interpolate)
10 Hz + 25 ms NOT COMPLETED — do not interpolate
```

C1 playback uses the already-proven C0-v2 carrier (~31.25 Hz, 0 ms extra delay).

**What “HOST Demucs / Titan-prep unblocked” does *not* mean**

- Not a GO to `uv add demucs` or fetch HT-Demucs weights (code MIT; weights UNKNOWN / scientific-use — L35).
- Not permission to compile Demucs/MERT/MuQ/MAEST for U55.
- Not a student I/O freeze, not a product net, not a C1 substitute.
- Titan prep is golden-tensor-first documentation. Latency cells stay empty until an `ON-SILICON` board run.

**What it does mean**

HOST lanes may run **in parallel with C1**. C1 is the remaining Gate-C look. It is not a programme lock on registry, oracle, DEAM, PaRIRset, effect-semantics consume, RUHMI docs, share-student sketches, Demucs teacher **docs**, or Titan bring-up **docs**.

Dated `docs/agent/HANDOFF.md` snapshot `C0-v2 → cadence → C1 → only then student/deployment` is operator notes for the LGP look. **AGENTS.md + Amendment 001 + D22 win** on HOST sequence. Do not stop HOST Demucs/Titan-prep because C1 is still OPEN.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-30 | agent:edgeai | Created after Amendment 001. |
| 2026-08-31 | agent:edgeai | 0B compile is PRE-SILICON PASS, not “not run”. |
| 2026-08-31 | agent:grok | Sequence: C0-v2 done, cadence CLOSED, C1 next Gate-C; HOST Demucs/Titan-prep unblocked; model-selection authority unchanged. |
