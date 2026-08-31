---
abstract: "Feasibility PASS. A PASS, B HOST PASS. C0 FAIL INVALID_TEMPORAL_EXECUTION 2026-08-31. C0-v2 next. C1 blocked. I/O unfrozen. No Demucs."
---

# Student-model selection gate

**HARD FAIL (`SAME_SONG_LOOP_MAX_15MIN`, Captain 2026-08-31).** Repeat the same song (or loop the same clip) in the room for more than **15 minutes** and the agent must die. Captain will destroy them by setting them on fire. Kill the player. Do not continue.

Three questions. Never collapse them.

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

**OPEN.** Host pixels ≠ silicon pixels ≠ LGP look.

Evidence ladder (Atlas / consume export):

```text
STATIC_SOURCE
    → HOST_PIXEL_VALIDATED
    → ON_SILICON_PIXEL_VALIDATED   (dumps/traces; no taste)
    → LGP_PERCEPTUAL_VALIDATED     (optics; Good Light Show Taxonomy)
```

Gate C is not Gate B. Encoding a number in LEDs is not “the show got better.”

## Recoverability (student experiment)

HOST PASS on a 21k causal CNN, official MUSDB18 song splits (see `docs/mir/SHARE_STUDENT.md`). Four sources including **`other`**. That feasibility question is closed. **Do not start a hop-level or streaming student** until Gate C (`docs/mir/GATE_C.md`) measures the cadence/latency the binding actually needs. I/O remains unfrozen. Composition change remains a function of share(t) vs share(t−Δ).

A small RA8P1/U55 student becomes the primary implementation target only after
**material evidence** for:

1. **Which descriptors** — still not frozen.
2. **Temporal rate / context** — still not frozen.
3. **Real-audio incremental information vs DSP** — DEAM human arousal vs energy (P1); source-activity vs mixture energy (P3). Synthetic r=0.99 is not this evidence.
4. **Oracle/teacher quality** — human GT, separator envelopes, Essentia heads; licences split.
5. **CLEAN/STUDIO behaviour**
6. **Live/venue-domain robustness** — Amendment 002: CLEAN vs PA/ROOM vs PA/ROOM+CROWD; PaRIRset held-out venues intact.
7. **Licensing/provenance** — `mir/registry.yaml`. Teacher use ≠ derived-weight clearance.
8. **Visual utility** — Gates B then C. Bind `descriptor × mode × lever`. Mean brightness is not the default metric. A fail on one binding is not a global fail.
9. **U55 compressibility** — PRE-SILICON compile of a candidate graph (RUHMI), not Semantic-v0-synthetic authority. GHA 33319114336: `ad01_int8.tflite` and `smoke.onnx` both emitted C99. Receipt: `docs/ruhmi/COMPILE_RECEIPT.md`. Not ON-SILICON.

Do not freeze Student-v0 yet.

Evidence so far (HOST-ONLY, not a freeze):

- Real-audio incremental vs DSP: DEAM 2015 human arousal vs energy mean r=0.37, R²=0.30. Not Semantic-v0's r=0.99.
- Visual utility (A/B/C replay, not firmware): A = onset baseline; B = same extra DoF from RMS; C = same extra DoF from human arousal; w=0.65. Five 2015 songs (2030/2028 controls; 2034/2041/2056 residuals). `docs/mir/visual_replay/index.html`. Not a Captain LED judgement and not a student freeze.
- Live/venue: PaRIRset test-split convolution on three held-out venues. Unaligned onset r is low because the IRs inject ~100 ms delay, not because events vanish. Delay-aligned native-hop F1@50 ms recovers 0.05 → 0.86 (HOST-ONLY). Old “onset dies” reading **invalidated**. Residual smear remains (aligned F1 0.79–0.92). CrowdioSet not ingested. Receipt: `docs/mir/PARIRSET_ONSET_ALIGNED.md`.
- Source activity: P3-B full MUSDB18 n=150. Within-track r(drums_share, mix)=0.10 vs r(drums_abs, mix)=0.62. Vocals 0.17 vs 0.44. Bass 0.16 vs 0.64. **abs DEMOTE; share PASS incremental-info (Gate A).** P3-C dump close: **`source_share × WaveformTempo × head_position` HOST PASS (Gate B)** (holdout Δ partial r 0.63, 9/9). Waveform Tempo is a **reference continuity carrier**. **`composition_change × Comet × impact-launch` FAIL** this comparator. Gate C OPEN. Recoverability: tiny causal CNN 20 788 params, official MUSDB18 song-level test n=50, within-track r(pred,true) vocals/drums/bass = 0.64/0.57/0.54 vs mix-linear 0.13/0.19/0.20. HOST-ONLY. I/O not frozen. `docs/mir/SHARE_STUDENT.md`. Demucs not installed.
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
