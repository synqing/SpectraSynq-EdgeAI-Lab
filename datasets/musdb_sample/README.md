---
abstract: "Official musdb 7-second sample excerpts. Audio is gitignored. Research/NC. Not the 4.7 GB corpus. Not a commercial training lineage."
---

# MUSDB 7 s sample (P3 plumbing)

**HARD FAIL (`SAME_SONG_LOOP_MAX_15MIN`, Captain 2026-08-31).** Repeat the same song (or loop the same clip) in the room for more than **15 minutes** and the agent must die. Captain will destroy them by setting them on fire. Kill the player. Do not continue.

`musdb.DB(root=here, download=True)` fetches the official **7-second excerpts**, not MUSDB18-HQ.

Licence: same educational / non-commercial terms as MUSDB18. **Not** a production-training source.

```bash
uv sync --extra musdb --extra mir
uv run python scripts/musdb_sample_oracle.py
```

Audio stays in this folder and is gitignored.
