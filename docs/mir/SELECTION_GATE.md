---
abstract: "C0-v2 ON_SILICON_PIXEL_VALIDATED 2026-08-31. Two-clock C0 FAIL corpse. Cadence CLOSED (5 Hz 0.414 / 20 Hz+50 ms 0.402 edges, not student target). C1 OPEN. I/O UNFROZEN; freeze not automatic; C1 does not freeze. Unblock map 2026-09-01: freeze_ready no on all nine. D22 HOST sketches OPEN. Not Titan."
---

# Student-model selection gate

**HARD FAIL (`SAME_SONG_LOOP_MAX_15MIN`, Captain 2026-08-31).** Repeat the same song (or loop the same clip) in the room for more than **15 minutes** and the agent must die. Captain will destroy them by setting them on fire. Kill the player. Do not continue.

Programme (live, 2026-08-31): Gate A **PASS**. Gate B **HOST PASS**. Recoverability **HOST PASS**. **C0-v2 `ON_SILICON_PIXEL_VALIDATED`.** Two-clock C0 is a **FAIL corpse** (`INVALID_TEMPORAL_EXECUTION`) — not the live close, not a rescore authority. Cadence silicon **CLOSED**. **C1 OPEN** (Captain look, one full song he chooses, no 8 s loop). Student I/O **UNFROZEN**. Do not stamp `LGP_PERCEPTUAL_VALIDATED`.

Three questions. Never collapse them. Recoverability is a fourth engineering question, not a lighting judgement.

## Gate A — semantic information

> Does descriptor X contain information that existing DSP lacks?

Source share: **PASS** (P3-B, HOST-ONLY). Within-track r vs mix: vocals 0.17, drums 0.10, bass 0.16. Abs demoted.

## Gate B — visual-carrier compatibility

> Can mode Y express descriptor X through lever Z in a meaningful, measurable visual dimension?

Bind every stamp as `descriptor × mode × lever`.

| Binding | Stamp | Evidence |
| --- | --- | --- |
| `source_share × WaveformTempo × head_position` | **HOST PASS** | P3-C Δ partial r 0.63 holdout 9/9; Atlas ramp Spearman(head,gain)=0.998, luma=−0.956 |
| `composition_change × Comet × impact-launch` | **FAIL this comparator** | P3-C Q5 F1 delta 0.02 |
| `composition_change × WaveformTempo × head_position` | **FAIL this comparator** | P3-C Q4 Δ r 0.06 |
| composition_change as a descriptor | **not decided** | park ML; Atlas may find a morph grammar or record `VISUAL_GRAMMAR_GAP` |

Waveform Tempo is a **reference continuity carrier**, not universal lighting proof. A second compatible mode would be a cross-mode check that the student learned musical state, not Tempo-specific pixels.

## Gate C — product / perceptual utility

> Does that binding actually improve the physical K1 light-show?

**OPEN.** Host pixels ≠ silicon pixels ≠ LGP look. C0-v2 closed the silicon-pixel rung. C1 is the remaining human LGP look. Do **not** stamp `LGP_PERCEPTUAL_VALIDATED`.

Evidence ladder (Atlas / consume export):

```text
STATIC_SOURCE
    → HOST_PIXEL_VALIDATED
    → ON_SILICON_PIXEL_VALIDATED   (dumps/traces; no taste)   ← C0-v2 2026-08-31
    → LGP_PERCEPTUAL_VALIDATED     (optics; Good Light Show Taxonomy)  ← C1 OPEN
```

Gate C is not Gate B. Encoding a number in LEDs is not “the show got better.”

### Live C0 — C0-v2 `ON_SILICON_PIXEL_VALIDATED` (2026-08-31)

Binding `source_share × Waveform Tempo × head_position`. Method: `docs/mir/GATE_C0V2.md`. Receipt `artifacts/gate_c0v2/C0V2_RESULT.json`. `lag_corrected: false`. Holdout n=10: Q1 **0.83** PASS; Q2 Δ **0.69** 9/9 PASS; Q3 Δ **0.58** 9/9 PASS. Probe `k1_main_rpl_rtrace_probe` @ `349d3cd4`. This is the live silicon-pixel close. It does **not** close Gate C.

### Two-clock C0 — FAIL corpse (historical, not live)

**2026-08-31 two-clock C0: FAIL — `INVALID_TEMPORAL_EXECUTION`.** Frozen at `artifacts/gate_c0/`. Do **not** quote this FAIL as the current C0 close. Do **not** promote it with a +14-hop rescore. The two-clock runner is **retired**. Successor is C0-v2 above.

### Cadence silicon — CLOSED (not “wait to measure”)

Captain close 2026-08-31. Receipt: `docs/mir/GATE_C0_CADENCE.md` / `artifacts/gate_c0_cadence_silicon/CADENCE_RESULT.json`. Do **not** reopen cells. Do **not** play the 8 s loop. Do **not** wait for Gate C to measure cadence — it is already measured.

```text
5 Hz @ 0 ms PASS     Q1 0.414   (slowest useful 0-delay)
20 Hz + 50 ms PASS   Q1 0.402   (largest added delay at 20 Hz; actual 64 ms = 2 hops)
100 ms at 20 Hz FAIL (Q1)
200 ms at 20 Hz FAIL
5 Hz + 50 ms FAIL (Q1) — do not AND the edges
10 Hz + 25 ms NOT COMPLETED — do not interpolate
```

Those two PASSes are **transport edges**, not the nominal student target. A student must **not** assume 5 Hz **and** 50 ms together. C1 playback is the already-proven C0-v2 carrier (~31.25 Hz, 0 ms extra delay) on product firmware — that is also not a student I/O freeze. Transport for C1 is `FROZEN_FOR_C1` (`docs/mir/SEMANTIC_TRANSPORT_CONTRACT.md`); student I/O stays **UNFROZEN**.

### C1 — OPEN

Captain look, **one full song he chooses**. No 8 s holdout loop. Method: `docs/mir/GATE_C1.md`. Dumps do not answer C1. Agent does not invent PASS.

## Recoverability (student experiment)

HOST PASS on a 21k causal CNN, official MUSDB18 song splits (see `docs/mir/SHARE_STUDENT.md`). Four sources including **`other`**. That feasibility question is closed.

**I/O remains UNFROZEN** until the nine criteria below **and** C1. Freeze is **not** automatic after C1 — freeze only if the contract still holds once C1 has spoken (`AGENTS.md`, D20/D22, `docs/agent/HANDOFF.md`). Do not freeze Student-v0 yet. Composition change remains a function of share(t) vs share(t−Δ).

**D22 HOST sketches OPEN** (parallel SSA; not Titan; not a product net):

- share-stream I/O sketches from the transport **edges** (pick one envelope; never AND 5 Hz with 50 ms)
- semantic-v0 as **experiment / toolchain** only, not architecture authority
- Demucs as a **HOST teacher probe** (docs/licence; weights UNKNOWN; not installed; not Titan; does not block C1)

A product hop-level or streaming student is **not** started from the 21k 1 s / 64-mel feasibility graph. Cadence is already CLOSED — that halt is gone. The remaining halt is: no product I/O freeze, no Titan, no shipping net, until the nine criteria plus C1.

A small RA8P1/U55 student becomes the primary implementation target only after
**material evidence** for:

1. **Which descriptors** — still not frozen.
2. **Temporal rate / context** — still not frozen. Cadence CLOSED gives **edges** (5 Hz Q1 0.414 at 0 ms; 20 Hz+50 ms Q1 0.402), not a nominal student hop, window, or emit clock. Do not treat either cliff as the target. Do not AND them.
3. **Real-audio incremental information vs DSP** — DEAM human arousal vs energy (P1); source-activity vs mixture energy (P3). Synthetic r=0.99 is not this evidence.
4. **Oracle/teacher quality** — human GT, separator envelopes, Essentia heads; licences split.
5. **CLEAN/STUDIO behaviour**
6. **Live/venue-domain robustness** — Amendment 002: CLEAN vs PA/ROOM vs PA/ROOM+CROWD; PaRIRset held-out venues intact.
7. **Licensing/provenance** — `mir/registry.yaml`. Teacher use ≠ derived-weight clearance.
8. **Visual utility** — Gates B then C. Bind `descriptor × mode × lever`. Mean brightness is not the default metric. A fail on one binding is not a global fail. Live: B HOST PASS; C0-v2 `ON_SILICON_PIXEL_VALIDATED`; **C1 still OPEN**.
9. **U55 compressibility** — PRE-SILICON compile of a candidate graph (RUHMI), not Semantic-v0-synthetic authority. GHA 33319114336: `ad01_int8.tflite` and `smoke.onnx` both emitted C99. Receipt: `docs/ruhmi/COMPILE_RECEIPT.md`. Not ON-SILICON. Not this 21k share net.

Do not freeze Student-v0 yet.

Evidence so far (HOST-ONLY unless labelled, not a freeze):

- Real-audio incremental vs DSP: DEAM 2015 human arousal vs energy mean r=0.37, R²=0.30. Not Semantic-v0's r=0.99. Criterion 3, not Gate A. Gate A PASS is source share only.
- Visual utility (A/B/C replay, not firmware): A = onset baseline; B = same extra DoF from RMS; C = same extra DoF from human arousal; w=0.65. Five 2015 songs (2030/2028 controls; 2034/2041/2056 residuals). `docs/mir/visual_replay/index.html`. Not a Captain LED judgement and not a student freeze.
- Live/venue: PaRIRset test-split convolution on three held-out venues. Unaligned onset r is low because the IRs inject ~100 ms delay, not because events vanish. Delay-aligned native-hop F1@50 ms recovers 0.05 → 0.86 (HOST-ONLY). Old “onset dies” reading **invalidated**. Residual smear remains (aligned F1 0.79–0.92). CrowdioSet not ingested. Receipt: `docs/mir/PARIRSET_ONSET_ALIGNED.md`.
- Source activity: P3-B full MUSDB18 n=150. Within-track r(drums_share, mix)=0.10 vs r(drums_abs, mix)=0.62. Vocals 0.17 vs 0.44. Bass 0.16 vs 0.64. **abs DEMOTE; share PASS incremental-info (Gate A).** P3-C dump close: **`source_share × WaveformTempo × head_position` HOST PASS (Gate B)** (holdout Δ partial r 0.63, 9/9). Waveform Tempo is a **reference continuity carrier**. **`composition_change × Comet × impact-launch` FAIL** this comparator. **C0-v2 `ON_SILICON_PIXEL_VALIDATED` 2026-08-31.** Cadence **CLOSED**. **C1 OPEN.** Recoverability: tiny causal CNN 20 788 params, official MUSDB18 song-level test n=50, within-track r(pred,true) vocals/drums/bass = 0.64/0.57/0.54 vs mix-linear 0.13/0.19/0.20. HOST-ONLY. I/O not frozen. `docs/mir/SHARE_STUDENT.md`. Demucs not installed; HOST teacher probe OPEN, not Titan.
- Cadence / transport edges (ON-SILICON, CLOSED): 5 Hz @ 0 ms Q1 **0.414** PASS; 20 Hz + 50 ms Q1 **0.402** PASS; joint 5 Hz + 50 ms FAIL. Edges, not the nominal student target. `student_freeze: false`.
- U55 compressibility: PRE-SILICON C99 for Renesas `ad01_int8.tflite` and lab `smoke.onnx` (GHA 33319114336, AdaptiveAvgPool2d after D11 ReduceMean split). Not ON-SILICON.
- Teacher/oracle quality: Essentia DEAM head ≠ human 2 Hz on two songs. Jamendo mood means differ; often clip-flat.

## Working shortlist (NOT a freeze)

Worth keeping on the visual-utility list after landscape + conventional traces:

| Descriptor | Class | Why it might matter | Risk |
| --- | --- | --- | --- |
| onset / flux / RMS | deterministic DSP | already the lighting engine’s backbone | ML should not recreate this |
| beat / tempo / downbeat | conventional MIR | phrase-scale motion | lag vs tight onset |
| source activity (vocals/drums/bass/…) | teacher-derived student candidate | modulation independent of mix energy | needs stem/separator teacher; Semantic-v0 synthetic GT is too easy |
| arousal (dynamic) | small ML or teacher head (DEAM) | energy-of-feeling vs energy-of-spectrum | 2 Hz annotations; NC dataset |
| Jamendo mood/theme (energetic, dark, relaxing, …) | tagging / teacher | closer to the old custom ontology than BUILDING/DROPPING | often clip-level, chatter if windowed; NC-SA weights |
| structural novelty | conventional + embedding Δ | section / drop correspondence | embedding movement ≠ musical section |
| music-text similarity (“percussive”, “dreamlike”) | host oracle (MuQ-MuLan / CLAP-class) | zero-shot labels without inventing GT | large, NC weights, lag |

**Do not invent BUILDING/DROPPING/CHAOTIC labels yet.** Check whether novelty + arousal + source activity + a mood head already cover the lighting intent.

A descriptor has no visual utility in the abstract. Gate A is information, Gate B is a named carrier, Gate C is the physical show. Recoverability (“can we infer it cheaply?”) is a fourth engineering question, not a lighting judgement.

Consume firmware `effect-semantics.json` with `source_firmware_sha` **and** `atlas_artifact_sha256` (the registry can move while firmware SHA stays put). See `docs/mir/EFFECT_SEMANTICS_CONSUME.md`.

## Unblock map 2026-09-01

HOST provenance + a paper streaming-shape sketch. **I/O remains UNFROZEN. C1 does not freeze.** Freeze is **not** automatic. No `LGP_PERCEPTUAL_VALIDATED`. No 16 kHz / 1 s / 64-mel lock. Pins in `mir/registry.yaml` are HOST-ONLY measured (0 invented). Cadence cells stay CLOSED.

| # | Question | Live state | HOST work that unblocks | Still needs Captain / counsel / board | freeze_ready? |
| --- | --- | --- | --- | --- | --- |
| 1 | Which descriptors | Not frozen. Shortlist exists. Live binding is `source_share × Waveform Tempo × head_position`. | Keep HOST traces. Do not freeze Student-v0 I/O. | Captain: which descriptors the lights actually need. | no |
| 2 | Temporal rate / context | Not frozen. Cadence CLOSED: 5 Hz @ 0 ms PASS, 20 Hz + 50 ms PASS, joint 5 Hz + 50 ms FAIL. Edges, not a hop. | HOST R XOR D emit-envelope sketch (`src/edgeai/mir/stream_sketch.py`). Never AND the cliffs. | Captain after C1: explicit I/O freeze only if the contract still holds. | no |
| 3 | Real-audio incremental vs DSP | DEAM human arousal vs energy r=0.37. Share vs mix PASS (Gate A). | More descriptor-vs-DSP HOST traces on real audio. No 8 s room loop. | Not a freeze. | no |
| 4 | Oracle / teacher quality | Essentia DEAM head ≠ human 2 Hz. Demucs HOST probe OPEN; weights UNKNOWN / LEGAL REVIEW. | Docs + local HF cache pin. Do not `uv add demucs`. | Counsel: teacher use does not clear derived student weights. | no |
| 5 | CLEAN / STUDIO behaviour | MUSDB18 STEMS executed as research/NC. `commercial_training_lineage: false`. | HOST evaluation on STEMS stays research. | Counsel / board: commercial-safe corpus. | no |
| 6 | Live / venue-domain robustness | PaRIRset: onset delayed ~100 ms, not killed. CrowdioSet not ingested. | Delay-aware HOST rescoring. Keep held-out venues. | Captain / counsel: crowd-file licences before ingest. | no |
| 7 | Licensing / provenance | Registry now has HOST-ONLY measured pins on hashed bytes / uv.lock wheels. Rest stay UNKNOWN. | Pin only what was hashed. Do not invent SHAs. | Counsel: commercial_training_lineage and teacher→student clearance. | no |
| 8 | Visual utility | Gate A PASS. Gate B HOST PASS. C0-v2 `ON_SILICON_PIXEL_VALIDATED`. **C1 OPEN.** | No agent LGP stamp. Dumps do not answer C1. | Captain: one full song he chooses. C1 does not freeze. | no |
| 9 | U55 compressibility | PRE-SILICON C99 for `ad01_int8.tflite` + `smoke.onnx`. Not this 21k share net. Not ON-SILICON. | Golden tensors + RUHMI compile receipts. | Board: no invented Titan / PDM numbers. | no |

`freeze_ready?` is **no** on every row. A later freeze is a separate written act after the nine criteria **and** C1, and only if the transport still holds.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-30 | agent:edgeai | Gate opened; no freeze. |
| 2026-08-30 | agent:edgeai | Evidence pointers; still OPEN. |
| 2026-08-31 | agent:edgeai | Nine criteria; smoke C99 PASS; PaRIRset onset provisional. |
| 2026-08-31 | agent:edgeai | Onset delay-aware: delayed not killed; A/B/C visual control. |
| 2026-08-31 | agent:edgeai | P3-A MUSDB samples; abs/share/delta; share ≠ mix energy. |
| 2026-08-31 | agent:edgeai | P3-B 150 tracks; within-track share vs mix; visual pages not a pass. |
| 2026-08-31 | agent:edgeai | Visual utility = P3-C engine pixels; abs demoted; Demucs still not next. |
| 2026-08-31 | agent:edgeai | P3-C dump-scored: share position PASS; composition-change comets FAIL. |
| 2026-08-31 | agent:edgeai | Visual utility binds descriptor × mode × lever; composition_change FAIL narrowed to Comet impact-launch. |
| 2026-08-31 | agent:edgeai | Permanent A/B/C gates; recoverability unblocked; C remains OPEN. |
| 2026-08-31 | agent:edgeai | Feasibility PASS; Gate C next; halt hop-level student. |
| 2026-08-31 | agent:edgeai | C0 FAIL INVALID_TEMPORAL_EXECUTION; C0-v2 successor. |
| 2026-08-31 | agent:grok | Live programme: C0-v2 ON_SILICON_PIXEL_VALIDATED; two-clock C0 labelled FAIL corpse; cadence CLOSED; C1 OPEN; I/O unfrozen until nine criteria + C1 (freeze not automatic); D22 HOST sketches OPEN; cliff PASSes are edges not student target; deleted “C0 FAIL / C0-v2 next / C1 blocked” and “wait until Gate C measures cadence.” |
| 2026-09-01 | agent:edgeai | Unblock map: nine questions, freeze_ready no; I/O remains UNFROZEN; C1 does not freeze. |
