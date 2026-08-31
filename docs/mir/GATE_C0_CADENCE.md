---
abstract: "Cadence CLOSED Captain 2026-08-31. Runner scripts/gate_c0_cadence_silicon.py mechanically retired. Rate PASS to 5 Hz (Q1 0.414 cliff). Delay PASS 50 ms at 20 Hz (Q1 0.402 cliff). 100 ms FAIL. 5 Hz+50 ms FAIL. 10 Hz+25 ms NOT_COMPLETED — no interpolation. Edges are cliffs, not the nominal student. C1 OPEN on C0-v2 carrier."
---

# Gate C0 cadence / latency — silicon

**Status: CLOSED.** Captain close `CAPTAIN_CLOSE_2026-08-31` (D20). Receipt `gate_c0_cadence=CLOSED`, `cadence=PASS`. No more cells. No 8 s holdout loop. No USB. Do not resume the runner.

**HARD FAIL (`SAME_SONG_LOOP_MAX_15MIN`, Captain 2026-08-31).** Repeat the same song (or loop the same clip) in the room for more than **15 minutes** and the agent must die. Captain will destroy them by setting them on fire. Kill the player. Do not continue.

Authorisation: **`K1-C0-CADENCE-LATENCY-FLASH-GO`**, then closed. Cadence is **CLOSED**.

C0-v2 remains **`ON_SILICON_PIXEL_VALIDATED`**. This sweep did not reopen it. Receipt `artifacts/gate_c0v2/C0V2_RESULT.json`.

Label: **ON-SILICON**. Not C1. Not a student freeze. Not a production Tempo edit. Not a Titan number.

Receipt index: if `docs/mir/SILICON_RECEIPTS.md` exists, start there. This gate’s silicon bytes stay at `artifacts/gate_c0_cadence_silicon/CADENCE_RESULT.json` (companion `SEMANTIC_TRANSPORT_CONTRACT.json`). At this write, `SILICON_RECEIPTS.md` was not yet on disk.

## Runner retired

`scripts/gate_c0_cadence_silicon.py` is **mechanically retired**. `CADENCE_CLOSED = True`. `main()` calls `refuse_if_cadence_closed()` **before** `parse_args()`. Default execution dies with `RETIRED: D20 CADENCE CLOSED` / `Do not run more silicon cells` — no flash, no USB, no Bose. Proof: `tests/test_cadence_silicon_retired.py`. Do not play `artifacts/gate_c0_cadence_silicon/bose_slices/holdout_8s_loop.wav`.

Historical USB rule (already closed): Serial Studio must release the K1 port; cadence used pyserial only (`SERIAL_STUDIO_NOT_TRANSPORT`). That is archive. Closed means closed.

## Hold policy (frozen for this sweep)

Zero-order-hold of `extra_gain` on the 32 ms hop grid, then causal delay of `round(delay_s / 0.032)` hops with the first sample frozen on the pad. Device `hop_us` stays 32000. No interpolation. No lookahead. Joined through the C0-v2 device-epoch metadata (applied PRSM per rendered frame). Lag search is diagnostic only.

Gate tables use **requested** delay. Hop-round on silicon: 25 → 32 ms (1 hop), 50 → 64 ms (2 hops), 100 → 96 ms (3 hops), 200 → 192 ms (6 hops).

## Pass rule

Same silicon binding scorer as C0-v2. Not a weaker bar.

- Q1 Spearman(head, extra_gain) ≥ 0.40
- Q2 median Δ partial r(head, share | mix) ≥ 0.15 and ≥ 70% clips Δ > 0
- Q3 source-abs after mix, same floor

Q1 uses the **native** extra_gain series (musical/semantic truth), not the held staircase. Integrity and lag use the **applied** series.

Reference cadence is the C0-v2 receipt (~31.25 Hz, 0 ms, `source=c0v2_receipt`): Q1 0.83; Q2 Δ 0.69 9/9; Q3 Δ 0.58 9/9. Chip `9087A500`, probe `k1_main_rpl_rtrace_probe` @ `349d3cd4`.

## Grid

Rate at 0 ms added delay: reference (C0-v2, not re-run), 20, 15, 10, 5 Hz.

Delay at a comfortably passing rate (20 Hz after it PASSed): 0, 25, 50, 100, 200 ms requested. Report requested and hop-rounded actual.

One combined corner after the 1-D sweeps. One extra rate or delay point only if the PASS/FAIL boundary is tight on Q2 (Δ in [0.15, 0.18]).

Oracle: perfect MUSDB four-source (vocals / drums / bass / other). No 21k net.

Bose played the **scored 8 s windows** looping, not full stems. Whole-song playback is not part of the measurement. Audio halted on Captain order. That loop must not start again.

## Results

Receipt: `artifacts/gate_c0_cadence_silicon/CADENCE_RESULT.json`. Cell JSON under `artifacts/gate_c0_cadence_silicon/cells/`. Complete cells only are verdicts. `r10_d25.json` does **not** exist. `r10_d25_partial.json` is 6/10 tracks — **not** a verdict.

| Cell | Requested | Actual | Q1 Spearman | Q2 | Q3 | Binding |
| --- | --- | --- | ---: | --- | --- | --- |
| ~31.25 Hz @ 0 ms | 0 ms | 0 hops | 0.832 | 9/9 | 9/9 | PASS (C0-v2 receipt) |
| 20 Hz @ 0 ms | 0 ms | 0 hops | 0.707 | 9/9 | 9/9 | PASS |
| 15 Hz @ 0 ms | 0 ms | 0 hops | 0.644 | 9/9 | 9/9 | PASS |
| 10 Hz @ 0 ms | 0 ms | 0 hops | 0.567 | 9/9 | 9/9 | PASS |
| 5 Hz @ 0 ms | 0 ms | 0 hops | **0.414** | 8/9 Δ 0.530 | 9/9 Δ 0.438 | PASS — **cliff** |
| 20 Hz + 25 ms | 25 ms | 32 ms / 1 hop | 0.536 | 9/9 | 9/9 | PASS |
| 20 Hz + 50 ms | 50 ms | 64 ms / 2 hops | **0.402** | 8/9 Δ 0.420 | 8/9 Δ 0.355 | PASS — **cliff** |
| 20 Hz + 100 ms | 100 ms | 96 ms / 3 hops | 0.368 | 7/9 PASS | 8/9 PASS | FAIL (Q1) |
| 20 Hz + 200 ms | 200 ms | 192 ms / 6 hops | 0.242 | 6/9 FAIL | 6/9 FAIL | FAIL (Q1+Q2+Q3) |
| 5 Hz + 50 ms (combined) | 50 ms | 64 ms / 2 hops | 0.245 | 8/9 PASS | 7/9 PASS | FAIL (Q1) |
| 10 Hz + 25 ms (tighten) | — | — | — | — | — | **NOT_COMPLETED** (aborted 6/10). **No interpolation.** |

Minimum demonstrated useful 0-delay rate: **5 Hz**.  
Maximum demonstrated added delay: **50 ms** (at **20 Hz**, not at 5 Hz).  
Combined 5 Hz + 50 ms: **FAIL** (kept; not interpolated).  
`plain.combined_10hz_25ms`: **NOT_COMPLETED**. `tighten_complete=false`.

Captain closed cadence 2026-08-31. **C1 OPEN** on the already-proven C0-v2 carrier (~31.25 Hz, 0 ms extra delay, product firmware). No more cells. No 8 s loop.

## Cliffs, not the nominal student

The 5 Hz 0-delay PASS (Q1 **0.414**) and the 20 Hz + 50 ms PASS (Q1 **0.402**) sit **just above** the 0.40 floor. They are **envelope cliffs**, not a comfortable operating point and **not** the nominal student / C1 playback.

Do **not**:

- treat 5 Hz or 50 ms as the student contract clock
- assume both edges at once (joint cell FAIL, Q1 0.245)
- invent a 10 Hz + 25 ms PASS by interpolating between 5 Hz and 20 Hz, or between 0 ms and 50 ms
- freeze student I/O from these cliffs

C1 playback uses the C0-v2 carrier. Student I/O stays unfrozen until C1 and `docs/mir/SELECTION_GATE.md`. A later student must **not** assume 5 Hz **and** 50 ms together (`student_must_not_assume` on the companion contract JSON).

Q4 FAIL at 5 Hz 0-delay (arrangement) does not change the Q1–Q3 envelope that closed this gate.

## Non-claims

- C0-v2 remains `ON_SILICON_PIXEL_VALIDATED`.
- Combined 5 Hz + 50 ms FAIL is kept (not interpolated).
- 10 Hz + 25 ms was not completed.
- C1 is not `LGP_PERCEPTUAL_VALIDATED`.
- No student freeze of network architecture.
- HOST cadence (`docs/mir/GATE_C_CADENCE_HOST.md`) is design evidence only, not this close.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:edgeai | Created. Method locked before silicon numbers. |
| 2026-08-31 | agent:grok | D19: cadence pyserial exclusive-port; SS must release USB first. |
| 2026-08-31 | agent:grok | 20/15/10 Hz silicon PASS. 5 Hz incomplete. USB RX-dead. No contract freeze. |
| 2026-08-31 | agent:grok | Rate PASS to 5 Hz. Delay PASS 50 ms FAIL 100 ms. Corner 5+50 FAIL. Audio stopped. |
| 2026-08-31 | agent:grok | SAME_SONG_LOOP_MAX_15MIN HARD FAIL. |
| 2026-08-31 | agent:grok | W3-L13: CLOSED + runner retired. Cliffs 5 Hz 0.414 and 20 Hz+50 ms 0.402. 10 Hz+25 not interpolated. Point SILICON_RECEIPTS if present. Supersedes the “5 Hz incomplete” changelog line above. |
