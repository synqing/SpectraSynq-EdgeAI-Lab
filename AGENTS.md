# SpectraSynq-EdgeAI-Lab — agent rules

This repository is the authority for the Edge-AI research programme.
Do **not** modify production K1 firmware from here.

## Purpose

Answer, with evidence:

1. What musical information can a tiny learned model provide that DSP does not?
2. Can that model be quantized and mapped onto RA8P1 Ethos-U55?
3. Can it run beside realtime audio/visual work without wrecking timing?
4. Does it actually make the visual engine look more musically intelligent?

ML is additive. If it is missing, DSP still works.

## Hard rules

- Shortest load-bearing path. No MLOps cathedral.
- Do not invent hardware numbers. Label `HOST-ONLY` / `PRE-SILICON` / `ON-SILICON`.
- Split **by song**, never by window.
- Document dataset licence vs technical suitability separately.
- First architecture is a boring depthwise-separable CNN, ~100k–500k params.
- Test U55 mapping as soon as an architecture exists, not after it is “good”.
- Export the **CNN**, not the STFT. Mel stays on CPU. Golden tensors are log-mel.
- Record seed, commit, config, metrics, sizes on every real run.
- Do not commit corpora, checkpoints, or ONNX unless explicitly asked.

## Lanes

| Lane | Status |
| --- | --- |
| A — train Semantic-v0 on Mac | now |
| B — RUHMI/MERA compile on x86 | now (Docker / GHA) |
| C — silicon latency | wait for Titan |
| D — live PDM | after golden tensors pass on U55 |

## First milestone

Not “impressive F1”. It is:

Mac → PyTorch → quantized embedded model → RA8P1/U55 compilation, with one
audio-semantic baseline and golden vectors ready for silicon.
