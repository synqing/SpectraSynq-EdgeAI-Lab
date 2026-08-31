---
abstract: "C1 LGP look sheet. OPEN. Captain marks look, lag, occupancy, wrong-source bleed, keep/kill on one full song he chooses. Product k1_main_rpl_im69d @ acaecaa8. Carrier C0-v2 ~31.25 Hz 0 ms. This file does not stamp LGP_PERCEPTUAL_VALIDATED. No audio/USB this lane."
---

# L01 — C1 look scorecard

**STATUS:** OPEN. Stamp **not** applied. This lane writes the sheet only.

**HARD FAIL (`SAME_SONG_LOOP_MAX_15MIN`).** Same song or clip looping in the room past **15 minutes** → kill the player. Card is void. Do not continue.

C1 is OPEN until Captain looks at the LGP. Dumps, MAD, occupancy counters, and silicon Q1–Q3 **do not** fill this sheet. Agents do not invent PASS. Agents do not stamp `LGP_PERCEPTUAL_VALIDATED` from this file.

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

## Song protocol

1. Captain names **one** full track. Agent does not pick it.
2. Play **once**, through the LGP, on product firmware, Waveform Tempo.
3. Captain marks the five rows **while looking at the plate**, not at dumps.
4. Stop at the end of the song. Do not restart. Do not A/B/D loop.
5. If the same audio is still in the room at 15 minutes → **kill**. Scorecard void.

Song (Captain): ________________________________  
Date: __________  
Length (once, not looped): __________

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
| 2026-08-31 | agent:grok | Overwrite: Captain marks look, lag, occupancy, bleed, keep/kill on one song. Stamp not applied. |
