#!/usr/bin/env python3
"""Score P3-C LED dumps against the source oracle. HOST-ONLY. Not a taste test."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from edgeai.mir.p3c_quant import cache_path, leds_path, score_clip, slice_oracle, summarise

ROOT = Path("artifacts/source_activity")
P3C = ROOT / "p3c"
CACHE = ROOT / "musdb18_oracle_cache"
RECEIPT_IN = P3C / "receipt_musdb18_p3c.json"
RECEIPT_OUT = P3C / "receipt_p3c_quant.json"
COMMITTED = Path("docs/mir/P3C_QUANT.json")
FIG = Path("docs/mir/figures/p3c_quant_share.png")


def write_figure(rows: list[dict], path: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    rows = [r for r in rows if r.get("delta_pos_share") == r.get("delta_pos_share")]
    names = [str(r["track"])[:22] for r in rows]
    vals = [float(r["delta_pos_share"]) for r in rows]
    colours = ["#3d8bfd" if r.get("set") == "holdout" else "#c45c26" for r in rows]
    fig, ax = plt.subplots(figsize=(10.5, 6.2))
    fig.patch.set_facecolor("#f4efe6")
    ax.set_facecolor("#f4efe6")
    y = np.arange(len(rows))
    ax.barh(y, vals, color=colours, height=0.72)
    ax.axvline(0.0, color="#1b1814", lw=0.8)
    ax.axvline(0.15, color="#6a645c", ls="--", lw=0.8, label="pass floor 0.15")
    ax.set_yticks(y)
    ax.set_yticklabels(names, fontsize=8)
    ax.invert_yaxis()
    ax.set_xlabel("partial r(head position, share | mix)  D minus B")
    ax.set_title(
        "HOST-ONLY  ·  Waveform Tempo extra control  ·  holdout blue, challenge rust",
        fontsize=11,
    )
    ax.legend(loc="lower right", fontsize=8)
    ax.grid(axis="x", alpha=0.25)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close(fig)


def main() -> int:
    raw = json.loads(RECEIPT_IN.read_text())
    rows = []
    for meta in raw["scores"]:
        oracle = np.load(cache_path(CACHE, meta["track"]))
        leds_npz = np.load(leds_path(P3C, meta["track"], meta["set"]))
        n = int(meta["n"])
        sliced = slice_oracle(oracle, float(meta["start_s"]), n)
        leds = {k: leds_npz[k] for k in leds_npz.files}
        rows.append(score_clip(leds, sliced, meta))
    summary = summarise(rows)
    out = {**summary, "clips": rows, "firmware_sha": raw.get("firmware_sha"), "html": raw.get("html")}
    P3C.mkdir(parents=True, exist_ok=True)
    RECEIPT_OUT.write_text(json.dumps(out, indent=2) + "\n")
    committed = {k: out[k] for k in out if k != "clips"}
    COMMITTED.write_text(json.dumps(committed, indent=2) + "\n")
    write_figure(rows, FIG)
    print(json.dumps(summary["stamps"], indent=2))
    print(json.dumps(summary["holdout"], indent=2))
    print(f"wrote {RECEIPT_OUT}")
    print(f"wrote {COMMITTED}")
    print(f"wrote {FIG}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
