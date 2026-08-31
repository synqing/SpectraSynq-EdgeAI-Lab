---
abstract: "Git-visible copy of gitignored C0-v2 and cadence silicon receipts. C0-v2 PASS ON_SILICON_PIXEL_VALIDATED. Cadence CLOSED 5 Hz / 50 ms; 5 Hz+50 ms FAIL. Chip 9087A500 git 349d3cd4. Do not reopen cadence."
---

# Silicon receipts — C0-v2 and cadence

**HARD FAIL (`SAME_SONG_LOOP_MAX_15MIN`, Captain 2026-08-31).** Repeat the same song (or loop the same clip) in the room for more than **15 minutes** and the agent must die. Captain will destroy them by setting them on fire. Kill the player. Do not continue.

`.gitignore` excludes `artifacts/`. This file is the Git-visible proof. It does **not** reopen Cadence silicon. No USB. No flash. No 8 s loop.

**Workspace presence (this Mac, 2026-08-31):** both receipts **exist**. Stamp is **`IN_WORKSPACE`**, not `NOT_IN_WORKSPACE`. Numbers below are copied from those JSON files (ON-SILICON). GATE_C0V2.md / GATE_C0_CADENCE.md / L40 are cross-checks, not the substitute path.

**SHA-256 of on-disk bytes (orchestrator 2026-08-31, HOST, no USB):**

```
57b408be9d9941735b42c09fba7e174488ddcd02b81494c3eb84f29e72391928  artifacts/gate_c0v2/C0V2_RESULT.json
371573dc9e5769629dae5dc1c572fb57c0a0884d9239a8c0245a8576f9b4449d  artifacts/gate_c0_cadence_silicon/CADENCE_RESULT.json
```

## C0-v2 — `artifacts/gate_c0v2/C0V2_RESULT.json`

| Field | Value |
| --- | --- |
| presence | **IN_WORKSPACE** |
| sha256 | `57b408be9d9941735b42c09fba7e174488ddcd02b81494c3eb84f29e72391928` |
| `c0v2` | `PASS` |
| stamp | `source_share × WaveformTempo × head_position = ON_SILICON_PIXEL_VALIDATED` |
| binding | `source_share × WaveformTempo × head_position` |
| `lag_corrected` | `false` |
| `retired_c0_untouched` | `true` |
| Q1 / Q2 / Q3 | `PASS` / `PASS` / `PASS` |
| holdout n | 10 |
| Q1 Spearman (`median_spearman_pos_gain`) | **0.8318621417942687** (docs round 0.83) |
| Q2 Δ (`median_delta_pos_share`) | **0.6902070639445945**, wins **9/9** (docs round 0.69) |
| Q3 Δ (`median_delta_pos_abs`) | **0.5849115161446871**, wins **9/9** (docs round 0.58) |
| self-test | `status=PASS`, `integrity=OK`, `best_lag_hops=0` |
| chip | `9087A500` |
| git | `349d3cd4` |
| env | `k1_main_rpl_rtrace_probe` |
| epoch | `1788135177` |
| pin | dense_index `17`, mode_ordinal `18` |
| receipt-time `cadence` | `OPEN — not this run` (historical; later closed — see cadence block) |
| receipt-time `c1` | `blocked until ON_SILICON_PIXEL_VALIDATED` (stamp now holds; programme C1 is OPEN — D20) |

Non-claims on the receipt (kept): previous C0 still FAIL `INVALID_TEMPORAL_EXECUTION`; no Gate C perceptual verdict; no student freeze; no cadence freeze *in that run*; no Titan.

## Cadence — `artifacts/gate_c0_cadence_silicon/CADENCE_RESULT.json`

| Field | Value |
| --- | --- |
| presence | **IN_WORKSPACE** |
| sha256 | `371573dc9e5769629dae5dc1c572fb57c0a0884d9239a8c0245a8576f9b4449d` |
| authorisation | `K1-C0-CADENCE-LATENCY-FLASH-GO` |
| `c0v2` | `ON_SILICON_PIXEL_VALIDATED` (not re-opened) |
| `cadence` | `PASS` |
| `gate_c0_cadence` | **`CLOSED`** |
| `cadence_close` | `CAPTAIN_CLOSE_2026-08-31` |
| `lag_corrected` | `false` |
| `stopped_audio` | `true` |
| `student_freeze` | `false` |
| chip | `9087A500` |
| git | `349d3cd4` |
| env | `k1_main_rpl_rtrace_probe` |
| session epoch (last cells) | `1788170175` |

### Rate / delay edges (`plain` + brackets)

| Edge | Value |
| --- | --- |
| minimum demonstrated useful rate | **5 Hz** (0 ms extra delay) |
| maximum demonstrated added delay | **50 ms** (at 20 Hz; requested; hop-round actual 64 ms) |
| combined 5 Hz + 50 ms | **FAIL** (kept; not interpolated) |
| combined 10 Hz + 25 ms | **`NOT_COMPLETED`** (`tighten_complete=false`) |
| slowest passing 0-delay rate | `rate.slowest_passing_rate_hz = 5.0` |
| largest passing delay | `delay.largest_passing_delay_s = 0.05` |

`plain.Q`:

| Cell | Q1 | Q2 | Q3 |
| --- | --- | --- | --- |
| 5 Hz | PASS | PASS | PASS |
| 20 Hz + 50 ms | PASS | PASS | PASS |
| 20 Hz + 100 ms | FAIL | PASS | PASS |
| 5 Hz + 50 ms | FAIL | PASS | PASS |

### Tiny cell verdicts (requested delay; hop-round in JSON)

| Cell | source | verdict | Q1 | Q2 | Q3 |
| --- | --- | --- | --- | --- | --- |
| 31.25 Hz @ 0 ms | `c0v2_receipt` | PASS | PASS | PASS | PASS |
| 20 / 15 / 10 / 5 Hz @ 0 ms | silicon | PASS | PASS | PASS | PASS |
| 20 Hz + 25 ms (actual 32 ms) | silicon | PASS | PASS | PASS | PASS |
| 20 Hz + 50 ms (actual 64 ms) | silicon | PASS | PASS | PASS | PASS |
| 20 Hz + 100 ms (actual 96 ms) | silicon | FAIL | FAIL | PASS | PASS |
| 20 Hz + 200 ms (actual 192 ms) | silicon | FAIL | FAIL | FAIL | FAIL |
| 5 Hz + 50 ms corner (actual 64 ms) | `r5_d50 silicon` | FAIL | FAIL | PASS | PASS |
| 10 Hz + 25 ms | aborted | `NOT_COMPLETED` | — | — | — |

L40 complete-cell table (HOST JSON, cadence CLOSED) matches these verdicts: Q1 Spearman 0.832 / 0.707 / 0.644 / 0.567 / 0.414 at 0 ms; 20 Hz+50 ms Q1 0.402; corner Q1 0.245.

Captain close on the receipt: `PASS — cadence silicon closed; no further cells; no 8 s loop`.

## What this file is not

- Not C1 `LGP_PERCEPTUAL_VALIDATED`.
- Not a student I/O freeze (`student_freeze=false`; SELECTION_GATE still open).
- Not a licence to assume 5 Hz **and** 50 ms together.
- Not a second silicon run. Cadence **CLOSED**. Do not run `scripts/gate_c0_cadence_silicon.py`.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:grok | Created. IN_WORKSPACE copy of C0V2_RESULT + CADENCE_RESULT; Cadence CLOSED; SHA-256 uncomputed this SSA. |
| 2026-08-31 | agent:grok | SHA-256 filled from on-disk bytes. No USB. |
