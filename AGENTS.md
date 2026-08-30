# SpectraSynq-EdgeAI-Lab — agent rules

This repository is the authority for the Edge-AI research programme.
Do **not** modify production K1 firmware from here.

Governing briefs: original Agent Operating Brief **plus** Amendment 001.
Amendment 001 wins on research sequence and model-selection authority.

## Purpose

Determine **what machine-extracted musical understanding improves the lights**,
then implement the **smallest robust realtime path** that supplies it.

That path may be DSP, conventional MIR, a distilled student, or several lanes.
It is **not** “put an NPU in SpectraSynq”.

## Hard rules

- Shortest load-bearing path. No MLOps cathedral.
- Do not invent hardware numbers. Label `HOST-ONLY` / `PRE-SILICON` / `ON-SILICON`.
- Split **by song**, never by window, if/when we train.
- Code licence ≠ weight licence ≠ dataset licence. `UNKNOWN` is allowed.
- Teacher use does not clear derived student weights.
- Semantic-v0 is an **experiment**, not architecture authority.
- Do not freeze student I/O until `docs/mir/SELECTION_GATE.md` is satisfied.
- Do not invent BUILDING/DROPPING/… labels before inspecting existing ontologies.
- Do not put MERT/MuQ/MAEST/Demucs on Titan.
- Export CNN not STFT when we do embed a student. Golden tensors first, PDM last.
- Do not commit corpora or checkpoints unless asked.

## Lanes

| Lane | Status |
| --- | --- |
| Host toolchain | keep |
| RUHMI/U55 compile | ad01_int8.tflite compiled (toolchain). smoke.onnx C99 failed on ReduceMean split; pool swapped |
| MIR registry + oracle | primary |
| DEAM arousal vs DSP | primary (real audio) |
| RUHMI CI | pin 6c5aad9 + libstdc++/gcc-13; ad01 then smoke |
| Live domain (PaRIRset) | Amendment 002 — not frozen |
| Semantic-v0 training | **deferred** |
| Silicon / PDM | wait for Titan |

## Pre-Titan target (amended)

Host MIR oracle lab + evidence-backed descriptor shortlist + Mac→RA8P1 pipeline
+ **one justified** student compiled for U55 with golden vectors — not the first
network we happened to train.
