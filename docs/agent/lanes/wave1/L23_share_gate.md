---
abstract: "L23: SHARE_STUDENT recoverability HOST PASS matches SELECTION_GATE. I/O unfrozen. Cadence-halt wording is stale vs D20. No USB."
---

# L23 — SHARE_STUDENT vs SELECTION_GATE

STATUS: CONSISTENT on stamps. One wording drift. HOST-ONLY. No USB.
CLAIM: Recoverability HOST PASS is the same closed fact in both: 20788-param causal CNN, official MUSDB18 song-level test n=50, four-source simplex including **`other`**, I/O **not** frozen. Gate A PASS (P3-B share) and Gate B HOST PASS (`source_share × WaveformTempo × head_position`) live only in SELECTION_GATE; SHARE_STUDENT does not re-score lights.
CLAIM: SHARE_STUDENT r(pred,true) vocals/drums/bass **0.637 / 0.568 / 0.537** vs mix-linear **0.132 / 0.187 / 0.202**; SELECTION_GATE rounds to **0.64 / 0.57 / 0.54** vs **0.13 / 0.19 / 0.20**. Same run, not a second result. Composition_change stays share(t)−share(t−Δ); no ML event head.
DRIFT: SELECTION_GATE recoverability still says “no hop-level/streaming student until Gate C measures cadence/latency.” Cadence silicon is **CLOSED** (D20). Live halt is SHARE_STUDENT: no deploy-grade streaming net until Gate C says the semantic deserves a contract (C1 / I/O freeze). D22 HOST sketches only (L36), not Titan.
EVIDENCE: `docs/mir/SHARE_STUDENT.md`; `docs/mir/SELECTION_GATE.md` (Recoverability + Evidence so far); `docs/DECISIONS.md` D16–D17, D20, D22.
COMMAND: none. No audio. No 8 s loop. No `/dev/cu.usbmodem*`.
METHOD_RISK: Recoverability PASS ≠ Gate C. Rounded SELECTION_GATE table is not a new experiment. 16 kHz / 1 s / 64-mel is this net’s frontend, not RA8P1 I/O.
NEXT: do not train a product student; keep `other`; freeze I/O only after Gate C (C1). Optional later: replace SELECTION_GATE cadence clause with the C1-contract halt.
HARD FAIL: `SAME_SONG_LOOP_MAX_15MIN` — same song/clip in the room >15 min → kill the player; agent dies.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:grok | L23 contract: share recoverability vs selection gate; cadence-halt drift. |
