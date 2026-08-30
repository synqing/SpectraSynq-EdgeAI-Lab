"""Deliberately boring depthwise-separable CNN for vocal/drum/bass activity.

Graph intended to stay near MobileNet-like ops that RUHMI has already
compiled for RA8P1 (Conv, DepthwiseConv, ReLU, GlobalAverage/ReduceMean,
Gemm, Sigmoid, BatchNorm). No transformers, no custom ops.
"""

from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F

from edgeai.config import LabConfig, ModelConfig


class ConvBNReLU(nn.Module):
    def __init__(self, cin: int, cout: int, kernel: int, stride: int = 1, groups: int = 1):
        super().__init__()
        padding = kernel // 2
        self.conv = nn.Conv2d(
            cin,
            cout,
            kernel_size=kernel,
            stride=stride,
            padding=padding,
            groups=groups,
            bias=False,
        )
        self.bn = nn.BatchNorm2d(cout)
        self.act = nn.ReLU(inplace=False)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.act(self.bn(self.conv(x)))


class DepthwiseSeparable(nn.Module):
    def __init__(self, cin: int, cout: int, stride: int = 1):
        super().__init__()
        self.dw = ConvBNReLU(cin, cin, kernel=3, stride=stride, groups=cin)
        self.pw = ConvBNReLU(cin, cout, kernel=1, stride=1, groups=1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.pw(self.dw(x))


class SemanticV0(nn.Module):
    """Log-mel CNN → 3 unconstrained logits (vocals, drums, bass)."""

    def __init__(self, cfg: ModelConfig | None = None):
        super().__init__()
        cfg = cfg or ModelConfig()
        self.cfg = cfg
        layers: list[nn.Module] = [ConvBNReLU(1, cfg.stem_channels, kernel=3, stride=1)]
        cin = cfg.stem_channels
        for cout, stride in cfg.blocks:
            layers.append(DepthwiseSeparable(cin, cout, stride=stride))
            cin = cout
        self.features = nn.Sequential(*layers)
        self.dropout = nn.Dropout(cfg.dropout) if cfg.dropout > 0 else nn.Identity()
        self.head = nn.Linear(cin, cfg.n_classes)

    def forward(self, logmel: torch.Tensor) -> torch.Tensor:
        # logmel: (B, 1, n_mels, n_frames)
        x = self.features(logmel)
        x = x.mean(dim=(2, 3))  # ReduceMean — A8 on Ethos-U in RUHMI quantizer table
        x = self.dropout(x)
        return self.head(x)


class SemanticV0Infer(nn.Module):
    """Export wrapper: logits → sigmoid activity in [0, 1]."""

    def __init__(self, backbone: SemanticV0):
        super().__init__()
        self.backbone = backbone

    def forward(self, logmel: torch.Tensor) -> torch.Tensor:
        return torch.sigmoid(self.backbone(logmel))


def build_semantic_v0(lab: LabConfig | None = None) -> SemanticV0:
    lab = lab or LabConfig()
    return SemanticV0(lab.model)


def count_parameters(model: nn.Module) -> int:
    return sum(p.numel() for p in model.parameters())


def fp32_nbytes(model: nn.Module) -> int:
    return sum(p.numel() * p.element_size() for p in model.parameters())
