# RA8P1 / Ethos-U55 compile lane

**PRE-SILICON.** This directory does not talk to a board. It exists so we can
discover toolchain incompatibilities before Titan arrives.

## Facts (not hopes)

- Pin: **ruhmi-framework-mcu `6c5aad9` / Release-2026-06-19**, MERA `2.6.0+pkg.4815`.
  Do not clone `main` in CI.
- Supported hosts: Ubuntu 22.04 and Windows 10/11, **Python 3.10**, **x86-64**.
- Wheel from that commit's `install/` directory, not a floating `main` URL.
- Ubuntu runners need Renesas' libstdc++ recipe (`ppa:ubuntu-toolchain-r/test`,
  upgrade `libstdc++6`/`libgcc-s1`, gcc-13). GHA run 33317047371 failed at
  `fe_onnx_cli` with missing `GLIBCXX_3.4.31`/`3.4.32` before this was applied.
- Prove compile with MLPerf Tiny `ad01_int8.tflite` **before** `smoke.onnx`.
- ONNX and PyTorch frontends are documented as **quantizer-flow only**.
- NPU compile: `python mcu_compile.py model.onnx out/ --npu --quantize --calib-data calib.npy`
- `--npu` requires INT8. `--ref-data` writes reference npy for on-target checks.
- Sigmoid is A8 on MCU_ETHOS and F32 on MCU_CPU in the quantizer table — prefer `--npu`.

## Local path (this Mac)

Emulate x86_64 Ubuntu:

```bash
docker build --platform linux/amd64 -t spectrasynq-ruhmi:2.6.0 deployment/ra8p1
./deployment/ra8p1/compile.sh artifacts/export/semantic_v0_fp32.onnx artifacts/ruhmi
```

QEMU emulation is acceptable for compilation. It is not a latency measurement.

## CI path

`.github/workflows/ruhmi-compile.yml` runs on `ubuntu-22.04` (native x86).
That is the preferred compile host once the repo is on GitHub.

## What to inspect after a successful compile

| Artifact | Why |
| --- | --- |
| `build/MCU/compilation/src/*.c` | generated C99 |
| `build/MCU/model_subgraphs.json` | NPU vs CPU partition (mera_visualizer) |
| `scripts/utils/check_model_metrics.py` output | RAM / Flash / MACs **as reported by the compiler**, still PRE-SILICON |
| logs mentioning fallback / unsupported ops | architecture change trigger |

If coverage is poor, **change the CNN** before chasing desktop F1.

## What this is not

Host `onnxruntime` INT8 ≠ MERA INT8 ≠ U55 INT8. Three numbers, three receipts.
