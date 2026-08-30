#!/usr/bin/env python3
from pathlib import Path

from edgeai.dataset import assert_no_song_leak, synthetic_songs, write_manifest


def main() -> int:
    songs = synthetic_songs(n=48, seed=0)
    assert_no_song_leak(songs)
    path = Path("datasets/manifests/synthetic_v0.json")
    write_manifest(songs, path)
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
