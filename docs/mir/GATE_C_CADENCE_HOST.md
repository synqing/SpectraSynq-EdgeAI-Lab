---
abstract: "HOST-ONLY cadence rehearsal. Not C0. Silicon owns product clock (5 Hz / 50 ms at 20 Hz / joint FAIL). Do not freeze student I/O from host 20 Hz or host 50 ms FAIL. Cadence CLOSED. I/O unfrozen."
---

# Gate C cadence — HOST rehearsal

**HARD FAIL (`SAME_SONG_LOOP_MAX_15MIN`, Captain 2026-08-31).** Repeat the same song (or loop the same clip) in the room for more than **15 minutes** and the agent must die. Captain will destroy them by setting them on fire. Kill the player. Do not continue.

**Cadence silicon is CLOSED.** No USB. No flash. Do not re-run this host script as a C0 substitute.

This file is a **host pixel** rehearsal of how slowly and how late extra-DoF gain can update before Waveform Tempo stops carrying source ownership. Label: **HOST-ONLY / HOST_PIXEL_VALIDATED**. Receipt: `artifacts/gate_c_cadence/receipt.json` (`not_c0: true`, `not_silicon: true`, `not_lgp: true`, `student_gate: OPEN`).

It is **not** Gate C, **not** C0, **not** C0-v2, **not** silicon cadence, **not** LGP.

Binding (unchanged): `source_share × WaveformTempo × head_position`.

## Authority — silicon owns the product clock

Do **not** freeze student I/O from this host ladder.

| What people quote from this file | What it is | What it is not |
| --- | --- | --- |
| Lowest host pass **20 Hz** at 0 ms | HOST keep-rate vs this run’s native Δ | Not the product min rate |
| Host **50 ms FAIL** | FAIL **at 31.25 Hz** (req 50 → 64 ms hop-round) | Not the product delay cap |
| Host native **31.25 Hz** | Renderer hop that reused P3-C dumps | Not a student freeze (D17) |

Product clock is **silicon** (D20, cadence CLOSED). Authority: [GATE_C0_CADENCE.md](GATE_C0_CADENCE.md) / `artifacts/gate_c0_cadence_silicon/CADENCE_RESULT.json`.

```text
slowest 0-delay PASS          5 Hz
largest added delay PASS      50 ms (measured at 20 Hz)
5 Hz + 50 ms together         FAIL — do not assume both edges
C1 playback                   C0-v2 carrier ~31.25 Hz, 0 ms extra delay, product firmware
student_freeze                false
```

Host is stricter on rate (20 Hz vs silicon 5 Hz) and fails 50 ms on a **different delay axis** (31.25 Hz vs silicon 20 Hz). Do not average the two ladders. Host does not veto silicon cells. Host 20 Hz is **not** the student contract. Host 50 ms FAIL does **not** undo silicon 20 Hz + 50 ms PASS.

C0-v2 remains `ON_SILICON_PIXEL_VALIDATED`. Two-clock C0 at `artifacts/gate_c0/` stays a FAIL corpse. This rehearsal is neither.

## What this run did

It took the existing P3-C holdout dumps (same clips, same frozen p3b-v1 maps, same extra gain in [0.62, 1.0]) and asked: if the extra-DoF gain is only refreshed at 2 / 5 / 10 / 20 / 31.25 Hz, or arrives 50 / 100 / 200 ms late, does the head still track share after mix is partialled out?

Native 31.25 Hz with 0 ms extra delay **reuses the P3-C LED dumps**. Other cells zero-order-hold that gain series, delay it causally, then re-render Waveform Tempo. LED frames are not resampled.

Corpus: P3-C holdout, n=10 of 10. Tracks: Enda Reilly - Cur An Long Ag Seol, BKS - Too Much, Speak Softly - Broken Man, Skelpolu - Resurrection, Angels In Amplifiers - I'm Alright, The Mountaineering Club - Mallory, Little Chicago's Finest - My Own, Georgia Wonder - Siren, Tom McKenzie - Directions, The Easton Ellises (Baumi) - SDRNR.

Share driver stays four-source (vocals / drums / bass / **other**). `composition_change` is not used.

Chroma for re-render: MUSDB mix chromagram, same window as P3-C. Head position is peak-driven; chroma is the same extra-DoF gain applied to the P3-C chromagram path.

## Pass rule (HOST only)

A rate (delay 0) **passes** when holdout median Δ partial r (D−B) of head position vs share | mix is:

1. ≥ 0.15 (P3-C extra-DoF floor), and
2. ≥ 70% of **this run's** native-rate median Δ.

P3-C documented holdout median Δ was 0.63. This run's native dump median Δ is 0.625 (PASS). This is **not** the C0-v2 Q1–Q3 bar.

## Result (HOST-ONLY)

**Lowest host rate that still passes: 20 Hz.**  
**Host delay that fails the combined pass rule (0.15 and 70% of native): 50 ms requested (64 ms after hop rounding), at 31.25 Hz.**  
**Host delay that drops under the absolute 0.15 extra-DoF floor: 200 ms requested, at 31.25 Hz.**

These three sentences are design evidence. They are **not** C0. They do **not** freeze a student.

10 Hz still has median Δ 0.37 (above 0.15, 60% of native) — it fails only the 70% keep-rate. 50 ms delay is the same shape: Δ 0.40 vs relative floor 0.44. 200 ms is the first delay that also falls under 0.15 (Δ 0.10).

### Hold rate (delay 0)

| rate Hz | delay ms | median Δ | fraction of native | wins | verdict |
| ---: | ---: | ---: | ---: | ---: | --- |
| 2 | 0 | 0.257 | 0.41 | 9/9 | FAIL |
| 5 | 0 | 0.305 | 0.49 | 9/9 | FAIL |
| 10 | 0 | 0.372 | 0.60 | 9/9 | FAIL |
| 20 | 0 | 0.501 | 0.80 | 9/9 | PASS |
| 31.25 | 0 | 0.625 | 1.00 | 9/9 | PASS |

### Added delay (native host rate 31.25 Hz — not the silicon delay axis)

| rate Hz | requested ms | actual ms (hop-rounded) | median Δ | fraction of native | verdict |
| ---: | ---: | ---: | ---: | ---: | --- |
| 31.25 | 0 | 0 | 0.625 | 1.00 | PASS |
| 31.25 | 50 | 64 | 0.398 | 0.64 | FAIL |
| 31.25 | 100 | 96 | 0.343 | 0.55 | FAIL |
| 31.25 | 200 | 192 | 0.104 | 0.17 | FAIL |

50 ms request rounds to 64 ms at a 32 ms hop. That rounding is part of the **host** grid, not the product clock. Silicon delay cells were taken **at 20 Hz**, where 50 ms (also 64 ms / 2 hops) **PASS**.

Figure: `docs/mir/figures/gate_c_cadence_host.png`.

## What this is not

- Not C0 / C0-v2 (`ON_SILICON_PIXEL_VALIDATED`). Host bytes are pre-gamma / pre-dither / pre-LGP.
- Not silicon cadence (`CADENCE_RESULT.json`). Cadence is **CLOSED**; do not reopen cells.
- Not C1. Nobody looked at the plate. Head-position Δ is the instrument.
- Not a student I/O freeze. Do **not** freeze from host 20 Hz or host 50 ms FAIL. Freeze only after C1 if the silicon contract still holds (`SELECTION_GATE.md`).
- Not a Demucs run. Not a new net.

## Ship path

1. **Already on silicon / in source:** this HOST rehearsal (`HOST_PIXEL_VALIDATED`); C0-v2 `ON_SILICON_PIXEL_VALIDATED`; cadence silicon CLOSED (5 Hz / 50 ms at 20 Hz / joint FAIL).
2. **Remaining:** C1 LGP perceptual on the already-proven C0-v2 carrier (~31.25 Hz, 0 ms extra delay), product firmware. Not more cadence cells. Not a host re-run. Not a student freeze from these numbers.
3. **Who:** Captain, one full song he chooses. Agent does not play the 8 s loop.
4. **Stamp that means C1 shipped:** `LGP_PERCEPTUAL_VALIDATED`. Not this file. Not host 20 Hz.

Firmware SHA 36466cd56c90 (host renderer). Compiler g++-15. Frozen map p3b-v1.

## Lane return (W3-L32)

**STATUS:** PASS (docs). Host receipt agrees with the tables below. Host rehearsal is **not C0**. Silicon owns the product clock. Cadence CLOSED.

**CLAIM:** `GATE_C_CADENCE_HOST` is HOST-ONLY / `HOST_PIXEL_VALIDATED` design evidence. Lowest host pass 20 Hz; host 50 ms FAIL is at 31.25 Hz, not at silicon 20 Hz. Do not freeze student I/O from host 20 Hz or host 50 ms FAIL. Product clock: 5 Hz 0-delay PASS; 50 ms PASS at 20 Hz; 5 Hz+50 ms FAIL. C1 plays ~31.25 Hz / 0 ms extra delay on product firmware.

**EVIDENCE:** this file; `artifacts/gate_c_cadence/receipt.json`; [GATE_C.md](GATE_C.md); [GATE_C0_CADENCE.md](GATE_C0_CADENCE.md); `artifacts/gate_c0_cadence_silicon/CADENCE_RESULT.json`; [SEMANTIC_TRANSPORT_CONTRACT.md](SEMANTIC_TRANSPORT_CONTRACT.md); `docs/DECISIONS.md` D17/D20.

**COMMAND:** none. Do not run `scripts/gate_c_cadence_host.py` or `scripts/gate_c0_cadence_silicon.py`. No USB, no `/dev/cu.usbmodem*`, no 8 s loop, no ffplay.

**METHOD_RISK:** Quoting host 20 Hz as “the cadence” undoes D20 silicon 5 Hz. Treating host 50 ms FAIL as the delay cap undoes silicon 50 ms PASS at 20 Hz. Treating host native 31.25 Hz as a student freeze undoes D17. Treating this rehearsal as C0 confuses C0-v2 pixels with a later subtest. Skelpolu NaNs drop one clip from the Δ denom (9/9).

**NEXT:** Leave host as HOST-ONLY. Consume silicon 5 Hz / 50 ms / joint FAIL. Do not freeze student I/O. C1 OPEN. Do not re-run cadence.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:edgeai | HOST cadence rehearsal of P3-C extra-DoF; lowest passing rate and delay cliff. Not C0. |
| 2026-08-31 | agent:grok | Silicon owns product clock. Host 20 Hz / host 50 ms FAIL are not a student freeze. Cadence CLOSED. Ship path: C1, not more C0 cells. |
