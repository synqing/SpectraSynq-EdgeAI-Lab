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

- **HARD FAIL (Captain 2026-08-31, `SAME_SONG_LOOP_MAX_15MIN`).** If any agent repeats the same song — including looping the same clip or 8-second holdout — in the room for more than **15 minutes**, that agent must die. Captain will destroy them by setting them on fire. Kill the player immediately. Do not continue.
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
- An authoritative silicon test that needs interactive command/reply owns that K1 serial port exclusively. Serial Studio must release it first. Do not multiplex two owners on one USB-CDC.

## Lanes

**D22:** all HOST lanes **OPEN for parallel SSA**. Cadence silicon stays CLOSED. No 8 s loop. No USB multiplex. One writer per file. Roster: `docs/agent/PARALLEL_LANES.md`.

| Lane | Status |
| --- | --- |
| Host toolchain | OPEN / parallel |
| RUHMI/U55 compile | OPEN / parallel (PRE-SILICON C99: ad01 + smoke on GHA 33319114336) |
| MIR registry + oracle | OPEN / parallel |
| DEAM arousal vs DSP | OPEN / parallel (real audio, no room loop >15 min) |
| RUHMI CI | OPEN / parallel (pin 6c5aad9 + libstdc++/gcc-13) |
| Live domain (PaRIRset) | OPEN / parallel (onset delayed ~100 ms, not killed) |
| Source oracle (MUSDB18) | OPEN / parallel. A PASS. B HOST PASS. C0-v2 ON_SILICON_PIXEL_VALIDATED. Cadence CLOSED. C1 OPEN |
| Source ownership | OPEN / parallel. PRE-PRODUCT FEASIBILITY PASS. Two-clock C0 corpse stays FAIL |
| Share student | OPEN / parallel. HOST recoverability PASS. I/O unfrozen. Streaming **unblocked for HOST sketches/tests**, not Titan |
| Effect semantics | OPEN / parallel (consume firmware export; no competing taxonomy) |
| Semantic-v0 | OPEN as experiment/toolchain only, not architecture authority |
| Demucs | OPEN HOST-only teacher probe (do not put on Titan; do not block C1) |
| C1 LGP | OPEN — Captain look, one full song he chooses, no 8 s loop |
| Serial Studio | observe/record only |
| Cadence silicon | **CLOSED** — do not reopen |
| Silicon / PDM / Titan | OPEN for prep docs; no invented board numbers |

## Pre-Titan target (amended)

Host MIR oracle lab + evidence-backed descriptor shortlist + Mac→RA8P1 pipeline
+ **one justified** student compiled for U55 with golden vectors — not the first
network we happened to train.
