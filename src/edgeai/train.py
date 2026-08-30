"""Mundane train / validate / checkpoint loop. MPS-first, CUDA/CPU portable."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
import torch
from torch.utils.data import DataLoader

from edgeai.config import CLASSES, LabConfig
from edgeai.dataset import (
    StemWindowDataset,
    assert_no_song_leak,
    collate,
    synthetic_songs,
    write_manifest,
)
from edgeai.device import device_name, pick_device
from edgeai.metrics import per_class_report
from edgeai.semantic_v0 import SemanticV0, count_parameters, fp32_nbytes


def git_commit(repo: Path) -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=repo, stderr=subprocess.DEVNULL, text=True
        ).strip()
    except Exception:
        return "UNCOMMITTED"


def set_seed(seed: int) -> None:
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


@torch.no_grad()
def evaluate(
    model: SemanticV0,
    loader: DataLoader,
    device: torch.device,
) -> tuple[float, dict[str, Any], np.ndarray, np.ndarray]:
    model.eval()
    loss_fn = torch.nn.BCEWithLogitsLoss()
    losses: list[float] = []
    ys: list[np.ndarray] = []
    ps: list[np.ndarray] = []
    for batch in loader:
        logmel = batch["logmel"].to(device)
        target = batch["target"].to(device)
        logits = model(logmel)
        loss = loss_fn(logits, target)
        losses.append(float(loss.item()))
        ys.append(target.detach().cpu().numpy())
        ps.append(torch.sigmoid(logits).detach().cpu().numpy())
    y = np.concatenate(ys, axis=0)
    p = np.concatenate(ps, axis=0)
    report = per_class_report(y, p)
    return float(np.mean(losses)), report, y, p


def train_one(
    *,
    lab: LabConfig,
    out_dir: Path,
    device: torch.device,
    source: str = "synthetic",
    musdb_root: Path | None = None,
) -> dict[str, Any]:
    set_seed(lab.train.seed)
    out_dir.mkdir(parents=True, exist_ok=True)
    songs = synthetic_songs(n=48, seed=lab.train.seed)
    assert_no_song_leak(songs)
    write_manifest(songs, out_dir / "split_manifest.json")

    train_ds = StemWindowDataset(
        songs, "train", lab, lab.train.windows_per_epoch, augment=True, base_seed=lab.train.seed
    )
    val_ds = StemWindowDataset(
        songs, "val", lab, lab.train.val_windows, augment=False, base_seed=lab.train.seed + 1
    )
    test_ds = StemWindowDataset(
        songs, "test", lab, lab.train.test_windows, augment=False, base_seed=lab.train.seed + 2
    )
    train_loader = DataLoader(
        train_ds,
        batch_size=lab.train.batch_size,
        shuffle=True,
        num_workers=lab.train.num_workers,
        collate_fn=collate,
    )
    val_loader = DataLoader(
        val_ds, batch_size=lab.train.batch_size, shuffle=False, collate_fn=collate
    )
    test_loader = DataLoader(
        test_ds, batch_size=lab.train.batch_size, shuffle=False, collate_fn=collate
    )

    model = SemanticV0(lab.model).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=lab.train.lr, weight_decay=lab.train.weight_decay)
    loss_fn = torch.nn.BCEWithLogitsLoss()

    history: list[dict[str, Any]] = []
    best_val = float("inf")
    best_path = out_dir / "semantic_v0_best.pt"

    t0 = time.perf_counter()
    for epoch in range(1, lab.train.epochs + 1):
        model.train()
        running = 0.0
        n_batches = 0
        for batch in train_loader:
            logmel = batch["logmel"].to(device)
            target = batch["target"].to(device)
            logits = model(logmel)
            loss = loss_fn(logits, target)
            opt.zero_grad(set_to_none=True)
            loss.backward()
            opt.step()
            running += float(loss.item())
            n_batches += 1
        train_loss = running / max(1, n_batches)
        val_loss, val_report, _, _ = evaluate(model, val_loader, device)
        row = {
            "epoch": epoch,
            "train_loss": train_loss,
            "val_loss": val_loss,
            "val_macro_mae": val_report["macro_mae"],
            "val_macro_f1": val_report["macro_f1"],
        }
        history.append(row)
        print(
            f"epoch {epoch:02d}  train_loss={train_loss:.4f}  "
            f"val_loss={val_loss:.4f}  val_mae={val_report['macro_mae']:.4f}  "
            f"val_f1={val_report['macro_f1']:.3f}",
            flush=True,
        )
        if val_loss < best_val:
            best_val = val_loss
            torch.save(
                {
                    "model": model.state_dict(),
                    "config": lab.to_dict(),
                    "epoch": epoch,
                    "val_loss": val_loss,
                    "val_report": val_report,
                    "classes": list(CLASSES),
                },
                best_path,
            )

    ckpt = torch.load(best_path, map_location="cpu", weights_only=False)
    model.load_state_dict(ckpt["model"])
    model.to(device)
    test_loss, test_report, y_test, p_test = evaluate(model, test_loader, device)

    # Host inference timing on one batch, HOST-ONLY.
    model.eval()
    sample = next(iter(test_loader))["logmel"][:1].to(device)
    if device.type == "mps":
        torch.mps.synchronize()
    elif device.type == "cuda":
        torch.cuda.synchronize()
    for _ in range(5):
        _ = model(sample)
    if device.type == "mps":
        torch.mps.synchronize()
    t_inf0 = time.perf_counter()
    n_rep = 20
    for _ in range(n_rep):
        _ = model(sample)
    if device.type == "mps":
        torch.mps.synchronize()
    elif device.type == "cuda":
        torch.cuda.synchronize()
    infer_ms = (time.perf_counter() - t_inf0) * 1000.0 / n_rep

    wall_s = time.perf_counter() - t0
    repo = Path(__file__).resolve().parents[2]
    receipt = {
        "label": "HOST-ONLY",
        "corpus": "SYNTHETIC" if source == "synthetic" else "MUSDB18-RESEARCH",
        "warning": (
            "Synthetic metrics prove the training loop, not musical intelligence. "
            "Do not promote these F1/MAE numbers as product evidence."
        ),
        "git_commit": git_commit(repo),
        "device": device_name(device),
        "torch": torch.__version__,
        "python": sys.version.split()[0],
        "seed": lab.train.seed,
        "config": lab.to_dict(),
        "classes": list(CLASSES),
        "param_count": count_parameters(model),
        "fp32_bytes": fp32_nbytes(model),
        "best_checkpoint": str(best_path),
        "best_val_loss": best_val,
        "test_loss": test_loss,
        "test_report": test_report,
        "history": history,
        "host_infer_ms_per_window": infer_ms,
        "wall_s": wall_s,
        "n_train_songs": sum(1 for s in songs if s.split == "train"),
        "n_val_songs": sum(1 for s in songs if s.split == "val"),
        "n_test_songs": sum(1 for s in songs if s.split == "test"),
    }
    (out_dir / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    np.savez(out_dir / "test_predictions.npz", y_true=y_test, y_pred=p_test)
    print(json.dumps({k: receipt[k] for k in ("param_count", "fp32_bytes", "test_report", "label")}, indent=2))
    return receipt


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Train Semantic-v0")
    p.add_argument("--out", type=Path, default=Path("experiments/semantic_v0_synth"))
    p.add_argument("--device", type=str, default=None)
    p.add_argument("--epochs", type=int, default=None)
    p.add_argument("--windows", type=int, default=None)
    p.add_argument("--seed", type=int, default=None)
    p.add_argument("--config", type=Path, default=None)
    args = p.parse_args(argv)
    lab = LabConfig.from_yaml(args.config) if args.config else LabConfig()
    if args.epochs is not None:
        lab.train.epochs = args.epochs
    if args.windows is not None:
        lab.train.windows_per_epoch = args.windows
    if args.seed is not None:
        lab.train.seed = args.seed
    device = pick_device(args.device)
    print(f"device={device_name(device)}", flush=True)
    train_one(lab=lab, out_dir=args.out, device=device)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
