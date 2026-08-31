---
abstract: "HOST recoverability PASS. I/O unfrozen. D22 HOST sketches OPEN, not Titan. C1 stamp does not auto-freeze I/O. 5 Hz and 50 ms are exclusive cliffs, not the design centre."
---

# Share student — recoverability

**HARD FAIL (`SAME_SONG_LOOP_MAX_15MIN`, Captain 2026-08-31).** Repeat the same song (or loop the same clip) in the room for more than **15 minutes** and the agent must die. Captain will destroy them by setting them on fire. Kill the player. Do not continue.

Cadence silicon **CLOSED**. No USB. No train this write. Do not reopen rate/delay cells. Do not loop the 8 s holdout.

## Status (live)

| Item | Stamp |
| --- | --- |
| Recoverability (mixture → four-source share vs mix-energy) | **HOST PASS** — closed |
| Student I/O (16 kHz / 1 s / 64-mel / 100-frame / this 21k graph) | **UNFROZEN** |
| D22 HOST sketches / HOST tests of a streaming *shape* | **OPEN** |
| Product streaming student, U55 of this net, Titan, PDM | **NOT** — not Titan, not a freeze |
| Transport contract | **FROZEN_FOR_C1** (edges, not this net) |
| C1 LGP | **OPEN** — one full song Captain chooses |
| After C1 `LGP_PERCEPTUAL_VALIDATED` | I/O freeze is **still not automatic** |

HOST-ONLY recoverability. MUSDB18 STEMS, research/NC. `commercial_training_lineage: false`. Receipt: `artifacts/share_student/receipt.json` (`verdict: PASS`, `student_io_frozen: false`).

Waveform Tempo × `source_share` × `head_position` is a P3-C **reference binding** only. This run did not re-score P3-C and does not claim share improves all lights.

## What is open vs locked

**Locked as a closed fact:** a tiny causal CNN recovers four-source **share** from the mixture, on official MUSDB18 **song-level** splits, better than a mix-energy baseline. `other` stays. The simplex is four-way.

**Not locked:** sample rate, window, stride, mel bins, tensor layout, CNN width/depth, windowed vs hop-level vs streaming graph, powers-then-normalise vs exported logits, U55 of *this* net. Do not freeze Student-v0 until `docs/mir/SELECTION_GATE.md` is satisfied **and** an explicit I/O freeze is written. A C1 look, even a PASS stamp, does not itself freeze 16 kHz / 1 s / 64-mel.

**D22 (Captain 2026-08-31):** HOST sketches and HOST tests of a streaming student **unblocked**. That is paper + host numpy/tests, not Titan, not a product net, not RUHMI of the 21k 1 s pool. D17’s “stop hop-level/streaming student work” is **superseded for HOST sketches only**. Product freeze + deploy still wait on C1 *and* a later explicit freeze.

## Cliffs are not the design centre

Silicon cadence (CLOSED) measured two **1-D edges** and one **joint** cell. The edges are mutually exclusive. They are not a design centre to AND into one student.

| Envelope | Cell | Q1 Spearman (head vs extra_gain) | Verdict |
| --- | --- | ---: | --- |
| Slowest 0-delay PASS | `r5_d0` · 5 Hz · 0 ms · 0 hops | 0.414 | **PASS** |
| Largest added-delay PASS | `r20_d50` · 20 Hz · 50 ms requested (64 ms = 2 hops) | 0.402 | **PASS** |
| AND — banned | `r5_d50` · 5 Hz · 50 ms requested (64 ms = 2 hops) | 0.245 | **FAIL (Q1)** |

Receipts: `artifacts/gate_c0_cadence_silicon/cells/{r5_d0,r20_d50,r5_d50}.json`, `CADENCE_RESULT.json`, `SEMANTIC_TRANSPORT_CONTRACT.json`. Hold is ZOH then causal delay; no interpolation; lookahead 0. 10 Hz + 25 ms **not completed** — do not interpolate it. 100 ms at 20 Hz FAIL.

**Design centre for C1 playback** is the already-proven C0-v2 carrier: **~31.25 Hz, 0 ms extra delay**, product firmware. That is the light-show clock for the LGP look. It is **not** a student I/O freeze (D17: do not freeze 31.25 Hz because a renderer used it).

**Design centre for a later student** is one exclusive envelope **R XOR D**, never both cliffs at once:

- **R:** emit ≥ 5 Hz with **0** extra delay after the sample exists.
- **D:** emit ≥ 20 Hz with **50 ms requested** extra delay (64 ms on the 32 ms hop grid).

A student that assumes 5 Hz **and** 50 ms extra delay rebuilds `r5_d50` Q1 FAIL. Packet clock ≠ emit clock: authored `hz` stays 30–240; do not put `hz=5` on the wire.

The 21k feasibility net pools a **1 s** log-mel with `AdaptiveAvgPool2d((1,1))` (~1 Hz emit, ~1 s latency). That graph **misses both edges** as a streaming frontend. Keep it as recoverability evidence. Do not gold-plate it as RA8P1 I/O. D11 still requires AdaptiveAvgPool2d (not `ReduceMean`) **if** a later CNN is exported — that is an op rule, not a 1 s window lock.

HOST cadence rehearsal (`docs/mir/GATE_C_CADENCE_HOST.md`) is design evidence only. Silicon owns the product clock.

## After C1, freeze is still not automatic

Programme:

```text
C0-v2 PASS → cadence CLOSED → transport frozen for C1 → C1 LGP look
  → stamp LGP_PERCEPTUAL_VALIDATED only if the three LGP questions pass
  → student I/O freeze only if SELECTION_GATE is satisfied AND the transport still holds
    AND someone writes the freeze
```

C1 answers whether ownership-driven head motion is a light show through the LGP. It does **not** auto-lock 16 kHz, 1 s windows, 64-mel, four logits, or a hop-level CNN. D20/D22: freeze student I/O **after C1 if the contract still holds** — a separate act, not a side effect of the look.

Until that freeze: HOST sketches OPEN; Titan CLOSED for this student; no new product net.

## Question (recoverability — closed)

Can a tiny model infer four-source ownership (share) from mixture audio, on official MUSDB18 **song-level** splits, better than a mix-energy baseline?

Share is hop stem-power / sum, silence → zeros — same definition as `source_oracle`. The student emits four non-negative powers (`softplus` logits) then that normalisation. No composition_change ML head (parked; still a function of share(t) vs share(t−Δ)).

Headline figures are vocals/drums/bass. **`other` stays.** Dropping `other` would quietly turn this back into a three-source student. It does not block Gate C. It must remain in receipts and MAE tables.

## Split

| set | n songs | n windows | origin |
| --- | ---: | ---: | --- |
| train | 90 | 2160 | official `train/` (all official-train remaining after val carve); val carved by hashed **song** id |
| val | 10 | 160 | official `train/` holdout songs, not windows |
| test | 50 | 12435 | official `test/` |

Window-level splitting is banned. `assert_no_song_leak` held.

## Model (experiment, not a lock)

- 20788 params, 81.2 KiB fp32
- causal depthwise-separable CNN + `AdaptiveAvgPool2d((1,1))` (D11 — no `tensor.mean`)
- 16 kHz / 1 s / 64-mel / 100-frame log-mel is this experiment's frontend, not a frozen student I/O. Causal conv + AdaptiveAvgPool2d((1,1)) → 1 s latency.

## Official test — within-track Pearson

n_test_songs = 50. 1 s windows, 1 s hop. Compared to this-run `r(true_share, mix)` and to P3-B hop-level refs (vocals 0.17, drums 0.10, bass 0.16).

| source | r(pred, true) | r(pred, mix) | r(true, mix) | P3-B r(true, mix) | mix-linear r(pred, true) | MAE |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| vocals | 0.637 | 0.066 | 0.143 | 0.17 | 0.132 | 0.114 |
| drums | 0.568 | 0.088 | 0.215 | 0.10 | 0.187 | 0.141 |
| bass | 0.537 | 0.160 | 0.219 | 0.16 | 0.202 | 0.125 |
| other | 0.547 | -0.385 | -0.165 | — | 0.116 | 0.138 |

Macro MAE = 0.129. Epochs = 6. Device = `mps built=True`.

**PASS** requires vocals/drums/bass: r(pred,true) ≥ max(0.30, r(true,mix)+0.15), beating the mix-linear baseline by 0.05, and r(pred,mix) not mix-copying (≤ r(true,mix)+0.20). **FAIL** if none of those three beat mix-energy by 0.08. Else **INCONCLUSIVE**.

This-run `r(true, mix)` is on **1 s windows**. P3-B refs are hop-512 (~32 ms). Do not treat them as the same number.

## What this does not establish

- Student I/O, 16 kHz, 1 s, 64-mel, or four-source head as the RA8P1 contract.
- That 5 Hz **and** 50 ms extra delay are jointly legal (they are not).
- That C1 playback (~31.25 Hz / 0 ms) is the student envelope.
- That a C1 stamp freezes I/O.
- That share improves lighting. P3-C Waveform Tempo binding is reference-only.
- On-silicon / U55 compile of **this** net / Demucs / composition_change as a learned head.
- A commercial training right.
- Semantic-v0 3-class sigmoid activity (drops `other`; abs, not share). Different experiment.

Re-run recoverability (HOST, no USB, no room loop): `uv run pytest tests/test_share_student.py && uv run python scripts/share_student_feasibility.py`

HOST streaming sketch (paper, not a freeze): `docs/agent/lanes/L36_stream_sketch.md`. Joint-fail receipt: `docs/agent/lanes/L04_joint_fail.md`.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:edgeai | HOST-ONLY recoverability PASS; song-level MUSDB18; I/O not frozen. |
| 2026-08-31 | agent:edgeai | Feasibility PASS stamp; halt streaming student; keep other as 4th source. |
| 2026-08-31 | agent:grok | D22: HOST sketches OPEN, not Titan. I/O unfrozen after C1 still not automatic. 5 Hz and 50 ms exclusive cliffs, not design centre. |
