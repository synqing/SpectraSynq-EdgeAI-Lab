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

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-30 | agent:edgeai | Amendment 002. |
