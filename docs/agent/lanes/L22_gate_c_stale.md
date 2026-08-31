---
abstract: "L22: GATE_C two-clock FAIL looks live, not labelled corpse. Corpse FAIL still true. Live C0 is C0-v2 PASS. HOST docs only."
---
STATUS: FAIL (doc drift — FAIL looks live)
CLAIM: The two-clock FAIL in `docs/mir/GATE_C.md` is **not** labelled corpse. It reads as the live C0 close. Corpse FAIL stays true at `artifacts/gate_c0/`. Live C0 is C0-v2 `ON_SILICON_PIXEL_VALIDATED`.
EVIDENCE: GATE_C L25 heading `ON_SILICON_PIXEL_VALIDATED` then L27 “**2026-08-31 silicon close: FAIL — INVALID TEMPORAL EXECUTION.**” Q1 0.13, Q2/Q3 6/9, “C1 blocked.” Word “corpse” appears once, L33, cadence aside only — not on the FAIL. Abstract L2 + changelog L96 stamp C0-v2 PASS / C1 OPEN. Receipt `artifacts/gate_c0v2/C0V2_RESULT.json` `c0v2=PASS` Q1 0.83 Q2 Δ 0.69 9/9 Q3 Δ 0.58 9/9 `lag_corrected=false` stamp `ON_SILICON_PIXEL_VALIDATED`. Corpse receipt `artifacts/gate_c0/C0_RESULT.json` `c0=FAIL` `execution=INVALID_TEMPORAL_EXECUTION` `authority` names dumps “the corpse”. GATE_C0V2.md L9 does label previous C0 FAIL. AGENTS.md source-ownership row: “Two-clock C0 corpse stays FAIL.” D17 revisit = corpse; D20 C1 OPEN.
COMMAND: none. HOST read of GATE_C vs C0_RESULT vs C0V2_RESULT. No USB. No scorer. No song.
METHOD_RISK: HOST-ONLY. Corpse FAIL is still the correct stamp for `artifacts/gate_c0/`. Drift = GATE_C body presents that FAIL as current silicon close under a PASS heading. Cadence CLOSED (D20) is not this lane. Do not promote the corpse with +14 hops.
NEXT: Rewrite GATE_C C0 body: historical two-clock **corpse FAIL** (keep), then C0-v2 **PASS** (authority). Drop live “C1 blocked.” Point inject path at `GATE_C0V2.md`, not `GATE_C0_SILICON_PATH.md`. Do not rescore dumps. Do not reopen cadence. Do not flash.

## Corpse vs live (the L22 question)

| Surface | How the two-clock FAIL is framed |
| --- | --- |
| `GATE_C.md` L27 | **Looks live.** Lead is “silicon close: FAIL”. No “previous”, no “corpse”, no “historical”. Ends “C1 blocked.” |
| `GATE_C.md` L33 | “two-clock corpse” — cadence exclusion only. Does not relabel L27. |
| `GATE_C.md` L2 / L25 / L53 / L96 | Live programme: C0-v2 PASS, C1 OPEN. Contradicts L27. |
| `GATE_C0V2.md` L9 | **Labelled corpse.** “Previous C0 … stays FAIL.” |
| `C0_RESULT.json` | **Labelled corpse.** `authority`: “Raw dumps and diagnosis.json are the corpse.” |
| `AGENTS.md` source-ownership | **Labelled corpse.** “Two-clock C0 corpse stays FAIL.” |

Verdict: **looks live in GATE_C.** Corpse labelling lives in sibling files, not on the GATE_C FAIL paragraph.

## Body sentences that still read as current C0

Keep as frozen history, not as live close: dumps at `artifacts/gate_c0/`; two-clock runner retired.

1. L10 “**Gate C OPEN.** … until C speaks.” — C0-v2 pixels already spoke.
2. L27 lead FAIL close — corpse close, not live C0.
3. L27 Q1 0.13 / Q2–Q3 6/9 — corpse scores. Authority: Q1 0.83; Q2 9/9; Q3 9/9.
4. L27 “two clocks” — retired `scripts/gate_c0_silicon.py`, not C0-v2.
5. L27 “Successor: C0-v2 … C1 blocked.” — successor already PASS. C1 is OPEN (L53, D20).
6. L33 cadence “later … after a nominal C0-v2 PASS” — PASS already happened; cadence later CLOSED.
7. L43 “C0 must re-measure on silicon.” — C0-v2 already did.
8. L45 silicon path → `GATE_C0_SILICON_PATH.md` — corpse recon. Live path is `GATE_C0V2.md`.
9. L47 “recon, **not** C0 PASS” — still frames current silicon as the two-clock attempt.
10. L55 “Only after C0 pixels behave.” — they do. That is why C1 is OPEN.

USB: none. Audio: none. Cadence: CLOSED.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:grok | L22 contract. Ten stale GATE_C body sentences vs C0-v2 PASS. |
| 2026-08-31 | agent:grok | Re-derive: GATE_C FAIL looks live, not labelled corpse. |
