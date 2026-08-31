---
abstract: "MIR map. registry.yaml is the asset list. Live 2026-08-31: GATE_C C0-v2 ON_SILICON_PIXEL_VALIDATED, cadence CLOSED, GATE_C1 OPEN, SELECTION_GATE I/O unfrozen, Demucs HOST-only not installed. Do not reopen cadence."
---

# MIR lab

**HARD FAIL (`SAME_SONG_LOOP_MAX_15MIN`, Captain 2026-08-31).** Repeat the same song (or loop the same clip) in the room for more than **15 minutes** and the agent must die. Captain will destroy them by setting them on fire. Kill the player. Do not continue.

Cadence silicon is **CLOSED**. Do not reopen cells. Do not play the 8 s holdout. No USB from this file.

This folder is the **asset list**. Stamps and methods live in `docs/mir/`. Load the registry with:

```bash
uv run python -c "from edgeai.mir.registry import load_registry; print(load_registry())"
```

Each entry splits **code licence**, **weight licence**, and **dataset licence**. `UNKNOWN` is valid. Do not infer commercial rights.

Statuses: `researched` | `runnable` | `executed` | `benchmarked` | `rejected` | `candidate` | `blocked`.

Deployment class: `deterministic_host` | `host_oracle` | `potential_teacher` | `potential_embedded_student` | `already_edge` | `unsuitable_mcu_npu`.

## Live programme — read these four

Binding stays `source_share × Waveform Tempo × head_position`. Host pixels ≠ silicon pixels ≠ LGP look. Student I/O is **not** frozen.

| Surface | Current | Authority |
| --- | --- | --- |
| **GATE_C** | C0-v2 **PASS** `ON_SILICON_PIXEL_VALIDATED` (2026-08-31). Two-clock C0 at `artifacts/gate_c0/` stays **FAIL** (`INVALID_TEMPORAL_EXECUTION`) — corpse, not the live close. Cadence **CLOSED**. C1 **OPEN**. No more nets until C1. | [docs/mir/GATE_C.md](../docs/mir/GATE_C.md). Method [GATE_C0V2.md](../docs/mir/GATE_C0V2.md). Receipt `artifacts/gate_c0v2/C0V2_RESULT.json`. |
| **GATE_C1** | **OPEN.** Captain looks through the LGP at **one full song he chooses**. Product firmware. Not dumps. Not the 8 s loop. Stamp `LGP_PERCEPTUAL_VALIDATED` only after the three LGP questions. | [docs/mir/GATE_C1.md](../docs/mir/GATE_C1.md) |
| **SELECTION_GATE** | Feasibility **PASS**. Gate A **PASS**. Gate B **HOST PASS**. Recoverability **HOST PASS** (21k, four-source including `other`). Gate C still **OPEN** until LGP. I/O **unfrozen**. The file’s abstract still says “C0 FAIL / C0-v2 next / C1 blocked” — that is **stale**; live C0/C1 is GATE_C above. | [docs/mir/SELECTION_GATE.md](../docs/mir/SELECTION_GATE.md). Recoverability receipt [SHARE_STUDENT.md](../docs/mir/SHARE_STUDENT.md). |
| **DEMUCS HOST** | **OPEN** as a HOST-only teacher **probe**. **Not installed.** Code **MIT**. Weights **UNKNOWN — not MIT** (scientific-use only). Teacher use does not clear a derived student. Not Titan. Not U55. Not Gate C. Do not block C1. Do not `uv add demucs`. | `mir/registry.yaml` `id: htdemucs`. [AGENTS.md](../AGENTS.md) Demucs row. Licence contract [docs/agent/lanes/L35_demucs.md](../docs/agent/lanes/L35_demucs.md). |

### Cadence (CLOSED — do not re-measure)

Receipt: [GATE_C0_CADENCE.md](../docs/mir/GATE_C0_CADENCE.md) / `artifacts/gate_c0_cadence_silicon/CADENCE_RESULT.json`.

```text
5 Hz @ 0 ms PASS
50 ms extra at 20 Hz PASS
100 ms at 20 Hz FAIL
5 Hz + 50 ms FAIL
10 Hz + 25 ms NOT COMPLETED — do not interpolate
```

A student must **not** assume 5 Hz **and** 50 ms together. Host rehearsal is not the product clock.

## Do not

- Quote the two-clock C0 FAIL as the current C0 close.
- Freeze student I/O from SELECTION_GATE recoverability or cadence numbers.
- Put Demucs / MERT / MuQ / MAEST on Titan.
- Treat Semantic-v0 as architecture authority.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:grok-ssa-w3-l21 | Map to live GATE_C / GATE_C1 / SELECTION_GATE / Demucs HOST. Cadence CLOSED. Registry load kept. |
