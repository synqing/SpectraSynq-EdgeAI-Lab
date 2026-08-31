---
abstract: "L22: GATE_C.md abstract+changelog say C0-v2 PASS / C1 OPEN; body still closes C0 as two-clock FAIL. Corpse FAIL stays true. Live stamp is ON_SILICON_PIXEL_VALIDATED. HOST docs only."
---

# L22 — GATE_C stale two-clock FAIL vs C0-v2 PASS

**HARD FAIL (`SAME_SONG_LOOP_MAX_15MIN`).** Docs only. No USB. No song. Cadence CLOSED.

| Field | Value |
| --- | --- |
| STATUS | FAIL (doc drift) |
| CLAIM | `docs/mir/GATE_C.md` abstract and changelog stamp C0-v2 `ON_SILICON_PIXEL_VALIDATED` + C1 OPEN; C0 body still reads as 2026-08-31 two-clock FAIL and C1 blocked. Two-clock corpse remains FAIL. Live C0 is C0-v2 PASS. |
| EVIDENCE | `docs/mir/GATE_C.md` L2, L10, L27, L33, L43, L45, L47, L55, L96; `docs/mir/GATE_C0V2.md`; `artifacts/gate_c0v2/C0V2_RESULT.json` `c0v2: PASS`; `docs/DECISIONS.md` D17 corpse + D20 C1 OPEN |
| COMMAND | none (read-only). Denominator: GATE_C body vs GATE_C abstract/changelog vs C0V2_RESULT, not vs itself. |
| METHOD_RISK | Corpse FAIL at `artifacts/gate_c0/` is still true. Stale = presented as current C0 close. Cadence CLOSED is D20, not this file. |
| NEXT | Rewrite GATE_C C0 section: corpse FAIL (historical) then C0-v2 PASS (authority). Unblock C1 wording. Point silicon path at GATE_C0V2.md. Do not rescore the corpse. |

## Stale sentences in `docs/mir/GATE_C.md` (current-status reading)

Keep as history, not as live close: dumps frozen at `artifacts/gate_c0/`; two-clock runner retired; successor `GATE_C0V2.md`.

1. L10: “**Gate C OPEN.** … No more neural-net work until C speaks.” — C0-v2 has spoken (`ON_SILICON_PIXEL_VALIDATED`). C1 is the remaining Gate C. “Until C speaks” is false for pixels.
2. L27 lead: “**2026-08-31 silicon close: FAIL — INVALID TEMPORAL EXECUTION.**” — that is the two-clock corpse close, not the live C0 close. Live close is C0-v2 PASS same day (`C0V2_RESULT.json`).
3. L27: “Holdout n=10: Q1 **0.13** FAIL; Q2/Q3 **6/9** FAIL.” — corpse scores. Authority scores are Q1 0.83; Q2 Δ 0.69 9/9; Q3 Δ 0.58 9/9.
4. L27: “Capture and PRSM injection used two clocks.” — true of retired `scripts/gate_c0_silicon.py`; false of C0-v2 device epoch.
5. L27: “Successor: C0-v2 device epoch (`docs/mir/GATE_C0V2.md`). C1 blocked.” — successor already ran PASS. “C1 blocked” contradicts this file’s L2/L53/L96 and D20.
6. L33: “**Cadence / latency characterisation is a later C0-v2 subtest**, run only after a nominal C0-v2 PASS.” — C0-v2 already PASS; cadence later CLOSED (D20). Not a future gate.
7. L43: “C0 must re-measure on silicon.” — C0-v2 already re-measured on silicon. Host 20 Hz note is rehearsal, not the open C0 action.
8. L45: “Silicon inject + dump path: [GATE_C0_SILICON_PATH.md](../mir/GATE_C0_SILICON_PATH.md).” — that path is the two-clock corpse. Live path is `GATE_C0V2.md`.
9. L47: “Shortest existing path (recon, **not** C0 PASS): USB-CDC **PRSM** …” — still frames current silicon as two-clock recon, not C0 PASS.
10. L55: “Only after C0 pixels behave.” — C0-v2 pixels already behave. C1 is OPEN for that reason.

Not stale: L25 heading `ON_SILICON_PIXEL_VALIDATED`; L53 “**OPEN.** Cadence CLOSED”; L2 abstract; L96 changelog “C0-v2 PASS; cadence Captain-closed; C1 OPEN.”

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:grok | L22 contract. Ten stale GATE_C body sentences vs C0-v2 PASS. |
