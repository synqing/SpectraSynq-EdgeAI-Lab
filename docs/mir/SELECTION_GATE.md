---
abstract: "Student-model selection gate. A U55 CNN may not be the primary target until these eight questions have evidence."
---

# Student-model selection gate

A small RA8P1/U55 student becomes the primary implementation target only after:

1. **Which descriptors are useful to SpectraSynq visuals?** — not frozen. Working hypotheses below.
2. **Temporal rate / context?** — not frozen. Visual lane may be 5–50 Hz; DSP stays faster.
3. **Redundant with DSP?** — band energy, flux, onset, RMS: **probably yes** for “energy”. Source identity, affect, structure: **open**.
4. **Which require ML?** — not frozen.
5. **Teacher/oracle?** — candidates: HT-Demucs activity envelopes (weights licence **UNKNOWN**), MUSDB/MoisesDB stems (NC research), MTG heads on EffNet/MusiCNN (CC BY-NC-SA weights), DEAM (dynamic VA, CC, often NC).
6. **Licensing?** — see `mir/registry.yaml`. Research-only teachers must not silently become production.
7. **Compressible to MCU/NPU?** — Semantic-v0 graph shape is a *deployment* witness, not a *task* witness.
8. **Output representation?** — not frozen. Do not lock 3 sigmoids.

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
