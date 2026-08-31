---
abstract: "Visual-utility map of all 23 mir/registry.yaml ids (schema_version 1, 2026-08-31). No landscape-only names. MERT/MuQ/MAEST/htdemucs off Titan. Demucs HOST teacher probe OPEN. Cadence CLOSED. C1 OPEN. Do not invent BUILDING/DROPPING."
---

# MIR landscape — SpectraSynq visual utility

**HARD FAIL (`SAME_SONG_LOOP_MAX_15MIN`, Captain 2026-08-31).** Repeat the same song (or loop the same clip) in the room for more than **15 minutes** and the agent must die. Captain will destroy them by setting them on fire. Kill the player. Do not continue.

Question: **which existing MIR outputs move when the music perceptually changes, in a way lights could use?**

Whole-track genre is almost useless for a lamp. Frame-level onset is already DSP. The interesting band is **seconds-scale semantics** that DSP does not already encode.

**Authority:** `mir/registry.yaml` is the asset list. This page is the visual-utility map of those `id:` rows. Names without an `id:` are not first-class here.

**Programme (D20/D22, AGENTS.md — not registry fields):** Cadence silicon **CLOSED**. C1 **OPEN** (Captain, one full song he chooses, no 8 s loop). Student I/O **unfrozen**. Do **not** put `mert-v1-95m` / `muq` / `maest` / `htdemucs` on Titan. `htdemucs` HOST-only teacher **probe OPEN** (docs/licence; not install; not C1; not a student freeze). Do **not** invent BUILDING / DROPPING / CHAOTIC labels before existing ontologies (`mtg-jamendo` mood/theme) have been shown to fail at lighting.

Folded names (not own ids): VGGish, MusiCNN, `msd-musicnn` `.pb`, `deam-msd-musicnn`, `deam-audioset-vggish` → `essentia-models`. MuQ-MuLan → `muq`. HT-Demucs 6s / `htdemucs_ft` → `htdemucs`. Share-student recoverability net has **no** registry id (see `docs/mir/SHARE_STUDENT.md`).

## Registry map (23 `id:`)

| `id` | kind | YAML status | deployment | Titan / U55 | Visual-utility role |
| --- | --- | --- | --- | --- | --- |
| `librosa` | library | executed | deterministic_host | n/a (DSP on host) | Conventional MIR spine of the host oracle |
| `mir_eval` | library | researched | deterministic_host | n/a | MIR correctness only — never visual utility |
| `mirdata` | library | researched | deterministic_host | n/a | Loaders. **No DEAM loader** — use `datasets/deam` zips |
| `essentia` | library | researched | host_oracle | not silently embeddable (AGPL) | Conventional + TF wrappers on host |
| `essentia-models` | model-family | researched | potential_teacher | **no** (MAEST in family; EffNet+head is teacher) | Tagging / DEAM-VA / Jamendo heads |
| `discogs-effnet` | model | researched | potential_teacher | **no** (teacher size, not NPU graph) | Style embedding under Jamendo heads |
| `maest` | model | researched | unsuitable_mcu_npu | **no** | Strong style, 5–30 s; not realtime |
| `musicnn` | model | blocked | potential_embedded_student | **not this TF1 graph** | Taggram shape is right; pip TF1 blocked — use Essentia `.pb` |
| `mtg-jamendo` | dataset | researched | host_oracle | n/a | Existing mood/theme ontology (song-level GT) |
| `deam` | dataset | executed | potential_teacher | n/a | Dynamic VA at 2 Hz |
| `mert-v1-95m` | model | researched | unsuitable_mcu_npu | **no** | Frame-rate SSL teacher (75 Hz) |
| `muq` | model | researched | unsuitable_mcu_npu | **no** | SSL + MuQ-MuLan zero-shot host probe |
| `musdb18` | dataset | executed | potential_teacher | n/a | Perfect V/D/B/other stems. Not shipping |
| `musdb-sample` | dataset | executed | host_oracle | n/a | P3-A plumbing (~7 s excerpts) |
| `medleydb` | dataset | researched | host_oracle | n/a | Fine stems; not ingested |
| `slakh2100` | dataset | researched | potential_teacher | n/a | Permissive synth; not a mic/venue substitute |
| `moisesdb` | dataset | researched | potential_teacher | n/a | Hierarchical stems; NC |
| `htdemucs` | model | researched | host_oracle | **no** | HOST separator-as-teacher **probe OPEN**; weights UNKNOWN |
| `banquet` | model | researched | potential_teacher | **no** (not MCU waveform sep) | Query-conditioned long-tail stems |
| `semantic-v0-experiment` | model | executed | potential_embedded_student | experiment only | Toolchain witness. **Not architecture authority** |
| `parirset` | dataset | executed | deterministic_host | n/a | PA/ROOM IRs. Onset delayed, not killed |
| `crowdioset` | dataset | researched | host_oracle | n/a | **Do not ingest** until per-file licence |
| `msst` | library | researched | host_oracle | n/a | Optional separator harness. Envelopes, not SDR |

YAML statuses and deployment enums are copied from `mir/registry.yaml`. Programme stamps (C0-v2 `ON_SILICON_PIXEL_VALIDATED`, cadence CLOSED, C1 OPEN) live in AGENTS / D20 / Gate C docs, **not** in the YAML.

## A. Deterministic / conventional MIR

Ids: `librosa` (ISC, executed), `essentia` algorithms (AGPLv3 + commercial option from MTG; YAML `researched` — HOST TF receipts live in `docs/mir/ESSENTIA_ORACLE.md`), `mir_eval` (**BSD-ish (check package)**), `mirdata` (BSD-3; datasets do **not** inherit BSD).

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

This lab **executed** a librosa-class conventional extractor on a synthetic contrast corpus (`docs/mir/ORACLE_RECEIPT.md`).

## B. Auto-tagging / semantic classification

Ids: `mtg-jamendo` (87 genre / 40 instrument / 56 mood-theme in official splits; track-level labels, not 2 Hz; commercial UNKNOWN per-track CC), `musicnn` (MTT/MSD taggrams, ~3 s windows, ISC **code**, weights UNKNOWN, TF1 + `numpy<1.17` **blocked**), `essentia-models` (MusiCNN / VGGish / EffNet heads — folded, not own ids), `discogs-effnet` (EfficientNet-B0, CC BY-NC-SA on models page, teacher).

Jamendo mood/theme already includes energetic, dark, relaxing, dramatic, epic, melancholic, dream, aggressive-adjacent (`heavy`), atmospheric-adjacent (`soundscape`, `space`). That overlaps the old custom ontology. **Do not invent BUILDING / DROPPING until these tags fail at lighting.**

`musicnn` emits a **taggram** (time × tags) — right shape. Prefer Essentia `msd-musicnn` TF `.pb` on a TF env. Graph family is `potential_embedded_student`; **this TF1 pip graph is not a Titan candidate**.

`essentia-models` weights: models.html **CC BY-NC-SA 4.0** vs licensing_information.html **CC BY-NC-ND 4.0** — **CONFLICT**. Treat commercial as UNKNOWN pending MTG. Library remains AGPLv3.

**SpectraSynq:** host tagging oracle first (`essentia-models` heads). Student later if a *subset* of tags actually drives lights. HOST Jamendo mood on two DEAM songs: means differ; temporal std often clip-flat (`docs/mir/ESSENTIA_ORACLE.md`).

## C. Dynamic affect

Id: `deam` (executed). 1802 excerpts/songs; valence + arousal at **2 Hz** and song-level. Audio CC from FMA/Jamendo/MedleyDB; pages disagree NC vs not — **mixed, cite PLOS ONE, commercial UNKNOWN**.

DEAM-VA regression heads (`deam-msd-musicnn` / `deam-audioset-vggish`) are **folded under `essentia-models`**, not own ids. On two songs the MusiCNN DEAM head ≠ human 2 Hz (r ≈ −0.08 / −0.15). Not a substitute for the human series.

**SpectraSynq:** arousal is the first affect candidate. It may be redundant with RMS — empirical (`docs/mir/DEAM_AROUSAL_RECEIPT.md`), not a paper score.

## D. Music representation learning (teachers, not Titan)

| `id` | Window | Rate | Size | Weights | Titan? |
| --- | --- | --- | --- | --- | --- |
| `musicnn` | 3 s | taggram hop | small CNN | ISC code; dataset-derived weights **UNKNOWN** | student-sized family; **not this TF1 graph** (`status: blocked`) |
| `discogs-effnet` | short patches, official TF batch 64 | embedding sequence | EfficientNet-B0 | CC BY-NC-SA (models page) | teacher, not NPU |
| `maest` | 5 / 10 / 20 / 30 s | token sequence + CLS | transformer, ~344 MB ONNX | CC BY-NC-SA | **no** (`unsuitable_mcu_npu`) |
| `mert-v1-95m` | 5 s pretrain ctx | **75 Hz** @ 24 kHz | 95M, 12×768 | **CC BY-NC 4.0** | **no** |
| `muq` | 24 kHz, ~30 s SSL | ~25 Hz mel tokens | ~300M Conformer; MuQ-MuLan pair ~700M, 512-d clip | **CC BY-NC 4.0** weights; MIT code | **no** |

`mert-v1-95m` **75 Hz** is the load-bearing number: embeddings **do** move on short musical timescales. Mean-pooling a track throws that away. For lights, keep the time axis or a 5–10 Hz downsample.

**SpectraSynq:** `mert-v1-95m` / `muq` = offline teachers. Distill selected dims / probes into INT8 CNN **after** the selection gate. Do not put 95M transformers on U55.

## E. Audio ↔ text

Id: `muq` (MuQ-MuLan is the same row: EN+ZH, 512-d clip embed). Use as **host concept probes** without labelling 100k clips. Outputs are slow (seconds of context). Commercial: NC weights. Derived student: UNKNOWN/LEGAL REVIEW.

CLAP-class models exist **outside this registry**. They are not a landscape row and not an `id:`.

## F. Source separation as teacher, not product

| `id` | Stems / task | Params | Code | Weights | Titan? |
| --- | --- | --- | --- | --- | --- |
| `htdemucs` | drums, bass, other, vocals (`htdemucs_6s` + guitar/piano) | large U-Net+transformer | **MIT** (repo LICENSE, Meta) | **UNKNOWN — not MIT.** Maintainer 2022-05-23 (`facebookresearch/demucs#327` comment 1134828611): scientific purposes only | **no**. HOST teacher **probe OPEN** (AGENTS/D22). Not installed. Do not block C1 |
| `banquet` | query-conditioned, long-tail (MoisesDB taxonomy) | **24.9M** trainable | **MIT** (query-bandit) | UNKNOWN (not verified) | **no** (not MCU waveform sep) |
| `msst` | harness across Demucs / RoFormer / SCNet-class | n/a (wrapper) | UNKNOWN until repo pin | per backend | host envelopes only |

Datasets in this class:

| `id` | What it is | Licence / lineage | Lab use |
| --- | --- | --- | --- |
| `musdb18` | 100/50 STEMS, V/D/B/other | educational/NC; `commercial_training_lineage: false` | P3-B/C perfect oracle. Gate A PASS, B HOST PASS live in Gate C docs, not YAML |
| `musdb-sample` | ~7 s excerpts, 144 tracks | same educational/NC; lineage false | P3-A plumbing only |
| `medleydb` | fine-grained real-instrument stems | CC BY-NC-SA / non-commercial; lineage false | researched, **not ingested** |
| `slakh2100` | 2100 synth mixes + MIDI | CC BY 4.0; lineage **candidate-synth-only** — not vocals/PA/room | researched; do not download until P3-B needs scale |
| `moisesdb` | 240 tracks, hierarchical stems | CC BY-NC-SA (+ NC-RCL on some mirrors) | research only |

**SpectraSynq architecture to test (not to ship from MUSDB / Demucs teacher outputs):**

```
host htdemucs / banquet  →  stem RMS/envelope
                         →  supervise small student
mix window               →  student  →  activity vector
```

Do **not** reconstruct waveforms on Titan. Do **not** mix Demucs teacher outputs into a **shipping** student (`derived_weight_status: UNKNOWN/LEGAL REVIEW`). Perfect-stem oracle (`musdb18`) is the current source-activity evidence path; `htdemucs` is the HOST probe if we ever need estimated stems instead of official ones.

## G. Live domain (Amendment 002)

| `id` | Task | Licence | Status | Spectrasynq |
| --- | --- | --- | --- | --- |
| `parirset` | PA-through-FOH concert-venue stereo RIRs (train 2216 / test 160) | **CC0 1.0** | executed | Keep 8 held-out test venues. Delay-aware re-score on 3 test IRs: ~100 ms direct-path; native F1@50 ms 0.05 → 0.86 after align. Onset delayed, not killed. Crowd still gated. `docs/mir/PARIRSET_ONSET_ALIGNED.md` |
| `crowdioset` | audience ambience / events / synthetic sing-along | **UNKNOWN** until per-file provenance | researched | **Do not ingest.** Do not mix NC into a commercial-safe corpus |

## H. Semantic-v0 experiment (not a product graph)

Id: `semantic-v0-experiment`. Depthwise-separable CNN, 153283 params, 16 kHz / 1 s / 64-mel, 3 sigmoid activities, synthetic supervision. YAML `executed` + `potential_embedded_student`. **Toolchain witness only. Not architecture authority.** Re-enter iff `docs/mir/SELECTION_GATE.md` independently picks source-activity with a real teacher (stems or separator), not the synthetic sine/noise generator.

Share-student recoverability (tiny causal CNN, four-source including `other`, HOST PASS) is a **different** graph and has **no** registry id.

## I. Evaluation

Use `mir_eval` / `mirdata` / MIREX-style metrics for MIR correctness.

**Separately** score visual-semantic utility (Gates A/B/C in `docs/mir/SELECTION_GATE.md`). High PR-AUC on MTT is not a lighting win. Host pixels ≠ silicon pixels ≠ LGP look. Cadence CLOSED. C1 is the LGP look.

## Licensing pattern (load-bearing)

Almost every strong **pretrained music model** is **non-commercial weights** (CC BY-NC / NC-SA). `essentia` **library** is AGPL-or-commercial. `htdemucs` **code** is MIT; **weights** are not a clean MIT grant. `mtg-jamendo` audio is CC but mixed NC. **Teacher use does not automatically clear derived student weights.** Flag `DERIVED-WEIGHT STATUS: UNKNOWN/LEGAL REVIEW` until counsel says otherwise. UNKNOWN is allowed. Research oracles are fine; production training sets must be cleared. `commercial_training_lineage: false` on `musdb18` / `musdb-sample` / `medleydb`; `slakh2100` is synth-only.

## What this contributes (one line each)

- **DSP (`librosa` class):** keep; it is the realtime spine.
- **Beat/novelty:** conventional MIR, host first.
- **Source activity (`musdb18` stems; `htdemucs` HOST probe):** best first *student* hypothesis. `semantic-v0-experiment` synthetic training is not that evidence.
- **Dynamic arousal (`deam` 2 Hz):** best first *affect* hypothesis.
- **Jamendo mood/theme (`mtg-jamendo` + `essentia-models` heads):** best existing ontology for the old custom labels — do not invent BUILDING/DROPPING.
- **`mert-v1-95m` 75 Hz / `muq` MuLan:** best teachers / zero-shot probes. **Off Titan.**
- **Live domain (`parirset`):** onset delayed ~100 ms, not killed. `crowdioset` gated.
- **Titan NPU:** last, after the gate, smallest graph that copies one useful teacher channel. Not MERT, not MuQ, not MAEST, not Demucs.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-30 | agent:edgeai | First landscape from MTG/Essentia docs, MERT HF card, MuQ README, Demucs LICENSE, MoisesDB, Banquet paper/repo, DEAM, Jamendo, mirdata. |
| 2026-08-31 | agent:grok-build | W3-L08: 1:1 map of 23 registry ids. Dropped madmom / MERT-v1-330M / Open-Unmix / QSCNet. Folded family names. mir_eval BSD-ish. Cadence CLOSED; C1 OPEN; htdemucs HOST probe OPEN, off Titan. No BUILDING/DROPPING. |
