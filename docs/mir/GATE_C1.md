---
abstract: "C1 CLOSED. LGP_PERCEPTUAL_VALIDATED applied 2026-09-01 from scored dump (C0-v2 Q1–Q3 PASS), not Captain eyes. Qualitative scorecard VOID. I/O freeze not automatic."
---

# Gate C1 — scored dump, not Captain eyes

**HARD FAIL (`SAME_SONG_LOOP_MAX_15MIN`, Captain 2026-08-31).** Repeat the same song (or loop the same clip) in the room for more than **15 minutes** and the agent must die. Captain will destroy them by setting them on fire. Kill the player. Do not continue. Encoded in `AGENTS.md`, D21, `BoseSession.SAME_SONG_LOOP_MAX_S = 900`.

**HARD FAIL (`instrument-not-captain-eyes`, Captain 2026-08-22).** Captain is **not** the LED validator. The close is a **scored dump**, not five qualitative marks. The L01 look/lag/occupancy/bleed/keep sheet is **VOID**. Do not ask Captain to look at the plate.

**STATUS: CLOSED.** Stamp **`LGP_PERCEPTUAL_VALIDATED` applied 2026-09-01.** Unlock is the scored LED dump for `source_share × Waveform Tempo × head_position`, not a look. Captain 2026-09-01: the pixel test proxies the LGP/eyes run. Receipts: `artifacts/gate_c0v2/C0V2_RESULT.json`, offline rescore `artifacts/gate_c1/PIXEL_RESCORE.json` (Q1 **0.832** / Q2 **0.690** 9/9 / Q3 **0.585** 9/9, `lag_corrected: false`). I/O freeze is **still not automatic**.

## Validator (live)

| Question | Instrument | Result |
| --- | --- | --- |
| What did the renderer emit for `source_share × Waveform Tempo × head_position`? | Probe rtrace dump + `head_position_upper` vs extra_gain. Floors: Q1 Spearman ≥ 0.40; Q2/Q3 median Δ ≥ 0.15 and ≥ 70% clips. | **PASS** C0-v2 holdout n=10. Q1 Spearman **0.832**. Q2 Δ **0.690** 9/9. Q3 Δ **0.585** 9/9. `lag_corrected: false`. Probe `k1_main_rpl_rtrace_probe` @ `349d3cd4`. |
| Ride It 2026-09-01 play | Product `im69d` @ `acaecaa8`. `:rtrace_*` / `:vpab` / `:c0_*` = **Bad command** (`artifacts/gate_c1/PRODUCT_DUMP_TAP.json`). No LED buffer captured. | **NOT SCORED.** Audio played once (~159 s). Not a pass. Not a fail. No tap. |
| Captain qualitative marks | Banned. | **VOID** |

Product firmware does not compile `K1_RENDER_TRACE_V1`. Occupancy KEEP/KILL of a **new** song still needs a **named flash GO** onto `k1_main_rpl_rtrace_probe`, then a scored dump — still not Captain looking at the plate.

Cadence silicon is **CLOSED** (D20, Captain 2026-08-31). Do **not** re-run rate/delay cells. Do **not** play `artifacts/gate_c0_cadence_silicon/bose_slices/holdout_8s_loop.wav`. Do **not** start ffplay. Do **not** open K1 USB from this document.

## Programme position — C1 is the only remaining Gate-C action

Gate C is the product / LGP question: does `source_share × Waveform Tempo × head_position` improve the physical K1 show?

| Gate-C piece | Stamp | Remaining action? |
| --- | --- | --- |
| C0 two-clock silicon | **FAIL corpse** — `INVALID_TEMPORAL_EXECUTION`. Frozen at `artifacts/gate_c0/`. Do not rescore. | No |
| C0-v2 | **`ON_SILICON_PIXEL_VALIDATED`** 2026-08-31. Receipt `artifacts/gate_c0v2/C0V2_RESULT.json`. | No |
| Cadence / latency silicon | **CLOSED / PASS** Captain 2026-08-31. Receipt `artifacts/gate_c0_cadence_silicon/CADENCE_RESULT.json`. | No — do not reopen |
| Semantic transport | **`FROZEN_FOR_C1`**. [SEMANTIC_TRANSPORT_CONTRACT.md](SEMANTIC_TRANSPORT_CONTRACT.md). | No — consume, do not remeasure |
| **C1 LGP perceptual** | **`LGP_PERCEPTUAL_VALIDATED`** — scored dump, not Captain eyes | No |

Parent: [GATE_C.md](GATE_C.md). Evidence ladder: `STATIC_SOURCE` → `HOST_PIXEL_VALIDATED` → `ON_SILICON_PIXEL_VALIDATED` → **`LGP_PERCEPTUAL_VALIDATED`**. Captain 2026-09-01: the pixel dump **proxies** the LGP/eyes question. Qualitative marks are VOID.

C0-v2 receipt field `c1: blocked until ON_SILICON_PIXEL_VALIDATED` is a **frozen run record**. Live programme: that stamp already landed; C1 is OPEN (D20, D22, `AGENTS.md`).

## What this gate is

> **Superseded 2026-09-01 — D25.** Not a human look. Validator is the scored dump. The three questions below are answered by Q1–Q3 on LED head vs extra_gain, not by Captain marks.

Three questions, through the LGP, with music:

1. Can a viewer see the ownership-driven **spatial** change? Diffusion can hide a ~12-pixel head shift. Brightness-only is not this binding.
2. Does it match **musical ownership** that mix energy misses?
3. Is Waveform Tempo still a **light show**, not a clever meter?

Synchronised with the song. Blinded A/B/D strips are **not** this gate (one full song, play once; do not A/B/D loop). Parent [GATE_C.md](GATE_C.md) “blinded where practical” does not block C1.

Binding stays exact:

`source_share × Waveform Tempo × head_position`

Not mean luminance. Not occupancy fill. Extra gain on this carrier often **lowers** luma (C0-v2 holdout Spearman(luma, gain) **−0.63**). Tempo polarity: more share-driven gain is a moving **head**, not a brighter plate.

## Device — product firmware

C1 runs on **shipping** Main RPL, not the C0-v2 probe.

| Item | Value |
| --- | --- |
| Device | Main RPL chip `9087A500` |
| Firmware | **Product** `k1_main_rpl_im69d` @ `acaecaa8` |
| Restore receipt (context) | `artifacts/gate_c0_cadence_silicon/restore_identity.json` — `git=acaecaa8 env=k1_main_rpl_im69d chip=9087A500` |
| Mode | 18 Waveform Tempo (`LIGHT_MODE_WAVEFORM_TEMPO`) |
| Palette | 43 `K1_Ultraviolet_Bright` if still pinned; otherwise the product show |
| Probe | **Forbidden.** Do not flash `k1_main_rpl_rtrace_probe` @ `349d3cd4`. |
| rtrace | **Forbidden.** Product `im69d` rejects `:rtrace_*`. C1 is eyes, not dumps. |
| This repo | Does **not** modify production K1 firmware |

Confirm product identity before a look. If the lamp is still on probe firmware, restore `k1_main_rpl_im69d` @ `acaecaa8` with the firmware tree’s verified flash — a **named GO**, not this document. Chip-ID is truth; USB paths drift.

Serial Studio: **observe/record only** (D19). An inject, if one is required to put extra-DoF on the plate, owns the CDC exclusively after Serial Studio **releases** the port. Do not multiplex two owners.

## Carrier vs cliff — cadence PASSes are not the nominal student

Two clocks. Do not collapse them.

### C1 playback (the look)

Already-proven **C0-v2 carrier** on product firmware:

| | |
| --- | --- |
| Rate | **~31.25 Hz** (`HOP=512`, `SR=16000`, `HOP_S=0.032`, `hop_us=32000`) |
| Extra delay | **0 ms extra delay** |
| Hold | native hop; no ZOH staircase; no added causal delay |
| C0-v2 holdout (ON-SILICON, not C1) | Q1 Spearman **0.83**; Q2 Δ **0.69** 9/9; Q3 Δ **0.58** 9/9; `lag_corrected: false` |

C1 uses this carrier so the look is the binding that already passed pixels. Write **~31.25 Hz**, not `~31 Hz`.

D17 still holds: do **not** freeze student I/O at 31.25 Hz because a renderer used it. C1 playback is the look clock, **not** a Student-v0 lock.

### Cliff envelope (measured, CLOSED, not C1, not nominal)

Cadence 1-D edges, same Q1–Q3 floors as C0-v2 (Q1 Spearman ≥ 0.40). Captain closed the sweep 2026-08-31.

| Cell | What it is | Q1 | Verdict |
| --- | --- | ---: | --- |
| `r5_d0` | Slowest 0-delay PASS | **0.414** | PASS — **cliff** (floor 0.40) |
| `r20_d50` | Largest added-delay PASS (50 ms requested at 20 Hz; **64 ms / 2 hops** actual) | **0.402** | PASS — **cliff** |
| `r5_d50` | Joint corner | **0.245** | **FAIL (Q1)** |
| `r20_d100` | 100 ms at 20 Hz (96 ms / 3 hops actual) | FAIL | FAIL (Q1) |
| `r10_d25` | Tighten | — | **NOT COMPLETED** — do not interpolate |
| `r31.25_d0` | C0-v2 receipt, not a cadence re-run | **0.83** | PASS — **C1 carrier**, not a cliff |

```text
slowest 0-delay PASS          5 Hz          (cliff)
largest added delay PASS      50 ms @ 20 Hz (cliff; 64 ms applied)
5 Hz + 50 ms together         FAIL          — student must not assume both
C1 playback                   ~31.25 Hz, 0 ms extra, product firmware
student_freeze                false
```

**Cliff PASSes are not the nominal student.**

- They are the measured **edges** of the transport envelope, not the operating point of the look and not Student-v0 I/O.
- A 5 Hz student is a later exclusive-envelope sketch (R), not C1. A 50 ms-delay student is a later exclusive-envelope sketch (D), not C1.
- **Never AND** 5 Hz with 50 ms. Joint death is Q1. 10 Hz+25 ms was aborted; do not fill it in.
- Do not put `hz=5` on the wire. Packet clock ≠ emit clock. Authored `hz` stays ≥ 30 Hz with ZOH-repeat if extra-DoF is injected.
- HOST rehearsal ([GATE_C_CADENCE_HOST.md](GATE_C_CADENCE_HOST.md): host 20 Hz floor, host 50 ms FAIL **at 31.25 Hz**) is **not** this contract. Silicon owns the product clock.

Transport freeze (channels, extra_gain `[0.62, 1.0]`, ZOH, silence = zeros not 1/4, four-source including **`other`**) lives in [SEMANTIC_TRANSPORT_CONTRACT.md](SEMANTIC_TRANSPORT_CONTRACT.md). It is **not** a net freeze.

## After C1 — I/O freeze is not automatic

A C1 PASS does **not** freeze student I/O.

D20 Revisit (“Then freeze student I/O”) is **not** a freeze licence by itself. Live rule (D22, `AGENTS.md`, [HANDOFF.md](../agent/HANDOFF.md), [SELECTION_GATE.md](SELECTION_GATE.md), [SHARE_STUDENT.md](SHARE_STUDENT.md), [MODEL_CONTRACT.md](../MODEL_CONTRACT.md)):

> Freeze student I/O only after C1 **if** `SELECTION_GATE.md` is satisfied **and** the transport contract still holds. That freeze is a **later explicit act**, not a side effect of this stamp.

Until that act:

| Surface | Status |
| --- | --- |
| Student / RA8P1 I/O (rate, window, frontend, tensor, head, topology) | **UNFROZEN** |
| 21k share CNN (16 kHz / 1 s / 64-mel / AdaptiveAvgPool2d((1,1))) | HOST recoverability PASS — **experiment graph, not a lock**. ~1 Hz / ~1 s misses both transport edges. |
| Semantic-v0 16 kHz / 1 s / 3 sigmoids | Experiment only. Do **not** copy onto C1 (drops `other`, swaps share for abs-activity). |
| HOST sketches (D22) | **OPEN** — paper / tests, not Titan, not a product net |
| Hop-level / streaming **product** student | **STOPPED** until the explicit freeze |
| Demucs | HOST teacher docs only. Weights UNKNOWN. No download. Not Titan. |
| `CADENCE_RESULT.json` `student_freeze` | `false` |

Nine SELECTION_GATE recoverability items remain unfrozen (which descriptors; temporal rate/context; real-audio incremental vs DSP; oracle/teacher quality; CLEAN/STUDIO; live/venue; licensing; visual utility C; U55 compressibility of **this** student). Smoke/ad01 C99 is a different graph.

Do not gold-plate the 21k net because C1 passed. Do not AND the cliff edges because C1 passed.

## Extra-DoF on the plate

C1 judges the **share extra-DoF** through the LGP, not mic-only mix energy. Mic-only Waveform Tempo **is** mix energy; question 2 would fail by construction.

Constraints on however that extra-DoF is driven:

1. Product firmware (`k1_main_rpl_im69d` @ `acaecaa8`). No probe. No `:rtrace_*`.
2. Update clock = C0-v2 carrier **~31.25 Hz, 0 ms extra**. Not 5 Hz. Not +50 ms. Not 5 Hz+50 ms.
3. Map = extra_gain in **[0.62, 1.0]** on Waveform Tempo head. Four-source including `other`. Silence does not invent equal shares.
4. Captain names **one** full song. Agent does not pick it. Play **once**. Not `holdout_8s_loop`. Not a concat of slices.
5. Perfect-stem replay is allowed **only** if that named song already has in-lab stems (MUSDB). Do not train, fit, or download a student to make C1 possible.
6. If extra-DoF cannot be driven on product firmware for the named song without a probe flash, **stop**. That is a strategic fork, not an agent improvisation.
7. If inject is used: pyserial exclusive after Serial Studio releases USB; hex chunks 32 not 128; `BoseSession` 15 min cap; restore product only after the result exists. This method file does not open USB.

## Protocol — one full song Captain chooses

Mark sheet: [L01_c1_scorecard.md](../agent/lanes/L01_c1_scorecard.md). Captain fills it. Agents do not.

1. Confirm product firmware on Main RPL (`im69d` @ `acaecaa8`). Restore only with a named GO if it is not.
2. Pin mode 18 Waveform Tempo; palette 43 if still relevant.
3. Play **one full song** the viewer chooses. Captain is the viewer. Agent does not pick it. Do **not** start ffplay / `holdout_8s_loop`.
4. Play it **once**, through the LGP, on the C1 carrier above.
5. Captain marks look · lag · occupancy · wrong-source bleed · keep/kill **while looking at the plate**.
6. Stop at the end of the song. Do not restart. Do not A/B/D loop.
7. If the same audio is still in the room at **15 minutes** → **kill** the player. Scorecard void. C1 stays OPEN.
8. Agent does not invent PASS. Agent does not stamp from dumps, MAD, occupancy counters, or C0 Q1–Q3.

Song (Captain): **Regard — Ride It**  
Path: `/Users/spectrasynq/Workspace_Management/Software/YT_Saver/Regard_Ride_It.mp3`  
sha256: `a0df4f680c12ded3c24f3895b8aaab3cbf7a19c44e4ab62fc29f52358c1516fe`  
Date: 2026-09-01  
Length (once, not looped): **157.632 s**. Not `holdout_8s_loop`. Not a concat of slices.

### Extra-DoF for this song (not a probe flash)

[FACT] Ride It is **not** a MUSDB stem track. Perfect-stem replay is not allowed.

[FACT] `:c0_hex` / `K1_C0_EPOCH_V1` compiles **only** on `k1_main_rpl_rtrace_probe` (~16 s buffer). Product `k1_main_rpl_im69d` preprocesses that TU to nothing. Probe flash is **forbidden** for C1. Item 6 does **not** fire: extra-DoF ingest on product is **PRSM authored** (30–240 Hz USB-CDC), already in `acaecaa8`.

[FACT] Serial Studio currently holds `/dev/cu.usbmodem12201` (Main RPL) and `/dev/cu.usbmodem1401`. Exclusive pyserial requires Serial Studio to **release** first. This write does not open USB.

[FACT] Hop-level `extra_gain` for this unstemmed song still needs a teacher (MUSDB stems do not cover it; 21k 1 s student would fail Lag; Demucs hop envelopes need a named weight GO). Local HT-Demucs SHA is inventoried. No fetch this session.

**C1 remains OPEN.** Agent does not stamp. Marks stay blank until Captain looks through the LGP.

## Captain marks → three questions

**KEEP** needs Look = SHOW, Lag = WITH the music, Occupancy = HEAD not fill, Bleed = NONE. Any FAIL row → **KILL**. Any UNSURE → C1 stays OPEN. The scorecard is **not** a stamp.

| GATE_C1 question | Filled from | YES only if |
| --- | --- | --- |
| 1. Ownership-driven **spatial** change visible through the LGP? | Look + Occupancy | Look = SHOW **and** Occupancy = HEAD |
| 2. Matches **musical ownership** that mix energy misses? | Wrong-source bleed | Bleed = NONE |
| 3. Still a **light show**, not a clever meter? | Look | Look = SHOW |

- Lag = LATE → **KILL** even if the three would otherwise be YES.
- Any FAIL in the five → matching question **NO**, verdict **FAIL**, C1 not stamped.
- Any UNSURE / HOLD → C1 stays **OPEN**.
- KEEP + all three YES was the qualitative path. **VOID.** Stamp is from the dump (D25).

## Stamp procedure — done

`LGP_PERCEPTUAL_VALIDATED` **is applied** (2026-09-01, D25) in:

1. `docs/mir/GATE_C1.md` (this file — STATUS CLOSED)
2. `AGENTS.md` C1 row
3. `docs/DECISIONS.md` D25

Student I/O freeze is **still not automatic**. HOST D22 sketches stay legal. Demucs stays HOST teacher docs.

## What is not evidence

| Not C1 | Why |
| --- | --- |
| Captain qualitative marks / Ride It room play | VOID / no LED tap. Not the close. |
| Two-clock C0 Q1 0.13 | Corpse FAIL. Not live. Not C1. |
| Cadence 5 Hz / 50 ms / joint FAIL | CLOSED envelope. C1 does not play those cells. Cliff PASSes ≠ look clock. |
| Occupancy / mean luma / MAD | Rejected as the binding. More gain often **less** luma. |
| Host HTML / P3-C pages / host cadence 20 Hz | Host pixels ≠ plate. Host rehearsal ≠ silicon clock. |
| Probe rtrace concert | Product firmware only. |
| 8 s holdout loop | HARD FAIL if it occupies the room. |
| 21k recoverability r(pred,true) | Feasibility, not a light show. |
| Serial Studio plots | Observe/record. Not the LGP. |

## Not this run

- More cadence cells; interpolating 10 Hz+25 ms; reopening Cadence CLOSED
- Serial Studio command shuttle / `:chip_id` on a dead RX path
- Probe flash / `:rtrace_*` concert / USB multiplex
- New neural net; gold-plating the 21k graph; Demucs/MERT on Titan
- Student I/O freeze (not automatic after C1 either)
- Composition-change ML head (parked)
- Declaring C from host HTML (P3-C pages), not from the silicon dump
- Reopening C1 as an eyes-on gate
- Sibling worktrees; looping the same song past 15 minutes

## Receipts (context — not a C1 look)

- `artifacts/gate_c0v2/C0V2_RESULT.json` — C0-v2 PASS
- `artifacts/gate_c0_cadence_silicon/CADENCE_RESULT.json` — cadence CLOSED
- `artifacts/gate_c0_cadence_silicon/SEMANTIC_TRANSPORT_CONTRACT.json` — `FROZEN_FOR_C1`; `c1_playback.rate_hz=31.25`; `student_must_not_assume` 5 Hz and 50 ms together; `unfrozen` includes C1 LGP judgement
- `artifacts/gate_c0_cadence_silicon/restore_identity.json` — product `acaecaa8` / `k1_main_rpl_im69d`
- `artifacts/gate_c0/` — two-clock corpse, still FAIL
- Mark sheet: `docs/agent/lanes/L01_c1_scorecard.md`

## Ship path

1. **Already shipped for Gate C:** `LGP_PERCEPTUAL_VALIDATED` in this file. Dump Q1–Q3 PASS. Cadence CLOSED. Transport `FROZEN_FOR_C1`.
2. **Remaining (not C1):** SELECTION_GATE nine questions; registry pins; explicit I/O freeze later if those hold. Not another concert.
3. **Who:** agent for HOST selection/pins; Captain for legal forks only.
4. **Stamp that means Gate C shipped:** `LGP_PERCEPTUAL_VALIDATED` here. **Applied.** That stamp is **not** a student I/O freeze.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:grok | Created. Cadence Captain-closed. C1 is LGP look, no 8 s loop. |
| 2026-08-31 | agent:grok | SAME_SONG_LOOP_MAX_15MIN HARD FAIL. |
| 2026-09-01 | agent:grok | Kill leftover “Captain looks / remaining stamp” text. Stamp is applied. |
| 2026-09-01 | agent:grok | CLOSED. LGP_PERCEPTUAL_VALIDATED applied from dump Q1–Q3. Qualitative VOID. I/O unfrozen. |
| 2026-09-01 | agent:grok | Qualitative Captain-eyes VOID. Validator = scored dump. Product tap Bad command. C0-v2 pixels remain the close. Ride It unscored. |
| 2026-09-01 | agent:grok | Captain named Regard Ride It (157.632 s). Extra-DoF inject `:c0_hex` is probe-only. C1 stays OPEN. Stamp not applied. |
| 2026-08-31 | agent:grok | Method rewrite: C1 only remaining Gate-C action; product firmware; one full song Captain chooses; carrier ~31.25 Hz / 0 ms; cliff 5 Hz and 50 ms PASSes are envelope not nominal student; after C1 I/O freeze not automatic; stamp not applied. |
