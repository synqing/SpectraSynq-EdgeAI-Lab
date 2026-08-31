---
abstract: "L04: student must not AND 5 Hz with 50 ms. Silicon r5_d50 Q1 FAIL; edges r5_d0 and r20_d50 PASS. 10 Hz+25 ms aborted, not interpolated."
---

# L04 — student must-not-assume 5 Hz+50 ms

**STATUS:** PASS — joint FAIL is a measured silicon cell; cadence CLOSED; no USB.

**CLAIM:** A student must **not** assume 5 Hz **and** 50 ms extra delay together. The 1-D edges pass independently; the AND is a measured `family=corner` cell, not a fill-in of aborted 10 Hz+25 ms.

**EVIDENCE:** `artifacts/gate_c0_cadence_silicon/cells/{r5_d0,r20_d50,r5_d50}.json` (no `r10_d25.json`; only `r10_d25_partial.json`, 6 tracks). `CADENCE_RESULT.json`: `corner.source="r5_d50 silicon"`, `corner.Q1=FAIL`, `tighten_complete=false`, `plain.combined_5hz_50ms=FAIL`, `plain.combined_10hz_25ms=NOT_COMPLETED`, `non_claims` “combined 5 Hz + 50 ms FAIL is kept (not interpolated)” and “10 Hz + 25 ms not completed”. `SEMANTIC_TRANSPORT_CONTRACT.json` `student_must_not_assume`. Dumps: `dumps/r5_d50/` 10 clips, `n_timing_invalid=0`; `dumps/r10_d25/` incomplete. Floors (`docs/mir/GATE_C0_CADENCE.md`): Q1 Spearman(head, extra_gain) ≥ 0.40; Q2/Q3 median Δ ≥ 0.15 and ≥ 70% clips Δ > 0.

| Cell | family / rate / delay | Q1 Spearman | Q2 Δ share | Q3 Δ abs | verdict |
| --- | --- | --- | --- | --- | --- |
| `r5_d0` | rate · 5 Hz · 0 ms (0 hops) · silicon | **0.414 PASS** | **0.530 8/9 PASS** | **0.438 9/9 PASS** | PASS |
| `r20_d50` | delay · 20 Hz · 50 ms req (64 ms, 2 hops) · silicon | **0.402 PASS** | **0.420 8/9 PASS** | **0.355 8/9 PASS** | PASS |
| `r5_d50` | **corner** · 5 Hz · 50 ms req (64 ms, 2 hops) · silicon | **0.245 FAIL** (< 0.40) | **0.281 8/9 PASS** | **0.310 7/9 PASS** | **BINDING_FAIL (Q1)** |
| `r10_d25` | tighten attempt | — | — | — | **NOT_COMPLETED** (partial 6/10; no verdict JSON) |

All three scored cells: `hold_policy` ZOH / no interpolation, `lag_corrected=false`. Binding `source_share × WaveformTempo × head_position`.

**COMMAND:** `python3 -c "import json,pathlib; root=pathlib.Path('artifacts/gate_c0_cadence_silicon'); p=root/'cells';
[print(n, {k:json.loads((p/n).read_text())[k] for k in ('family','rate_hz','delay_s','actual_delay_ms','source','verdict','Q1','Q2','Q3','median_spearman_pos_gain','median_delta_pos_share','median_delta_pos_abs','n_clips','n_timing_invalid')}) for n in ('r5_d0.json','r20_d50.json','r5_d50.json')];
c=json.loads((root/'CADENCE_RESULT.json').read_text()); print('corner',c['corner']); print('plain',{k:c['plain'][k] for k in ('combined_5hz_50ms','combined_10hz_25ms')}); print('non_claims',c['non_claims'][:3]); print('r10_d25.json exists', (p/'r10_d25.json').exists(), 'partial_tracks', len(json.loads((p/'r10_d25_partial.json').read_text())))"` — HOST JSON only. Do not open USB, flash, or play audio.

**METHOD_RISK:** Joint death is **Q1**, not Q2/Q3. Q1 scores native extra_gain vs head; applied series is ZOH + causal hop delay. 50 ms requested → `round(0.05/0.032)=2` hops = 64 ms actual. Skelpolu NaNs drop one clip from Δ wins (denom 9). Do **not** treat aborted 10 Hz+25 ms (`tighten_complete=false`) as a substitute corner or interpolate it. Edges are not a union: 5 Hz PASSes at 0 ms; 50 ms PASSes at 20 Hz.

**NEXT:** Streaming/student sketches consume this must-not (L36): pick one envelope, never AND. C1 plays C0-v2 ~31.25 Hz / 0 ms extra delay. Do not reopen cadence cells.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:grok | L04: r5_d50 Q1 FAIL is a silicon receipt; edges PASS; student must-not both. |
| 2026-08-31 | agent:grok | Re-derived: abort of 10 Hz+25 ms (6/10 partial, no verdict JSON) is not interpolated into the corner. |
