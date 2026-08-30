---
abstract: "P2 HOST-ONLY: native Essentia-TF oracles. DEAM head vs human 2 Hz is not a substitute. Jamendo mood means differ across songs; temporal std often tiny."
---

# Essentia host oracles

Weights: CC BY-NC-SA. Native Apple-silicon `essentia_tensorflow`. Not TF1 `musicnn`. Not Titan.

## DEAM VA head (`deam-msd-musicnn-2` on MusiCNN embeddings)

On 2030 / 2034, predicted arousal vs human 2 Hz: r ≈ −0.08 / −0.15. Not a freeze: hop/scale may be wrong; two songs. Not an automatic substitute for the human series.

## Jamendo mood/theme (`discogs-effnet-bs64` + `mtg_jamendo_moodtheme-discogs-effnet-1`)

Watch slice means:

| song | energetic | relaxing | happy | dark |
| --- | --- | --- | --- | --- |
| 2030 | 0.223 | 0.016 | 0.036 | 0.090 |
| 2034 | 0.022 | 0.070 | 0.100 | 0.016 |

2030 reads more energetic; 2034 more relaxing/happy. Temporal std on 2034 energetic is 0.009 — almost clip-level. Weak for drop-scale lighting unless a later windowing study shows otherwise.

No MAEST/MERT/MuQ.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-30 | agent:edgeai | DEAM head + Jamendo mood on two songs. |
