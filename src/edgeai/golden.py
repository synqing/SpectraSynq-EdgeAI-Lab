"""Deterministic golden tensors for Titan bring-up.

Feed these log-mel tensors into the NPU before introducing live PDM.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import soundfile as sf
import torch

from edgeai.config import CLASSES, LabConfig
from edgeai.dataset import StemWindowDataset, synthetic_songs
from edgeai.export import load_backbone, _ort_infer
from edgeai.frontend import LogMelFrontend


def write_vectors(
    *,
    ckpt: Path,
    out_dir: Path,
    n: int = 32,
    onnx_fp32: Path | None = None,
    onnx_int8: Path | None = None,
) -> Path:
    model, lab = load_backbone(ckpt)
    fe = LogMelFrontend(lab.frontend)
    fe.eval()
    songs = synthetic_songs(n=48, seed=lab.train.seed)
    ds = StemWindowDataset(
        songs, "test", lab, n_windows=n, augment=False, base_seed=7_001
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    index = []
    model.eval()
    with torch.no_grad():
        for i in range(n):
            item = ds[i]
            case = out_dir / f"test_{i:03d}"
            case.mkdir(exist_ok=True)
            pcm = item["pcm"].numpy()
            wav_path = case / "input.wav"
            sf.write(wav_path, pcm, lab.frontend.sample_rate, subtype="PCM_16")
            logmel = item["logmel"].unsqueeze(0)
            np.save(case / "expected_preprocessed_tensor.npy", logmel.numpy())
            fp32 = torch.sigmoid(model(logmel)).numpy()[0]
            fp32_map = {name: float(fp32[j]) for j, name in enumerate(CLASSES)}
            (case / "expected_fp32_output.json").write_text(json.dumps(fp32_map, indent=2) + "\n")
            int8_map = None
            if onnx_int8 and onnx_int8.exists():
                q = _ort_infer(onnx_int8, logmel.numpy())[0]
                int8_map = {name: float(q[j]) for j, name in enumerate(CLASSES)}
                (case / "expected_int8_output.json").write_text(json.dumps(int8_map, indent=2) + "\n")
            meta = {
                "id": f"test_{i:03d}",
                "song_id": item["song_id"],
                "split": item["split"],
                "sample_rate": lab.frontend.sample_rate,
                "n_samples": lab.frontend.n_samples,
                "input_shape": list(lab.frontend.input_shape),
                "classes": list(CLASSES),
                "target_from_stems": [float(x) for x in item["target"].tolist()],
                "fp32": fp32_map,
                "int8_host_ort": int8_map,
                "label": "HOST-ONLY",
            }
            (case / "metadata.json").write_text(json.dumps(meta, indent=2) + "\n")
            index.append(meta)
    index_path = out_dir / "index.json"
    index_path.write_text(
        json.dumps(
            {
                "n": n,
                "checkpoint": str(ckpt),
                "frontend": lab.to_dict()["frontend"],
                "how_to_use_on_titan": (
                    "Do not start with the PDM mic. Load expected_preprocessed_tensor.npy "
                    "into the U55 input arena and compare activity[] to expected_int8_output.json."
                ),
                "cases": index,
            },
            indent=2,
        )
        + "\n"
    )
    return index_path


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--ckpt", type=Path, required=True)
    p.add_argument("--out", type=Path, default=Path("artifacts/golden"))
    p.add_argument("--n", type=int, default=32)
    p.add_argument("--int8-onnx", type=Path, default=None)
    args = p.parse_args(argv)
    path = write_vectors(ckpt=args.ckpt, out_dir=args.out, n=args.n, onnx_int8=args.int8_onnx)
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
