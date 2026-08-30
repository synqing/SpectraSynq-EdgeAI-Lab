from edgeai.dataset import assert_no_song_leak, synthetic_songs


def test_synthetic_splits_are_song_level_and_disjoint():
    songs = synthetic_songs(n=48, seed=0)
    assert_no_song_leak(songs)
    by = {"train": [], "val": [], "test": []}
    for s in songs:
        by[s.split].append(s.song_id)
    assert by["train"]
    assert by["val"]
    assert by["test"]
    assert set(by["train"]).isdisjoint(by["val"])
    assert set(by["train"]).isdisjoint(by["test"])


def test_split_is_deterministic():
    a = [s.__dict__ for s in synthetic_songs(n=48, seed=0)]
    b = [s.__dict__ for s in synthetic_songs(n=48, seed=0)]
    assert a == b
