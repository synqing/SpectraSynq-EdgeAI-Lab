---
abstract: "P3-B HOST-ONLY on 150 full MUSDB18 STEMS. Within-track r(share, mix) is 0.10–0.17 vs r(abs, mix) 0.44–0.64. P3-A bass r=−0.22 was a 7 s artefact. Oracle-ranked 20-track visual set. No Demucs."
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

Those pages are the evidence for a lighting judgement. They are **not** that judgement. Do not train. Do not install Demucs until a product evaluator says D beats B (continuous) or composition_change beats |Δ mix| (events).

Re-run: `uv run python scripts/download_musdb.py --fetch` then `uv run python scripts/musdb18_p3b.py`. Receipt: `artifacts/source_activity/receipt_musdb18_p3b.json`.

Older HPSS-on-DEAM numbers remain a mixture-only baseline, not stem truth.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-30 | agent:edgeai | HPSS probe on three DEAM songs. |
| 2026-08-31 | agent:edgeai | P3-A MUSDB samples; abs/share/delta; share ≠ mix energy. |
| 2026-08-31 | agent:edgeai | P3-B 150 full tracks; oracle-ranked 20; within-track share vs mix. |
