# SpectraSynq EdgeAI Lab

Experimental Edge-AI lab for SpectraSynq. **Not production firmware.**

The first model is intentionally narrow:

> **Semantic-v0** — from a 1-second mixed-audio window, estimate continuous
> `vocals`, `drums`, and `bass` activity.

That one target exercises the whole future chain: dataset, Mac training,
quantization, Ethos-U55 compilation, golden vectors, and later “does this
actually make the lights more musically intelligent?”

## Current phase

**Pre-Titan, host pipeline up.** The RA8P1 Titan Mini is ordered and not here.
On 2026-08-30 this Mac: venv, MPS smoke, Semantic-v0 trained on **synthetic**
stems, ONNX + host INT8, 32 golden tensors. RUHMI compile is wired
(`deployment/ra8p1`) but **not executed** — Docker daemon was down.

Any number not measured on the board is labelled `HOST-ONLY` or `PRE-SILICON`.
See [docs/HOST_RECEIPTS.md](docs/HOST_RECEIPTS.md).

## Two machines, two environments

| Lane | Where | What |
| --- | --- | --- |
| Train / export | this M4 Mac, Python 3.12, PyTorch MPS | dataset, CNN, ONNX, host INT8, golden tensors |
| RUHMI / MERA compile | Ubuntu 22.04 **x86-64**, Python 3.10 | FP32 ONNX → INT8 → C99 for Ethos-U55 |

There is no native Apple-silicon RUHMI wheel. Do not turn the whole lab into
an x86 VM just because the compiler is x86.

## Reproduce (host)

```bash
cd /Users/spectrasynq/SpectraSynq-EdgeAI-Lab
uv sync --python 3.12
uv run edgeai-host-probe
uv run edgeai-smoke
uv run pytest
uv run edgeai-train --out experiments/semantic_v0_synth
uv run edgeai-export --ckpt experiments/semantic_v0_synth/semantic_v0_best.pt --out artifacts/export
uv run edgeai-golden --ckpt experiments/semantic_v0_synth/semantic_v0_best.pt \
    --int8-onnx artifacts/export/semantic_v0_int8.onnx --out artifacts/golden
```

## Reproduce (RA8P1 compile, x86)

See [deployment/ra8p1/README.md](deployment/ra8p1/README.md). Short version:

```bash
docker build --platform linux/amd64 -t spectrasynq-ruhmi:2.6.0 deployment/ra8p1
./deployment/ra8p1/compile.sh artifacts/export/semantic_v0_fp32.onnx artifacts/ruhmi
```

Until that job has actually produced C sources, U55 coverage is **not measured**.

## What this is not

- Not a production singing/drum/bass detector for sale.
- Not a replacement for K1 deterministic DSP (onset, tempo, spectral energy).
- Not a licence to train a shipping model on MUSDB18 (research / non-commercial
  corpus — see [datasets/README.md](datasets/README.md)).

## Layout

```
src/edgeai/           library (frontend, CNN, train, export, golden)
models/configs/       YAML overlays
datasets/             manifests + licence notes (no audio in git)
deployment/ra8p1/     RUHMI Docker + compile wrapper
docs/                 decisions, host, Titan bring-up
experiments/          run receipts (gitignored)
artifacts/            onnx / golden / ruhmi output (gitignored)
```

## Pre-Titan finish line

A reproducible Mac → PyTorch → quantized ONNX → RA8P1/U55 compile path, one
useful audio-semantic baseline, and golden tensors ready for silicon.

Ship path after that is in [docs/TITAN_BRINGUP.md](docs/TITAN_BRINGUP.md).
