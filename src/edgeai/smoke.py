"""Phase 1 host smoke: TRAIN → SAVE → LOAD → EXPORT on synthetic tensors.

Does not download MUSDB. Does not claim musical accuracy.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch

from edgeai.config import LabConfig
from edgeai.device import device_name, pick_device
from edgeai.export import export_onnx
from edgeai.semantic_v0 import SemanticV0, count_parameters, fp32_nbytes
from edgeai.train import git_commit, set_seed


def probe(device: torch.device) -> dict:
    x = torch.randn(4, 1, 64, 100, device=device)
    t0 = time.perf_counter()
    y = (torch.nn.functional.relu(x) + 1).mean()
    if device.type == "mps":
        torch.mps.synchronize()
    elif device.type == "cuda":
        torch.cuda.synchronize()
    _ = float(y.detach().cpu())
    return {
        "device": device_name(device),
        "torch": torch.__version__,
        "python": sys.version.split()[0],
        "mps_available": bool(torch.backends.mps.is_available()),
        "cuda_available": bool(torch.cuda.is_available()),
        "probe_s": time.perf_counter() - t0,
    }


def smoke_train_export(out_dir: Path, device: torch.device, steps: int = 8) -> dict:
    set_seed(0)
    lab = LabConfig()
    lab.train.epochs = 1
    model = SemanticV0(lab.model).to(device)
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    loss_fn = torch.nn.BCEWithLogitsLoss()
    n_params = count_parameters(model)

    losses = []
    model.train()
    for step in range(steps):
        logmel = torch.randn(8, 1, lab.frontend.n_mels, lab.frontend.n_frames, device=device)
        target = torch.rand(8, 3, device=device)
        logits = model(logmel)
        loss = loss_fn(logits, target)
        opt.zero_grad(set_to_none=True)
        loss.backward()
        opt.step()
        losses.append(float(loss.item()))

    out_dir.mkdir(parents=True, exist_ok=True)
    ckpt = out_dir / "smoke.pt"
    torch.save({"model": model.state_dict(), "config": lab.to_dict()}, ckpt)

    loaded = SemanticV0(lab.model)
    loaded.load_state_dict(torch.load(ckpt, map_location="cpu", weights_only=False)["model"])
    loaded.eval()
    model_cpu = SemanticV0(lab.model)
    model_cpu.load_state_dict(model.state_dict())
    model_cpu.eval()

    x = torch.randn(1, 1, lab.frontend.n_mels, lab.frontend.n_frames)
    with torch.no_grad():
        a = torch.sigmoid(model_cpu(x)).numpy()
        b = torch.sigmoid(loaded(x)).numpy()
    load_mae = float(np.mean(np.abs(a - b)))

    onnx_path = out_dir / "smoke.onnx"
    export_onnx(model_cpu, onnx_path, lab, sigmoid=True)

    import onnxruntime as ort

    sess = ort.InferenceSession(str(onnx_path), providers=["CPUExecutionProvider"])
    c = sess.run(["activity"], {"logmel": x.numpy()})[0]
    onnx_mae = float(np.mean(np.abs(a - c)))

    receipt = {
        "label": "HOST-ONLY",
        "phase": 1,
        "ok": load_mae < 1e-6 and onnx_mae < 1e-4,
        "git_commit": git_commit(Path(__file__).resolve().parents[2]),
        "probe": probe(device),
        "param_count": n_params,
        "fp32_bytes": fp32_nbytes(model_cpu),
        "train_losses": losses,
        "load_mae": load_mae,
        "onnx_vs_pytorch_mae": onnx_mae,
        "onnx_path": str(onnx_path),
        "ckpt_path": str(ckpt),
        "input_shape": list(lab.frontend.input_shape),
        "onnx_opset": lab.onnx_opset,
    }
    (out_dir / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    return receipt


def host_probe_main(argv: list[str] | None = None) -> int:
    device = pick_device()
    info = probe(device)
    print(json.dumps(info, indent=2))
    Path("artifacts").mkdir(exist_ok=True)
    Path("artifacts/host_probe.json").write_text(json.dumps(info, indent=2) + "\n")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--out", type=Path, default=Path("artifacts/smoke"))
    p.add_argument("--device", type=str, default=None)
    p.add_argument("--steps", type=int, default=8)
    args = p.parse_args(argv)
    device = pick_device(args.device)
    print(f"device={device_name(device)}", flush=True)
    receipt = smoke_train_export(args.out, device, steps=args.steps)
    print(json.dumps(receipt, indent=2))
    if not receipt["ok"]:
        print("SMOKE FAILED", file=sys.stderr)
        return 1
    print("SMOKE PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
