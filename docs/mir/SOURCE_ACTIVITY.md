---
abstract: "P3-A HOST-ONLY: MUSDB 7 s samples, 144 tracks. Source oracle is abs/share/delta, not RMS(stem). Vocal share vs mix r=0.12 vs abs r=0.46. Not a product visual. Demucs not installed."
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

## P3-B — not run

Need 10–20 **full** songs chosen for contrasting source events (vocal enter/exit, quiet vocal over sparse bed, drums without loudness change, section change without RMS change). Official sample excerpts cannot answer that.

Do not install Demucs until P3-B visual A/B/C/D on full songs says the perfect oracle wins.

Older HPSS-on-DEAM numbers (2030/2034/2041) remain a mixture-only baseline, not stem truth.

Receipt: `artifacts/source_activity/receipt_musdb_sample.json`. Re-run: `uv run python scripts/musdb_sample_oracle.py`.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-30 | agent:edgeai | HPSS probe on three DEAM songs. |
| 2026-08-31 | agent:edgeai | P3-A MUSDB samples; abs/share/delta; share ≠ mix energy. |
