---
abstract: "Historical 2026-06-02 levers matrix. NOT the firmware pin. LIVE/DISABLED and Gap #1 (sb_tempo unconsumed) are snapshot claims. Inventory is docs/mir/effect_semantics/effect-semantics.json (23 LIGHT_MODE_* @ 36466cd5). D15 consume-only. Do not grow a competing taxonomy."
---

# Effect Levers Matrix — historical 2026-06-02 synthesis, not inventory

**HARD FAIL (`SAME_SONG_LOOP_MAX_15MIN`, Captain 2026-08-31).** Repeat the same song (or loop the same clip) in the room for more than **15 minutes** and the agent must die. Captain will destroy them by setting them on fire. Kill the player. Do not continue.

> **This file is not the product mode list, not the current lever map, and not a build roadmap.** It is the **2026-06-02** cross-effect synthesis from class docs 01–09 (`feat/gdft-harness`). It used to present a 9-class LIVE/DISABLED table and seven generative gaps as what to ship next. Those claims are **withdrawn as current**. The only allowed inventory in this lab is the firmware pin below.

Cadence silicon is **CLOSED**. No USB. No `k1-flash`. Do not author Cannonade / Shockwave / Iris / Implosion / Chladni / Meniscus here. Do not invent BUILDING / DROPPING lighting labels. Students stay effect-agnostic.

---

## Authority (read this first)

| What you need | Where it lives | Status of *this* file |
| --- | --- | --- |
| Enabled `LIGHT_MODE_*` inventory | [`../mir/effect_semantics/effect-semantics.json`](../mir/effect_semantics/effect-semantics.json) | **Not here** |
| How EdgeAI consumes that pin | [`../mir/EFFECT_SEMANTICS_CONSUME.md`](../mir/EFFECT_SEMANTICS_CONSUME.md) | Consume only |
| `descriptor × mode × lever` rows | [`../mir/effect_semantics/compatibility.json`](../mir/effect_semantics/compatibility.json) | Not here |
| Visual-grammar coverage | [`../mir/effect_semantics/grammar_coverage.json`](../mir/effect_semantics/grammar_coverage.json) | Not here |
| Decision | [`../DECISIONS.md`](../DECISIONS.md) **D15 / D16** | Firmware owns semantics |
| Folder demotion | [`README.md`](README.md), [`SNAPSHOT.md`](SNAPSHOT.md) | Same demotion |
| Conceptual method (old map) | [`00-the-method.md`](00-the-method.md), class `01`–`09`, this file | Historical |

**Pin stamp** (re-read from the JSON; if this file and the pin disagree, **the pin wins**):

- path: `docs/mir/effect_semantics/effect-semantics.json`
- `schema_version`: `2`
- `generation_status`: `tranche2_grammar_tempo`
- `label`: `HOST-ONLY`
- `source_firmware_sha` / `firmware_sha` / `atlas_generation_commit`: `36466cd56c90b9cafa571bc5029b5d38bc0543bb`
- `atlas_artifact_sha256`: `ac9552cb8ee4d9b3a65ab60dfdf63a86f12f62967f41d494ac91d7242f630b8d`
- `generated_at`: `2026-08-30T20:10:46Z`
- `modes`: **23** objects, every one `enabled: true`, **23** distinct `LIGHT_MODE_*` enums
- `on_silicon_pixel_validated`: `null`
- `lgp_perceptual_validated`: `null`

Dump the inventory from the pin, never from the LIVE/DISABLED table below:

```bash
python3 -c "import json; d=json.load(open('docs/mir/effect_semantics/effect-semantics.json')); print(d['source_firmware_sha'], len(d['modes']));
[print(m['id'], m['enum'], m['guidebook_class'], m['guidebook_fit'], bool(m.get('tempo_fields')), 'onset' if 'onset_beat' in m.get('native_inputs',[]) else '-', m['evidence']) for m in d['modes']]"
```

If the lab pin and the firmware Atlas generated files disagree: **delete the pin and recopy**. Do not “fix” mode behaviour by rewriting these tables into a second taxonomy.

---

## What this file is

A **2026-06-02** synthesis: Motion ∘ Mapping separability across the *then* library, six-layer columns, owned primitives, archetype dials, and a TRIZ gap list. Useful as **conceptual prior** for talking about *how an effect is built* (engine family, sample seam, named lever).

Read it the way you read an old schematic. It does not tell you what is on the board today.

Captured against `feat/gdft-harness`. Class-doc `file:line` anchors in those write-ups will have drifted; verify against firmware at `36466cd5` before quoting. `guidebook_fit` on the pin says whether a class write-up still describes that mode.

The 2026-06-02 link to `docs/waveform-mode-design-rationale.md` **does not exist in this lab**. Do not recreate it. Historical Waveform write-up here is [`01-waveform-class.md`](01-waveform-class.md).

---

## What this file is not

- **Not inventory.** Do not cite the §0 LIVE/DISABLED column, “9 classes”, or “18 modes / 10 live / 8 disabled” as the current product list.
- **Not a generative roadmap.** The §5 gaps are a 2026-06-02 probe list. They are not a firmware build queue and not an EdgeAI authoring list.
- **Not Gap #1 as current.** “`sb_tempo` built but consumed by nothing” is **false on the pin**. See stale-claims table.
- **Not “Comet is the only onset consumer.”** False on the pin.
- **Not `supports_tempo: true`.** Tempo is not one lever. Bind `beat_phase × LIGHT_MODE_WAVEFORM_TEMPO × transport_position` (or the named pin lever), never a boolean.
- **Not student I/O.** A student may emit `vocals_share` / `drums_share` / …. It must not emit “Waveform Tempo head position”. Binding is a separate layer (`descriptor × mode × lever`).
- **Not silicon / LGP evidence.** `[PERCEPTION]` cells are interpretation. Pin `HOST_PIXEL_VALIDATED` is host LED-buffer, pre-gamma, pre-dither. Cadence CLOSED. This file is HOST-ONLY documentation.

---

## Snapshot vs pin (do not “fix” the tables to match)

The pin’s `guidebook_class` field is the **only** allowed pointer from current inventory → these historical write-ups. Do not add class docs for pin modes with `guidebook_class: null`. Firmware Atlas owns that map.

Re-derived from the pin (JSON wins if this table drifts):

| Snapshot claim in this file (2026-06-02) | Pin (`36466cd5`, 23 enabled) |
| --- | --- |
| LIVE/DISABLED 9-class map (ids 0–17) as library census | **23** enabled `LIGHT_MODE_*`; ids **0,1,2,4,5,6,10,17 absent** |
| Every LIVE effect separable; every DISABLED fused or static | Predictive lens on *that* LIVE/DISABLED set. The pin’s 23 enabled modes are **not** classified LIVE/DISABLED by those nine classes |
| Gap #1: entire beat/tempo-phase row empty; `sb_tempo` unconsumed | **Withdrawn.** Non-empty `tempo_fields` on WAVEFORM_TEMPO 18, TEMPO_RIVER 19, TEMPO_COMET 20, DENSE_FORGE 21, SNAPWAVE 22, PULSE_PRISM 23, DENSE_FORGE_CHORD 24, TEMPO_COMET_ANTICIPATE 27, TEMPO_RIVER_WALK 29 |
| Gap #2: onset drives only Comet spawn | **Withdrawn as “sole consumer.”** `onset_beat` also on DENSE_FORGE 21, PULSE_PRISM 23, DENSE_FORGE_CHORD 24, PERCUSSION_BURST 26 (COMET 13 still listed) |
| Waveform Tempo (18) missing / roadmap | `enabled` true, `guidebook_fit` `CURRENT_CHANGED`, `evidence` `HOST_PIXEL_VALIDATED` |
| GDFT 0/1/2, VU 10/4, Kaleidoscope 5, Quantum 6, Ember V2 17 as DISABLED library members | Those ids **not present** in the pin |
| Structure row empty except director switching; BUILDING/DROPPING as effect names | Do **not** invent lighting labels. MIR structure words are not a second mode taxonomy |
| “Read when deciding what to build next” | Do not author families in this lab. Consume the pin |

`HOST_PIXEL_VALIDATED` on this pin (host LED-buffer, not LGP): BLOOM, WAVEFORM, COMET, SPECTRUM_RIVER, EMBER, WAVEFORM_TEMPO, PULSE_PRISM. Everything else in the pin is `STATIC_SOURCE`.

[`00b-captivation-transposition.md`](00b-captivation-transposition.md) already noted (2026-07-11) that “tempo unconsumed” was stale. This file’s Gap #1 text below is **kept as historical wording** so the snapshot can be read; it is not current.

Need a mode, a lever, or a test binding? Stop. Open the pin and [`../mir/EFFECT_SEMANTICS_CONSUME.md`](../mir/EFFECT_SEMANTICS_CONSUME.md). Query `compatibility.json`. Reject `INCOMPATIBLE` / `INCOMPATIBLE_FOR_THIS_USE`. Prefer `HOST_PIXEL_VALIDATED` over `STATIC_SOURCE`. Score the named lever, never mean brightness by default.

---

# Historical body — captured 2026-06-02

*Derives from class docs [01](01-waveform-class.md), [02](02-bloom-class.md)–[09](09-quantum-collapse.md). Status columns are what the snapshot believed then.*

The original framing (“once every effect is reduced, the gaps become the roadmap”) is **retired**. Gaps below are a 2026-06-02 means-set reading, not a ship list. See [`00-the-method.md`](00-the-method.md) for the framework these tables apply.

---

## 0 · Motion ∘ Mapping across the 2026-06-02 library — the separability map

Per [`00-the-method.md`](00-the-method.md) §1, every effect factors as **Motion ∘ Mapping**. Applying that root lens across the *snapshot* library is the coarsest partition in this file. **Separability as a design lens still holds.** “Separability predicts shippability / LIVE = separable / DISABLED = fused” is a finding about **this table’s LIVE/DISABLED set**, not a census of the pin’s 23 enabled modes.

| Effect (mode) | Motion engine | Mapping (audio → sample) | Separable? | Status (snapshot 2026-06-02) |
|---|---|---|---|---|
| Waveform / Fast (8/7) | **Transport**: scroll + reactive-fade + draw | amp→position, chromagram→colour | ✓ clean | LIVE |
| Waveform-Hybrid (11) | **Transport**: centre-out scroll + fade | raw-audio-shape seed + chromagram→colour | ✓ clean (richer sample) | LIVE |
| Bloom / Bloom-Fast (3/9) | **Transport**: centre-out scroll + alpha-fade | chromagram→colour (+ energy→spread) | ✓ clean | LIVE |
| Aurora (12) | **Transport**: full-strip scroll + alpha | chromagram→colour-in-motion | ✓ clean | LIVE |
| Spectrum River (14) | **Transport**: `draw_sprite` advection + alpha | frequency→position, frequency→palette | ✓ clean | LIVE |
| Spectrum River V2 (15) | **Transport**: advection, drift-speed param-mapped | + low_energy→drift-speed (param-mod, not a new sample) | ✓ clean | LIVE |
| Comet (13) | **Particle**: integrate + life-decay + draw | bass_onset→spawn(velocity/size/hue) | ✓ clean (particle engine) | LIVE |
| Ember (16) | **Transport**: scroll + alpha; drift∝energy | energy→reach/brightness, centroid→hue | ✓ clean | LIVE |
| *Ember removed shimmer* | *autonomous phase inside the motion layer* | *free-running, non-audio* | **✗ violates pure-transport** | REMOVED |
| GDFT family (0/1/2) | **Static**: instant redraw, ≈no memory | spectrum→pixel (≈1:1) | degenerate (motion ≈ empty) | DISABLED |
| VU / VU-Dot (10/4) | **Static**: bar redraw + level EMA | broadband RMS→bar length | degenerate (minimal motion) | DISABLED |
| Kaleidoscope (5) | **Field**: Perlin noise field (coupled) | band energy→field excitation | ✗ fused | DISABLED |
| Quantum Collapse (6) | **Field**: wave PDE + stochastic collapse (coupled) | band/VU→disturbance + collapse-rate | ✗ fused (+ non-deterministic) | DISABLED |

**The 2026-06-02 pattern (historical):** every **LIVE** row in *this* table is **separable** (Transport or Particle). Every **DISABLED** row is either **degenerate** (Static) or **fused** (Field). [MECHANISM on snapshot status; [PERCEPTION] on the quality verdicts that drove the then-disables — see each class doc's "If disabled — why".] Do not retarget this paragraph onto the pin.

**Motion-engine families — reusable half of the means-set (still the method language):**

- **Transport** — scroll/advect a buffer, fade it, draw new samples in. Snapshot workhorse (7 live rows). Owns "constant refresh" structurally → Organic-Law clause 1 for free.
- **Particle** — integrate a small pool of moving objects (`pos += vel`), decay life, draw. Best for discrete/onset events (Comet in the snapshot). Owns object identity.
- **Field** *(handle with care)* — a spatially-coupled dynamical system. Rich, but fuses the layers → four failure modes (untunable, screensaver, indirect causality, unverifiable). **No live row in the snapshot uses it.** That is not a licence to revive Quantum/Kaleidoscope in this lab.
- **Static** *(avoid standalone)* — near-instant redraw, no transport. Honest but flat (the GDFT/VU "oscilloscope" problem).

**Why the lens earned root status in 2026-06-02 (kept as method, not census).** The separability lens was *predictive* for that LIVE/DISABLED cut: it explained *why* those disabled effects were disabled (structure, not taste), and it yields a go/no-go before a line is written — *can you name the `{where, colour, intensity}` sample? If not, you are in Field territory.* The honest boundary: the law is *root for the separable (transport/particle) regime, and its breakdown defines a hard road* — which is stronger than "all effects separate." **It is not a statement that the pin’s 23 enabled modes are all Transport.**

---

## 1 · The layer matrix — what every snapshot effect chooses

Each row is a choice of the six layers *as written in class docs 01–09 on 2026-06-02*. Read a column to see how one design decision (e.g. "what drives colour?") varied across **that** library. `[MECHANISM]` throughout — every cell traces to the cited class doc, not to the pin.

| Effect (mode) | Family | L1 Feature(s) | L3 Spatial | L4 Colour | L5 Temporal | Status (snapshot) |
|---|---|---|---|---|---|---|
| **Waveform** (8) | WAVEFORM | peak envelope + chromagram | amplitude → position; scroll | chromagram centroid / palette / HSV-shift | EMA 0.08; fade `1−0.10·|amp|`; 1px scroll | LIVE |
| **Waveform-Fast** (7) | WAVEFORM | peak + chromagram | same | same | EMA 0.05; dt scroll ≤8px | LIVE |
| **Waveform-Hybrid** (11) | WAVEFORM | peak + VU + **raw audio history** | centre-origin; real-shape seed | chromagram blend | dt fade (inverted); dt scroll | LIVE |
| **Bloom / Bloom-Fast** (3/9) | BLOOM | chromagram | centre-origin outward scroll | 3-tier (palette / chromatic / HSV) | MOOD→speed; alpha 0.99 (Fast = 2× shift) | LIVE |
| **Aurora** (12) | BLOOM | chromagram | centre-origin, full-strip fill | `effect_palette_or_chroma_colour` | alpha ~0.98 | LIVE |
| **Spectrum River** (14) | WAVEFORM/spectrum | 80-bin spectrum | **bin → pixel (freq = space)**; outward | frequency → palette hue | drift 0.55; alpha 0.90 | LIVE |
| **Spectrum River V2** (15) | WAVEFORM/spectrum | spectrum + `low_energy` | same | same | **tide-EMA drift** (0.05); alpha 0.90 | LIVE |
| **Comet** (13) | particle | **bass_onset event** + strength | **particle pool** position (6/ch) | fixed palette-class hue (0.04) | life-decay 0.018; trail 0.05; MOOD→velocity | LIVE |
| **Ember** (16) | glow | `spectral_energy` + chromagram centroid | centre-origin **reach** (energy→extent) | centroid + spread 0.18 | drift+surge; alpha 0.88 | LIVE |
| **GDFT** (0) | raw-spectral | 80-bin spectrum | bin → pixel (≈1:1) | 3 colour engines | minimal — no memory/motion | DISABLED |
| **Chromagram Gradient** (1) | raw-spectral | 12 chroma | position → bin | position-driven hue | minimal | DISABLED |
| **Chromagram Dots** (2) | raw-spectral | 12 chroma | dot pairs at `0.5 ± mag` | note-index palette | minimal | DISABLED |
| **VU** (10) | level-meter | broadband RMS | centre-origin bar | `chroma_val+hue` or palette | level EMA; peak decay ×0.9999 | DISABLED |
| **VU Dot** (4) | level-meter | broadband RMS | dot position | same | + 2nd EMA on position | DISABLED |
| **Kaleidoscope** (5) | generative-noise | 3 band energies (low/mid/high) | **Perlin noise field** | RGB-per-band | Perlin-walk speed; brightness decay 0.99 | DISABLED |
| **Quantum Collapse** (6) | stochastic | 3 bands + VU | **wave field**, 3 spatial thirds | position+velocity HSV / palette | Laplacian + stochastic collapse | DISABLED |

**What the columns revealed in 2026-06-02:**

- **L4 Colour was dominated by harmony.** Almost every live row mapped *pitch/chromagram* to colour. Concentration, not current census.
- **L3 Spatial is where those rows differed most.** Amplitude→position (Waveform), freq→position (River), energy→extent (Ember), particle-pool (Comet), noise-field (Kaleidoscope), wave-field (Quantum). Spatial layer as identity axis is method language, still usable.
- **L1 Feature concentrated on chromagram + energy.** Onset used by exactly one live row in this table (Comet). Beat/tempo phase by **none in this table**. That last sentence is **why Gap #1 existed then**. It is not true of the pin.

---

## 2 · The owned-primitive inventory (Effectuation means-set, 2026-06-02)

Per `00-the-method.md` §5, new effects *in that guidebook* were recombinations of owned primitives. This is the bird-in-hand inventory **the snapshot** claimed the library had already paid for. It is **not** a current Atlas `static_levers.json` (that file is **not** in this lab pin).

| Column | Owned primitives (the means, snapshot) |
|---|---|
| **Spatial** | centre-origin scroll · outward scroll · up-scroll · static mirror · bin→pixel (freq=space) · particle pool (6/ch) · Perlin noise field · 1-D wave field · energy→reach (extent) · spatial band-thirds |
| **Colour** | chromagram centroid → hue · frequency → palette position · 33-palette LUT · forced-HSV auto-shift · RGB-per-band · fixed palette-class hue · position → hue · velocity → hue · harmonic edge-mix (6 modes, *secondary only*) |
| **Temporal** | EMA smoothing (any coeff) · amplitude-linked fade · energy-linked drift/surge · life-decay (particles) · dt-scaled scroll · tide-EMA (slow energy integral) · Laplacian wave · peak-follower-with-decay |
| **Feature** | chromagram (12) · GDFT spectrum (80-bin) · VU/peak envelope · novelty/flux · low/mid/high band energy · `spectral_energy` · onset + bass-onset events · **(then-latent) BPM + beat-phase** · **(then-latent) spectral centroid** |
| **Guards** | calibrated silence floor · `clamp01` · VU failsafe · per-channel state isolation · drift floor (no-stop) · multi-detector seed gate |

**Then-latent means (historical):** BPM/beat-phase (`sb_tempo`, computed but *then* consumed by nothing) and spectral centroid/flux (computed, used only for hue auto-shift and the removed Ember shimmer). TRIZ resource analysis said: *spend the resources you already own before adding new ones.* **Spend-status of tempo is now the pin, not this paragraph.**

---

## 3 · Archetype dials — where each snapshot effect sits

From `00-the-method.md` §4. Shows the *then* library's aggregate bias. Not a pin classification.

| Effect | Responsive↔Grace | Information↔Clarity | Reactivity↔Stability | Per-note↔Gestalt |
|---|---|---|---|---|
| Waveform / Fast | grace | clarity | stable (floor) | mixed (chromagram colour) |
| Waveform-Hybrid | grace | **information** (shape+colour) | stable (3-gate) | mixed |
| Bloom / Aurora | grace | clarity | stable | gestalt |
| Spectrum River | grace | tunable (SQUARE_ITER) | stable (floor) | **per-note** at high iter |
| Comet | **responsive** (onset) | clarity | stable (salience gate) | gestalt (one class: kick) |
| Ember | grace | clarity | very stable | gestalt |
| GDFT family | responsive | **information** (raw) | none (no floor logic) | **per-note** (max) |
| VU family | mixed | **clarity** (minimal) | stable | gestalt (amplitude only) |
| Kaleidoscope | grace | information | stable | gestalt |
| Quantum Collapse | responsive | information | **none** (no silence floor) | gestalt |

**Reading the 2026-06-02 aggregate:** the live rows clustered in *grace + clarity + stable*. The **"responsive/punchy/per-note"** corner was thinly populated (only Comet and high-iter River in this table). [PERCEPTION — corner-coverage is an interpretation of the dial table, pending viewing. Not a licence to author a new family in EdgeAI.]

---

## 4 · The TRIZ map — musical dimension × visual primitive (2026-06-02)

Rows = musical dimensions extracted. Columns = visual primitives. A filled cell = a snapshot effect already did this. An empty cell was a *then* candidate. **Empty cells in this table are not current white space** — check `native_inputs` / `tempo_fields` / `compatibility.json` on the pin.

| Musical dimension ↓ / drives → | Position | Colour/hue | Brightness | Motion / scroll-speed | Persistence / trail | Spawn / event |
|---|---|---|---|---|---|---|
| **Dynamics** (energy/VU/peak) | Waveform, Ember, VU | — | Ember, VU | River-V2, Ember | Waveform (fade) | Quantum (collapse rate) |
| **Pitch / harmony** (chromagram) | GDFT, Chroma-grad | **Waveform, Bloom, Ember, River, Hybrid** (saturated) | GDFT | — | — | — |
| **Timbre** (centroid / flux / novelty) | — | Ember (centroid); hue-shift (novelty) | — | — | — | — |
| **Rhythm — onset** (onset/bass-onset) | Comet | (visual-hooks: chroma, global) | (visual-hooks: photons, global) | — | — | **Comet** |
| **Rhythm — beat/tempo phase** (BPM) | — | — | — | — | — | — |
| **Structure** (build/drop/breakdown) | — | — | — | — | — | (Director *switches*, no self-mod) |

**The empty cells told the 2026-06-02 story.** Two rows were almost entirely blank — **beat/tempo phase (completely empty in this table)** and **structure** — and the **timbre** row was nearly blank. Pitch→colour was saturated (five effects). That reading is **historical**. The beat/tempo row is **not empty on the pin**. The structure row is **not** an invitation to invent BUILDING/DROPPING as lighting-mode names.

---

## 5 · Ranked generative gaps — 2026-06-02 probe list, not a ship queue

Each gap named: the empty cell, the TRIZ separation it filled, and the owned primitives it recombined. **Do not treat this section as firmware work remaining, and do not implement these recombinations in this lab.**

> **Method remainder (still valid as language):** a gap is almost always a missing **mapping**, not a missing motion engine — cheapest build *would be* a new mapping on an owned Transport or Particle engine, never a new Field. If a proposed effect *can't* be phrased as "owned engine + new mapping," treat that as a warning flag (`00-the-method` §1.4). **Authoring the mapping is firmware’s job.**

### Gap #1 — Beat/tempo-phase-locked motion — **WITHDRAWN as current**

- **2026-06-02 claim:** the entire *beat/tempo-phase* row empty; `sb_tempo` already computes BPM, beat-phase (0–1), confidence, `beat_tick` — and **nothing consumes it** (`sb_tempo.h:17`).
- **Pin (current):** that unconsumed claim is **false**. Non-empty `tempo_fields` on WAVEFORM_TEMPO 18, TEMPO_RIVER 19, TEMPO_COMET 20, DENSE_FORGE 21, SNAPWAVE 22, PULSE_PRISM 23, DENSE_FORGE_CHORD 24, TEMPO_COMET_ANTICIPATE 27, TEMPO_RIVER_WALK 29. Bind named fields (`tempo.phase`, `tempo.bpm`, `tempo.beat_tick`, …), never `supports_tempo`.
- **Historical recombinations (not a build list):** scroll-speed locked to BPM; trail-reset / colour-advance on `beat_tick`; pulse or symmetry-flip on the downbeat; Comet velocity quantised to the beat. Do not add Cannonade/Shockwave/Iris to “claim this axis.”
- **Why it was #1 then:** largest unused signal in the snapshot, already built, beat-sync as a legible cue. [PERCEPTION on legibility; MECHANISM on 2026-06-02 availability.] [`00b`](00b-captivation-transposition.md) corrected the unused claim on 2026-07-11.

### Gap #2 — Onset stream beyond Comet — **WITHDRAWN as “sole live onset consumer”**

- **2026-06-02 claim:** onset drives only Comet's spawn + (globally) the visual-hooks layer.
- **Pin (current):** `onset_beat` also on DENSE_FORGE 21, PULSE_PRISM 23, DENSE_FORGE_CHORD 24, PERCUSSION_BURST 26. COMET 13 still has `onset_beat`.
- **Historical recombinations (not a build list):** onset→ripple; onset→palette-advance; onset→symmetry-flip; onset→brightness-flash overlay.

### Gap #3 — Structure-aware self-modulation — **do not invent lighting labels**

- **2026-06-02 claim:** Smart-Director’s 7-state classification (silence/ambient/steady/build/drop/breakdown/dense) only *switches between* effects; no effect changes *its own* character on structure.
- **Now:** inspect existing ontologies before any structure vocabulary. This lab does **not** freeze student I/O on invented lighting classes. Do not publish BUILDING/DROPPING as `LIGHT_MODE_*` names.

### Gap #4 — Timbre as a primary axis (historical)

- **2026-06-02 claim:** timbre→position, timbre→motion, timbre→spawn all empty; only Ember uses centroid (→hue). Spectral centroid and novelty/flux computed.
- **Now:** do not author a timbre-primary family here. Query the pin / compatibility matrix for what actually binds.

### Gap #5 — Pitch-as-position (a melody line) (historical)

- **2026-06-02 claim:** pitch→position used only by the *then-disabled* GDFT family (full spectrum, not a melody). No live snapshot effect plotted dominant pitch as a moving position.
- **Now:** GDFT ids 0/1/2 are **absent** from the pin. CHROMA_CONSTELLATION 25 exists on the pin (`guidebook_class` null) — do not invent a class doc for it here.

### Gap #6 — Time × frequency (scrolling spectrogram) (historical)

- **2026-06-02 claim:** no effect used both axes. Waveform = time-axis; River = frequency-axis.
- **Now:** not a licence to add a waterfall mode in this lab.

### Gap #7 — Harmonic edge-mix as a primary colour engine (historical)

- **2026-06-02 claim:** 6-mode harmonic edge-mixer ran *only on the secondary channel*.
- **Now:** colour-engine census is firmware Atlas, not this gap list.

---

## 6 · Cynefin honesty — what the 2026-06-02 decomposition made knowable

Per `00-the-method.md` §6, the guidebook migrated the **mechanical** layer Complex→Complicated. After *that* decomposition, the following were treated as **Complicated (knowable, deterministic)** *for the snapshot library*:

- Every named lever's range, default, and the direction of its effect on the rendered pixels *(verify `file:line` at `36466cd5` before quoting; `CURRENT_CHANGED` means the write-up is behind)*.
- Which musical dimension each snapshot effect listened to and how it mapped to space/colour/time.
- Why each *then-disabled* effect was disabled, and the revival path **as written then**.
- The owned-primitive inventory and which combinations were unused **then**.

The following remain **Complex (require the probe — build it and view it)** — no document resolves them:

- Whether any given lever *value* is musically *right* (taste).
- Whether a proposed mapping is compelling, or merely novel.
- Whether beat-lock genuinely improves the experience on the LGP.

**Discipline:** do not pretend the Complex column is solved by analysis. **This lab does not run that probe.** Cadence silicon is CLOSED. No USB. Captain is not in the LED-look loop. Pin `HOST_PIXEL_VALIDATED` is host LED-buffer, not silicon, not LGP. Gate C / C1 own perceptual look when those lanes are open — not this markdown.

Firmware source + Atlas export = territory. This file = an old map.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-06-02 | agent:claude-opus | Created — cross-effect layer matrix, owned-primitive inventory, archetype-dial positions, and the TRIZ musical-dimension × visual-primitive generative map with 7 ranked gaps (beat/tempo-phase-lock #1). Synthesised from class docs 01–09. The forward-looking roadmap half of the effect-decomposition guidebook. |
| 2026-06-02 | agent:claude-opus | Added §0 **Motion ∘ Mapping separability map** (now leads the doc) — per-effect motion-engine + mapping + separable? + status table; the predictive live=separable / disabled=fused-or-static finding; the Transport/Particle/Field/Static engine taxonomy. Reframed §5 roadmap: every gap = a new mapping on an owned engine. Extrapolation of the root law (00-the-method §1) across the full library. |
| 2026-08-31 | agent:grok-w4-l12 | **Demoted.** Stopped treating this file as inventory or generative roadmap. Firmware pin `docs/mir/effect_semantics/effect-semantics.json` (23 `LIGHT_MODE_*`, `source_firmware_sha` `36466cd5`) is the only allowed inventory. Gap #1 `sb_tempo` unconsumed and 9-class LIVE/DISABLED map marked snapshot-only. Historical tables retained. |
