---
abstract: "Engineering comparison corpus. Synthetic clips generated on demand. No copyrighted audio in git."
---

# Eval corpus

Purpose: run **the same** extractors on contrasting material.

In-repo generation (license-clean, not music):

```bash
uv run python scripts/mir_oracle_run.py
```

writes WAV + `manifest.json` under `artifacts/mir_oracle/corpus/` (gitignored).

Contrasts: sparse/dense, bass drone, vocal-like, drop at 4 s, quiet→loud, irregular hits, mixed.

External slots (not downloaded): FMA/DEAM CC audio, MUSDB sample. See `external_slots` in the generated manifest.
