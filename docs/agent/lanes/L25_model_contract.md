---
abstract: "L25: MODEL_CONTRACT blanks vs FROZEN_FOR_C1 transport. Four NOT_MEASURED. Semantic-v0 I/O filled but UNFROZEN. Do not freeze I/O."
---

# L25 — MODEL_CONTRACT blanks vs FROZEN_FOR_C1

**HARD FAIL (`SAME_SONG_LOOP_MAX_15MIN`).** Same song/clip looped >15 min → agent dies. Cadence CLOSED. No USB.

STATUS: PASS
CLAIM: `docs/MODEL_CONTRACT.md` is a Semantic-v0 experiment sheet, not the C1 transport freeze. Honest blanks are four `NOT_MEASURED` silicon cells plus two unlocked input fields. Filled frontend/output cells are HOST-ONLY experiment values and stay **UNFROZEN**. They do not match `FROZEN_FOR_C1`. This lane did not freeze I/O.
EVIDENCE: `docs/MODEL_CONTRACT.md`; `docs/mir/SEMANTIC_TRANSPORT_CONTRACT.md`; `artifacts/gate_c0_cadence_silicon/SEMANTIC_TRANSPORT_CONTRACT.json`; `experiments/semantic_v0/AUTHORITY.md`; `docs/mir/SELECTION_GATE.md`; `docs/mir/SHARE_STUDENT.md`; L06/L24.
COMMAND: none executed. Source-read only. No train, no room audio, no `/dev/cu.usbmodem*`, no Cadence reopen.
METHOD_RISK: Title “SpectraSynq Audio Semantic Model” plus filled 16 kHz / 1 s / 64×100 / 3-sigmoid cells look like a product lock. Copying them onto C1 would drop `other`, swap share/`extra_gain` for unconstrained activity, and miss the 5 Hz floor (1 s context ≈ 1 Hz). JSON `unfrozen` lists architecture + C1 LGP only; MD still says student I/O unfrozen until C1. L03 delay-unit / MD-vs-plain caveats still bind; cadence stays CLOSED.
NEXT: Do not freeze student I/O. Do not fill U55 / CPU fallback / RAM from hope. Fill those only from silicon receipts. C1 LGP (Captain look, one full song) is the remaining freeze trigger, not this sheet.

## Split (load-bearing)

Two different contracts. Do not merge them.

| Surface | Status | What it is |
| --- | --- | --- |
| Source-ownership **transport** | **FROZEN_FOR_C1** (Captain cadence close 2026-08-31) | Four-source `extra_gain` carrier edges. Not a net. |
| Semantic-v0 **MODEL_CONTRACT** | experiment / toolchain | What a toy 3-class activity CNN filled from HOST receipts. Not architecture. |
| Share-student / Student-v0 I/O | **UNFROZEN** until SELECTION_GATE / C1 | 16 kHz, window, stride, mel, tensor, head, topology. |

JSON `status` is now `FROZEN_FOR_C1 — Captain closed cadence 2026-08-31` (reconciled vs L03’s older `PROPOSED` read). JSON `unfrozen`: `neural-network architecture`, `C1 LGP judgement`. MD: “Student I/O still unfrozen until C1.”

## Still blank / honesty tokens on MODEL_CONTRACT

No empty table cells. Honesty tokens used.

| Field | Token | Class |
| --- | --- | --- |
| U55 metrics (Performance) | `NOT_MEASURED` | silicon blank |
| This contract’s U55 accuracy/latency (under NPU coverage) | `NOT_MEASURED` | silicon blank; smoke C99 GHA 33319114336 is a **related** graph, not this net |
| CPU fallback | `NOT_MEASURED` | silicon blank |
| RAM / scratch | `NOT_MEASURED on silicon` | silicon blank |
| sample_rate | `16000 Hz (hypothesis, not product lock)` | unlocked |
| stride | `not locked; semantic lane is slower than the audio callback` | unlocked |
| tensor “quantized later” | deferred | not a U55 INT8 lock |

Filled but **not product evidence** (must not be treated as freeze): SYNTHETIC train (MUSDB_ROOT absent); HOST-ONLY FP32 MAE/F1; HOST-ONLY ORT QDQ INT8; param_count 153283; FP32/INT8 byte sizes; host infer 1.33 ms/window on M4 Pro MPS.

## Filled experiment I/O — present, still UNFROZEN

Do **not** freeze these from this sheet.

- Input: 16 kHz hypothesis, mono, float32 host / int16 golden, 1.0 s context, log-mel 25 ms / 10 ms / 64 bins / 100 frames HTK, tensor `(1, 1, 64, 100)` NCHW.
- Output: classes `vocals, drums, bass` (no `other`); `[0,1]` sigmoid **activity** (log-RMS presence, not mix share); smoothing none.
- Graph: Conv×15 Relu×15 AdaptiveAvgPool2d×1 Gemm×1 Sigmoid×1 (D11: no ReduceMean).

AUTHORITY + D8 + Amendment 001 + SELECTION_GATE: do not freeze 16 kHz / 1 s / 3 sigmoids as the RA8P1 contract.

## FROZEN_FOR_C1 (transport) — absent from MODEL_CONTRACT

These are frozen on the **carrier**, not on Semantic-v0.

| Frozen item | Transport value | On MODEL_CONTRACT? |
| --- | --- | --- |
| Channels + order | `vocals, drums, bass, other` | **No** — three activity classes, no `other` |
| Semantics | four-source powers/shares; simplex | **No** — unconstrained sigmoids, “not mix share” |
| extra_gain | `[0.62, 1.0]` | **No** |
| Silence | zeros / extra_gain stays in range; no 1/4 | **No** |
| Hold | ZOH, no interpolation, lookahead=0; hop_us=32000 | **No** |
| Slowest 0-delay PASS | **5 Hz** | **No** — 1.0 s context, stride not locked |
| Largest added delay PASS | **50 ms** at 20 Hz (requested; actual hop-quantised) | **No** |
| 5 Hz + 50 ms | **FAIL** — student must not assume both | **No** |
| 100 ms at 20 Hz | **FAIL** | **No** |
| C1 playback | C0-v2 ~31.25 Hz, 0 ms extra delay | **No** |

## Collision if anyone copied MODEL_CONTRACT onto C1

1. Drop `other` → three-source student (banned by SHARE_STUDENT).
2. Activity not share/`extra_gain`.
3. ~1 Hz window vs 5 Hz floor; 1 s context vs C1 ~31.25 Hz carrier.
4. No joint-fail awareness (L04 `r5_d50` Q1).

## What this lane did not do

Did not edit `docs/MODEL_CONTRACT.md`. Did not freeze I/O. Did not invent U55 numbers. Did not play audio. Did not open USB. Did not reopen Cadence.

AUDIO: none. `SAME_SONG_LOOP_MAX_15MIN` unused.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:grok | Inventory: four NOT_MEASURED + two unlocked; I/O unfrozen. |
| 2026-08-31 | agent:grok | Explicit split vs FROZEN_FOR_C1 transport; do not freeze I/O. |
