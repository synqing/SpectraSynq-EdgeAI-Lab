#!/usr/bin/env python3
from pathlib import Path
from edgeai.dsp_goldens import make_vectors


def main() -> int:
    meta = make_vectors(Path("artifacts/dsp_goldens"))
    print(meta)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
