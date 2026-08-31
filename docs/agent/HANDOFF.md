---
abstract: "Handover 2026-08-31. Cadence CLOSED Captain PASS. C1 OPEN. Do not loop songs >15 min. Do not reopen Serial Studio shuttle. Do not run more cadence cells."
---

# Handover — EdgeAI-Lab 2026-08-31

**HARD FAIL (`SAME_SONG_LOOP_MAX_15MIN`, Captain 2026-08-31).** Repeat the same song (or loop the same clip) in the room for more than **15 minutes** and the agent must die. Captain will destroy them by setting them on fire. Kill the player. Do not continue. Encoded in `AGENTS.md`, D21, `BoseSession.SAME_SONG_LOOP_MAX_S = 900`.

Cadence silicon is **CLOSED**. Do **not** resume `gate_c0_cadence_silicon.py`. Do **not** play `artifacts/gate_c0_cadence_silicon/bose_slices/holdout_8s_loop.wav`.

## Goal

Run **C1 LGP perceptual** on product firmware. Stamp `LGP_PERCEPTUAL_VALIDATED` only after Captain answers the three LGP questions on **one full song he chooses**. Then student I/O freeze is still not automatic — freeze only after C1 if the contract still holds.

Programme (load-bearing):

```text
C0-v2 PASS → cadence CLOSED → transport contract frozen → C1 LGP → only then student/deployment
```

## Current progress

| Item | Status |
| --- | --- |
| Gate A (share has extra information) | PASS |
| Gate B HOST (share × WaveformTempo × head_position) | PASS |
| Share student HOST recoverability | PASS (21k, four-source incl. `other`). Streaming student STOPPED |
| C0 two-clock silicon | FAIL corpse. Do not rescore. `artifacts/gate_c0/` |
| C0-v2 | `ON_SILICON_PIXEL_VALIDATED` 2026-08-31. Receipt `artifacts/gate_c0v2/C0V2_RESULT.json` |
| Cadence/latency silicon | **CLOSED / PASS** Captain 2026-08-31. Receipt `artifacts/gate_c0_cadence_silicon/CADENCE_RESULT.json` |
| Semantic transport contract | Frozen for C1. `docs/mir/SEMANTIC_TRANSPORT_CONTRACT.md` |
| Serial Studio command shuttle | **DEAD / DEMOTED** (D19). Observe/record only |
| C1 LGP | **OPEN** — one full song Captain chooses. Not tonight unless he wants it. |
| Student I/O freeze | NOT YET. Freeze only after `SELECTION_GATE.md` **and** C1 if the contract still holds. |
| HOST sketches (share stream, semantic-v0 experiment, Demucs teacher docs) | **OPEN** (D22). Not Titan. Not a product net. |
| Titan / U55 student compile | PRE-SILICON docs only. No invented board numbers. |

### Cadence numbers (do not re-measure)

```text
minimum demonstrated useful rate: 5 Hz (0 ms extra delay)  PASS
maximum demonstrated added delay: 50 ms (at 20 Hz)         PASS
100 ms at 20 Hz: FAIL (Q1)
200 ms at 20 Hz: FAIL
5 Hz + 50 ms together: FAIL (Q1)
10 Hz + 25 ms: NOT COMPLETED — Captain ordered audio stopped
```

A student must **not** assume 5 Hz **and** 50 ms extra delay at the same time.

C1 playback uses the already-proven C0-v2 carrier (~31.25 Hz, 0 ms extra delay) on **product firmware**.

## Device (last verified)

- Main RPL chip `9087A500`, USB `B4:3A:45:A5:87:90`, typically `/dev/cu.usbmodem12201`
- Product restored: `IDENTITY OK git=acaecaa8 env=k1_main_rpl_im69d`
- Do **not** flash `k1_main_rpl_rtrace_probe` for C1
- Do **not** modify production K1 firmware from this repo
- Firmware worktree used for flashes: `/Users/spectrasynq/SpectraSynq_K1_Firmware/.worktrees/effect-response-atlas`

## What worked

- Exclusive **pyserial** after Serial Studio releases USB (D19). Not the SS shuttle.
- C0-v2 one device-epoch harness. Same Q1–Q3 scorer as P3-C. No lag correction as a PASS.
- Cadence 1-D: 20/15/10/5 Hz PASS at 0 ms; 25/50 ms PASS at 20 Hz.
- Killing ffplay when Captain says stop. `SAME_SONG_LOOP_MAX_S` in `BoseSession`.

## What did not work — do not repeat

- Serial Studio as command transport / `:chip_id` shuttle / gRPC / MCP / USB-reset archaeology. D19. Optional later, not on C1 path.
- Two-clock C0 (`scripts/gate_c0_silicon.py` RETIRED).
- Looping the 8 s holdout for hours. Captain will destroy the agent.
- 128-char `:c0_hex` chunks (`HEX FAIL: parse`). Keep 32-char chunks if you ever inject again.
- `osascript 'get volume settings'` aborting silicon; crash `finally` flashing product mid-test.
- Restoring product firmware on every exception while a probe session is still needed.
- Interpolating 10 Hz+25 ms. Combined 5 Hz+50 ms FAIL is real.
- Asking Captain to squint at LEDs for buffer/pixel questions (`/instrument-not-captain-eyes`). C1 **is** the human LGP look — different question.
- Re-asking approval after GO (`/no-reapprove-already-given`).
- Leading summaries with audit labels (`/plain-english-work-summaries`).
- Closing a hold without a numbered ship path (`/ship-path-required`).

## Next steps (C1)

Canonical method: `docs/mir/GATE_C1.md`.

1. Read `AGENTS.md`, `docs/DECISIONS.md` D19–D22, `docs/mir/GATE_C.md`, `docs/mir/GATE_C1.md`, `docs/mir/SEMANTIC_TRANSPORT_CONTRACT.md`.
2. Confirm product firmware still on Main RPL. If not, restore `k1_main_rpl_im69d` @ `acaecaa8` with `k1-flash-verified.sh`. No probe.
3. Do **not** start ffplay / holdout_8s_loop. Captain plays **one full song he likes**.
4. Mode: Waveform Tempo (18), palette 43 if still relevant; else product show.
5. Captain answers the three LGP questions. Agent does not invent PASS.
6. PASS → stamp `LGP_PERCEPTUAL_VALIDATED` in `docs/mir/GATE_C1.md` + `AGENTS.md` + `docs/DECISIONS.md`. Student I/O freeze is still not automatic. HOST D22 sketches stay legal. Demucs is HOST teacher docs only — not Titan, not a download.
7. If a silicon inject is ever required again: pyserial exclusive, Serial Studio closed, hex chunk 32, BoseSession 15 min cap, no 8 s loop, restore product only after the result file exists.

## Read order

1. `AGENTS.md`
2. `docs/agent/HANDOFF.md` (this file)
3. `docs/DECISIONS.md` (D19 shuttle dead, D20 cadence closed, D21 15 min kill, D22 HOST lanes OPEN)
4. `docs/mir/GATE_C1.md` — **active**
5. `docs/mir/SEMANTIC_TRANSPORT_CONTRACT.md`
6. `artifacts/gate_c0_cadence_silicon/CADENCE_RESULT.json` — do not reopen cells
7. `docs/mir/GATE_C0V2.md` — C0-v2 already PASS
8. `docs/mir/SERIAL_STUDIO.md` — observe/record only

Repo: `/Users/spectrasynq/SpectraSynq-EdgeAI-Lab`

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:grok | Created. Cadence closed. C1 next. 15 min same-song kill. |
| 2026-08-31 | agent:grok | D22: HOST sketches OPEN; freeze is SELECTION_GATE + C1, not C1-alone. |
