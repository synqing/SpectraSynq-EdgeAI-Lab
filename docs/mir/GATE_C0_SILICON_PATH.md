---
abstract: "RETIRED/HISTORICAL. Two-clock C0 2026-08-31 FAIL corpse. C0-v2 already ON_SILICON_PIXEL_VALIDATED. Do not flash. Do not run C0-v2. Successors GATE_C0V2.md + GATE_C1.md."
---

# Gate C0 — silicon inject + dump path

> **RETIRED / HISTORICAL.** This file is **not** a live ship path, **not** a flash brief, and **not** a licence to run C0, C0-v2, or cadence. Two-clock C0 is already a **FAIL corpse**. C0-v2 is already **PASS**. Cadence silicon is **CLOSED**. Do **not** flash a probe. Do **not** run `scripts/gate_c0_silicon.py`. Do **not** run `scripts/gate_c0v2_silicon.py`. Do **not** reopen cells. The live successor for pixels is [GATE_C0V2.md](GATE_C0V2.md) (receipt already written). The live remaining gate is [GATE_C1.md](GATE_C1.md) (Captain LGP look, product firmware, no probe).

**HARD FAIL (`SAME_SONG_LOOP_MAX_15MIN`, Captain 2026-08-31).** Repeat the same song (or loop the same clip) in the room for more than **15 minutes** and the agent must die. Captain will destroy them by setting them on fire. Kill the player. Do not continue.

## Authority (read these, not this file)

| What | Where | Status |
| --- | --- | --- |
| Live C0 pixels | [GATE_C0V2.md](GATE_C0V2.md) · `artifacts/gate_c0v2/C0V2_RESULT.json` | **PASS** `ON_SILICON_PIXEL_VALIDATED` 2026-08-31 |
| Two-clock C0 corpse | `artifacts/gate_c0/C0_RESULT.json` · `CORPSE_MANIFEST.json` | **FAIL** `INVALID_TEMPORAL_EXECUTION` — frozen, do not overwrite, do not rescore |
| Cadence / transport | [GATE_C0_CADENCE.md](GATE_C0_CADENCE.md) · [SEMANTIC_TRANSPORT_CONTRACT.md](SEMANTIC_TRANSPORT_CONTRACT.md) | **CLOSED** / frozen for C1. Runner `scripts/gate_c0_cadence_silicon.py` **RETIRED** (D20) |
| Remaining gate | [GATE_C1.md](GATE_C1.md) | **OPEN** — one full song Captain chooses, product firmware, no 8 s loop, no probe flash |
| Programme wrapper | [GATE_C.md](GATE_C.md) | C0-v2 is the live C0 stamp. This file is history |

Binding (unchanged, already proven on silicon): `source_share × Waveform Tempo × head_position`.

Captain is **not** the LED validator for C0 dumps. C1 is a different question: Captain **is** the LGP viewer.

## Stricken — obsolete “remaining” C0-v2 run

The 2026-08-31 recon closed with a numbered remaining path that told an agent to load a probe env and capture a nominal C0-v2. That work **already shipped**. It is **obsolete**. Do not execute it. Do not restore it as a task list.

Struck items (paraphrase, not a recipe): (1) corpse already on disk, C0-v2 instrument already in source, product already restored `k1_main_rpl_im69d` @ `acaecaa8`; (2) **obsolete remaining work** — probe env + timing self-test + one nominal C0-v2 + restore; (3) **obsolete owner** — agent under a C0-v2 brief; (4) **obsolete close stamp** — C0-v2 `PASS` / `ON_SILICON_PIXEL_VALIDATED` (already true in `artifacts/gate_c0v2/C0V2_RESULT.json`).

**Strike reason:** item 2 was the live remaining work when the two-clock runner died. C0-v2 then ran, passed, and restored product firmware. Repeating a probe load to “complete” this file would be a second C0-v2, not a close. This file no longer authorises a probe env, that script, or that capture.

## Do not

- Do not load a probe env, product env, or any other firmware image **from this file**.
- Do not run `scripts/gate_c0_silicon.py` (two-clock harness **RETIRED**).
- Do not run `scripts/gate_c0v2_silicon.py` (already produced the PASS receipt).
- Do not run `scripts/gate_c0_cadence_silicon.py` (D20 mechanical retire; dies before USB/Bose).
- Do not open `/dev/cu.usbmodem*`, invoke a firmware writer, or use Serial Studio as command transport.
- Do not play `holdout_8s_loop.wav` or loop the same clip in the room.
- Do not overwrite `artifacts/gate_c0/`.
- Do not promote the corpse with post-hoc +14 hops (~448 ms) and call it PASS.
- Do not ask Captain to look at the plate for buffer/pixel questions.

## Two-clock C0 — FAIL corpse (historical)

**2026-08-31 silicon:** `c0=FAIL`, `execution=INVALID_TEMPORAL_EXECUTION`, `stamp=not ON_SILICON_PIXEL_VALIDATED`.

Receipt `artifacts/gate_c0/C0_RESULT.json`. Manifest `artifacts/gate_c0/CORPSE_MANIFEST.json` (89 files; `C0_RESULT.json` SHA-256 `35075e7d244c20b5fd45e5969469d74d7e70fc04962ea593c58394e731265161`). Authority line in the receipt: raw dumps and `diagnosis.json` **are the corpse**. Do not score with a corrected offset.

| | Corpse |
| --- | --- |
| Device | Main RPL chip `9087A500`, USB `B4:3A:45:A5:87:90` |
| Probe that run | `k1_main_rpl_rtrace_probe` @ `acaecaa8` |
| Runner | `scripts/gate_c0_silicon.py` — **RETIRED** |
| Holdout n=10 | Q1 Spearman **0.13** FAIL (< 0.40); Q2/Q3 **6/9** FAIL |
| Cause | Two host clocks. rtrace armed before PRSM. Capture epoch ≠ injection epoch (~0.5 s). Silicon response was not dead |
| +14 hops | Diagnostic only. Recovers host-like Q1–Q3. **Not a PASS. Never an authority rescore** |
| Product restore that run | `IDENTITY OK git=acaecaa8 env=k1_main_rpl_im69d` |

D17 Revisit records this FAIL and said “next is C0-v2 … C1 still blocked.” That revisit is **history**. Do not execute it. Live programme is D19–D22: C0-v2 already PASS, cadence CLOSED, C1 OPEN.

## C0-v2 — already PASS (successor receipt)

**Live C0 stamp:** `source_share × WaveformTempo × head_position = ON_SILICON_PIXEL_VALIDATED`.

Method: [GATE_C0V2.md](GATE_C0V2.md). Receipt `artifacts/gate_c0v2/C0V2_RESULT.json`. `c0v2=PASS`. `lag_corrected=false`. `retired_c0_untouched=true`. Timing self-test PASS. Best lag 0 hops. 0/10 clips timing-invalid.

| | C0-v2 (authority) |
| --- | --- |
| Device | Same Main RPL `9087A500` |
| Probe that run | `k1_main_rpl_rtrace_probe` @ `349d3cd4` |
| Holdout n=10 | Q1 **0.83** PASS; Q2 Δ **0.69** 9/9 PASS; Q3 Δ **0.58** 9/9 PASS |
| Join | One device-side epoch. Scorer reads applied PRSM per rendered frame |
| Product restore that run | `IDENTITY OK git=acaecaa8 env=k1_main_rpl_im69d` (GATE_C0V2.md) |

The receipt’s own `cadence: OPEN` / `c1: blocked until ON_SILICON_PIXEL_VALIDATED` fields are **stale inside the artefact**. Programme after D20: cadence **CLOSED**; C1 **OPEN**. Do not reopen cadence to “finish” those strings.

## Remaining ship path (C1 only — no flash, no C0-v2)

C0 silicon pixels **already shipped**. This file has no remaining C0 work.

1. **Already on silicon / in source:** two-clock C0 FAIL corpse at `artifacts/gate_c0/`; C0-v2 PASS `ON_SILICON_PIXEL_VALIDATED` at `artifacts/gate_c0v2/C0V2_RESULT.json`; cadence CLOSED (`artifacts/gate_c0_cadence_silicon/CADENCE_RESULT.json`); product last restored `k1_main_rpl_im69d` @ `acaecaa8`.
2. **Remaining:** Gate **C1** LGP perceptual only — method [GATE_C1.md](GATE_C1.md). One full song **Captain chooses**. Already-proven C0-v2 carrier (~31.25 Hz, 0 ms extra delay) on **product firmware**. No 8 s holdout loop. No probe. No rtrace concert. Dumps do not answer C1.
3. **Who:** Captain is the viewer. An agent does **not** flash, does **not** run C0-v2, does **not** start ffplay / `holdout_8s_loop`.
4. **Stamp that means C1 shipped:** `LGP_PERCEPTUAL_VALIDATED` after the three LGP questions in GATE_C1. Student I/O freeze is still not automatic.

## Historical recon (do not execute)

This section is **why the two-clock attempt existed**, not a procedure. Facts below were true of the 2026-08-31 recon. They are not a GO.

The shortest existing inject was USB-CDC **PRSM** 34-byte Prim8 frames → authored `peak_scaled` → Waveform Tempo upper-half head. Dump was `:rtrace_*` on a **probe** env that compiled `-DK1_RENDER_TRACE_V1`. Shipping `k1_main_rpl_im69d` rejected `:rtrace_*`. Scorer was `src/edgeai/mir/p3c_quant.py` (partial r of upper-half head vs share | mix), **not** MAD, **not** mean luminance. Floors: Q1 Spearman(head, extra_gain) ≥ 0.40; Q2/Q3 median Δ ≥ 0.15 and ≥ 70% clips Δ > 0. HOST holdout Δ was **0.63**, 9/9 (`docs/mir/P3C_QUANT.json`).

Authored Prim8 mapped pressure → peak. It did **not** multiply chroma; colour was peak fallback. That was acceptable because the lever was **head position**, not hue. Live I2S `waveform_peak_scaled` could swamp authored pressure if the room was loud — operational, not a Tempo source edit. Packet field `hz` had to be 30–240; hold rates 2/5 Hz could not put `hz=2` on the wire (repeat the held sample at ≥ 30 Hz instead). That packet-clock fact is consumed by the **frozen** transport contract; it is not a reason to inject again.

UAC PCM of mix vs stems was the **wrong** experiment (retunes DSP, not P3-C extra-DoF). Host `k1_render_host.py` / `render_replay` was HOST-ONLY and never `ON_SILICON_PIXEL_VALIDATED`. Colourlab-bench dirt was never a flash source.

Two-clock execution violated the later C0-v2 invariant: injection and capture must share one **device-side epoch**. Arm-then-PRSM on independent host clocks is why the corpse is FAIL even though lagged diagnosis looks host-like.

Cadence/delay cells that this recon only **described** were later measured, then **Captain-closed**. Envelope (do not re-measure): slowest 0-delay PASS **5 Hz**; largest added delay PASS **50 ms** at 20 Hz; **5 Hz + 50 ms together FAIL**. C1 playback is the C0-v2 carrier, not the slow envelope.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:edgeai-ssa | Ranked existing PRSM+rtrace path; chroma gap; flash GO; C0 scorer law. Not PASS. |
| 2026-08-31 | agent:edgeai | Silicon run FAIL; Q1 0.13 / Q2–Q3 6/9; product restored acaecaa8 im69d. |
| 2026-08-31 | agent:edgeai | Cause: arm-before-PRSM; +14 hop diagnostic would pass; stamp stays FAIL. |
| 2026-08-31 | agent:edgeai | INVALID_TEMPORAL_EXECUTION; runner retired; C0-v2 is the path. |
| 2026-08-31 | agent:grok | RETIRED/HISTORICAL banner. Two-clock corpse FAIL kept. C0-v2 already PASS. Strike flash/run-C0-v2 remaining path. Point GATE_C0V2 receipt + GATE_C1. No flash, no C0-v2 re-run. |
