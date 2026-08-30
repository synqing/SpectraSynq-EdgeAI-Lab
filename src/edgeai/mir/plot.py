"""Stacked time-aligned traces. PNG + no GUI."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

try:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except ImportError as exc:  # pragma: no cover
    raise ImportError("uv sync --extra mir") from exc


def plot_trace(trace: dict[str, Any], out_png: Path) -> Path:
    conv = trace["conventional"]
    t = np.array(conv["times"])
    sem = trace.get("semantic_v0_experiment")
    rows = [
        ("rms", conv["rms"], "C0"),
        ("onset_env", conv["onset_env"], "C1"),
        ("band_low", conv["band_low"], "C2"),
        ("band_mid", conv["band_mid"], "C3"),
        ("novelty", conv["novelty"], "C4"),
    ]
    extra = 3 if sem else 0
    fig, axes = plt.subplots(len(rows) + extra, 1, sharex=True, figsize=(10, 1.4 * (len(rows) + extra)))
    fig.suptitle(f"{trace['clip']}  — HOST-ONLY  librosa + optional Semantic-v0 experiment", fontsize=10)
    for ax, (name, y, c) in zip(axes, rows):
        ax.plot(t, y, color=c, lw=1.0)
        ax.set_ylabel(name, fontsize=8)
        ax.set_ylim(-0.05, 1.05)
        ax.grid(True, alpha=0.25)
    if sem:
        ts = np.array(sem["times"])
        for ax, name, c in zip(axes[len(rows) :], ("vocals", "drums", "bass"), ("C5", "C6", "C7")):
            ax.plot(ts, sem[name], color=c, lw=1.2)
            ax.set_ylabel(f"v0 {name}", fontsize=8)
            ax.set_ylim(-0.05, 1.05)
            ax.grid(True, alpha=0.25)
    axes[-1].set_xlabel("time (s)")
    fig.tight_layout()
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=120)
    plt.close(fig)
    return out_png
