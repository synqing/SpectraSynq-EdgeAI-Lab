---
abstract: "P3 HOST-ONLY: HPSS envelopes vs mix RMS on DEAM. Not r=0.99. Demucs not installed. No student."
---

# Source-activity teacher — first probe

Question: does source identity/activity add information beyond mixture energy?

HT-Demucs is **not installed** here. MSST unused. No separator training. No U55.

Always-on baseline: librosa HPSS → RMS envelopes of harmonic / percussive vs mix.

| song | r(perc, mix RMS) | r(harm, mix RMS) | r(arousal, perc) | r(arousal, mix) |
| --- | --- | --- | --- | --- |
| 2030 | 0.79 | 0.79 | 0.23 | 0.23 |
| 2034 | 0.67 | 0.81 | 0.34 | 0.26 |
| 2041 | 0.50 | 0.89 | 0.36 | 0.33 |

This is **not** the Semantic-v0 synthetic drums-vs-RMS r=0.99 failure. Percussive envelope on 2041 is only half-redundant with mix energy.

It is also **not** a Demucs/RoFormer teacher yet. Next time a neural separator is brought up, the bar is: envelopes must beat HPSS *and* mix RMS on real audio, then survive PaRIRset.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-30 | agent:edgeai | HPSS probe on three DEAM songs. |
