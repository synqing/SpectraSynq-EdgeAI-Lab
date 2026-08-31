"""Share-student unit tests. Synthetic audio only — MUSDB is the script's job."""

from __future__ import annotations

import numpy as np
import pytest
import torch
import torch.nn as nn

from edgeai.dataset import SongRef, assert_no_song_leak
from edgeai.frontend import LogMelFrontend
from edgeai.mir.source_oracle import SOURCES, frame_mean_square, source_oracle
from edgeai.share_student import (
    CausalConvBNReLU,
    ShareStudent,
    ShareWindowDataset,
    WindowBank,
    musdb_song_split,
    resolve_musdb_root,
    share_loss,
    shares_from_powers,
    take_songs,
    verdict_from_metrics,
    window_powers_and_share,
)


SR = 16_000
HOP = 512


def _sine(freq: float, n: int, amp: float) -> np.ndarray:
    t = np.arange(n, dtype=np.float32) / SR
    return (amp * np.sin(2 * np.pi * freq * t)).astype(np.float32)


def _clicks(n: int, amp: float, interval_s: float = 0.25) -> np.ndarray:
    y = np.zeros(n, dtype=np.float32)
    step = int(interval_s * SR)
    width = int(0.008 * SR)
    for i in range(0, n - width, step):
        y[i : i + width] = amp
    return y


def test_silence_does_not_invent_equal_shares():
    zeros = np.zeros(4, dtype=np.float64)
    share = shares_from_powers(zeros)
    assert np.allclose(share, 0.0)
    assert float(share.sum()) == 0.0
    t = shares_from_powers(torch.zeros(2, 4), silent_thresh=0.0)
    assert torch.all(t == 0)


def test_share_sums_to_one_when_energy_present():
    p = np.array([0.4, 0.1, 0.3, 0.2], dtype=np.float64)
    s = shares_from_powers(p)
    assert pytest.approx(float(s.sum()), abs=1e-6) == 1.0
    assert list(s) == pytest.approx([0.4, 0.1, 0.3, 0.2], abs=1e-6)


def test_window_share_matches_source_oracle_hop_power():
    n = SR
    stems = {
        "vocals": _sine(220.0, n, 0.2),
        "drums": _clicks(n, 0.5),
        "bass": _sine(55.0, n, 0.25),
        "other": _sine(800.0, n, 0.1),
    }
    powers, share = window_powers_and_share(stems, hop=HOP)
    oracle_p = np.array(
        [float(np.sum(frame_mean_square(stems[k], HOP))) for k in SOURCES],
        dtype=np.float64,
    )
    assert np.allclose(powers, oracle_p, atol=1e-7)
    expect = oracle_p / oracle_p.sum()
    assert np.allclose(share, expect, atol=1e-6)
    assert "other" in SOURCES and len(SOURCES) == 4


def test_same_vocal_dominant_alone_buried_in_mixture_share():
    n = SR * 3
    vocals = _sine(220.0, n, 0.08)
    buried = {
        "vocals": vocals,
        "drums": _clicks(n, 0.9),
        "bass": _sine(55.0, n, 0.35),
        "other": 0.05 * np.random.default_rng(0).normal(size=n).astype(np.float32),
    }
    solo = {
        "vocals": vocals,
        "drums": np.zeros(n, dtype=np.float32),
        "bass": np.zeros(n, dtype=np.float32),
        "other": np.zeros(n, dtype=np.float32),
    }
    _, buried_s = window_powers_and_share(buried, hop=HOP)
    _, solo_s = window_powers_and_share(solo, hop=HOP)
    ora_b = source_oracle(buried, sr=SR, hop=HOP)
    ora_s = source_oracle(solo, sr=SR, hop=HOP)
    assert float(solo_s[0]) > 0.85
    assert float(buried_s[0]) < 0.35
    assert float(solo_s[0]) > float(buried_s[0]) + 0.4
    assert abs(float(np.mean(ora_s["vocals_abs"])) - float(np.mean(ora_b["vocals_abs"]))) < 0.15


def test_windows_inherit_song_split_never_re_split():
    songs = [
        SongRef("musdb18/train/A.stem.mp4", "train", "musdb18"),
        SongRef("musdb18/train/B.stem.mp4", "val", "musdb18"),
        SongRef("musdb18/test/C.stem.mp4", "test", "musdb18"),
    ]
    assert_no_song_leak(songs)
    bank = WindowBank(
        logmel=np.zeros((6, 1, 4, 4), dtype=np.float32),
        share=np.zeros((6, 4), dtype=np.float32),
        mix_rms=np.zeros(6, dtype=np.float32),
        powers=np.zeros((6, 4), dtype=np.float32),
        song_ids=["musdb18/train/A.stem.mp4"] * 3
        + ["musdb18/train/B.stem.mp4"] * 2
        + ["musdb18/test/C.stem.mp4"],
    )
    ds = ShareWindowDataset(bank)
    ids = [ds[i]["song_id"] for i in range(len(ds))]
    split_of = {s.song_id: s.split for s in songs}
    # A window cannot change split: lookup is by song_id.
    assert {split_of[i] for i in ids} == {"train", "val", "test"}
    assert split_of["musdb18/train/A.stem.mp4"] == "train"
    assert split_of["musdb18/test/C.stem.mp4"] == "test"
    leaked = take_songs(songs, "train", 1, seed=0)
    assert leaked[0].split == "train"
    assert all("/test/" not in s.song_id for s in leaked)


def test_scan_musdb_is_song_level_when_present():
    root = resolve_musdb_root()
    if root is None:
        pytest.skip("MUSDB18 not on disk")
    songs = musdb_song_split(root)
    assert_no_song_leak(songs)
    by = {"train": set(), "val": set(), "test": set()}
    for s in songs:
        by[s.split].add(s.song_id)
    assert by["train"] and by["val"] and by["test"]
    assert all("/test/" in i for i in by["test"])
    assert all("/train/" in i for i in by["train"] | by["val"])
    assert by["train"].isdisjoint(by["val"])
    assert by["train"].isdisjoint(by["test"])
    n_train_files = sum(1 for _ in (root / "train").glob("*.mp4"))
    n_test_files = sum(1 for _ in (root / "test").glob("*.mp4"))
    assert len(by["train"]) + len(by["val"]) == n_train_files
    assert len(by["test"]) == n_test_files


def test_student_four_sources_adaptive_avg_pool_not_tensor_mean():
    model = ShareStudent()
    pools = [m for m in model.modules() if isinstance(m, nn.AdaptiveAvgPool2d)]
    assert len(pools) == 1
    assert pools[0].output_size == (1, 1)
    src = inspect_forward_source()
    assert "tensor.mean" not in src and ".mean(dim=" not in src
    fe = LogMelFrontend()
    logmel = fe(torch.zeros(2, fe.cfg.n_samples))
    out = model(logmel)
    assert tuple(out["shares"].shape) == (2, 4)
    assert tuple(out["powers"].shape) == (2, 4)
    assert torch.all(out["powers"] >= 0)
    n = sum(p.numel() for p in model.parameters())
    assert 5_000 < n < 80_000
    assert any(isinstance(m, CausalConvBNReLU) for m in model.modules())


def inspect_forward_source() -> str:
    import inspect

    return inspect.getsource(ShareStudent.forward)


def test_near_zero_predicted_power_does_not_become_uniform_quarter():
    torch.manual_seed(0)
    model = ShareStudent().eval()
    fe = LogMelFrontend()
    with torch.no_grad():
        model.head.weight.zero_()
        model.head.bias.fill_(-30.0)
        shares = model(fe(torch.zeros(1, 16_000)))["shares"][0]
        powers = model(fe(torch.zeros(1, 16_000)))["powers"][0]
    assert float(powers.sum()) < 1e-10
    assert float(shares.sum()) == 0.0
    assert float(shares.max()) == 0.0


def test_student_learns_buried_vs_solo_on_synthetic():
    torch.manual_seed(0)
    np.random.seed(0)
    device = torch.device("cpu")
    from edgeai.share_student import ShareStudentConfig

    model = ShareStudent(ShareStudentConfig(dropout=0.0)).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=1e-3)
    fe = LogMelFrontend()
    n = fe.cfg.n_samples

    def _example(kind: str, i: int) -> tuple[np.ndarray, np.ndarray]:
        phase = _sine(220.0, n, 1.0)
        if kind == "solo":
            stems = {
                "vocals": (0.35 * phase).astype(np.float32),
                "drums": np.zeros(n, dtype=np.float32),
                "bass": np.zeros(n, dtype=np.float32),
                "other": np.zeros(n, dtype=np.float32),
            }
        else:
            stems = {
                "vocals": (0.08 * phase).astype(np.float32),
                "drums": _clicks(n, 0.9),
                "bass": _sine(55.0, n, 0.35),
                "other": _sine(800.0, n, 0.12),
            }
        mix = sum(stems[k] for k in stems)
        _, share = window_powers_and_share(stems, hop=HOP)
        return mix.astype(np.float32), share

    def _pack(kinds: list[str]) -> tuple[torch.Tensor, torch.Tensor]:
        mixes, shares = zip(*[_example(k, i) for i, k in enumerate(kinds)])
        pcm = torch.from_numpy(np.stack(mixes))
        with torch.no_grad():
            logmel = fe(pcm)
        return logmel.to(device), torch.from_numpy(np.stack(shares)).to(device)

    model.train()
    kinds = ["solo", "buried"] * 4
    for _ in range(60):
        logmel, target = _pack(kinds)
        opt.zero_grad(set_to_none=True)
        pred = model(logmel)["shares"]
        loss = share_loss(pred, target)
        loss.backward()
        opt.step()

    model.eval()
    with torch.no_grad():
        solo_x, solo_y = _pack(["solo"] * 8)
        bur_x, bur_y = _pack(["buried"] * 8)
        solo_p = model(solo_x)["shares"][:, 0].mean().item()
        bur_p = model(bur_x)["shares"][:, 0].mean().item()
        solo_t = solo_y[:, 0].mean().item()
        bur_t = bur_y[:, 0].mean().item()
    assert solo_t > bur_t + 0.4
    assert solo_p > bur_p + 0.2


def test_verdict_fail_when_student_is_mix_energy():
    student = {
        "vocals": {"r_pred_true": 0.17, "r_pred_mix": 0.99, "r_true_mix": 0.17, "n_songs": 16},
        "drums": {"r_pred_true": 0.10, "r_pred_mix": 0.99, "r_true_mix": 0.10, "n_songs": 16},
        "bass": {"r_pred_true": 0.16, "r_pred_mix": 0.99, "r_true_mix": 0.16, "n_songs": 16},
        "other": {"r_pred_true": 0.1, "r_pred_mix": 0.9, "r_true_mix": 0.1, "n_songs": 16},
    }
    linear = {k: dict(v) for k, v in student.items()}
    assert verdict_from_metrics(student, linear, n_test_songs=16) == "FAIL"
    good = {
        name: {"r_pred_true": 0.55, "r_pred_mix": 0.18, "r_true_mix": 0.17, "n_songs": 16}
        for name in SOURCES
    }
    lin = {
        name: {"r_pred_true": 0.20, "r_pred_mix": 0.9, "r_true_mix": 0.17, "n_songs": 16}
        for name in SOURCES
    }
    good["drums"]["r_true_mix"] = 0.10
    good["bass"]["r_true_mix"] = 0.16
    assert verdict_from_metrics(good, lin, n_test_songs=16) == "PASS"
    assert verdict_from_metrics(good, lin, n_test_songs=4) == "INCONCLUSIVE"
