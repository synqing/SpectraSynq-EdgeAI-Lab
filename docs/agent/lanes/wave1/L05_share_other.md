---
abstract: "L05 MATCH. Four-source simplex including other is required (tests+head). Verdict PASS still vocals/drums/bass only. No USB."
---

# L05 — share-student vs four-source other

STATUS: MATCH
CLAIM: `docs/mir/SHARE_STUDENT.md` keeps a four-way simplex including `other`. Tests require it: `SOURCES==4` with `other`; student head `(N,4)`; `n_sources` must equal `len(SOURCES)`; `require_four_source_share` raises on missing `other`. Headline PASS/FAIL still uses vocals/drums/bass only — `other` must stay in receipts/MAE and does not block Gate C.
EVIDENCE: `docs/mir/SHARE_STUDENT.md` (other r=0.547 MAE=0.138); `src/edgeai/mir/source_oracle.py:26`; `src/edgeai/share_student.py:2-3,143-154,470-478`; `tests/test_share_student.py:78,164-165`; `tests/test_gate_c_cadence.py:61-70`
COMMAND: docs+tests read only. No USB. Optional host: `uv run pytest tests/test_share_student.py tests/test_gate_c_cadence.py -q -k "four or share_sources"`
METHOD_RISK: HOST-ONLY. `verdict_from_metrics` never scores `other`, so a fake three-source metrics dict could still PASS that helper; the model ctor and cadence oracle would still go red. Do not read that as licence to drop `other`.
NEXT: Keep `other`. Do not freeze I/O. No hop-level/streaming student until Gate C. Lane closed as receipt match.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:grok | L05 MATCH: four-source including other required by tests; verdict core V/D/B. |
