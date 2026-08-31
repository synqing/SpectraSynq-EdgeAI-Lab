---
abstract: "L03: SEMANTIC_TRANSPORT_CONTRACT.md frozen numbers match CADENCE_RESULT + cells. extra_gain [0.62,1.0] is not a cell field. 50 ms is requested (actual 64 ms). Receipt contract.status still PROPOSED. Cadence CLOSED."
---

# L03 — transport contract vs CADENCE_RESULT vs cells

STATUS: MATCH (frozen cadence numbers vs measured cells). Cadence CLOSED. No USB. No audio.

CLAIM: The MD freeze table agrees with `CADENCE_RESULT.json` `plain` / rate / delay / corner and with complete cell JSONs: four-source including `other` is the contract channel list; slowest 0-delay PASS is **5 Hz**; largest passing extra delay at 20 Hz is **50 ms requested**; **5 Hz + 50 ms together FAIL** (Q1); student must not assume both edges. `extra_gain` **[0.62, 1.0]** is frozen in the MD and in `SEMANTIC_TRANSPORT_CONTRACT.json`, not as a numeric field in `CADENCE_RESULT.json` or `cells/*.json`. Receipt `contract.status` is still `PROPOSED`; MD + companion JSON are `FROZEN_FOR_C1`. No docs copy of `CADENCE_RESULT.json`.

EVIDENCE: `docs/mir/SEMANTIC_TRANSPORT_CONTRACT.md`; `artifacts/gate_c0_cadence_silicon/CADENCE_RESULT.json`; `artifacts/gate_c0_cadence_silicon/SEMANTIC_TRANSPORT_CONTRACT.json`; `artifacts/gate_c0_cadence_silicon/cells/{r5_d0,r20_d50,r5_d50,r20_d100,r31.25_d0}.json`. Chip `9087A500` git `349d3cd4`. Floors: Q1 Spearman ≥ 0.40; Q2/Q3 median Δ ≥ 0.15 and ≥ 70% clips Δ > 0 (`docs/mir/GATE_C0_CADENCE.md`).

COMMAND: none run this lane — HOST JSON read. Optional check: `python3 -c "import json,pathlib as P; r=json.loads(P.Path('artifacts/gate_c0_cadence_silicon/CADENCE_RESULT.json').read_text()); print(r['plain']); print(r['contract']['channels'], r['contract']['status']); print([(c['rate_hz'],c['requested_delay_ms'],c['actual_delay_ms'],c['verdict'],c['Q1']) for c in r['rate']['cells']+r['delay']['cells']]); print(r['corner'])"` — do not run `gate_c0_cadence_silicon.py`, flash, USB, or play `holdout_8s_loop.wav`.

METHOD_RISK: Gate uses **requested** delay; hop-round is `round(delay_s/0.032)` so 50 ms → 64 ms (2 hops), 100 ms → 96 ms. Q1 is tight at 5 Hz (0.414) and 20 Hz+50 ms (0.402) vs ≥ 0.40. 5 Hz 0-delay Q4 FAIL does not change the Q1–Q3 envelope. Cell `source_delta_medians` names `vocals_share` only — four-source including `other` is the oracle/contract, not a per-cell other-share column. `extra_gain` range is P3-C mapping, not a cadence verdict. Do not treat `contract.status=PROPOSED` as licence to reopen cells.

NEXT: Leave cadence closed. Do not freeze student I/O. Do not assume 5 Hz and 50 ms together. C1 plays C0-v2 ~31.25 Hz / 0 ms extra on product firmware, one Captain-chosen full song, no 8 s loop.

## Frozen MD row → receipt → cell

| Frozen item (MD) | CADENCE_RESULT | Cell | Match? |
| --- | --- | --- | --- |
| Channels vocals, drums, bass, **other** | `contract.channels` same four; `semantics` “four source powers/shares” | not a cell field; GATE oracle is MUSDB four-source | MATCH (contract, not a cell metric) |
| extra_gain [0.62, 1.0] | absent as numbers; `hold_policy` names extra_gain ZOH | absent (`0.62` not in artefact JSON) | MATCH to `SEMANTIC_TRANSPORT_CONTRACT.json` `range.extra_gain` only — **not a measured cell** |
| Hold sample-and-hold, no interpolation, no lookahead | `hold_policy` ZOH on 32 ms hop; `lag_corrected=false`; `interpolation` none | same `hold_policy` on every complete cell | MATCH (MD omits hop-grid wording) |
| Slowest 0-delay PASS **5 Hz** | `rate.slowest_passing_rate_hz=5.0`; `plain.minimum_demonstrated_useful_rate_hz=5.0`; rate cells 31.25/20/15/10/5 all `verdict=PASS` | `r5_d0.json` rate 5 Hz, delay 0, Q1/Q2/Q3 PASS, Spearman 0.4139, n=10, `n_timing_invalid=0` | MATCH |
| Largest added delay PASS **50 ms at 20 Hz** | `delay.test_rate_hz=20`; `largest_passing_delay_s=0.05`; `plain.maximum_demonstrated_added_delay_s=0.05`; 20 Hz+50 ms Q1–Q3 PASS | `r20_d50.json` requested 50 / actual **64** / 2 hops, verdict PASS, Spearman 0.4025 | MATCH as **requested** ms |
| 5 Hz + 50 ms together **FAIL**; student must not assume both | `plain.combined_5hz_50ms=FAIL`; `corner.verdict=FAIL` Q1 FAIL Q2/Q3 PASS; `non_claims` “kept (not interpolated)” | `r5_d50.json` family=corner, 5 Hz, req 50 / actual 64, `BINDING_FAIL`, Spearman 0.2450 | MATCH |
| 100 ms FAIL at 20 Hz | `plain.Q.20Hz_100ms.Q1=FAIL`; delay cell verdict FAIL | `r20_d100.json` req 100 / actual 96, Q1 FAIL Q2/Q3 PASS | MATCH |
| C1 playback C0-v2 ~31.25 Hz, 0 ms extra | rate cell 31.25 Hz / 0 ms `source=c0v2_receipt` PASS (Spearman 0.832); not duplicated in `plain` | `r31.25_d0.json` | MATCH (carrier exists; C1 LGP not this receipt) |

## Numbers that do **not** match, or are not cell-measured

1. **MD `FROZEN_FOR_C1` vs receipt `contract.status=PROPOSED`.** Companion `SEMANTIC_TRANSPORT_CONTRACT.json` is `FROZEN_FOR_C1`. `plain.captain_close` PASS; `gate_c0_cadence=CLOSED`; `cadence_close=CAPTAIN_CLOSE_2026-08-31`. Cadence is closed either way — do not reopen.
2. **50 ms vs 64 ms.** Frozen “50 ms” is requested delay. Silicon applied **64 ms** (2 hops). Student delay budget in hop units is 2 hops at `hop_us=32000`, not a 50.000 ms wire time.
3. **`plain.combined_10hz_25ms=NOT_COMPLETED`** is omitted from the MD freeze table (aborted 6/10; not interpolated). Envelope does not use it.
4. **`extra_gain` [0.62, 1.0]** is not scored as a cell; it is the P3-C map the hold policy applies. Do not invent a silicon measurement of those bounds from cadence cells.

Envelope the student may consume: four-source including `other`; extra_gain in [0.62, 1.0] (from contract JSON, not cells); 5 Hz 0-delay PASS; 50 ms extra at 20 Hz PASS (64 ms applied); **not both at once**.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:grok | L03: CADENCE_RESULT plain vs MD; CONFLICT on freeze/units/extra_gain. |
| 2026-08-31 | agent:grok | L03: re-derived MD freeze vs CADENCE_RESULT + complete cells; cadence numbers MATCH; extra_gain not a cell field; cadence CLOSED. |
