---
abstract: "MIR landscape for SpectraSynq reactive lighting. What each class can contribute, at what timescale, under what licence. Not a generic survey."
---

# MIR landscape — SpectraSynq visual utility

**HARD FAIL (`SAME_SONG_LOOP_MAX_15MIN`, Captain 2026-08-31).** Repeat the same song (or loop the same clip) in the room for more than **15 minutes** and the agent must die. Captain will destroy them by setting them on fire. Kill the player. Do not continue.

Question: **which existing MIR outputs move when the music perceptually changes, in a way lights could use?**

Whole-track genre is almost useless for a lamp. Frame-level onset is already DSP. The interesting band is **seconds-scale semantics** that DSP does not already encode.

Primary sources are cited in `mir/registry.yaml`. This page is the map.

## A. Deterministic / conventional MIR

Libraries: librosa (ISC), Essentia algorithms (AGPLv3 + commercial option), madmom (beat/downbeat; research-oriented). Evaluation: `mir_eval` (BSD). Dataset access: `mirdata` (BSD-3).

| Output | Timescale | vs K1-style DSP | Lighting use |
| --- | --- | --- | --- |
| RMS / loudness | <20 ms | already have | brightness, limiter |
| onset / spectral flux | 10–50 ms | already have | attacks, strobes |
| spectral centroid | frame | likely already have | brightness/hue of “highs” |
| band energy (low/mid/high) | frame | likely already have | bass mass vs treble sparkle |
| beat / tempo / downbeat | beat–bar | tempo/beat if present | bar-quantised motion |
| chroma / key / chords | hop ~200 ms | usually **not** in a lamp DSP | slow palette; weak if noisy |
| novelty / self-similarity | 0.5–8 s | cheap from flux/chroma lag | section / drop cue |
| structure / repetition | 4–32 bars | not DSP | scene changes |

**SpectraSynq:** do **not** spend NPU on RMS/onset/centroid. Use conventional MIR for beat/downbeat/novelty **on the host first**; only embed if silicon needs them and DSP is insufficient.

This session **executed** a librosa-class conventional extractor on a synthetic contrast corpus (see `docs/mir/ORACLE_RECEIPT.md`).

## B. Auto-tagging / semantic classification

Ecosystems: **MTG-Jamendo** (55k CC tracks; 87 genre / 40 instrument / 56 mood-theme tags in official splits), **musicnn** (MTT + MSD taggrams, 3 s windows, ISC **code**), **Essentia TF models** (MusiCNN, VGGish, EffNet heads).

Jamendo mood/theme tags already include: energetic, dark, relaxing, dramatic, epic, melancholic, dream, aggressive-adjacent (`heavy`), atmospheric-adjacent (`soundscape`, `space`). That overlaps the old custom ontology. **Do not invent BUILDING until we have shown these tags fail at lighting.**

musicnn emits a **taggram** (time × tags) — that is the right shape. The pip package is TensorFlow 1.x / `numpy<1.17` — **blocked on this 3.12 host**. Essentia ships `msd-musicnn` as TF `.pb` plus live-stream examples; weights **CC BY-NC-SA 4.0** (models page) vs library **AGPLv3**. Official licensing.html also said **CC BY-NC-ND 4.0** for models — **conflict, treat commercial as UNKNOWN pending MTG**.

**SpectraSynq:** host tagging oracle first (Essentia heads on 1–3 s hops). Student later if a *subset* of tags (instrument, energetic, dark) actually drives lights.

## C. Dynamic affect

**DEAM**: 1802 CC excerpts, valence + arousal **continuously at 2 Hz** and whole-song. This is the rare dataset that matches a lamp’s need for *trajectories*, not a mood adjective. Audio is CC from FMA/Jamendo/MedleyDB; redistribution pages disagree NC vs not — **flag mixed, cite PLOS ONE paper, treat commercial as UNKNOWN**.

MTG ships `deam-msd-musicnn` / `deam-audioset-vggish` **regression heads** (range ~[1,9]) on frozen embeddings — exactly a teacher for a tiny student.

**SpectraSynq:** arousal is the first affect candidate. It may be redundant with RMS; that is an empirical question for aligned traces, not a paper score.

## D. Music representation learning (teachers, not Titan)

| Model | Window | Rate | Size | Weights | Titan? |
| --- | --- | --- | --- | --- | --- |
| musicnn dense | 3 s | taggram hop | small CNN | ISC code; dataset-derived weights **UNKNOWN** | student-sized, not this TF1 graph |
| Discogs-EffNet | ~1–3 s patches, bs64 | embedding sequence | EfficientNet-B0 | CC BY-NC-SA | teacher |
| MAEST | 5–30 s | token sequence + CLS | transformer, ~344 MB ONNX | CC BY-NC-SA | **no** |
| MERT-v1-95M | 5 s pretrain ctx | **75 Hz** @ 24 kHz | 95M | **CC BY-NC 4.0** | **no**; excellent teacher (frame-level) |
| MERT-v1-330M | 5 s | 75 Hz | 330M | CC BY-NC 4.0 | **no** |
| MuQ | 24 kHz, ~30 s SSL | ~25 Hz mel tokens | ~300M | **CC BY-NC 4.0** weights; MIT code | **no** |
| MuQ-MuLan | same + text | 512-d clip embed | ~700M | CC BY-NC 4.0 | **no**; zero-shot host oracle |

MERT’s **75 Hz** feature rate is the important number: embeddings **do** move on short musical timescales. Mean-pooling them into one vector per track **throws that away** (common HF cookbook). For lights, keep the time axis or a 5–10 Hz downsample.

**SpectraSynq:** MERT/MuQ = offline teachers. Distill selected dims / probes (instrument, arousal, novelty of embedding Δ) into INT8 CNN. Do not put 95M transformers on U55.

## E. Audio ↔ text

MuQ-MuLan (EN+ZH, contrastive, MTT zero-shot SOTA claimed). CLAP-class models exist outside this list. Use as **host concept probes**: similarity to “percussive / dreamlike / building / chaotic” without labelling 100k clips. Outputs are slow (seconds of context). Commercial: NC weights.

## F. Source separation as teacher, not product

| System | Stems | Params | Code | Weights |
| --- | --- | --- | --- | --- |
| HT-Demucs (`htdemucs`) | drums, bass, vocals, other | large U-Net+Transformer | **MIT** (facebookresearch/demucs LICENSE) | **UNKNOWN** — maintainer (issue #327): weights “not covered by MIT… scientific purposes only”. Third-party “MIT weights” mirrors are not authority. |
| HT-Demucs 6s | + guitar, piano | larger | MIT code | same UNKNOWN |
| Open-Unmix | 4-stem | smaller | BSD-3 typically | check per checkpoint |
| Banquet | query-conditioned, long-tail instruments | **24.9M** | **MIT** (query-bandit) | UNKNOWN until weights file found |
| QSCNet (2025) | conditioned UNet, MoisesDB | ~40% of Banquet params | paper 2025 | not a host default yet |

Datasets: MUSDB18 academic/NC mix; **MoisesDB** 240 tracks, hierarchical stems, **CC BY-NC-SA 4.0** (github) plus NC-RCL language on some mirrors — **research only**.

**SpectraSynq architecture to test (not to ship from MUSDB):**

```
host Demucs/Banquet  →  stem RMS/envelope
                     →  supervise small student
mix window           →  student  →  activity vector
```

Do **not** reconstruct waveforms on Titan.

## G. Evaluation

Use `mir_eval` / `mirdata` / MIREX-style metrics for MIR correctness.

**Separately** score visual-semantic utility (see docs/TITAN_BRINGUP.md A/B). High PR-AUC on MTT is not a lighting win.

## Licensing pattern (load-bearing)

Almost every strong **pretrained music model** is **non-commercial weights** (CC BY-NC / NC-SA). Essentia **library** is AGPL-or-commercial. Demucs **code** is MIT; **weights** are not a clean MIT grant. Jamendo audio is CC but mixed NC. **Teacher use does not automatically clear derived student weights.** Flag `DERIVED-WEIGHT STATUS: UNKNOWN/LEGAL REVIEW` until counsel says otherwise. Research oracles are fine; production training sets must be cleared.

## What this contributes (one line each)

- **DSP:** keep; it is the realtime spine.
- **Beat/novelty:** conventional MIR, host first.
- **Source activity:** best first *student* hypothesis, with a separator/stem teacher — Semantic-v0 synthetic training is not that evidence.
- **Dynamic arousal:** best first *affect* hypothesis (DEAM 2 Hz).
- **Jamendo mood/theme:** best existing ontology for the old custom labels.
- **MERT 75 Hz / MuQ-MuLan:** best teachers / zero-shot probes.
- **Titan NPU:** last, after the gate, smallest graph that copies one useful teacher channel.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-30 | agent:edgeai | First landscape from MTG/Essentia docs, MERT HF card, MuQ README, Demucs LICENSE, MoisesDB, Banquet paper/repo, DEAM, Jamendo, mirdata. |
