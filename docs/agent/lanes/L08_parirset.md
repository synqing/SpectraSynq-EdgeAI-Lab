---
abstract: "L08: receipt_aligned.json vs PARIRSET_ONSET_ALIGNED + Amendment 002. HOST-ONLY. Onset delayed ~100 ms on 3 short test IRs, not killed. No USB."
---

# L08 — PaRIRset onset aligned receipt

**HARD FAIL (`SAME_SONG_LOOP_MAX_15MIN`).** Same song/clip in the room >15 min → kill the player; agent dies.
Cadence CLOSED. No USB. No `/dev/cu.usbmodem*`. No playback. No 8 s loop.

STATUS: MATCH (HOST-ONLY). Receipt and canon agree: onset **delayed ~100 ms, not killed**, on **3 short test IRs**.
CLAIM: `artifacts/parirset_probe/receipt_aligned.json` is the delay-aware authority. Means over 9 comparisons (DEAM 2030/2034/2041 × olivenzaOutdoors / valenciaMoon / palmaEsGremi): direct-path **99.7 ms**; native F1@50 ms **0.05 → 0.86** after align; native onset r **0.05 → 0.88**; 9/9 `onset_delayed`. Unaligned 2 Hz r is a delay artefact. Old “onset dies” reading **invalidated**.
CLAIM: AGENTS.md live-domain line (“onset delayed ~100 ms, not killed”) matches this receipt. OPEN/parallel is D22 roster status, not a probe output.
EVIDENCE: `docs/mir/PARIRSET_ONSET_ALIGNED.md`; `docs/AMENDMENT_002.md` (2026-08-31 update); `artifacts/parirset_probe/receipt_aligned.json`; AGENTS.md live-domain row; `docs/DECISIONS.md` D10; `docs/mir/SELECTION_GATE.md` live/venue bullet.
COMMAND: none (docs-only confirm). Do **not** re-run `scripts/parirset_onset_aligned.py`. Do not play DEAM or RIRs.
METHOD_RISK: three IRs only (~0.4–0.6 s), 3/8 held-out venues, CrowdioSet gated, residual aligned F1 0.79–0.92 (smear / extra peaks), HOST-ONLY not ON-SILICON. ~100 ms may be dataset pre-delay (4410 samples @ 44.1 kHz), still product-relevant. Unaccounted 100 ms still wrecks a 50 ms lighting-sync budget.
NEXT: keep Amendment 002 delay-aware scoring; do not freeze “onset dies in PA/ROOM”; do not ingest CrowdioSet; do not generalise to long hall tails or remaining five test venues.

## Receipt vs canon (re-derived)

| metric | receipt_aligned.json | PARIRSET_ONSET_ALIGNED.md |
| --- | ---: | ---: |
| mean direct-path | 0.0996875 s | 99.7 ms |
| onset r, legacy 2 Hz, zero-lag | 0.0702 | 0.07 |
| onset r, native hop, zero-lag | 0.0527 | 0.05 |
| onset r, native hop, delay-aligned | 0.8753 | **0.88** |
| event F1 @ 50 ms, unaligned | 0.0525 | 0.05 |
| event F1 @ 50 ms, aligned | 0.8576 | **0.86** |
| event F1 @ 100 ms, unaligned | 0.6219 | 0.62 |
| event F1 @ 100 ms, aligned | 0.8704 | 0.87 |
| RMS r, zero-lag | 0.5760 | 0.58 |
| RMS r, aligned | 0.8251 | 0.83 |
| verdict | 9 `onset_delayed` | 9/9 (`F1@50 aligned ≥ 0.7` and unaligned `< 0.4`) |

2034 (old negative-r scare): 2 Hz zero-lag −0.27 / −0.29 / −0.27 → native aligned r 0.87 / 0.92 / 0.82; F1@50 aligned 0.86 / 0.92 / 0.86. Precision drop 2030 olivenza 0.73; recall drop 2041 olivenza 0.71. Matches the canon table.

Checker: `tests/test_onset_align.py` (synthetic clicks; red if events deleted or 80 ms delay scored at 50 ms unaligned). Not a tautology.

## Bound (this lane)

Not a student freeze. Not ON-SILICON. Not “onset needs no live-domain care”. PA/ROOM first is delay/sync, then residual smear. Amendment 002 continues.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:grok-ssa-l08 | Confirmed receipt vs PARIRSET_ONSET_ALIGNED: delayed ~100 ms, not killed, 3 short test IRs. |
