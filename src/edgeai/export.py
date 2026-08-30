"""PyTorch → ONNX (opset 14) → host INT8 via ONNX Runtime.

RUHMI/MERA compilation is a separate x86 Linux lane (deployment/ra8p1).
ONNX + PyTorch frontends for RUHMI must go through the quantizer flow.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
import torch

from edgeai.config import CLASSES, LabConfig
from edgeai.dataset import StemWindowDataset, collate, synthetic_songs
from edgeai.metrics import per_class_report, quantization_delta
from edgeai.semantic_v0 import SemanticV0, SemanticV0Infer, count_parameters, fp32_nbytes


def load_backbone(ckpt_path: Path, lab: LabConfig | None = None) -> tuple[SemanticV0, LabConfig]:
    ckpt = torch.load(ckpt_path, map_location="cpu", weights_only=False)
    if lab is None:
        lab = LabConfig()
        if "config" in ckpt:
            lab = _lab_from_dict(ckpt["config"])
    model = SemanticV0(lab.model)
    model.load_state_dict(ckpt["model"])
    model.eval()
    return model, lab


def _lab_from_dict(d: dict[str, Any]) -> LabConfig:
    cfg = LabConfig()
    if "frontend" in d:
        from edgeai.config import FrontendConfig

        cfg.frontend = FrontendConfig(**d["frontend"])
    if "model" in d:
        from edgeai.config import ModelConfig

        m = dict(d["model"])
        if "blocks" in m:
            m["blocks"] = tuple(tuple(x) for x in m["blocks"])
        cfg.model = ModelConfig(**m)
    if "train" in d:
        from edgeai.config import TrainConfig

        cfg.train = TrainConfig(**d["train"])
    if "onnx_opset" in d:
        cfg.onnx_opset = int(d["onnx_opset"])
    return cfg


def export_onnx(
    model: SemanticV0,
    path: Path,
    lab: LabConfig,
    *,
    sigmoid: bool = True,
) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    wrapped: torch.nn.Module = SemanticV0Infer(model) if sigmoid else model
    wrapped.eval()
    dummy = torch.zeros(lab.frontend.input_shape, dtype=torch.float32)
    kwargs = dict(
        input_names=["logmel"],
        output_names=["activity"],
        opset_version=lab.onnx_opset,
        do_constant_folding=True,
    )
    with torch.no_grad():
        try:
            torch.onnx.export(wrapped, dummy, str(path), dynamo=False, **kwargs)
        except TypeError:
            torch.onnx.export(wrapped, dummy, str(path), **kwargs)
    return path


def make_calib_npy(lab: LabConfig, path: Path, n: int = 32, seed: int = 0) -> Path:
    songs = synthetic_songs(n=48, seed=seed)
    ds = StemWindowDataset(songs, "train", lab, n_windows=n, augment=False, base_seed=seed)
    xs = []
    for i in range(n):
        xs.append(ds[i]["logmel"].numpy())
    arr = np.stack(xs, axis=0).astype(np.float32)
    path.parent.mkdir(parents=True, exist_ok=True)
    np.save(path, arr)
    return path


def quantize_onnx_int8(
    fp32_onnx: Path,
    calib_npy: Path,
    int8_onnx: Path,
) -> Path:
    from onnxruntime.quantization import (
        CalibrationDataReader,
        QuantFormat,
        QuantType,
        quantize_static,
    )

    class Reader(CalibrationDataReader):
        def __init__(self, array: np.ndarray):
            self.data = array
            self.i = 0

        def get_next(self):
            if self.i >= len(self.data):
                return None
            x = self.data[self.i : self.i + 1]
            self.i += 1
            return {"logmel": x}

    calib = np.load(calib_npy)
    int8_onnx.parent.mkdir(parents=True, exist_ok=True)
    quantize_static(
        model_input=str(fp32_onnx),
        model_output=str(int8_onnx),
        calibration_data_reader=Reader(calib),
        quant_format=QuantFormat.QDQ,
        activation_type=QuantType.QInt8,
        weight_type=QuantType.QInt8,
        per_channel=True,
    )
    return int8_onnx


def _ort_infer(onnx_path: Path, x: np.ndarray) -> np.ndarray:
    """Graph is exported with static batch=1 (U55). Feed windows one at a time."""
    import onnxruntime as ort

    sess = ort.InferenceSession(str(onnx_path), providers=["CPUExecutionProvider"])
    x = np.asarray(x, dtype=np.float32)
    if x.ndim == 3:
        x = x[None, ...]
    outs = []
    for i in range(x.shape[0]):
        outs.append(sess.run(["activity"], {"logmel": x[i : i + 1]})[0])
    return np.concatenate(outs, axis=0)


def compare_fp32_int8(
    backbone: SemanticV0,
    lab: LabConfig,
    fp32_onnx: Path,
    int8_onnx: Path,
    n: int = 48,
    seed: int = 0,
) -> dict[str, Any]:
    songs = synthetic_songs(n=48, seed=seed)
    ds = StemWindowDataset(songs, "test", lab, n_windows=n, augment=False, base_seed=seed + 9)
    xs, ys, pt, o32, o8 = [], [], [], [], []
    backbone.eval()
    with torch.no_grad():
        for i in range(n):
            item = ds[i]
            logmel = item["logmel"].unsqueeze(0)
            xs.append(logmel.numpy())
            ys.append(item["target"].numpy())
            pt.append(torch.sigmoid(backbone(logmel)).numpy()[0])
    x = np.concatenate(xs, axis=0).astype(np.float32)
    y = np.stack(ys, axis=0)
    pred_pt = np.stack(pt, axis=0)
    pred_onnx = _ort_infer(fp32_onnx, x)
    pred_int8 = _ort_infer(int8_onnx, x)
    pt_rep = per_class_report(y, pred_pt)
    onnx_rep = per_class_report(y, pred_onnx)
    int8_rep = per_class_report(y, pred_int8)
    onnx_mae = float(np.mean(np.abs(pred_pt - pred_onnx)))
    return {
        "label": "HOST-ONLY",
        "n": n,
        "pytorch_fp32": pt_rep,
        "onnx_fp32": onnx_rep,
        "onnx_int8": int8_rep,
        "pytorch_vs_onnx_fp32_mae": onnx_mae,
        "fp32_vs_int8": quantization_delta(onnx_rep, int8_rep),
        "classes": list(CLASSES),
    }


def export_from_checkpoint(
    ckpt: Path,
    out_dir: Path,
    *,
    n_calib: int = 32,
) -> dict[str, Any]:
    model, lab = load_backbone(ckpt)
    out_dir.mkdir(parents=True, exist_ok=True)
    fp32 = out_dir / "semantic_v0_fp32.onnx"
    int8 = out_dir / "semantic_v0_int8.onnx"
    calib = out_dir / "calib_logmel.npy"
    export_onnx(model, fp32, lab, sigmoid=True)
    make_calib_npy(lab, calib, n=n_calib, seed=lab.train.seed)
    quantize_onnx_int8(fp32, calib, int8)
    report = compare_fp32_int8(model, lab, fp32, int8, n=48, seed=lab.train.seed)
    report.update(
        {
            "checkpoint": str(ckpt),
            "fp32_onnx": str(fp32),
            "int8_onnx": str(int8),
            "calib_npy": str(calib),
            "param_count": count_parameters(model),
            "fp32_bytes": fp32_nbytes(model),
            "fp32_onnx_bytes": fp32.stat().st_size,
            "int8_onnx_bytes": int8.stat().st_size,
            "onnx_opset": lab.onnx_opset,
            "input_shape": list(lab.frontend.input_shape),
            "note": (
                "Host ORT INT8 is not RUHMI INT8. RUHMI must re-quantize with its "
                "own calibrator on x86 Linux. See deployment/ra8p1/."
            ),
        }
    )
    (out_dir / "quant_report.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--ckpt", type=Path, required=True)
    p.add_argument("--out", type=Path, default=Path("artifacts/export"))
    args = p.parse_args(argv)
    report = export_from_checkpoint(args.ckpt, args.out)
    print(json.dumps({k: report[k] for k in ("fp32_onnx", "int8_onnx", "fp32_vs_int8", "label")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
