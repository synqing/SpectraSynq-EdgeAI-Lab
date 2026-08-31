---
abstract: "C0-v2 PASS 2026-08-31: source_share × WaveformTempo × head_position = ON_SILICON_PIXEL_VALIDATED. Timing self-test PASS. No lag correction. Cadence OPEN. C1 blocked. Previous C0 corpse still FAIL. Product restored acaecaa8 im69d."
---

# Gate C0-v2 — one device epoch

Previous C0 (`artifacts/gate_c0/`) stays **FAIL — INVALID TEMPORAL EXECUTION**. Do not rescore it with +14 hops. Do not overwrite those dumps.

The two-clock runner `scripts/gate_c0_silicon.py` is **retired**. It armed rtrace and streamed PRSM on independent host clocks. That permitted `capture epoch != injection epoch` (~0.5 s).

## Invariant

Injection and capture share one authoritative **device-side epoch**.

The scorer reads from the dump, for each rendered frame:

- rtrace frame index
- device monotonic `us` and render tick
- `c0_epoch_id`
- frames since epoch
- condition id
- semantic sample index
- **actual PRSM pressure applied to this frame**
- injection-active

No host sleep, no guessed startup latency, no post-hoc hop search as authority.

No `[C0_EPOCH]` marker → `INVALID_RUN`.

A diagnostic lag search exists only as an error detector. If best-fit lag materially disagrees with declared metadata, the run is **INVALID_RUN**. It must never silently correct the score.

## Probe-only firmware

Atlas worktree branch `probe/c0-epoch-v2`. Flag `K1_C0_EPOCH_V1` on `k1_main_rpl_rtrace_probe` only.

Preload extra_gain as u16 → `:c0_run` arms rtrace, preroll, stamps epoch on a VP frame, replays the trace, post-roll, halt, dump.

Waveform Tempo source is not edited. Competing mic `waveform_peak_scaled` is held at 0 only while C0 owns the snapshot.

## Result states

| State | Meaning |
| --- | --- |
| PASS | Timing valid and Q1–Q3 pass. Stamp `ON_SILICON_PIXEL_VALIDATED`. |
| BINDING_FAIL | Timing valid, source-share carrier fails the existing bars. |
| INVALID_RUN | Marker missing, drops, sequence mismatch, lag detector trip. Not a binding fail. |

Previous C0 is this last class, while keeping its official C0 FAIL stamp.

Cadence/latency stays **OPEN** until a nominal C0-v2 PASS, then a separate small decision set.

C1 remains blocked. No new net.

## 2026-08-31 silicon

Timing self-test **PASS**.

Nominal **PASS.** Stamp:

`source_share × WaveformTempo × head_position = ON_SILICON_PIXEL_VALIDATED`

Receipt `artifacts/gate_c0v2/C0V2_RESULT.json`. Q1 Spearman 0.83; Q2 Δ 0.69 9/9; Q3 Δ 0.58 9/9. No lag correction. 0/10 clips timing-invalid. Continuous Bose Mini II SoundLink, full holdout tracks looping. Probe `349d3cd4`.

Does **not** close Gate C. C1 still blocked. Cadence/latency still OPEN. Student I/O unfrozen. No new net.

Product restored: `IDENTITY OK git=acaecaa8 env=k1_main_rpl_im69d epoch=1788136403`.

## Ship path

1. Already: C0-v2 `ON_SILICON_PIXEL_VALIDATED`; product on `acaecaa8` / `k1_main_rpl_im69d`.
2. Remaining: (a) cadence/latency as a **separate** silicon experiment, same device-epoch harness, small decision set; (b) C1 LGP perceptual only after that contract is known, or after Captain names C1 without cadence.
3. Who: agent runs cadence after a named flash GO. C1 is the first human visual judgement.
4. C1 shipped stamp: `LGP_PERCEPTUAL_VALIDATED`. Cadence shipped stamp: silicon min-rate / max-delay written into the student contract. Neither is this run.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:edgeai | Created. Retire two-clock C0. Device epoch invariant. |
| 2026-08-31 | agent:edgeai | Silicon: self-test PASS, nominal INVALID_RUN (dump drops), product restored. |
| 2026-08-31 | agent:edgeai | Chunked dump re-run PASS ON_SILICON_PIXEL_VALIDATED; product restored acaecaa8. |
