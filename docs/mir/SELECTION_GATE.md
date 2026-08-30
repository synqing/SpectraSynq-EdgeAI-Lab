---
abstract: "Student-model selection gate. A U55 CNN may not be the primary target until these nine questions have evidence."
---

# Student-model selection gate

A small RA8P1/U55 student becomes the primary implementation target only after
**material evidence** for:

1. **Which descriptors** — still not frozen.
2. **Temporal rate / context** — still not frozen.
3. **Real-audio incremental information vs DSP** — DEAM human arousal vs energy (P1); source-activity vs mixture energy (P3). Synthetic r=0.99 is not this evidence.
4. **Oracle/teacher quality** — human GT, separator envelopes, Essentia heads; licences split.
5. **CLEAN/STUDIO behaviour**
6. **Live/venue-domain robustness** — Amendment 002: CLEAN vs PA/ROOM vs PA/ROOM+CROWD; PaRIRset held-out venues intact.
7. **Licensing/provenance** — `mir/registry.yaml`. Teacher use ≠ derived-weight clearance.
8. **Visual utility** — offline replay of `semantic_trace.jsonl` against lights **before** student training. If a perfect oracle does not improve lights, do not train.
9. **U55 compressibility** — PRE-SILICON compile of a candidate graph (RUHMI), not Semantic-v0-synthetic authority. GHA 33319114336: `ad01_int8.tflite` and `smoke.onnx` both emitted C99. Receipt: `docs/ruhmi/COMPILE_RECEIPT.md`. Not ON-SILICON.

Do not freeze Student-v0 yet.

Evidence so far (HOST-ONLY, not a freeze):

- Real-audio incremental vs DSP: DEAM 2015 human arousal vs energy mean r=0.37, R²=0.30. Not Semantic-v0's r=0.99.
- Visual utility (A/B/C replay, not firmware): A = onset baseline; B = same extra DoF from RMS; C = same extra DoF from human arousal; w=0.65. Five 2015 songs (2030/2028 controls; 2034/2041/2056 residuals). `docs/mir/visual_replay/index.html`. Not a Captain LED judgement and not a student freeze.
- Live/venue: PaRIRset test-split convolution on three held-out venues. Unaligned onset r is low because the IRs inject ~100 ms delay, not because events vanish. Delay-aligned native-hop F1@50 ms recovers 0.05 → 0.86 (HOST-ONLY). Old “onset dies” reading **invalidated**. Residual smear remains (aligned F1 0.79–0.92). CrowdioSet not ingested. Receipt: `docs/mir/PARIRSET_ONSET_ALIGNED.md`.
- Source activity: P3-B full MUSDB18 n=150. Within-track r(drums_share, mix)=0.10 vs r(drums_abs, mix)=0.62. Vocals 0.17 vs 0.44. Bass 0.16 vs 0.64. P3-A bass r=−0.22 was a 7 s artefact. Oracle-ranked 20-track A/B/C/D + event pages exist; not a lighting pass. Demucs not installed. `docs/mir/SOURCE_ACTIVITY.md`.
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
