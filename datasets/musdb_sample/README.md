---
abstract: "Official musdb 7-second sample excerpts. Audio is gitignored. Research/NC. Not the 4.7 GB corpus. Not a commercial training lineage."
---

# MUSDB 7 s sample (P3 plumbing)

`musdb.DB(root=here, download=True)` fetches the official **7-second excerpts**, not MUSDB18-HQ.

Licence: same educational / non-commercial terms as MUSDB18. **Not** a production-training source.

```bash
uv sync --extra musdb --extra mir
uv run python scripts/musdb_sample_oracle.py
```

Audio stays in this folder and is gitignored.
