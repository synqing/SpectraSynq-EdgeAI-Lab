"""Single source of truth for Semantic-v0 shapes. YAML may overlay, not replace."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import yaml

CLASSES = ("vocals", "drums", "bass")


@dataclass
class FrontendConfig:
    sample_rate: int = 16_000
    duration_s: float = 1.0
    n_fft: int = 400  # 25 ms at 16 kHz
    win_length: int = 400
    hop_length: int = 160  # 10 ms at 16 kHz
    n_mels: int = 64
    n_frames: int = 100
    f_min: float = 20.0
    f_max: float = 8_000.0
    log_offset: float = 1.0e-6
    # log-mel is clipped then left in log space; quantizer finds the range.
    log_clip_min: float = -12.0
    log_clip_max: float = 6.0

    @property
    def n_samples(self) -> int:
        return int(round(self.sample_rate * self.duration_s))

    @property
    def input_shape(self) -> tuple[int, int, int, int]:
        # NCHW log-mel image consumed by the CNN / NPU graph.
        return (1, 1, self.n_mels, self.n_frames)


@dataclass
class ModelConfig:
    stem_channels: int = 32
    blocks: tuple[tuple[int, int], ...] = (
        (64, 2),
        (64, 1),
        (128, 2),
        (128, 1),
        (192, 2),
        (192, 1),
        (256, 1),
    )
    n_classes: int = 3
    dropout: float = 0.0  # keep 0 until U55 mapping is proven


@dataclass
class TrainConfig:
    seed: int = 0
    epochs: int = 8
    batch_size: int = 16
    windows_per_epoch: int = 256
    val_windows: int = 64
    test_windows: int = 64
    lr: float = 1.0e-3
    weight_decay: float = 1.0e-4
    num_workers: int = 0
    mute_prob: float = 0.18
    gain_db_min: float = -20.0
    gain_db_max: float = 6.0
    noise_prob: float = 0.25
    noise_snr_db_min: float = 8.0
    noise_snr_db_max: float = 30.0
    eq_prob: float = 0.35


@dataclass
class LabConfig:
    frontend: FrontendConfig = field(default_factory=FrontendConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    train: TrainConfig = field(default_factory=TrainConfig)
    onnx_opset: int = 14  # RA8P1 zoo includes several opset-14 ONNX nets

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_yaml(cls, path: Path | str) -> "LabConfig":
        raw = yaml.safe_load(Path(path).read_text()) or {}
        cfg = cls()
        if "frontend" in raw:
            cfg.frontend = FrontendConfig(**raw["frontend"])
        if "model" in raw:
            m = dict(raw["model"])
            if "blocks" in m:
                m["blocks"] = tuple(tuple(x) for x in m["blocks"])
            cfg.model = ModelConfig(**m)
        if "train" in raw:
            cfg.train = TrainConfig(**raw["train"])
        if "onnx_opset" in raw:
            cfg.onnx_opset = int(raw["onnx_opset"])
        return cfg


def default_config() -> LabConfig:
    return LabConfig()
