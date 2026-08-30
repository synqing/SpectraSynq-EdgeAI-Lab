#!/usr/bin/env python3
"""Print how to obtain MUSDB18. Does not download. Access is gated on Zenodo."""

from __future__ import annotations

NOTE = """
MUSDB18 is not fetched automatically.

1. Request access on Zenodo (academic/educational use):
   https://zenodo.org/records/1117372          # STEMS / AAC
   https://zenodo.org/records/3338373          # HQ WAV (preferred)

2. Unzip so you have:
   $MUSDB_ROOT/train/<track>/
   $MUSDB_ROOT/test/<track>/

3. uv sync --extra musdb
4. uv run python scripts/scan_musdb.py --root "$MUSDB_ROOT"

Licence: research / non-commercial across much of the corpus.
Do not train a shipping SpectraSynq model on this set.
See datasets/README.md.
"""


def main() -> int:
    print(NOTE.strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
