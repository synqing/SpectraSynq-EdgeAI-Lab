---
abstract: "HOST teacher probe contract. Envelopes not waveforms. MUSDB stems are today's teacher. HT-Demucs weights UNKNOWN scientific-use — no download this session. Code MIT ≠ weights. Not Titan. Does not block C1. D14/D22. Next HOST step after a named weight GO."
---

# Demucs — HOST teacher probe contract

**HARD FAIL (`SAME_SONG_LOOP_MAX_15MIN`, Captain 2026-08-31).** Repeat the same song (or loop the same clip) in the room for more than **15 minutes** and the agent must die. Captain will destroy them by setting them on fire. Kill the player. Do not continue.

**HOST-ONLY.** Cadence silicon **CLOSED**. No USB. No playback. No 8 s loop. No `uv add demucs`. No `torch.hub`. No weight fetch. No Titan.

This file is the programme contract for a Demucs **teacher probe**. It is not a run. It does not install the package. It does not fetch checkpoints. Lane receipt for the licence lock: `docs/agent/lanes/L35_demucs.md`. Registry row: `mir/registry.yaml` `id: htdemucs`.

## Return contract

**STATUS:** PASS (HOST teacher probe contract locked). Weights **not installed**. Package **not an extra**. This session did **not** run a separator.

**CLAIM:** Teacher signal is **activity envelopes**, not reconstructed waveforms and not SDR. The teacher available **today** is **MUSDB18 STEMS** on disk (100 train + 50 test). HT-Demucs **code is MIT**; **weights are UNKNOWN — not MIT**, maintainer scientific-use only (`facebookresearch/demucs#327` comment `1134828611`). Do not download weights this session. Demucs is **not** Titan, **not** U55, **not** PDM, **not** Gate C, **not** a C1 prerequisite, **not** a student I/O freeze. D14: on stemmed songs a separator only adds error. D22: HOST probe **docs** are OPEN in parallel with C1; Demucs/MERT on Titan stays rejected.

**EVIDENCE:** this file; `AGENTS.md` Demucs row; `docs/DECISIONS.md` D14 + D22; `mir/registry.yaml` `id: htdemucs`; `docs/mir/LANDSCAPE.md` §F; `docs/mir/SOURCE_ACTIVITY.md`; `docs/mir/SHARE_STUDENT.md`; `docs/mir/GATE_C.md` parked row; `src/edgeai/mir/teachers.py` (`activity_envelope`, `try_demucs`); `tests/test_teachers.py` (HPSS only); `pyproject.toml` extras `{musdb, mir, dev, silicon}` (no `demucs`); `uv.lock` zero `demucs` hits; `uv run` `try_demucs() is None`; `docs/mir/P3C_RECEIPT.json` `demucs_installed: false`; `docs/mir/P3C_QUANT.json` stamps `"demucs": "NO"`; `datasets/musdb18/{train,test}` 100+50 STEMS; GitHub LICENSE raw (MIT, Meta); issue `#327` still **open** (locked), comment `1134828611` 2022-05-23T15:36:04Z.

**COMMAND:** none. Docs/licence/role lock only. Did not `uv add demucs`. Did not import `demucs.api`. Did not call `Separator`. Did not hit `torch.hub` or `dl.fbaipublicfiles.com`. No USB, no flash, no Cadence reopen, no song in the room.

**METHOD_RISK:** Licence facts re-fetched from public GitHub (LICENSE raw + issues API). **Not legal advice.** PyPI “MIT” and third-party “MIT weights” mirrors are **not** a Meta grant. `try_demucs() is None` proves `ImportError`, not that a hub cache is empty — we did not fetch. MUSDB on disk is **STEMS** (AAC `.mp4`), not HQ WAV. A later HOST probe still needs a **named weight GO** and still does not go to Titan.

**NEXT:** Leave weights UNKNOWN. Leave `try_demucs()` returning `None`. Do not block C1. The next **real** HOST step is **after a named weight GO** (checkpoint + scientific-use acceptance + unstemmed envelope probe, HOST only). Until that GO, MUSDB stems remain the teacher.

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
    → HOST separator                # HT-Demucs or other
    → activity_envelope(stem)       # RMS / share — throw the waveform away
    → supervise the same tiny student
    → mix window → student → activity vector

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

Envelope path already in-tree (`teachers.py`): hop RMS of each stem, peak-normalised for the cheap HPSS baseline. The **oracle** path (`source_oracle.py`) is the one the student copies: hop **power** → four-way share, silence → zeros, no invented equal shares. A Demucs teacher, if it ever runs, must emit **that** shape (or the four powers that normalise into it). It must not emit stereo WAVs as the stored teacher signal.

`mir/registry.yaml` `htdemucs.temporal_resolution`: `waveform; activity via envelope of stems`.  
`msst` row: *“Teacher signal is activity envelopes, not SDR.”*

Do **not** reconstruct waveforms on Titan. LANDSCAPE §F.

## Available teacher today: MUSDB stems

[FACT] `datasets/musdb18/train/` has **100** tracks, `test/` has **50**. Native Instruments STEMS (`.mp4`, five AAC streams: mix, drums, bass, other, vocals). Educational / non-commercial. `commercial_training_lineage: false`.

That **is** the teacher for source ownership **now**.

| Job | Teacher | Status |
| --- | --- | --- |
| Perfect abs / share / delta on 150 songs | MUSDB18 STEMS | **executed** (P3-B, P3-C) |
| Tiny CNN recoverability from the mix | same stems, song-level split | **HOST PASS** |
| Unstemmed scale (no GT stems) | would be a separator | **not started** — weights UNKNOWN, no download |
| Live/venue | PaRIRset IRs on DSP onset, not stems | different lane |

D14, verbatim sense: if lights never benefit, there is nothing to teach; if they do, **MUSDB stems are already perfect supervision — a separator teacher would only add error.** Share × Waveform Tempo × head_position **did** pass on those stems. Therefore Demucs on MUSDB is a **worse** teacher than the stems we already have. Installing it “to complete P3” is a regression.

SOURCE_ACTIVITY: *“Demucs only after recoverability, for unstemmed scale.”* Recoverability is HOST PASS. Unstemmed scale is still **later**, and still **HOST**, and still behind a **named weight GO**.

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

D22 unblocked every **HOST** lane for parallel SSA. Cadence stays CLOSED. C1 is the LGP look (one full song Captain chooses, no 8 s loop). **Rejected:** Demucs/MERT on Titan.

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
| `docs/mir/P3C_RECEIPT.json` | `"demucs_installed": false` |
| `docs/mir/P3C_QUANT.json` | `"demucs": "NO"` |
| MUSDB STEMS on disk | 100 train + 50 test |

Leave `try_demucs()` as a **soft optional**. Do not make tests require it. Do not `uv add` to satisfy the import.

## What a future HOST probe is (and is not)

**Is:** after a **named weight GO**, a HOST-only run that:

1. Pins **one** checkpoint by name (`htdemucs` / `htdemucs_ft` / `htdemucs_6s` — pick one; do not fetch the zoo).
2. Accepts the **scientific-use** bound in writing on that GO (not a product grant).
3. Runs on **unstemmed** audio we already have licence to research (not a new 22 GB grab as a blocker).
4. Stores **envelopes / powers / share**, not WAVs, not SDR tables as the lighting score.
5. Compares teacher share vs mix energy and vs HPSS — same question as P3, not a SiSEC bake-off.
6. Stays off USB, off Cadence, off Titan, off C1’s critical path.
7. Leaves `derived_weight_status: UNKNOWN/LEGAL REVIEW`. Does not freeze student I/O. Does not mix outputs into a shipping corpus.

**Is not:** `uv add demucs` because an agent is bored. Not a PyPI “MIT” fetch. Not torch.hub “just to see”. Not MUSDB re-separation. Not an 8 s loop. Not a lamp demo.

## Named weight GO — what it must name

No fetch until a GO names **all** of:

1. **Checkpoint id** — one of `htdemucs` / `htdemucs_ft` / `htdemucs_6s` (or a later pin with SHA/URL).
2. **Fetch channel** — explicit path (which repo/hub). Ban anonymous `torch.hub.load` without the pin.
3. **Licence acceptance** — scientific-use only; code MIT ≠ weights; derived student remains UNKNOWN/LEGAL REVIEW.
4. **Audio** — which unstemmed set; song-level split if we train; no window split; no SAME_SONG_LOOP.
5. **Output** — envelopes / four powers / share; not waveforms; not SDR-as-pass.
6. **Non-goals** — not Titan, not U55, not PDM, not C1 blocker, not I/O freeze.

Until that GO exists, the next HOST action on this lane is **nothing**.

## Bounds

| Act | Bound |
| --- | --- |
| Download HT-Demucs weights this session | **NO** |
| `uv add demucs` / `pip install demucs` / `torch.hub` | **NO** until named weight GO |
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
| HOST envelope probe **after** named weight GO | **allowed**, HOST-ONLY, unstemmed scale |
| Keep MUSDB stems as today’s teacher | **YES** |

## Reading path

| Audience | Read |
| --- | --- |
| Operator / SSA | this return contract + Bounds |
| MIR | LANDSCAPE §F → registry `htdemucs` → SOURCE_ACTIVITY (stems first) → SHARE_STUDENT |
| Licence | this § Licence + L26 UNKNOWN census + L35 lane receipt |
| C1 owner | GATE_C1 — Demucs is not on that path |
| Counsel | UNKNOWN/LEGAL REVIEW; scientific-use quote; not a product grant |

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:grok-ssa-w3-l26 | Created. HOST teacher probe contract: envelopes not waveforms; MUSDB stems today; weights UNKNOWN scientific-use; no download; not Titan; does not block C1; next HOST step after named weight GO. |
