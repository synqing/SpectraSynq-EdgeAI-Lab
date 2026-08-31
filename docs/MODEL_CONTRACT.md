---
abstract: "Student I/O UNFROZEN. Semantic-v0 HOST sheet is not FROZEN_FOR_C1. Do not copy 16 kHz / 1 s / 3-sigmoid onto C1. Transport freeze lives in SEMANTIC_TRANSPORT_CONTRACT."
---

# Model contract — I/O unfrozen

**HARD FAIL (`SAME_SONG_LOOP_MAX_15MIN`, Captain 2026-08-31).** Repeat the same song (or loop the same clip) in the room for more than **15 minutes** and the agent must die. Captain will destroy them by setting them on fire. Kill the player. Do not continue.

**This file is not `FROZEN_FOR_C1`.** The cadence-closed C1 carrier freeze is `docs/mir/SEMANTIC_TRANSPORT_CONTRACT.md` plus `artifacts/gate_c0_cadence_silicon/SEMANTIC_TRANSPORT_CONTRACT.json`. Do not merge them.

Student I/O stays **UNFROZEN** until `docs/mir/SELECTION_GATE.md` is satisfied **and** C1 LGP speaks (`docs/mir/GATE_C.md`). Gate A PASS, Gate B HOST PASS, share-student recoverability HOST PASS, and this Semantic-v0 sheet do **not** freeze a net.

Cadence silicon is **CLOSED**. No USB from this document. No 8 s loop.

## Authority split

| Surface | Status | Owns |
| --- | --- | --- |
| Source-ownership **transport** | **`FROZEN_FOR_C1`** (Captain 2026-08-31) | Four-source `extra_gain` carrier edges. Not a net. |
| Student / RA8P1 **I/O** | **UNFROZEN** | Rate, window, stride, frontend, tensor, head, topology. |
| Semantic-v0 **sheet** (below) | experiment / toolchain | HOST-ONLY 3-class activity CNN on synthetic stems. Not architecture. |
| Share-student 21k CNN | HOST recoverability PASS | Four-source share including `other`. Experiment graph, not a lock. |

JSON `unfrozen` lists `neural-network architecture` and `C1 LGP judgement`. Canonical unfrozen set is this file + `docs/mir/SHARE_STUDENT.md` + `docs/mir/SELECTION_GATE.md`, not that two-line array.

## Do not copy onto C1

Do **not** copy Semantic-v0 `16 kHz` / `1.0 s` / 3 unconstrained sigmoids (`vocals, drums, bass`) onto C1, RA8P1, or the transport contract.

If anyone did:

1. Drop `other` → three-source student (banned by `docs/mir/SHARE_STUDENT.md`).
2. Swap four-source share / `extra_gain [0.62, 1.0]` for unconstrained log-RMS **activity**.
3. Put a ~1 Hz global pool against a **5 Hz** 0-delay floor; 1 s context against C1 playback at **~31.25 Hz / 0 ms**.
4. Miss the joint cell: **5 Hz + 50 ms FAIL** (`student_must_not_assume` both edges).

C1 playback is the already-proven C0-v2 carrier on product firmware. Binding stays `source_share × Waveform Tempo × head_position`. Oracle on silicon was MUSDB four-source share → `extra_gain`, **not** this net.

Transport values (pointer only — this file does not freeze them):

| Frozen on the **carrier** | Value |
| --- | --- |
| Channels + order | `vocals, drums, bass, other` |
| Semantics | four-source powers/shares; simplex; silence is zeros, not 1/4 |
| extra_gain | `[0.62, 1.0]` |
| Hold | ZOH; no interpolation; lookahead = 0; `hop_us` = 32000 |
| Slowest 0-delay PASS | **5 Hz** |
| Largest added delay PASS | **50 ms** at 20 Hz (requested; hop-quantised on device) |
| 5 Hz + 50 ms | **FAIL** |
| 100 ms at 20 Hz | **FAIL** |
| C1 playback | C0-v2 ~31.25 Hz, 0 ms extra delay |

## Unfrozen — student I/O

Not a product lock. Do not fill from hope.

| Field | Status |
| --- | --- |
| sample_rate | UNFROZEN (16 kHz is an **experiment** frontend, not RA8P1) |
| window / context | UNFROZEN (1.0 s is experiment; AdaptiveAvgPool2d((1,1)) → ~1 s latency) |
| stride / hop | UNFROZEN |
| frontend (mel / STFT / hop / bins / frames) | UNFROZEN |
| tensor layout | UNFROZEN (`(1, 1, 64, 100)` NCHW is experiment) |
| head | UNFROZEN (3-sigmoid activity ≠ 4-source share) |
| topology / param count | UNFROZEN |
| descriptors that become Student-v0 | UNFROZEN (`SELECTION_GATE`) |
| U55 / CPU fallback / RAM of **this** net | `NOT_MEASURED` until a silicon receipt of this graph |

Amendment 001 superseded “freeze 16 kHz / 1 s / 64-mel now.” D8: MIR-first; Semantic-v0 is not architecture authority. D3/D4 host-frontend numbers are the experiment graph; D3 revisit is explicit.

## Semantic-v0 experiment sheet (HOST-ONLY, not C1)

**Not** named “SpectraSynq Audio Semantic Model.” **Not** `FROZEN_FOR_C1`. Filled cells are receipts, still **UNFROZEN**. Blank silicon cells stay `NOT_MEASURED`. Invented numbers are forbidden.

Authority: `experiments/semantic_v0/AUTHORITY.md`. Registry id `semantic-v0-experiment`. Graph keep: `src/edgeai/semantic_v0.py` as a U55-shaped **toy**. Do not train it as the default programme. Do not quote synthetic F1 as musical intelligence.

Fill from `experiments/semantic_v0_synth/receipt.json` and `artifacts/export/quant_report.json`.

### Identity

| Field | Value |
| --- | --- |
| name | Semantic-v0 (experiment / toolchain witness) |
| version | v0 — not Student-v0, not RA8P1 |
| purpose | Estimate vocal/drum/bass **activity** from a short mixed window. Additive modulation probe. DSP remains the product path if this graph is absent. |

### Input — experiment values, UNFROZEN

| Field | Experiment value | Freeze? |
| --- | --- | --- |
| sample_rate | 16000 Hz | **no** — hypothesis, not product lock |
| channels | 1 | **no** |
| PCM | float32 host / int16 WAV golden | **no** |
| context | 1.0 s | **no** — do not copy onto C1 |
| stride | not locked; this lane is slower than the audio callback | **no** |
| frontend | log-mel, 25 ms window, 10 ms hop, 64 bins, 100 frames, HTK mel, log(power+1e-6), clip [-12, 6] | **no** |
| tensor | `(1, 1, 64, 100)` NCHW float32 (host INT8 later is not MERA/U55) | **no** |

### Output — experiment values, UNFROZEN

| Field | Experiment value | Freeze? |
| --- | --- | --- |
| classes | `vocals`, `drums`, `bass` — **no `other`** | **no** — C1 carrier is four-source |
| range | `[0, 1]` sigmoid activity | **no** |
| interpretation | log-RMS **presence** of that stem in the window. Not mix share. Not `extra_gain`. Not a one-shot event. | **no** |
| smoothing | none in v0 | **no** |

### Performance — HOST-ONLY synthetic, not product evidence

| Field | Value |
| --- | --- |
| train corpus | SYNTHETIC (`MUSDB_ROOT` absent). See `datasets/README.md` |
| val/test | song-level 34 / 6 / 8, `datasets/manifests/synthetic_v0.json` |
| FP32 metrics | HOST-ONLY synthetic test n=64: vocals MAE 0.101 F1 1.00; drums MAE 0.229 F1 0.67; bass MAE 0.054 F1 1.00. **Not product evidence.** Vocals/bass F1=1.0 because the generator is spectrally easy. |
| host INT8 metrics | HOST-ONLY ORT QDQ, n=48, macro MAE 0.137 → 0.134. Not MERA. Not U55. |
| U55 metrics | **NOT_MEASURED** |

### Deployment — this graph unmeasured on silicon

| Field | Value |
| --- | --- |
| param_count | 153 283 (experiment) |
| FP32 size | 613 132 B weights; 613 727 B ONNX |
| host INT8 ONNX | 213 240 B |
| live graph | Conv×15 Relu×15 **AdaptiveAvgPool2d×1** Gemm×1 Sigmoid×1 (BN folded). D11: do **not** export ReduceMean. The 2026-08-30 dump `docs/onnx_graph_semantic_v0.json` still lists ReduceMean — stale vs live `src/edgeai/semantic_v0.py`. |
| NPU coverage | Related **smoke** graph only: PRE-SILICON C99 on GHA 33319114336 (88.9% node coverage, 8 CPU nodes). This contract’s U55 accuracy/latency: **NOT_MEASURED**. Not ON-SILICON. Do not promote smoke 88.9% as Semantic-v0 U55. |
| CPU fallback | **NOT_MEASURED** |
| RAM / scratch | **NOT_MEASURED** on silicon |
| host infer | 1.33 ms / 1 s window on M4 Pro MPS — not U55 |

## Failure behaviour

If the semantic experiment is absent, corrupt, delayed, or disabled:
**deterministic SpectraSynq DSP and the visual engine remain functional.**
v0 is an additive lane. That additive rule is load-bearing. The I/O numbers above are not.

## What would freeze I/O (not this sheet)

1. `SELECTION_GATE` closed on descriptor, rate/context, teacher, licences, and U55 of the **chosen** student.
2. C1 LGP on one full song Captain chooses (no 8 s loop).
3. A written freeze of the student graph that **meets the transport edges** (exclusive envelope: 5 Hz @ 0 ms **or** 20 Hz @ 50 ms — never AND). HOST sketches may exist; they are not a freeze.

Until then: honest blanks, experiment receipts, I/O unfrozen.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-30 | agent:edgeai | Created; filled first HOST-ONLY synthetic measurements. |
| 2026-08-31 | agent:edgeai | Pooling is AdaptiveAvgPool2d; smoke C99 is not U55 product metrics. |
| 2026-08-31 | agent:grok | Split vs FROZEN_FOR_C1; I/O unfrozen; do not copy 16 kHz / 1 s / 3-sigmoid onto C1. |
