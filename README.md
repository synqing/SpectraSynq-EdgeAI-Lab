# SpectraSynq EdgeAI Lab

Experimental lab: what musical understanding should drive SpectraSynq lights,
and can a tiny NPU model carry any of it?

**Not production firmware. Not “put an NPU in the product.”**

Amendment 001 is in force: **MIR reconnaissance and a host oracle come before
a bespoke student model.** Semantic-v0 (vocals/drums/bass CNN) is a kept
**experiment** and a deployment-toolchain witness — not architecture authority.

## Current phase

**Pre-Titan, MIR-first.** Host PyTorch/MPS/ONNX path exists. RUHMI compile is
wired and **not run** (Docker down). MIR registry + landscape + conventional
oracle traces are in `docs/mir/` and `mir/registry.yaml`.

Numbers not measured on the RA8P1 are `HOST-ONLY` or `PRE-SILICON`.

## Reproduce

```bash
uv sync --python 3.12 --extra mir --extra dev
uv run pytest
uv run edgeai-smoke                 # toolchain, not the product model
uv run python scripts/mir_oracle_run.py
```

RUHMI (x86 Ubuntu 22.04 / Python 3.10), when Docker is up:

```bash
./deployment/ra8p1/compile.sh artifacts/smoke/smoke.onnx artifacts/ruhmi
```

## Layout

```
mir/registry.yaml         asset + licence matrix
docs/mir/                 landscape, gate, delta
src/edgeai/mir/           host oracle (librosa traces, plots)
src/edgeai/semantic_v0.py experiment / U55-shaped toy
deployment/ra8p1/         RUHMI Docker + GHA
experiments/semantic_v0/  NOT architecture authority
```

## Pre-Titan finish line (amended)

A host MIR oracle lab, an evidence-backed idea of which descriptors are useful
and legal, a working Mac→U55 compile path, and **then** one justified student
with golden vectors — so Titan tests a domain-informed candidate.

Delta: [docs/AMENDMENT_001_DELTA.md](docs/AMENDMENT_001_DELTA.md).
Gate: [docs/mir/SELECTION_GATE.md](docs/mir/SELECTION_GATE.md).
