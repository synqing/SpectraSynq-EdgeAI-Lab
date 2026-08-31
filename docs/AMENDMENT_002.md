---
abstract: "Amendment 002: live/venue-domain testing. CLEAN vs PA/ROOM vs PA/ROOM+CROWD. PaRIRset CC0 held-out venues."
---

# Amendment 002 — live-domain robustness

**HARD FAIL (`SAME_SONG_LOOP_MAX_15MIN`, Captain 2026-08-31).** Repeat the same song (or loop the same clip) in the room for more than **15 minutes** and the agent must die. Captain will destroy them by setting them on fire. Kill the player. Do not continue.

Every serious descriptor or student must eventually be scored on:

1. **CLEAN/STUDIO**
2. **PA/ROOM** (convolve with PaRIRset test-split RIRs — 8 held-out venues)
3. **PA/ROOM + CROWD** (PaRIRset wet + CrowdioSet-class audience, only with per-file provenance)

PaRIRset: 40 professional concert venues through actual PA, measured at FOH. Train 32 venues / test 8 never seen. **CC0**. Paper: Gusó & Serra, ISMIR 2026, arXiv:2607.27828. Dataset: `enricguso/parirset`.

CrowdioSet: companion audience-noise set. **Do not ingest until each file's licence is recorded.** Do not mix NC material into a future commercial-safe corpus.

Held-out venue split is load-bearing. Do not train on `test/`.

Question:

> Does `vocal_activity = 0.84` or `arousal = 0.72` survive PA, room, and a crowd?

That is product-relevant. Improving studio SDR is not.

Plumbing: `edgeai.mir.live_domain.convolve_rir`. A synthetic exponential IR exists only to test the function — it is **not** PaRIRset.

Acoustic path delay is measured with `acoustic_path_delay_s` (RIR `argmax |h|`). It is **not** algorithm latency. On the three short test IRs used so far it is ~100 ms. Preserve it as its own variable.

### Update — 2026-08-30: first held-out venue convolution

Three **test-split** RIRs (venues never in PaRIRset train): olivenzaOutdoors, valenciaMoon, palmaEsGremi. Convolved onto DEAM 2030 / 2034 / 2041. CrowdioSet not ingested.

The onset column below is **unaligned 2 Hz Pearson**. Keep it as a historical trap, not as product truth.

| song | venue | r(clean RMS, wet RMS) | r(clean onset, wet onset) 2 Hz zero-lag |
| --- | --- | --- | --- |
| 2030 | olivenzaOutdoors | 0.74 | 0.23 |
| 2030 | valenciaMoon | 0.64 | 0.28 |
| 2030 | palmaEsGremi | 0.57 | 0.29 |
| 2034 | olivenzaOutdoors | 0.55 | −0.27 |
| 2034 | valenciaMoon | 0.40 | −0.29 |
| 2034 | palmaEsGremi | 0.37 | −0.27 |

### Update — 2026-08-31: delay-aware re-score **invalidates** “onset dies”

Same nine comparisons. Native hop (~32 ms). Align wet PCM to `argmax |RIR|` (~100 ms on these three files).

| metric | mean |
| --- | ---: |
| onset r native zero-lag | 0.05 |
| onset r native delay-aligned | 0.88 |
| event F1 @ 50 ms unaligned | 0.05 |
| event F1 @ 50 ms aligned | 0.86 |

All nine rows: **onset delayed**, not killed. 2034’s negative r recovers to ~0.82–0.92 after alignment. Residual aligned F1 is 0.79–0.92 (some smear / extra peaks), not a collapse.

> **Superseded** — do not quote the 2026-08-30 onset column as “PA/room kills onset”. See `docs/mir/PARIRSET_ONSET_ALIGNED.md`.

HOST-ONLY. Receipts: `artifacts/parirset_probe/receipt.json` (old, unaligned) and `receipt_aligned.json`.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-30 | agent:edgeai | Amendment 002. |
| 2026-08-30 | agent:edgeai | First PaRIRset test-split convolution; onset dies. |
| 2026-08-31 | agent:edgeai | Qualify onset result as provisional pending delay compensation. |
| 2026-08-31 | agent:edgeai | Delay-aware re-score: onset delayed, not killed. |
| 2026-08-31 | agent:edgeai | Name acoustic path delay as its own measured variable. |
