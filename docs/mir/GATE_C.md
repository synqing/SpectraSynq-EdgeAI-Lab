---
abstract: "C0-v2 ON_SILICON_PIXEL_VALIDATED. Cadence CLOSED. C1 OPEN, not stamped. GATE_C0_SILICON_PATH is historical corpse recon, not a live inject recipe. Closed inject/dump is GATE_C0V2 (already ran). 5 Hz / 50 ms are cliffs. Product/Titan nets wait. HOST sketches/tests OPEN (D22). I/O unfrozen."
---

# Gate C — source ownership on the physical K1

**HARD FAIL (`SAME_SONG_LOOP_MAX_15MIN`, Captain 2026-08-31).** Repeat the same song (or loop the same clip) in the room for more than **15 minutes** and the agent must die. Captain will destroy them by setting them on fire. Kill the player. Do not continue.

Cadence silicon is **CLOSED**. Do not reopen cells. Do not play the 8 s holdout. This file does **not** stamp `LGP_PERCEPTUAL_VALIDATED`.

Programme stamp: **Source Ownership — PRE-PRODUCT FEASIBILITY PASS.**

Binding stays exact:

`source_share × Waveform Tempo × head_position`

Not “pixels changed.” Not mean brightness.

## Live stamps

| Gate | Stamp | Authority |
| --- | --- | --- |
| A — semantic information | **PASS** (share ≠ mix) | [SELECTION_GATE.md](SELECTION_GATE.md) |
| B — visual carrier | **HOST PASS** on this binding | P3-C `docs/mir/P3C_QUANT.json` |
| Recoverability | **HOST PASS** (21k CNN, four-source including `other`) | [SHARE_STUDENT.md](SHARE_STUDENT.md) |
| C0 two-clock silicon | **FAIL corpse** — `INVALID_TEMPORAL_EXECUTION` | `artifacts/gate_c0/` |
| C0-v2 | **`ON_SILICON_PIXEL_VALIDATED`** | [GATE_C0V2.md](GATE_C0V2.md), `artifacts/gate_c0v2/C0V2_RESULT.json` |
| Cadence / latency | **CLOSED** Captain 2026-08-31 | [GATE_C0_CADENCE.md](GATE_C0_CADENCE.md), `artifacts/gate_c0_cadence_silicon/CADENCE_RESULT.json` |
| Transport | **FROZEN_FOR_C1** (envelope, not a net) | [SEMANTIC_TRANSPORT_CONTRACT.md](SEMANTIC_TRANSPORT_CONTRACT.md) |
| C1 LGP | **OPEN** — not stamped | [GATE_C1.md](GATE_C1.md) |
| Student I/O | **UNFROZEN** until SELECTION_GATE **and** C1, if the contract still holds | D20 / D22 / `AGENTS.md` |

**Gate C is still OPEN.** C0-v2 pixels and the cadence envelope are necessary, not sufficient. C1 is the remaining human look.

## “No more neural-net work until C speaks” — resolved

> **Superseded.** The first-cut GATE_C / D17 sentence *“No more neural-net work until C speaks”* is not a total NN ban. D22 splits it.

**Why D17 said it.** The 21k net proved recoverability is plausible. Gold-plating that net, or starting a hop-level / streaming **product** student, before silicon said the semantic deserves a clock, is the wrong leverage point.

**What has already spoken.**

- C0-v2 **pixels** spoke: this binding is `ON_SILICON_PIXEL_VALIDATED` (Q1 0.83; Q2 Δ 0.69 9/9; Q3 Δ 0.58 9/9; `lag_corrected: false`).
- Cadence **1-D envelope** spoke: slowest 0-delay PASS 5 Hz; largest added-delay PASS 50 ms at 20 Hz; joint 5 Hz + 50 ms FAIL. Captain closed further cells.

**What has not spoken.** C1 LGP. Dumps do not answer it. This file does not stamp it.

**The live split (D22).** Product / Titan nets still **wait**. HOST sketches and HOST tests are **OPEN**. Streaming is unblocked for HOST sketches/tests, not Titan (`AGENTS.md`). Student I/O stays unfrozen.

| Allowed now (HOST) | Still wait |
| --- | --- |
| I/O paper sketches from the **transport edges** (exclusive envelope R **xor** D; never AND) | Train / fit a hop-level or streaming **product** student |
| HOST tests: pytest, numpy ZOH of an existing four-source oracle, contract tests | Gold-plate the 21k 1 s global pool as RA8P1 I/O |
| Semantic-v0 **experiment / toolchain** (not architecture) | Freeze Student-v0 I/O |
| Demucs **HOST teacher docs** (weights UNKNOWN; no Titan; no download from this file) | Demucs / MERT / MuQ / MAEST on Titan / U55 / PDM |
| MIR registry, oracle, DEAM, PaRIRset, effect-semantics consume | Extra product nets “because C0 passed” |
| RUHMI PRE-SILICON smoke / ad01 C99 (witness graph, not this student) | U55 compile of a streaming share student |
| Titan **prep docs** (no invented board numbers) | Treat C1 playback (~31.25 Hz, 0 ms) as a frozen student emit |

Sketches and tests are not a net. A HOST train of a deployment student is a product net and stays parked.

## Effect semantics set the ML clock

Wrong: model speaks at 31.25 Hz, so the effect is fed at 31.25 Hz.  
Right: measure the lowest cadence and worst extra delay at which this binding still carries ownership; the semantic lane must stay **inside that PASS region**.

BPM, phase, tick, and confidence are different bindings, not `"supports_tempo": true`.

Packet clock ≠ emit clock. Authored `hz` is 30–240; freshness 50 ms is the **wire**. Hold a slow semantic by **repeating** packets. Do not put `hz=5` on the wire.

## C0 — live: `ON_SILICON_PIXEL_VALIDATED`

**Live stamp (2026-08-31): C0-v2 PASS.** Closed inject/dump (already ran; **not** a re-inject recipe): [GATE_C0V2.md](GATE_C0V2.md). Receipt `artifacts/gate_c0v2/C0V2_RESULT.json`.

| Item | Value |
| --- | --- |
| Binding | `source_share × Waveform Tempo × head_position` |
| Holdout n | 10 |
| Q1 Spearman(head, extra_gain) | **0.83** PASS (≥ 0.40) |
| Q2 Δ partial r(head, share \| mix) | **0.69** 9/9 PASS |
| Q3 Δ source-abs after mix | **0.58** 9/9 PASS |
| Lag correction as PASS | **false** |
| Probe | `k1_main_rpl_rtrace_probe` @ `349d3cd4` |
| Chip | `9087A500` |
| Product restore after the run | `acaecaa8` / `k1_main_rpl_im69d` |

C0-v2 does **not** close Gate C. It opens C1.

Feed was the same extra-DoF as P3-C: A baseline, B mix-energy, D oracle share. Gain in [0.62, 1.0] on peak + chroma. Palette path. Waveform Tempo. Dump LED buffers. Score head-position extra-DoF (partial r of D vs B vs share | mix). Captain is not the C0 validator.

Do **not** re-run C0-v2 for C1. C1 plays **product firmware**, no probe, no rtrace concert. There is **no live inject recipe** in this file.

### Two-clock corpse (historical, not live)

**2026-08-31 two-clock C0: FAIL — INVALID TEMPORAL EXECUTION.** Frozen at `artifacts/gate_c0/`. Main RPL `9087A500`, probe `k1_main_rpl_rtrace_probe` @ `acaecaa8`. Holdout n=10: Q1 **0.13** FAIL; Q2/Q3 **6/9** FAIL. Capture and PRSM injection used two clocks. Silicon response was not dead. Post-hoc +14 hops (~448 ms) recovers host-like Q1–Q3 — **diagnosis only, not a PASS, never an authority rescore.**

Do **not** quote this FAIL as the current C0 close. The two-clock runner `scripts/gate_c0_silicon.py` is **retired**. Successor is C0-v2 above (already PASS). [GATE_C0_SILICON_PATH.md](GATE_C0_SILICON_PATH.md) is **historical recon of the two-clock corpse only**. It is **not** a live inject recipe, **not** a flash brief, and **not** a licence to run C0-v2.

## Cadence / latency — CLOSED. Cliffs are edges, not the student target

Receipt: [GATE_C0_CADENCE.md](GATE_C0_CADENCE.md) / `artifacts/gate_c0_cadence_silicon/CADENCE_RESULT.json` (`gate_c0_cadence=CLOSED`, `student_freeze=false`, `cadence_close=CAPTAIN_CLOSE_2026-08-31`). Transport table: [SEMANTIC_TRANSPORT_CONTRACT.md](SEMANTIC_TRANSPORT_CONTRACT.md).

Do **not** reopen cells. Do **not** play `artifacts/gate_c0_cadence_silicon/bose_slices/holdout_8s_loop.wav`. Do **not** interpolate the aborted 10 Hz + 25 ms cell.

Zero-order-hold the oracle series on the 32 ms hop grid; delay is causal `round(delay_s / 0.032)` hops. `lag_corrected=false`.

```text
~31.25 / 20 / 15 / 10 / 5 Hz @ 0 ms     PASS
20 Hz + 25 ms                           PASS
20 Hz + 50 ms requested (64 ms / 2 hops) PASS   ← delay cliff
20 Hz + 100 ms requested (96 ms / 3 hops) FAIL (Q1)
20 Hz + 200 ms                          FAIL
5 Hz + 50 ms (combined corner)          FAIL (Q1)
10 Hz + 25 ms                           NOT COMPLETED — do not interpolate
```

| What the 1-D sweep measured | What it is | What it is not |
| --- | --- | --- |
| Slowest 0-delay PASS **5 Hz** (`r5_d0`, Q1 0.414) | Rate **cliff** at 0 extra delay | Nominal student emit |
| Largest added-delay PASS **50 ms** at **20 Hz** (`r20_d50`, Q1 0.402; applied 64 ms) | Delay **cliff** at a comfortable rate | Nominal student latency |
| Combined **5 Hz + 50 ms FAIL** (`r5_d50`, Q1 0.245) | Measured AND-ban | A fill-in of 10 Hz+25 ms |
| C1 playback ~**31.25 Hz, 0 ms** extra (C0-v2 Q1 0.83) | Already-proven **carrier** on product firmware | A student I/O freeze (D17: do not freeze 31.25 Hz because a renderer used it) |

Both cliff Q1 scores sit on the 0.40 bar (0.414 and 0.402). Sitting on a cliff is sitting on the fail line. A student that **AND**s the two cliffs rebuilds `r5_d50` and fails Q1. A student that treats 5 Hz **or** 50 ms as the **design point after C1** is reading an envelope bound as a target.

**After C1, the cliffs stay edges.** If C1 PASSes and I/O later freezes, freeze the **contract** (four-source including `other`, share vs powers, hold policy, silence, numeric range, and the PASS **region**). Do **not** freeze “emit at 5 Hz” or “budget 50 ms extra delay” as the nominal student. Nominal remains unfrozen until that explicit freeze; a freeze that still holds this contract must serve the show C1 judged (the proven interior carrier) or a justified **interior** point, never both cliffs at once.

Pick one envelope if a sketch sits near a bound: **R** = ≥ 5 Hz and **0** extra delay, **or** **D** = ≥ 20 Hz and 50 ms requested (64 ms applied). Enum, not a union. HOST sketch: `docs/agent/lanes/L36_stream_sketch.md`.

A HOST rehearsal of the same holds ([GATE_C_CADENCE_HOST.md](GATE_C_CADENCE_HOST.md)) is **design evidence only**. Host lowest pass was 20 Hz; host 50 ms FAIL was at 31.25 Hz. That is not C0 and does not veto silicon. Do **not** freeze student I/O from the host ladder.

## C1 — `LGP_PERCEPTUAL_VALIDATED` (OPEN, not stamped)

**OPEN.** Method: [GATE_C1.md](GATE_C1.md). Cadence CLOSED. No 8 s holdout loop. No probe flash.

Only after C0 pixels behave — they do. Synchronised with music. Blinded where practical. Good Light Show Taxonomy: audio must change the *right* visual dimension.

Three questions:

1. Can a viewer perceive the ownership-driven spatial change through the LGP (diffusion can hide a 12-pixel head shift)?
2. Does it correspond to musical ownership that mix energy misses?
3. Does it keep Waveform Tempo as a light show, not a clever meter?

This is the first load-bearing **human** visual judgement. Dumps still exist; they do not answer C1. Captain is the viewer. This file does **not** write `LGP_PERCEPTUAL_VALIDATED`.

## After C PASSes — freeze the **semantic contract**, not the 21k net

Then lock, with numbers from C0 / cadence / C1, and only if [SELECTION_GATE.md](SELECTION_GATE.md) is also satisfied:

- four-source semantics (vocals / drums / bass / **other** — simplex is four-way)
- powers vs normalised share on the wire
- required update cadence as a **region**, not the 5 Hz cliff
- permitted extra latency as a **region**, not the 50 ms cliff (and never AND with the rate cliff)
- smoothing / interpolation (today: sample-and-hold, no interpolation, lookahead 0)
- silence (no invented equal shares)
- numeric range (`extra_gain` in [0.62, 1.0] on this binding)

Then — and only then — build a causal streaming **product** student to that contract. Do not gold-plate the 21k feasibility net first.

Then: streaming infer → quant → goldens → RUHMI/U55 → clean/live domain → Titan.

HOST sketches may exist **before** that freeze. They do not mint the freeze.

## Parked

- Product / Titan streaming-student train, goldens, U55 of a share student
- Student I/O freeze (HOST sketch OPEN; tests OPEN; I/O unfrozen)
- Demucs on Titan (HOST teacher docs OPEN; weights UNKNOWN; no download from this file)
- composition_change ML head (still a function of `share(t)` vs `share(t−Δ)`)
- Declaring C from host pixels
- Reopening cadence cells
- Stamping C1 from this document

## Ship path

1. **Already on silicon / in source:** C0-v2 `ON_SILICON_PIXEL_VALIDATED`; cadence 1-D CLOSED; transport FROZEN_FOR_C1; product on `acaecaa8` / `k1_main_rpl_im69d`; HOST sketches/tests legal (D22).
2. **Remaining:** Captain C1 LGP look on **one full song he chooses** (no 8 s loop) → if PASS, stamp `LGP_PERCEPTUAL_VALIDATED` in [GATE_C1.md](GATE_C1.md) + `AGENTS.md` + `docs/DECISIONS.md` → freeze student I/O only if SELECTION_GATE still holds and this envelope still holds → then a product streaming student.
3. **Who acts:** Captain for the C1 look. HOST SSAs for sketches/tests. Nobody flashes, nobody reopens cadence, nobody trains a Titan net from this file.
4. **Stamp that means Gate C shipped:** `LGP_PERCEPTUAL_VALIDATED`. This file is not that stamp. Student I/O freeze is a later explicit stamp, not automatic.

---
**Document Changelog**
| Date | Author | Change |
| --- | --- | --- |
| 2026-08-31 | agent:edgeai | C0 pixel+cadence then C1 LGP; semantics set ML clock; no NN until C. |
| 2026-08-31 | agent:edgeai | C0 silicon FAIL on Main RPL; Q1 0.13 / Q2–Q3 6/9; C1 blocked. |
| 2026-08-31 | agent:edgeai | FAIL cause = inject alignment; lagged rescore not a PASS. |
| 2026-08-31 | agent:edgeai | Stamp INVALID_TEMPORAL_EXECUTION; two-clock runner retired; C0-v2 successor. |
| 2026-08-31 | agent:grok | C0-v2 PASS; cadence Captain-closed; C1 OPEN. |
| 2026-08-31 | agent:grok | SAME_SONG_LOOP_MAX_15MIN HARD FAIL. |
| 2026-08-31 | agent:grok | C0 body: two-clock FAIL labelled corpse; live stamp C0-v2 PASS; cadence CLOSED numbers. |
| 2026-08-31 | agent:grok | D17 “no NN until C speaks” vs D22: product/Titan wait; HOST sketches/tests OPEN. 5 Hz / 50 ms are cliffs, not the post-C1 student target. C1 not stamped. Cadence stays CLOSED. |
| 2026-08-31 | agent:grok | W4-L23: GATE_C0_SILICON_PATH retargeted historical corpse recon, not live inject recipe. Closed inject/dump is GATE_C0V2 (already ran). C0-v2 PASS stays live. Cadence stays CLOSED. |
