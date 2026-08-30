#!/usr/bin/env python3
"""Run conventional MIR (+ optional Semantic-v0 experiment) on the eval corpus."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from edgeai.mir.eval_corpus import write_corpus
from edgeai.mir.plot import plot_trace
from edgeai.mir.registry import licensing_matrix, load_registry
from edgeai.mir.traces import correlation_report, run_clip
from edgeai.train import git_commit


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--out", type=Path, default=Path("artifacts/mir_oracle"))
    p.add_argument(
        "--ckpt",
        type=Path,
        default=Path("experiments/semantic_v0_synth/semantic_v0_best.pt"),
    )
    args = p.parse_args()
    corpus_dir = args.out / "corpus"
    manifest = json.loads(write_corpus(corpus_dir).read_text())
    ckpt = args.ckpt if args.ckpt.is_file() else None
    reports = []
    for clip in manifest["clips"]:
        trace = run_clip(Path(clip["path"]), ckpt=ckpt)
        corr = correlation_report(trace)
        png = plot_trace(trace, args.out / "plots" / f"{clip['id']}.png")
        (args.out / "traces" / f"{clip['id']}.json").parent.mkdir(parents=True, exist_ok=True)
        (args.out / "traces" / f"{clip['id']}.json").write_text(json.dumps(trace) + "\n")
        reports.append({"id": clip["id"], "corr_dsp_vs_v0": corr, "plot": str(png)})
        print(f"{clip['id']:20s} {corr}")
    registry = load_registry()
    receipt = {
        "label": "HOST-ONLY",
        "git_commit": git_commit(Path(__file__).resolve().parents[1]),
        "corpus": "synthetic_eval_v0",
        "extractors_executed": ["librosa_conventional", "semantic_v0_experiment" if ckpt else None],
        "extractors_not_run": [
            "essentia-models",
            "musicnn (blocked: TF1)",
            "MERT",
            "MuQ",
            "HT-Demucs",
            "MAEST",
        ],
        "clips": reports,
        "licensing_matrix": licensing_matrix(registry),
        "note": "Synthetic clips. Correlations on sines/noise are not musical evidence.",
    }
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print("wrote", args.out / "receipt.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
