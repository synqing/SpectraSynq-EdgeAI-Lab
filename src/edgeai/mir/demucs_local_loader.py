"""Exact-checkpoint loader used only by the isolated Demucs HOST probe venv."""

from __future__ import annotations

import hashlib
import os
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Protocol

from edgeai.mir.demucs_network_guard import demucs_network_forbidden

CHECKPOINT_SHA256 = "d9fa14133cfcc034a6758923bb3a8ca9f8dfd0b582134643bbf83f72c17576dd"
NAMED_GO = "D26_HOST_BLITZ_2026-09-01"
CHECKPOINT = (
    Path.home()
    / ".cache/huggingface/hub/models--adefossez--HTDemucs"
    / "snapshots/bf35a81b663819a8255c8fefee17f9d812b786b5"
    / "955717e8.safetensors"
)


class LoadedModel(Protocol):
    sources: list[str]
    samplerate: int
    audio_channels: int
    training: bool

    def state_dict(self): ...

    def parameters(self): ...


class DemucsLoadRefused(RuntimeError):
    def __init__(self, code: str, detail: str):
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_local_authority(checkpoint: Path) -> str:
    """Refuse Titan/no-GO/wrong object before Demucs is imported."""
    if "SPECTRASYNQ_TITAN" in os.environ:
        raise DemucsLoadRefused("DEMUCS_TITAN_REFUSED", "Demucs stays off Titan")
    if os.environ.get("SPECTRASYNQ_DEMUCS_NAMED_GO") != NAMED_GO:
        raise DemucsLoadRefused(
            "DEMUCS_NAMED_GO_REQUIRED", f"expected {NAMED_GO}"
        )
    if not checkpoint.is_file():
        raise DemucsLoadRefused("LOCAL_CHECKPOINT_MISSING", str(checkpoint))
    actual_sha = sha256_file(checkpoint)
    if actual_sha != CHECKPOINT_SHA256:
        raise DemucsLoadRefused("CHECKPOINT_SHA256_MISMATCH", actual_sha)
    return actual_sha


@contextmanager
def pinned_demucs_model(checkpoint: Path = CHECKPOINT) -> Iterator[LoadedModel]:
    """Hold the egress guard for model import, construction, and all inference."""
    verify_local_authority(checkpoint)
    with demucs_network_forbidden():
        from demucs.hf import load_safetensors_model

        model = load_safetensors_model(checkpoint)
        yield model
