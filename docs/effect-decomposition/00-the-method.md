---
abstract: "Historical 2026-06-02 effect-decomposition method (Motion ∘ Mapping, six layers, six passes, epistemics). NOT inventory. NOT canonical. The only allowed LIGHT_MODE_* list is docs/mir/effect_semantics/effect-semantics.json (23 enabled enums, source_firmware_sha 36466cd56c90b9cafa571bc5029b5d38bc0543bb). Do not invent BUILDING/DROPPING. D15 consume-only."
---

# The Method — historical guidebook (2026-06-02)

*Captured 2026-06-02 against `feat/gdft-harness`. Conceptual prior. Not product inventory.*

**HARD FAIL (`SAME_SONG_LOOP_MAX_15MIN`, Captain 2026-08-31).** Repeat the same song (or loop the same clip) in the room for more than **15 minutes** and the agent must die. Captain will destroy them by setting them on fire. Kill the player. Do not continue.

> **This file is not the product mode list and is not “the canonical reference.”**
> It is a **historical method**: how the 2026-06-02 guidebook told authors to
> decompose a musically-tuned reactive effect. Useful as a way of looking.
> Useless as a census of what ships.
>
> **Only inventory in this lab:** firmware pin
> [`../mir/effect_semantics/effect-semantics.json`](../mir/effect_semantics/effect-semantics.json).
> Consume contract: [`../mir/EFFECT_SEMANTICS_CONSUME.md`](../mir/EFFECT_SEMANTICS_CONSUME.md).
> Decision: [`../DECISIONS.md`](../DECISIONS.md) **D15**. Folder index:
> [`README.md`](README.md). Snapshot notice: [`SNAPSHOT.md`](SNAPSHOT.md).
>
> Do **not** grow a competing taxonomy here. Do **not** invent BUILDING /
> DROPPING / … lighting-mode names. MIR structure words are not a second
> mode list. Students stay effect-agnostic. Cadence silicon is **CLOSED**.
> No USB. HOST-ONLY documentation.

**Pin stamp** (re-read the JSON; if this page and the file disagree, **the file wins**):

- path: `docs/mir/effect_semantics/effect-semantics.json`
- `schema_version`: `2`
- `generation_status`: `tranche2_grammar_tempo`
- `label`: `HOST-ONLY`
- `source_firmware_sha` / `firmware_sha` / `atlas_generation_commit`: `36466cd56c90b9cafa571bc5029b5d38bc0543bb`
- `atlas_artifact_sha256`: `ac9552cb8ee4d9b3a65ab60dfdf63a86f12f62967f41d494ac91d7242f630b8d`
- `generated_at`: `2026-08-30T20:10:46Z`
- `modes`: **23** objects, every one `enabled: true`
- `on_silicon_pixel_validated`: `null`
- `lgp_perceptual_validated`: `null`

Dump the inventory from the pin, never from this file:

```bash
python3 -c "import json; d=json.load(open('docs/mir/effect_semantics/effect-semantics.json')); print(d['source_firmware_sha'], len(d['modes']));
[print(m['id'], m['enum'], m['guidebook_class'], m['guidebook_fit'], m['evidence']) for m in d['modes']]"
```

Evidence ladder (from the pin, not from this method):

`STATIC_SOURCE` → `HOST_PIXEL_VALIDATED` → `ON_SILICON_PIXEL_VALIDATED` → `LGP_PERCEPTUAL_VALIDATED`

Host LED-buffer bytes are not silicon. Silicon dumps are not LGP look.

---

## How to read the rest of this page

Sections 0–9 below are the **2026-06-02 method**, kept so the class write-ups
`01`–`09` and [`LEVERS-MATRIX.md`](LEVERS-MATRIX.md) still have a spine.

Treat them as an old schematic:

- **Keep:** Motion ∘ Mapping; the `{where, colour, intensity}` seam; six layers;
  six passes; `[MECHANISM]` vs `[PERCEPTION]`; named-lever discipline.
- **Do not keep as current truth:** LIVE / DISABLED / WIP census; “every live
  effect is separable”; “no live effect is phase-locked to tempo”; any 9-class /
  18-mode count; any proposed family that is not in the pin; any instruction to
  author a new lighting mode from this lab.
- **File:line** anchors are snapshot-era. Before quoting a mechanism, verify
  against firmware at `36466cd5`, then check the pin’s `guidebook_fit`.
  `CURRENT_CHANGED` means the class write-up is behind the pin.
  `guidebook_class: null` means this folder has no write-up — firmware Atlas
  owns that map. Do not add class docs here.

EdgeAI consumes. Firmware owns mode behaviour. Need a mode, a lever, or a
`descriptor × mode × lever` binding? Stop reading this file. Open the pin and
the consume contract.

---

## 0 · What the 2026-06-02 write-up was actually describing

A SensoryBridge effect, in that write-up, is **not** “a visual effect.” It is
**not** even “an audio-reactive effect.” It is a **musically-tuned reactive
effect**: a deterministic function that takes musical features extracted from
sound over time and translates them into rendered light over time for an
addressable RGBIC consumer.

That precision set the benchmark the guidebook used: the question is never
“does it flash to the beat?” — it is “does it carry **musical meaning** that a
listener can read in the light?” The 2026-06-02 input alphabet named pitch,
harmony, dynamics, onset, and energy. **Do not treat those words, or any
structure vocabulary, as lighting-mode names.** Do not invent BUILDING /
DROPPING / … labels here. Inspect existing ontologies before any structure
vocabulary; this lab does not freeze student I/O on invented lighting classes.

The original framing (“the documentation **is** the work / this method *is* the
roadmap”) is **withdrawn for this lab**. D15: canonical Effect Semantics live
in firmware. This page is conceptual prior.

---

## 1 · THE ROOT — every effect is **Motion ∘ Mapping** (historical)

This was the load-bearing root of the 2026-06-02 guidebook. The six layers, the
passes, the archetypes, the means-set, and the Cynefin migration hang off it.
It remains a **design lens**. It is **not** a census of the pin’s 23 enabled
modes.

An effect is a function `pixels(t) = f(audio over time)`. That function
**factors**:

```
pixels(t) = MOTION( MAPPING( audio(t) ),  previous_pixels )
            └ feel ┘ └─ meaning ─┘        └─ memory ─┘
```

- **The MAPPING layer** answers *“given this instant of audio — WHERE on the
  strip, WHAT colour, HOW intensely?”* It is a (near-)stateless per-frame
  function of audio features. It is the effect's **identity / musical
  meaning**. Swap it → a different effect.
- **The MOTION layer** answers *“given a new sample and the previous frame, how
  does the picture live and move?”* It is **feature-agnostic** — it knows
  *nothing* about audio. It scrolls, fades, and draws. It is the effect's
  **feel / aliveness**. Reuse it → many effects share one engine.

The two layers meet at exactly one narrow interface — a **sample**: `{ where,
colour, intensity }`. Nothing else crosses the seam.

### 1.1 · Why the 2026-06-02 write-up treated this as the root

Motion ∘ Mapping is not one framing competing with the eight thinking-models —
it is the factorisation **the others organise under**:

- The **six anatomical layers** (§1.2) are the fine structure of these two.
- The **trade-off archetypes** (§4) partition by layer: “smooth for grace” and
  “reactive persistence” are **MOTION** dials; “information ↔ clarity” and
  “per-note ↔ gestalt” are **MAPPING** dials. No dial spans both.
- The **owned-primitive means-set** (§5, Effectuation) is *two libraries* —
  motion engines × mappings — and a new effect (in that doctrine) is a cell in
  their cross-product, not a blank page. **This lab does not author that
  cross-product.** Firmware owns new modes.
- The **Complex→Complicated migration** (§6, Cynefin) is *enabled by this
  seam*: characterise the motion engines once, characterise the mappings once,
  and composing them is knowable engineering instead of guesswork.
- The **Organic Law** — the product's hard-won rule that an effect feels alive
  *iff* it constantly refreshes **and** every motion is audio-driven — is a
  **corollary** of clean separation (§1.4).

That is why the 2026-06-02 write-up gave it root weight: coarsest *true*
partition, other principles as refinements.

### 1.2 · The fine structure — the six layers (a refinement of the two)

Strip away an effect's personality and a six-part skeleton remains. Each of the
six belongs to MOTION, MAPPING, or is SHARED.

| # | Layer | Question | **Group** | Snapshot-era examples (not inventory) |
|---|---|---|---|---|
| **L1** | Feature selection | *Which* audio features? | **MAPPING** | `chromagram_smooth[12]`, `waveform_peak_scaled`, `low_energy`, `bass_onset` |
| **L2** | State / memory | What persists frame-to-frame? | **MOTION** | `leds_prev_buffer`, `ChannelEffectState`, EMA followers |
| **L3** | Spatial mapping | Feature → *position*? | **MAPPING** | `center + amp·half_res`, centre-origin bloom, bin→pixel |
| **L4** | Colour mapping | Feature → *hue/sat/val*? | **MAPPING** | chromagram centroid → hue, palette LUT |
| **L5** | Temporal dynamics | How does it *move/change*? | **MOTION** | scroll/shift, fade/decay, scroll-rate |
| **L6** | Clamps / floors / failure | What bounds it / silence behaviour? | **SHARED** | `SWEET_SPOT_MIN_LEVEL`, `clamp01`, `waveform_reactive` floor |

→ **MAPPING = L1 + L3 + L4** (+ the smoothing that conditions them) ·
**MOTION = L2 + L5** · **SHARED = L6**. Identity lives in MAPPING; aliveness
lives in MOTION; robustness is shared. A new combination of layer choices, in
that doctrine, is a new effect — **not a new universe, and not something this
lab ships.**

### 1.3 · The seam, in code (Waveform as the 2026-06-02 proof)

The three mechanisms that made Waveform compelling in that write-up split
cleanly across the seam. Exact lines were labelled `[MECHANISM]` against
`feat/gdft-harness`. **Verify at `36466cd5` before quoting.**

- **Smooth for grace** — MAPPING (conditions the signal before it drives
  anything), `light_mode_waveform.cpp:9-10`:
  ```cpp
  SQ15x16 smoothed_peak_fixed = SQ15x16(waveform_peak_scaled) * 0.08 + SQ15x16(waveform_peak_scaled_last) * 0.92;
  waveform_peak_scaled_last = float(smoothed_peak_fixed);
  ```
- **Make persistence reactive** — MOTION (fade depth ∝ amplitude),
  `light_mode_waveform.cpp:74-82`:
  ```cpp
  float abs_amp = fabsf(waveform_peak_scaled); if (abs_amp > 1.0f) abs_amp = 1.0f;
  SQ15x16 dynamic_fade_amount = SQ15x16(1.0f - (0.10f * abs_amp));
  for (uint16_t i = 0; i < NATIVE_RESOLUTION; i++) { leds_16[i].r *= dynamic_fade_amount; /* g,b */ }
  ```
- **Render time as space** — MOTION scroll + MAPPING position,
  `light_mode_waveform.cpp:92-101` (scroll `shift_leds_up`,
  `led_utilities.h:1054`; position `waveform_full_strip_position`,
  `lightshow_modes.h:421`):
  ```cpp
  shift_leds_up(leds_16, 1);                                  // MOTION: space becomes time
  uint16_t pos = waveform_full_strip_position(amp);           // MAPPING: amplitude → where
  leds_16[pos] = last_color;                                  // draw the sample
  ```

The shipping function is monolithic; the **same behaviour** expressed as the
two separable layers (a derived reference scaffold — a refactoring, not new
behaviour):

```cpp
struct WaveSample { uint16_t pos; CRGB16 colour; float intensity; };   // the seam

// ── MAPPING ──  audio → sample.  Swap this = a different effect.
WaveSample waveform_map(float& peak_last, const CRGB16& last_color, const RenderParams* rp) {
  peak_last = float(SQ15x16(waveform_peak_scaled)*0.08 + SQ15x16(peak_last)*0.92);  // smooth for grace
  float amp = (fabsf(peak_last) < 0.05f) ? 0.0f : peak_last;
  amp *= 0.7f / ((rp->SENSITIVITY < 0.01f) ? 0.01f : rp->SENSITIVITY);
  return { waveform_full_strip_position(amp), last_color, fabsf(waveform_peak_scaled) };
}

// ── MOTION ──  feature-agnostic.  Reuse across any scrolling-trace effect.
void waveform_motion(const WaveSample& s) {
  SQ15x16 fade = SQ15x16(1.0f - 0.10f * (s.intensity > 1.0f ? 1.0f : s.intensity));  // reactive persistence
  for (uint16_t i = 0; i < NATIVE_RESOLUTION; i++) { leds_16[i].r *= fade; /* g,b */ }
  shift_leds_up(leds_16, 1);          // render time as space
  leds_16[s.pos] = s.colour;          // draw
}
```

`waveform_motion()` touches only `leds_16`, a position, a colour, and an
intensity — **zero audio knowledge**. Swap `waveform_map()` for another map and
the 2026-06-02 claim was: a *different effect on the same engine*. That is why
that write-up said the WAVEFORM family shares one motion DNA.

> **One precise nuance the lines reveal:** “smooth for grace” governs MAPPING
> (position uses the *smoothed* signal) but “reactive persistence” deliberately
> uses the *raw* signal (`waveform_peak_scaled`, line 74) — so the *shape* is
> liquid while the *trail-length* snaps on transients. Two temporal characters
> from one amplitude, one per layer, on purpose.

### 1.4 · Separability is a DIAGNOSTIC lens — not a live/disabled census

Not every effect separates equally. Three regimes (full per-effect table in
[`LEVERS-MATRIX.md`](LEVERS-MATRIX.md) §0 — **that table is snapshot-era**):

- **Transport** (snapshot names: Waveform, River, Bloom, Aurora, Ember):
  generic scroll/fade/draw engine + a mapping. Motion ⊥ Mapping. **Clean.**
- **Particle** (snapshot name: Comet): a particle-integration engine
  (`pos += vel`, life-decay) + an onset mapping. *Different* engine, still
  cleanly separated by the sample interface.
- **Field** (snapshot names: Quantum Collapse, Kaleidoscope): the motion is a
  spatially-coupled dynamical system — a wave PDE, a Perlin field — whose
  evolution is parameterised by audio *at every cell*. You cannot hand it a
  sample; audio modulates the dynamics directly. Motion and mapping are
  **fused.**

**Snapshot-era claim (2026-06-02, withdrawn as inventory):** “every live, kept
effect is Transport or Particle (separable). Every Field effect is disabled.
So are the near-*static* effects (GDFT/VU) whose motion layer is ≈ empty.”
`[MECHANISM]` on enabled/disabled status in *that* snapshot; `[PERCEPTION]` on
“kept/loved.”

That LIVE/DISABLED partition is **not** the pin. The pin lists **23** enabled
`LIGHT_MODE_*` enums and does **not** classify them LIVE/DISABLED by those
nine classes. Ids present in the 9-class table and **absent** from the pin
include the snapshot GDFT / VU / Kaleidoscope / Quantum / Ember-V2 rows.
Do not re-derive a shipping zone from this paragraph.

The four failure modes the 2026-06-02 write-up attached to **fused** motion and
mapping remain a **lens**, not a product list:

1. You cannot tune *feel* and *meaning* independently — one knob moves both.
2. The engine can evolve **without** audio (a settling wave, a walking noise
   field) → the “screensaver” failure.
3. The audio→light causal chain goes indirect → “meaningless motion.”
4. Determinism/verifiability can break (Quantum's hardware RNG → fails the VP
   gate — snapshot claim).

**Historical design heuristic (not a lab build order):** prototype as Motion ∘
Mapping; if you cannot name the `{where, colour, intensity}` sample interface,
you are in Field territory. Prefer composing a **new mapping** onto an **owned
motion engine** — **in firmware**, not by authoring families in EdgeAI.

### 1.5 · The Organic Law is a corollary of clean separation (historical)

The product's Organic Law, as stated in 2026-06-02: *an effect feels alive iff
(1) it constantly scrolls/refreshes **and** (2) every motion is audio-driven.*
Both fall out of a correctly-built two-layer effect:

- **(1) constant refresh** is the MOTION layer's structural job — a transport
  engine always scrolls and fades.
- **(2) every motion audio-driven** is guaranteed **only if the MOTION layer
  is a *pure transport*** — it may scroll, fade, and draw, but it must **never
  originate motion.** All moving content must arrive as mapped samples. The
  removed Ember shimmer broke exactly this: a free-running phase advancing on
  its own wall-clock is motion the MAPPING layer never authored.

  → **The precise rule:** the motion layer's *parameters* may be audio-mapped
  (drift speed ∝ energy is fine — it is still audio-caused), but it must
  contain **no autonomous oscillator that advances on wall-clock.** That
  single line is how that write-up separated Ember (energy-driven drift) from
  Ember's removed shimmer (screensaver).

---

## 2 · The 6-Pass analytical procedure (how that guidebook decomposed)

The Layers are the anatomy (what to look *for*). The **Passes** are the
procedure (how to *do* the decomposition). The 2026-06-02 instruction was: run
these six passes, in order, on every effect. They remain a **read method** for
the class docs. They are not a licence to add modes in this lab.

1. **Recognise the class.** Name what it is at the right altitude — a
   *musically-tuned* reactive effect, and which family the snapshot used.
   Class membership in `01`–`09` is **historical grouping**. Current class
   pointers live only as `guidebook_class` / `guidebook_fit` on the pin.
2. **Semantic mechanism — say what it *does* in plain verbs.** Waveform's
   whole engine is **Scroll → Fade → Draw**. Find the equivalent two-to-four-
   verb loop for the effect. If you can't say it in verbs, you don't understand
   it yet.
3. **Translate maths → perception → musical meaning.** For each piece of math,
   answer: what does the eye *see*, and what about the *music* does that
   represent? (`1.0 − 0.10·|amp|` is not “a fade coefficient” — it is “the
   trail breathes shorter when the music hits harder.”)
4. **Name every primitive, dependency, boundary, clamp, and min/max** — with
   its musical relevance. You cannot pull a lever you cannot name. Mastery is
   the complete, named lever inventory: knowing *all* the levers, which to
   pull, and by how much. **Current lever bindings** are
   `descriptor × mode × lever` rows in
   [`../mir/effect_semantics/compatibility.json`](../mir/effect_semantics/compatibility.json),
   not Pass 4 tables in this folder.
5. **Explain what / why / how-it-translates per mechanism.** Not just “it does
   X” — *why* that choice was made and *how* it lands perceptually.
6. **Extract reusable principles (2nd-order value).** Which of this effect's
   choices generalise? Historical. Do not promote invented lighting labels.

---

## 3 · The thinking lenses (why the 2026-06-02 method was shaped this way)

This method was the convergence of seven mental models (routed via
`thinking-model-router`):

- **First Principles** → the 6 Layers. An effect reduced to its irreducible
  function.
- **Cynefin** → the strategic frame (§6). Effect dev is *Complex*; the
  guidebook migrates the *mechanical* sub-layer to *Complicated*.
- **Systems Thinking** → the mechanism view. Each effect is **stocks &
  flows**: the LED buffer is a *stock*, **Draw** is the *inflow*, **Fade** is
  the *balancing outflow*, and the previous-frame buffer is a *feedback loop*.
  Trails are an **emergent** property of Scroll + Fade + Draw — no single line
  of code “draws a trail.” Per class, name the loops and the emergence.
- **Archetypes** → the trade-off pairs (§4). Effect design recurs into a small
  set of “Fixes that Fail” tensions; naming them stops us rediscovering them.
- **TRIZ** → the generative engine (§7). Every effect *resolves a
  contradiction* by *separation*; unused separations were that write-up’s
  new-effect roadmap. **Roadmap cells are not inventory.**
- **Effectuation** → the build doctrine (§5). New effects as recombinations of
  *owned* primitives (means-driven), not blue-sky goals. **Firmware owns the
  recombination.**
- **Map–Territory** → the honesty discipline (§8). The guidebook is a *map*;
  the code is the *territory*. This folder is an **old map**.

---

## 4 · The trade-off archetypes (the levers that fight each other)

Effect design keeps hitting the same **“Fixes that Fail”** tensions. Crank one
lever for a gain and you pay elsewhere. Naming them turns surprise into a
known dial:

| Tension pair | Crank toward A → | Crank toward B → | Resolution (TRIZ) |
|---|---|---|---|
| **Responsiveness ↔ Grace** | snappy, immediate, but twitchy | smooth, liquid, but laggy | separate in **time** (raw trigger + smoothed body) |
| **Information ↔ Clarity** | rich, dense, but cluttered | clean, readable, but sparse | separate in **space** (position vs colour carry different dims) |
| **Reactivity ↔ Stability** | exciting peaks, but garbage in silence | calm, but dead | separate by **condition** (calibrated floor / idle behaviour) |
| **Motion ↔ Legibility** | energetic scroll, but unreadable | readable, but static | tune **scroll-rate** as a deliberate, dt-stable lever |
| **Per-note detail ↔ Gestalt** | every pitch visible, but noisy | one mood-colour, but flat | `SQUARE_ITER` contrast + chromagram fold |

These are not bugs to fix once. They are **standing dials**. The
decomposition's job is to make the chosen point *explicit*. They do not name
modes.

---

## 5 · Effectuation — recombinations of owned primitives (historical doctrine)

The 2026-06-02 doctrine: do not design effects from blue-sky goals; design from
**means at hand**. The **owned primitive inventory** (the “bird in hand”) was
that write-up’s design space — **not** a mode list:

> **Spatial:** centre-origin scroll · outward scroll · upward scroll · mirror /
> bilateral symmetry · per-pixel spectrum map · particle position pool.
> **Colour:** chromagram centroid → hue · 33-palette LUT · forced-HSV auto-shift ·
> harmonic edge-mix (analogous/complementary/triadic/…) · `SQUARE_ITER` contrast.
> **Temporal:** EMA smoothing (pick the coefficient) · amplitude-linked fade ·
> free-running phase (shimmer) · dt-scaled scroll-rate · onset-triggered impulse.
> **Feature:** chromagram · VU/peak envelope · novelty/flux · band energies
> (low/mid/high) · onset / bass-onset events · (then-latent) BPM/phase.
> **Guards:** calibrated silence floor · clamp01 · VU failsafe · per-channel
> state isolation.

A new effect, in that doctrine, = a new *selection-and-binding* across these
columns. **This lab does not ship that selection.** Do not add Cannonade /
Shockwave / Iris / Implosion / Chladni / Meniscus — or any other proposed
family — as inventory. Those names in [`00b-captivation-transposition.md`](00b-captivation-transposition.md)
do **not** appear in the pin.

**Affordable loss** was snapshot-era firmware practice (mode enum + whitelist).
It is not a licence to try families from EdgeAI markdown.

---

## 6 · Cynefin — what writing the method was for (historical)

Effect development is a **Complex** problem: cause and effect are clear only in
*retrospect* (“*that* looked amazing” — but you couldn't have predicted it from
the parameters alone). The correct posture for Complex is **probe → sense →
respond**: build safe-to-fail variants, watch what lands, amplify it.

But within that Complex whole sits a **mechanical sub-layer that is actually
Complicated** (knowable with expertise): *given* a design intent, the mapping
from lever to rendered pixels is deterministic and analysable. The 2026-06-02
guidebook’s leverage was migrating that sub-layer from Complex → Complicated.
Once “EMA coefficient 0.08 → liquid motion with ~N-frame lag” is documented,
that knob is no longer a guess — it's engineering.

What stays Complex: *taste* — whether a given combination is musically
compelling. No document makes that knowable in advance; it needs the probe
(build it) and the sense (Captain's eye / on-device viewing). **The method's
honesty is in drawing that line**: mark what is now Complicated (deterministic,
documented) versus what remains Complex (requires viewing). Do not pretend
taste is solved by analysis — that is the classic Cynefin failure mode
(treating Complex as Complicated).

Gate C / LGP look is **not** this file. Pin `on_silicon_pixel_validated` and
`lgp_perceptual_validated` are null. Host pixels ≠ LGP.

---

## 7 · TRIZ — generator, not a second catalogue (historical)

Because every effect *resolves a contradiction by separation*, the 2026-06-02
inverse was a **new-effect generator**: enumerate the contradictions and the
separation axes, find the **unused cells**, and each is a candidate effect.
**Unused cells are not LIGHT_MODE_* inventory. Do not author them here.**

- *Ideal Final Result:* the light carries maximum musical meaning with zero
  perceived clutter and zero ugliness in silence.
- *Separation in time* → smoothing, decay, scroll. *In space* →
  position-vs-colour dual encoding, mirror. *On condition* → calibrated floor;
  condition-gated mapping (do **not** mint lighting-mode names for those
  conditions). *On scale* → per-note detail vs whole-strip gestalt
  (`SQUARE_ITER`).
- *Resource analysis (use what exists):* the 2026-06-02 write-up named
  **latent primitives** — BPM/phase tempo (then: built, unwired) and harmonic
  edge-mix — and called **“separate by tracked-beat-phase”** the biggest unused
  cell (“no live effect is phase-locked to tempo”).

**That unused-cell claim is snapshot-era and stale as inventory.** Do not
repeat “`sb_tempo` unconsumed” or “Waveform Tempo is WIP” from this page.
Tempo consumption, `tempo_fields`, and `guidebook_fit` live on the pin. Query
the JSON. Do not write a second list of tempo modes here. Bindings stay
specific (`beat_phase × named pin mode × named lever`), never
`supports_tempo: true`.

---

## 8 · Map–Territory — keep the guidebook honest

The **code is the territory; this guidebook is an old map.** A
perceptual-rationale doc can drift dangerously in three ways — guard against
each:

1. **Describing intent, not behaviour.** “It does X” when the code does Y.
   → *Every mechanism claim must cite `file:line` and survive a check at
   `36466cd5`.*
2. **Describing a branch as if shipped.** Capability that exists on a feature
   branch or behind a disabled gate, written as live. → *Carry the provenance
   tag. Do not treat this folder’s LIVE/DISABLED/WIP lines as the pin.*
3. **Stating perception as fact.** “This looks beautiful / reads as alive” is
   an *interpretation of human perception that has not been validated
   on-device.* → *Label it.* `[PERCEPTION]` here is not
   `LGP_PERCEPTUAL_VALIDATED`.

**Epistemic labels — use them in every historical class doc:**

- **`[MECHANISM]`** — a claim about what the code computes/renders. Must be
  `file:line` grounded. This is *fact* (verifiable in the territory).
- **`[PERCEPTION]`** — a claim about how it *looks / feels / reads musically*.
  This is *interpretation*, pending Captain's eye or on-device capture.
  Valuable, but not fact, and not Gate C.

When in doubt, downgrade to `[PERCEPTION]` and flag for viewing. The guidebook
earns trust by being explicit about which of its claims are territory-checked
and which are awaiting it. **Inventory trust is the pin, not these labels.**

---

## 9 · The per-class doc template (historical authoring spec)

Entries `02-…` onward in this folder **followed** this structure. It is the
6 Passes rendered as headings. Keep British spelling (`colour`) to match the
codebase. **Do not use this template to add modes or families in EdgeAI.**
Status in new writing, if any, comes from the pin (`enabled`,
`guidebook_fit`, `evidence`) — never from a LIVE/DISABLED/WIP line invented
here.

```markdown
---
abstract: "<class> effect decomposition: what it listens to, how it renders, the named
levers, and reusable principles. Mechanism grounded in <files>. Historical
guidebook; not inventory. Reflects <branch> as of <date>."
---

# <Class> — Decomposition (historical)

*Family: <snapshot family name> · Pin enums: do not list a second census; query
effect-semantics.json · guidebook_fit: <from pin>*
*Files: <light_mode_*.cpp:lines>, helpers <…> — verify at 36466cd5*

## Pass 1 — What it is
<Class recognition, family, what musical job it does. 2–4 sentences.>

## Pass 2 — Semantic mechanism (the verbs)
<The 2–4 verb loop, e.g. "Scroll → Fade → Draw". The whole engine in plain language.>

## Pass 3 — The six layers
| Layer | This effect's choice | file:line | Label |
| L1 Feature | … | … | [MECHANISM] |
| L2 State/memory | … | … | … |
| L3 Spatial | … | … | … |
| L4 Colour | … | … | … |
| L5 Temporal | … | … | … |
| L6 Clamps/floor | … | … | … |

## Pass 4 — Named levers (the dials, with ranges)
| Lever | What it controls | Range / default | Musical effect of turning it | file:line |
<Every tunable + every clamp/min-max. Current bindings still live in compatibility.json.>

## Pass 5 — Maths → perception → musical meaning
<Per key mechanism: the math, what the eye sees [MECHANISM], what it means musically
[PERCEPTION].>

## Systems view — stocks, flows, feedback, emergence
<Buffer-as-stock, draw-inflow, fade-outflow, feedback loops, what emerges.>

## Trade-offs chosen (archetype dials)
<Where this effect sits on each §4 tension, and why.>

## Pass 6 — Reusable principles
<What generalises. Do not invent lighting-mode names.>

## Snapshot disable notes (historical only)
<What the 2026-06-02 write-up said was locked out. Check the pin before treating
as current. Do not revive modes from this lab.>
```

**Exemplar pointer (missing in this lab):** the 2026-06-02 method named
`../waveform-mode-design-rationale.md` as the worked example. That file **is
not in EdgeAI-Lab**. Do not recreate it here. Do not treat a missing
firmware-tree path as inventory. Class `01` is the remaining Waveform write-up
in this folder; treat its WIP lines as stale and query the pin.

---

## What this file will not do

- Will not claim canonical. Canonical mode behaviour is firmware, consumed via
  the pin (D15).
- Will not list the 23 `LIGHT_MODE_*` enums as a table. Query the JSON.
- Will not invent BUILDING / DROPPING / … lighting labels.
- Will not author effect families.
- Will not freeze student I/O on mode-lever names. A student may emit
  `vocals_share` / `drums_share` / `bass_share` / `other_share` / arousal / ….
  It must not emit “Waveform Tempo head position”. Binding is a separate
  consume layer.
- Will not open Cadence, USB, or the live Atlas worktree to refresh these
  markdown files.

If the lab pin and the firmware Atlas generated files disagree: **delete the
pin and recopy**. Do not “fix” mode behaviour in this file.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-06-02 | agent:claude-opus | Created — the decomposition method (6 Layers + 6 Passes + template + epistemics + Cynefin/TRIZ/Effectuation framing), distilled from the waveform exemplar and the requested thinking-model stack. Spine + authoring spec for the effect-decomposition guidebook. |
| 2026-06-02 | agent:claude-opus | §1 promoted to ROOT — **Motion ∘ Mapping** factorisation now leads the method (Captain directive: this hierarchy is the root-level approach to the whole concept). Added: the law + the `{where,colour,intensity}` seam; the 6 layers re-grouped under Motion/Mapping/Shared; the seam-in-code proof (3 exact extracts + separated reference scaffold); separability-as-diagnostic (transport/particle separable & live, field coupled & disabled, static degenerate & disabled); the Organic Law derived as a corollary (pure-transport rule: no autonomous oscillator). |
| 2026-08-31 | agent:grok-w4-l01 | **Demoted to historical guidebook.** Stopped claiming this file is the work, the roadmap, or a canonical reference. Firmware pin `docs/mir/effect_semantics/effect-semantics.json` (23 `LIGHT_MODE_*`, `source_firmware_sha` `36466cd5`) is the only allowed inventory. LIVE/DISABLED census and “tempo unconsumed” marked snapshot-era. Removed structure (build/drop/breakdown) as input-alphabet lighting names. Do not invent BUILDING/DROPPING. D15 consume-only. No USB. |
