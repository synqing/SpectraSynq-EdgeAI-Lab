"""HOST envelope pipeline. Stems → hop power → four-way share. No Demucs import."""

from __future__ import annotations

import ast
import importlib.util
import inspect
import sys
from pathlib import Path

import numpy as np

from edgeai.mir.source_oracle import SOURCES
from edgeai.mir.teachers import (
    envelopes_from_stems,
    local_htdemucs_checkpoint,
    share_from_stems,
    try_demucs,
)

SR = 8_000
HOP = 512

# HOST inventory only — not a named GO. Do not fetch. Do not load tensors.
HTDEMUCS_LOCAL = (
    Path.home()
    / ".cache/huggingface/hub/models--adefossez--HTDemucs"
    / "snapshots/bf35a81b663819a8255c8fefee17f9d812b786b5"
    / "955717e8.safetensors"
)
HTDEMUCS_SIZE = 84_025_440


def _sine(freq: float, n: int, amp: float) -> np.ndarray:
    t = np.arange(n, dtype=np.float32) / SR
    return (amp * np.sin(2 * np.pi * freq * t)).astype(np.float32)


def _four_stems(n: int) -> dict[str, np.ndarray]:
    return {
        "vocals": _sine(220.0, n, 0.25),
        "drums": _sine(150.0, n, 0.20),
        "bass": _sine(55.0, n, 0.22),
        "other": _sine(800.0, n, 0.12),
    }


def _separator_calls(src: str) -> list[str]:
    tree = ast.parse(src)
    hits: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Name) and func.id == "Separator":
            hits.append("Separator")
        elif isinstance(func, ast.Attribute) and func.attr == "Separator":
            hits.append("Separator")
    return hits


def test_share_sums_to_one_on_nonsilence() -> None:
    share = share_from_stems(_four_stems(SR * 2), SR, hop=HOP)
    total = sum(share[name] for name in SOURCES)
    assert set(share) == set(SOURCES)
    assert np.allclose(total, 1.0, atol=1e-5)


def test_silence_share_is_zeros_not_quarter() -> None:
    n = SR
    zeros = {name: np.zeros(n, dtype=np.float32) for name in SOURCES}
    share = share_from_stems(zeros, SR, hop=HOP)
    stacked = np.stack([share[name] for name in SOURCES], axis=0)
    assert np.allclose(stacked, 0.0)
    assert not np.allclose(stacked.sum(axis=0), 0.25)


def test_vocals_only_share_is_one() -> None:
    n = SR * 2
    share = share_from_stems({"vocals": _sine(220.0, n, 0.3)}, SR, hop=HOP)
    assert float(np.mean(share["vocals"])) > 0.99
    assert np.allclose(share["drums"], 0.0)
    assert np.allclose(share["bass"], 0.0)
    assert np.allclose(share["other"], 0.0)


def test_missing_stem_is_zeros() -> None:
    n = SR
    share = share_from_stems(
        {"vocals": _sine(220.0, n, 0.3), "drums": _sine(150.0, n, 0.2)},
        SR,
        hop=HOP,
    )
    assert np.allclose(share["bass"], 0.0)
    assert np.allclose(share["other"], 0.0)
    total = share["vocals"] + share["drums"]
    assert np.allclose(total, 1.0, atol=1e-5)


def test_envelopes_include_hop_power_and_share() -> None:
    env = envelopes_from_stems(_four_stems(SR * 2), SR, hop=HOP)
    assert set(env["share"]) == set(SOURCES)
    assert set(env["power"]) == set(SOURCES)
    total = sum(env["share"][name] for name in SOURCES)
    assert np.allclose(total, 1.0, atol=1e-5)
    for name in SOURCES:
        assert env["power"][name].shape == env["share"][name].shape
        assert float(np.mean(env["power"][name])) > 0.0


def test_envelope_helpers_do_not_import_demucs() -> None:
    assert importlib.util.find_spec("demucs") is None
    share_from_stems(_four_stems(SR), SR, hop=HOP)
    envelopes_from_stems({"vocals": _sine(220.0, SR, 0.3)}, SR, hop=HOP)
    assert "demucs" not in sys.modules
    src = inspect.getsource(share_from_stems) + inspect.getsource(envelopes_from_stems)
    assert "demucs" not in src


def test_local_htdemucs_checkpoint_none_by_default(monkeypatch) -> None:
    monkeypatch.delenv("SPECTRASYNQ_DEMUCS_LOCAL", raising=False)
    assert local_htdemucs_checkpoint() is None


def test_local_htdemucs_checkpoint_inventory_path_not_loaded(monkeypatch) -> None:
    assert HTDEMUCS_LOCAL.is_file()
    assert HTDEMUCS_LOCAL.stat().st_size == HTDEMUCS_SIZE
    monkeypatch.setenv("SPECTRASYNQ_DEMUCS_LOCAL", str(HTDEMUCS_LOCAL))

    def _forbid_load(*_a, **_k):
        raise AssertionError("must not load HT-Demucs tensors")

    import torch

    monkeypatch.setattr(torch, "load", _forbid_load)
    src = inspect.getsource(local_htdemucs_checkpoint)
    assert "torch" not in src
    assert "safetensors" not in src
    assert "torch.load" not in src
    assert "read_bytes" not in src
    assert "open(" not in src
    got = local_htdemucs_checkpoint()
    assert got == HTDEMUCS_LOCAL
    assert got.is_file()


def test_try_demucs_still_none() -> None:
    assert importlib.util.find_spec("demucs") is None
    assert try_demucs() is None


def test_teachers_source_does_not_construct_separator() -> None:
    path = Path(__file__).resolve().parents[1] / "src" / "edgeai" / "mir" / "teachers.py"
    src = path.read_text(encoding="utf-8")
    assert _separator_calls(src) == []
    assert "Separator(repo" not in src
    assert "Separator()" not in src
    # Protocol class may be named Separator; construction call must not exist.
    assert "demucs.api.Separator(" not in src
