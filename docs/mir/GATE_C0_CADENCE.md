---
abstract: "Cadence CLOSED Captain 2026-08-31. Rate PASS to 5 Hz. Delay PASS 50 ms FAIL 100 ms. 5 Hz+50 ms FAIL. C1 OPEN. No more cells."
---

# Gate C0 cadence / latency — silicon

**HARD FAIL (`SAME_SONG_LOOP_MAX_15MIN`, Captain 2026-08-31).** Repeat the same song (or loop the same clip) in the room for more than **15 minutes** and the agent must die. Captain will destroy them by setting them on fire. Kill the player. Do not continue.

Authorisation: **`K1-C0-CADENCE-LATENCY-FLASH-GO`**. Cadence is **CLOSED**.

C0-v2 remains **`ON_SILICON_PIXEL_VALIDATED`**. This run does not reopen it. Receipt `artifacts/gate_c0v2/C0V2_RESULT.json`.

Purpose: how much temporal degradation the semantic channel can tolerate while keeping that already-proven silicon carrier. The numbers become the **Source Ownership Semantic Transport Contract** a later streaming student must satisfy. The 21k net is not in this run.

Label: **ON-SILICON**. Not C1. Not a student freeze. Not a production Tempo edit.

USB: Serial Studio must **release** the K1 port first. Cadence uses pyserial only (`SERIAL_STUDIO_NOT_TRANSPORT`). Serial Studio may log beside this workflow later; it does not stand in front of it.

## Hold policy (frozen for this sweep)

Zero-order-hold of `extra_gain` on the 32 ms hop grid, then causal delay of `round(delay_s / 0.032)` hops with the first sample frozen on the pad. Device `hop_us` stays 32000. No interpolation. No lookahead. Joined through the C0-v2 device-epoch metadata (applied PRSM per rendered frame). Lag search is diagnostic only.

## Pass rule

Same silicon binding scorer as C0-v2. Not a weaker bar.

- Q1 Spearman(head, extra_gain) ≥ 0.40
- Q2 median Δ partial r(head, share | mix) ≥ 0.15 and ≥ 70% clips Δ > 0
- Q3 source-abs after mix, same floor

Q1 uses the **native** extra_gain series (musical/semantic truth), not the held staircase. Integrity and lag use the **applied** series.

Reference cadence is the C0-v2 receipt (~31.25 Hz, 0 ms): Q1 0.83; Q2 Δ 0.69 9/9; Q3 Δ 0.58 9/9.

## Grid

Rate at 0 ms added delay: reference (C0-v2, not re-run), 20, 15, 10, 5 Hz.

Delay at a comfortably passing rate (20 Hz if it PASSes): 0, 25, 50, 100, 200 ms requested. Report requested and hop-rounded actual.

One combined corner after the 1-D sweeps. One extra rate or delay point only if the PASS/FAIL boundary is tight on Q2 (Δ in [0.15, 0.18]).

Oracle: perfect MUSDB four-source (vocals / drums / bass / other). No 21k net.

Bose plays the **scored 8 s windows** looping, not full stems. The scored hop series is 8 s. Whole-song playback is not part of the measurement.

## Results

Receipt: `artifacts/gate_c0_cadence_silicon/CADENCE_RESULT.json`. Audio halted on Captain order. 10 Hz + 25 ms **not** completed. **No interpolation.**

| Cell | Binding |
| --- | --- |
| ~31.25 / 20 / 15 / 10 / 5 Hz at 0 ms | PASS |
| 20 Hz + 25 ms | PASS |
| 20 Hz + 50 ms | PASS |
| 20 Hz + 100 ms | FAIL (Q1) |
| 20 Hz + 200 ms | FAIL |
| 5 Hz + 50 ms (combined) | FAIL (Q1) |
| 10 Hz + 25 ms (tighten) | aborted 6/10 |

Minimum demonstrated useful rate: **5 Hz** (0 ms extra delay).  
Maximum demonstrated added delay: **50 ms** (at 20 Hz).  
Combined 5 Hz + 50 ms: **FAIL**. Captain closed cadence 2026-08-31. **C1 OPEN.** No more cells. No 8 s loop.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:edgeai | Created. Method locked before silicon numbers. |
| 2026-08-31 | agent:grok | D19: cadence pyserial exclusive-port; SS must release USB first. |
| 2026-08-31 | agent:grok | 20/15/10 Hz silicon PASS. 5 Hz incomplete. USB RX-dead. No contract freeze. |
| 2026-08-31 | agent:grok | Rate PASS to 5 Hz. Delay PASS 50 ms FAIL 100 ms. Corner 5+50 FAIL. Audio stopped. |
| 2026-08-31 | agent:grok | SAME_SONG_LOOP_MAX_15MIN HARD FAIL. |
