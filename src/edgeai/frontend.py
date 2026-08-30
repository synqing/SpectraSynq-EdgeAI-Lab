"""Host-side log-mel frontend. This graph is NOT the U55 graph.

STFT / mel stays on the CPU (or host) because FFT is hostile to Ethos-U55.
The NPU model consumes a (1, n_mels, n_frames) log-mel image.
"""

from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F
import torchaudio

from edgeai.config import FrontendConfig


class LogMelFrontend(nn.Module):
    def __init__(self, cfg: FrontendConfig | None = None):
        super().__init__()
        self.cfg = cfg or FrontendConfig()
        self.mel = torchaudio.transforms.MelSpectrogram(
            sample_rate=self.cfg.sample_rate,
            n_fft=self.cfg.n_fft,
            win_length=self.cfg.win_length,
            hop_length=self.cfg.hop_length,
            n_mels=self.cfg.n_mels,
            f_min=self.cfg.f_min,
            f_max=self.cfg.f_max,
            power=2.0,
            center=True,
            pad_mode="constant",
            mel_scale="htk",
            norm=None,
        )

    def forward(self, pcm: torch.Tensor) -> torch.Tensor:
        """pcm: (B, T) float32 in [-1, 1] → (B, 1, n_mels, n_frames)."""
        cfg = self.cfg
        if pcm.dim() == 1:
            pcm = pcm.unsqueeze(0)
        if pcm.dim() != 2:
            raise ValueError(f"expected (B, T) PCM, got {tuple(pcm.shape)}")
        t = pcm.shape[-1]
        if t < cfg.n_samples:
            pcm = F.pad(pcm, (0, cfg.n_samples - t))
        elif t > cfg.n_samples:
            pcm = pcm[..., : cfg.n_samples]
        spec = self.mel(pcm.float())  # (B, n_mels, time)
        log_mel = torch.log(spec + cfg.log_offset)
        log_mel = log_mel.clamp(cfg.log_clip_min, cfg.log_clip_max)
        log_mel = _fit_time(log_mel, cfg.n_frames)
        return log_mel.unsqueeze(1).contiguous()


def _fit_time(x: torch.Tensor, n_frames: int) -> torch.Tensor:
    time = x.shape[-1]
    if time == n_frames:
        return x
    if time > n_frames:
        extra = time - n_frames
        start = extra // 2
        return x[..., start : start + n_frames]
    return F.pad(x, (0, n_frames - time))


def pcm_to_logmel(pcm: torch.Tensor, cfg: FrontendConfig | None = None) -> torch.Tensor:
    fe = LogMelFrontend(cfg)
    fe.eval()
    with torch.no_grad():
        return fe(pcm)
