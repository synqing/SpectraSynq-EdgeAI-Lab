#!/usr/bin/env python3
"""P1: human DEAM arousal vs DSP. No student."""

from __future__ import annotations

from pathlib import Path

from edgeai.mir.arousal_vs_dsp import run_corpus
from edgeai.mir.deam import AUDIO_DIR


def main() -> int:
    if not AUDIO_DIR.is_dir():
        print("DEAM audio missing. See datasets/deam/README.md")
        return 2
    out = Path("artifacts/deam_arousal")
    summary = run_corpus(out_dir=out)
    print("n_songs", summary["n_songs"])
    print("by_cohort", summary.get("by_cohort"))
    print("wrote", out / "receipt.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
