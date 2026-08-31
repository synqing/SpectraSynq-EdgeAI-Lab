#!/usr/bin/env python3
"""HOST-ONLY: can a tiny causal CNN recover four-source share from a mixture?

Official MUSDB18 song-level splits. Not a student-I/O freeze.
commercial_training_lineage=false.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
import torch
from torch.utils.data import DataLoader

from edgeai.config import FrontendConfig
from edgeai.dataset import SongRef, assert_no_song_leak
from edgeai.device import device_name, pick_device
from edgeai.frontend import LogMelFrontend
from edgeai.mir.source_oracle import SOURCES
from edgeai.share_student import (
    ShareStudent,
    ShareWindowDataset,
    WindowBank,
    apply_mix_linear_baseline,
    assert_full_musdb,
    concat_banks,
    count_parameters,
    featurize_starts,
    fit_mix_linear_baseline,
    fp32_nbytes,
    grid_starts,
    load_song_stems_16k,
    musdb_song_split,
    random_starts,
    resolve_musdb_root,
    safe_name,
    share_loss,
    song_mp4,
    take_songs,
    verdict_from_metrics,
    within_track_rows,
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts" / "share_student"
DOC = ROOT / "docs" / "mir" / "SHARE_STUDENT.md"
P3B_TRUE_MIX = {"vocals": 0.17, "drums": 0.10, "bass": 0.16}

# Experiment frontend — recorded, not a product lock.
FE_NOTE = (
    "16 kHz / 1 s / 64-mel / 100-frame log-mel is this experiment's frontend, "
    "not a frozen student I/O. Causal conv + AdaptiveAvgPool2d((1,1)) → 1 s latency."
)


def git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, stderr=subprocess.DEVNULL, text=True
        ).strip()
    except Exception:
        return "UNCOMMITTED"


def blocked(paths_checked: list[str], reason: str, out_dir: Path) -> int:
    out_dir.mkdir(parents=True, exist_ok=True)
    receipt = {
        "status": "BLOCKED",
        "label": "HOST-ONLY",
        "commercial_training_lineage": False,
        "student_io_frozen": False,
        "reason": reason,
        "paths_checked": paths_checked,
        "commit": git_commit(),
    }
    (out_dir / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    DOC.write_text(_markdown_blocked(receipt))
    print(f"BLOCKED: {reason}", file=sys.stderr)
    return 2


def _mae(a: np.ndarray, b: np.ndarray) -> dict[str, float]:
    d = np.abs(np.asarray(a) - np.asarray(b))
    out = {name: float(np.mean(d[:, i])) for i, name in enumerate(SOURCES)}
    out["macro"] = float(np.mean(d))
    return out


def _feat_cache_path(
    cache_dir: Path,
    song: SongRef,
    *,
    mode: str,
    n_random: int,
    hop_label: int,
    seed: int,
) -> Path:
    return cache_dir / f"{safe_name(song)}__{mode}_n{n_random}_h{hop_label}_s{seed}.npz"


def _load_cached_bank(path: Path, song: SongRef) -> WindowBank | None:
    if not path.is_file():
        return None
    z = np.load(path)
    n = int(z["share"].shape[0])
    return WindowBank(
        logmel=z["logmel"].astype(np.float32),
        share=z["share"].astype(np.float32),
        mix_rms=z["mix_rms"].astype(np.float32),
        powers=z["powers"].astype(np.float32),
        song_ids=[song.song_id] * n,
    )


def _save_bank(path: Path, bank: WindowBank) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        path,
        logmel=bank.logmel,
        share=bank.share,
        mix_rms=bank.mix_rms,
        powers=bank.powers,
    )


def featurize_song(
    song: SongRef,
    root: Path,
    frontend: LogMelFrontend,
    *,
    mode: str,
    n_random: int,
    hop_label: int,
    seed: int,
    cache_dir: Path | None = None,
) -> WindowBank:
    if cache_dir is not None:
        cpath = _feat_cache_path(
            cache_dir, song, mode=mode, n_random=n_random, hop_label=hop_label, seed=seed
        )
        cached = _load_cached_bank(cpath, song)
        if cached is not None:
            return cached
    stems16 = load_song_stems_16k(song_mp4(root, song), dst_sr=frontend.cfg.sample_rate)
    mix = stems16["mix"]
    stems = {k: stems16[k] for k in SOURCES}
    n_audio = int(mix.shape[0])
    n_samples = frontend.cfg.n_samples
    if mode == "grid":
        starts = grid_starts(n_audio, n_samples, n_samples)
    else:
        digest = int(hashlib.sha256(song.song_id.encode()).hexdigest()[:8], 16)
        rng = np.random.default_rng(seed + digest % 10_000)
        starts = random_starts(n_audio, n_samples, n_random, rng)
    if not starts:
        raise RuntimeError(f"track too short for 1 s windows: {song.song_id} n={n_audio}")
    bank = featurize_starts(stems, mix, starts, frontend, hop_label)
    bank.song_ids = [song.song_id] * len(starts)
    if cache_dir is not None:
        _save_bank(
            _feat_cache_path(
                cache_dir, song, mode=mode, n_random=n_random, hop_label=hop_label, seed=seed
            ),
            bank,
        )
    return bank


def run_split(
    songs: list[SongRef],
    root: Path,
    frontend: LogMelFrontend,
    *,
    mode: str,
    n_random: int,
    hop_label: int,
    seed: int,
    label: str,
    cache_dir: Path | None = None,
) -> WindowBank:
    banks: list[WindowBank] = []
    t0 = time.perf_counter()
    for i, song in enumerate(songs, start=1):
        bank = featurize_song(
            song,
            root,
            frontend,
            mode=mode,
            n_random=n_random,
            hop_label=hop_label,
            seed=seed,
            cache_dir=cache_dir,
        )
        banks.append(bank)
        dt = time.perf_counter() - t0
        print(
            f"  [{label}] {i}/{len(songs)} {song.song_id.split('/')[-1][:48]} "
            f"n={len(bank)}  {dt:.1f}s",
            flush=True,
        )
    out = concat_banks(banks)
    assert_no_song_leak(songs)
    return out


def train_loop(
    model: ShareStudent,
    train_ds: ShareWindowDataset,
    val_ds: ShareWindowDataset,
    device: torch.device,
    *,
    epochs: int,
    batch_size: int,
    lr: float,
) -> list[dict[str, Any]]:
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False, num_workers=0)
    history: list[dict[str, Any]] = []
    best_val = float("inf")
    best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
    for epoch in range(1, epochs + 1):
        model.train()
        running = 0.0
        n_batches = 0
        for batch in train_loader:
            logmel = batch["logmel"].to(device)
            target = batch["share"].to(device)
            opt.zero_grad(set_to_none=True)
            pred = model(logmel)["shares"]
            loss = share_loss(pred, target)
            loss.backward()
            opt.step()
            running += float(loss.item())
            n_batches += 1
        val_loss, val_mae = eval_loss(model, val_loader, device)
        row = {
            "epoch": epoch,
            "train_mse": running / max(n_batches, 1),
            "val_mse": val_loss,
            "val_mae_macro": val_mae,
        }
        history.append(row)
        print(
            f"  epoch {epoch}/{epochs} train_mse={row['train_mse']:.4f} "
            f"val_mse={val_loss:.4f} val_mae={val_mae:.4f}",
            flush=True,
        )
        if val_loss < best_val:
            best_val = val_loss
            best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
    model.load_state_dict(best_state)
    return history


@torch.no_grad()
def eval_loss(model: ShareStudent, loader: DataLoader, device: torch.device) -> tuple[float, float]:
    model.eval()
    losses: list[float] = []
    maes: list[float] = []
    for batch in loader:
        pred = model(batch["logmel"].to(device))["shares"]
        target = batch["share"].to(device)
        losses.append(float(share_loss(pred, target).item()))
        maes.append(float((pred - target).abs().mean().item()))
    return float(np.mean(losses)), float(np.mean(maes))


@torch.no_grad()
def predict_bank(model: ShareStudent, bank: WindowBank, device: torch.device, batch_size: int) -> np.ndarray:
    model.eval()
    ds = ShareWindowDataset(bank)
    loader = DataLoader(ds, batch_size=batch_size, shuffle=False, num_workers=0)
    chunks: list[np.ndarray] = []
    for batch in loader:
        shares = model(batch["logmel"].to(device))["shares"].cpu().numpy()
        chunks.append(shares)
    return np.concatenate(chunks, axis=0)


def pack_source_metrics(rows: dict[str, dict[str, float]]) -> dict[str, Any]:
    return {
        name: {
            "within_r_pred_true": rows[name]["r_pred_true"],
            "within_r_pred_mix": rows[name]["r_pred_mix"],
            "within_r_true_mix": rows[name]["r_true_mix"],
            "p3b_within_r_true_mix_ref": P3B_TRUE_MIX.get(name),
            "n_songs": int(rows[name]["n_songs"]),
        }
        for name in SOURCES
    }


def _fmt(x: float) -> str:
    if not np.isfinite(x):
        return "nan"
    return f"{x:.3f}"


def write_markdown(receipt: dict[str, Any]) -> None:
    DOC.parent.mkdir(parents=True, exist_ok=True)
    DOC.write_text(_markdown(receipt))


def _markdown_blocked(receipt: dict[str, Any]) -> str:
    paths = ", ".join(f"`{p}`" for p in receipt["paths_checked"])
    return f"""---
abstract: "Share-student recoverability BLOCKED — MUSDB18 full STEMS not found. HOST-ONLY. student I/O not frozen."
---

# Share student — recoverability

**BLOCKED.** Full MUSDB18 STEMS not found. Paths checked: {paths}.

`datasets/musdb_sample` is 7 s excerpts — screening only, not this close.

Student I/O is **not** frozen. Waveform Tempo remains a P3-C reference binding only.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:edgeai | BLOCKED receipt; MUSDB path miss. |
"""


def _markdown(receipt: dict[str, Any]) -> str:
    v = receipt["verdict"]
    m = receipt["metrics"]["student"]
    lin = receipt["metrics"]["mix_linear"]
    mae = receipt["metrics"]["student_mae"]
    split = receipt["split"]
    rows = []
    for name in SOURCES:
        s, l = m[name], lin[name]
        p3 = s.get("p3b_within_r_true_mix_ref")
        p3s = "—" if p3 is None else f"{p3:.2f}"
        rows.append(
            f"| {name} | {_fmt(s['within_r_pred_true'])} | {_fmt(s['within_r_pred_mix'])} | "
            f"{_fmt(s['within_r_true_mix'])} | {p3s} | {_fmt(l['within_r_pred_true'])} | {_fmt(mae[name])} |"
        )
    table = "\n".join(rows)
    train_note = (
        "all official-train remaining after val carve"
        if split["train_capped"] is False
        else f"bounded subset n={split['n_train']} of official train"
    )
    return f"""---
abstract: "HOST-ONLY share-student recoverability {v} on official MUSDB18 song splits. Four-source mixture→share vs mix-energy. Student I/O not frozen. commercial_training_lineage=false."
---

# Share student — recoverability

**{v}** on whether a tiny causal CNN recovers vocals/drums/bass/other **share** from the mixture better than mix-energy.

HOST-ONLY. MUSDB18 STEMS, research/NC. `commercial_training_lineage: false`. Student I/O is **not** frozen.

Waveform Tempo × `source_share` × `head_position` is a P3-C **reference binding** only. This run did not re-score P3-C and does not claim share improves all lights.

## Question

Can a tiny model infer four-source ownership (share) from mixture audio, on official MUSDB18 **song-level** splits, better than a mix-energy baseline?

Share is hop stem-power / sum, silence → zeros — same definition as `source_oracle`. The student emits four non-negative powers (`softplus` logits) then that normalisation. No composition_change ML head.

## Split

| set | n songs | n windows | origin |
| --- | ---: | ---: | --- |
| train | {split["n_train"]} | {split["n_train_windows"]} | official `train/` ({train_note}); val carved by hashed **song** id |
| val | {split["n_val"]} | {split["n_val_windows"]} | official `train/` holdout songs, not windows |
| test | {split["n_test"]} | {split["n_test_windows"]} | official `test/` |

Window-level splitting is banned. `assert_no_song_leak` held.

## Model (experiment, not a lock)

- {receipt["model"]["params"]} params, {receipt["model"]["fp32_kib"]} KiB fp32
- causal depthwise-separable CNN + `AdaptiveAvgPool2d((1,1))` (D11 — no `tensor.mean`)
- {FE_NOTE}

## Official test — within-track Pearson

n_test_songs = {split["n_test"]}. 1 s windows, 1 s hop. Compared to this-run `r(true_share, mix)` and to P3-B hop-level refs (vocals 0.17, drums 0.10, bass 0.16).

| source | r(pred, true) | r(pred, mix) | r(true, mix) | P3-B r(true, mix) | mix-linear r(pred, true) | MAE |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
{table}

Macro MAE = {mae["macro"]:.3f}. Epochs = {receipt["train"]["epochs"]}. Device = `{receipt["device"]}`.

**PASS** requires vocals/drums/bass: r(pred,true) ≥ max(0.30, r(true,mix)+0.15), beating the mix-linear baseline by 0.05, and r(pred,mix) not mix-copying (≤ r(true,mix)+0.20). **FAIL** if none of those three beat mix-energy by 0.08. Else **INCONCLUSIVE**.

This-run `r(true, mix)` is on **1 s windows**. P3-B refs are hop-512 (~32 ms). Do not treat them as the same number.

## What this does not establish

- Student I/O, 16 kHz, 1 s, 64-mel, or four-source head as the RA8P1 contract.
- That share improves lighting. P3-C Waveform Tempo binding is reference-only.
- On-silicon / U55 compile / Demucs / composition_change as a learned head.
- A commercial training right.

Re-run: `uv run pytest tests/test_share_student.py && uv run python scripts/share_student_feasibility.py`

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:edgeai | HOST-ONLY recoverability {v}; song-level MUSDB18; I/O not frozen. |
"""


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, default=None)
    p.add_argument("--out", type=Path, default=OUT)
    p.add_argument("--epochs", type=int, default=6)
    p.add_argument("--batch-size", type=int, default=16)
    p.add_argument("--lr", type=float, default=1e-3)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--max-train", type=int, default=None)
    p.add_argument("--max-val", type=int, default=None)
    p.add_argument("--max-test", type=int, default=None)
    p.add_argument("--train-windows", type=int, default=24)
    p.add_argument("--val-windows", type=int, default=16)
    p.add_argument("--hop-label", type=int, default=512)
    p.add_argument("--device", type=str, default=None)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    out_dir = args.out if args.out.is_absolute() else ROOT / args.out
    out_dir.mkdir(parents=True, exist_ok=True)

    checked = [
        str((args.root or Path("datasets/musdb18")).resolve()),
        str(Path("datasets/musdb18").resolve()),
        str(Path(os_env_root())) if os_env_root() else "(MUSDB_ROOT unset)",
    ]
    root = resolve_musdb_root(args.root)
    if root is None:
        return blocked(checked, "MUSDB18 train/test not found (full STEMS expected)", out_dir)
    try:
        assert_full_musdb(root)
    except (FileNotFoundError, RuntimeError) as exc:
        return blocked(checked + [str(root)], str(exc), out_dir)

    fe_cfg = FrontendConfig()
    frontend = LogMelFrontend(fe_cfg)
    frontend.eval()
    songs = musdb_song_split(root, seed=args.seed)
    assert_no_song_leak(songs)
    train_songs = take_songs(songs, "train", args.max_train, args.seed)
    val_songs = take_songs(songs, "val", args.max_val, args.seed + 1)
    test_songs = take_songs(songs, "test", args.max_test, args.seed + 2)
    if not train_songs or not val_songs or not test_songs:
        return blocked(checked, "empty train/val/test after song carve", out_dir)

    print(
        f"MUSDB {root}  train={len(train_songs)} val={len(val_songs)} test={len(test_songs)}",
        flush=True,
    )
    t_load = time.perf_counter()
    feat_cache = out_dir / "feats"
    train_bank = run_split(
        train_songs, root, frontend, mode="random", n_random=args.train_windows,
        hop_label=args.hop_label, seed=args.seed, label="train", cache_dir=feat_cache,
    )
    val_bank = run_split(
        val_songs, root, frontend, mode="random", n_random=args.val_windows,
        hop_label=args.hop_label, seed=args.seed + 11, label="val", cache_dir=feat_cache,
    )
    test_bank = run_split(
        test_songs, root, frontend, mode="grid", n_random=0,
        hop_label=args.hop_label, seed=args.seed, label="test", cache_dir=feat_cache,
    )
    load_s = time.perf_counter() - t_load

    device = pick_device(args.device)
    print(f"device {device_name(device)}  load {load_s:.1f}s", flush=True)
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    model = ShareStudent().to(device)
    n_params = count_parameters(model)
    history = train_loop(
        model,
        ShareWindowDataset(train_bank),
        ShareWindowDataset(val_bank),
        device,
        epochs=args.epochs,
        batch_size=args.batch_size,
        lr=args.lr,
    )

    pred = predict_bank(model, test_bank, device, args.batch_size)
    true = test_bank.share
    mix = test_bank.mix_rms
    coef = fit_mix_linear_baseline(train_bank.mix_rms, train_bank.share)
    lin_pred = apply_mix_linear_baseline(mix, coef)
    student_rows = within_track_rows(true, pred, mix, test_bank.song_ids)
    linear_rows = within_track_rows(true, lin_pred, mix, test_bank.song_ids)
    n_test = len({s for s in test_bank.song_ids})
    verdict = verdict_from_metrics(student_rows, linear_rows, n_test)
    ckpt = out_dir / "share_student_best.pt"
    torch.save({"state_dict": model.state_dict(), "cfg": model.cfg.__dict__}, ckpt)

    receipt: dict[str, Any] = {
        "status": "VERIFIED" if verdict in {"PASS", "FAIL", "INCONCLUSIVE"} else "NOT_VERIFIED",
        "verdict": verdict,
        "label": "HOST-ONLY",
        "commercial_training_lineage": False,
        "student_io_frozen": False,
        "corpus": "MUSDB18 standard STEMS (not HQ, not 7s sample)",
        "licence": "educational/NC; commercial_training_lineage=false",
        "root": str(root),
        "commit": git_commit(),
        "device": device_name(device),
        "frontend": {
            "sample_rate": fe_cfg.sample_rate,
            "duration_s": fe_cfg.duration_s,
            "n_mels": fe_cfg.n_mels,
            "n_frames": fe_cfg.n_frames,
            "n_fft": fe_cfg.n_fft,
            "hop_length": fe_cfg.hop_length,
            "product_lock": False,
            "note": FE_NOTE,
        },
        "label_definition": {
            "sources": list(SOURCES),
            "hop_samples": args.hop_label,
            "share": "sum of hop mean-square per stem / total; silence total<=1e-10 → zeros",
            "matches_source_oracle": True,
            "composition_change_head": False,
        },
        "split": {
            "unit": "song",
            "official_train_test": True,
            "val_carved_from_train_by_song_hash": True,
            "n_train": len(train_songs),
            "n_val": len(val_songs),
            "n_test": len(test_songs),
            "n_train_windows": len(train_bank),
            "n_val_windows": len(val_bank),
            "n_test_windows": len(test_bank),
            "train_capped": args.max_train is not None,
            "val_capped": args.max_val is not None,
            "test_capped": args.max_test is not None,
            "train_songs": [s.song_id for s in train_songs],
            "val_songs": [s.song_id for s in val_songs],
            "test_songs": [s.song_id for s in test_songs],
        },
        "model": {
            "class": "ShareStudent",
            "params": n_params,
            "fp32_nbytes": fp32_nbytes(model),
            "fp32_kib": round(fp32_nbytes(model) / 1024, 1),
            "pool": "AdaptiveAvgPool2d((1,1))",
            "causal_conv": True,
            "powers_activation": "softplus",
        },
        "train": {
            "epochs": args.epochs,
            "batch_size": args.batch_size,
            "lr": args.lr,
            "seed": args.seed,
            "loss": "mse(share)",
            "history": history,
            "load_s": load_s,
        },
        "metrics": {
            "student": pack_source_metrics(student_rows),
            "mix_linear": pack_source_metrics(linear_rows),
            "student_mae": _mae(true, pred),
            "mix_linear_mae": _mae(true, lin_pred),
            "p3b_reference_within_r_true_share_vs_mix": P3B_TRUE_MIX,
        },
        "p3c_waveform_tempo": "reference binding only; not re-run",
        "checkpoint": str(ckpt),
    }
    (out_dir / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    write_markdown(receipt)
    print(f"verdict {verdict}  receipt {out_dir / 'receipt.json'}", flush=True)
    return 0


def os_env_root() -> str | None:
    import os

    return os.environ.get("MUSDB_ROOT")


if __name__ == "__main__":
    raise SystemExit(main())
