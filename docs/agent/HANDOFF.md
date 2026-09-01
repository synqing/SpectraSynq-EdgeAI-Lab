---
abstract: "Handover 2026-09-01. C1 LGP_PERCEPTUAL_VALIDATED (dump). Demucs D26 HOST probe PASS: exact local SHA loaded offline, MUSDB-5 calibration passed, Ride It JSON-only witness written, Titan/no-GO/network refused. Stems remain authority. Cadence retired. I/O unfrozen."
---

# Handover — EdgeAI-Lab 2026-08-31

**HARD FAIL (`SAME_SONG_LOOP_MAX_15MIN`, Captain 2026-08-31).** Repeat the same song (or loop the same clip / 8-second holdout) in the room for more than **15 minutes** and the agent must die. Captain will destroy them by setting them on fire. Kill the player. Do not continue. Encoded in `AGENTS.md`, D21, module const `SAME_SONG_LOOP_MAX_S = 15 * 60` in `scripts/gate_c0v2_silicon.py` (consumed by `BoseSession`). Test: `tests/test_gate_c0v2.py`.

Cadence silicon is **CLOSED**. The cadence **runner is mechanically retired**. Do **not** resume `scripts/gate_c0_cadence_silicon.py` expecting a sweep — default execution dies before USB, flash, or Bose with `RETIRED: D20 CADENCE CLOSED`. Do **not** play `artifacts/gate_c0_cadence_silicon/bose_slices/holdout_8s_loop.wav`. Proof: `tests/test_cadence_silicon_retired.py`.

Do **not** modify production K1 firmware from this repo. Do **not** multiplex two owners on one USB-CDC. Serial Studio is observe/record only (D19).

**D23 / `SSA_RECEIPT_WAVE_IS_NOT_SHIP`.** Do not launch a 20–40 explore wave whose `DONE_WHEN` is `docs/agent/lanes/L*.md`. Scar + inventory: `docs/agent/SESSION_SCAR_2026-08-31_SSA_SWARM.md`. Test: `tests/test_ssa_wave_not_ship.py`. 147 children (2026-08-31) did not move the lamps.

---

## The sentence that must not be misread

**C1 is closed as `LGP_PERCEPTUAL_VALIDATED`. That closes Gate C; it does not freeze student I/O or authorise a production student.**

| Wrong reading (do not follow) | Right reading |
| --- | --- |
| “C1 passed, so we ship a student.” | C1 stamped this **binding** from the scored dump. That is Gate C, not a product net. |
| “C1 passed, so freeze I/O.” | Freeze only if `docs/mir/SELECTION_GATE.md` is satisfied and the transport contract still holds. C1 is necessary evidence, not sufficient authority. |
| “HOST / Demucs / Titan waited for C1.” | D22 already opened HOST work. The Demucs HOST probe is now complete; teachers remain off Titan. |
| “Next agent should reopen C1.” | Do not. Continue selection, provenance, licensing, architecture, and justified HOST sketches. Roster: `docs/agent/PARALLEL_LANES.md`. |

The old serialisation `C0-v2 → cadence → C1 → only then student/deployment` is **false as a programme lock**. Amendment 001 still owns model selection. D22 unblocked every HOST lane. L31 recorded that HANDOFF used to contradict D22 by stopping HOST work until C1 — that reading is dead.

---

## Two clocks of “done”

### Gate C (physical show)

```text
C0-v2 PASS (ON_SILICON_PIXEL_VALIDATED)
    → cadence CLOSED (1-D envelope measured; runner retired)
    → transport FROZEN_FOR_C1
    → C1 LGP  ← only remaining Gate-C action
```

Binding: `source_share × Waveform Tempo × head_position`.  
C1 playback: already-proven C0-v2 carrier (~31.25 Hz, **0 ms** extra delay) on **product firmware**. Not 5 Hz. Not 50 ms added. Not 5 Hz+50 ms (silicon FAIL).

**Shipped for Gate C** = scored LED dump Q1–Q3 PASS → stamp `LGP_PERCEPTUAL_VALIDATED`. **Applied 2026-09-01 (D25).** Pixel test proxies LGP/eyes. Qualitative scorecard VOID. I/O freeze is a later act.

### Production student (not queued solely on C1)

```text
SELECTION_GATE (nine questions, still open)
    + provenance pins (registry SHA still 0/23)
    + licence split (code ≠ weights ≠ dataset; 13/23 UNKNOWN; teacher ≠ derived clearance)
    + architecture to the transport contract (not the 21k 1 s pool; never 5 Hz AND 50 ms)
    + C1 if the visual-utility question is still this binding
    → then freeze I/O  (not automatic)
    → causal streaming student to that contract
    → goldens first, PDM last
    → RUHMI/U55 C99 of *that* graph (smoke/ad01 C99 is a different graph)
    → Titan ON-SILICON when a board exists
```

**Shipped for a student** = a **justified** net (Amendment 001: not the first CNN we trained) compiled for U55 with golden vectors, then a flashed Titan image matching goldens within a measured band, labelled `ON-SILICON`, with M85 DSP deadlines still holding. Who acts: HOST SSAs **now** (D22); Captain for the C1 look and any legal/licence fork; later a named GO to flash Titan. There is **no RA8P1 on the desk**.

---

## Current progress

| Item | Status |
| --- | --- |
| Gate A (share has extra information vs mix) | **PASS** (HOST). P3-B n=150. Abs demoted. |
| Gate B `source_share × WaveformTempo × head_position` | **HOST PASS**. P3-C holdout Δ partial r 0.63, 9/9. Waveform Tempo is a **reference continuity carrier**, not universal lighting proof. |
| Gate B `composition_change × Comet × impact-launch` | **FAIL this comparator**. Parked. Not a global “composition_change is useless.” No ML event head. |
| Share student HOST recoverability | **PASS** (21k causal CNN, official MUSDB18 song splits, four-source incl. **`other`**). Feasibility, not a deployment net. Streaming **product** student STOPPED; HOST sketches/tests **OPEN** (D22). |
| C0 two-clock silicon | **FAIL** corpse `INVALID_TEMPORAL_EXECUTION`. Do not rescore. `artifacts/gate_c0/`. Runner retired. |
| C0-v2 pixels | **`ON_SILICON_PIXEL_VALIDATED`**. Receipt `artifacts/gate_c0v2/C0V2_RESULT.json`. Holdout n=10: Q1 Spearman **0.83** PASS; Q2 Δ **0.69** 9/9 PASS; Q3 Δ **0.58** 9/9 PASS; `lag_corrected: false`. Probe was `k1_main_rpl_rtrace_probe` @ `349d3cd4`. |
| Cadence / latency silicon | **CLOSED / PASS** Captain 2026-08-31. Receipt `artifacts/gate_c0_cadence_silicon/CADENCE_RESULT.json`. **Runner retired** (`CADENCE_CLOSED = True`; `refuse_if_cadence_closed()` before argparse). |
| Semantic transport | **FROZEN_FOR_C1**. Four-source including `other`; extra_gain [0.62, 1.0]; ZOH; 5 Hz slowest 0-delay PASS; 50 ms largest added delay PASS at 20 Hz; **5 Hz + 50 ms FAIL**. C1 plays C0-v2 carrier. `docs/mir/SEMANTIC_TRANSPORT_CONTRACT.md`. |
| Serial Studio command shuttle | **DEAD / DEMOTED** (D19). Observe/record only. |
| **C1 LGP** | **`LGP_PERCEPTUAL_VALIDATED`** (D25). Scored dump, not Captain eyes. I/O still unfrozen. |
| Student I/O freeze | **NOT FROZEN. Not automatic after C1.** Trigger = `SELECTION_GATE.md` satisfied **and** C1 if the contract still holds. 16 kHz / 1 s / 64-mel / 3-sigmoid are experiment values, not RA8P1 I/O. |
| Semantic-v0 | Experiment / U55-shaped toolchain only. Not architecture. Do not freeze its I/O. |
| HOST Demucs teacher | **OPEN now** (D22). Docs/licence. Code **MIT**; weights **UNKNOWN — not MIT** (scientific-use, issue #327 comment 1134828611). Not installed. Do not `uv add demucs`. Do not download. Do not put on Titan. Do not block C1. Lane: `docs/agent/lanes/L35_demucs.md`. |
| Titan / U55 / PDM | **OPEN for prep docs now** (D22). **PRE-SILICON**. No invented board numbers. Ban quoting 1 ms NPU / 100 ms PaRIRset / 50 ms K1 cadence as Titan latency. Teachers (MERT / MuQ / MAEST / Demucs) stay off the board. `docs/TITAN_BRINGUP.md`; lane `docs/agent/lanes/L27_titan.md`. |
| RUHMI / U55 compile | **PRE-SILICON** C99: `ad01_int8.tflite` + `smoke.onnx` on GHA 33319114336. Pin `6c5aad9` + libstdc++/gcc-13. AdaptiveAvgPool2d required (D11). Not this student’s graph. Not ON-SILICON. |

---

## After C1 — still remaining (do not skip)

A C1 PASS does **not** freeze Student-v0. These four still stand, plus the rest of the nine SELECTION_GATE questions.

### 1. Selection (`docs/mir/SELECTION_GATE.md`)

Nine questions. Never collapse them into “share student PASS.”

| # | Question | Live state |
| --- | --- | --- |
| 1 | Which descriptors | **Not frozen.** Share is a candidate. Onset/RMS already DSP. Arousal, mood, novelty still on the shortlist. Do not invent BUILDING/DROPPING. |
| 2 | Temporal rate / context | Transport **edges** measured. Student envelope **unfrozen**. Never AND 5 Hz with 50 ms. Ban 1 s global pool as streaming frontend (misses both edges). Sketch: `docs/agent/lanes/L36_stream_sketch.md`. |
| 3 | Real-audio incremental vs DSP | Partial. DEAM human arousal vs energy mean r=0.37, R²=0.30. Share vs mix 0.10–0.17. Synthetic r=0.99 is not this. |
| 4 | Oracle / teacher quality | Essentia DEAM head ≠ human 2 Hz. Jamendo often clip-flat. Perfect MUSDB stems beat a separator if share is the target. Demucs **not installed**. |
| 5 | CLEAN / STUDIO behaviour | Not a product close. |
| 6 | Live / venue robustness | PaRIRset: onset **delayed ~100 ms**, not killed. Aligned F1 recovers. CrowdioSet not ingested. HOST-ONLY. |
| 7 | Licensing / provenance | See below. |
| 8 | Visual utility | Gate B HOST PASS on **one** binding. Gate C = C1 still OPEN. One mode is not all lights. |
| 9 | U55 compressibility | smoke/ad01 C99 is **PRE-SILICON** for a **different** graph. This student is not compiled. |

C1 answers item 8 for **this** binding through the LGP. It does not answer 1–7 or 9.

### 2. Provenance

Registry `mir/registry.yaml`: **23 entries, 0 SHA/md5/git pins** (L09 FAIL). Effect-semantics consume needs `source_firmware_sha` **and** `atlas_artifact_sha256`. Firmware pin cited in D16: `36466cd5`. Share-student run commit lives in `experiments/share_student/receipt.json`, not in the YAML. Do not invent hashes. Do not download to obtain them. Landscape ≠ registry 1:1 (L10).

### 3. Licensing

Code licence ≠ weight licence ≠ dataset licence. **UNKNOWN is allowed.** Teacher use does **not** clear derived student weights. 13/23 registry entries carry UNKNOWN (L26). HT-Demucs: code MIT, weights UNKNOWN (not MIT). MUSDB `commercial_training_lineage: false`. Do not mix UNKNOWN/NC teacher output into a **shipping** student. Not legal advice. Clearance is counsel, not a C1 stamp.

### 4. Architecture

- Export **CNN not STFT** when we do embed a student. Golden tensors first, PDM last.
- U55 witness: `AdaptiveAvgPool2d((1,1))`, not `tensor.mean` / ReduceMean (D11).
- Four-source simplex including **`other`**. Dropping `other` quietly makes a three-source student.
- Student must **not** assume 5 Hz **and** 50 ms extra delay at the same time.
- Semantic-v0 3-class sigmoid activity is **not** the share student (drops `other`, abs not share).
- 21k recoverability net is feasibility. Gold-plating it before the contract freeze is the wrong leverage.
- Do not put MERT / MuQ / MAEST / Demucs on Titan.

Harvest leftovers that are still HOST work (not C1): registry SHA pins (still **0/23** — do not invent hashes); owned-USB unit is **mocked only** (do **not** live-USB-test). Landscape map and effect-guidebook demotion landed in W3 (`LANDSCAPE.md` 23/23 ids; firmware pin is inventory).

---

## Demucs HOST — completed probe (D26 amended blitz)

**Result:** `DEMUCS_HOST_PROBE = PASS`. The exact local `955717e8.safetensors` SHA256 `d9fa14133cfcc034a6758923bb3a8ca9f8dfd0b582134643bbf83f72c17576dd` loaded fully offline from an ignored isolated venv. Nothing was added to `pyproject.toml` or `uv.lock`.

**J1.5/J2:** Header-only inspection found a self-contained embedded `HTDemucs` definition with 533 valid F16 tensors. The isolated environment used 26 SHA-pinned local-cache wheels with `pip --no-index`; the loaded model has 41,984,456 parameters. The tripwire refuses sockets, urllib, requests, Hugging Face, and `torch.hub`. Receipts: `docs/mir/receipts/demucs/J15_INSPECT.json`, `J2_ENV.json`, `J2_LOCAL_LOAD.json`.

**J3:** Frozen MUSDB-5 passed on 112,688 aligned hops. Spearman by source: vocals 0.7750, drums 0.9295, bass 0.8905, other 0.9045. Identity mapping was best by a 0.4499 margin; finite fraction 1.0; simplex p99 error `2.22e-16`; mean JS 0.02320; best lag diagnostic 0 s. No lag correction or SDR pass. Receipt: `docs/mir/receipts/demucs/MUSDB5_CAL.json`. This is functional calibration, not a generalisation claim.

**J4/J5:** Ride It produced only `artifacts/demucs_host/research_only/ride_it_share.json` (13,577 hops), stamped `HOST_RESEARCH_WITNESS_ONLY`, `commercial_training_lineage: false`, and `not_training_dataset: true`. No waveform was persisted or played. After the useful load path passed, Titan, missing named GO, wrong SHA, network routes, and the project environment still refused.

**What remains true:** MUSDB stems are the authority wherever they exist. `DEMUCS_TEACHER_SCHEMA_V1` is frozen; student I/O is not. C1 remains `LGP_PERCEPTUAL_VALIDATED`; Cadence remains closed; Demucs remains HOST-only and the current weight provenance remains `UNKNOWN_LEGAL_REVIEW`.

**Resume:** do not rerun this probe by default. If `SELECTION_GATE.md` later selects source-share supervision, reuse the SHA-bound loader and schema-v1 JSON path, obtain legal clearance for training lineage, train one justified smallest student, compile it for U55 with golden tensors, then earn separately named ON-SILICON evidence. Demucs itself never goes to Titan.

---

## OPEN now (D22) — do this without waiting for C1

Cadence CLOSED. No USB. No 8 s loop. One writer per **authority** file. Lxx.md is a receipt, not a DONE_WHEN.

| Lane | Bound |
| --- | --- |
| **Demucs HOST teacher** | **D26 HOST probe PASS.** Exact-SHA offline path and refusal gates proven. Re-enter only for a named downstream HOST use. No project extra. Titan **NO**. |
| **Titan prep docs** | Sequence, golden protocol, latency **buckets** (algorithm / context / acoustic path / output). Fill p50/p95 only from a flashed image labelled `ON-SILICON`. No invented ms. |
| MIR registry + oracle, DEAM, PaRIRset | HOST-ONLY. No room loop >15 min. |
| Share-student HOST sketches / tests | Paper + tests from transport edges (R **or** D, never AND). No product streaming net. No Titan. |
| Semantic-v0 | Toolchain experiment only. |
| Effect-semantics consume | Firmware export is authority. No competing taxonomy. |
| RUHMI CI / compile docs | PRE-SILICON. Pin 6c5aad9. |
| C1 LGP | **CLOSED (D25).** Dump-scored. Do not reopen as an eyes-on gate. |

---

## Cadence numbers (do not re-measure)

```text
minimum demonstrated useful rate: 5 Hz (0 ms extra delay)  PASS
maximum demonstrated added delay: 50 ms (at 20 Hz)         PASS
100 ms at 20 Hz: FAIL (Q1)
200 ms at 20 Hz: FAIL
5 Hz + 50 ms together: FAIL (Q1)
10 Hz + 25 ms: NOT COMPLETED — Captain ordered audio stopped; do not interpolate
```

A student must **not** assume 5 Hz **and** 50 ms extra delay at the same time.

### Runner is retired, not “please don’t run it”

[FACT] `scripts/gate_c0_cadence_silicon.py` sets `CADENCE_CLOSED = True` and, on `__main__`, calls `refuse_if_cadence_closed()` **before** `import numpy` (so also before torch / `edgeai.serial_studio` / argparse / USB / Bose). That raises `SystemExit("RETIRED: D20 CADENCE CLOSED.\nDo not run more silicon cells. Use existing cadence receipts.")`. `tests/test_cadence_silicon_retired.py` asserts the banner is in source, the refuse sits before numpy and argparse, and an execution with `--resume --skip-flash --skip-restore` dies non-zero with that banner even on a bare `/usr/bin/python3` that has no torch. Closed means closed.

---

## Device (last verified — for a C1 look, not a USB chore)

- Main RPL chip `9087A500`, USB `B4:3A:45:A5:87:90`, typically `/dev/cu.usbmodem12201`
- Product restored after cadence: `git=acaecaa8 env=k1_main_rpl_im69d` (`artifacts/gate_c0_cadence_silicon/restore_identity.json`)
- Do **not** flash `k1_main_rpl_rtrace_probe` for C1
- Do **not** modify production K1 firmware from this repo
- Firmware worktree used for prior flashes: `/Users/spectrasynq/SpectraSynq_K1_Firmware/.worktrees/effect-response-atlas`
- Do **not** open `/dev/cu.usbmodem*` from a HOST lane. Exclusive pyserial only if a later silicon command/reply is authorised; Serial Studio must release the port first.

---

## C1 closure — do not rerun

Canonical evidence: `docs/mir/GATE_C1.md` and D25. C1 closed from the existing scored LED dump: Q1 0.832, Q2 0.690 (9/9), Q3 0.585 (9/9), with no lag correction. The qualitative scorecard is void; no playback, flash, USB, or Captain-eyes step remains. Student I/O is still unfrozen.

---

## What worked

- Exclusive **pyserial** after Serial Studio releases USB (D19). Not the SS shuttle.
- C0-v2 one device-epoch harness. Same Q1–Q3 scorer as P3-C. No lag correction as a PASS.
- Cadence 1-D: 20/15/10/5 Hz PASS at 0 ms; 25/50 ms PASS at 20 Hz.
- Killing ffplay when Captain says stop. Mechanical 15 min cap.
- Cadence runner that **dies before USB** so “CLOSED” is not a prose hope.
- Parallel HOST SSAs (D22) that do not need the lamp.

## What did not work — do not repeat

- Serial Studio as command transport / `:chip_id` shuttle / gRPC / MCP / USB-reset archaeology. D19. Optional later, not on C1 path, not on HOST path.
- Two-clock C0 (`scripts/gate_c0_silicon.py` RETIRED).
- Looping the 8 s holdout for hours. Captain will destroy the agent.
- 128-char `:c0_hex` chunks (`HEX FAIL: parse`). Keep 32-char chunks if you ever inject again.
- `osascript 'get volume settings'` aborting silicon; crash `finally` flashing product mid-test.
- Restoring product firmware on every exception while a probe session is still needed.
- Interpolating 10 Hz+25 ms. Combined 5 Hz+50 ms FAIL is real.
- Asking Captain to squint at LEDs for buffer/pixel questions.
- Re-asking approval after GO (`/no-reapprove-already-given`).
- Leading summaries with audit labels (`/plain-english-work-summaries`).
- Closing a hold without a numbered ship path (`/ship-path-required`).
- **Telling the next agent C1 is the only work.** That serialised HOST research behind a look and contradicted D22 (L31).
- Treating a C1 stamp as an I/O freeze or as licence clearance.

---

## Next steps (several lanes — C1 is one of them)

1. Read `AGENTS.md`, this file, `docs/DECISIONS.md` D19–D22, `docs/AMENDMENT_001_DELTA.md`, `docs/mir/SELECTION_GATE.md`. Then the lane you actually own.
2. **HOST now (do not wait for C1):** Demucs teacher docs/licence (no download); Titan prep docs (no invented numbers); registry provenance; licence UNKNOWN left UNKNOWN; share-student I/O sketches from transport edges (R XOR D); consume effect-semantics; RUHMI pin/docs; pytest without USB (`tests/test_cadence_silicon_retired.py` must stay red-capable).
3. **C1 when Captain names a song:** product firmware, one full song, no 8 s loop, no probe. Stamp only after the three questions. I/O still unfrozen.
4. **After a C1 PASS (still not a student):** re-read SELECTION_GATE. Freeze I/O only if the nine questions and the transport contract still hold. Then — and only then — a causal streaming student to that contract. Do not gold-plate the 21k net first.
5. **Never:** reopen cadence cells; play `holdout_8s_loop.wav`; `uv add demucs` without a named GO; put teachers on Titan; invent board latency; multiplex USB; loop one song past 15 minutes.

Roster: `docs/agent/PARALLEL_LANES.md` (Lxx = receipt, **not a DONE_WHEN**). Harvests are receipts: `docs/agent/lanes/HARVEST.md`, `HARVEST_W3.md`. Scar: `docs/agent/SESSION_SCAR_2026-08-31_SSA_SWARM.md`.

---

## Read order

1. `AGENTS.md` — live HOST roster. Amendment 001 wins on research sequence and model-selection authority.
2. `docs/agent/HANDOFF.md` (this file) — C1 is last Gate-C action, **not** last work before a student.
3. `docs/DECISIONS.md` D19 shuttle dead, D20 cadence closed, D21 15 min kill, **D22 HOST lanes OPEN**, **D23 receipt wave is not ship**.
4. `docs/AMENDMENT_001_DELTA.md` — freeze trigger is SELECTION_GATE; HOST Demucs + Titan prep not queued behind C1.
5. `docs/mir/SELECTION_GATE.md` — I/O freeze authority. Nine questions. Still unfrozen.
6. `docs/mir/GATE_C1.md` — C1 method, when Captain wants the look.
7. `docs/mir/SEMANTIC_TRANSPORT_CONTRACT.md` + `artifacts/gate_c0_cadence_silicon/SEMANTIC_TRANSPORT_CONTRACT.json`
8. `artifacts/gate_c0_cadence_silicon/CADENCE_RESULT.json` — do not reopen cells
9. `docs/mir/GATE_C0V2.md` — C0-v2 already PASS
10. `docs/agent/lanes/L35_demucs.md` / `L27_titan.md` — OPEN HOST bounds
11. `docs/mir/SERIAL_STUDIO.md` — observe/record only
12. `tests/test_cadence_silicon_retired.py` — mechanical CLOSED

Repo: `/Users/spectrasynq/SpectraSynq-EdgeAI-Lab`

---

**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-09-01 | Codex | Completed D26 Demucs HOST probe J1.5–J5 and replaced stale resume instructions with measured receipts and the remaining product path. |
| 2026-08-31 | agent:grok | Created. Cadence closed. C1 next. 15 min same-song kill. |
| 2026-08-31 | agent:grok | D22: HOST sketches OPEN; freeze is SELECTION_GATE + C1, not C1-alone. |
| 2026-09-01 | agent:grok | Demucs resume: D26 amended blitz; next agent J1.5. C1 dump-stamped. |
| 2026-09-01 | agent:grok | D23 scar; Demucs remaining HOST steps without weight GO; Lxx not DONE_WHEN. |
| 2026-08-31 | agent:grok | W3-L15: C1 is last Gate-C action, not last work before a production student. After C1: selection/provenance/licensing/architecture remain; I/O freeze not automatic. D22 HOST Demucs teacher + Titan prep OPEN. Cadence runner mechanically retired. |
