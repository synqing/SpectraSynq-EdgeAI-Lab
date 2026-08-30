---
abstract: "Student-model selection gate. A U55 CNN may not be the primary target until these eight questions have evidence."
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
9. **U55 compressibility** — PRE-SILICON compile of a candidate graph (RUHMI), not Semantic-v0-synthetic authority.

Do not freeze Student-v0 yet.

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
