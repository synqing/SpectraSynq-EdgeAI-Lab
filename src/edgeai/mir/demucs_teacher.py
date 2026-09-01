"""Ephemeral waveform-to-DEMUCS_TEACHER_SCHEMA_V1 helpers. HOST-only."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Mapping

import numpy as np
from numpy.typing import NDArray

from edgeai.mir.source_power import SOURCES, frame_mean_square

FFMPEG = Path("/opt/homebrew/bin/ffmpeg")
SCHEMA = "DEMUCS_TEACHER_SCHEMA_V1"


def decode_audio_stream(
    path: Path,
    *,
    stream_index: int = 0,
    samplerate: int = 44_100,
    channels: int = 2,
) -> NDArray[np.float32]:
    """Decode one local stream to channel-first float32 in memory; write nothing."""
    if not path.is_file():
        raise FileNotFoundError(path)
    if not FFMPEG.is_file():
        raise FileNotFoundError(FFMPEG)
    command = [
        str(FFMPEG),
        "-nostdin",
        "-v",
        "error",
        "-protocol_whitelist",
        "file,pipe,fd",
        "-i",
        str(path.resolve()),
        "-map",
        f"0:a:{stream_index}",
        "-vn",
        "-f",
        "f32le",
        "-acodec",
        "pcm_f32le",
        "-ar",
        str(samplerate),
        "-ac",
        str(channels),
        "pipe:1",
    ]
    process = subprocess.run(
        command,
        check=False,
        capture_output=True,
        timeout=900,
    )
    if process.returncode != 0:
        detail = process.stderr.decode("utf-8", errors="replace")[-2000:]
        raise RuntimeError(f"ffmpeg decode failed for stream {stream_index}: {detail}")
    samples = np.frombuffer(process.stdout, dtype="<f4")
    if samples.size == 0 or samples.size % channels:
        raise RuntimeError(
            f"invalid decoded sample count {samples.size} for {channels} channels"
        )
    return samples.reshape(-1, channels).T


def power_and_share(
    stems: Mapping[str, NDArray], *, hop: int = 512
) -> dict[str, object]:
    """Apply the frozen schema: mono mean-square, simplex share, silence zeros."""
    power = {
        source: np.asarray(frame_mean_square(stems[source], hop), dtype=np.float64)
        for source in SOURCES
    }
    n = min(values.size for values in power.values())
    matrix = np.stack([power[source][:n] for source in SOURCES], axis=1)
    total = matrix.sum(axis=1)
    share = np.zeros_like(matrix)
    nonsilent = total > 1e-10
    share[nonsilent] = matrix[nonsilent] / total[nonsilent, None]
    return {
        "power": {source: matrix[:, index] for index, source in enumerate(SOURCES)},
        "share": {source: share[:, index] for index, source in enumerate(SOURCES)},
        "total_power": total,
        "silent": ~nonsilent,
    }


def separate_to_envelopes(
    model,
    mixture: NDArray[np.float32],
    *,
    samplerate: int = 44_100,
    hop: int = 512,
) -> dict[str, object]:
    """Separate one in-memory mix and immediately collapse waveforms to envelopes."""
    import torch
    from demucs.apply import apply_model

    if samplerate != int(model.samplerate):
        raise ValueError(f"mixture sr {samplerate} != model sr {model.samplerate}")
    pcm = np.asarray(mixture, dtype=np.float32)
    if pcm.ndim != 2 or pcm.shape[0] != int(model.audio_channels):
        raise ValueError(
            f"expected [{model.audio_channels}, time] mixture, got {pcm.shape}"
        )
    waveform = torch.from_numpy(np.array(pcm, copy=True))
    reference = waveform.mean(0)
    mean = reference.mean()
    std = reference.std() + 1e-8
    normalised = ((waveform - mean) / std)[None]
    with torch.inference_mode():
        separated = apply_model(
            model,
            normalised,
            shifts=0,
            split=True,
            overlap=0.25,
            device="cpu",
            num_workers=0,
            progress=False,
        )[0]
        separated = separated * std + mean
    source_order = list(model.sources)
    if source_order != ["drums", "bass", "other", "vocals"]:
        raise RuntimeError(f"DEMUCS_SOURCE_ORDER_INVALID: {source_order}")
    stems = {
        source: separated[source_order.index(source)].detach().cpu().numpy().T
        for source in SOURCES
    }
    return power_and_share(stems, hop=hop)
