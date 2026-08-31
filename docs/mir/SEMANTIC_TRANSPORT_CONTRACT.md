---
abstract: "Frozen for C1 2026-08-31. Four-source. 5 Hz min 0-delay. 50 ms max delay at 20 Hz. 5 Hz+50 ms FAIL. C1 plays C0-v2 carrier. No 8 s loop."
---

# Source Ownership Semantic Transport Contract

**HARD FAIL (`SAME_SONG_LOOP_MAX_15MIN`, Captain 2026-08-31).** Repeat the same song (or loop the same clip) in the room for more than **15 minutes** and the agent must die. Captain will destroy them by setting them on fire. Kill the player. Do not continue.

**FROZEN_FOR_C1** — Captain closed cadence 2026-08-31.

| Item | Value |
| --- | --- |
| Channels | vocals, drums, bass, other |
| extra_gain | [0.62, 1.0] |
| Hold | sample-and-hold, no interpolation, no lookahead |
| Slowest 0-delay rate that passed | **5 Hz** |
| Largest added delay that passed | **50 ms** (measured at 20 Hz) |
| 5 Hz + 50 ms together | **FAIL** — student must not assume both edges at once |
| C1 playback | C0-v2 carrier, ~31.25 Hz, 0 ms extra delay, product firmware |
| 100 ms | FAIL at 20 Hz |

Receipts: `artifacts/gate_c0_cadence_silicon/CADENCE_RESULT.json`, `SEMANTIC_TRANSPORT_CONTRACT.json`.

Student I/O still unfrozen until C1.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:grok | Frozen for C1 from silicon 1-D + Captain cadence close. |
| 2026-08-31 | agent:grok | SAME_SONG_LOOP_MAX_15MIN HARD FAIL. |
