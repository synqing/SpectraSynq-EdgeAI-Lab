---
abstract: "HISTORICAL CLOSE-STATE. C0-v2 PASS 2026-08-31: source_share × WaveformTempo × head_position = ON_SILICON_PIXEL_VALIDATED. Timing self-test PASS. No lag correction. Cadence CLOSED (D20). C1 OPEN. This file is not cadence/C1 authority. Do not reopen cells. Two-clock C0 corpse still FAIL. Product restored acaecaa8 im69d."
---

# HISTORICAL / C0-v2 CLOSE-STATE

```text
╔══════════════════════════════════════════════════════════════════╗
║  HISTORICAL RECORD — C0-v2 CLOSE-STATE — NOT LIVE AUTHORITY      ║
║                                                                  ║
║  This file records the 2026-08-31 C0-v2 PASS moment.             ║
║  Stamp: ON_SILICON_PIXEL_VALIDATED                               ║
║                                                                  ║
║  It is NOT current cadence authority.                            ║
║  It is NOT current C1 authority.                                 ║
║  Do NOT reopen cadence cells. Do NOT loop the 8 s holdout.       ║
║                                                                  ║
║  Cadence silicon: CLOSED  (D20, 2026-08-31)                      ║
║    → docs/mir/GATE_C0_CADENCE.md                                 ║
║    → artifacts/gate_c0_cadence_silicon/CADENCE_RESULT.json       ║
║                                                                  ║
║  C1 LGP: OPEN                                                    ║
║    → docs/mir/GATE_C1.md                                         ║
║                                                                  ║
║  Programme wrapper: docs/mir/GATE_C.md                           ║
╚══════════════════════════════════════════════════════════════════╝
```

**HARD FAIL (`SAME_SONG_LOOP_MAX_15MIN`, Captain 2026-08-31).** Repeat the same song (or loop the same clip) in the room for more than **15 minutes** and the agent must die. Captain will destroy them by setting them on fire. Kill the player. Do not continue.

---

## 1. What this file is

The frozen close of **Gate C0-v2**: one device-epoch silicon run that proved the already-HOST-passed binding on Main RPL LED dumps.

```text
source_share × WaveformTempo × head_position = ON_SILICON_PIXEL_VALIDATED
```

Receipt: [`artifacts/gate_c0v2/C0V2_RESULT.json`](../../artifacts/gate_c0v2/C0V2_RESULT.json)  
Runner (historical; do not re-run): `scripts/gate_c0v2_silicon.py`  
Scorer: `src/edgeai/mir/p3c_quant.py` (`score_clip` + `summarise`)

Read this file when you need the **pixel stamp**, the device-epoch invariant, or why the two-clock C0 corpse is not the live C0 close.

## 2. What this file is not

| This file is not | Go here instead |
| --- | --- |
| Cadence / latency silicon authority | [GATE_C0_CADENCE.md](GATE_C0_CADENCE.md) · D20 in [DECISIONS.md](../DECISIONS.md) |
| C1 LGP perceptual protocol | [GATE_C1.md](GATE_C1.md) — **OPEN** |
| Semantic transport contract (5 Hz / 50 ms) | [SEMANTIC_TRANSPORT_CONTRACT.md](SEMANTIC_TRANSPORT_CONTRACT.md) |
| Programme Gate C wrapper | [GATE_C.md](GATE_C.md) |
| Two-clock C0 inject recon | [GATE_C0_SILICON_PATH.md](GATE_C0_SILICON_PATH.md) — corpse path, retired |
| A licence to re-flash the probe, reopen cells, or play `holdout_8s_loop.wav` | **Forbidden.** Cadence CLOSED. No USB from this file. |

Receipt-time JSON still carries `"cadence": "OPEN — not this run"` and `"c1": "blocked until ON_SILICON_PIXEL_VALIDATED"`. Those strings describe **this run's non-claims at close**, not the live programme. Live programme after D20: **cadence CLOSED, C1 OPEN.** Do not execute those receipt fields as a task list.

---

## 3. Close record — 2026-08-31 silicon PASS

**Verdict:** `c0v2 = PASS`  
**Stamp:** `source_share × WaveformTempo × head_position = ON_SILICON_PIXEL_VALIDATED`  
**Lag correction:** `lag_corrected: false` (authority). Diagnostic lag search did not promote the score.  
**Retired C0 untouched:** `retired_c0_untouched: true`

### 3.1 Holdout Q1–Q3 (n=10; authority)

Same floors as HOST P3-C. Thresholds were not moved after silicon. Holdout is the close. C0-v2 `native.challenge` is empty (`n_clips: 0`) — ignore its FAIL labels.

| Gate | Floor | Silicon holdout | Verdict |
| --- | --- | --- | --- |
| Q1 Spearman(head_position, extra_gain) | ≥ 0.40 | **0.832** (`median_spearman_pos_gain` 0.8318621417942687) | **PASS** |
| Q2 median Δ partial r(head, share \| mix) | ≥ 0.15 and ≥ 70% clips Δ > 0 | **Δ 0.690** **9/9** (B 0.160 vs D 0.844) | **PASS** |
| Q3 source-abs after mix, same floor | same | **Δ 0.585** **9/9** | **PASS** |

HOST P3-C holdout (`docs/mir/P3C_QUANT.json`, n=10) was Q1 0.677 / Q2 Δ 0.625 9/9 / Q3 Δ 0.451 9/9. Silicon is stronger, not a regression. HOST `all` n=20 is not this close.

Q4 (arrangement) silicon PASS Δ 0.166 9/10 is **out of the C0-v2 stamp**. Q5 (Comet vs loudness at drums) FAIL on both HOST and silicon — parked with `composition_change`.

### 3.2 Timing self-test

`artifacts/gate_c0v2/timing_selftest.json` / receipt `selftest.status = PASS`.

| Check | Value |
| --- | --- |
| integrity | OK |
| dropped F / M | 0 / 0 |
| tick gaps | 0 (max gap 1) |
| `[C0_EPOCH]` markers | 1 |
| applied PRSM mismatches | 0 |
| hop coverage | 1.0 (64/64) |
| frames / inject | 377 / 299 |
| diagnostic lag | best 0 hops; Spearman 0.807; `invalid: false` |
| pipeline_lat | 0 |

0/10 nominal clips timing-invalid.

### 3.3 Device at PASS

| Item | Value |
| --- | --- |
| Role | Main RPL |
| Chip | `9087A500` |
| USB | `B4:3A:45:A5:87:90` |
| Port (that run) | `/dev/cu.usbmodem12201` |
| Probe env | `k1_main_rpl_rtrace_probe` |
| Probe git | `349d3cd4` |
| Probe epoch | `1788135177` |
| Pin | mode ordinal **18** (Waveform Tempo), dense 17, palette **43**, mood 0.65 |
| Bose | Mini II SoundLink, output volume 44, continuous full holdout stems (not the later cadence 8 s loop) |
| Dumps | `artifacts/gate_c0v2/dumps/` (31 log + 31 npz, including timing self-test) |

### 3.4 Product restore after PASS

`IDENTITY OK git=acaecaa8 env=k1_main_rpl_im69d epoch=1788136403`

C1 plays **product** firmware. Do not flash `k1_main_rpl_rtrace_probe` for C1.

---

## 4. Why C0-v2 existed

Previous C0 (`artifacts/gate_c0/`) stays **FAIL — INVALID TEMPORAL EXECUTION**. Do not rescore it with +14 hops. Do not overwrite those dumps.

The two-clock runner `scripts/gate_c0_silicon.py` is **retired**. It armed rtrace and streamed PRSM on independent host clocks. That permitted `capture epoch ≠ injection epoch` (~0.5 s). Holdout n=10: Q1 **0.13** FAIL; Q2/Q3 **6/9** FAIL. Silicon was not dead. Post-hoc +14 hops (~448 ms) recovers host-like Q1–Q3 — **diagnosis only, not a PASS, never an authority rescore.**

C0-v2 is the successor method. Same binding. Same scorer. One device epoch.

| | Two-clock C0 (corpse) | C0-v2 (this close) |
| --- | --- | --- |
| Receipt | `artifacts/gate_c0/C0_RESULT.json` | `artifacts/gate_c0v2/C0V2_RESULT.json` |
| Verdict | `c0=FAIL` `INVALID_TEMPORAL_EXECUTION` | `c0v2=PASS` |
| Stamp | `not ON_SILICON_PIXEL_VALIDATED` | `ON_SILICON_PIXEL_VALIDATED` |
| Probe git | `acaecaa8` | `349d3cd4` |
| Chip | `9087A500` | `9087A500` |
| Q1 / Q2 / Q3 | 0.13 FAIL; Δ 0.17 6/9; Δ 0.19 6/9 | 0.83 PASS; Δ 0.69 9/9; Δ 0.58 9/9 |
| Timing | two host clocks | one device epoch; lag 0 |

---

## 5. Frozen method (how the PASS was earned)

Do not re-run this method unless a later Captain GO names a new silicon inject. Cadence CLOSED is not a reopen of this harness.

### 5.1 Invariant

Injection and capture share one authoritative **device-side epoch**.

The scorer reads from the dump, for each rendered frame:

- rtrace frame index
- device monotonic `us` and render tick
- `c0_epoch_id`
- frames since epoch
- condition id
- semantic sample index
- **actual PRSM pressure applied to this frame**
- injection-active

No host sleep, no guessed startup latency, no post-hoc hop search as authority.

No `[C0_EPOCH]` marker → `INVALID_RUN`.

A diagnostic lag search exists only as an error detector. If best-fit lag materially disagrees with declared metadata, the run is **INVALID_RUN**. It must never silently correct the score.

### 5.2 Probe-only firmware

Atlas worktree branch `probe/c0-epoch-v2`. Flag `K1_C0_EPOCH_V1` on `k1_main_rpl_rtrace_probe` only.

Preload extra_gain as u16 → `:c0_run` arms rtrace, preroll, stamps epoch on a VP frame, replays the trace, post-roll, halt, dump.

Waveform Tempo source is not edited. Competing mic `waveform_peak_scaled` is held at 0 only while C0 owns the snapshot.

Hex preload uses **32-character** chunks (128-char chunks `HEX FAIL: parse`). That is operational history, not a reason to inject again.

### 5.3 Result states

| State | Meaning |
| --- | --- |
| PASS | Timing valid and Q1–Q3 pass. Stamp `ON_SILICON_PIXEL_VALIDATED`. **This is the 2026-08-31 close.** |
| BINDING_FAIL | Timing valid, source-share carrier fails the existing bars. |
| INVALID_RUN | Marker missing, drops, sequence mismatch, lag detector trip. Not a binding fail. |

The two-clock C0 is this last class, while keeping its official C0 FAIL stamp.

---

## 6. Live programme after this close (do not execute from this file)

Order that actually happened:

```text
C0-v2 PASS (this file)
    → cadence/latency silicon (GATE_C0_CADENCE.md) → Captain D20 CLOSE
    → transport contract frozen for C1
    → C1 LGP OPEN (GATE_C1.md)
```

**Cadence silicon is CLOSED** (Captain 2026-08-31, D20). Envelope, for pointer only — authority is [GATE_C0_CADENCE.md](GATE_C0_CADENCE.md):

```text
slowest 0-delay PASS: 5 Hz
largest added delay PASS: 50 ms at 20 Hz
5 Hz + 50 ms together: FAIL
10 Hz + 25 ms: NOT COMPLETED — do not interpolate
```

Do **not** reopen cells. Do **not** play `artifacts/gate_c0_cadence_silicon/bose_slices/holdout_8s_loop.wav`.

**C1 is OPEN.** Playback uses this C0-v2 carrier (~31.25 Hz, 0 ms extra delay) on **product firmware**. Captain looks at **one full song he chooses**. Dumps do not answer C1. Stamp `LGP_PERCEPTUAL_VALIDATED` only after the three LGP questions in [GATE_C1.md](GATE_C1.md).

Student I/O still unfrozen. No new net. No Titan from this file.

---

## 7. Ship path

1. **Already on silicon / in source:** C0-v2 `PASS` / `ON_SILICON_PIXEL_VALIDATED` 2026-08-31. Receipt `artifacts/gate_c0v2/C0V2_RESULT.json`. Product restored `k1_main_rpl_im69d` @ `acaecaa8`. Cadence 1-D envelope already measured and **CLOSED** (D20). Transport contract frozen for C1.
2. **Remaining:** C1 LGP perceptual on product firmware — one Captain-chosen full song, no 8 s loop, no probe flash, no cadence cells. Then student I/O freeze only if [SELECTION_GATE.md](SELECTION_GATE.md) and C1 still hold.
3. **Who:** Captain is the C1 viewer. Agent does not start the loop, does not flash for C1, does not ask Captain to score LED buffers (dumps already exist for that).
4. **Stamp that means shipped:**
   - C0-v2 (this gate): **already shipped** — `ON_SILICON_PIXEL_VALIDATED` in `C0V2_RESULT.json`.
   - Cadence: **already shipped-closed** — D20 + `CADENCE_RESULT.json` `gate_c0_cadence=CLOSED`.
   - C1: `LGP_PERCEPTUAL_VALIDATED` in [GATE_C1.md](GATE_C1.md) after the look. **Not this file.**

---

## 8. Non-claims (still true)

- Previous C0 is still FAIL `INVALID_TEMPORAL_EXECUTION`
- No Gate C perceptual verdict (`LGP_PERCEPTUAL_VALIDATED` not applied)
- No student I/O freeze
- No Titan, no Demucs-on-device, no product Tempo edit
- This file does not freeze cadence (D20 did)
- This file does not open a new silicon cell

---

## 9. Reading paths

| Reader | Read |
| --- | --- |
| Need the pixel stamp | §3 + `C0V2_RESULT.json` |
| Need why two-clock C0 is dead | §4 + `artifacts/gate_c0/C0_RESULT.json` |
| About to touch cadence | **Stop.** [GATE_C0_CADENCE.md](GATE_C0_CADENCE.md) CLOSED. D20. |
| About to run C1 | [GATE_C1.md](GATE_C1.md) · [HANDOFF.md](../agent/HANDOFF.md) |
| Programme status | [GATE_C.md](GATE_C.md) · [AGENTS.md](../../AGENTS.md) |

USB: none from this document. Audio: none. Cadence cells: **do not reopen.**

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:edgeai | Created. Retire two-clock C0. Device epoch invariant. |
| 2026-08-31 | agent:edgeai | Silicon: self-test PASS, nominal INVALID_RUN (dump drops), product restored. |
| 2026-08-31 | agent:edgeai | Chunked dump re-run PASS ON_SILICON_PIXEL_VALIDATED; product restored acaecaa8. |
| 2026-08-31 | agent:grok | HISTORICAL / C0-v2 CLOSE-STATE banner. Abstract: Cadence CLOSED (D20), C1 OPEN. Not cadence/C1 authority. Do not reopen cells. Receipt-time JSON “cadence OPEN / C1 blocked” labelled non-claims, not live programme. |
