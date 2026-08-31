---
abstract: "L18: CADENCE_RESULT.json cell verdicts match GATE_C0_CADENCE.md Results and AGENTS.md CLOSED. No interpolation of aborted 10 Hz+25. Cadence CLOSED."
---

# L18 — CADENCE_RESULT vs GATE_C0_CADENCE vs AGENTS.md

STATUS: MATCH. Cadence CLOSED. Do not reopen cells.

CLAIM: Receipt, `docs/mir/GATE_C0_CADENCE.md` Results, and `AGENTS.md` lane status agree. Rate 31.25/20/15/10/5 Hz @ 0 ms PASS. Delay at 20 Hz: 25/50 ms PASS; 100 ms FAIL; 200 ms FAIL. Corner 5 Hz+50 ms FAIL. 10 Hz+25 ms aborted 6/10 — **not interpolated**. Min useful 0-delay rate 5 Hz. Max added delay 50 ms at 20 Hz. Student must not assume 5 Hz and 50 ms together. C1 OPEN on the C0-v2 carrier. AGENTS.md does not restate the Hz/ms table; it correctly marks Cadence silicon **CLOSED** and C1 **OPEN**.

EVIDENCE: `artifacts/gate_c0_cadence_silicon/CADENCE_RESULT.json` (`cadence=PASS`, `gate_c0_cadence=CLOSED`, `cadence_close=CAPTAIN_CLOSE_2026-08-31`, `plain.combined_10hz_25ms=NOT_COMPLETED`); `docs/mir/GATE_C0_CADENCE.md` Results; `AGENTS.md` Source oracle + Cadence silicon rows; `artifacts/gate_c0_cadence_silicon/cells/r10_d25_partial.json` (6 `"track"` objects).

COMMAND: none — docs-only. Do not run `gate_c0_cadence_silicon.py`. Do not play `holdout_8s_loop.wav`. Do not flash. No USB.

METHOD_RISK: Gate Results use **requested** delay; JSON hop-rounds 25→32, 50→64, 100→96, 200→192 ms. Q1 is tight at 5 Hz (0.414) and 20 Hz+50 ms (0.402) vs ≥0.40. 200 ms FAIL is Q1+Q2+Q3 (GATE table omits the Q split; 100 ms and the corner name Q1). GATE changelog still contains a superseded “5 Hz incomplete” line; the Results section supersedes it. `CADENCE_RESULT.json` `contract.status` is still `PROPOSED` (L03 owns that vs the MD freeze). Do not treat the aborted 10 Hz+25 partial as a verdict. Not a reopen.

NEXT: Leave cadence closed. C1 LGP on product firmware, one Captain-chosen full song, no 8 s loop.

## Cell matrix (receipt → GATE Results)

| Cell | Receipt verdict | GATE_C0_CADENCE.md | AGENTS.md |
| --- | --- | --- | --- |
| 31.25 Hz @ 0 ms | PASS (`source=c0v2_receipt`, Q1 0.832) | PASS (bundled 0 ms row) | (no Hz table; Cadence CLOSED) |
| 20 Hz @ 0 ms | PASS (Q1 0.707) | PASS | same |
| 15 Hz @ 0 ms | PASS (Q1 0.644) | PASS | same |
| 10 Hz @ 0 ms | PASS (Q1 0.567) | PASS | same |
| 5 Hz @ 0 ms | PASS (Q1 0.414, Q2 8/9) | PASS | same |
| 20 Hz + 25 ms | PASS (actual 32 ms) | PASS | same |
| 20 Hz + 50 ms | PASS (actual 64 ms, Q1 0.402) | PASS | same |
| 20 Hz + 100 ms | FAIL (Q1; Q2/Q3 PASS; actual 96 ms) | FAIL (Q1) | same |
| 20 Hz + 200 ms | FAIL (Q1+Q2+Q3; actual 192 ms) | FAIL | same |
| 5 Hz + 50 ms | FAIL (Q1; Q2/Q3 PASS) | FAIL (Q1) | same |
| 10 Hz + 25 ms | `NOT_COMPLETED` / `tighten_complete=false` | aborted 6/10 | no reopen |

Envelope: `slowest_passing_rate_hz=5.0`; `largest_passing_delay_s=0.05`; `plain.combined_5hz_50ms=FAIL`; interpolation none.

## AGENTS.md (status, not a second results table)

- Cadence silicon: **CLOSED — do not reopen**. Matches `gate_c0_cadence=CLOSED`.
- Source oracle: C0-v2 `ON_SILICON_PIXEL_VALIDATED`. Cadence CLOSED. C1 OPEN. Matches `c0v2` + `c1`.
- HARD FAIL `SAME_SONG_LOOP_MAX_15MIN`. Matches GATE header.
- No USB multiplex / no 8 s loop. Matches Captain close.

## Out of this lane

L03: JSON `contract.status=PROPOSED` vs MD `FROZEN_FOR_C1`. L04: student must-not-assume 5+50. L22: `GATE_C.md` body still carries the two-clock corpse and the pre-silicon 2/5/10/20/~31 × 0/50/100/200 grid — that is not the cadence Results table. L40: complete cell JSON table.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:grok | L18: receipt vs GATE_C0_CADENCE match; CLOSED. |
| 2026-08-31 | agent:grok | L18: re-derived cells vs GATE Results + AGENTS.md; 10 Hz+25 not interpolated. |
