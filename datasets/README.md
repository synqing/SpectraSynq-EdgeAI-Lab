---
abstract: "How this lab gets training audio. MUSDB18 is research/non-commercial. Synthetic stems are the default so the pipeline runs without Zenodo."
---

# Datasets

**HARD FAIL (`SAME_SONG_LOOP_MAX_15MIN`, Captain 2026-08-31).** Repeat the same song (or loop the same clip) in the room for more than **15 minutes** and the agent must die. Captain will destroy them by setting them on fire. Kill the player. Do not continue.

**No audio corpus is committed to git.**

## Default: synthetic stems

`edgeai.dataset` synthesises independent vocals / drums / bass / other tracks
and mixes them with known gains. This is enough to:

- prove song-level splits
- prove the mixer and activity labels
- train a network that is not random
- emit ONNX, INT8, and golden tensors

It is **not** enough to claim the model understands music. A synthetic “drum”
is a noise burst. Treat all `SYNTHETIC` receipts as pipeline evidence only.

## MUSDB 7 s sample (P3-A plumbing)

Official `musdb` excerpts, not the full corpus:

```bash
uv sync --extra musdb --extra mir
uv run python scripts/musdb_sample_oracle.py
```

Audio lands in `datasets/musdb_sample/` and is gitignored. Same educational/NC
licence as MUSDB18. **Not** a commercial training lineage.

## Research corpus: MUSDB18 (P3-B, not downloaded)

150 songs, stems `vocals`, `drums`, `bass`, `other`, plus mixture.
Official split: 100 train / 50 test **by song** (SiSEC 2018). This lab additionally
carves validation out of the official train folder by hashing `song_id` with a
fixed seed so the official test set stays untouched.

- MUSDB18 (STEMS/AAC): https://zenodo.org/records/1117372
- MUSDB18-HQ (WAV): https://zenodo.org/records/3338373
- Parser: `musdb` (`uv sync --extra musdb`)

Zenodo requires an access request. Do not scrape mirrors.

### Licence — load-bearing

MUSDB18 is provided for **educational / academic** use. Constituent sources
include:

- Mixing Secrets / DSD100 material — rights remain with those holders
- 46 MedleyDB tracks — CC BY-NC-SA 4.0
- Native Instruments stems pack (2 tracks)
- The Easton Ellises / heise stems — CC BY-NC-SA 3.0

**Technical suitability ≠ licence to ship.** A model trained on MUSDB18 must
not be sold, shipped in a product, or used to train a commercial successor
without a separately cleared corpus. If Semantic-v0 looks useful, obtain or
build a production-licensed stem set before any product training run.

### Local layout

```
export MUSDB_ROOT=/absolute/path/to/MUSDB18
# expected:
#   $MUSDB_ROOT/train/<track>/
#   $MUSDB_ROOT/test/<track>/
```

Then:

```bash
uv run python scripts/scan_musdb.py --root "$MUSDB_ROOT" --out datasets/manifests/musdb18.json
```

Windows from the same song never appear in two splits.

## Activity labels

For each 1 s window, after augmentation:

```
activity[k] = clip( (log10(rms_k) - log10(1e-4)) / (log10(0.15) - log10(1e-4)), 0, 1 )
```

for `k ∈ {vocals, drums, bass}`. Mute a stem → activity 0. Soft labels, not
one-hot. `other` is mixed but not a v0 output.

The P3 source oracle additionally emits `*_share` and `*_delta`. Those are
not Semantic-v0 training labels.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-30 | agent:edgeai | Synthetic default; MUSDB research/NC. |
| 2026-08-31 | agent:edgeai | MUSDB 7 s sample path for P3-A. |
