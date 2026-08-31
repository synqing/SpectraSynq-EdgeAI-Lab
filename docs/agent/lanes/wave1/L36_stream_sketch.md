---
abstract: "L36 HOST sketch: streaming student I/O from silicon 5 Hz / 50 ms as exclusive envelopes, not AND. No train. I/O unfrozen."
---

# L36 — HOST streaming-student I/O sketch (10-line contract)

**HARD FAIL (`SAME_SONG_LOOP_MAX_15MIN`).** Same song/clip looped >15 min → agent dies. Docs-only. No USB. No train.

1. **STATUS:** HOST sketch only. Student I/O **UNFROZEN**. Transport **FROZEN_FOR_C1**. No weights, no U55, no Titan. Cadence silicon **CLOSED**.
2. **CLAIM:** Sketch the streaming I/O from the silicon transport *edges*, not from the 21k 16 kHz / 1 s / 64-mel graph. Pick **one** envelope. **Never AND 5 Hz with 50 ms** — joint cell `r5_d50` is Q1 FAIL (`family=corner`, not interpolated).
3. **ENVELOPES (exclusive; enum, not a union):** **R** = `r5_d0` — emit ≥ **5 Hz**, extra delay **0 hops**. **D** = `r20_d50` — emit ≥ **20 Hz** (the rate at which 50 ms PASSed), extra delay **50 ms requested = 64 ms = 2 hops** of `hop_us=32000`. 100 ms at 20 Hz FAIL. C1 playback (~31.25 Hz, 0 ms, C0-v2 carrier) is **not** a student envelope.
4. **OUTPUT (transport-bound, not a net freeze):** 4-vector order `vocals, drums, bass, other`; simplex share; silence → zeros not 1/4; `extra_gain` ∈ [0.62, 1.0]; ZOH / no interpolation / lookahead=0. **Packet clock ≠ emit clock:** ZOH-repeat PRSM at ≥ 30 Hz (`hz` 30–240). Do not put `hz=5` on the wire.
5. **INPUT (HOST sketch, UNFROZEN):** **S1 (matches how silicon was scored)** — causal net emits on the 32 ms hop grid; ZOH+delay is a *later* stage that then chooses R *or* D. **S2 (cheaper, HOST-HYPOTHESIS)** — net hop equals the chosen emit period (200 ms for R, 50 ms for D). S2 is **not** the silicon 5 Hz PASS (that PASS held a native-hop oracle). Ban `AdaptiveAvgPool2d((1,1))` over 1 s: that graph is ~1 Hz / 1 s latency and misses both edges. 16 kHz / mel bins / tensor layout stay unlocked.
6. **NOT THIS:** do not train; do not gold-plate the 21k CNN; do not copy Semantic-v0 3-class sigmoid (drops `other`); do not treat authored freshness 50 ms as the silicon added-delay 50 ms; do not fill 10 Hz+25 ms; do not compile this sketch for U55.
7. **EVIDENCE:** `docs/mir/SEMANTIC_TRANSPORT_CONTRACT.md`; `artifacts/gate_c0_cadence_silicon/SEMANTIC_TRANSPORT_CONTRACT.json` (`combined_5hz_50ms=FAIL`, `student_must_not_assume`); `CADENCE_RESULT.json` + `cells/{r5_d0,r20_d50,r5_d50}.json`; L04; L06; `docs/mir/SHARE_STUDENT.md` (1 s pool is experiment I/O).
8. **COMMAND:** none executed. Docs-only JSON already on disk. No pytest train, no USB, no `/dev/cu.usbmodem*`, no 8 s loop, no ffplay.
9. **METHOD_RISK:** student receptive-field latency is **not** silicon `actual_delay_ms`. Folding a 200 ms window into “5 Hz PASS” and then spending 50 ms extra delay rebuilds the failed joint. Host cadence (20 Hz floor, 50 ms FAIL) is not this contract (L33). Authored drop-cut at 50 ms is a wire-freshness law, satisfied by packet repeat, not by slowing the net.
10. **NEXT:** keep I/O open. A later HOST test may implement S1 ZOH as a numpy hold (no fit). Freeze only after `SELECTION_GATE` + C1 if the contract still holds. C1 LGP is the remaining human look, on the proven carrier, not this sketch.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:grok | L36 HOST streaming I/O sketch: exclusive 5 Hz / 50 ms envelopes; S1 vs S2; no train. |
