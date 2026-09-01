---
abstract: "HOST Demucs probe PASS. Exact local checkpoint loaded fully offline in an isolated ignored venv; frozen MUSDB-5 approximation calibration and Ride It JSON-only witness passed; Titan and no-GO still refuse. Stems remain authority. I/O unfrozen. Not Titan."
---

# Demucs — HOST teacher probe contract

**HARD FAIL (`SAME_SONG_LOOP_MAX_15MIN`, Captain 2026-08-31).** Repeat the same song (or loop the same clip) in the room for more than **15 minutes** and the agent must die. Captain will destroy them by setting them on fire. Kill the player. Do not continue.

**HOST-ONLY.** Cadence silicon **CLOSED**. No USB. No playback. No 8 s loop. No `uv add demucs`. No `torch.hub`. No weight fetch. No Titan.

This file is the programme contract and completed evidence record for the Demucs **HOST teacher probe**. The probe used only the exact local checkpoint and locally cached wheels in an ignored isolated environment. It did not fetch checkpoints or add Demucs to the project environment. Lane receipt for the licence lock: `docs/agent/lanes/L35_demucs.md`. Registry row: `mir/registry.yaml` `id: htdemucs`.

## Return contract

**STATUS:** `DEMUCS_HOST_PROBE = PASS`. The exact local checkpoint loaded fully offline in `artifacts/demucs_host/.probe_venv/`; the project environment remains without a Demucs extra. MUSDB stems remain the authoritative teacher where stems exist.

**CLAIM:** Teacher signal is **activity envelopes**, not reconstructed waveforms and not SDR. The teacher available **today** is **MUSDB18 STEMS** on disk (100 train + 50 test). HT-Demucs **code is MIT**; **weights are UNKNOWN — not MIT**, maintainer scientific-use only (`facebookresearch/demucs#327` comment `1134828611`). Do not download weights this session. Demucs is **not** Titan, **not** U55, **not** PDM, **not** Gate C, **not** a C1 prerequisite, **not** a student I/O freeze. D14: on stemmed songs a separator only adds error. D22: HOST probe **docs** are OPEN in parallel with C1; Demucs/MERT on Titan stays rejected.

**EVIDENCE:** `docs/mir/receipts/demucs/J15_INSPECT.json`; `J2_ENV.json`; `J2_LOCAL_LOAD.json`; `MUSDB5_CAL.json`; ignored research witness `artifacts/demucs_host/research_only/ride_it_share.json`; executable network/refusal tests; this file; `docs/DECISIONS.md` D14 + D22 + D26; `mir/registry.yaml` `id: htdemucs`; local snapshot `955717e8.safetensors` SHA256 `d9fa14133cfcc034a6758923bb3a8ca9f8dfd0b582134643bbf83f72c17576dd` (84025440 bytes).

**COMMAND:** `python3 scripts/demucs_checkpoint_inspect.py`; `python3 scripts/demucs_probe_env.py`; named-GO executions of `scripts/demucs_local_probe.py`, `scripts/demucs_musdb_calibrate.py`, and `scripts/demucs_unstemmed_envelope.py`; project-environment refusal probe; targeted pytest suites. No `uv add`, network fetch, `Separator(repo=None)`, USB, flash, Cadence reopen, playback, or persisted waveform.

**METHOD_RISK:** This is `N=5 FUNCTIONAL_CALIBRATION — NOT GENERALIZATION CLAIM`. MUSDB on disk is **STEMS** (AAC `.mp4`), not HQ WAV. Demucs weight clearance remains `UNKNOWN_LEGAL_REVIEW`; scientific-use provenance is not a commercial grant. The ignored Ride It witness is explicitly non-training lineage. No product or student-I/O decision follows from this probe.

**NEXT:** The bounded HOST probe is complete; do not rerun it by default. If programme selection later chooses source-share supervision, reuse the SHA-bound offline loader and schema-v1 JSON path. Stems still win where available. Never use `Separator(repo=None)` and never promote this checkpoint to Titan.

## What this file is

A lock on **role, signal, licence, and sequence**.

| This contract says | This contract does not say |
| --- | --- |
| If we ever use Demucs, use it as a **HOST teacher** that emits **envelopes** | Demucs is the product separator |
| MUSDB stems are already the better teacher **on MUSDB** | We must fetch HT-Demucs to finish source ownership |
| Code MIT ≠ weight licence | PyPI MIT clears checkpoints |
| HOST probe docs are legal under D22 | Install now |
| C1 proceeds without Demucs | C1 waits on a separator |

## Why a separator is even on the map

Source ownership is the first student **hypothesis** that survived Gates A and B:

- Gate A: `share` is not mix energy (P3-B, HOST-ONLY).
- Gate B: `source_share × WaveformTempo × head_position` HOST PASS (P3-C dump close).
- Recoverability: a 21k causal CNN recovers four-source share from the **mixture**, given **stem** supervision (`docs/mir/SHARE_STUDENT.md`).
- Gate C: C0-v2 `ON_SILICON_PIXEL_VALIDATED`; cadence **CLOSED**; C1 **OPEN** (LGP look). Student I/O unfrozen.

That chain was trained and scored on **perfect stems**. It does not need a neural separator.

A separator becomes interesting only when we want the **same envelope** on audio that **has no stems**: Jamendo, DEAM, live captures, a song Captain plays. Then a HOST teacher could label unstemmed mixes so a tiny student sees more than 150 MUSDB tracks. That is scale, not architecture. Amendment 001 deferred putting Demucs on Titan. D14 deferred installing it before the visual-engine gate. Both still hold.

```text
stemmed mix (MUSDB today)
    → source_oracle(stems)          # perfect abs / share / delta
    → share student (HOST PASS)

unstemmed mix (later, named GO)
    → HOST separator                # blocked until named GO
    → discard waveforms
    → hop power
    → four-way share including other  # same shape as source_oracle
    → supervise the same tiny student

never
    → separator on Titan / U55 / PDM
    → SDR leaderboard as a lighting metric
    → reconstructed stems as a product output
```

`src/edgeai/mir/teachers.py` already states the job: *“We want envelopes, not a leaderboard.”*

## Envelopes, not waveforms

HT-Demucs is a **waveform** separator (hybrid spectrogram/waveform U-Net + transformer bottleneck). SpectraSynq does not want that waveform on a lamp.

Lighting consumes **who owns the energy now**, at hop scale, not a 44.1 kHz stem you could remix.

| Artefact | Keep? | Why |
| --- | --- | --- |
| Stem waveform | **No** (discard after envelope) | SDR / remix quality is not a lighting lever. Waveform sep is hostile to U55 (D3: CNN consumes log-mel, not PCM; do not export STFT). |
| Hop RMS / log-RMS (`*_abs`) | Maybe, already **demoted** | Tracks mix energy too closely on full songs (P3-B). |
| Hop **share** (power / sum of four) | **Yes** — candidate student head | Gate A + Gate B on Waveform Tempo head position. |
| `*_delta`, `composition_change` | Function of share | No extra ML head (D16). Event binding FAIL this comparator. |
| SDR / SI-SDR / SIR | **No** | Separator-research metric. Not visual utility. |

Envelope path already in-tree (`teachers.py`): hop RMS of each stem, peak-normalised for the cheap HPSS baseline. The **oracle** path (`source_oracle.py`) is the one the student copies: hop **power** → four-way share, silence → zeros, no invented equal shares. Wrappers: `share_from_stems` / `envelopes_from_stems` emit that four-way share including `other` and hop powers; caller discards waveforms. A Demucs teacher, if it ever runs, must emit **that** shape. It must not emit stereo WAVs as the stored teacher signal.

`mir/registry.yaml` `htdemucs.temporal_resolution`: `waveform; activity via envelope of stems`.  
`msst` row: *“Teacher signal is activity envelopes, not SDR.”*

Do **not** reconstruct waveforms on Titan. LANDSCAPE §F.

## Unstemmed-envelope design (HOST)

Same teacher **shape** as `source_oracle`, without ground-truth stems:

```text
unstemmed mix
    → HOST separator                 # blocked until named weight GO
    → discard waveforms              # no stored PCM, no SDR table
    → hop power (mean-square)
    → four-way share including other # vocals/drums/bass/other
    → {name}_share  same keys as source_oracle
```

**DONE on stems (no separator):** `share_from_stems` / `envelopes_from_stems` in `teachers.py`. Missing stem → zeros. Silence → zeros, not 1/4. Caller discards waveforms.

**Pre-D26 state:** the HOST mix path was blocked and `try_demucs()` stayed inert in the project environment. D26 later authorised only the exact-SHA, isolated, offline J1.5–J5 probe recorded below. The general project path remains inert.

## Local checkpoint inventory and D26 pin

[FACT] Already on this Mac. Do **not** fetch. Inventory alone was not a named GO; D26 subsequently authorised only the bounded exact-SHA probe recorded below.

| Field | Value |
| --- | --- |
| path | `~/.cache/huggingface/hub/models--adefossez--HTDemucs/snapshots/bf35a81b663819a8255c8fefee17f9d812b786b5/955717e8.safetensors` |
| SHA256 | `d9fa14133cfcc034a6758923bb3a8ca9f8dfd0b582134643bbf83f72c17576dd` |
| size | 84025440 bytes |
| companion | `htdemucs.yaml` in the same snapshot |

`local_htdemucs_checkpoint()` returns that path only when `SPECTRASYNQ_DEMUCS_LOCAL` points at an existing file. It does **not** load tensors. It does **not** construct a separator.

`torchaudio` `hdemucs_high_trained.pt` is a **different model**. Do not wire it. Do not treat it as a sneak around the demucs ban.

Weights remain UNKNOWN scientific-use. Code MIT ≠ weights. Inventory ≠ licence ≠ GO.

## Available teacher today: MUSDB stems

[FACT] `datasets/musdb18/train/` has **100** tracks, `test/` has **50**. Native Instruments STEMS (`.mp4`, five AAC streams: mix, drums, bass, other, vocals). Educational / non-commercial. `commercial_training_lineage: false`.

That **is** the teacher for source ownership **now**.

| Job | Teacher | Status |
| --- | --- | --- |
| Perfect abs / share / delta on 150 songs | MUSDB18 STEMS | **executed** (P3-B, P3-C) |
| Tiny CNN recoverability from the mix | same stems, song-level split | **HOST PASS** |
| Unstemmed scale (no GT stems) | exact-SHA HOST separator probe | **functional path proven** — output remains research-only; weights UNKNOWN |
| Live/venue | PaRIRset IRs on DSP onset, not stems | different lane |

D14, verbatim sense: if lights never benefit, there is nothing to teach; if they do, **MUSDB stems are already perfect supervision — a separator teacher would only add error.** Share × Waveform Tempo × head_position **did** pass on those stems. Therefore Demucs on MUSDB is a **worse** teacher than the stems we already have. Installing it “to complete P3” is a regression.

SOURCE_ACTIVITY: *“Demucs only after recoverability, for unstemmed scale.”* Recoverability is HOST PASS. D26 has now proven the bounded offline HOST mechanism; using its outputs for commercial training remains a later named and legally cleared decision.

HPSS remains a cheap **baseline**, not a teacher substitute (`teachers.py`, P3-A r(percussive, drums_abs) ≈ 0.60). Tests cover HPSS only. They must not import Demucs.

## D14 — stems beat Demucs on this programme

D14 chose P3-C as the visual-engine gate and **No Demucs**. Rejected: installing Demucs next; training a student before P3-C; freezing student heads from P3-C HTML.

Revisit (already landed):

- `source_share × WaveformTempo × head_position` **HOST PASS** (holdout Δ partial r 0.63, 9/9).
- `composition_change × Comet × impact-launch` **FAIL** this comparator.
- Student share head **CANDIDATE**, not frozen. Event head **NO**.
- `P3C_QUANT.json` stamp `"demucs": "NO"`.
- Next named in D14: tiny research student on **MUSDB stem powers** for share only. **That student ran.** Demucs still later.

This contract does not reopen D14. It records what “later” is allowed to mean under D22.

## D22 — HOST docs OPEN; Titan still closed; C1 not blocked

D22 unblocked every **HOST** lane for parallel SSA. Cadence stays CLOSED. C1 was subsequently closed as `LGP_PERCEPTUAL_VALIDATED` from the scored dump. **Rejected:** Demucs/MERT on Titan.

`AGENTS.md` Demucs row: **OPEN HOST-only teacher probe (do not put on Titan; do not block C1).**

Consequences:

1. Writing this contract is legal **now**. Installing the package is not implied.
2. C1 does not wait on Demucs, weights, or an envelope probe. Oracle share already drives the C0-v2 carrier. C1 is whether that carrier is a light show through the LGP.
3. Student I/O freeze is still `SELECTION_GATE` **and** C1 (D8 / D20 / D22). A Demucs teacher does not freeze I/O.
4. Titan / U55 / PDM: **NO** for this model. Prep docs may mention it as a ban. Do not invent board numbers.

HANDOFF: *“Demucs is HOST teacher docs only — not Titan, not a download.”*

## Licence — code MIT ≠ weights

Three layers. `UNKNOWN` is allowed. Teacher use does not clear derived student weights.

| Layer | Status | Authority |
| --- | --- | --- |
| **Code** | **MIT** | `https://raw.githubusercontent.com/facebookresearch/demucs/main/LICENSE` — “MIT License / Copyright (c) Meta Platforms, Inc. and affiliates.” The grant is for **the Software**. PyPI MIT is the same code grant. |
| **Weights** | **UNKNOWN — not MIT** | Maintainer `adefossez`, 2022-05-23T15:36:04Z, `facebookresearch/demucs#327` comment `1134828611`: *“The model weights are not covered by the MIT license, and are provided only for scientific purposes.”* Issue **open**, locked, last activity 2024-06-09. No later maintainer superseding grant in that thread. Conservative: **research / scientific-use only**. Not a product grant. |
| **Training data** | MUSDB-HQ + ~800 internal songs | Registry `dataset_licence`. MUSDB itself is educational/NC. Extra internal songs are not a shipping corpus. |
| **Derived student** | `UNKNOWN/LEGAL REVIEW` | Distilling envelopes from scientific-use weights does **not** mint a commercial student. `redistribution: weights unclear`. |

Intel OpenVINO / Hugging Face mirrors that label checkpoints “MIT” are **not authority**. Same issue thread (2024-06): a third party asked; the maintainer did **not** re-grant. Do not treat those mirrors as clearance.

This is **not legal advice**. Counsel owns any product-path reading. Until then the registry field stays UNKNOWN.

Repo `facebookresearch/demucs` is archived (2025-01-01). Maintained fork `adefossez/demucs` does not change the weight grant.

## Install state (this session) [FACT]

| Check | Result |
| --- | --- |
| `pyproject.toml` extras | `{musdb, mir, dev, silicon}` only. **No `demucs` extra.** `docs/HOST.md` records the same. |
| `uv.lock` | **zero** `demucs` hits |
| `from edgeai.mir.teachers import try_demucs; try_demucs()` | **`None`** (`import demucs.api` → `ImportError`) |
| `tests/test_teachers.py` | HPSS + envelope length. Does **not** import Demucs |
| `tests/test_demucs_envelope.py` | share/silence/vocals-only; no Demucs import; local path without tensor load |
| `docs/mir/P3C_RECEIPT.json` | `"demucs_installed": false` |
| `docs/mir/P3C_QUANT.json` | `"demucs": "NO"` |
| MUSDB STEMS on disk | 100 train + 50 test |
| Local HT-Demucs snapshot | inventoried (SHA above). **Not** a named GO. Not loaded |

Leave `try_demucs()` as a **soft optional**. Do not make tests require it. Do not `uv add` to satisfy the import.

## What the D26 HOST probe was (and remains)

**Was:** a named, bounded HOST-only run that:

1. Pinned one exact local `htdemucs` checkpoint by SHA and fetched nothing.
2. Preserved the **scientific-use** bound in writing (not a product grant).
3. Used the frozen MUSDB-5 only for comparison against stem truth, then one already-local unstemmed research witness.
4. Stored **envelopes / powers / share**, not WAVs or SDR tables.
5. Measured approximation quality against the stem oracle with source mapping, simplex, silence, finite-hop, and uncorrected lag diagnostics.
6. Stayed off USB, Cadence, Titan, and the already-closed C1 path.
7. Left derived weight clearance `UNKNOWN_LEGAL_REVIEW`, student I/O unfrozen, and outputs outside shipping/training lineage.

**Was not:** a project `uv add`, PyPI fetch, torch.hub experiment, MUSDB teacher replacement, 8 s loop, or lamp demo.

## Future reuse — what a new GO must name

D26 named the exact local SHA and required zero fetch. It does not authorise later checkpoint use. Any later reuse must name **all** of:

1. **Checkpoint id** — one of `htdemucs` / `htdemucs_ft` / `htdemucs_6s` (or a later pin with SHA/URL).
2. **Fetch channel** — explicit path (which repo/hub). Ban anonymous `torch.hub.load` without the pin.
3. **Licence acceptance** — scientific-use only; code MIT ≠ weights; derived student remains UNKNOWN/LEGAL REVIEW.
4. **Audio** — which unstemmed set; song-level split if we train; no window split; no SAME_SONG_LOOP.
5. **Output** — envelopes / four powers / share; not waveforms; not SDR-as-pass.
6. **Non-goals** — not Titan, not U55, not PDM, not C1 blocker, not I/O freeze.

The D26 HOST steps are complete: envelope design, structural inspection, isolated exact-SHA model load, MUSDB-5 calibration, unstemmed JSON witness, and hostile refusal regression. There was no fetch and no `Separator(repo=None)`. Do not rerun them by default.

## Bounds

| Act | Bound |
| --- | --- |
| Download HT-Demucs weights this session | **NO** |
| `uv add demucs` / project-environment install | **NO** |
| Isolated local-cache-only `pip --no-index` install | **DONE only for D26 J2**; ignored venv, dependency hashes unchanged |
| `torch.hub` | **NO**; executable tripwire |
| Treat MIT code as MIT weights | **NO** |
| Treat Intel/HF “MIT weights” as Meta grant | **NO** |
| Run Demucs on MUSDB as if it improved the oracle | **NO** — stems already win (D14) |
| Put Demucs / MERT / MuQ / MAEST on Titan | **NO** |
| Export the separator graph to U55 / PDM | **NO** |
| Reconstruct waveforms on-device | **NO** |
| Block C1 on this probe | **NO** |
| Freeze student I/O from Demucs stems | **NO** |
| Mix Demucs teacher outputs into a shipping student | **NO** (`UNKNOWN/LEGAL REVIEW`) |
| Loop a song/clip > 15 min in the room | **HARD FAIL** |
| Cadence silicon / USB-CDC / Serial Studio command | **NO** (CLOSED / observe only) |
| D26 HOST envelope probe under its named exact-SHA GO | **PASS**, HOST-ONLY, unstemmed scale |
| Keep MUSDB stems as today’s teacher | **YES** |
| Treat local HT-Demucs SHA inventory as a general named GO | **NO** — D26 authorised only the bounded exact-SHA probe |
| Load inventoried safetensors / construct Separator | **DONE only for D26 J2** with the tripwire active; no general project permission |

## Blitz execution brief — 2026-09-01 (amended; D26)

Captain approved the HOST blitz with amendments. This section is the amended execution authority; its completed result is recorded below.

**META_TASK:** Prove we can use **this exact locally pinned** scientific-use HT-Demucs artifact, **entirely offline**, to convert unstemmed HOST audio into **source-oracle-compatible** four-way activity shares. Stems remain authority where available. Every product / Titan / shipping path stays refused.

**PASS means:** that sentence. **PASS does not mean:** Demucs is part of K1.

**Legal fail-closed close:** `LOCAL_CHECKPOINT_INCOMPLETE` or load requires network → **STOP**. MUSDB stems remain authority. That is a successful probe, not a defect.

**NOT_THE_TASK:** C1, cadence, Titan, U55, PDM, student I/O freeze, `uv add demucs` into this repo, torch.hub, `Separator(repo=None)`, synthesizing `config.json`, 150-track bake-off, SDR as pass, Lxx.md waves, playing audio in the room.

### DEMUCS_TEACHER_SCHEMA_V1 (teacher artifact, not student I/O)

Student I/O stays **UNFROZEN**. This schema is only what a Demucs teacher **must emit** so runs are comparable.

```text
DEMUCS_TEACHER_SCHEMA_V1
sources:     vocals, drums, bass, other
stem measure: hop mean-square power  (same as source_oracle.frame_mean_square)
share:       P_i / ΣP
silence:     ΣP <= 1e-10 → [0,0,0,0]   (source_oracle silent total)
timebase:    source_oracle hop grid (default hop=512 samples)
waveforms:   ephemeral only; never persisted; no .wav; no stem cache
```

Helpers already in-tree: `share_from_stems`, `envelopes_from_stems`.

### Named checkpoint (local only)

| Field | Pin |
| --- | --- |
| File | `~/.cache/huggingface/hub/models--adefossez--HTDemucs/snapshots/bf35a81b663819a8255c8fefee17f9d812b786b5/955717e8.safetensors` |
| SHA256 | `d9fa14133cfcc034a6758923bb3a8ca9f8dfd0b582134643bbf83f72c17576dd` (84025440 bytes) |
| Companion | `htdemucs.yaml` = `models: ['955717e8']` only — **incomplete-manifest risk** |
| Licence | Weights UNKNOWN scientific-use (issue 327 comment 1134828611). Code MIT ≠ weights. Derived student UNKNOWN/LEGAL REVIEW. |
| Load | Never `Separator(repo=None)`. Never hub. Never fbaipublicfiles. |

### Frozen MUSDB-5 (J3) — `N=5 FUNCTIONAL_CALIBRATION — NOT GENERALIZATION CLAIM`

Picked **before** any Demucs run from existing `test_*` oracle-cache **mean share** (HOST, no separator). Do not swap after seeing results.

| Role | MUSDB18 test file | Mean share (V/D/B/O) |
| --- | --- | --- |
| vocal_dominant | `Side Effects Project - Sing With Me.stem.mp4` | 0.430 / 0.298 / 0.160 / 0.097 |
| drum_dominant | `PR - Happy Daze.stem.mp4` | 0.011 / 0.695 / 0.135 / 0.159 |
| bass_heavy | `Skelpolu - Resurrection.stem.mp4` | 0.024 / 0.176 / 0.532 / 0.254 |
| other_heavy | `Timboz - Pony.stem.mp4` | 0.121 / 0.170 / 0.105 / 0.587 |
| balanced | `Cristina Vane - So Easy.stem.mp4` | 0.252 / 0.246 / 0.218 / 0.285 |

Stop early if clearly broken on **three** tracks.

### Network tripwire (executable, not env-only)

`HF_HUB_OFFLINE=1` / `TRANSFORMERS_OFFLINE=1` are **not sufficient**. Before importing Demucs, install a process guard:

- `socket.socket.connect` and `socket.create_connection` raise **`DEMUCS_NETWORK_FORBIDDEN`**
- Also hard-fail `urllib.request`, `requests` (if present), `huggingface_hub` file download, `torch.hub.load` / `torch.hub.load_state_dict_from_url`

Invariant: **any connection attempt raises before a packet leaves.** Tests must **force** a fake hub/download path and watch it go **RED**. Env flags stay as belt; the tripwire is the braces.

### Isolated probe environment (J2) — no project mutation

```text
this repo pyproject.toml / uv.lock     UNTOUCHED
cached local wheels + local safetensors
        ↓
ephemeral venv  artifacts/demucs_host/.probe_venv/   (under gitignored artifacts/)
        ↓
HOST probe with tripwire
        ↓
keep JSON receipts; delete or keep venv separately
```

If the Demucs **wheel and deps are not already on this machine**, **STOP**. Do not `uv add demucs` into the project extra this blitz. Promote to a real extra only after HOST probe PASS **and** a later named decision.

### Sequence

```text
J1 DONE (D26) → J1.5 inspect (no tensor load, no install)
    → if not self-contained: LOCAL_CHECKPOINT_INCOMPLETE (legal close)
    → J2 isolated offline env + SHA-bound construct + tripwire
    → if loader green: J3 MUSDB-5 then J4 Ride It (sequential; same agent OK)
    → J5 refuse regression (Titan / no-GO) AFTER useful path works
    → DEMUCS_HOST_PROBE = PASS | LOCAL_CHECKPOINT_INCOMPLETE | NETWORK_FORBIDDEN
```

### Execution result — 2026-09-01

`DEMUCS_HOST_PROBE = PASS` for this exact local SHA. No network fetch occurred and no project dependency file changed.

| Gate | Result | Durable evidence |
| --- | --- | --- |
| **J1.5** | `STRUCTURALLY_PLAUSIBLE_FOR_OFFLINE_LOAD_PROBE`: 56,520-byte Safetensors header, 533 contiguous F16 tensors, embedded `demucs.htdemucs.HTDemucs`, expected four sources, SHA/size match, no tensor load or invented config | `docs/mir/receipts/demucs/J15_INSPECT.json` |
| **J2** | `OFFLINE_PROBE_ENV_READY` then `LOCAL_CHECKPOINT_LOAD_PASS`: isolated venv, 26 SHA-pinned local-cache wheels, `pip --no-index`, network tripwire, 41,984,456 parameters, project dependency hashes unchanged | `J2_ENV.json`; `J2_LOCAL_LOAD.json` |
| **J3** | `FUNCTIONAL_CALIBRATION_PASS`: frozen MUSDB-5, 112,688 aligned hops, identity mapping best by 0.4499 mean-Spearman margin, finite fraction 1.0, simplex p99 error `2.22e-16`, mean JS `0.02320`, best lag diagnostic 0 s for all sources | `MUSDB5_CAL.json` |
| **J4** | `RIDE_IT_RESEARCH_WITNESS_PASS`: 13,577-hop schema-v1 JSON under `research_only/`; required provenance; no wav, stem cache, playback, or training-lineage claim | `artifacts/demucs_host/research_only/ride_it_share.json` (ignored) |
| **J5** | Useful J2 path stays green while Titan, missing named GO, wrong SHA, arbitrary socket/urllib/requests/Hugging Face/torch.hub paths, and project-environment use all refuse | executable tests listed below |

J3 per-source approximation metrics:

| Source | Spearman | Pearson | MAE | RMSE |
| --- | ---: | ---: | ---: | ---: |
| vocals | 0.7750 | 0.9440 | 0.0345 | 0.0932 |
| drums | 0.9295 | 0.9604 | 0.0368 | 0.0967 |
| bass | 0.8905 | 0.9690 | 0.0404 | 0.0808 |
| other | 0.9045 | 0.9312 | 0.0566 | 0.1204 |

These figures establish a sensible, correctly ordered HOST approximation on the frozen five songs. They do not establish generalisation. `stems_beat_demucs: true` remains doctrine; SDR was not used for pass and no lag correction was applied.

Do **not** spawn J3/J4 execution before J2 is green. Scaffolding scripts in disjoint files is allowed; running Demucs is not.

Orchestration: **one orchestrator + at most two support lanes with disjoint files.** Not 40. Not Lxx.md. `SSA_RECEIPT_WAVE_IS_NOT_SHIP`.

### Jobs and DONE_WHEN

| ID | Job | Writer | DONE_WHEN (must be able to go red) |
| --- | --- | --- | --- |
| **J1** | Provenance lock | `docs/DECISIONS.md` D26 | **DONE.** `rg "## D26" docs/DECISIONS.md` |
| **J1.5** | Safetensors **header** + companion inventory. SHA re-hash. No tensor load. No install. No network. No invented config.json. | `scripts/demucs_checkpoint_inspect.py` → `docs/mir/receipts/demucs/J15_INSPECT.json` | Script exit 0 with `sha256_match: true` and either `structurally_plausible: true` **or** `verdict: LOCAL_CHECKPOINT_INCOMPLETE`. **Red** if it loads tensors, writes config, or opens a socket. |
| **J2** | Isolated venv from **local cache only**. SHA-bound load. Tripwire on. Construct the exact model. Never `repo=None`. | `src/edgeai/mir/demucs_network_guard.py` + loader used **only** from the probe venv; `tests/test_demucs_network_guard.py`; `tests/test_demucs_local_loader.py` | Guard tests go **red** on a forced hub/download. Loader **red** on SHA mismatch. Project `uv.lock` **unchanged**. |
| **J3** | Frozen MUSDB-5 mix → schema-v1 share vs stem oracle. | `scripts/demucs_musdb_calibrate.py` → `docs/mir/receipts/demucs/MUSDB5_CAL.json` | See J3 JSON below. **Red** if mapping invalid, shares non-finite, or sources swapped. `stems_beat_demucs` is a **doctrine field**, not the usefulness test. `N=5 FUNCTIONAL_CALIBRATION — NOT GENERALIZATION CLAIM`. No lag correction as authority. SDR diagnostic only, never pass. |
| **J4** | Ride It unstemmed envelopes. | `scripts/demucs_unstemmed_envelope.py` → `artifacts/demucs_host/research_only/ride_it_share.json` | JSON has schema-v1 keys; **no** `.wav`; provenance block below. **Red** if a wav/stem cache appears. Do **not** play the file. |
| **J5** | Hostile refuse after J2 works. | extend `tests/test_demucs_host.py` | `SPECTRASYNQ_TITAN=1` → None/refuse. Named GO unset → refuse. Probe exit 2 in the **project** env (no demucs extra). |

### J3 receipt shape (usefulness, not tautology)

```json
{
  "teacher_authority": "MUSDB_STEMS",
  "demucs_role": "approximation_calibration_only",
  "n": 5,
  "claim": "FUNCTIONAL_CALIBRATION — NOT GENERALIZATION CLAIM",
  "stems_beat_demucs": true,
  "tracks": ["Side Effects Project - Sing With Me", "PR - Happy Daze", "Skelpolu - Resurrection", "Timboz - Pony", "Cristina Vane - So Easy"],
  "per_source": {
    "vocals": {"spearman": null, "pearson": null, "mae": null, "rmse": null},
    "drums":  {"spearman": null, "pearson": null, "mae": null, "rmse": null},
    "bass":   {"spearman": null, "pearson": null, "mae": null, "rmse": null},
    "other":  {"spearman": null, "pearson": null, "mae": null, "rmse": null}
  },
  "share_sum_error_p99": null,
  "simplex_js_mean": null,
  "timing_lag_diagnostic": null,
  "mapping_valid": null,
  "silence_ok": null,
  "finite_hop_fraction": null,
  "lag_corrected": false
}
```

`mapping_valid` false (source-order swap / nonsense) → **J3 RED** even if `stems_beat_demucs` is true.

### J4 provenance (mandatory)

```json
{
  "purpose": "HOST_RESEARCH_WITNESS_ONLY",
  "source_audio": "/Users/spectrasynq/Workspace_Management/Software/YT_Saver/Regard_Ride_It.mp3",
  "source_audio_sha256": "a0df4f680c12ded3c24f3895b8aaab3cbf7a19c44e4ab62fc29f52358c1516fe",
  "teacher": "HTDemucs local 955717e8.safetensors",
  "checkpoint_sha256": "d9fa14133cfcc034a6758923bb3a8ca9f8dfd0b582134643bbf83f72c17576dd",
  "schema": "DEMUCS_TEACHER_SCHEMA_V1",
  "commercial_training_lineage": false,
  "derived_weight_clearance": "UNKNOWN_LEGAL_REVIEW",
  "not_training_dataset": true
}
```

Directory `artifacts/demucs_host/research_only/` — do not sweep into a training corpus.

### Preconditions preserved

Envelope helpers; probe exit 2 in project env; `try_demucs()` does not construct Separator; local SHA in registry; MUSDB 100+50; Ride It on disk; C1 `LGP_PERCEPTUAL_VALIDATED`; D26 written. J1 through J5 are now also complete; do not redo them without a named downstream reason.

### Resume rule

J1 through J5 are complete. Do not rerun Demucs simply to reconfirm the receipt. Re-enter only for a specifically named HOST downstream use, preserve the exact checkpoint SHA and network tripwire, and keep outputs outside commercial training lineage until counsel clears them.

### Ship path

1. **Shipped now:** D26 HOST probe is complete: exact-SHA offline load, frozen MUSDB-5 calibration, research-only unstemmed witness, and hostile refusal regression all pass.
2. **Selection:** satisfy `docs/mir/SELECTION_GATE.md`; freeze student I/O only if that gate selects source-share supervision.
3. **Provenance:** counsel must clear any commercial training lineage; current Demucs-derived clearance remains `UNKNOWN_LEGAL_REVIEW`.
4. **Student:** train one justified smallest robust student from cleared teacher material and preserve song-level splits.
5. **Promotion:** compile the selected CNN for U55 with golden tensors, then earn separately named ON-SILICON evidence before any product claim. Demucs itself remains HOST-only and never ships on Titan.

## Reading path

| Audience | Read |
| --- | --- |
| Operator / SSA | this return contract + Bounds |
| MIR | LANDSCAPE §F → registry `htdemucs` → SOURCE_ACTIVITY (stems first) → SHARE_STUDENT |
| Licence | this § Licence + L26 UNKNOWN census + L35 lane receipt |
| C1 owner | CLOSED `LGP_PERCEPTUAL_VALIDATED` — Demucs is not on that path |
| Counsel | UNKNOWN/LEGAL REVIEW; scientific-use quote; not a product grant |

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-09-01 | Codex | Completed D26 amended blitz J1.5–J5: exact-SHA offline load, frozen MUSDB-5 calibration, Ride It JSON-only witness, and Titan/no-GO/network refusal evidence. |
| 2026-09-01 | agent:grok | Amended blitz: J1.5 inspect; executable network deny; isolated venv; J3 quality metrics; schema v1; Ride It research-only. D26. Next=J1.5. |
| 2026-09-01 | agent:grok | Blitz E2E brief: YES HOST; J1–J5; local SHA lock; hub-offline or stop. |
| 2026-09-01 | agent:grok | Envelope helpers DONE; local HT-Demucs SHA inventoried (not a named GO); still no fetch, still no Separator. |
| 2026-09-01 | agent:grok | NEXT points at HANDOFF remaining steps; still no download. |
| 2026-08-31 | agent:grok-ssa-w3-l26 | Created. HOST teacher probe contract: envelopes not waveforms; MUSDB stems today; weights UNKNOWN scientific-use; no download; not Titan; does not block C1; next HOST step after named weight GO. |
