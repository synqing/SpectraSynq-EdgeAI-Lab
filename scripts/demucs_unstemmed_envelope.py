#!/usr/bin/env python3
"""J4: Ride It research-only four-way share JSON. No playback and no WAV."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from edgeai.mir.demucs_local_loader import (  # noqa: E402
    CHECKPOINT,
    CHECKPOINT_SHA256,
    pinned_demucs_model,
)
from edgeai.mir.demucs_teacher import decode_audio_stream, separate_to_envelopes  # noqa: E402
from edgeai.mir.source_power import SOURCES  # noqa: E402

SOURCE = Path("/Users/spectrasynq/Workspace_Management/Software/YT_Saver/Regard_Ride_It.mp3")
SOURCE_SHA256 = "a0df4f680c12ded3c24f3895b8aaab3cbf7a19c44e4ab62fc29f52358c1516fe"
OUT_DIR = ROOT / "artifacts/demucs_host/research_only"
DEFAULT_OUTPUT = OUT_DIR / "ride_it_share.json"
SR = 44_100
HOP = 512
FORBIDDEN_MEDIA_SUFFIXES = {".aac", ".flac", ".m4a", ".mp3", ".mp4", ".ogg", ".wav"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_research_output(output: Path) -> None:
    """Keep the witness JSON inside the one research-only boundary."""
    resolved = output.resolve()
    try:
        resolved.relative_to(OUT_DIR.resolve())
    except ValueError as exc:
        raise RuntimeError(f"J4_RED: output outside research_only: {resolved}") from exc
    if resolved.suffix.lower() != ".json":
        raise RuntimeError(f"J4_RED: output must be JSON: {resolved}")


def forbidden_media(root: Path = OUT_DIR) -> list[Path]:
    """Return persisted audio/stem candidates forbidden from the witness tree."""
    if not root.exists():
        return []
    return sorted(
        path
        for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() in FORBIDDEN_MEDIA_SUFFIXES
    )


def build_witness(source: Path) -> dict[str, object]:
    actual_source_sha = sha256_file(source)
    if actual_source_sha != SOURCE_SHA256:
        raise RuntimeError(f"RIDE_IT_SHA256_MISMATCH: {actual_source_sha}")
    with pinned_demucs_model(CHECKPOINT) as model:
        mixture = decode_audio_stream(source, stream_index=0, samplerate=SR, channels=2)
        envelopes = separate_to_envelopes(model, mixture, samplerate=SR, hop=HOP)
    n = min(np.asarray(envelopes["share"][source_name]).size for source_name in SOURCES)
    times = ((np.arange(n, dtype=np.float64) * HOP) + HOP * 0.5) / SR
    return {
        "purpose": "HOST_RESEARCH_WITNESS_ONLY",
        "source_audio": str(source),
        "source_audio_sha256": actual_source_sha,
        "teacher": "HTDemucs local 955717e8.safetensors",
        "checkpoint_sha256": CHECKPOINT_SHA256,
        "schema": "DEMUCS_TEACHER_SCHEMA_V1",
        "sources": list(SOURCES),
        "stem_measure": "hop_mean_square_power",
        "share_definition": "P_i / sum(P)",
        "silence": "sum(P) <= 1e-10 -> [0,0,0,0]",
        "timebase": {
            "samplerate": SR,
            "hop_samples": HOP,
            "alignment": "hop-centre",
        },
        "times_s": times.tolist(),
        "power": {
            source_name: np.asarray(envelopes["power"][source_name])[:n].tolist()
            for source_name in SOURCES
        },
        "share": {
            source_name: np.asarray(envelopes["share"][source_name])[:n].tolist()
            for source_name in SOURCES
        },
        "commercial_training_lineage": False,
        "derived_weight_clearance": "UNKNOWN_LEGAL_REVIEW",
        "not_training_dataset": True,
        "waveforms_persisted": False,
        "network_fetch": False,
        "titan": False,
        "student_io_frozen": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Write the Ride It research-only share JSON.")
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)
    try:
        validate_research_output(args.output)
    except RuntimeError as exc:
        raise SystemExit(str(exc)) from exc
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if media := forbidden_media():
        raise SystemExit(f"J4_RED: waveform/stem media exists in research_only: {media}")
    witness = build_witness(args.source)
    args.output.write_text(json.dumps(witness, separators=(",", ":")) + "\n", encoding="utf-8")
    if media := forbidden_media():
        raise SystemExit(f"J4_RED: waveform/stem media created in research_only: {media}")
    print("RIDE_IT_RESEARCH_WITNESS_PASS", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
