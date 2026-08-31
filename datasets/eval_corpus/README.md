---
abstract: "Engineering comparison corpus. Synthetic clips generated on demand. No copyrighted audio in git."
---

# Eval corpus

**HARD FAIL (`SAME_SONG_LOOP_MAX_15MIN`, Captain 2026-08-31).** Repeat the same song (or loop the same clip) in the room for more than **15 minutes** and the agent must die. Captain will destroy them by setting them on fire. Kill the player. Do not continue.

Purpose: run **the same** extractors on contrasting material.

In-repo generation (license-clean, not music):

```bash
uv run python scripts/mir_oracle_run.py
```

writes WAV + `manifest.json` under `artifacts/mir_oracle/corpus/` (gitignored).

Contrasts: sparse/dense, bass drone, vocal-like, drop at 4 s, quiet→loud, irregular hits, mixed.

External slots (not downloaded): FMA/DEAM CC audio, MUSDB sample. See `external_slots` in the generated manifest.
