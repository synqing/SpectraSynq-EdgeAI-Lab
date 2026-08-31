---
abstract: "L06: student I/O UNFROZEN until SELECTION_GATE; C1 transport FROZEN; streaming student STOPPED. Docs-only. No USB."
---

# L06 — share-student I/O unfrozen vs C1 transport frozen

**HARD FAIL (`SAME_SONG_LOOP_MAX_15MIN`).** Same song/clip looped >15 min → agent dies. Cadence CLOSED. No USB. No 8 s loop.

**STATUS:** student I/O **UNFROZEN**. Semantic transport **FROZEN_FOR_C1**. Streaming student **STOPPED**. `SELECTION_GATE.md` **not satisfied** (C OPEN). HOST-ONLY recoverability PASS is not an RA8P1 lock.

**CLAIM:** Do not freeze Student-v0 I/O until `docs/mir/SELECTION_GATE.md` is satisfied. Gate A PASS and Gate B HOST PASS on one binding do not freeze the 21k CNN’s 16 kHz / 1 s / 64-mel / 100-frame graph. C1 may consume four-source `extra_gain` on the already-proven C0-v2 carrier. A later product student must meet the transport **edges**, never AND 5 Hz with 50 ms. HOST I/O sketches (L36) may exist on paper; they do not start a hop-level or streaming net.

## Gate (why I/O cannot freeze)

| Gate | Stamp | Freeze licence? |
| --- | --- | --- |
| A semantic information | PASS (`source_share` vs mix) | no |
| B visual-carrier | HOST PASS **only** `source_share × WaveformTempo × head_position` | no |
| C product / LGP | OPEN. C0-v2 `ON_SILICON_PIXEL_VALIDATED`. Cadence CLOSED. C1 LGP **not** `LGP_PERCEPTUAL_VALIDATED` | no |

Nine SELECTION_GATE recoverability items still unfrozen: which descriptors; temporal rate/context; real-audio incremental vs DSP (partial evidence only); oracle/teacher quality; CLEAN/STUDIO; live/venue; licensing; visual utility C; U55 compressibility of **this** student (smoke/ad01 C99 is not this graph).

D20/D22: freeze student I/O **after C1 if the contract still holds** — not this receipt.

## Frozen for C1 — transport, not a net

From `docs/mir/SEMANTIC_TRANSPORT_CONTRACT.md` + `artifacts/gate_c0_cadence_silicon/SEMANTIC_TRANSPORT_CONTRACT.json` (`status`: `FROZEN_FOR_C1`). Oracle on silicon was MUSDB four-source share → `extra_gain`, **not** the 21k net.

| Item | Frozen value |
| --- | --- |
| Channels + order | `vocals, drums, bass, other` (`other` stays; simplex is four-way) |
| Share | simplex over those four |
| Silence | no invented equal shares (zeros, not 1/4) |
| Numeric range on the lever | `extra_gain` ∈ [0.62, 1.0] |
| Hold | ZOH / sample-and-hold; no interpolation; lookahead = 0 |
| Device hop | `hop_us` = 32000 (32 ms grid); delay = `round(delay_s/0.032)` hops |
| Slowest 0-delay PASS | **5 Hz** (`r5_d0`) |
| Largest added-delay PASS | **50 ms** requested at **20 Hz** (`r20_d50`; actual 64 ms = 2 hops) |
| Joint | **5 Hz + 50 ms FAIL** (`r5_d50` Q1). `student_must_not_assume` both edges |
| 100 ms at 20 Hz | FAIL (Q1) |
| 10 Hz + 25 ms | **not** a cell; aborted; do not interpolate |
| C1 playback | C0-v2 carrier, **~31.25 Hz, 0 ms extra delay**, product firmware |
| Packet clock ≠ emit clock | authored `hz` 30–240; ZOH-repeat on the wire. Do not put `hz=5` on the wire |
| Cadence silicon | **CLOSED** — no more rate/delay cells |

C1 playback is **not** a student envelope. Binding stays `source_share × Waveform Tempo × head_position`.

## Unfrozen — student I/O (experiment, not product)

The 21k feasibility net (`docs/mir/SHARE_STUDENT.md`, ~20788 params, 81.2 KiB fp32):

| Item | Experiment value (not a lock) |
| --- | --- |
| Sample rate | 16 kHz |
| Window / hop | 1 s / 1 s |
| Frontend | 64-mel, 100-frame log-mel |
| Pool | `AdaptiveAvgPool2d((1,1))` → ~1 s latency / ~1 Hz — **misses both transport edges** |
| Topology | causal depthwise-separable CNN; param count; dropout |
| Tensor layout | unfrozen |
| Head | 4 softplus powers then deterministic share (vs exported logits) |
| Graph class | windowed vs hop-level vs streaming |
| U55 / RUHMI of this net | not compiled; smoke/ad01 C99 is a different graph |
| Titan / PDM | not this student |

Also unfrozen (selection, not transport):

- which descriptors become Student-v0
- composition_change as ML head (**parked**; still a function of `share(t)` vs `share(t−Δ)`)
- Semantic-v0 3-class sigmoid activity (drops `other`; abs-activity, not share)
- Demucs teacher; extra nets
- HOST cadence numbers (20 Hz floor; 50 ms FAIL) — design evidence only, L33; not this contract

JSON `unfrozen` list is **thin** (`neural-network architecture`, `C1 LGP judgement`). Canonical unfrozen set is SHARE_STUDENT + SELECTION_GATE, not that two-line array.

## Streaming student — STOPPED

| Allowed now | Stopped |
| --- | --- |
| Docs / HOST I/O **sketches** from transport edges (L36: exclusive envelope R=`r5_d0` **or** D=`r20_d50`, never AND) | Train, fit, goldens, hop-level product student |
| Keep `other` in receipts/MAE | Gold-plate the 21k 1 s pool as RA8P1 I/O |
| C1 LGP look on proven carrier | U55 compile of a streaming student; Titan; PDM |

D17 / SHARE_STUDENT / GATE_C parked list: do not build hop-level or streaming student until Gate C says the semantic deserves a contract **and** SELECTION_GATE is satisfied. D22 unblocks HOST sketches, not Titan and not a freeze.

**EVIDENCE:** `docs/mir/SELECTION_GATE.md`; `docs/mir/SHARE_STUDENT.md`; `docs/mir/GATE_C.md`; `docs/mir/GATE_C1.md`; `docs/mir/SEMANTIC_TRANSPORT_CONTRACT.md`; `artifacts/gate_c0_cadence_silicon/SEMANTIC_TRANSPORT_CONTRACT.json`; `CADENCE_RESULT.json`; `docs/DECISIONS.md` D17/D20/D22; `AGENTS.md` (I/O unfrozen; streaming unblocked for HOST sketches only); `docs/agent/HANDOFF.md` (streaming STOPPED; I/O freeze NOT YET); L04 joint FAIL; L05 `other`; L36 sketch.

**COMMAND:** none executed. Docs + JSON read only. No USB, no `/dev/cu.usbmodem*`, no flash, no ffplay, no 8 s loop, no train.

**METHOD_RISK:** Freezing the 1 s / `AdaptiveAvgPool2d((1,1))` frontend would miss the 5 Hz floor and the joint-fail. AND-ing 5 Hz with 50 ms rebuilds `r5_d50` Q1 FAIL. Copying Semantic-v0 I/O drops `other` and swaps share for abs-activity. Treating C1’s ~31.25 Hz / 0 ms playback as the student contract freezes the renderer clock, which D17 rejected. JSON `unfrozen` omitting frontend/rate would hide an illegal freeze.

**NEXT:** Keep I/O open. Do not start a streaming student. C1 LGP (`GATE_C1.md`) is the remaining human look on the proven carrier. Freeze I/O only after SELECTION_GATE + C1 if the transport still holds. L36 may HOST-sketch from exclusive envelopes; this lane does not implement it.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:grok | L06 10-line I/O-unfrozen vs transport-frozen contract. |
| 2026-08-31 | agent:grok | Checklist: unfrozen I/O vs C1-frozen transport; streaming STOPPED; SELECTION_GATE not satisfied. |
