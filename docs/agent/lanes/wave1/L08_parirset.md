---
abstract: "L08: AGENTS live-domain vs PARIRSET_ONSET_ALIGNED. HOST-ONLY. No USB."
---
HARD_FAIL: SAME_SONG_LOOP_MAX_15MIN. No USB. No /dev/cu.usbmodem*. Cadence CLOSED.
STATUS: MATCH (compressed)
CLAIM: AGENTS.md “onset delayed ~100 ms, not killed” matches PARIRSET_ONSET_ALIGNED (direct-path 99.7 ms; F1@50 0.05→0.86; 9/9 onset_delayed). OPEN/parallel is D22, not probe output.
EVIDENCE: AGENTS.md:44 ; docs/mir/PARIRSET_ONSET_ALIGNED.md ; artifacts/parirset_probe/receipt_aligned.json
COMMAND: none (docs-only; do not re-run parirset_onset_aligned.py)
METHOD_RISK: AGENTS drops smear (F1 0.79–0.92), 3/8 venues, short clips, pre-delay hypothesis, CrowdioSet gated, HOST-ONLY. “Onset needs no live-domain care” is a false reading; 100 ms wrecks 50 ms lighting sync.
NEXT: keep Amendment 002 delay-aware scoring; do not freeze “onset dies”; CrowdioSet gated; no silicon.
