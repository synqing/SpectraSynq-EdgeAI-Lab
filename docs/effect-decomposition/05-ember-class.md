---
abstract: "HISTORICAL 2026-06-02 Ember-class guidebook write-up. NOT inventory. Pin inventory is LIGHT_MODE_EMBER id 16 only (guidebook_class 05-ember, guidebook_fit CURRENT_CONFIRMED, evidence HOST_PIXEL_VALIDATED). Snapshot Ember V2 (id 17) is ABSENT from docs/mir/effect_semantics/effect-semantics.json at source_firmware_sha 36466cd56c90b9cafa571bc5029b5d38bc0543bb. Do not treat LIVE/DISABLED in this file as product truth. Do not revive V2 here. Cadence CLOSED. HOST-ONLY. No USB."
---

# Ember class — HISTORICAL (2026-06-02 snapshot)

**HARD FAIL (`SAME_SONG_LOOP_MAX_15MIN`, Captain 2026-08-31).** Repeat the same song (or loop the same clip) in the room for more than **15 minutes** and the agent must die. Captain will destroy them by setting them on fire. Kill the player. Do not continue.

```
╔══════════════════════════════════════════════════════════════════╗
║  HISTORICAL RECORD — 2026-06-02 GUIDEBOOK — NOT INVENTORY        ║
║  NOT Atlas authority. NOT a mode list. NOT a revival brief.      ║
║  Cadence silicon CLOSED. No USB. No k1-flash. HOST-ONLY.         ║
╚══════════════════════════════════════════════════════════════════╝
```

This file is the **2026-06-02** Ember-class write-up from the effect-decomposition guidebook (`feat/gdft-harness`). It teaches the old **Motion ∘ Mapping** language for a centre-anchored glow. It does **not** say which modes ship.

The only allowed inventory in this lab is the firmware pin:

[`../mir/effect_semantics/effect-semantics.json`](../mir/effect_semantics/effect-semantics.json)

Consume contract: [`../mir/EFFECT_SEMANTICS_CONSUME.md`](../mir/EFFECT_SEMANTICS_CONSUME.md). Folder demotion: [`README.md`](README.md). Decision: [`../DECISIONS.md`](../DECISIONS.md) **D15 / D16**. Do not grow a competing Ember taxonomy here. Do not author Ember V2, Cannonade, or lighting labels (BUILDING / DROPPING / …) as inventory. Student I/O stays effect-agnostic.

---

## 0 · Authority (pin vs this file)

| What you need | Where it lives | This file |
| --- | --- | --- |
| Enabled `LIGHT_MODE_*` list | the pin JSON | **Not here** |
| Ember mechanism language (old map) | body below, captured 2026-06-02 | Historical |
| `file:line` in `light_mode_ember.cpp` | firmware at pin SHA | Snapshot anchors; verify before quoting |
| `descriptor × mode × lever` | [`../mir/effect_semantics/compatibility.json`](../mir/effect_semantics/compatibility.json) | Not here |
| Visual grammar | [`../mir/effect_semantics/grammar_coverage.json`](../mir/effect_semantics/grammar_coverage.json) | Not here |

**Pin stamp** (re-read from JSON; the file wins if this markdown drifts):

- path: `docs/mir/effect_semantics/effect-semantics.json`
- `schema_version`: `2`
- `generation_status`: `tranche2_grammar_tempo`
- `label`: `HOST-ONLY`
- `source_firmware_sha` / `firmware_sha` / `atlas_generation_commit`: `36466cd56c90b9cafa571bc5029b5d38bc0543bb`
- `atlas_artifact_sha256`: `ac9552cb8ee4d9b3a65ab60dfdf63a86f12f62967f41d494ac91d7242f630b8d`
- `generated_at`: `2026-08-30T20:10:46Z`
- `on_silicon_pixel_validated`: `null`
- `lgp_perceptual_validated`: `null`

Evidence ladder (from the pin, not from Pass 5 below):

`STATIC_SOURCE` → `HOST_PIXEL_VALIDATED` → `ON_SILICON_PIXEL_VALIDATED` → `LGP_PERCEPTUAL_VALIDATED`

Host LED-buffer bytes are not silicon. Silicon dumps are not LGP look. Cadence silicon is **CLOSED**. This file is HOST-ONLY documentation.

---

## 1 · Pin facts for Ember (re-derived 2026-08-31)

Dump, never trust this table if the JSON disagrees:

```bash
python3 -c "import json; d=json.load(open('docs/mir/effect_semantics/effect-semantics.json'));
print(d['source_firmware_sha'], len(d['modes']));
[print(m['id'], m['enum'], m.get('guidebook_class'), m.get('guidebook_fit'), m['enabled'], m['evidence']) for m in d['modes'] if m['enum']=='LIGHT_MODE_EMBER' or m['id']==17]"
```

Re-derived from that pin:

| Field | Pin value |
| --- | --- |
| id | `16` |
| `display_name` | `EMBER FIELD` |
| `enum` | `LIGHT_MODE_EMBER` |
| `enabled` | `true` |
| `guidebook_class` | `05-ember` |
| `guidebook_fit` | `CURRENT_CONFIRMED` |
| `implementation` | `effects/light_mode_ember.cpp` |
| `native_inputs` | `audio_snapshot`, `chroma_centroid`, `snapshot.spectral_energy`, `control.mirror`, `centre_origin_mirror` |
| `tempo_fields` | `[]` (empty) |
| `host_renderable` | `true` |
| `harness_key` | `ember` |
| `visual_carriers` | `radial_extent`, `occupancy`, `mean_luminance` |
| `evidence` | `HOST_PIXEL_VALIDATED` |

Host notes on the pin (host LED-buffer, pre-gamma, pre-dither — **not** LGP):

| Sweep | `transfer` | `primary` | `r` | trap |
| --- | --- | --- | --- | --- |
| `peak_ramp` | `DETECTED` | `head_position_upper` | `1.0` | none |
| `chroma_rotate` | `DETECTED` | `tip_energy` | `0.5538` | `mean_luminance` is not the primary carrier (and may invert) |
| `onset_train` | `DETECTED` | `centre_energy` | `0.8045` | same luminance trap |
| `band_low_vs_high` | `DETECTED` | `head_position_upper` | `0.816` | none |

`grammar_coverage.json` names Ember as the **representative** of grammar `continuous_amplitude` (`mode_id` 16, slug `ember`, lever `radial_extent + luminance`, host `peak ramp extent=0.9998 luma=1.0`). Note on that grammar: “Ember extent and luma rise together. Not the Tempo inversion.” That is a **host-pixel grammar stamp**, not a licence to freeze student I/O on Ember reach.

**Id 17 / `LIGHT_MODE_EMBER_V2` is absent from the pin.** The snapshot body below still says V2 is DISABLED / compiled-but-unreachable. That was 2026-06-02 guidebook talk. The pin has 23 enabled `LIGHT_MODE_*` and **no row for 17**. Do not put Ember V2 back on an inventory list. Do not write a revival path as lab work.

`guidebook_fit: CURRENT_CONFIRMED` means the write-up still describes mode 16’s *shape*. Lever values and `file:line` may still have drifted vs firmware at `36466cd5`. Verify source before quoting a constant. Do not “fix” this snapshot to match HEAD.

---

## 2 · Snapshot claims that are not product truth

Left in the historical body. Do not consume as inventory.

| Snapshot claim (2026-06-02) | Pin / lab |
| --- | --- |
| Ember (16) LIVE, Ember V2 (17) DISABLED | 16 enabled; **17 absent** |
| “Read when tuning or extending the Ember family” | Firmware owns semantics. EdgeAI consumes. |
| V2 gated in `light_mode_is_enabled()` / revival options (a)(b)(c) | Historical diagnosis. Not a build list. |
| `[PERCEPTION]` breathing-field / mood-shift language | Interpretation. Not LGP. |
| Energy → reach as “the” Ember readout | Pin host primary on `peak_ramp` is `head_position_upper`; carriers also list `radial_extent` / `occupancy` / `mean_luminance`. Bind the named lever. Do not score mean brightness by default. |

---

## 3 · Historical 2026-06-02 write-up

*Family: glow / continuous-organic · Modes (snapshot census): LIGHT_MODE_EMBER (16, then called LIVE), LIGHT_MODE_EMBER_V2 (17, then called DISABLED 2026-06-02)*
*Files named in the snapshot: `light_mode_ember.cpp`, `light_mode_ember_v2.cpp`, helpers `lightshow_modes.h`, `led_utilities.h:1649`, `sb_audio_snapshot.h`, `channel_effect_state.h:57–58`*

The LIVE / DISABLED labels in this section are **what the snapshot believed**. They are not the pin.

### Pass 1 — What it is

Ember is the **continuous-organic glow** class: a warm radiant field that breathes with broadband energy rather than tracking discrete musical events. Where Comet (mode 13) spawns, travels, and expires one projectile per onset — a *discrete* cause-and-effect — Ember maintains a *permanently present* glowing medium that expands and contracts, brightens and dims, as energy rises and falls. There are no birth or death events; the field simply is, always, and the music modulates its size and intensity.

The live mode (16) is **centre-anchored**: the glow is injected at the strip's midpoint and its reach — how many pixels it illuminates toward the edges — scales directly with `spectral_energy`. At low energy a small warm core persists; at high energy the bloom floods toward the edges. Hue tracks the music's tonal centre (`chromagram_centroid_hue`), so the colour of the glow shifts as harmony changes. The whole glowing medium scrolls outward continuously via `draw_sprite`, creating a constant refresh that prevents any pixel from persisting forever.

### Pass 2 — Semantic mechanism (the verbs)

Every frame is four operations:

> **Clear → Scroll → Bloom → Snapshot**

1. **Clear** the working buffer to black (`memset`, `light_mode_ember.cpp:53`).
2. **Scroll** the previous frame outward by `drift` pixels at alpha `EMBER_ALPHA = 0.88` using `draw_sprite` (`light_mode_ember.cpp:55`), then zero the lower (left-mirror) half — only the right half accumulates history (`light_mode_ember.cpp:56`).
3. **Bloom** — inject fresh glow pixels from the centre outward to `reach` pixels, brightness falling quadratically with distance, hue sweeping across a small palette spread (`light_mode_ember.cpp:62–75`).
4. **Snapshot** the result into `leds_prev_buffer` for the next frame's Scroll, then clamp and mirror (`light_mode_ember.cpp:78–86`).

There are no conditionals on onset events, no particle spawn/death, no beat-phase gating. The loop runs identically every frame; the audio features simply modulate the shape of the Bloom step and the speed of the Scroll step.

### Pass 3 — The six layers

| Layer | This effect's choice | file:line | Label |
|---|---|---|---|
| **L1 Feature** | `snap.spectral_energy` (broadband RMS energy, 0–1) for reach and brightness; `chromagram_centroid_hue()` (circular mean of 12 chroma bins) for hue | `sb_audio_snapshot.h:20`; `lightshow_modes.h:266` | [MECHANISM] |
| **L2 State/memory** | `leds_prev_buffer` (full-strip CRGB16 frame — the scrolling history stock); `fx.ember_shimmer_phase` declared in struct but **unused** in live v1 (marked `(void)fx`, comment: "v2 is stateless (shimmer phase removed)") | `light_mode_ember.cpp:36`; `channel_effect_state.h:57–58` | [MECHANISM] |
| **L3 Spatial** | Centre-origin bloom: pixels injected from `HALF` (strip midpoint) outward to `HALF + reach`; `reach = EMBER_MIN_REACH + energy * (HALF − EMBER_MIN_REACH)`; distance `d = k / reach` is the radial coordinate | `light_mode_ember.cpp:62–65` | [MECHANISM] |
| **L4 Colour** | Palette LUT via `palette_manual_colour(pal, hue, brightness)`; hue = `centroid + d * EMBER_HUE_SPREAD (0.18)` — a small centre→edge sweep atop the tonal-centre hue | `light_mode_ember.cpp:69–70`; `lightshow_modes.h:136` | [MECHANISM] |
| **L5 Temporal** | Constant outward scroll (`draw_sprite` at `drift` px/frame, alpha `0.88`); `drift = EMBER_DRIFT_BASE * (EMBER_DRIFT_FLOOR + EMBER_DRIFT_SURGE * energy) * NR/128` — energy nudges scroll speed but a floor guarantees constant refresh | `light_mode_ember.cpp:54–55` | [MECHANISM] |
| **L6 Clamps/floor** | `energy` hard-clamped to `[0, 1]` after NaN guard (`light_mode_ember.cpp:45–47`); per-pixel brightness skip below `EMBER_FLOOR = 0.015` (`light_mode_ember.cpp:68`); `clamp_crgb16` on every output pixel (`light_mode_ember.cpp:82`); `EMBER_MIN_REACH = 4.0` keeps a non-zero core even in silence | `light_mode_ember.cpp:45–47`, `62`, `68`, `82` | [MECHANISM] |

### Pass 4 — Named levers (the dials, with ranges)

Snapshot constants. Verify at `36466cd5` before quoting as current firmware.

| Lever | What it controls | Range / default | Musical effect of turning it up | file:line |
|---|---|---|---|---|
| `EMBER_DRIFT_BASE` | Base outward scroll speed (px/frame, NR-scaled) | `0.45` px/frame at NR=128 | Faster trail turnover; history refreshes more quickly, old glow evaporates sooner | `light_mode_ember.cpp:26` |
| `EMBER_DRIFT_SURGE` | Extra scroll speed added per unit energy | `0.6` × energy | Loud passages visibly rush outward — the glow surges on peaks, slows on quiet | `light_mode_ember.cpp:27` |
| `EMBER_DRIFT_FLOOR` | Minimum scroll multiplier (fraction of `DRIFT_BASE`) | `0.7` (always ≥ 70% of base) | Raising ensures the strip never stagnates; lowering lets the glow pool in silence | `light_mode_ember.cpp:28` |
| `EMBER_ALPHA` | Per-frame fade coefficient of scrolled history | `0.88` (constant, no energy link) | Lower = shorter trails, punchier; higher = longer trails, more ambient wash; currently constant (unlike Waveform's amplitude-linked fade) | `light_mode_ember.cpp:29` |
| `EMBER_FLOOR` | Per-pixel brightness skip threshold | `0.015` | Raising clips dark outer edges — harder boundary; lowering extends faint glow further | `light_mode_ember.cpp:30` |
| `EMBER_GAIN` | Injection brightness multiplier on freshly-drawn pixels | `0.95` | Overall glow intensity ceiling; keeps injected pixels from saturating at low energy | `light_mode_ember.cpp:31` |
| `EMBER_HUE_SPREAD` | Palette sweep from centre to glow edge (hue units, 0–1) | `0.18` (small spread) | Wider = visible warm→cool gradient across the bloom; narrower = near-monochromatic core colour | `light_mode_ember.cpp:32` |
| `EMBER_MIN_REACH` | Minimum bloom radius in pixels, independent of energy | `4.0` px | Sets the silence floor size — always a small glowing core; raising it means louder ambient presence at rest | `light_mode_ember.cpp:33` |
| `reach` (computed) | Live bloom radius: `EMBER_MIN_REACH + energy * (HALF − EMBER_MIN_REACH)` | `[4, HALF]` px, linear in energy | **The primary energy-to-space lever**: loud music floods the half-strip, quiet contracts to 4 px | `light_mode_ember.cpp:62` |
| `d` (computed) | Normalised radial distance within bloom: `k / reach` | `[0, 1]` | Used in brightness falloff and hue sweep — controls the gradient shape across the bloom | `light_mode_ember.cpp:65` |
| `b` (computed) | Per-pixel brightness: `energy * (1 − d²) * EMBER_GAIN` | `[0, EMBER_GAIN]` | Quadratic falloff: bright at core, soft at edge — avoids hard ring boundary; scales with energy | `light_mode_ember.cpp:66–67` |
| Chromagram centroid | Base hue (0–1) of the bloom, updated every frame | `[0, 1]`, full palette range | Tonal-centre tracking — bass-heavy music = warm palette region, bright treble = cool region [PERCEPTION] | `lightshow_modes.h:266` |
| `NR/128` scale factor | Normalises `drift` for non-128-LED strips | `NATIVE_RESOLUTION / 128.0` | Keeps scroll speed perceptually constant across different strip lengths | `light_mode_ember.cpp:54` |

### Pass 5 — Maths → perception → musical meaning

#### 5.1 The reach equation: energy becomes space

**Maths:** `reach = EMBER_MIN_REACH + energy * (HALF − EMBER_MIN_REACH)` `(light_mode_ember.cpp:62)`

[MECHANISM] `reach` is a linear function of `spectral_energy` bounded between 4 pixels (floor) and `HALF` pixels (full half-strip). When `energy = 0`, `reach = 4`; when `energy = 1`, `reach = HALF`.

[PERCEPTION] The eye sees the glowing field literally grow and shrink with the music's overall intensity. A loud section floods the half-strip with warm colour; a quiet passage contracts it to a small pulsing core at the centre. This is the Ember class's primary musical readout: **loudness is rendered as spatial extent**, not as a flashing brightness pulse. The result is easier to read as energy rather than onset — there is no beat-sync, no sudden flash; just a breathing, expanding/contracting field that mirrors the track's dynamic arc. Build sections visibly inflate the bloom; drop sections expand it further; breakdowns contract it back to the core.

Those structure words in the last sentence are **perception prose from the snapshot**, not a lighting-mode ontology. Do not freeze student I/O on BUILDING / DROPPING.

#### 5.2 Quadratic brightness falloff: soft edge

**Maths:** `b = energy * (1.0 − d * d) * EMBER_GAIN` where `d = k / reach` `(light_mode_ember.cpp:65–67)`

[MECHANISM] Brightness within the bloom is `energy` at the core (`d = 0`) and zero at the glow boundary (`d = 1`), with a quadratic (`d²`) rather than linear roll-off. The `EMBER_GAIN = 0.95` scalar keeps the injected peak just below clamp.

[PERCEPTION] The quadratic curve creates a glowing-ember quality: the centre is intensely lit and the edge fades softly without a hard ring. A linear roll-off would produce a cone with a visible boundary; the squared falloff reads as diffuse heat radiating outward. At low energy the bloom is both dim and small (a faint point); at high energy it is bright and wide (a sweeping warm wash). Musical meaning: **intensity is encoded twice** — in reach (spatial extent) and in brightness (core glow) — and both are driven by the same `energy` value, so they move together.

Pin grammar note agrees that extent and luma rise together on host pixels. That is still not LGP.

#### 5.3 Hue sweep: the chromagram painted across space

**Maths:** `hue = centroid + d * EMBER_HUE_SPREAD (0.18)` `(light_mode_ember.cpp:69)`

[MECHANISM] Each pixel in the bloom receives a hue shifted from the chromagram centroid by `d × 0.18`. At the core (`d = 0`) the hue is exactly the centroid; at the edge (`d = 1`) it is `centroid + 0.18` palette units. `chromagram_centroid_hue()` computes the circular mean of all 12 chroma bins as a unit-circle vector sum, mapped to `[0, 1]` `(lightshow_modes.h:266–281)`.

[PERCEPTION] The bloom is not uniformly coloured: the core carries the tonal centre whilst the outer fringe shifts fractionally toward a neighbour palette region. The spread is deliberately narrow (0.18 ≈ one-fifth of the palette wheel) to preserve harmony-tracking without randomising colour. The result reads as a slight warm→cool gradient from core to edge, giving the glow dimensional depth. When harmony modulates — a chord change shifts the centroid — the entire bloom recolours every frame, gradually (the centroid is a weighted mean, not a snapping value), reading as **mood shift**, not as a flash.

#### 5.4 Constant outward scroll: the flow that prevents stasis

**Maths:** `drift = EMBER_DRIFT_BASE * (EMBER_DRIFT_FLOOR + EMBER_DRIFT_SURGE * energy) * (NR / 128)` `(light_mode_ember.cpp:54)`, fed to `draw_sprite(..., drift, EMBER_ALPHA)` `(light_mode_ember.cpp:55)`

[MECHANISM] `draw_sprite` (`led_utilities.h:1649`) shifts the previous frame outward by `drift` pixels with sub-pixel interpolation and scales each pixel by `EMBER_ALPHA = 0.88`. The lower half is zeroed immediately after (`:56`), so only the right half accumulates history; `mirror_image_downwards` reflects it symmetrically at the end. The floor term `EMBER_DRIFT_FLOOR = 0.7` makes the minimum drift `0.45 × 0.7 = 0.315` px/frame (NR-scaled), never zero; at `energy = 1.0`, `drift = 0.45 × 1.3 = 0.585` px/frame.

[PERCEPTION] Constant scroll keeps the strip **always refreshing**: injected glow travels outward and fades over ~`1/(1−0.88) ≈ 8` frames (≈60 ms at 133 Hz). No frozen state, no held pose — this is the mechanism that makes Ember feel like a *flowing medium*, not a *drawn shape*. The energy-surge on drift means the glow visibly rushes outward on loud peaks (urgency / momentum) and slows to a gentle drift when quiet. Compare to Waveform: Waveform *shortens trails* under load (aggressive, snappy); Ember *accelerates the outward flow* under load (expansive, rushing). Different temporal character, same energy input.

#### 5.5 The (void)fx annotation and the removed shimmer

**History:** `channel_effect_state.h:57–58` defines `ember_shimmer_phase` as a free-running turbulence phase advanced by `novelty`. The live function accepts `ChannelEffectState& fx` but immediately suppresses it: `(void)fx;` `(light_mode_ember.cpp:36)`.

[MECHANISM] The v1 ember used a free-running sine shimmer driven by `fx.ember_shimmer_phase`, advanced each frame by `novelty`. It was removed by the 2026-06-02 fix (comment: "fails — predictable, meaningless motion edge→centre that doesn't align with anything") and replaced with the energy-only architecture. The struct field is retained for ABI/struct stability only; it is not written or read in either live ember function.

[PERCEPTION] The removal is architecturally significant and validates the method's own standard: a free-running phase produces motion **decoupled from the audio** — its cadence runs independently of musical structure even if its speed is modulated by novelty. By the decomposition method's definition, motion whose period and direction are not anchored to a musical feature is a screensaver, not a music-reactive effect. The new architecture has **no free motion**: every position, brightness, and colour change is a direct function of `spectral_energy` or `chromagram_centroid_hue` each frame. Silence → a static, dim core. Music → an expanding, shifting, flowing field. The causal chain is unbroken.

### Systems view — stocks, flows, feedback, emergence

**Stock:** `leds_prev_buffer` — full-strip CRGB16 frame holding accumulated glow history (`:78`).
**Inflow:** the Bloom step injects `b = energy·(1−d²)·EMBER_GAIN` across `reach` pixels (`:63–75`).
**Outflow / decay:** `draw_sprite` × `EMBER_ALPHA = 0.88` reduces every pixel to 88%/frame (first-order decay) while displacing it outward — pixels both fade and travel.
**Feedback:** the frame is snapped to `leds_prev_buffer` (`:78`) before mirror/clamp, so the next frame scrolls what was just drawn — a one-frame loop. Rapid successive blooms (sustained loud section) stack on still-visible earlier glow.
**Emergence:** the breathing, radiant-field quality is drawn by no single line. It emerges from inflow + decay (non-zero ambient glow between hits), energy-linked reach + energy-linked drift (loud = bigger *and* faster = visual surge), and chromagram-linked hue (the visible history is a colour-time record of recent harmony). [PERCEPTION] The "ember" quality — warmth, breath, glow-without-structure — is the emergent property of the four flows, not a programmed personality.

### Trade-offs chosen (archetype dials)

| Tension | Ember's position | Consequence |
|---|---|---|
| **Responsiveness ↔ Grace** | Toward grace: `energy` is used raw in-function, but the scrolling history (0.88/frame) integrates transients | Snappy to peaks, but the *field* never flickers because the stock absorbs transients |
| **Reactivity ↔ Stability** | Stability-biased: `MIN_REACH=4` and `DRIFT_FLOOR=0.7` guarantee the strip is never dark or static | Silence shows a small warm core — correct for ambient-glow; wrong for a pure onset effect |
| **Motion ↔ Legibility** | Motion-biased, but radially symmetric and gradual → organic, not busy | Individual harmonics are not resolved; a gestalt mode |
| **Per-note detail ↔ Gestalt** | Firmly gestalt: `spectral_energy` is broadband; no per-note spatial encoding | Great ambient/background; cannot convey melody |
| **Information ↔ Clarity** | Low info / high clarity: two dimensions (energy→reach/brightness, centroid→hue) | Immediately readable at a glance; harmonic detail sacrificed |

### Pass 6 — Reusable principles

Snapshot design notes. Not a licence to author new families in this lab.

1. **A floor on every motion parameter prevents dead states.** `DRIFT_FLOOR=0.7` + `MIN_REACH=4` encode "an ambient glow should never be fully dark or fully static." Put explicit floors on motion and brightness levers; zero is rarely the right silence behaviour for a glow.
2. **Spatial extent as the primary energy readout.** `energy → reach` (how many pixels lit) rather than `energy → brightness` makes the field *grow* rather than *pulse*. A named design axis — spatial-extent vs brightness encoding — for any bloom-family effect.
3. **The constant-scroll architecture is the ambient-organic template.** Clear → Scroll → Inject → Snapshot with a refresh floor and energy-linked injection yields a continuously-alive strip with zero free motion. Start new ambient effects here.
4. **Energy-linked scroll speed (surge) is a distinct character lever from trail length.** Waveform uses amplitude-linked fade (snappy aggression); Ember uses energy-linked drift (the medium accelerates). Same input, different temporal idioms.
5. **Free-running phase ≠ music-reactive.** A phase advanced by novelty still runs with its own cadence. For motion to carry musical meaning, its amplitude *and* direction must be a direct function of a musical feature each frame.
6. **`ember_shimmer_phase` as a named structural relic.** The retained-but-unused field is the K1 pattern: struct fields are never removed (struct-stability), but may be suppressed at the use site with `(void)fx`. Don't assume every `ChannelEffectState` field is live.

### If disabled — why (snapshot: Ember V2)

#### Ember V2 (LIGHT_MODE_EMBER_V2, mode 17) — DISABLED 2026-06-02 *in the snapshot*

**This subsection is historical.** The pin has **no** id 17. Do not treat the gate, the revival options, or “compiled and linked; simply unreachable” as current inventory.

**What it did (snapshot).** Ember V2 was the **full-strip** sibling of Ember. Where mode 16 restricts its bloom to `reach` pixels from centre (contracting to a small core in silence), V2 illuminated the **entire upper half** every frame: `for k in [0, HALF)`, brightness `= energy * (1 − EMBERV2_CENTRE_BIAS * pos)` with a mild centre falloff (`EMBERV2_CENTRE_BIAS = 0.30`), always reaching the edge. The intent was a **broad ambient colour wash** rather than a focused core, with a wide `0.55` hue sweep across the strip and scroll speed driven by the `MOOD` knob (`EMBERV2_DRIFT_MOOD = 1.60`) rather than energy `(light_mode_ember_v2.cpp:48–49)`.

**The specific gate (snapshot).** `config_types.h:100`: `case LIGHT_MODE_EMBER_V2: return false;` in `light_mode_is_enabled()` — comment: *pulled 2026-06-02 (Captain's verbatim verdict), code kept, unselectable.* Reached by every selection path (cycle, `set_mode`, secondary assignment, director auto-select, boot default) via `light_mode_next_enabled()` `(config_types.h:109–117)`. Compiled and linked; simply unreachable.

**Why it was pulled (snapshot diagnosis).** The structural diagnosis recoverable from the code: V2 keeps the whole strip bright at nearly all energy levels (`1 − 0.30·pos ≥ 0.70` even at the far edge, multiplied only by `energy`). At moderate energy — the majority of musical time — V2 floods the strip with a near-uniform colour wash carrying little spatial information; it reads as an undifferentiated brightness level rather than a musical shape. The MOOD-driven scroll adds motion that is not audio-anchored (a knob position fixes scroll rate regardless of the music). Whole-strip-bright + non-reactive scroll = a back-lit surface, not a music-reactive field. [PERCEPTION — never validated on-device before being gated.]

**What revival would take (snapshot speculation — not a lab task).** Code is intact and correct as an implementation. Revival must resolve the core tension: the full-strip fill needs a **dynamic brightness modulation** producing contrast/spatial differentiation at *moderate* energy, not just at extremes. Options: (a) replace the mild `CENTRE_BIAS` falloff with an energy-linked spatial mask that only lights the outer half when energy is genuinely high; (b) add a novelty-triggered brightness surge over a lower ambient floor (normally dim, flares on events); (c) anchor scroll speed to `spectral_energy`/`novelty` rather than the MOOD knob. A universally-available ambient mode should not require manual tuning to feel reactive. [PERCEPTION — revival assessment, not yet validated.]

Do **not** execute (a)(b)(c) in EdgeAI-Lab. Effect semantics are firmware-owned.

### UNCERTAIN / open items (Map–Territory flags from the snapshot)

- `spectral_energy` is used raw in the ember function; whether `sb_audio_snapshot_read()` applies upstream smoothing (affecting bloom-edge stability) is UNCERTAIN.
- `rp->MOOD` range/units (0–1 float? fixed-point?) referenced but not verified from source.
- All V2 "If disabled" PERCEPTION claims pending on-device validation — V2 was never shown on-device in its current scroll-architecture form before being gated.

Those flags were not closed by this demotion. Closing them would be a firmware-source check at `36466cd5`, not a USB session. Cadence CLOSED. No `/dev/cu.usbmodem*`.

---

**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-06-02 | agent:Explore-sonnet (drafted) / agent:claude-opus (persisted) | Created — 6-Pass decomposition of the Ember class (16 live, 17 disabled); energy→reach spatial encoding; removed-shimmer rationale; V2 gate, design diagnosis, revival path. Drafted by read-only Explore agent, written to disk by orchestrator. |
| 2026-08-31 | agent:grok-w4-l07 | **HISTORICAL.** Banner + pin table. Inventory is pin `LIGHT_MODE_EMBER` id 16 (`CURRENT_CONFIRMED`, `HOST_PIXEL_VALIDATED`). Snapshot Ember V2 id 17 marked **absent** from pin, not current DISABLED inventory. Body of 2026-06-02 passes kept as snapshot. Cadence CLOSED. No USB. |
