---
abstract: "Local dataset map. MUSDB18 teacher STEMS are on disk (100 train / 50 test .stem.mp4). HOST share work uses those stems; Demucs is not required. Audio gitignored. Research/NC. Cadence CLOSED."
---

# Datasets

**HARD FAIL (`SAME_SONG_LOOP_MAX_15MIN`, Captain 2026-08-31).** Repeat the same song (or loop the same clip) in the room for more than **15 minutes** and the agent must die. Captain will destroy them by setting them on fire. Kill the player. Do not continue.

**Cadence silicon CLOSED.** No USB. No 8 s holdout loop.

**No audio corpus is committed to git.** Trees under this folder are local caches. README files stay; `.mp4` / `.mp3` / `.wav` / zips are gitignored.

## HOST share work — teacher stems exist; Demucs not required

Current HOST share / source-oracle work reads **ground-truth MUSDB18 STEMS** from this tree. Isolated `vocals` / `drums` / `bass` / `other` plus mixture are already in each `.stem.mp4`. That is the teacher.

- **Do not install Demucs** for this work. `try_demucs()` is an optional HOST probe and returns `None` when the package is absent. Leave it that way.
- Demucs is **not** Titan, **not** a student I/O freeze, **not** a shipping teacher. Code MIT ≠ weight licence (UNKNOWN; scientific-use). See `docs/agent/lanes/L35_demucs.md`.
- D14: if lights benefit, MUSDB stems are already perfect supervision — a separator teacher would only add error.

Receipt that used this tree: `artifacts/share_student/receipt.json` (`root` = `datasets/musdb18`, corpus = standard STEMS, not HQ, not 7 s).

## MUSDB18 STEMS (on disk)

Official SiSEC 2018 split, Native Instruments stems (`.mp4`, AAC, 44.1 kHz stereo):

| split | n songs | path |
| --- | ---: | --- |
| train | 100 | `datasets/musdb18/train/*.stem.mp4` |
| test | 50 | `datasets/musdb18/test/*.stem.mp4` |

Stream order in each file: `0` mixture, `1` drums, `2` bass, `3` other, `4` vocals.

Resolver (`src/edgeai/share_student.py::resolve_musdb_root`): `MUSDB_ROOT` if set, else `datasets/musdb18`. Full-song close rejects the 7 s sample (`assert_full_musdb`). This lab carves validation from official **train songs** by hashed `song_id`; official **test songs** stay untouched. Split by song, never by window.

```
datasets/musdb18/
  train/<track>.stem.mp4     # 100
  test/<track>.stem.mp4      # 50
  musdb18.zip                # local archive; gitignored
  README.md                  # upstream track list + licences
```

Not HQ WAVs. `datasets/musdb18hq/` is unused. Parser: `musdb` + `stempeg` (`uv sync --extra musdb`).

```bash
# optional: point elsewhere
export MUSDB_ROOT=/absolute/path/to/MUSDB18

uv run python scripts/scan_musdb.py --root "${MUSDB_ROOT:-datasets/musdb18}" --out datasets/manifests/musdb18.json
uv run pytest tests/test_share_student.py
```

Zenodo (access request; do not scrape mirrors):

- MUSDB18 STEMS: https://zenodo.org/records/1117372
- MUSDB18-HQ WAV: https://zenodo.org/records/3338373

`scripts/download_musdb.py` is the fetch/unzip helper. Do not re-fetch if the 150 stems are already here.

### Licence — load-bearing

MUSDB18 is **educational / academic**. Constituent sources include Mixing Secrets / DSD100, 46 MedleyDB tracks (CC BY-NC-SA 4.0), Native Instruments stems pack (2 tracks), The Easton Ellises / heise (CC BY-NC-SA 3.0). Details: `datasets/musdb18/README.md`.

**Technical suitability ≠ licence to ship.** `commercial_training_lineage: false`. A model trained on MUSDB18 must not be sold, shipped, or used to train a commercial successor without a separately cleared corpus. Teacher use of stems does not clear derived student weights.

## MUSDB 7 s sample (P3-A plumbing only)

Official `musdb.DB(download=True)` excerpts. **Not** the share-student close. Screening only.

```bash
uv sync --extra musdb --extra mir
uv run python scripts/musdb_sample_oracle.py
```

Audio: `datasets/musdb_sample/` (gitignored). Same educational/NC terms.

## Default pipeline: synthetic stems

`edgeai.dataset` still synthesises independent vocals / drums / bass / other when MUSDB is not requested. Enough to prove song-level splits, mixer, labels, ONNX/INT8/goldens. **Not** music understanding. Treat `SYNTHETIC` receipts as pipeline evidence only. Semantic-v0 remains an experiment (`experiments/semantic_v0/AUTHORITY.md`).

## Other local caches

| tree | role | licence note |
| --- | --- | --- |
| `datasets/deam/` | DEAM arousal/valence vs DSP | CC-mixed; commercial UNKNOWN; not via mirdata |
| `datasets/parirset/` | small CC0 test-split RIR cache | do not train on `test/` |
| `datasets/eval_corpus/` | generated contrast clips (on demand) | no copyrighted audio in git |
| `datasets/manifests/` | scan outputs | `synthetic_v0.json` committed; MUSDB manifests gitignored if present |

## Activity labels (Semantic-v0)

For each 1 s window, after augmentation:

```
activity[k] = clip( (log10(rms_k) - log10(1e-4)) / (log10(0.15) - log10(1e-4)), 0, 1 )
```

for `k ∈ {vocals, drums, bass}`. Mute a stem → activity 0. Soft labels, not one-hot. `other` is mixed but not a v0 output.

P3 source oracle / share student additionally emit four-source `*_share` (and `*_delta`). Those are **not** Semantic-v0 training labels. Share student I/O is unfrozen.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-30 | agent:edgeai | Synthetic default; MUSDB research/NC. |
| 2026-08-31 | agent:edgeai | MUSDB 7 s sample path for P3-A. |
| 2026-08-31 | agent:grok-ssa-w3-l33 | Stale “not downloaded” killed. STEMS on disk (100/50). HOST share uses teacher stems; Demucs not required. Cadence CLOSED. |
