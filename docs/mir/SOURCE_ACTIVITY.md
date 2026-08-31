---
abstract: "P3-B share ≠ mix. Bindings: source_share × WaveformTempo × head_position HOST PASS (holdout Δr=0.63, 9/9); composition_change × Comet × impact-launch FAIL. Tempo is a continuity carrier, not universal lighting proof. No Demucs. Student OPEN."
---

# Source activity — perfect oracle

Question: if we had perfect vocals/drums/bass information, what should the lighting engine actually consume?

Not:

```text
vocals_activity = RMS(vocal_stem)
```

Three channels per source:

| channel | meaning | range |
| --- | --- | --- |
| `*_abs` | how much energy this stem has (fixed log-RMS map, D7 constants) | [0, 1] |
| `*_share` | this stem’s power / sum of stem powers (dominance) | [0, 1], sums to 1 |
| `*_delta` | first difference of share (enter / exit / surge) | [−1, 1] |

Silence does not invent equal shares. `acoustic_path_delay_s` is a different variable (venue), not this oracle.

HPSS remains a cheap baseline, not ground truth. Demucs is **not** installed.

## P3-A — pipeline proof (this session)

Official `musdb.DB(download=True)` **7-second excerpts**. 140 MB, 144 tracks, into `datasets/musdb_sample/` (gitignored). **Not** the 4.7 GB corpus.

HOST-ONLY. Research/NC. `commercial_training_lineage: false`.

Synthetic unit tests (no recorded audio) prove share ≠ abs: the same vocal stem is dominant when alone and buried under loud drums. `tests/test_source_oracle.py`.

### vs mix energy (mean Pearson, n=144)

| source | r(abs, mix) | r(share, mix) |
| --- | ---: | ---: |
| vocals | 0.46 | **0.12** |
| drums | 0.42 | 0.25 |
| bass | 0.37 | **−0.22** |

Vocal *presence* still partly tracks loudness. Vocal *dominance* mostly does not. Bass dominance often **anti-correlates** with mix energy (bass in quieter texture). 96% of tracks: vocals_share is less redundant with mix than vocals_abs (Δr > 0.05). 76% for drums.

HPSS percussive vs drums_abs mean r=0.60 — a usable hint, not a teacher substitute.

Replay machinery: A/B/C/D with the **same** extra mix as arousal (`w=0.65`). 7 s is too short for a product lighting call. Open `docs/mir/visual_replay/source_abcd.html`. On Helado Negro / Hollow Ground the green dominance strip is not the blue mix strip.

### What this does **not** establish

- Perfect source information improves lights on full songs.
- A student can recover share from a mixture.
- HPSS or Demucs is good enough.
- Anything ON-SILICON.
- A commercial training right. MUSDB stays quarantined.

## P3-B — full MUSDB18 STEMS (not HQ)

Zenodo 1117372 `musdb18.zip` md5 `af06762477334799bfc5abf237648207`. 100 train + 50 test. HOST-ONLY. NC. `commercial_training_lineage: false`.

Fourth oracle channel: `composition_change` = causal L1/2 of the 4-share vector vs 0.5 s ago, hop-centre timestamps, no lookahead (D13).

The **oracle ranked** all 150 tracks. A balanced 20-song visual set was taken from the strongest events in five classes (4 each): vocal ownership change, drum ownership change, bass dominance, composition change without loudness change, loudness change without composition change (negative control). Seed names from P3-A are present in the corpus as sanity checks; they did **not** dictate the set.

### Within-track vs pooled Pearson vs mix energy (n=150)

| source | within r(abs, mix) | within r(share, mix) | pooled r(abs, mix) | pooled r(share, mix) |
| --- | ---: | ---: | ---: | ---: |
| vocals | 0.44 | **0.17** | 0.38 | 0.13 |
| drums | 0.62 | **0.10** | 0.60 | 0.09 |
| bass | 0.64 | **0.16** | 0.58 | 0.21 |

Drum *energy* largely tracks the mix. Drum *ownership* does not. That is the lighting-relevant within-track fact.

P3-A’s bass_share r=−0.22 **does not survive** full songs. It was a short-excerpt screening number. Do not quote it as product evidence.

Visual extra-DoF uses frozen corpus 5th–95th maps (`p3b-v1`), not per-song min-max.

- P3-B1 continuous: A / B mix / C abs / D share — `docs/mir/visual_replay/p3b1_continuous.html`
- P3-B2 events: |Δ mix| vs |share delta| vs composition_change — `docs/mir/visual_replay/p3b2_events.html`

Those pages are **information** evidence, not a lighting judgement. Condition A was an existing-behaviour stand-in. Do not train from them.

## P3-B gate stamps (information only)

| Quantity | Stamp | Why |
| --- | --- | --- |
| Source ABS | **DEMOTE** | Full-song within-track r vs mix: vocals 0.44, drums 0.62, bass 0.64. Source-specific, but behaves too much like another energy meter to be the principal new semantic. |
| Source SHARE | **PASS incremental-information** | Within-track r vs mix: vocals 0.17, drums 0.10, bass 0.16. Survives 150 full tracks. Musical ownership is a different class from acoustic energy. Not a product claim from r itself. |
| Composition-change | **PASS to visual-engine test** | Causal L1/2 of the four-share vector vs 0.5 s ago, [0,1], no lookahead. Objective arrangement-change, not an invented DROP label. |
| P3-B HTML lighting call | **NOT TAKEN** | Scalar diagnostic proxy. Not the K1 visual engine. |

The 20-track page is the **P3-B CHALLENGE SET** (oracle-ranked for green ≠ blue). It must not be the only visual material.

## P3-C — visual-engine oracle replay (HOST-ONLY)

Isolated replay of firmware **palette path** (not chroma HSV). Continuous engine is `light_mode_waveform_tempo` (tempo-locked scroll velocity, `effect_palette_or_chroma_colour`). Events are firmware `light_mode_comet` launches composited over that tempo floor. Palette is `K1_Ultraviolet_Bright`. Square-iter is 0 so the host linear dump is not crushed. A host sRGB/exposure preview makes the page readable; the dump is still pre-gamma. No production firmware edits. Host tempo is a locked 120 BPM phase from frame time, identical across versions.

Captain asked for Waveform Tempo after a Spectrum River pass that was visually usable. River remains a valid host mode; it is not the P3-C continuous engine.

The first P3-C pass used chromatic bloom + PHOTONS² and was unreadable. That is rejected as a lighting instrument.

Same extra degree of freedom, high floor so versions can be seen:

- A / B / D = same Waveform Tempo; extra gain in [0.62, 1.0] on peak + chroma from constant / frozen mix / frozen share
- P3-C2 = same comet launch over that tempo floor; control trigger `|Δ mix|`, MIR trigger `composition_change`

20 clips: 10 challenge (from the P3-B oracle set) + 10 MUSDB **test** holdout tracks stratified by duration quartile, **not** by share/RMS disagreement.

HOST chroma is a causal 12-bin STFT on the oracle hop grid. Identical across versions before extra gain. Not firmware GDFT. One second of warmup precedes each clip. Host frame rate is 31.25 Hz (device AP is 133 Hz).

### P3-C quantitative close (dumps, not eyes)

The close is on LED buffers vs the source oracle. Captain is not the validator. Circular trap: raw r(pixels, share) is not a pass, because D was driven by share. The extra-DoF test is whether D's **wave head position** tracks share after mix RMS is partialled out, compared with B.

| Gate | Holdout stamp | Number |
| --- | --- | --- |
| Q1 knob is head position | **PASS** | Spearman(position, extra gain) 0.68 |
| Q2 share increment in pixels | **PASS** | partial r D 0.68 vs B 0.04; Δ 0.63; 9/9 clips |
| Q3 source abs after mix | **PASS** | Δ 0.45; 9/9 (abs was not the driver) |
| Q4 `composition_change × WaveformTempo × head_position` | **FAIL this comparator** | Δ partial r 0.06 — arrangement is not a continuous head-position signal |
| Q5 `composition_change × Comet × impact-launch` | **FAIL this comparator** | F1 delta 0.02 vs `|Δ mix|` at drum attacks |

Stamps (bound, not global):

| Binding | Stamp |
| --- | --- |
| `source_share × WaveformTempo × head_position` | **HOST PASS** |
| `composition_change × Comet × impact-launch` | **FAIL this comparator** |
| composition_change as a descriptor | **not decided** — wrong instrument for arrangement-state |
| Student share head | **CANDIDATE**, not frozen |
| Event head | **NO** |
| Demucs | **NO** |
| Student gate | **OPEN** |

Waveform Tempo is a **reference continuity carrier**.

- Scorer: `uv run python scripts/p3c_quant_score.py`
- Receipt: `docs/mir/P3C_QUANT.json`
- Chart: `docs/mir/figures/p3c_quant_share.png`
- Continuous page (reference, not the close): `docs/mir/visual_replay/p3c1_continuous.html`
- Events page (reference, not the close): `docs/mir/visual_replay/p3c2_events.html`

If share had failed Q2/Q3 on holdout: do not train a dominance student. It passed **Gate B on this binding**. Gate A already passed. Gate C (physical show) is still OPEN.

Share-student recoverability is **HOST PASS** (21k CNN, four-source including `other`). Programme stamp: **PRE-PRODUCT FEASIBILITY PASS**. Next is Gate C, not another network. Waveform Tempo remains the continuity/reference replay.

**Composition-change implementation is parked.** It is a deterministic function of share(t) vs share(t−Δ). No extra ML head. Atlas may find a macro-transition grammar or record a visual-language gap. Replaying the existing oracle through a new binding does not need new neural work.

Demucs only after recoverability, for unstemmed scale.

Re-run: `uv run python scripts/download_musdb.py --fetch` then `uv run python scripts/musdb18_p3b.py` then `uv run --extra musdb python scripts/musdb18_p3c.py`. Requires `SPECTRASYNQ_K1_FIRMWARE` (or the workstation checkout) and g++-15.

Re-run: `uv run python scripts/download_musdb.py --fetch` then `uv run python scripts/musdb18_p3b.py`. Receipt: `artifacts/source_activity/receipt_musdb18_p3b.json`.

Older HPSS-on-DEAM numbers remain a mixture-only baseline, not stem truth.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-30 | agent:edgeai | HPSS probe on three DEAM songs. |
| 2026-08-31 | agent:edgeai | P3-A MUSDB samples; abs/share/delta; share ≠ mix energy. |
| 2026-08-31 | agent:edgeai | P3-B 150 full tracks; oracle-ranked 20; within-track share vs mix. |
| 2026-08-31 | agent:edgeai | P3-B stamps: abs demoted, share info-PASS; P3-C bloom+PHOTONS blinded replay. |
| 2026-08-31 | agent:edgeai | P3-C continuous engine swapped to firmware Waveform Tempo on the palette path. |
| 2026-08-31 | agent:edgeai | P3-C quantitative close: share extra-DoF PASS in wave position; composition-change comets FAIL. |
| 2026-08-31 | agent:edgeai | FAIL narrowed to composition_change × Comet × impact-launch; Tempo is a continuity carrier. |
| 2026-08-31 | agent:edgeai | Share student unblocked; composition-change ML parked; Gate C OPEN. |
| 2026-08-31 | agent:edgeai | Feasibility PASS stamp; Gate C next; no hop-level student. |
