---
abstract: "P1 HOST-ONLY: human DEAM 2 Hz arousal vs deterministic DSP on real CC music. Not r=0.99 with RMS. Gate still open."
---

# DEAM human arousal vs DSP — 2026-08-30

Canonical DEAM files (not mirdata). 82 tracks with local audio: 24 × 2013 45 s clips + **58 × 2015 full songs** (manual: dynamic arousal more reliable in 2015).

Human annotations at 2 Hz, starting ~15 s. DSP from librosa, interpolated onto that grid.

## Headline

On the 2015 full-song cohort, human arousal is **not** an energy meter.

| cohort | n | mean r(arousal, RMS) | mean R² energy (RMS+bands) | mean R² DSP full |
| --- | --- | --- | --- | --- |
| 2013_clip | 24 | −0.04 | 0.11 | 0.15 |
| **2015_full** | **58** | **0.37** | **0.30** | **0.34** |

Contrast with Semantic-v0 synthetic drums vs RMS **r = 0.99**. That falsifier does **not** repeat on human arousal.

Energy still explains *some* songs (e.g. 2030 r_rms=0.81, R²_energy=0.76). Others barely (2034, 2041, 2049, 2056: R²_energy < 0.04). Those are the clips a visual A/B should use first.

Adding flux/onset/novelty only lifts mean R² 0.30 → 0.34 on 2015. Most of the human series is still unexplained by this DSP set.

**Interpretation:** arousal remains a live semantic-lane hypothesis.

P5 visual replay (HOST-ONLY, not firmware): A/B/C with the **same** extra mix (`w=0.65`). A = onset baseline; B = extra DoF from RMS; C = extra DoF from human arousal. Controls 2030/2028; residuals 2034/2041/2056. On 2034, C is a slow arc that B does not reproduce. That is the kill-test shape — not a Captain eyes-on of LEDs. See `docs/mir/figures/visual_oracle_replay.png` and `docs/mir/visual_replay/index.html`.

Do not train a student until a product lighting evaluator says C beats B. This lab's replay is the control plot, not a production lighting A/B.

P2 Essentia MusiCNN + `deam-msd-musicnn-2` (CC BY-NC-SA weights) ran on 2030 and 2034. Patch-wise predicted arousal vs human 2 Hz: r ≈ −0.08 and −0.15. That is **not** a freeze: hop/scale alignment may be wrong; two songs. It is enough to say the head is not an automatic substitute for the human series.

Licence: DEAM research; commercial UNKNOWN. Traces in `artifacts/deam_arousal/traces/` (gitignored).

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-30 | agent:edgeai | P1 executed on 82 DEAM files. |
| 2026-08-30 | agent:edgeai | P5 disagreement plot for 2030 vs 2034. |
| 2026-08-31 | agent:edgeai | A/B/C control: same extra DoF, five 2015 songs. |
