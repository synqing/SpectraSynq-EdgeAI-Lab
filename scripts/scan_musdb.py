#!/usr/bin/env python3
"""Scan a local MUSDB18 tree and write a song-level split manifest. No download."""

from __future__ import annotations

import argparse
from pathlib import Path

from edgeai.dataset import assert_no_song_leak, scan_musdb, write_manifest


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, required=True)
    p.add_argument("--out", type=Path, default=Path("datasets/manifests/musdb18.json"))
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--val-frac", type=float, default=0.15)
    args = p.parse_args()
    songs = scan_musdb(args.root, seed=args.seed, val_frac=args.val_frac)
    assert_no_song_leak(songs)
    write_manifest(songs, args.out)
    print(f"wrote {args.out} n={len(songs)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
