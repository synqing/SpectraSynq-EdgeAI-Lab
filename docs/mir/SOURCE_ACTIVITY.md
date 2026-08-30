---
abstract: "P3-B information gate: share ≠ mix (within r 0.10–0.17). abs demoted. P3-C is firmware bloom + apply_brightness, blinded, challenge+holdout. No Demucs. Student still OPEN."
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

Isolated replay of firmware `light_mode_bloom` compiled via `render_replay.py` (firmware SHA recorded in the receipt) plus the shipping `apply_brightness` photons curve (`PHOTONS²`, mode 0). No production firmware edits.

Same extra degree of freedom, same gain, same range:

- A = bloom + constant PHOTONS 0.675
- B = bloom + PHOTONS driven by frozen mix energy
- D = bloom + PHOTONS driven by frozen source share (`abs` kept as engineering reference, not on the page)

P3-C2: the same `k1_visual_hooks` onset→photons accent (gain 0.16, tau 100 ms). Control trigger = `|Δ mix|`. MIR trigger = `composition_change`. Frozen corpus thresholds, rates printed per version.

20 clips: 10 challenge (from the P3-B oracle set) + 10 MUSDB **test** holdout tracks stratified by duration quartile, **not** by share/RMS disagreement. Versions are **Version 1/2/3** (and Version 1/2 on events). Key is sealed until after judging.

HOST chromagram is a causal 12-bin STFT mapped into bloom’s expected range (mix-gain × broadband floor). Identical across A/B/D. Not firmware GDFT. One second of bloom warmup precedes each clip so the still is not a cold centre-dot. Bloom host frame rate is 31.25 Hz (device AP is 133 Hz); motion is slower; identical across versions.

- Continuous: `docs/mir/visual_replay/p3c1_continuous.html`
- Events: `docs/mir/visual_replay/p3c2_events.html`
- Keys: `docs/mir/visual_replay/P3C1_BLIND_KEY_OPEN_AFTER_JUDGING.json` (open only after scoring)
- Receipt: `artifacts/source_activity/p3c/receipt_musdb18_p3c.json`

This is still not a lighting verdict. Pixel MAD proves the extra DoF moved the bytes. Taste is the remaining call.

If share never beats mix on the lights: do not train a dominance student. If composition-change never beats `|Δ mix|` on the same accent: do not train an arrangement-change student. If one of them does: train a tiny research student **directly on MUSDB stem powers**, derive share/delta/composition_change in deterministic code. Demucs only after that, for unstemmed scale.

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
