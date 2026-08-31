---
abstract: "L40 HOST table of complete cadence cell JSONs. Cadence CLOSED. Do not reopen cells."
---
# L40 — cadence cell JSON table
STATUS: TABLE. Cadence CLOSED. Do not reopen cells.
CLAIM: Ten complete cells (`*_partial.json` skipped). Rate 31.25/20/15/10/5 Hz @ 0 ms all PASS. Delay at 20 Hz: 25/50 ms PASS; 100 ms FAIL (Q1); 200 ms FAIL (Q1+Q2+Q3). Corner 5 Hz+50 ms FAIL (Q1). Min useful rate 5 Hz (0 ms). Max added delay 50 ms (at 20 Hz).
EVIDENCE: `artifacts/gate_c0_cadence_silicon/cells/*.json` (complete only). Identity chip `9087A500` git `349d3cd4`. Q1 = `median_spearman_pos_gain`. Frac = `fraction_of_c0v2`.
COMMAND: none — HOST JSON read. Do not run `gate_c0_cadence_silicon.py`. Do not play `holdout_8s_loop.wav`. Do not flash. No USB.
METHOD_RISK: Gate uses requested delay; JSON hop-rounds (25→32, 50→64, 100→96, 200→192 ms). Q1 tight at 5 Hz (0.414) and 20 Hz+50 ms (0.402) vs ≥0.40. Not a reopen.
NEXT: Leave cadence closed. C1 LGP on product firmware, one Captain-chosen full song, no 8 s loop.

| file | family | rate_hz | req_ms | actual_ms | hops | source | verdict | status | Q1 | Q2 | Q3 | n | Q1 spearman | Q2 wins | frac_c0v2 |
| --- | --- | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | ---: | ---: | --- | ---: |
| r31.25_d0.json | rate | 31.25 | 0 | 0 | 0 | c0v2_receipt | PASS | PASS | PASS | PASS | PASS | 10 | 0.832 | 9/9 | 1.000 |
| r20_d0.json | rate | 20 | 0 | 0 | 0 | silicon | PASS | PASS | PASS | PASS | PASS | 10 | 0.707 | 9/9 | 0.859 |
| r15_d0.json | rate | 15 | 0 | 0 | 0 | silicon | PASS | PASS | PASS | PASS | PASS | 10 | 0.644 | 9/9 | 0.793 |
| r10_d0.json | rate | 10 | 0 | 0 | 0 | silicon | PASS | PASS | PASS | PASS | PASS | 10 | 0.567 | 9/9 | 0.842 |
| r5_d0.json | rate | 5 | 0 | 0 | 0 | silicon | PASS | PASS | PASS | PASS | PASS | 10 | 0.414 | 8/9 | 0.768 |
| r20_d25.json | delay | 20 | 25 | 32 | 1 | silicon | PASS | PASS | PASS | PASS | PASS | 10 | 0.536 | 9/9 | 0.879 |
| r20_d50.json | delay | 20 | 50 | 64 | 2 | silicon | PASS | PASS | PASS | PASS | PASS | 10 | 0.402 | 8/9 | 0.608 |
| r20_d100.json | delay | 20 | 100 | 96 | 3 | silicon | FAIL | BINDING_FAIL | FAIL | PASS | PASS | 10 | 0.368 | 7/9 | 0.478 |
| r20_d200.json | delay | 20 | 200 | 192 | 6 | silicon | FAIL | BINDING_FAIL | FAIL | FAIL | FAIL | 10 | 0.242 | 6/9 | 0.159 |
| r5_d50.json | corner | 5 | 50 | 64 | 2 | silicon | FAIL | BINDING_FAIL | FAIL | PASS | PASS | 10 | 0.245 | 8/9 | 0.407 |

Skipped `_partial` (not verdicts): `r5_d0_partial.json`, `r5_d50_partial.json`, `r10_d25_partial.json` (aborted 6/10), `r15_d0_partial.json`, `r20_d0_partial.json`, `r20_d25_partial.json`, `r20_d50_partial.json`, `r20_d100_partial.json`, `r20_d200_partial.json`.
---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:grok | L40: ten complete cell verdicts tabulated; Cadence CLOSED. |
| 2026-08-31 | agent:grok | L40: re-derived ten complete cells from JSON; Cadence CLOSED. |
