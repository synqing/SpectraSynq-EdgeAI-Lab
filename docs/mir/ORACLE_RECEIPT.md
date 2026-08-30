---
abstract: "HOST-ONLY conventional MIR execution on synthetic contrast clips. Not musical evidence. Documents DSP vs Semantic-v0 redundancy and lag."
---

# Oracle receipt — 2026-08-30

**HOST-ONLY. SYNTHETIC eval corpus.** 8 × 8 s clips, 16 kHz. Extractors: librosa conventional + Semantic-v0 experiment (1 s window, 50% hop).

Not run: Essentia models, musicnn (TF1 blocked), MERT, MuQ, MAEST, HT-Demucs.

## What moved

On `drop` (pad until t=4 s, then percussion) — see [figures/drop.png](figures/drop.png):

- DSP `onset_env`, `rms`, `novelty` jump **at** 4 s and resolve individual hits.
- Semantic-v0 `drums` rises over ~0.5–1 s and **latches near 1.0**. It sees the regime change, not the hits.
- That lag is the 1 s context, not a bug in librosa.

On `quiet_loud`, v0 `drums` vs DSP `rms` correlation **0.99**. On that clip the CNN is an energy meter with extra steps.

## DSP vs v0 Pearson r (synthetic — not product)

| clip | bass vs band_low | drums vs onset | drums vs flux | vocals vs band_mid | drums vs rms |
| --- | --- | --- | --- | --- | --- |
| sparse_ambient | −0.37 | 0.10 | −0.12 | −0.04 | 0.50 |
| percussion_dense | 0.59 | 0.03 | −0.23 | 0.00 | 0.50 |
| bass_drone | −0.21 | 0.75 | 0.13 | −0.03 | 0.13 |
| vocal_like | −0.49 | −0.36 | −0.56 | **0.78** | −0.58 |
| drop | −0.64 | 0.61 | **0.86** | −0.55 | 0.09 |
| quiet_loud | −0.67 | −0.71 | −0.58 | 0.86 | **0.99** |
| irregular_hits | −0.39 | 0.41 | 0.39 | 0.48 | 0.38 |
| mixed_full | 0.14 | −0.07 | 0.36 | 0.37 | 0.27 |

## Reading (provisional)

1. Conventional MIR already encodes the drop and the hits. An NPU is not required for that.
2. Semantic-v0 on synthetic data often tracks **energy / midband**, not source identity. That is why synthetic F1 looked high.
3. Keep v0 as a U55-shaped experiment. Do not freeze it as the student until a **stem or separator teacher** is on the same traces.
4. Next execute (when env allows): Essentia DEAM head + MusiCNN taggram on **real CC audio**, not these sines.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-30 | agent:edgeai | First executed conventional oracle. |