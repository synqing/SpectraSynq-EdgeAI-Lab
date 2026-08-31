---
abstract: "L18 docs-only: CADENCE_RESULT.json matches GATE_C0_CADENCE.md. Cadence CLOSED. Do not reopen cells."
---
# L18 — CADENCE_RESULT vs GATE_C0_CADENCE
STATUS: MATCH. Cadence CLOSED. Do not reopen cells.
CLAIM: Receipt equals gate table. Rate 31.25/20/15/10/5 Hz @ 0 ms PASS. Delay at 20 Hz: 25/50 ms PASS; 100 ms FAIL (Q1); 200 ms FAIL (Q1+Q2+Q3). Corner 5 Hz+50 ms FAIL (Q1). 10 Hz+25 ms aborted 6/10 (`r10_d25_partial.json`). Min useful rate 5 Hz (0 ms). Max added delay 50 ms (at 20 Hz). No interpolation. Student must not assume 5 Hz and 50 ms together. C1 OPEN on C0-v2 carrier.
EVIDENCE: `artifacts/gate_c0_cadence_silicon/CADENCE_RESULT.json` (`cadence=PASS`, `gate_c0_cadence=CLOSED`, `cadence_close=CAPTAIN_CLOSE_2026-08-31`); `docs/mir/GATE_C0_CADENCE.md` Results; `cells/r10_d25_partial.json` (6 tracks).
COMMAND: none — docs-only. Do not run `gate_c0_cadence_silicon.py`. Do not play `holdout_8s_loop.wav`. Do not flash. No USB.
METHOD_RISK: Gate table uses requested delay; JSON hop-rounds (25→32, 50→64, 100→96, 200→192 ms). Q1 tight at 5 Hz (0.414) and 20 Hz+50 ms (0.402) vs ≥0.40. Not a reopen.
NEXT: Leave cadence closed. C1 LGP on product firmware, one Captain-chosen full song, no 8 s loop.
---
**Document Changelog**
| Date | Author | Change |
| 2026-08-31 | agent:grok | L18: receipt vs GATE_C0_CADENCE match; CLOSED. |
