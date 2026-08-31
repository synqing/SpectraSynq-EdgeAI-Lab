---
abstract: "L04: 5 Hz+50 ms FAIL is silicon cell r5_d50 (Q1), not interpolated. Edges r5_d0 and r20_d50 PASS. Student must not assume both."
---

# L04 — student must-not-assume 5 Hz+50 ms

**STATUS:** PASS — joint FAIL is on disk; cadence CLOSED; no USB.

**CLAIM:** A student must **not** assume 5 Hz **and** 50 ms extra delay together. 1-D edges PASS; the combined corner is a measured silicon cell `family=corner`, `source=silicon`, `hold_policy` ZOH/no interpolation, `lag_corrected=false`. Not a 10 Hz+25 ms fill-in (`tighten_complete=false`).

**EVIDENCE:** `artifacts/gate_c0_cadence_silicon/cells/{r5_d0,r20_d50,r5_d50}.json` + `CADENCE_RESULT.json` `corner.source="r5_d50 silicon"` + `plain.combined_5hz_50ms="FAIL"` + `non_claims` “kept (not interpolated)” + `dumps/r5_d50/` (10 clips, `n_timing_invalid=0`). Floors: Q1 Spearman≥0.40; Q2/Q3 median Δ≥0.15 and ≥70% clips Δ>0 (`docs/mir/GATE_C0_CADENCE.md`).

| Cell | rate / delay | Q1 Spearman | Q2 Δ share wins | Q3 Δ abs wins | verdict |
| --- | --- | --- | --- | --- | --- |
| `r5_d0` | 5 Hz / 0 ms (0 hops) | **0.414 PASS** | **0.530 8/9 PASS** | **0.438 9/9 PASS** | PASS |
| `r20_d50` | 20 Hz / 50 ms req (64 ms, 2 hops) | **0.402 PASS** | **0.420 8/9 PASS** | **0.355 8/9 PASS** | PASS |
| `r5_d50` | 5 Hz / 50 ms req (64 ms, 2 hops) | **0.245 FAIL** | **0.281 8/9 PASS** | **0.310 7/9 PASS** | **BINDING_FAIL (Q1)** |

**COMMAND:** `python3 -c "import json,pathlib; p=pathlib.Path('artifacts/gate_c0_cadence_silicon/cells');
[print(n, {k:json.loads((p/n).read_text())[k] for k in ('family','rate_hz','delay_s','actual_delay_ms','source','verdict','Q1','Q2','Q3','median_spearman_pos_gain','median_delta_pos_share','median_delta_pos_abs','n_clips','n_timing_invalid')}) for n in ('r5_d0.json','r20_d50.json','r5_d50.json')]"` — HOST JSON only. Do not open USB, flash, or play audio.

**METHOD_RISK:** Q1 uses native extra_gain vs head; applied series is ZOH+causal delay. Joint death is **Q1**, not Q2/Q3. 50 ms requested → 2 hops = 64 ms actual. Skelpolu NaNs drop one clip from Δ wins (denom 9). Do not treat 10 Hz+25 ms as a substitute corner.

**NEXT:** Streaming/student sketches consume this must-not (L36). C1 plays C0-v2 ~31.25 Hz / 0 ms extra delay. Do not reopen cadence cells.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:grok | L04: r5_d50 Q1 FAIL is a silicon receipt; edges PASS; student must-not both. |
