"""Portable accelerator selection. Semantics must not depend on the device."""

from __future__ import annotations

import torch


def pick_device(prefer: str | None = None) -> torch.device:
    if prefer:
        name = prefer.lower()
        if name == "mps":
            if not torch.backends.mps.is_available():
                raise RuntimeError("MPS requested but not available")
            return torch.device("mps")
        if name == "cuda":
            if not torch.cuda.is_available():
                raise RuntimeError("CUDA requested but not available")
            return torch.device("cuda")
        if name == "cpu":
            return torch.device("cpu")
        raise ValueError(f"unknown device preference: {prefer}")
    if torch.backends.mps.is_available():
        return torch.device("mps")
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


def device_name(device: torch.device | None = None) -> str:
    if device is None:
        device = pick_device()
    extra = ""
    if device.type == "mps":
        extra = f" built={torch.backends.mps.is_built()}"
    if device.type == "cuda":
        extra = f" {torch.cuda.get_device_name(0)}"
    return f"{device}{extra}"
