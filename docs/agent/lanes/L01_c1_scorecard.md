---
abstract: "C1 scorecard VOID as Captain-eyes. Validator is scored rtrace dump (C0-v2 Q1–Q3). Ride It play uninstrumented. Product im69d rejects :rtrace. Stamp LGP_PERCEPTUAL_VALIDATED not applied."
---

# L01 — C1 instrument sheet

**STATUS:** Qualitative Captain marks **VOID**. Gate stamp **`LGP_PERCEPTUAL_VALIDATED` applied** in `docs/mir/GATE_C1.md` (D25, dump-scored). This sheet does not re-stamp.

**HARD FAIL (`SAME_SONG_LOOP_MAX_15MIN`).** Same song or clip looping in the room past **15 minutes** → kill the player.

**HARD FAIL (`instrument-not-captain-eyes`).** Do **not** fill look / lag / occupancy / bleed / keep by walking to the plate. The five-mark table below is **historical**. Live validator: scored LED dump (`head_position_upper` vs extra_gain), same floors as C0-v2.

Authority: `docs/mir/GATE_C1.md` (D20, D21, D22). Binding: `source_share × Waveform Tempo × head_position`. C0-v2 remains `ON_SILICON_PIXEL_VALIDATED`. Cadence **CLOSED**.

## What this is

The mark sheet for **one** full song Captain chooses. Five marks: **look · lag · occupancy · wrong-source bleed · keep/kill**.

This lane does **not** play audio, open USB, flash, inject PRSM, run ffplay, or loop the 8 s holdout.

## Preconditions (must already hold)

| Item | Required |
| --- | --- |
| Device | Main RPL chip `9087A500` |
| Firmware | **Product** last restored `k1_main_rpl_im69d` @ `acaecaa8`. No probe. No `:rtrace_*`. No flash this lane. |
| Mode | 18 Waveform Tempo. Palette 43 if still pinned; else the product show. |
| Carrier | Proven C0-v2 path only: **~31.25 Hz, 0 ms extra delay.** Do not run 5 Hz. Do not add 50 ms. Do **not** run 5 Hz+50 ms (silicon FAIL). |
| Player | Captain. **One full song he chooses.** Play it once. Not `holdout_8s_loop`. Not a concat of slices. |
| Cap | 15 min same-audio → kill. Serial Studio observe/record only. No USB multiplex. No cadence cells. |

Last restore receipt (context, not a C1 look): `artifacts/gate_c0_cadence_silicon/restore_identity.json` — `git=acaecaa8 env=k1_main_rpl_im69d chip=9087A500`.

Live pin 2026-09-01 (Serial Studio released): `artifacts/gate_c1/PIN_RECEIPT.json` — chip `9087A500`, `env=k1_main_rpl_im69d`, `git=acaecaa8`, Waveform Tempo dense 17 / ordinal 18, palette 43. Port `/dev/cu.usbmodem12201` closed after pin. No audio, no `:c0_hex`, no stamp.

## Song protocol

1. Captain names **one** full track. Agent does not pick it.
2. Play **once**, through the LGP, on product firmware, Waveform Tempo.
3. Captain marks the five rows **while looking at the plate**, not at dumps.
4. Stop at the end of the song. Do not restart. Do not A/B/D loop.
5. If the same audio is still in the room at 15 minutes → **kill**. Scorecard void.

Song (Captain): Regard — Ride It  
Path: `/Users/spectrasynq/Workspace_Management/Software/YT_Saver/Regard_Ride_It.mp3`  
sha256: `a0df4f680c12ded3c24f3895b8aaab3cbf7a19c44e4ab62fc29f52358c1516fe`  
Date: 2026-09-01  
Length (once, not looped): **157.632 s** (~2 min 38 s). Not an 8 s loop. Play **once**. Cap 15 min.

## Five marks (Captain only)

Answer each row. **KEEP** needs Look = SHOW, Lag = WITH the music, Occupancy = HEAD not fill, Bleed = NONE. Any FAIL row → **KILL**. Any UNSURE → C1 stays OPEN. This table is **not** a stamp.

| Mark | Watch this | PASS | FAIL | U |
| --- | --- | --- | --- | --- |
| **Look** | Through the LGP, is Waveform Tempo still a **light show** — a wave-head moving in space — not a clever meter or a brightness blob? Diffusion can hide a ~12-pixel head shift. Brightness-only is FAIL. | ☐ SHOW | ☐ METER / BLIND | ☐ |
| **Lag** | Does the head move **with** the music, or behind it? C1 plays the already-proven carrier (~31.25 Hz, **0 ms** extra). Do not re-run cadence. Late vs the hit = FAIL. | ☐ WITH | ☐ LATE | ☐ |
| **Occupancy** | Is the story the **wave-head position** (centre seam → tip), or the plate filling / emptying / getting brighter? Occupancy and luma are **not** the binding. Extra gain often **lowers** luma. Fill-as-cue = FAIL. | ☐ HEAD | ☐ FILL / BRIGHT | ☐ |
| **Wrong-source bleed** | When **one** source owns (vocal out front, drums take it, bass in a quiet stretch, *other* bed), does the head follow **that** owner — or mix loudness / the wrong stem? Mix-energy stealing the head is bleed. Four-source includes `other`. | ☐ NONE | ☐ BLEED | ☐ |
| **Keep / kill** | Keep this extra-DoF as product lighting, or kill it? KEEP is **not** `LGP_PERCEPTUAL_VALIDATED`. KILL is FAIL. | ☐ KEEP | ☐ KILL | ☐ HOLD |

Notes (optional, one line): ________________________________

## Collapse into GATE_C1 (agents, after Captain marks)

Do **not** fill these for Captain. Do **not** stamp from this table in this file.

| GATE_C1 question | Filled from | YES only if |
| --- | --- | --- |
| 1. Ownership-driven **spatial** change visible through the LGP? | Look + Occupancy | Look = SHOW **and** Occupancy = HEAD |
| 2. Matches **musical ownership** that mix energy misses? | Wrong-source bleed | Bleed = NONE |
| 3. Still a **light show**, not a clever meter? | Look | Look = SHOW |

- Lag = LATE → **KILL** even if the three would otherwise be YES (the show is late).
- Any FAIL in the five → GATE_C1 **NO** on the matching question, verdict **FAIL**, C1 not stamped.
- Any UNSURE / HOLD → C1 stays **OPEN**.
- KEEP + all three YES is the **only** path that later allows a stamp — written in `GATE_C1.md` + `AGENTS.md` + `DECISIONS.md` by a later act, **not here**.

**This file's verdict:** OPEN / FAIL / *(stamp forbidden here)*  
**Stamp `LGP_PERCEPTUAL_VALIDATED`:** **not applied.**

## What is not evidence

| Not C1 | Why |
| --- | --- |
| C0-v2 Q1 Spearman 0.83, Q2 Δ 0.69 9/9, Q3 Δ 0.58 9/9 | Silicon pixels. Not LGP. `lag_corrected=false`. |
| Cadence 5 Hz / 50 ms / joint FAIL | CLOSED. C1 does not play those cells. |
| Occupancy / mean luma / MAD | Rejected as the binding. Tempo polarity: more gain often **less** luma. |
| Host HTML / P3-C pages | Host pixels ≠ plate. |
| Probe rtrace concert | Product firmware only. `:rtrace_*` rejected on `k1_main_rpl_im69d`. |
| 8 s holdout loop | HARD FAIL if it occupies the room. |

## Not this lane

Cadence cells · ffplay · `/dev/cu.usbmodem*` · `k1-flash` · probe `k1_main_rpl_rtrace_probe` · Serial Studio shuttle · new net · student I/O freeze · Demucs / Titan · sibling worktrees · inventing PASS · stamping `LGP_PERCEPTUAL_VALIDATED`.

Receipts (context only): `artifacts/gate_c0v2/C0V2_RESULT.json`, `artifacts/gate_c0_cadence_silicon/restore_identity.json`, `docs/mir/SEMANTIC_TRANSPORT_CONTRACT.md`, `docs/mir/GATE_C1.md`.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:grok | Created. One-page C1 LGP scorecard from GATE_C1. No audio. |
| 2026-09-01 | agent:grok | Qualitative marks VOID. Validator is C0-v2 scored dump. Ride It play had no LED tap. |
| 2026-09-01 | agent:grok | Ride It played once (~159 s wall, afplay -t 160, Bose). Player dead. Marks still blank. Stamp not applied. |
| 2026-09-01 | agent:grok | Product identity live-confirmed; Waveform Tempo pinned. Marks still blank. Stamp not applied. |
| 2026-09-01 | agent:grok | Song filled: Regard Ride It, 157.632 s, sha256 a0df4f68… Marks still blank. Stamp not applied. |
| 2026-08-31 | agent:grok | Overwrite: Captain marks look, lag, occupancy, bleed, keep/kill on one song. Stamp not applied. |
