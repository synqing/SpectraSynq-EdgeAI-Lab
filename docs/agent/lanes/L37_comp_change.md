---
abstract: "L37: composition_change PARKED, not next. GATE_C Parked list + SOURCE_ACTIVITY park + contract four-source only. Do not unpark. C1 is next. Docs-only; no USB."
---

# L37 — composition_change parked (not next)

**HARD FAIL (`SAME_SONG_LOOP_MAX_15MIN`).** Same song/clip looped >15 min → agent dies. Docs-only. No USB. Cadence CLOSED. Do not unpark.

| Field | Value |
| --- | --- |
| STATUS | `composition_change` **PARKED**. **Not next.** ML head stays off. DSP function of share remains legal. HOST-ONLY. |
| CLAIM | Park is the live programme state. Next load-bearing work is **C1 LGP**, not this descriptor. GATE_C binds `source_share × Waveform Tempo × head_position` and lists **composition_change ML head** under Parked. SOURCE_ACTIVITY stamps Event head **NO** and parks the implementation as `share(t)` vs `share(t−Δ)`. The semantic transport contract carries **vocals / drums / bass / other** only — no fifth channel. Share recoverability and C0-v2 do not unpark it. |
| EVIDENCE | `docs/mir/GATE_C.md` Binding + Parked (`composition_change ML head`; After C: four-source freeze, not a change head). `docs/mir/SOURCE_ACTIVITY.md` Q4/Q5 FAIL this comparator; Event head **NO**; “Composition-change implementation is parked”; Next is Gate C, not another network. `docs/mir/SEMANTIC_TRANSPORT_CONTRACT.md` Channels vocals, drums, bass, other; C1 playback C0-v2; I/O unfrozen until C1. Also D16 Rejected neural head; `SHARE_STUDENT.md` “No composition_change ML head”; `GATE_C_CADENCE_HOST.md` “composition_change is not used.” |
| COMMAND | none. Docs-only. No train, no USB, no flash, no `/dev/cu.usbmodem*`, no 8 s loop, no Atlas grammar hunt in this lane. |
| METHOD_RISK | Treating P3-C Comet FAIL as “useless, delete DSP” or as “needs a neural head” both reopen D16. Adding `composition_change` to the frozen-for-C1 four-vector would invent a fifth wire the silicon contract does not carry. Unparking because share recovered, C0-v2 PASSed, or C1 is OPEN is the same error. |
| NEXT | **Keep parked. Do not unpark.** Programme next is C1 (Captain, one full song he chooses, no 8 s loop) on the C0-v2 carrier. Revisit only if Atlas names a morph/transition grammar **and** Captain unparks D16. |

## Parked, not next — three authorities

**[FACT]** `docs/mir/GATE_C.md` programme next remaining Gate C work is **C1 OPEN** (`LGP_PERCEPTUAL_VALIDATED`). Cadence CLOSED. After C passes, freeze four-source share semantics (vocals / drums / bass / **other**). Parked list names **composition_change ML head** with hop-level student, Demucs, and declaring C from host pixels. Binding is share × Tempo × head_position, not composition_change.

**[FACT]** `docs/mir/SOURCE_ACTIVITY.md`: `composition_change × Comet × impact-launch` **FAIL this comparator**; `× WaveformTempo × head_position` **FAIL this comparator**; descriptor **not decided**; Event head **NO**. “Composition-change implementation is parked. It is a deterministic function of share(t) vs share(t−Δ). No extra ML head.” Next named there is Gate C, not another network, not this head.

**[FACT]** `docs/mir/SEMANTIC_TRANSPORT_CONTRACT.md` **FROZEN_FOR_C1**: channels **vocals, drums, bass, other**. No composition_change. Student I/O still unfrozen until C1. C1 plays the already-proven C0-v2 carrier (~31.25 Hz, 0 ms extra delay).

**[FACT]** D16 Chosen: composition-change implementation parked; Rejected: a composition_change neural head. D20 Chosen: next load-bearing task is **C1 LGP perceptual**. No new net.

Do not train/export/U55 a change head. Do not freeze student I/O on it. DSP `source_oracle.composition_change` (causal L1/2, 0.5 s lag, hop-centre, lookahead=0, D13) may stay as an oracle channel. Gate C share driver does not consume it.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:grok | L37 10-line: composition_change ML head still parked (D16). |
| 2026-08-31 | agent:grok | Confirm PARKED not next; cite GATE_C / SOURCE_ACTIVITY / SEMANTIC_TRANSPORT_CONTRACT; do not unpark. |
