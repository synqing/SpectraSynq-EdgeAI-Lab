---
abstract: "L27: TITAN_BRINGUP has no ON-SILICON stamp. 1 ms NPU is PRE-SILICON hypothetical. 100 ms is PaRIRset HOST. 50 ms is C0-v2 cadence, not U55."
---

# L27 — TITAN_BRINGUP invented numbers

STATUS: PASS (no ON-SILICON claim) + HAZARD (1 ms looks like board NPU)
CLAIM: `docs/TITAN_BRINGUP.md` banners PRE-SILICON (L9: no RA8P1; do not quote latency). No filled p50/p95/µs. GHA 33319114336 is PRE-SILICON C99. Golden band is HOST-ONLY until first board (L39).
CLAIM: One number **looks** ON-SILICON and is not: **1 ms** NPU (“even if the NPU runs in 1 ms”, L61) — PRE-SILICON hypothetical, never measured. **100 ms** acoustic path is PaRIRset HOST-ONLY (three short test IRs; AMENDMENT_002 / PARIRSET_ONSET_ALIGNED), not Titan. **50 ms** is K1 C0-v2 added-delay PASS / visual-sync budget, not U55. **1 kHz** is an anti-default (L73), not a rate.
EVIDENCE: `docs/TITAN_BRINGUP.md` L9, L39, L60–61, L73, L99; `docs/AMENDMENT_002.md` ~100 ms; `docs/mir/PARIRSET_ONSET_ALIGNED.md` HOST-ONLY; `docs/mir/GATE_C0_CADENCE.md` 50 ms ON-SILICON cadence (not Titan).
COMMAND: none (HOST grep/read only). Cadence CLOSED. No USB. No flash. No room audio.
METHOD_RISK: Quoting 1 ms / 100 ms / 50 ms from this file as Titan latency is the failure. File already forbids quoting latency; the 1 ms clause still invites it.
NEXT: Do not cite 1 ms as U55. If L60–61 is edited, stamp 100 ms `HOST-ONLY` and 1 ms `PRE-SILICON hypothetical`. No invented board numbers.
HARD FAIL: `SAME_SONG_LOOP_MAX_15MIN` — this lane played nothing.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:grok | L27 contract. 1 ms NPU is PRE-SILICON lookalike. |
