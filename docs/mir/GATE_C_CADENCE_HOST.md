---
abstract: "HOST-ONLY cadence of source_share × WaveformTempo × head_position. Lowest passing hold 20 Hz; 50 ms fails 70%-of-native; 200 ms fails 0.15. Not C0. I/O unfrozen."
---

# Gate C cadence — HOST rehearsal

This is a **host pixel** rehearsal of how slowly and how late the extra control can update before Waveform Tempo stops carrying source ownership. It is **not** Gate C, **not** C0, **not** silicon, **not** LGP.

Binding (unchanged): `source_share × WaveformTempo × head_position`.

Label: **HOST-ONLY / HOST_PIXEL_VALIDATED**. Student I/O is still OPEN.

## What this run did

It took the existing P3-C holdout dumps (same clips, same frozen p3b-v1 maps, same extra gain in [0.62, 1.0]) and asked: if the extra-DoF gain is only refreshed at 2 / 5 / 10 / 20 / 31.25 Hz, or arrives 50 / 100 / 200 ms late, does the head still track share after mix is partialled out?

Native 31.25 Hz with 0 ms extra delay **reuses the P3-C LED dumps**. Other cells zero-order-hold that gain series, delay it causally, then re-render Waveform Tempo. LED frames are not resampled.

Corpus: P3-C holdout, n=10 of 10. Tracks: Enda Reilly - Cur An Long Ag Seol, BKS - Too Much, Speak Softly - Broken Man, Skelpolu - Resurrection, Angels In Amplifiers - I'm Alright, The Mountaineering Club - Mallory, Little Chicago's Finest - My Own, Georgia Wonder - Siren, Tom McKenzie - Directions, The Easton Ellises (Baumi) - SDRNR.

Share driver stays four-source (vocals / drums / bass / **other**). `composition_change` is not used.

Chroma for re-render: MUSDB mix chromagram, same window as P3-C. Head position is peak-driven; chroma is the same extra-DoF gain applied to the P3-C chromagram path.

## Pass rule

A rate (delay 0) **passes** when holdout median Δ partial r (D−B) of head position vs share | mix is:

1. ≥ 0.15 (P3-C extra-DoF floor), and
2. ≥ 70% of **this run's** native-rate median Δ.

P3-C documented holdout median Δ was 0.63. This run's native dump median Δ is 0.625 (PASS).

## Result

**Lowest rate that still passes: 20 Hz.**  
**Delay that fails the combined pass rule (0.15 and 70% of native): 50 ms requested (64 ms after hop rounding).**  
**Delay that drops under the absolute 0.15 extra-DoF floor: 200 ms requested.**

10 Hz still has median Δ 0.37 (above 0.15, 60% of native) — it fails only the 70% keep-rate. 50 ms delay is the same shape: Δ 0.40 vs relative floor 0.44. 200 ms is the first delay that also falls under 0.15 (Δ 0.10).

### Hold rate (delay 0)

| rate Hz | delay ms | median Δ | fraction of native | wins | verdict |
| ---: | ---: | ---: | ---: | ---: | --- |
| 2 | 0 | 0.257 | 0.41 | 9/9 | FAIL |
| 5 | 0 | 0.305 | 0.49 | 9/9 | FAIL |
| 10 | 0 | 0.372 | 0.60 | 9/9 | FAIL |
| 20 | 0 | 0.501 | 0.80 | 9/9 | PASS |
| 31.25 | 0 | 0.625 | 1.00 | 9/9 | PASS |

### Added delay (native rate)

| rate Hz | requested ms | actual ms (hop-rounded) | median Δ | fraction of native | verdict |
| ---: | ---: | ---: | ---: | ---: | --- |
| 31.25 | 0 | 0 | 0.625 | 1.00 | PASS |
| 31.25 | 50 | 64 | 0.398 | 0.64 | FAIL |
| 31.25 | 100 | 96 | 0.343 | 0.55 | FAIL |
| 31.25 | 200 | 192 | 0.104 | 0.17 | FAIL |

50 ms request rounds to 64 ms at a 32 ms hop. That rounding is part of the host grid, not a product clock.

Figure: `docs/mir/figures/gate_c_cadence_host.png`.

## What this is not

- Not C0 (`ON_SILICON_PIXEL_VALIDATED`). Host bytes are pre-gamma / pre-dither / pre-LGP.
- Not C1. Nobody looked at the plate. Head-position Δ is the instrument.
- Not a student I/O freeze. Cadence numbers here are **design evidence** for a later contract, if C0/C1 pass.
- Not a Demucs run. Not a new net.

## Ship path

1. Already in source: this HOST rehearsal plus the P3-C dumps it reused.
2. Remaining: C0 silicon LED dumps of the same extra-DoF at these holds/delays; then C1 LGP perceptual.
3. Who: a named Captain GO to flash / dump on the physical K1. Not this script.
4. Shipped for C0 means silicon dumps scored with the same Δ floor, stamped `ON_SILICON_PIXEL_VALIDATED`.

Firmware SHA 36466cd56c90. Compiler g++-15. Frozen map p3b-v1.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:edgeai | HOST cadence rehearsal of P3-C extra-DoF; lowest passing rate and delay cliff. Not C0. |
