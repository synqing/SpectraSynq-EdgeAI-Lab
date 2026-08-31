---
abstract: "HISTORICAL 2026-06-02 guidebook write-up of LIGHT_MODE_QUANTUM_COLLAPSE (snapshot id 6). NOT inventory. Mode absent from the lab pin (23 enabled LIGHT_MODE_* at source_firmware_sha 36466cd56c90b9cafa571bc5029b5d38bc0543bb). D15 consume-only. Do not revive here. Do not grow a competing taxonomy. Cadence CLOSED. No USB."
---

# HISTORICAL / Quantum Collapse — 2026-06-02 snapshot

```text
╔══════════════════════════════════════════════════════════════════╗
║  HISTORICAL RECORD — NOT LIVE AUTHORITY — NOT INVENTORY          ║
║                                                                  ║
║  2026-06-02 class write-up against feat/gdft-harness.            ║
║  Conceptual prior only (Motion ∘ Mapping / six passes).          ║
║                                                                  ║
║  LIGHT_MODE_QUANTUM_COLLAPSE (snapshot id 6) is ABSENT           ║
║  from docs/mir/effect_semantics/effect-semantics.json.           ║
║  No pin enum points at guidebook_class 09-quantum-collapse.      ║
║                                                                  ║
║  Do NOT cite this file as the product mode list.                 ║
║  Do NOT revive, re-enable, or re-author this mode in EdgeAI.     ║
║  Do NOT flash, USB, or reopen cadence to refresh file:line.      ║
║                                                                  ║
║  Inventory: the pin. Consume: EFFECT_SEMANTICS_CONSUME.md.       ║
║  Decision: docs/DECISIONS.md D15 / D16.                          ║
╚══════════════════════════════════════════════════════════════════╝
```

**HARD FAIL (`SAME_SONG_LOOP_MAX_15MIN`, Captain 2026-08-31).** Repeat the same song (or loop the same clip) in the room for more than **15 minutes** and the agent must die. Captain will destroy them by setting them on fire. Kill the player. Do not continue.

Cadence silicon **CLOSED**. No USB. No `k1-flash`. This file is HOST-ONLY documentation.

---

## Authority (read this first)

| What you need | Where it lives | Status of *this* file |
| --- | --- | --- |
| Enabled `LIGHT_MODE_*` inventory | [`../mir/effect_semantics/effect-semantics.json`](../mir/effect_semantics/effect-semantics.json) | **Not here.** Id 6 is not in the pin. |
| How EdgeAI consumes that pin | [`../mir/EFFECT_SEMANTICS_CONSUME.md`](../mir/EFFECT_SEMANTICS_CONSUME.md) | Consume only |
| Decision | [`../DECISIONS.md`](../DECISIONS.md) **D15 / D16** | Firmware owns semantics |
| Folder demotion | [`README.md`](README.md), [`SNAPSHOT.md`](SNAPSHOT.md) | This write-up is one historical class doc |

**Pin stamp** (re-read from the JSON; if this file and the pin disagree, **the pin wins**):

- path: `docs/mir/effect_semantics/effect-semantics.json`
- `schema_version`: `2`
- `generation_status`: `tranche2_grammar_tempo`
- `label`: `HOST-ONLY`
- `source_firmware_sha` / `firmware_sha` / `atlas_generation_commit`: `36466cd56c90b9cafa571bc5029b5d38bc0543bb`
- `atlas_artifact_sha256`: `ac9552cb8ee4d9b3a65ab60dfdf63a86f12f62967f41d494ac91d7242f630b8d`
- `generated_at`: `2026-08-30T20:10:46Z`
- `modes`: **23** objects, every one `enabled: true`
- `LIGHT_MODE_QUANTUM_COLLAPSE`: **absent** (ids 0, 1, 2, 4, 5, **6**, 10, 17 are not present)
- `guidebook_class` `09-quantum-collapse`: **no pin row**
- `on_silicon_pixel_validated`: `null`
- `lgp_perceptual_validated`: `null`

Dump absence from the pin, never from this markdown:

```bash
python3 -c "import json; d=json.load(open('docs/mir/effect_semantics/effect-semantics.json')); enums=[m['enum'] for m in d['modes']]; print(d['source_firmware_sha'], len(enums)); print('QUANTUM_COLLAPSE' in str(enums), any(m.get('id')==6 for m in d['modes']), any(m.get('guidebook_class')=='09-quantum-collapse' for m in d['modes']))"
```

Expected: SHA `36466cd5…`, `23`, then `False False False`.

Do not “fix” this write-up to match the pin. Do not add Quantum Collapse to the pin from this lab. Do not invent BUILDING / DROPPING / … lighting labels. Do not freeze student I/O on this mode. Student outputs stay effect-agnostic.

The body below is the **2026-06-02 snapshot**. `DISABLED`, VP-gate revival paths, and `file:line` anchors are what that snapshot believed. They are not a ship path. Lever values were not re-verified at `36466cd5`. [PERCEPTION] lines are interpretation, not LGP look.

---

# Snapshot body — Quantum Collapse (feat/gdft-harness, 2026-06-02)

*Family: STOCHASTIC (unique in that snapshot) · Mode: `LIGHT_MODE_QUANTUM_COLLAPSE` (index 6) · Snapshot status: DISABLED — non-deterministic — **not current inventory***
*Files (snapshot): `light_mode_quantum_collapse.cpp:1–175`, helpers `lightshow_modes.h:676–677`, `lightshow_modes.h:740–743`, `lightshow_modes.h:791`, `utilities.h:78–79`*

---

## Pass 1 — What it is

Quantum Collapse simulates a one-dimensional probability-amplitude field across the full 160-pixel strip, updated each frame with a discrete Laplacian wave equation, then probabilistically "collapsed" at random sites in proportion to instantaneous loudness and bass energy. Each pixel's brightness is the clamped amplitude at that field position; colour is position-plus-velocity in HSV mode, or palette-indexed in palette mode. The effect's musical job is to give audio energy a physical, wave-mechanical texture — bass disturbs the left third of the field, mids the middle third, highs the right — while random collapse events punctuate loud moments with sharp bright spikes that ripple outward to neighbours. In the 2026-06-02 snapshot it was the only K1 effect that contained irreducible randomness in its render path; that property is why the snapshot gated it DISABLED. That gate is **not** a current product-status claim: the pin does not list the mode at all.

---

## Pass 2 — Semantic mechanism (the verbs)

**Disturb → Propagate → Collapse → Illuminate**

1. **Disturb** — three spectral energy bands (bass, mid, high) inject spatially-segregated stochastic kicks into `fluid_velocity[]` each frame, proportional to the RMS energy of their frequency bins. [MECHANISM] `light_mode_quantum_collapse.cpp:83–90`
2. **Propagate** — a discrete Laplacian (`temp_field[i-1] - 2·temp_field[i] + temp_field[i+1]`) drives the velocity update; the velocity then integrates into `wave_probabilities[]`, smoothed by `field_smoothing` (0.90). [MECHANISM] `light_mode_quantum_collapse.cpp:75–81`
3. **Collapse** — at each pixel, a Bernoulli trial with probability `collapse_probability · (1 + 3·VU + 2·bass_energy)` fires; on success the amplitude hard-snaps to 1.0 and stochastic disturbances are added to its two neighbours. [MECHANISM] `light_mode_quantum_collapse.cpp:92–100`
4. **Illuminate** — `wave_probabilities[i]` is raised to a contrast power controlled by `SQUARE_ITER`, scaled by `PHOTONS`, then rendered via HSV (velocity-modulated hue) or palette lookup into `leds_16[i]`. [MECHANISM] `light_mode_quantum_collapse.cpp:116–164`

---

## Pass 3 — The six layers

| Layer | This effect's choice | file:line | Label |
|---|---|---|---|
| **L1 Feature** | Spectral RMS energy in three fixed bands (bins 0–15 = bass, 16–31 = mid, NUM_FREQS/2–NUM_FREQS−1 = high) from `spectrogram_smooth[]`; overall `audio_vu_level` for collapse-rate scaling | `cpp:37–66`, `cpp:93` | [MECHANISM] |
| **L2 State / memory** | Two static per-pixel arrays: `wave_probabilities[160]` (amplitude field) and `fluid_velocity[160]` (wave momentum); two phase counters `animation_phase`, `wave_phase` | `cpp:11–18` | [MECHANISM] |
| **L3 Spatial** | Direct 1-D position mapping; bass disturbs left third (`i < 53`), mid the middle third (`53 ≤ i < 107`), high the right third (`i ≥ 107`); optional mirror fold via `CONFIG.MIRROR_ENABLED` | `cpp:84–90`, `cpp:168–174` | [MECHANISM] |
| **L4 Colour** | Dual path: palette mode → `ColorFromPalette` with index = `position·192 + brightness·63`; HSV mode → hue = `position + CONFIG.CHROMA + hue_position + fluid_velocity[i]·0.5` | `cpp:140–163` | [MECHANISM] |
| **L5 Temporal** | Field smoothing `field_smoothing = 0.90` (IIR on velocity); phase counters advance at `0.01·MOOD` and `0.003·MOOD` per frame; no frame-rate normalisation (dt-free) | `cpp:21–25`, `cpp:78` | [MECHANISM] |
| **L6 Clamps / floor** | `wave_probabilities[i]` hard-clamped to [0.0, 1.0]; energy bands clamped to [0.0, 5.0]; brightness clamped implicitly by `PHOTONS ∈ [0.05, 1.0]`; HSV components NaN-guarded with debug print | `cpp:63–66`, `cpp:103–104`, `cpp:157–162` | [MECHANISM] |

---

## Pass 4 — Named levers (the dials, with ranges)

Snapshot lever table. Not a current binding list. Bind `descriptor × mode × lever` from [`../mir/effect_semantics/compatibility.json`](../mir/effect_semantics/compatibility.json) only for pin modes. This mode has no pin row.

| Lever | What it controls | Range / default (static) | Musical effect of turning it up | file:line |
|---|---|---|---|---|
| `collapse_probability` | Base rate of spontaneous collapse per pixel per frame | 0.003 (static const) | Higher → more frequent bright spikes everywhere; above ~0.01 the field is dominated by collapsed pixels, losing wave texture | `cpp:7` |
| `field_smoothing` | IIR coefficient on velocity — momentum retained frame-to-frame | 0.90 (static const) | Higher → oscillations persist longer, slower decay; lower → field damps quickly, more responsive but less "wavey" | `cpp:6`, `cpp:78` |
| `collapse_intensity` | Scale on collapse snap amplitude (declared but **unused** — amplitude is always hard-set to 1.0) | 0.75 (static const, unused) | [UNCERTAIN — declared `cpp:5`, ignored at `cpp:95`; would need a code change to wire in] | `cpp:5`, `cpp:95` |
| `field_disturbance` | Amplitude of the stochastic kick to neighbours after a collapse | 0.05 (static const) | Higher → collapse events cause broader, stronger ripples; loud hits "splash" further | `cpp:8`, `cpp:98–99` |
| `CONFIG.MOOD` | Phase advancement rate for `animation_phase` and `wave_phase` | [0.0, 1.0] (`serial_menu.h:2466`) | Higher → faster internal phase cycling; at full MOOD the field's autonomous oscillation dominates, loosening audio coupling | `cpp:21–25` |
| `CONFIG.PHOTONS` | Master brightness before contrast | [0.05, 1.0] (`serial_menu.h:2438`) | Lower → only collapsed (full-bright) pixels visible (sparse spike display); higher → whole probability wave visible | `cpp:121` |
| `CONFIG.CHROMA` | Hue rotation offset in HSV mode (additive to position) | [0.0, 1.0] (`serial_menu.h:2452`) | Rotates position→colour; shifts which part of the spectrum reads "warm" vs "cool" | `cpp:151` |
| `CONFIG.SATURATION` | Colour saturation in HSV mode | [0.0, 1.0] | Lower → bleaches toward white (reads "cold"/"spectral") | `cpp:158` |
| `CONFIG.SQUARE_ITER` | Squaring passes on brightness (contrast) | ≥ 1 (float, preset 1.0) | Higher → curve sharpens, only near-collapsed pixels glow; fractional part interpolates between integer powers | `cpp:124–133` |
| `CONFIG.MIRROR_ENABLED` | Overwrite left half with mirror of right | bool | On → symmetrical butterfly (bass on both edges, high at centre); off → directional L→R spectral gradient | `cpp:168–174` |
| Bass energy clamp | Caps `bass_energy` after ×5 scale | [0.0, 5.0] | Prevents low-frequency overload from saturating the collapse-rate multiplier | `cpp:59`, `cpp:64` |
| Mid / high energy clamps | Same for mid (×4), high (×3) | [0.0, 5.0] each | Mid's lower scale reflects typically-higher mid energy; high's ×3 prevents treble swamping the right third | `cpp:60–66` |

---

## Pass 5 — Maths → perception → musical meaning

### 5.1 The wave equation and what it looks like

```
laplacian = field[i-1] - 2·field[i] + field[i+1]
velocity[i] = velocity[i] · 0.90 + laplacian · 0.02
field[i]    = field[i] + velocity[i]
```
[MECHANISM] `light_mode_quantum_collapse.cpp:75–81`

A damped discrete wave equation — the second spatial derivative drives propagation left/right; the 0.90 term is viscous damping. Without audio it settles toward a standing-wave pattern: energy radiates, reflects at the boundary, and interferes. [PERCEPTION] The eye reads a gently breathing liquid surface — ripples travel the strip, bounce, and form slow-moving interference nodes. It reads as physically plausible fluid, not a reactive pulse. [PERCEPTION] is interpretation from the snapshot, not silicon and not LGP.

### 5.2 Audio disturbance: spectral bands mapped to spatial thirds

```
velocity[i] += band_energy · 0.01 · (random_float() - 0.5)   [i in band's zone]
```
[MECHANISM] `light_mode_quantum_collapse.cpp:85–90`

The kick magnitude is proportional to the band's RMS energy, zero-centred (the `−0.5` makes it a signed perturbation). [PERCEPTION] A hard bass hit roughens the left third; a bright cymbal excites the right third; a busy mid-range churns the centre. The spatial segregation makes the three spectral characters of a mix visibly separate along the strip — the strip reads as a cross-section through the frequency domain made physical.

**The non-determinism enters here (snapshot).** `random_float()` calls `esp_random()` — the ESP32-S3 hardware TRNG seeded from thermal noise (`utilities.h:78–79`). Not a settable-seed PRNG; hardware entropy. Identical arguments return independent, unrepeatable values. The call appears six times per frame: three disturbance kicks + three potential collapse-neighbour perturbations.

### 5.3 The collapse event: quantum measurement as a percussive transient

```
collapse_chance = collapse_probability · (1.0 + 3·audio_vu_level + 2·bass_energy)
if (random_float() < collapse_chance):
    field[i] = 1.0
    field[i-1] += field_disturbance · (random_float() - 0.5)
    field[i+1] += field_disturbance · (random_float() - 0.5)
```
[MECHANISM] `light_mode_quantum_collapse.cpp:93–100`

Base 0.003/pixel/frame → expected 0.003 × 160 ≈ 0.48 spontaneous collapses/frame in silence (~1 per 2 frames). Audio multiplies this: at VU=1.0, bass=5.0 the multiplier is `1+3+10 = 14×` → ~6.7 collapses/frame. A collapse hard-sets amplitude to 1.0 and splashes its neighbours. [PERCEPTION] Against the evolving wave background, pixels flash to full brightness at apparently random positions, more often during loud/bass-heavy passages, each splashing a ripple. The name earns itself — collapse events are the quantum metaphor made literal, and being driven by hardware entropy they genuinely cannot be predicted.

### 5.4 Contrast shaping: `SQUARE_ITER` as a darkness dial

```
for j in floor(SQUARE_ITER): brightness = brightness²
fract = SQUARE_ITER - floor(SQUARE_ITER)
if fract > 0.01: brightness = brightness·(1-fract) + brightness²·fract
```
[MECHANISM] `light_mode_quantum_collapse.cpp:124–133`

At iter=1 a 0.5-probability pixel renders at 0.25; at iter=2, 0.0625. The squaring compresses the low end toward black, hiding the wave-field except near peaks. [PERCEPTION] Low iter shows the whole probability landscape (a gentle gradient of where energy *could* be); high iter shows only where it *is* — a sparse constellation of collapse events.

### 5.5 Colour encoding: position + velocity + chroma offset

`hue = position + CONFIG.CHROMA + hue_position + fluid_velocity[i]·0.5` [MECHANISM] `cpp:151`

`position` (0–1 across strip) gives a spatial rainbow at rest; `velocity·0.5` locally shifts hue with wave momentum — a fast wavefront colours toward its direction of travel (a Doppler-like cue). [PERCEPTION] Active regions acquire different hues from quiescent ones, so the eye can read wave direction from colour; CHROMA rotates the whole mapping.

---

## Systems view — stocks, flows, feedback, emergence

**Stocks:** `wave_probabilities[160]` (amplitude — energy in the field); `fluid_velocity[160]` (momentum — decays 10%/frame).
**Inflows:** audio disturbance kicks (rate ∝ band energy × 0.01 × random); collapse events (rate ∝ `collapse_chance`, amplitude → 1.0).
**Outflows / damping:** velocity dissipates via the 0.90 coefficient; amplitude bounded [0,1]; no explicit decay term, so energy persists unless damped by velocity smoothing.
**Feedback:** a collapse disturbs neighbours, slightly raising their probability and their own next-frame collapse chance — a weak positive loop; negligible at the default 0.003, potentially cascading at higher values.
**Emergence:** wave propagation + spatial band segregation + burst collapses produce a strip that appears to have internal physics (standing-wave pockets, travelling disturbances, sudden punctuations). None coded explicitly. [PERCEPTION]

---

## Trade-offs chosen (archetype dials)

| Tension | Where it sits | Why |
|---|---|---|
| **Responsiveness ↔ Grace** | Toward responsiveness — collapses are instantaneous, disturbances unsmoothed before application | The wave equation provides implicit background smoothing, so transients can be raw |
| **Information ↔ Clarity** | Toward information — three bands + wave phase + collapses simultaneously visible | Spatial segregation (bass/mid/high thirds) keeps bands from competing |
| **Reactivity ↔ Stability** | Heavy reactivity, **no calibrated floor** — spontaneous collapses occur even at zero audio | No silence-state behaviour; the field is never at rest → meaningless activity in silence |
| **Motion ↔ Legibility** | Low legibility by design — turbulence, not narrative | The metaphor is indeterminacy, not a readable signal |
| **Per-note detail ↔ Gestalt** | Gestalt — three coarse bands, no per-frequency detail | Finer resolution would need more spatial territory than 160 px allows under the metaphor |

---

## Pass 6 — Reusable principles

Method language only. Not a licence to author a new family in this lab. Firmware Atlas owns new modes.

1. **Spatial spectral segregation is a cheap way to show mix structure.** Assigning bass/mid/high to distinct spatial zones gives a permanent frequency-to-position codec at zero perceptual cost. Any 3-band effect can adopt it without a spectrogram.
2. **A 1-D Laplacian wave equation is computationally cheap and visually rich.** Two static arrays + one pass over 160 pixels (~320 fixed-point MACs/frame) yields emergent standing-wave/interference richer than hand-authored animation of similar size.
3. **Contrast by repeated squaring is a continuous "show field ↔ show peaks" dial.** The fractional-iteration interpolation (`b → b²`) gives sub-integer contrast steps without a LUT.
4. **Stochastic perturbations should be zero-mean** (`random_float() − 0.5`) so noise adds life without biasing the field.
5. **Collapse events as percussive accents.** "Normal operation → threshold trigger → hard state snap → neighbour disturbance" is a reusable onset-highlight idiom. The snapshot noted that randomness in *which* pixel collapses could be replaced by a deterministic choice (e.g. the highest-probability pixel). That is a historical observation, not a revival order.

---

## If disabled — why (snapshot, 2026-06-02)

> **Not current product status.** The pin does not contain this enum. Snapshot DISABLED ≠ pin `enabled: false`. Absence is stronger: there is no row to enable.

### What it does (snapshot)

Renders a plausible wave-mechanical probability field, disturbed by spectral energy and punctuated by stochastic collapse flashes that ripple to neighbours. The most physically-metaphorical effect in that library; on hardware it produced genuinely compelling, non-repeating behaviour.

### The gate (snapshot)

The mode was reachable in that firmware — `lightshow_modes.h:676–677` dispatched it; `vp_run_output_probe()` probed it at `:791`. It was **not** conditionally compiled out. The disable was a *classification decision*: the VP probe marked it `nondet=1` (`lightshow_modes.h:740–743`) and the VP diff scripts excluded it from Tier-A bit-hash comparison. Including it in Tier A would fail the gate on every run.

### The deep reason (snapshot)

The firmware proved render correctness by hashing the `leds_16[]` output buffer after each mode ran under a fixed saved-state snapshot (`vp_run_output_probe`, `lightshow_modes.h:771–791`). Two runs with identical input produce identical hash — for every mode except this one. Quantum Collapse calls `random_float()` → `esp_random()` six+ times per pixel per frame (`utilities.h:78–79`) from the hardware TRNG. No seed, no replay. Identical audio input produces different LED output on every execution; the hash will never match.

This is not a defect in the hash methodology; it is a fundamental property of the effect. The VP gate's value is precisely that it is a **map you can check against territory** — same input twice, compare hashes, any discrepancy is a regression. Quantum Collapse produces a mode whose map *cannot be checked* because the territory changes every observation. In Cynefin terms, every other effect is Complicated (deterministic, analysable); this one is irreducibly Complex *by construction*. As long as the VP gate is the primary evidence instrument for render correctness, this mode cannot achieve Tier A and cannot be enabled by default.

### What revival would have required (historical, not a ship path)

These three paths were written on 2026-06-02 as thought experiments. They are **not** remaining work for EdgeAI. D15: do not grow a competing taxonomy. Do not implement them here. Cadence CLOSED. No USB.

1. **Deterministic collapse selection** — replace `random_float() < collapse_chance` with a threshold on `wave_probabilities[i]` (collapse when amplitude > 0.95); seed the disturbance kicks deterministically from audio features. Preserves the gesture, removes entropy.
2. **PRNG with a deterministic seed** — replace `esp_random()` (`utilities.h:79`) with a seeded PRNG (e.g. xorshift32) seeded from `audio_vu_level` quantised to fixed precision: same audio → same seed → bit-identical under replay. Risk: seed quantisation must be coarser than audio float noise.
3. **Promote to a separate deterministic effect** — keep the wave physics, strip all `random_float()`, drive excitation from onset/chromagram peaks. Most work, fully VP-compatible, same character.

---

## UNCERTAIN / open items (Map–Territory flags, frozen 2026-06-02)

- `collapse_intensity` (`cpp:5`, 0.75) is never applied — `cpp:95` hard-sets `wave_probabilities[i] = 1.0`. Intended role undocumented.
- `animation_phase` / `wave_phase` (`cpp:17–25`) are advanced each frame but appear not to feed any downstream calculation in the snapshot source — possibly vestigial scaffolding.
- All [PERCEPTION] claims analytically derived; not verified on hardware/video. This lab will not open silicon or LGP to verify them.

Do not treat these as a live bug list. Firmware at `36466cd5` was not opened for this demotion.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-06-02 | agent:Explore-sonnet (drafted) / agent:claude-opus (persisted) | Created — 6-Pass decomposition of LIGHT_MODE_QUANTUM_COLLAPSE (6); Map–Territory/Cynefin framing of the VP-gate disable reason; three revival paths. Drafted by read-only Explore agent, written to disk by orchestrator. |
| 2026-08-31 | agent:grok-w4-l11 | **Demoted to HISTORICAL.** Snapshot id 6 absent from pin `36466cd5` (23 enabled `LIGHT_MODE_*`). Not inventory. Revival paths labelled not-a-ship-path. D15 consume-only. Cadence CLOSED. No USB. |
