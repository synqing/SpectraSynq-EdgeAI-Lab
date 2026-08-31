---
abstract: "HOST recoverability PASS (feasibility). Four-source simplex including other. No hop-level/streaming student until Gate C. I/O not frozen."
---

# Share student — recoverability

**PASS** on whether a tiny causal CNN recovers four-source **share** from the mixture better than mix-energy.

HOST-ONLY. MUSDB18 STEMS, research/NC. `commercial_training_lineage: false`. Student I/O is **not** frozen.

**Stop.** Do not build a hop-level or streaming student until Gate C (`docs/mir/GATE_C.md`) says the semantic deserves a contract. This 21k net is feasibility evidence, not a deployment candidate.

Headline figures are vocals/drums/bass. **`other` stays.** The simplex is four-way; dropping `other` would quietly turn this back into a three-source student. It does not block Gate C. It must remain in receipts and MAE tables.

Waveform Tempo × `source_share` × `head_position` is a P3-C **reference binding** only. This run did not re-score P3-C and does not claim share improves all lights.

## Question

Can a tiny model infer four-source ownership (share) from mixture audio, on official MUSDB18 **song-level** splits, better than a mix-energy baseline?

Share is hop stem-power / sum, silence → zeros — same definition as `source_oracle`. The student emits four non-negative powers (`softplus` logits) then that normalisation. No composition_change ML head.

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
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| vocals | 0.637 | 0.066 | 0.143 | 0.17 | 0.132 | 0.114 |
| drums | 0.568 | 0.088 | 0.215 | 0.10 | 0.187 | 0.141 |
| bass | 0.537 | 0.160 | 0.219 | 0.16 | 0.202 | 0.125 |
| other | 0.547 | -0.385 | -0.165 | — | 0.116 | 0.138 |

Macro MAE = 0.129. Epochs = 6. Device = `mps built=True`.

**PASS** requires vocals/drums/bass: r(pred,true) ≥ max(0.30, r(true,mix)+0.15), beating the mix-linear baseline by 0.05, and r(pred,mix) not mix-copying (≤ r(true,mix)+0.20). **FAIL** if none of those three beat mix-energy by 0.08. Else **INCONCLUSIVE**.

This-run `r(true, mix)` is on **1 s windows**. P3-B refs are hop-512 (~32 ms). Do not treat them as the same number.

## What this does not establish

- Student I/O, 16 kHz, 1 s, 64-mel, or four-source head as the RA8P1 contract.
- That share improves lighting. P3-C Waveform Tempo binding is reference-only.
- On-silicon / U55 compile / Demucs / composition_change as a learned head.
- A commercial training right.

Re-run: `uv run pytest tests/test_share_student.py && uv run python scripts/share_student_feasibility.py`

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:edgeai | HOST-ONLY recoverability PASS; song-level MUSDB18; I/O not frozen. |
| 2026-08-31 | agent:edgeai | Feasibility PASS stamp; halt streaming student; keep other as 4th source. |
