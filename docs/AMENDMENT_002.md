---
abstract: "Amendment 002: live/venue-domain testing. CLEAN vs PA/ROOM vs PA/ROOM+CROWD. PaRIRset CC0 held-out venues."
---

# Amendment 002 — live-domain robustness

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

### Update — 2026-08-30: first held-out venue convolution

Three **test-split** RIRs (venues never in PaRIRset train): olivenzaOutdoors, valenciaMoon, palmaEsGremi. Convolved onto DEAM 2030 / 2034 / 2041. CrowdioSet not ingested.

| song | venue | r(clean RMS, wet RMS) | r(clean onset, wet onset) |
| --- | --- | --- | --- |
| 2030 | olivenzaOutdoors | 0.74 | 0.23 |
| 2030 | valenciaMoon | 0.64 | 0.28 |
| 2030 | palmaEsGremi | 0.57 | 0.29 |
| 2034 | olivenzaOutdoors | 0.55 | −0.27 |
| 2034 | valenciaMoon | 0.40 | −0.29 |
| 2034 | palmaEsGremi | 0.37 | −0.27 |

These are **unaligned** wet-vs-clean correlations: `convolve_rir` keeps the original length and does not time-align to the RIR direct-path peak. A delayed onset envelope can look like “onset died” when it only moved. Treat the onset column as **provisional** until a delay-compensated evaluation exists. RMS still degrades but keeps the same sign in this probe.

That is why Amendment 002 exists: studio-only scores would lie about the microphone's world. Do not freeze “onset dies in PA/ROOM” from this first cut.

HOST-ONLY. Receipt: `artifacts/parirset_probe/receipt.json` (gitignored audio).

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-30 | agent:edgeai | Amendment 002. |
| 2026-08-30 | agent:edgeai | First PaRIRset test-split convolution; onset dies. |
| 2026-08-31 | agent:edgeai | Qualify onset result as provisional pending delay compensation. |
