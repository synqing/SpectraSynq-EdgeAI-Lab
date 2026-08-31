---
abstract: "L23: SHARE_STUDENT recoverability HOST PASS is the same closed fact as SELECTION_GATE (20788-param CNN, MUSDB18 n=50, other stays). I/O unfrozen. Do not freeze. Semantic-v0 is not this graph. SELECTION_GATE cadence/C0 wording stale vs D20. No USB."
---

# L23 — SHARE_STUDENT vs SELECTION_GATE

**HARD FAIL (`SAME_SONG_LOOP_MAX_15MIN`).** Docs-only. No USB. No song. Cadence CLOSED. Semantic-v0 is experiment, not architecture.

| Field | Value |
| --- | --- |
| STATUS | CONSISTENT on recoverability stamps. Two wording drifts in `SELECTION_GATE.md`. HOST-ONLY. I/O **UNFROZEN**. |
| CLAIM | Recoverability HOST PASS is one closed fact, not two experiments. SHARE_STUDENT owns the receipt; SELECTION_GATE cites it. Gate A PASS and Gate B HOST PASS live only in SELECTION_GATE. SHARE_STUDENT does not re-score lights and does not freeze I/O. Do not freeze student I/O. Semantic-v0 is a different (synthetic) graph. |
| EVIDENCE | `docs/mir/SHARE_STUDENT.md`; `docs/mir/SELECTION_GATE.md`; `docs/DECISIONS.md` D16–D17, D20, D22; `AGENTS.md` share-student row; `docs/agent/lanes/L06_share_io.md`; `docs/agent/lanes/L36_stream_sketch.md` |
| COMMAND | none. No train. No `share_student_feasibility.py`. No pytest. No `/dev/cu.usbmodem*`. No 8 s loop. |
| METHOD_RISK | Recoverability PASS ≠ Gate C. Rounded two-decimal table in SELECTION_GATE is not a second run. 16 kHz / 1 s / 64-mel is this net’s frontend, not RA8P1 I/O. Collapsing A/B/C + recoverability into one “share student PASS” would freeze the wrong thing. |
| NEXT | Do not train a product student. Keep `other`. Keep I/O unfrozen until C1. Optional later (not this lane): retarget SELECTION_GATE recoverability halt from “until Gate C measures cadence” to “until C1 / I/O freeze”; refresh SELECTION_GATE abstract C0/C1 line. |

## Same closed fact (recoverability)

Both files stamp **HOST PASS** that a tiny causal CNN recovers four-source **share** from mixture better than mix-energy, on official MUSDB18 **song-level** splits.

| Item | SHARE_STUDENT | SELECTION_GATE |
| --- | --- | --- |
| Stamp | PASS (feasibility / recoverability) | HOST PASS, 21k causal CNN; “feasibility question is closed” |
| Params | **20788**, 81.2 KiB fp32 | “20 788 params” in Evidence so far; “21k” in Recoverability |
| Split | official train 90 / val 10 (song-id carve) / **test 50**; window split banned | “official MUSDB18 song-level test n=50” |
| Sources | four-way simplex including **`other`** | “Four sources including **`other`**” |
| Headline r(pred,true) | vocals **0.637** drums **0.568** bass **0.537** | rounded **0.64 / 0.57 / 0.54** |
| Mix-linear r(pred,true) | **0.132 / 0.187 / 0.202** | rounded **0.13 / 0.19 / 0.20** |
| `other` | r=0.547 MAE=0.138; must stay; does not block Gate C | named in Recoverability; not in the three-source headline |
| I/O | **not frozen**; 16 kHz / 1 s / 64-mel is experiment frontend | “I/O remains unfrozen”; “Do not freeze Student-v0 yet” |
| composition_change | no ML head; share(t) vs share(t−Δ) | same: “function of share(t) vs share(t−Δ)” |
| Lights | did **not** re-score P3-C; Waveform Tempo binding is reference-only | Gate B table is the lighting stamp |

**[FACT]** Rounding is the same run: 0.637→0.64, 0.568→0.57, 0.537→0.54, 0.132→0.13, 0.187→0.19, 0.202→0.20.

**[FACT]** SHARE_STUDENT this-run `r(true, mix)` on **1 s** windows is 0.143 / 0.215 / 0.219. P3-B refs (vocals 0.17, drums 0.10, bass 0.16) are hop-512. SHARE_STUDENT forbids treating them as one number. SELECTION_GATE Gate A uses the P3-B hop figures; recoverability evidence uses mix-linear r(pred,true), not this-run r(true,mix). No contradiction if those clocks stay split.

## What SELECTION_GATE owns that SHARE_STUDENT does not

Never collapse these (SELECTION_GATE: “Three questions. Never collapse them.” Recoverability is a fourth engineering question.)

| Question | Stamp | In SHARE_STUDENT? |
| --- | --- | --- |
| Gate A — share vs mix energy (P3-B n=150) | **PASS**; abs DEMOTE | No. Cite P3-B r as hop refs only. |
| Gate B — `source_share × WaveformTempo × head_position` | **HOST PASS** (Δ partial r 0.63, 9/9) | Explicitly **not** re-scored. |
| Gate B — `composition_change × Comet × impact-launch` | **FAIL this comparator** | No ML event head; parked. |
| Gate C — physical K1 / LGP | **OPEN** (C1 remaining) | Halt until C “deserves a contract”; no C0/C1 scores. |
| Recoverability | HOST PASS | This file **is** the receipt. |
| Semantic-v0 synthetic r=0.99 | **not** Gate A | Different experiment. |

**[FACT]** AGENTS.md: do not freeze student I/O until `docs/mir/SELECTION_GATE.md` is satisfied. Nine criteria are still not all closed (descriptors, temporal rate, U55 of *this* net, C1 visual utility). Feasibility PASS is not that freeze.

**[FACT]** Semantic-v0 remains experiment/toolchain (L24 / `experiments/semantic_v0/AUTHORITY.md`). SHARE_STUDENT is mixture→four powers→share. Copying Semantic-v0 3-class sigmoid would drop `other` and swap share for abs-activity.

## Wording drifts (stamps still true)

1. **Cadence halt (live vs stale).** SHARE_STUDENT: do not build a hop-level/streaming student until Gate C **says the semantic deserves a contract**. SELECTION_GATE Recoverability: do not start a hop-level/streaming student until Gate C **measures the cadence/latency the binding actually needs**. Cadence silicon is **CLOSED** (D20): 5 Hz 0-delay PASS, 50 ms at 20 Hz PASS, joint 5+50 FAIL. Live halt is D17/D20/D22: no **product** streaming net until C1 / I/O freeze; HOST sketches **unblocked** (L36), not Titan. SELECTION_GATE “until C measures cadence” is **stale**. SHARE_STUDENT “until C deserves a contract” still matches D17 freeze-the-contract-after-C.

2. **SELECTION_GATE abstract vs body vs D20.** Abstract still reads `C0 FAIL INVALID_TEMPORAL_EXECUTION … C0-v2 next. C1 blocked.` Body Recoverability still treats cadence as future. Live programme: C0-v2 `ON_SILICON_PIXEL_VALIDATED`, cadence CLOSED, C1 OPEN, I/O unfrozen (D20; GATE_C0V2; L22 owns GATE_C.md body drift). Recoverability **numbers** are not stale.

Not a drift: Demucs not installed / not next. `commercial_training_lineage: false`. MUSDB18 STEMS research/NC. Teacher use ≠ derived-weight clearance.

## Do not freeze

Unfrozen (must stay): sample rate, 1 s window, stride, 64-mel / 100-frame, param count, causal-CNN topology, powers-then-normalise vs exported logits, windowed vs hop-level vs streaming graph, U55 of *this* net, Student-v0.

Not this lane’s freeze: C1 transport envelope (L06 / L36) is **FROZEN_FOR_C1** (5 Hz *or* 50 ms, never AND). That is not student I/O.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:grok | L23 contract: share recoverability vs selection gate; cadence-halt drift. |
| 2026-08-31 | agent:grok | Re-derive: rounding table, A/B/C split, Semantic-v0 not this graph, SELECTION_GATE abstract C0/C1 stale vs D20. |
