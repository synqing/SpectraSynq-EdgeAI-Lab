---
abstract: "L06: share-student I/O unfrozen; C1 transport frozen. Docs-only; no USB."
---

# L06 — share-student I/O vs transport (10-line contract)

**HARD FAIL (`SAME_SONG_LOOP_MAX_15MIN`).** Same song/clip looped >15 min → agent dies.

1. **STATUS:** student I/O **UNFROZEN**; semantic **transport FROZEN_FOR_C1** (Captain cadence close 2026-08-31). HOST-ONLY recoverability PASS is not an RA8P1 lock.
2. **CLAIM:** C1 may consume four-source `extra_gain` on a proven carrier; the 21k CNN’s 16 kHz / 1 s / 64-mel / 100-frame / four-logit graph is experiment I/O, not product I/O. Do not freeze Student-v0.
3. **FROZEN (transport, not net):** channels+order `vocals, drums, bass, other`; share simplex; silence → zeros not 1/4; `extra_gain` [0.62, 1.0]; ZOH / no interpolation / lookahead=0; hop_us=32000; 5 Hz 0-delay PASS; 50 ms added delay PASS at 20 Hz; **5 Hz+50 ms joint FAIL**; 100 ms FAIL at 20 Hz; C1 playback = C0-v2 ~31.25 Hz, 0 ms extra delay. `other` stays.
4. **UNFROZEN (student I/O):** sample rate, window, stride/hop, log-mel bins/frames, tensor layout, param count, causal-CNN topology, powers-then-normalise vs exported logits, windowed vs hop-level vs streaming graph, U55 compile of *this* net.
5. **UNFROZEN (selection):** which descriptors; temporal rate/context the binding needs; composition_change as ML head (parked; still a function of share(t) vs share(t−Δ)); Semantic-v0 3-class sigmoid activity is a different experiment — not this contract.
6. **GATE:** `SELECTION_GATE.md` — A PASS (share), B HOST PASS (`source_share × WaveformTempo × head_position` only), C OPEN. Halt hop-level/streaming *product* student until Gate C names cadence/latency; HOST sketches allowed, Titan not. I/O stays unfrozen until C1.
7. **EVIDENCE:** `docs/mir/SHARE_STUDENT.md`; `docs/mir/SELECTION_GATE.md`; `docs/mir/SEMANTIC_TRANSPORT_CONTRACT.md`; `artifacts/gate_c0_cadence_silicon/SEMANTIC_TRANSPORT_CONTRACT.json`.
8. **COMMAND:** none. Docs-only. No USB, no flash, no `/dev/cu.usbmodem*`, no 8 s loop.
9. **METHOD_RISK:** freezing experiment frontend (1 s ≈ 1 Hz) would miss the 5 Hz floor and the joint-fail; copying Semantic-v0 3-class I/O would drop `other` and swap share for abs-activity.
10. **NEXT:** keep I/O open; L36 may HOST-sketch streaming *from the transport edges*, not from 16 kHz/1 s; C1 LGP is the remaining freeze trigger, not this receipt.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:grok | L06 10-line I/O-unfrozen vs transport-frozen contract. |
