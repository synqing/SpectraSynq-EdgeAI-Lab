---
abstract: "C0-v2 ON_SILICON_PIXEL_VALIDATED. Cadence CLOSED Captain 2026-08-31 (5 Hz / 50 ms; joint 5+50 FAIL). C1 OPEN. I/O unfrozen. No more nets."
---

# Gate C — source ownership on the physical K1

**HARD FAIL (`SAME_SONG_LOOP_MAX_15MIN`, Captain 2026-08-31).** Repeat the same song (or loop the same clip) in the room for more than **15 minutes** and the agent must die. Captain will destroy them by setting them on fire. Kill the player. Do not continue.

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

**Live stamp (2026-08-31): C0-v2 PASS — `ON_SILICON_PIXEL_VALIDATED`.** Method: [GATE_C0V2.md](GATE_C0V2.md). Receipt `artifacts/gate_c0v2/C0V2_RESULT.json`. Binding `source_share × Waveform Tempo × head_position`. `lag_corrected: false`. Holdout n=10: Q1 **0.83** PASS; Q2 Δ **0.69** 9/9 PASS; Q3 Δ **0.58** 9/9 PASS. Probe `k1_main_rpl_rtrace_probe` @ `349d3cd4`. C1 is **OPEN**.

### Two-clock corpse (historical, not live)

**2026-08-31 two-clock C0: FAIL — INVALID TEMPORAL EXECUTION.** Frozen at `artifacts/gate_c0/`. Main RPL `9087A500`, probe `k1_main_rpl_rtrace_probe` @ `acaecaa8`. Holdout n=10: Q1 **0.13** FAIL; Q2/Q3 **6/9** FAIL. Capture and PRSM injection used two clocks. Silicon response was not dead. Post-hoc +14 hops (~448 ms) recovers host-like Q1–Q3 — **diagnosis only, not a PASS, never an authority rescore.** Do **not** quote this FAIL as the current C0 close. The two-clock runner is **retired**. Successor is C0-v2 above.

Feed the real K1 the same extra-DoF as P3-C: A baseline, B mix-energy, D oracle share. Gain in [0.62, 1.0] on peak + chroma. Palette path. Waveform Tempo.

Dump LED buffers (`:rtrace_dump` or the live equivalent). Score with the P3-C head-position extra-DoF test (partial r of D vs B vs share | mix). Captain is not the validator.

**Cadence / latency silicon is CLOSED** Captain 2026-08-31. Receipt: [GATE_C0_CADENCE.md](GATE_C0_CADENCE.md) / `artifacts/gate_c0_cadence_silicon/CADENCE_RESULT.json`. Do not reopen cells. Do not play the 8 s loop.

```text
5 Hz @ 0 ms PASS (slowest useful 0-delay)
50 ms extra at 20 Hz PASS
100 ms at 20 Hz FAIL (Q1)
200 ms at 20 Hz FAIL
5 Hz + 50 ms FAIL (Q1)
10 Hz + 25 ms NOT COMPLETED — do not interpolate
```

Zero-order-hold the oracle series; delay is causal. A student must **not** assume 5 Hz **and** 50 ms together.

A HOST rehearsal of the same holds ([GATE_C_CADENCE_HOST.md](GATE_C_CADENCE_HOST.md)) is **design evidence only**. It is not C0. Do **not** freeze student I/O from the host 20 Hz / host 50 ms FAIL numbers. Silicon owns the product clock.

Silicon inject + dump path: [GATE_C0_SILICON_PATH.md](GATE_C0_SILICON_PATH.md).

Shortest existing path (recon, **not** C0 PASS): USB-CDC **PRSM** Prim8 pressure = extra_gain in [0.62, 1.0] at packet rate ≥ 30 Hz → authored `peak_scaled` → Waveform Tempo head. Pin mode 18, palette 43. Dump `:rtrace_*` on **`k1_main_rpl_rtrace_probe`** only (shipping Main RPL rejects rtrace). Score `p3c_quant` head position, not MAD. Authored does **not** multiply chroma; colour is peak fallback — acceptable because the lever is position. Mic peak can swamp authored pressure — quiet room. Flash is a **named GO** of a **clean** tree, not colourlab-bench dirt. Restore product env after the dump.

Hold rates 2/5 Hz must **repeat** packets at ≥ 30 Hz (`hz` field rejects < 30). Do not put `hz=2` on the wire.

## C1 — `LGP_PERCEPTUAL_VALIDATED`

**OPEN.** Cadence CLOSED Captain 2026-08-31. Method: [GATE_C1.md](GATE_C1.md). No 8 s holdout loop.

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

- Product streaming-student freeze (HOST sketch OPEN; I/O unfrozen)
- Demucs on Titan (HOST teacher docs OPEN; weights UNKNOWN; no download)
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
| 2026-08-31 | agent:grok | C0-v2 PASS; cadence Captain-closed; C1 OPEN. |
| 2026-08-31 | agent:grok | SAME_SONG_LOOP_MAX_15MIN HARD FAIL. |
| 2026-08-31 | agent:grok | C0 body: two-clock FAIL labelled corpse; live stamp C0-v2 PASS; cadence CLOSED numbers. |
