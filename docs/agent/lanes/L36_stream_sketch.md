---
abstract: "L36 HOST sketch. Exclusive envelopes R=5 Hz/0 ms and D=20 Hz/50 ms; never AND. Four-source simplex → extra_gain [0.62,1.0] ZOH. Ban 1 s global pool. I/O unfrozen. No train."
---

# L36 — HOST streaming-student sketch from frozen transport

**HARD FAIL (`SAME_SONG_LOOP_MAX_15MIN`).** Same song/clip looped >15 min → agent dies. Cadence silicon **CLOSED**. No USB. No train. No U55. No Titan. Docs + HOST JSON only.

This is a **HOST-ONLY paper sketch**. It does not freeze student I/O. It does not compile a net. Silicon numbers below are **ON-SILICON** receipts already on disk; the sketch itself is not ON-SILICON.

## STATUS

HOST sketch only. Student I/O **UNFROZEN** (`CADENCE_RESULT.json` `student_freeze: false`; `SELECTION_GATE` not satisfied). Transport **FROZEN_FOR_C1**. Cadence **CLOSED**. No weights, no fit, no USB, no U55.

## CLAIM

Sketch the streaming I/O from the silicon **transport edges**, not from the 21k 16 kHz / 1 s / 64-mel graph.

- Pick **one** envelope. **Never AND 5 Hz with 50 ms.** Joint cell `r5_d50` is Q1 FAIL (`family=corner`, not interpolated; 10 Hz+25 ms aborted).
- **R** = 5 Hz, 0 extra delay. **D** = 20 Hz, 50 ms requested (64 ms = 2 hops). Enum, not a union.
- Output is four-source simplex (`vocals, drums, bass, other`) then `extra_gain` ∈ [0.62, 1.0], ZOH, lookahead 0.
- Ban a **1 s global pool** as the streaming frontend: that graph is ~1 Hz / ~1 s latency and misses both edges.
- 16 kHz / mel bins / tensor layout stay unlocked.

## EVIDENCE

Re-derived 2026-08-31 from on-disk JSON + source (not from wave-1 L36 prose).

| Source | What it locks for this sketch |
| --- | --- |
| `docs/mir/SEMANTIC_TRANSPORT_CONTRACT.md` + `artifacts/gate_c0_cadence_silicon/SEMANTIC_TRANSPORT_CONTRACT.json` | `status=FROZEN_FOR_C1`; channels/order; `extra_gain [0.62, 1.0]`; simplex; `combined_5hz_50ms=FAIL`; `student_must_not_assume`; hold policy; `lookahead=0`; C1 playback 31.25 Hz / 0 ms |
| `artifacts/gate_c0_cadence_silicon/CADENCE_RESULT.json` | `gate_c0_cadence=CLOSED`; `student_freeze=false`; `plain.minimum_demonstrated_useful_rate_hz=5`; `maximum_demonstrated_added_delay_s=0.05`; `combined_10hz_25ms=NOT_COMPLETED`; `tighten_complete=false` |
| `cells/r5_d0.json` | **R** silicon: 5 Hz, 0 hops, Q1 0.414 PASS, Q2 Δ 0.530 8/9, Q3 Δ 0.438 9/9 |
| `cells/r20_d50.json` | **D** silicon: 20 Hz, 50 ms req → 64 ms / 2 hops, Q1 0.402 PASS, Q2 Δ 0.420 8/9, Q3 Δ 0.355 8/9 |
| `cells/r5_d50.json` | **AND banned**: 5 Hz + 50 ms req (64 ms / 2 hops), Q1 0.245 FAIL (< 0.40); Q2/Q3 still PASS. Joint death is Q1. |
| `cells/r20_d100.json` | 100 ms at 20 Hz FAIL (Q1 0.368); actual 96 ms = 3 hops. Not an envelope. |
| L04 | must-not-assume; 10 Hz+25 ms not interpolated |
| L06 | I/O unfrozen vs transport frozen; HOST sketches allowed, product student stopped |
| L14 | AdaptiveAvgPool2d is the D11 U55 **op**. The **1 s time window** is a streaming-latency ban here, not an op ban. |
| L33 | HOST 20 Hz floor / 50 ms FAIL-at-31.25 Hz is **not** this contract |
| `src/edgeai/mir/gate_c_cadence.py` | `HOP=512`, `SR=16000`, `HOP_S=0.032`; `zero_order_hold` then `causal_delay`; `GAIN_LO=0.62`, `GAIN_HI=1.0` |
| `src/edgeai/mir/host_chroma.py` `extra_gain` | `clip(x,0,1)` then `0.62 + 0.38·x` |
| `src/edgeai/mir/source_oracle.py` | `SOURCES = ("vocals", "drums", "bass", "other")`; silence → zeros not 1/4 (`total < 1e-10`) |
| `src/edgeai/share_student.py` | 21k experiment: `AdaptiveAvgPool2d((1, 1))` over 1 s log-mel. I/O not a lock. |
| `docs/mir/SHARE_STUDENT.md` | HOST recoverability PASS; 1 s / 1 s hop; stop hop-level product student until Gate C |
| `docs/DECISIONS.md` D11 / D17 / D20 / D22 | AdaptiveAvgPool export; PRE-PRODUCT PASS; cadence closed 5/50/joint; HOST sketches unblocked |
| `docs/mir/GATE_C0_SILICON_PATH.md` §6 | Packet clock ≠ emit clock; do not put `hz=5` on the wire; authored `hz` 30–240 |

`cells/r10_d25.json` does **not** exist (only a partial). Do not fill it.

## COMMAND

HOST JSON + hop math only. No pytest train, no USB, no `/dev/cu.usbmodem*`, no 8 s loop, no ffplay, no U55.

```text
python3 -c "import json,pathlib; root=pathlib.Path('artifacts/gate_c0_cadence_silicon'); p=root/'cells';
keys=('family','rate_hz','delay_s','actual_delay_ms','actual_delay_hops','verdict','Q1','median_spearman_pos_gain');
[print(n,{k:json.loads((p/n).read_text())[k] for k in keys}) for n in ('r5_d0.json','r20_d50.json','r5_d50.json','r20_d100.json')];
c=json.loads((root/'CADENCE_RESULT.json').read_text()); t=json.loads((root/'SEMANTIC_TRANSPORT_CONTRACT.json').read_text());
print('student_freeze',c['student_freeze'],'cadence',c['gate_c0_cadence']);
print('plain',{k:c['plain'][k] for k in ('minimum_demonstrated_useful_rate_hz','maximum_demonstrated_added_delay_s','combined_5hz_50ms','combined_10hz_25ms')});
print('must_not',t['student_must_not_assume']); print('HOP_S',512/16000,'d50_hops',round(0.05/(512/16000)),'g0',0.62,'g1',1.0);
print('r10_d25.json',(p/'r10_d25.json').exists())"
```

Ran this SSA. Witness: R PASS 5 Hz/0 hops Q1=0.414; D PASS 20 Hz/2 hops/64 ms Q1=0.402; AND FAIL Q1=0.245; 100 ms FAIL Q1=0.368; `student_freeze=false`; `combined_5hz_50ms=FAIL`; `r10_d25.json` absent; `HOP_S=0.032`; extra_gain(0)=0.62, extra_gain(1)=1.0.

## METHOD_RISK

- **Student receptive-field latency is not silicon `actual_delay_ms`.** A 200 ms window called “5 Hz PASS” plus 50 ms extra delay rebuilds `r5_d50` Q1 FAIL. Extra delay in the contract is *after* the sample exists (`causal_delay` on the held series), not the CNN’s look-back.
- **50 ms requested ≠ 50 ms actual.** `round(0.05/0.032)=2` hops = **64 ms**. 100 ms requested = 3 hops = **96 ms**. Quote both.
- **Authored freshness 50 ms ≠ silicon added delay 50 ms.** Wire drop-cut is satisfied by **packet repeat** at ≥ 30 Hz, not by slowing the net. Do not put `hz=5` on the wire.
- **HOST cadence is not this contract (L33).** Host 20 Hz floor and host 50 ms FAIL were at native 31.25 Hz. Silicon D envelope is 50 ms PASS **at 20 Hz**.
- **S2 is HOST-HYPOTHESIS.** Silicon 5 Hz PASS held a **native-hop** oracle then ZOH. A net whose hop is 200 ms is not that PASS.
- **AdaptiveAvgPool2d vs 1 s pool.** D11 requires AdaptiveAvgPool2d (not `ReduceMean`) for U55 export. L36 bans pooling a **1 s global time window** as the streaming output. A short-context pool that still meets the chosen envelope is unfrozen architecture, not this ban.
- **`extra_gain` is a scalar lever**, not the 4-vector. P3-C maps one share series (`p3b-v1` 5th–95th) then `extra_gain`. Which share drives the knob is a binding choice (`_share_key`); it is not a student-I/O freeze.
- **JSON `unfrozen` is thin.** Canonical unfrozen set is SHARE_STUDENT + SELECTION_GATE, not the two-line array on the contract JSON.
- **C1 playback is not a student envelope.** ~31.25 Hz / 0 ms is the already-proven C0-v2 carrier. D17 forbids freezing 31.25 Hz because a renderer used it.
- Cadence JSON `contract.status` is still `PROPOSED`; the **MD + `SEMANTIC_TRANSPORT_CONTRACT.json`** are `FROZEN_FOR_C1` (L03 owns that split). This sketch consumes the frozen MD/JSON.

## NEXT

Keep I/O open. Do not train. Do not compile this for U55. Do not reopen cadence cells.

Ship path (this sketch is not a freeze and not a product student):

1. **Already in source / on silicon:** transport frozen; C0-v2 `ON_SILICON_PIXEL_VALIDATED`; cadence CLOSED; this HOST sketch.
2. **Remaining:** Captain C1 LGP look on one full song he chooses (no 8 s loop) → if PASS, stamp `LGP_PERCEPTUAL_VALIDATED` → freeze student I/O **only if** this contract still holds → then a HOST numpy S1 ZOH (no fit) may exist as a test, not a net.
3. **Who acts:** Captain for C1 look. Later HOST SSA for the numpy hold. Nobody flashes or trains from L36.
4. **Stamp that means shipped:** `LGP_PERCEPTUAL_VALIDATED` then an explicit I/O freeze. This file is neither.

---

## Sketch (HOST-ONLY, I/O unfrozen)

Three clocks. Do not collapse them.

| Clock | Period | Owner | Notes |
| --- | ---: | --- | --- |
| Device hop (scoring grid) | **32 ms** (`hop_us=32000`, 512/16000) | silicon hold policy | Native oracle lived here. C1 carrier ~31.25 Hz is this grid at 0 extra delay. |
| Semantic emit | **R 200 ms** or **D 50 ms** | this sketch, pick one | ZOH onto the 32 ms grid. Never 5 Hz **and** 50 ms extra delay. |
| Packet / authored | **≥ 30 Hz**, `hz` field **30–240** | PRSM wire | Repeat the held `extra_gain`. Freshness 50 ms is this clock, not envelope D. |

### Exclusive envelopes (enum, not a union)

Pick **R XOR D**. Illegal to take R’s rate and D’s delay.

| Env | Emit | Extra delay | Silicon cell | Q1 Spearman | Verdict |
| --- | --- | --- | --- | ---: | --- |
| **R** | ≥ **5 Hz** (200 ms, 6.25 hops) | **0 hops / 0 ms** | `r5_d0` `family=rate` | 0.414 | **PASS** |
| **D** | ≥ **20 Hz** (50 ms, 1.5625 hops) | **50 ms requested = 64 ms = 2 hops** | `r20_d50` `family=delay` | 0.402 | **PASS** |
| **AND — banned** | 5 Hz | 50 ms req / 64 ms | `r5_d50` `family=corner` | 0.245 | **FAIL (Q1)** |
| not an envelope | 20 Hz | 100 ms req / 96 ms / 3 hops | `r20_d100` | 0.368 | FAIL (Q1) |
| not an envelope | ~31.25 Hz | 0 ms | C0-v2 / C1 playback | 0.83 | proven **carrier**, not a student contract |

Hold: `apply_cadence = zero_order_hold(rate_hz) then causal_delay(round(delay_s/0.032) hops)` with first-sample freeze on the pad. No interpolation. `lag_corrected=false`. Lookahead = 0.

100 ms at 20 Hz FAIL. Do not interpolate 10 Hz+25 ms.

### Pipeline

```text
mixture PCM                    # rate UNFROZEN (16 kHz is experiment, not a lock)
  → causal frontend            # window/hop UNFROZEN; BAN 1 s global pool
  → causal student             # architecture UNFROZEN; 4 non-negative powers (softplus or equivalent)
  → shares_from_powers         # simplex; silence (total ≤ 1e-10) → zeros, not 1/4
  → [optional] p3b-v1 map      # 5th–95th of one share series → frozen 0–1; binding, not I/O freeze
  → extra_gain                 # g = 0.62 + 0.38 * clip(x, 0, 1)  ∈ [0.62, 1.0]
  → envelope R XOR D           # ZOH then causal delay; never AND
  → packet repeater            # ZOH-repeat extra_gain at ≥ 30 Hz; hz 30–240; do not put hz=5 on the wire
```

Two input sketches, both HOST, both unfrozen:

| Id | What the net emits | Status |
| --- | --- | --- |
| **S1** | Causal net on the **32 ms** hop grid. ZOH+delay is a **later** stage that then chooses R *or* D. | Matches how silicon was scored (native-hop oracle, then hold). |
| **S2** | Net hop equals the chosen emit period (200 ms for R, 50 ms for D). | **HOST-HYPOTHESIS / cheaper.** Not the silicon 5 Hz PASS. |

A later HOST test may implement S1 ZOH as `apply_cadence` / `extra_gain_cadence` on an existing four-source oracle (numpy hold, **no fit**). That test is not this file and is not a student freeze.

### Output (transport-bound, not a net freeze)

| Item | Value |
| --- | --- |
| Vector | 4-share, order `vocals, drums, bass, other` |
| Simplex | non-negative, sums to 1 when not silent |
| Silence | all zeros; **never** invent 0.25/0.25/0.25/0.25 |
| Lever | `extra_gain` ∈ **[0.62, 1.0]** after the frozen 0–1 map |
| Hold | ZOH / sample-and-hold; no interpolation; lookahead 0 |
| `other` | stays. Dropping it is a three-source student (L05). |

Semantic-v0 3-class sigmoid (`vocals, drums, bass` activity) is a different experiment. Do not copy it here.

### Ban: 1 s global pool

The 21k recoverability net pools the **whole 1 s / 100-frame log-mel** with `AdaptiveAvgPool2d((1, 1))`, hop 1 s. That is ~**1 Hz** emit and ~**1 s** latency.

| Edge | Why 1 s global pool misses it |
| --- | --- |
| R (≥ 5 Hz, 0 extra delay) | 1 Hz is slower than 5 Hz. |
| D (≤ 64 ms extra delay after the sample exists) | 1 s receptive-field latency already exceeds 50 ms, 64 ms, and the 100 ms FAIL cliff. |

**Banned as a streaming frontend.** Not a freeze of AdaptiveAvgPool2d as a U55 op (D11 / L14: export CNN GlobalAveragePool, not `ReduceMean`, not STFT-in-graph). A causal pool over a **short** context that still meets the chosen envelope is allowed on paper and still **unfrozen**.

### Unfrozen (do not lock from this sketch)

Sample rate, n_mels, n_frames, tensor layout, CNN width/depth, dropout, log-mel vs other frontend, S1 vs S2, which share series drives `extra_gain`, composition_change as ML head (parked; still a function of `share(t)` vs `share(t−Δ)`), U55 of this graph, Titan, PDM.

Freeze only after `docs/mir/SELECTION_GATE.md` **and** C1, and only if this transport still holds (D20/D22).

### Not this

- Train, goldens, hop-level product student, U55 compile of this sketch, Titan, PDM.
- Gold-plate the 21k 1 s pool as RA8P1 I/O.
- Copy Semantic-v0 3-class sigmoid (drops `other`; abs-activity not share).
- Treat authored 50 ms freshness as envelope D.
- Fill 10 Hz+25 ms.
- AND 5 Hz with 50 ms.
- Put `hz=5` on the PRSM wire.
- Reopen cadence cells or loop the 8 s holdout.
- Call C1’s ~31.25 Hz / 0 ms playback the student envelope.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:grok | L36 HOST streaming I/O sketch: exclusive 5 Hz / 50 ms envelopes; S1 vs S2; no train. |
| 2026-08-31 | agent:grok | Wave 2: re-derived cells + hop math; three clocks; 1 s pool ban vs D11 op; extra_gain formula; ship path. |
