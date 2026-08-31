---
abstract: "Gate C OPEN. C0 FAIL INVALID_TEMPORAL_EXECUTION 2026-08-31 (two-clock race). C0-v2 is the successor harness. C1 blocked. I/O unfrozen. No more nets."
---

# Gate C — source ownership on the physical K1

Programme stamp: **Source Ownership — PRE-PRODUCT FEASIBILITY PASS.**  
Gate A PASS. Gate B HOST PASS. Recoverability HOST PASS. **Gate C OPEN.** Student I/O unfrozen. No more neural-net work until C speaks.

Binding stays exact:

`source_share × Waveform Tempo × head_position`

Not “pixels changed.” Not mean brightness.

## Effect semantics set the ML clock

Wrong: model speaks at 31.25 Hz, so the effect is fed at 31.25 Hz.  
Right: measure the lowest cadence and worst extra delay at which this binding still carries ownership, then the semantic lane is that X Hz / Y ms.

BPM, phase, tick, and confidence are different bindings, not `"supports_tempo": true`.

## C0 — `ON_SILICON_PIXEL_VALIDATED`

**2026-08-31 silicon close: FAIL — INVALID TEMPORAL EXECUTION.** Main RPL `9087A500`, probe `k1_main_rpl_rtrace_probe` @ `acaecaa8`, mode 18, palette 43, rgb16hex, P3-C scorer unchanged. Holdout n=10: Q1 **0.13** FAIL; Q2/Q3 **6/9** FAIL. Capture and PRSM injection used two clocks. Silicon response was not dead. Post-hoc +14 hops (~448 ms) recovers host-like Q1–Q3 — **diagnosis only, not a PASS, never an authority rescore.** Dumps frozen at `artifacts/gate_c0/`. The two-clock runner is **retired**. Successor: C0-v2 device epoch (`docs/mir/GATE_C0V2.md`). C1 blocked.

Feed the real K1 the same extra-DoF as P3-C: A baseline, B mix-energy, D oracle share. Gain in [0.62, 1.0] on peak + chroma. Palette path. Waveform Tempo.

Dump LED buffers (`:rtrace_dump` or the live equivalent). Score with the P3-C head-position extra-DoF test (partial r of D vs B vs share | mix). Captain is not the validator.

**Cadence / latency characterisation is a later C0-v2 subtest**, run only after a nominal C0-v2 PASS. Not part of the two-clock corpse. Not part of the first C0-v2 silicon attempt.

| Hold rate | Added delay |
| --- | --- |
| 2, 5, 10, 20, ~31 Hz | 0, 50, 100, 200 ms |

Zero-order-hold the oracle series; delay is causal. Report the slowest rate and largest delay that still clear the extra-DoF floor (P3-C holdout Δ ≥ 0.15 as the numeric floor; also ≥ ~70% of the native-rate Δ on the same clips).

A HOST rehearsal of the same holds ([GATE_C_CADENCE_HOST.md](GATE_C_CADENCE_HOST.md)) is **design evidence only**. It is not C0.

HOST holdout (n=10, native Δ 0.625): **20 Hz** still passes both floors (Δ 0.50, 80% of native). **10 Hz** is still above 0.15 (Δ 0.37) but only 60% of native. **50 ms** extra delay fails the 70% keep-rate; **200 ms** fails the 0.15 floor. Do **not** freeze 20 Hz as the student contract. C0 must re-measure on silicon.

Silicon inject + dump path: [GATE_C0_SILICON_PATH.md](GATE_C0_SILICON_PATH.md).

Shortest existing path (recon, **not** C0 PASS): USB-CDC **PRSM** Prim8 pressure = extra_gain in [0.62, 1.0] at packet rate ≥ 30 Hz → authored `peak_scaled` → Waveform Tempo head. Pin mode 18, palette 43. Dump `:rtrace_*` on **`k1_main_rpl_rtrace_probe`** only (shipping Main RPL rejects rtrace). Score `p3c_quant` head position, not MAD. Authored does **not** multiply chroma; colour is peak fallback — acceptable because the lever is position. Mic peak can swamp authored pressure — quiet room. Flash is a **named GO** of a **clean** tree, not colourlab-bench dirt. Restore product env after the dump.

Hold rates 2/5 Hz must **repeat** packets at ≥ 30 Hz (`hz` field rejects < 30). Do not put `hz=2` on the wire.

## C1 — `LGP_PERCEPTUAL_VALIDATED`

Only after C0 pixels behave. Synchronised with music. Blinded where practical. Good Light Show Taxonomy — audio must change the *right* visual dimension.

Three questions:

1. Can a viewer perceive the ownership-driven spatial change through the LGP (diffusion can hide a 12-pixel head shift)?
2. Does it correspond to musical ownership that mix energy misses?
3. Does it keep Waveform Tempo as a light show, not a clever meter?

This is the first load-bearing **human** visual judgement. Dumps still exist; they do not answer C1.

## After C passes — freeze the **semantic contract**, not the network

Then lock, with numbers from C0/C1:

- four-source semantics (vocals / drums / bass / **other** — simplex is four-way)
- powers vs normalised share on the wire
- required update cadence
- permitted extra latency
- smoothing / interpolation
- silence (no invented equal shares)
- numeric range

Then — and only then — build a causal streaming student to that contract. Do not gold-plate the 21k feasibility net first.

Then: streaming infer → quant → goldens → RUHMI/U55 → clean/live domain → Titan.

## Parked

- Hop-level / streaming student
- Demucs
- composition_change ML head
- Declaring C from host pixels

---
**Document Changelog**
| Date | Author | Change |
| --- | --- | --- |
| 2026-08-31 | agent:edgeai | C0 pixel+cadence then C1 LGP; semantics set ML clock; no NN until C. |
| 2026-08-31 | agent:edgeai | C0 silicon FAIL on Main RPL; Q1 0.13 / Q2–Q3 6/9; C1 blocked. |
| 2026-08-31 | agent:edgeai | FAIL cause = inject alignment; lagged rescore not a PASS. |
| 2026-08-31 | agent:edgeai | Stamp INVALID_TEMPORAL_EXECUTION; two-clock runner retired; C0-v2 successor. |
