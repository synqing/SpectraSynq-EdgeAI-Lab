---
abstract: "PaRIRset local cache. CC0. Test split is 8 held-out venues. Do not train on test/."
---

# PaRIRset (local)

Canonical remote: https://huggingface.co/datasets/enricguso/parirset (CC0 1.0).

This directory holds a **small test-split cache** used by `scripts/parirset_probe.py`.
Audio is gitignored. Do not mix train-split RIRs into evaluation.

Held-out `test/` venues stay held out.

CrowdioSet is **not** stored here. Per-file licence required before ingest.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-30 | agent:edgeai | Cache pointer for Amendment 002. |
