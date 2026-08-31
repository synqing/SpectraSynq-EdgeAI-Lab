---
abstract: "C1 LGP scorecard. OPEN. Captain answers 3 questions on one full song he chooses, product firmware, no 8 s loop. Stamp LGP_PERCEPTUAL_VALIDATED only after all three YES. No audio from this lane."
---

# C1 scorecard — LGP perceptual

**Status:** OPEN. Stamp **not** applied. Authority: `docs/mir/GATE_C1.md` (D20, D21).  
**Binding:** `source_share × Waveform Tempo × head_position`. C0-v2 remains `ON_SILICON_PIXEL_VALIDATED`. Cadence **CLOSED**.  
**Viewer:** Captain. Dumps / MAD / Q1–Q3 **do not** answer this gate.

## Preconditions (must hold before the look)

| Item | Required |
| --- | --- |
| Device | Main RPL chip `9087A500` |
| Firmware | **Product** `k1_main_rpl_im69d` @ `acaecaa8`. No probe. No `:rtrace_*`. No flash this lane. |
| Mode | 18 Waveform Tempo; palette 43 if still pinned; else the product show |
| Carrier | Already-proven C0-v2 path (~31 Hz, **0 ms** extra delay). Do **not** run 5 Hz+50 ms. |
| Player | Captain. **One full song he chooses.** Not `holdout_8s_loop`. Not ffplay. |
| Cap | `SAME_SONG_LOOP_MAX_15MIN` HARD FAIL. Kill the player. Do not continue. |

## Song protocol

1. Captain names **one** full track (any length he wants; play it once).  
2. Agent does **not** pick, loop, concatenate, or restart it.  
3. If the same audio is still in the room at 15 minutes → **kill**. Scorecard is void.  
4. Serial Studio observe/record only. No USB multiplex. No cadence cells.

## Three LGP questions (Captain only)

Answer each **YES / NO / UNSURE**. All three must be **YES** to stamp. Any NO = FAIL. Any UNSURE = still OPEN.

| # | Question | Y | N | ? |
| --- | --- | --- | --- | --- |
| **Q1 Spatial** | Through the LGP, can you see the ownership-driven **spatial** change? (Diffusion can hide a ~12-pixel head shift. If you only see brightness, that is NO.) | ☐ | ☐ | ☐ |
| **Q2 Ownership** | Does that change match **musical ownership** that mix energy misses? (Who is driving the mix, not how loud the mix is.) | ☐ | ☐ | ☐ |
| **Q3 Show** | Is Waveform Tempo still a **light show**, not a clever meter? | ☐ | ☐ | ☐ |

Song title (Captain): ______________________________  
Date: __________  Verdict: OPEN / FAIL / `LGP_PERCEPTUAL_VALIDATED`

## Stamp rule

- **PASS** → write `LGP_PERCEPTUAL_VALIDATED` in `GATE_C1.md` + `AGENTS.md` + `DECISIONS.md`. Student I/O freeze is **still not automatic**.  
- **Until then** C1 stays OPEN. Do not invent PASS from pixels.

## Not this scorecard

Cadence cells · 8 s holdout · Serial Studio shuttle · probe flash · new net · student I/O freeze · Demucs/Titan.

Receipts (context only, not C1 evidence): `artifacts/gate_c0_cadence_silicon/CADENCE_RESULT.json`, `docs/mir/SEMANTIC_TRANSPORT_CONTRACT.md`.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:grok | Created. One-page C1 LGP scorecard from GATE_C1. No audio. |
