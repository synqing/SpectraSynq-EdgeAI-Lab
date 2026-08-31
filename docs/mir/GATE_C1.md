---
abstract: "C1 OPEN. Cadence CLOSED Captain 2026-08-31. No 8 s holdout loops. Product firmware. LGP look is the gate. Student I/O still unfrozen."
---

# Gate C1 — LGP perceptual

**HARD FAIL (`SAME_SONG_LOOP_MAX_15MIN`, Captain 2026-08-31).** Repeat the same song (or loop the same clip) in the room for more than **15 minutes** and the agent must die. Captain will destroy them by setting them on fire. Kill the player. Do not continue.

Cadence is **CLOSED**. Do **not** re-run rate/delay silicon. Do **not** loop the 8-second holdout clips.

C0-v2 remains `ON_SILICON_PIXEL_VALIDATED`. Binding stays `source_share × Waveform Tempo × head_position`.

Transport contract (frozen for this gate): four-source including `other`; extra_gain in [0.62, 1.0]; sample-and-hold; **5 Hz** is the slowest 0-delay rate that passed; **50 ms** is the largest added delay that passed at 20 Hz; **5 Hz + 50 ms together FAIL** — do not assume both edges at once. C1 playback is the already-proven carrier (~31 Hz, 0 ms extra delay) on **product firmware**.

## This gate

Three questions, through the LGP, with music:

1. Can a viewer see the ownership-driven spatial change (diffusion can hide a 12-pixel head shift)?
2. Does it match musical ownership that mix energy misses?
3. Is Waveform Tempo still a light show, not a clever meter?

Dumps do not answer this. Captain is the viewer. Agent does not start the 8 s loop.

## How

Product firmware is already on Main RPL (`k1_main_rpl_im69d` @ `acaecaa8`). No probe flash. No rtrace concert.

Play **one full song** the viewer chooses. Not the test-slice loop. Mode 18 Waveform Tempo, palette 43 if still pinned; otherwise the product show.

Stamp `LGP_PERCEPTUAL_VALIDATED` only after the three questions are answered. Until then C1 is OPEN.

## Not this run

- More cadence cells
- Serial Studio shuttle
- New neural net
- Student I/O freeze

Receipts: `artifacts/gate_c0_cadence_silicon/CADENCE_RESULT.json`, `SEMANTIC_TRANSPORT_CONTRACT.json`.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:grok | Created. Cadence Captain-closed. C1 is LGP look, no 8 s loop. |
| 2026-08-31 | agent:grok | SAME_SONG_LOOP_MAX_15MIN HARD FAIL. |
