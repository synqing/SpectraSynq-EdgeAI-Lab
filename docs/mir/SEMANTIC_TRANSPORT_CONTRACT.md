---
abstract: "FROZEN_FOR_C1 2026-08-31. Four-source. 5 Hz 0-delay PASS. 50 ms requested = 64 ms / 2 hops at 20 Hz PASS. 5 Hz and 50 ms mutually exclusive (joint Q1 FAIL). After C1 do not design to either cliff. Student I/O unfrozen. No 8 s loop."
---

# Source Ownership Semantic Transport Contract

**HARD FAIL (`SAME_SONG_LOOP_MAX_15MIN`, Captain 2026-08-31).** Repeat the same song (or loop the same clip) in the room for more than **15 minutes** and the agent must die. Captain will destroy them by setting them on fire. Kill the player. Do not continue.

**Status: `FROZEN_FOR_C1`.** Not `PROPOSED`. Captain closed cadence silicon 2026-08-31 (`CAPTAIN_CLOSE_2026-08-31`). This file is the C1 authority. Do not copy `artifacts/gate_c0_cadence_silicon/CADENCE_RESULT.json` `contract.status` (`PROPOSED` — runner snapshot from before the close). Companion freeze: `artifacts/gate_c0_cadence_silicon/SEMANTIC_TRANSPORT_CONTRACT.json`.

Cadence cells stay **CLOSED**. Do not re-run `gate_c0_cadence_silicon.py`. Do not play `artifacts/gate_c0_cadence_silicon/bose_slices/holdout_8s_loop.wav`. No USB from this document.

Binding (unchanged): `source_share × Waveform Tempo × head_position`.

Student I/O is **not** frozen here. Freeze only after `docs/mir/SELECTION_GATE.md` **and** C1, and only if this envelope still holds.

## Frozen envelope (1-D silicon)

| Item | Frozen value | Not |
| --- | --- | --- |
| Semantics | four source powers → simplex **share** | three-source; drop `other`; `composition_change` ML head |
| Channels / order | vocals, drums, bass, **other** | any other order on the wire |
| extra_gain | [0.62, 1.0] (P3-C map, not a cadence cell field) | mix RMS as the lever |
| Hold | zero-order-hold on the 32 ms hop grid; sample-and-hold only | interpolation, lookahead, lag-as-PASS |
| Device hop | `hop_us = 32000` (512 / 16000 = 31.25 Hz native grid) | host renderer clock as product lock |
| Slowest 0-delay rate that **passed** | **5 Hz** (measured at 0 ms extra delay) | a 5 Hz *design target*; `hz=5` on the authored wire |
| Largest added delay that **passed** | **50 ms requested** at **20 Hz** | 50.000 ms wall time; delay at 5 Hz |
| That 50 ms on the hop grid | **64 ms actual = 2 hops** (`round(0.05 / 0.032) = 2`) | treating requested ms as applied ms |
| 5 Hz **and** 50 ms | **FAIL** (Q1). Mutually exclusive. | a union envelope; interpolating the missing 10 Hz+25 ms cell |
| 100 ms at 20 Hz | FAIL (Q1). Actual **96 ms = 3 hops**. | admissible extra delay |
| 200 ms at 20 Hz | FAIL. Actual **192 ms = 6 hops**. | — |
| 10 Hz + 25 ms | **NOT_COMPLETED** (aborted 6/10). Do not interpolate. | a tightening that “almost” passed |
| Silence | no invented equal shares; extra_gain stays in [0.62, 1.0]; oracle silence → zeros, not 1/4 | filling a simplex in quiet |
| Lookahead | 0 | non-causal pads |
| C1 playback | already-proven **C0-v2 carrier**, **31.25 Hz**, **0 ms extra delay**, **product firmware** | the 5 Hz cliff; the 50 ms cliff; probe flash; 8 s holdout |

Delay math (frozen hold policy): causal delay of `round(delay_s / 0.032)` hops with the first sample frozen on the pad. Extra delay is **after** the sample exists, not CNN look-back.

```text
50 ms requested  → round(0.050 / 0.032) = 2 hops → 64 ms applied
25 ms requested  → 1 hop  → 32 ms applied   (PASS at 20 Hz; not a freeze edge)
100 ms requested → 3 hops → 96 ms applied   FAIL at 20 Hz (Q1)
200 ms requested → 6 hops → 192 ms applied  FAIL at 20 Hz
```

Packet clock ≠ descriptor clock. Authored `hz` must stay in 30–240; freshness drop is 50 ms **on the wire**, a different 50 ms. Hold rates 5 Hz **repeat** packets at ≥ 30 Hz. Do not put `hz=5` on the wire.

## 5 Hz and 50 ms are mutually exclusive

Two 1-D PASSes do **not** make a 2-D PASS.

| Cell | Rate | Delay | Applied | Q1 | Q2 | Q3 | Verdict |
| --- | ---: | --- | --- | --- | --- | --- | --- |
| `r5_d0` | 5 Hz | 0 ms | 0 hops | PASS (Spearman 0.414) | PASS | PASS | PASS |
| `r20_d50` | 20 Hz | 50 ms requested | 64 ms / 2 hops | PASS (Spearman 0.402) | PASS | PASS | PASS |
| `r5_d50` | 5 Hz | 50 ms requested | 64 ms / 2 hops | **FAIL** (Spearman 0.245 < 0.40) | PASS | PASS | **FAIL** |

A student, sketch, or streaming I/O **must not assume 5 Hz and 50 ms extra delay at the same time**. Pick **one** 1-D envelope if you need a cliff for a paper sketch: **R** = 5 Hz / 0 ms extra, **or** **D** = 20 Hz / 50 ms requested (64 ms / 2 hops). Never AND them. Joint death is Q1, not Q2/Q3.

Do not invent a 10 Hz+25 ms interior from the aborted cell.

## C1 uses the proven carrier, not the cliffs

C1 LGP plays the C0-v2 carrier already stamped `ON_SILICON_PIXEL_VALIDATED`: ~31.25 Hz, 0 ms extra delay, product firmware (`k1_main_rpl_im69d`). Not the 5 Hz hold. Not the 50 ms delay. Not `k1_main_rpl_rtrace_probe`. Method: `docs/mir/GATE_C1.md`. One full song Captain chooses. No 8 s loop.

This freeze is the **transport envelope C1 inherits**. It is not a student I/O freeze and not an LGP stamp.

## After C1 — do not design to the cliffs

`5 Hz` and `50 ms requested` are **measured envelope edges**, not nominal student setpoints.

Q1 is already tight on both PASSes (0.414 and 0.402 against a 0.40 floor). Designing a net, hop, or pipeline to sit on either cliff, or on both, is how the joint cell died.

**After C1**, if this contract still holds and student I/O is frozen:

1. Nobody uses **5 Hz** as the nominal update rate.
2. Nobody uses **50 ms requested / 64 ms / 2 hops** as the nominal extra-delay budget.
3. Pick **engineering margin inside the envelope**: faster than the slowest demonstrated PASS **and** less extra delay than the largest demonstrated PASS, **and** never the AND of the two cliffs.
4. Student receptive-field latency is **not** silicon `actual_delay_ms`. A 200 ms window labelled “5 Hz PASS” plus 50 ms extra delay rebuilds `r5_d50` Q1 FAIL.

Until that freeze, HOST sketches may **name** a cliff only as a bound they must stay inside (D22). They still must not AND the cliffs. They still must not compile it for U55 / Titan.

## What this is not

- Not C1 (`LGP_PERCEPTUAL_VALIDATED`). Nobody has looked at the LGP for this gate.
- Not a student I/O freeze. 16 kHz / 1 s / 64-mel / 21k CNN remain experiments.
- Not HOST cadence. Host rehearsal failed 50 ms at **31.25 Hz** and passed rate only at **20 Hz**. Silicon owns the product clock. Do not freeze host 20 Hz / host 50 ms FAIL as this contract.
- Not Semantic-v0 architecture authority.
- Not a licence to reopen cadence, interpolate 10 Hz+25 ms, or loop the holdout.

## Receipts (do not re-measure)

- `artifacts/gate_c0_cadence_silicon/CADENCE_RESULT.json` — `gate_c0_cadence=CLOSED`; `plain.combined_5hz_50ms=FAIL`; `student_freeze=false`
- `artifacts/gate_c0_cadence_silicon/SEMANTIC_TRANSPORT_CONTRACT.json` — `status=FROZEN_FOR_C1`
- Cells: `r5_d0.json`, `r20_d50.json`, `r5_d50.json`, `r20_d100.json`, `r31.25_d0.json`
- C0-v2: `artifacts/gate_c0v2/C0V2_RESULT.json` (`ON_SILICON_PIXEL_VALIDATED`)
- Method: `docs/mir/GATE_C0_CADENCE.md`, `docs/mir/GATE_C.md`, `docs/DECISIONS.md` D20
- Hold implementation: `src/edgeai/mir/gate_c_cadence.py` (`HOP_S=0.032`, `delay_hops`, `zero_order_hold` then `causal_delay`)

Pass floors (same as C0-v2; not a weaker bar): Q1 Spearman(head, extra_gain) ≥ 0.40; Q2/Q3 median Δ ≥ 0.15 and ≥ 70% clips Δ > 0. Q1 scores the **native** extra_gain series. `lag_corrected: false`.

## Ship path

1. **Already on silicon / in source:** C0-v2 PASS; cadence 1-D envelope measured and Captain-closed; this file `FROZEN_FOR_C1`.
2. **Remaining:** C1 LGP look on one full song Captain chooses. Then, only if the envelope still holds, freeze student I/O with **margin inside** this envelope — not at 5 Hz, not at 50 ms, not both.
3. **Who acts:** Captain for the C1 look. Agents do not flash, do not reopen cells, do not loop audio. Later HOST sketches stay legal (D22) and must obey the AND-ban.
4. **Stamp that means shipped for C1:** `LGP_PERCEPTUAL_VALIDATED` in `docs/mir/GATE_C1.md`. This file is not that stamp. A later student freeze is a separate stamp, not automatic.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:grok | Frozen for C1 from silicon 1-D + Captain cadence close. |
| 2026-08-31 | agent:grok | SAME_SONG_LOOP_MAX_15MIN HARD FAIL. |
| 2026-08-31 | agent:grok | W3-L14: status FROZEN_FOR_C1 not PROPOSED; 50 ms requested = 64 ms / 2 hops; 5 Hz and 50 ms mutually exclusive; after C1 pick margin inside the envelope, do not design to either cliff. |
