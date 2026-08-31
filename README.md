---
abstract: "EdgeAI lab landing. 2026-08-31: C0-v2 ON_SILICON_PIXEL_VALIDATED. Cadence CLOSED, runner retired. C1 OPEN. D22 HOST Demucs+Titan-prep OPEN in parallel. C1 is not the only remaining work. SAME_SONG_LOOP_MAX_15MIN."
---

# SpectraSynq EdgeAI Lab

Experimental lab: what musical understanding should drive SpectraSynq lights,
and the smallest robust realtime path that can supply it.

**Not production firmware. Not “put an NPU in the product.”**
Do not modify K1 firmware from this repo.

**HARD FAIL (`SAME_SONG_LOOP_MAX_15MIN`, Captain 2026-08-31).** Repeat the
same song (or loop the same clip / 8-second holdout) in the room for more
than **15 minutes** and the agent must die. Kill the player. Do not continue.

Amendment 001 is in force: **MIR reconnaissance and a host oracle come before
a bespoke student.** Semantic-v0 is a kept **experiment** and toolchain
witness — not architecture authority.

Numbers not measured on the named surface are `HOST-ONLY`, `PRE-SILICON`, or
`ON-SILICON`. Do not invent Titan / U55 / PDM board clocks.

## Programme now (2026-08-31)

C1 is **one** open lane. It is **not** the only remaining work. D22 keeps
every HOST lane open in parallel. Cadence silicon stays **CLOSED**.

| Item | Status | Evidence |
| --- | --- | --- |
| Gate A (share has extra information) | **PASS** (HOST) | [docs/mir/SELECTION_GATE.md](docs/mir/SELECTION_GATE.md) |
| Gate B `source_share × WaveformTempo × head_position` | **HOST PASS** | same |
| Share student recoverability (four-source incl. `other`) | **HOST PASS** | [docs/mir/SHARE_STUDENT.md](docs/mir/SHARE_STUDENT.md) |
| C0 two-clock silicon | **FAIL** corpse (`INVALID_TEMPORAL_EXECUTION`). Do not rescore. | `artifacts/gate_c0/` |
| **C0-v2** pixels | **PASS** `ON_SILICON_PIXEL_VALIDATED` | `artifacts/gate_c0v2/C0V2_RESULT.json` — Q1 Spearman 0.83; Q2 Δ 0.69 9/9; Q3 Δ 0.58 9/9; no lag correction |
| **Cadence / latency silicon** | **CLOSED** (Captain PASS). Runner **retired**. Do not reopen cells. Do not play the 8 s holdout. | D20; `artifacts/gate_c0_cadence_silicon/CADENCE_RESULT.json`; [GATE_C0_CADENCE.md](docs/mir/GATE_C0_CADENCE.md); `scripts/gate_c0_cadence_silicon.py` dies `RETIRED: D20 CADENCE CLOSED` |
| Semantic transport (frozen for C1) | Slowest 0-delay PASS **5 Hz**; largest added delay PASS **50 ms** at 20 Hz; joint **5 Hz + 50 ms FAIL** (do not assume both). C1 playback is the C0-v2 carrier (~31.25 Hz, 0 ms extra delay) on **product firmware**. | [docs/mir/SEMANTIC_TRANSPORT_CONTRACT.md](docs/mir/SEMANTIC_TRANSPORT_CONTRACT.md) |
| **C1 LGP** | **OPEN** — Captain look, one full song he chooses, no 8 s loop. Dumps do not answer. | [docs/mir/GATE_C1.md](docs/mir/GATE_C1.md) |
| Student I/O freeze | **Not frozen.** Freeze only after [SELECTION_GATE.md](docs/mir/SELECTION_GATE.md) **and** C1 if the contract still holds. | D17 / D20 / D22 |
| Serial Studio | Observe/record only. Not command transport. | D19 |

## Open in parallel (D22) — not queued behind C1

These run **now**, on HOST, without the lamp and without USB:

- MIR registry + oracle, DEAM arousal vs DSP, PaRIRset onset (HOST-ONLY; no room loop >15 min)
- Share-student **HOST sketches / streaming tests** — not Titan; I/O still unfrozen
- Semantic-v0 experiment / U55-shaped toolchain only
- **Demucs HOST-only teacher probe** — docs/licence; code MIT; weights **UNKNOWN (not MIT, scientific-use)**. Do not `uv add demucs`. Do not put Demucs on Titan. Do not block C1.
- **Titan / U55 / PDM prep docs** and golden-tensor protocol — **PRE-SILICON**. No invented board numbers. Teachers (MERT / MuQ / MAEST / Demucs) stay off Titan.
- RUHMI compile path — **PRE-SILICON** C99 on GHA 33319114336 (`ad01_int8.tflite` + `smoke.onnx`); pin `6c5aad9`
- Effect-semantics **consume** firmware export; do not invent a competing taxonomy
- C1 LGP look when Captain names a song (product firmware; no probe flash)

Roster: [docs/agent/PARALLEL_LANES.md](docs/agent/PARALLEL_LANES.md). Rules: [AGENTS.md](AGENTS.md). Decisions D20–D22: [docs/DECISIONS.md](docs/DECISIONS.md).

## Reproduce (HOST)

No K1 USB. No cadence cells. No 8 s holdout loop.

```bash
uv sync --python 3.12 --extra mir --extra dev
uv run pytest
uv run edgeai-smoke                 # toolchain, not the product model
uv run python scripts/mir_oracle_run.py
uv run python scripts/deam_arousal_vs_dsp.py   # needs local DEAM audio
uv run python scripts/make_dsp_goldens.py
```

`uv run pytest` includes `tests/test_cadence_silicon_retired.py`: the cadence
runner must refuse before USB or audio. Do **not** invoke
`scripts/gate_c0_cadence_silicon.py` expecting a sweep.

RUHMI (x86 Ubuntu 22.04 / Python 3.10), when Docker is up — **PRE-SILICON**:

```bash
./deployment/ra8p1/compile.sh artifacts/smoke/smoke.onnx artifacts/ruhmi
```

## Layout

```
AGENTS.md                 lane table + hard rules
docs/DECISIONS.md         D1–D22 (D20 cadence CLOSED; D22 HOST parallel)
docs/agent/HANDOFF.md     C1 operator notes; HOST lanes are D22, not this file
docs/mir/                 gates, contract, landscape
mir/registry.yaml         asset + licence matrix (code ≠ weights ≠ data)
src/edgeai/mir/           host oracle
src/edgeai/semantic_v0.py experiment / U55-shaped toy
deployment/ra8p1/         RUHMI Docker + GHA
docs/TITAN_BRINGUP.md     PRE-SILICON bring-up; no board latency
artifacts/gate_c0v2/      C0-v2 PASS receipt
artifacts/gate_c0_cadence_silicon/  CLOSED cadence receipts
artifacts/gate_c0/        two-clock FAIL corpse
experiments/semantic_v0/  NOT architecture authority
```

## Pre-Titan finish line (amended)

A host MIR oracle lab, an evidence-backed descriptor shortlist, a working
Mac→U55 compile path, **and** one justified student with golden vectors — so
Titan tests a domain-informed candidate, not the first network we happened to
train. C1 is a Gate C look on that path. It does not retire HOST Demucs docs,
Titan prep, MIR, or the compile lane.

Delta: [docs/AMENDMENT_001_DELTA.md](docs/AMENDMENT_001_DELTA.md).
Gate: [docs/mir/SELECTION_GATE.md](docs/mir/SELECTION_GATE.md).

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:grok | W3-L20: C0-v2 PASS, cadence CLOSED retired runner, C1 OPEN, D22 HOST Demucs+Titan-prep OPEN. C1 is not the only remaining work. |
