---
abstract: "HOST-ONLY delay-aware PaRIRset onset. Same 3 held-out venues as the first probe. Zero-lag onset r is a delay artefact; after ~100 ms alignment F1@50 ms recovers 0.05 → 0.86. Old 'onset dies' reading is invalidated, not confirmed."
---

# PaRIRset onset — delay-aware re-score

**HOST-ONLY.** PaRIRset CC0 test split. DEAM research audio. CrowdioSet not ingested. Held-out venues intact.

Question the first probe could not answer:

> Did PA/ROOM kill onsets, or only delay them?

## Method (what changed)

The first receipt (`artifacts/parirset_probe/receipt.json`) scored wet vs clean **onset envelopes interpolated onto the DEAM 2 Hz grid**, with **no alignment** to the RIR direct-path peak.

That is the wrong instrument for transients:

1. These three test RIRs all have a **~100 ms** leading peak (`argmax |h|` after 16 kHz resample). Envelope xcorr on the music agrees (~96 ms).
2. Onset energy lives on tens of milliseconds. A 2 Hz grid aliases it.
3. A delayed-but-preserved click train produces low zero-lag Pearson and near-zero F1 at a 50 ms window even when every event is still there.

This re-score:

- extracts RMS / flux / onset at **native hop 512 @ 16 kHz (~32 ms)**;
- reports zero-lag Pearson **and** Pearson after advancing wet PCM by the RIR direct-path peak;
- peak-picks the same unit onset envelope on clean and wet;
- greedy event F1 at **50 ms** and **100 ms**.

Synthetic controls (see `tests/test_onset_align.py`) go red when clicks are deleted or when an 80 ms delay is scored with a 50 ms window, and go green after alignment. The checker is not a tautology.

Same three songs × three venues as the first probe (2030 / 2034 / 2041 × olivenzaOutdoors / valenciaMoon / palmaEsGremi). Causal `numpy.convolve` truncated to original length — unchanged.

## Headline

The first probe’s onset column is **invalidated** as a claim that “PA/room kills onset”.

It is **confirmed** as a description of **unaligned zero-lag correlation**. That number is real and mostly measures **delay**, not missed events.

| metric | mean over 9 comparisons |
| --- | ---: |
| RIR direct-path | 99.7 ms |
| onset r, legacy 2 Hz, zero-lag (old method) | 0.07 |
| onset r, native hop, zero-lag | 0.05 |
| onset r, native hop, delay-aligned | **0.88** |
| event F1 @ 50 ms, unaligned | 0.05 |
| event F1 @ 50 ms, aligned | **0.86** |
| event F1 @ 100 ms, unaligned | 0.62 |
| event F1 @ 100 ms, aligned | 0.87 |
| RMS r, zero-lag | 0.58 |
| RMS r, aligned | 0.83 |

All nine rows classify as **`onset_delayed`**: aligned F1@50 ms ≥ 0.7 and unaligned F1@50 ms < 0.4.

The 100 ms F1 window almost covers the 100 ms delay, so unaligned F1@100 ms is already 0.62. That is independent evidence that the events moved rather than vanished.

## 2034 (the old negative-r scare)

| venue | old 2 Hz zero-lag r | native aligned r | F1@50 aligned |
| --- | ---: | ---: | ---: |
| olivenzaOutdoors | −0.27 | 0.87 | 0.86 |
| valenciaMoon | −0.29 | 0.92 | 0.92 |
| palmaEsGremi | −0.27 | 0.82 | 0.86 |

Negative unaligned r on 2034 was a delayed sparse envelope, not a destroyed detector.

## Residual after alignment (real, smaller)

Aligned F1 is 0.79–0.92, not 1.0. Precision sometimes drops (extra wet peaks: 2030 olivenza 0.73) and recall sometimes drops (2041 olivenza 0.71). That is leftover smear / amplitude / false-onset, not the previous “onset dies” story.

RMS also improves once delay is removed (0.58 → 0.83). The first probe’s RMS column was less poisoned because RMS is slow.

## What this does **not** establish

- These three files are **short** (~0.4–0.6 s). Do not generalise to a long hall tail.
- Only three of eight PaRIRset test venues.
- No crowd layer (CrowdioSet still gated).
- Not ON-SILICON. Not a student. Not “onset needs no live-domain care” — a 100 ms shift **does** wreck a 50 ms lighting sync budget if you do not account for it.
- The ~100.0 ms peak on all three IRs may be dataset pre-delay (4410 samples at 44.1 kHz) rather than physical FOH distance. Product-relevant either way: naive convolution injects it.

## Decision impact

- Continue Amendment 002. Do **not** freeze “onset dies in PA/ROOM”.
- Treat PA/ROOM first as a **delay / sync** problem for deterministic onset, then as a residual smear problem.
- Semantic candidates still need CLEAN vs PA/ROOM vs PA/ROOM+CROWD once they exist — delay-aware, native-rate, not 2 Hz Pearson on onset.

Receipt: `artifacts/parirset_probe/receipt_aligned.json` (gitignored audio). Re-run: `uv run python scripts/parirset_onset_aligned.py`.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:edgeai | Delay-aware re-score; old onset-dies reading invalidated. |
