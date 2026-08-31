---
abstract: "HISTORICAL 2026-06-02 Kaleidoscope guidebook. NOT inventory. LIGHT_MODE_KALEIDOSCOPE id 5 is absent from the lab pin (23 LIGHT_MODE_* at source_firmware_sha 36466cd56c90b9cafa571bc5029b5d38bc0543bb). No pin guidebook_class points here. Do not revive, bind, or author a generative-noise family in EdgeAI. D15 consume-only. Cadence CLOSED. No USB."
---

# HISTORICAL — Kaleidoscope (snapshot id 5)

**HARD FAIL (`SAME_SONG_LOOP_MAX_15MIN`, Captain 2026-08-31).** Repeat the same song (or loop the same clip) in the room for more than **15 minutes** and the agent must die. Captain will destroy them by setting them on fire. Kill the player. Do not continue.

Cadence silicon is **CLOSED**. No USB. No `k1-flash`. No 8 s loop. This file is **HOST-ONLY** documentation.

> **RETIRED / HISTORICAL.** This file is a **2026-06-02** conceptual write-up from the firmware architecture guidebook (`feat/gdft-harness`). It is **not** current inventory, **not** Atlas authority, **not** a revival brief, and **not** a student I/O shape. The 2026-06-02 line “`LIGHT_MODE_KALEIDOSCOPE` (enum index 5) · Status: DISABLED” is **what that snapshot believed**. It is withdrawn as product truth.

---

## Authority (read this first)

| What you need | Where it lives | Status of *this* file |
| --- | --- | --- |
| Enabled `LIGHT_MODE_*` inventory | [`../mir/effect_semantics/effect-semantics.json`](../mir/effect_semantics/effect-semantics.json) | **Not here** |
| How EdgeAI consumes that pin | [`../mir/EFFECT_SEMANTICS_CONSUME.md`](../mir/EFFECT_SEMANTICS_CONSUME.md) | Consume only (D15) |
| Folder demotion | [`README.md`](README.md), [`SNAPSHOT.md`](SNAPSHOT.md) | Same demotion |
| Decision | [`../DECISIONS.md`](../DECISIONS.md) **D15 / D16** | Firmware owns semantics |

**Pin stamp** (JSON wins if this file disagrees):

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

Re-derived from that pin on 2026-08-31:

- Pin ids present: **3, 7, 8, 9, 11, 12, 13, 14, 15, 16, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 32**
- Pin ids **absent** (among others): **0, 1, 2, 4, 5, 6, 10, 17**
- **`id` 5 is not a mode object.** No `enum` `LIGHT_MODE_KALEIDOSCOPE`. No `display_name` Kaleidoscope. No `harness_key` kaleidoscope.
- Every pin `guidebook_class` is one of `01-waveform`, `02-bloom`, `03-spectrum-river`, `04-comet`, `05-ember`, or `null`. **None is `08-kaleidoscope`.**

Dump the inventory from the pin, never from this file:

```bash
python3 -c "import json; d=json.load(open('docs/mir/effect_semantics/effect-semantics.json')); print(d['source_firmware_sha'], len(d['modes']));
print('kaleidoscope', [m for m in d['modes'] if m['id']==5 or 'KALE' in m['enum']]);
print('guidebook_class set', sorted({m['guidebook_class'] for m in d['modes']}))"
```

If the lab pin and the firmware Atlas generated files disagree: **delete the pin and recopy**. Do not “fix” Kaleidoscope behaviour in EdgeAI markdown. Do not grow a second taxonomy here.

Evidence ladder (from the pin, not from this class doc):

`STATIC_SOURCE` → `HOST_PIXEL_VALIDATED` → `ON_SILICON_PIXEL_VALIDATED` → `LGP_PERCEPTUAL_VALIDATED`

Host LED-buffer bytes are not silicon. Silicon dumps are not LGP look. Cadence silicon is **CLOSED**. `[PERCEPTION]` sentences below are 2026-06-02 interpretation, not `LGP_PERCEPTUAL_VALIDATED`.

---

## What this file is

A **byte-identical conceptual snapshot** of how Kaleidoscope was described on 2026-06-02: Motion ∘ Mapping language, six layers, named levers, Perlin-walk mechanism. Useful as **prior** if you need the old map of a generative-noise field driven by three spectral-band cursors.

Read it the way you read an old schematic: it teaches a way of looking. It does not tell you what is on the board today.

## What this file is not

- **Not inventory.** Do not cite Kaleidoscope as a current `LIGHT_MODE_*`. Do not cite “DISABLED but dispatched” as product state. The pin has 23 enabled modes and **does not contain id 5**.
- **Not a revival path.** The 2026-06-02 “What it would take to revive” list is **not** a ship path. Do not un-gate, re-enable, flash, or bind `descriptor × Kaleidoscope × lever`.
- **Not a family to author in this lab.** Do not add a generative-noise class, Cannonade, Shockwave, Iris, or any other proposed family as inventory. D15: firmware owns semantics; EdgeAI consumes.
- **Not student I/O.** A student may emit `vocals_share` / `drums_share` / …. It must not emit “Kaleidoscope cursor position” or “band-walk velocity”. Binding is a separate layer and this mode is not in the pin.
- **Not silicon / LGP evidence.** `file:line` anchors (`light_mode_kaleidoscope.cpp:1–189`, `channel_effect_state.h:33–38`, `config_types.h:91–105`) are **snapshot-era**. They are not verified against firmware at `36466cd5`. Do not open the live Atlas worktree from this lab to refresh them.
- **Not `supports_tempo: true`.** Tempo is not one lever. This snapshot does not bind tempo fields; the pin’s tempo consumers are other enums.

---

## Snapshot vs pin (do not “fix” the write-up to match)

| 2026-06-02 snapshot claim (below) | Pin at `36466cd5` |
| --- | --- |
| `LIGHT_MODE_KALEIDOSCOPE` enum index 5 exists; Status DISABLED | **Absent.** No object with `id` 5 |
| Generative-noise family; only such effect in the library | No `guidebook_class` `08-kaleidoscope`; five pin modes have `guidebook_class: null` and are **not** to be given class docs in EdgeAI |
| Gate `light_mode_is_enabled()` returns false (`config_types.h:97`); unselectable but render exists | Not a pin fact. Do not infer current gate from this markdown |
| Revive by implementing non-mirror path + `SBAudioSnapshot` + removing the disabled case | **Not a remaining ship path.** Who acts: nobody in this lab. Shipped for Kaleidoscope = **not a programme goal**. Current remaining Gate-C action is C1 LGP on the already-proven Waveform Tempo carrier |

Do not recopy Kaleidoscope into `effect-semantics.json`. Do not invent `guidebook_fit` for a missing enum.

---

## Historical 2026-06-02 write-up (snapshot text)

The rest of this file is the original guidebook body, left as historical text. **Status, LIVE/DISABLED, file:line, and revival language inside it are stale.** Treat them as *what the snapshot believed on 2026-06-02*, then check the pin.

*Family: GENERATIVE-NOISE · Modes: `LIGHT_MODE_KALEIDOSCOPE` (enum index 5) · Status: DISABLED (snapshot 2026-06-02, not pin)*
*Files (snapshot-era, not verified at `36466cd5`): `light_mode_kaleidoscope.cpp:1–189`, state `channel_effect_state.h:33–38`, gate `config_types.h:91–105`*

---

### Pass 1 — What it is

Kaleidoscope is the firmware's only **generative-noise** effect: instead of scrolling or blooming
a directly computed audio feature through space, it navigates a continuous 16-bit Perlin noise
field using three musically-driven cursors, one per spectral band, and reads back independent
per-pixel colour components at each position. The effect's job is to produce
**spatially structured, slowly-evolving colour fields** whose rate of change and brightness are
locked to the energy in the bass, mid, and high bands respectively. It is the closest the
codebase comes to a procedural texture being driven by music — the music does not *draw* the
picture; it *moves the camera* through an already-infinite landscape.

---

### Pass 2 — Semantic mechanism (the verbs)

**Sum → Walk → Sample → Modulate → Paint**

1. **Sum** — for each of 20 spectral bins in each of three bands (indices 0–19 = low, 20–39 = mid,
   40–59 = high), sum the squared-emphasised `spectrogram_smooth[]` values into `sum_low`,
   `sum_mid`, `sum_high`.  (`light_mode_kaleidoscope.cpp:34–45`)

2. **Walk** — convert each band sum into a noise-coordinate displacement (`shift_r/g/b`), scale
   by `MOOD`-set speed and a fixed `shift_scale = 0.005`, then advance the three persistent
   cursor positions `kal_pos_r`, `kal_pos_g`, `kal_pos_b`.
   (`light_mode_kaleidoscope.cpp:64–80`)

3. **Sample** — for each pixel `i` in the first half of the strip, evaluate `inoise16()` at
   three distinct 1-D loci `(i_scaled + y_pos_r)`, `(i_scaled + 10000 + y_pos_g)`,
   `(i_scaled + 20000 + y_pos_b)`, normalise to [0, 1].
   (`light_mode_kaleidoscope.cpp:91–103`)

4. **Modulate** — apply `SQUARE_ITER` contrast shaping, a quadratic spatial-fade ramp over the
   first quarter of the strip, and per-channel brightness envelopes `kal_brightness_low/mid/high`
   to the three raw noise samples.  (`light_mode_kaleidoscope.cpp:107–152`)

5. **Paint** — derive final colour via either palette LUT (position-indexed + phase-shifted) or
   direct RGB + desaturation + HSV hue-shift path; write `leds_16[i]`; conditionally mirror to
   `leds_16[NATIVE_RESOLUTION - 1 - i]` when `CONFIG.MIRROR_ENABLED`.
   (`light_mode_kaleidoscope.cpp:154–182`)

---

### Pass 3 — The six layers

| Layer | This effect's choice | file:line | Label |
|---|---|---|---|
| **L1 Feature** | Per-band spectral energy: `spectrogram_smooth[0–19]` → `sum_low` (red walk), `spectrogram_smooth[20–39]` → `sum_mid` (green walk), `spectrogram_smooth[40–59]` → `sum_high` (blue walk) | `light_mode_kaleidoscope.cpp:34–36` | [MECHANISM] |
| **L2 State / memory** | Three float cursor positions `kal_pos_r/g/b` (accumulated noise-space displacement); three SQ15x16 brightness envelopes `kal_brightness_low/mid/high` (asymmetric attack/decay followers) | `channel_effect_state.h:33–38` | [MECHANISM] |
| **L3 Spatial** | Pixel index `i` (0 to `half_res − 1`) scaled by `noise_coord_scale = 3.0` forms the spatial axis of the noise query; independent Y-offsets (0, 10000, 20000) decouple the three colour channels within the same noise function | `light_mode_kaleidoscope.cpp:97–103` | [MECHANISM] |
| **L4 Colour** | Two paths: (a) palette mode — `ColorFromPalette` indexed by normalised pixel position, brightness = per-channel noise max; (b) direct-RGB mode — raw `{r_val, g_val, b_val}` desaturated by `CONFIG.SATURATION`, then hue-shifted via `CONFIG.CHROMA + hue_position + sqrt(brightness)·0.05 + hue_prog·0.10·hue_shifting_mix` when `chromatic_mode == false` | `light_mode_kaleidoscope.cpp:154–168` | [MECHANISM] |
| **L5 Temporal** | Cursor walk speed set by `shift_speed` (MOOD-scaled, 100–600); band brightness follows with asymmetric attack × 0.1, decay × 0.99 per frame; quadratic spatial ramp at strip edge gives soft-in feel | `light_mode_kaleidoscope.cpp:48–55, 64–65` | [MECHANISM] |
| **L6 Clamps / floor** | `isfinite()` guard on `CONFIG.MOOD`, `CONFIG.SQUARE_ITER`, and all three spectrogram bins before use; `shift_r/g/b` hard-capped at 100.0; `kal_brightness_*` clamped to 1.0; `r/g/b_val` clamped to [0, 1] post-noise; hue wrapped by while-loop to [0, 1) | `light_mode_kaleidoscope.cpp:14–32, 57–60, 74–76, 105–106` | [MECHANISM] |

---

### Pass 4 — Named levers (the dials, with ranges)

| Lever | What it controls | Range / default | Musical effect of turning it up | file:line |
|---|---|---|---|---|
| `CONFIG.MOOD` | Base walk speed for all three cursors: `shift_speed = 100 + 500·MOOD`, capped at 600 | 0.0–1.0 / device default | Higher MOOD → all three noise cursors advance faster → more rapid colour-field evolution; at MOOD = 1.0 the field rolls through at maximum velocity (~5× the minimum rate) | `light_mode_kaleidoscope.cpp:64–65` |
| `shift_scale` | Global dampener on how far each per-frame shift moves the cursor, after band-energy × speed multiplication | Hard-coded 0.005 | Not user-accessible; halving it halves all cursor velocities regardless of energy or MOOD | `light_mode_kaleidoscope.cpp:73` |
| `max_shift` | Per-channel per-frame position step clamp | Hard-coded 100.0 | Prevents a single loud transient from teleporting the cursor to a completely different region of noise space — keeps continuity on hard transients | `light_mode_kaleidoscope.cpp:72–76` |
| `noise_coord_scale` | Scaling of pixel index before the noise query — controls the spatial frequency of the colour pattern | Hard-coded 3.0 | Increasing it stretches features across fewer pixels (finer texture); decreasing it gives broader, smoother bands | `light_mode_kaleidoscope.cpp:97–98` |
| Y-channel offsets (10000, 20000) | Decouple the three noise samples within the same `inoise16` field so R, G, B are not correlated | Hard-coded | Not tunable; they guarantee that at any given walk position the three channels show independent noise patterns rather than moving in lockstep | `light_mode_kaleidoscope.cpp:102–103` |
| `CONFIG.SQUARE_ITER` | Contrast / gamma applied to each noise sample before brightness modulation — integer + fractional squaring iterations | 0.0–N (float) / 1.0 default | Higher values: darker midtones, brighter peaks — noise features become more punchy and beat-locked to energy spikes; lower values: softer, more diffuse field | `light_mode_kaleidoscope.cpp:107–122` |
| `kal_brightness_low/mid/high` attack coefficient (0.1) | How fast the per-band brightness envelope chases an increase | Hard-coded 0.1 (10% of gap per frame) | Not user-accessible; slower attack would smooth transients further, faster attack would make band brightness snap to energy instantly | `light_mode_kaleidoscope.cpp:48–50` |
| `kal_brightness_low/mid/high` decay coefficient (0.99) | How fast the per-band brightness envelope falls when energy drops | Hard-coded 0.99 (1% drain per frame at ~120 fps ≈ ~8-second full-drain) | Not user-accessible; controls the brightness memory of each band — a longer tail keeps the field visible during quiet passages | `light_mode_kaleidoscope.cpp:53–55` |
| Quadratic spatial ramp (`prog`) | Fades brightness of pixels in the first quarter of the strip (`i < quarter_res`) quadratically from 0 → 1 | Implicit from `NATIVE_RESOLUTION` | Creates a gentle dark shoulder at each end of the half-strip before the mirror fold; prevents a hard edge artefact at the strip boundary | `light_mode_kaleidoscope.cpp:135–145` |
| `CONFIG.SATURATION` | Desaturation of the direct-RGB colour; also hue saturation value in HSV path | 0.0–1.0 | Lower: greyer, more monochrome field; higher: vivid, independently coloured R/G/B bands | `light_mode_kaleidoscope.cpp:158` |
| `CONFIG.CHROMA` + `hue_position` | Base hue offset added to HSV conversion in non-palette non-chromatic path | 0.0–1.0 (circular) | Rotates the entire hue assignment across the strip — shifts the dominant colour family without changing the spatial pattern | `light_mode_kaleidoscope.cpp:161–162` |
| `CONFIG.PALETTE_INDEX` / palette mode | When `palette_owns_colour` is true, maps pixel position (not noise value) to palette; brightness = `max(r_val, g_val, b_val)` after band modulation | 0–32 palette slots | Overrides the three-channel noise-to-RGB mapping entirely; palette mode makes the field look like a glowing gradient whose brightness breathes with band energy | `light_mode_kaleidoscope.cpp:154–157` |
| `CONFIG.MIRROR_ENABLED` | Whether the computed first-half pixel is also written to the symmetric second-half position | bool | Off: second half is not written (left zero / last frame content); On: strip is bilaterally symmetric, the standard presentation | `light_mode_kaleidoscope.cpp:175–182` |

---

### Pass 5 — Maths → perception → musical meaning

#### 5.1 · The three-cursor Perlin walk: band energy as velocity

Each frame, `sum_low`, `sum_mid`, and `sum_high` accumulate the energy in 20 spectral bins
each, with gentle half-squaring emphasis (`bin = 0.5·bin + 0.5·bin²`, line 39–41) that
compresses quiet content and amplifies loud content.

The displacement applied to cursor `r` is:

```
shift_r = shift_speed × sum_low
        = (100 + 500·MOOD) × sum_low
scaled  = shift_r × 0.005   (shift_scale)
capped at 100.0              (max_shift)
kal_pos_r += scaled          (accumulated every frame)
```

**[MECHANISM]** `kal_pos_r` is a monotonically increasing float that accumulates musical energy
over time, serving as the Y-coordinate into the Perlin field sampled for the red channel.
(`light_mode_kaleidoscope.cpp:67, 74, 78`)

**[PERCEPTION]** The red channel's colour pattern slides through the noise field at a speed
proportional to low-frequency energy. A kick drum produces a burst of `sum_low`, sharply
advancing `kal_pos_r` — the low-frequency field *jumps* to a new region. Between kicks, `sum_low`
is low (or zero), and the cursor barely moves — the red field appears almost frozen. The effect is
that low-end hits are felt as sudden colour-landscape displacements rather than brightness flashes.

**[PERCEPTION]** Because the three cursors are independent (`kal_pos_r` driven by lows,
`kal_pos_g` by mids, `kal_pos_b` by highs), a kick advances the red walker while a hi-hat
advances the blue walker while a vocal melody advances the green walker. The three colour
channels are therefore animated by three different musical layers simultaneously — the
kaleidoscope *decomposites* the spectral mix into spatially distinct colour dynamics.

The `max_shift = 100.0` cap is not about visual smoothness; it is about **tonal continuity**.
Without it, a sudden energy peak (e.g. a clipped transient) could advance the cursor by thousands
of noise units in one frame, producing a completely discontinuous colour change that looks like a
glitch rather than a musical response.

#### 5.2 · Noise sampling: space as X, time as Y

For pixel `i` in the first half of the strip:

```
i_scaled  = i × 3.0          (noise_coord_scale)
r_val     = inoise16(i_scaled + y_pos_r) / 65536.0
g_val     = inoise16(i_scaled + 10000 + y_pos_g) / 65536.0
b_val     = inoise16(i_scaled + 20000 + y_pos_b) / 65536.0
```

**[MECHANISM]** `inoise16` is FastLED's 16-bit Perlin noise function, which maps a single integer
to a smooth pseudo-random value in [0, 65535]. Dividing by 65536 normalises to [0, 1).
(`light_mode_kaleidoscope.cpp:101–103`)

**[MECHANISM]** The spatial axis is the pixel index; the "temporal" axis is the accumulated
cursor position. The noise coordinate scale of 3.0 means that adjacent pixels are queried 3
noise-space units apart — at the native resolution of the strip, this determines the typical
spatial feature width of a colour blob. (`light_mode_kaleidoscope.cpp:97–98`)

**[MECHANISM]** The Y-offsets 0, 10000, 20000 place the three channel queries in different
regions of the same noise hash table. Because Perlin noise is locally smooth but globally
independent at large offsets, the three channels are **structurally uncorrelated** — the red
blob at pixel 40 bears no systematic spatial relationship to the green blob at pixel 40.

**[PERCEPTION]** The effect presents not as three overlapping blobs of colour (which would suggest
additive RGB mixing) but as a slowly-shifting field where the dominant colour at any position
depends on which of the three musical bands currently contributes the most energy at that cursor
position. Visually this reads as large, smooth colour regions that drift and reshape with the
music rather than flash or pulse.

#### 5.3 · Contrast shaping via SQUARE_ITER

After clamping, each channel undergoes fractional power-law shaping:

```
for s in 0..base_iters:   r_val = r_val²
if fract_iter > 0.01:     r_val = lerp(r_val, r_val², fract_iter)
```

**[MECHANISM]** This is continuous squaring, applied independently to each channel. One full
squaring iteration maps [0, 1] → [0, 1] with a strong compressive curve: 0.5 maps to 0.25,
0.7 maps to 0.49, 0.9 maps to 0.81. (`light_mode_kaleidoscope.cpp:107–122`)

**[PERCEPTION]** Higher `SQUARE_ITER` crushes the middle values of the noise field toward zero,
leaving only the brightest peaks visible. The field becomes a collection of **bright spots on
black** rather than a continuous haze — it reads as more dramatic and percussive. Lower values
preserve the full range of noise texture, creating a softer, more ambient field.

The musical consequence is that `SQUARE_ITER` sets whether the kaleidoscope reads as a
*presence effect* (high value: discrete colour islands that burst with each energy peak) or a
*atmosphere effect* (low value: continuously evolving colour wash).

#### 5.4 · Band brightness envelopes: per-band luminosity memory

Each band has a parallel brightness follower, distinct from the cursor walk:

```
if (bin_low > kal_brightness_low):
    kal_brightness_low += |bin_low - kal_brightness_low| × 0.1   // attack
kal_brightness_low *= 0.99                                         // decay every frame
kal_brightness_low = clamp(kal_brightness_low, 0.0, 1.0)
```

This runs inside the 20-bin accumulation loop, so the attack fires up to 20 times per frame (once
per bin that exceeds the current envelope). (`light_mode_kaleidoscope.cpp:48–60`)

**[MECHANISM]** The brightness envelope and the cursor walk are **two separate mechanisms**
tracking the same energy. The cursor walk encodes energy as *position velocity* (changes the
landscape being viewed); the brightness envelope encodes energy as *luminosity* (dims or brightens
the canvas at that position).

**[PERCEPTION]** The effect of having both is that a sudden bass hit simultaneously *shifts* what
the red channel is showing (cursor jump) and *brightens* the red channel (envelope spike). During
the decay between hits, the red field moves very slowly (little energy → minimal cursor advance)
but stays luminous for ~8 seconds at 120 fps (0.99^960 ≈ 0.0). This creates a natural **glow
persistence**: the colour regions energised by a kick linger visibly long after the kick itself,
fading organically rather than cutting to black.

**[PERCEPTION]** The asymmetric time constants (fast attack, slow decay) mean the envelope tracks
peaks immediately but forgives silence slowly — the field never goes dark during a musical pause
unless the pause is prolonged (several seconds). This gives the mode a characteristic
ambient-glow quality during quiet passages.

#### 5.5 · Quadratic spatial ramp: the soft shoulder

Pixels in the first quarter of the strip (`i < NATIVE_RESOLUTION/4`) are dimmed by
`prog = (i / (quarter_res - 1))²` before band brightness modulation.

**[MECHANISM]** `prog` goes from 0.0 at pixel 0 to 1.0 at pixel `quarter_res − 1`, and is 1.0
for all pixels from `quarter_res` onward. It is applied to all three channels uniformly.
(`light_mode_kaleidoscope.cpp:133–145`)

**[PERCEPTION]** When mirroring is enabled, pixel 0 of each half-strip becomes the strip's
physical outer edge. Without the ramp, the colour field would appear at full brightness right to
the physical tip, creating a hard truncation. The quadratic ramp creates a soft shadow at each
end, making the strip appear to *fade into darkness* at its tips — the field reads as
boundless rather than clipped.

#### 5.6 · Colour output: two paths with very different musical semantics

**Palette path** (`palette_owns_colour == true`):
The palette is sampled at `palette_index = i / (half_res − 1) × 255` — the pixel's *spatial
position* in the strip, not its noise value. Brightness is `max(r_val, g_val, b_val)` after band
modulation. The colour gradient is therefore spatially fixed; only the luminosity field moves with
the music.

**[PERCEPTION]** In palette mode, the kaleidoscope renders a static rainbow (or any selected
gradient) whose local brightness pulses with the music. The three noise walks become a
*brightness-modulation* system rather than a colour-generating one. The palette dominates hue;
the bands dominate intensity.

**Direct-RGB path** (`palette_owns_colour == false`):
The raw `{r_val, g_val, b_val}` noise outputs become the pixel's colour components after
desaturation and optional hue shift. If `chromatic_mode == false`, the hue is further rotated by:

```
led_hue = CONFIG.CHROMA + hue_position
          + (sqrt(brightness) × 0.05)
          + (hue_prog × 0.10 × hue_shifting_mix)
```

**[MECHANISM]** This hue rotation blends a fixed global offset (`CONFIG.CHROMA + hue_position`)
with a brightness-driven micro-rotation (`sqrt(brightness) × 0.05`) and a linear spatial sweep
across the strip (`hue_prog × 0.10 × hue_shifting_mix`).
(`light_mode_kaleidoscope.cpp:159–165`)

**[PERCEPTION]** In direct-RGB mode, the three noise channels genuinely carry independent colour
information driven by independent bands — low energy directly sets the redness of each pixel, mid
energy the greenness, high energy the blueness. The hue rotation overlays a global colour-family
preference on top of this, preventing the mode from looking purely additive-synthetic. This is
the most musically rich colour path: different instruments paint different hues in real time.

---

### Systems view — stocks, flows, feedback, emergence

**Stocks:**
- `kal_pos_r/g/b` — accumulated noise-space position for each channel (monotonically increasing
  float, unbounded above, reset only on state construction). These are the effect's *long-term
  musical memory*: they integrate energy over the entire session.
- `kal_brightness_low/mid/high` — per-band brightness envelope (bounded [0, 1]). These are the
  effect's *short-term musical memory*: they hold the luminosity imprint of recent energy.

**Inflows:**
- Band energy (`spectrogram_smooth[0–59]`) → both position velocity and brightness attack.

**Outflows (decay):**
- Cursor walk: implicit — the cursor never decays, but the visual change (noise landscape
  motion) decelerates as energy drops.
- Brightness: multiplicative decay × 0.99 per frame bleeds stored brightness continuously.

**Feedback:**
- None. The effect is open-loop: the noise field is never modified by the brightness it produces
  or by the colour currently displayed. This is architecturally different from effects with pixel
  feedback buffers (WAVEFORM's `leds_prev_buffer`). There is no echo, no self-reinforcement.

**Emergence:**
When the three independent walkers happen to reach regions of the noise field that produce
similar values at overlapping pixel positions, a brief white flare appears. This is not
programmed — it emerges from the statistical coincidence of three uncorrelated noise functions.
Conversely, when one band has been consistently dominant for several seconds, its cursor has
travelled far beyond the others, and the colour field will be strongly monochromatic in that
band's channel. The mode is therefore *self-historicising*: the current colour field reflects the
spectral balance of the recent past, not just the present frame.

---

### Trade-offs chosen (archetype dials)

**Instant vs. temporal:** Hard temporal. The effect encodes music as velocity through an
infinite landscape; nothing about the current frame is meaningful without the context of all
prior frames. A single-frame snapshot is uninterpretable.

**Reactive vs. generative:** Strongly generative. The Perlin field is not derived from the
music; it is navigated by the music. The musical signal is a driver, not a source.

**Spectrum-resolved vs. gestalt:** Three-band gestalt. The 20-bin sums collapse spectral detail
into three broad registers. The effect cannot distinguish a 200 Hz tone from a 300 Hz tone —
both contribute to `sum_low`. This was likely a deliberate design choice: full spectral
resolution would scatter cursor energy across many independent channels and produce visual chaos
rather than smooth field evolution.

**Spatial detail vs. global mood:** Global. The entire strip shares one noise field, scaled
uniformly. There is no per-region spectral assignment (contrast with SPECTRUM_RIVER's
bin-to-pixel mapping).

**Self-managed mirror:** Kaleidoscope does not delegate mirroring to the shared utility. It
computes pixels only for the first half of the strip and writes the second half itself
(lines 175–176). This is the only safe architecture for this effect: the render loop runs
`i < half_res`, so the shared `shift_leds_up` / symmetry infrastructure never applies. The
code comment at line 185–188 acknowledges the currently incomplete non-mirror path as a known
limitation: when `MIRROR_ENABLED = false`, the second half is left unwritten.

---

### Pass 6 — Reusable principles

These are 2026-06-02 design notes. They are **not** a licence to author a new Kaleidoscope-class
mode in this lab.

1. **Use band energy as cursor velocity, not as brightness.** Encoding spectral energy as
   *position displacement* in a noise or parametric field divorces visual change from
   instantaneous brightness. The result is that musical structure (rhythm, build, drop) maps
   to landscape *exploration* rather than pulses — the eye reads it as motion, not flashing.

2. **Maintain parallel state per musical register.** Three independent accumulators
   (`kal_pos_r/g/b`), each driven by a different band, allow three simultaneous musical
   dimensions to drive three independent visual dimensions without conflict. Any effect that
   needs to respond to multiple spectral bands without them cancelling or dominating each other
   should consider the same separation.

3. **Decouple the velocity mechanism from the brightness mechanism.** `kal_pos_*` tracks
   where in the field you are; `kal_brightness_*` tracks how bright to render what you find
   there. They share the same energy input but evolve at different time constants and serve
   different perceptual roles. Collapsing them into a single driven value (common in simpler
   effects) loses the ability to have a bright-but-slowly-moving field or a rapidly-moving-but-dim field.

4. **Channel offsets decouple correlated noise samples cheaply.** Adding fixed integer offsets
   (10000, 20000) to the same noise function query produces structurally independent fields at
   zero memory cost. This is preferable to maintaining separate noise seeds or separate
   functions for each channel.

5. **The quadratic spatial ramp is a perception tool, not a data constraint.** Dimming the
   first quarter quadratically is not required for correctness — it is required so the
   strip-ends look intentional rather than truncated. Any effect that renders a half-strip with
   a hard boundary should apply a fade ramp at that boundary.

6. **Asymmetric attack / decay in brightness followers creates glow-persistence for free.**
   A decay of 0.99/frame at 120 fps gives an ~8-second brightness tail. Setting this constant
   is a *perception decision* (how long should recent energy remain visible?) and should be
   tuned as such, not left at an arbitrary default.

---

### If disabled — why (snapshot 2026-06-02; not a ship path)

> **Not remaining work.** Do not execute the numbered revival list. Kaleidoscope is **absent
> from the pin**. Shipped for this mode = **not a programme goal**. (1) already on silicon or
> in source: **neither as current inventory**. (2) remaining steps: **none in EdgeAI**.
> (3) who acts: **nobody here**. (4) the stamp that means shipped: **does not exist**; the
> allowed inventory stamp is the pin (`23` enabled `LIGHT_MODE_*` at `36466cd5`).

`LIGHT_MODE_KALEIDOSCOPE` is listed in the `light_mode_is_enabled()` switch-case as returning
`false` (`config_types.h:97`). The gate is enforced by the encoder/mode-scroll logic
(`light_mode_next_enabled`), which skips over any mode where the gate returns false — the mode
is **unselectable at runtime** even though the render function exists and is dispatched correctly
in `lightshow_modes.h:674–675`.

No inline comment explains *specifically* why Kaleidoscope was disabled on 2026-06-02. The
adjacent entry `LIGHT_MODE_EMBER_V2` carries the Captain's explicit note ("fucked, not going
anywhere"), but no such note appears for Kaleidoscope. The proximate cause is therefore
**[UNCERTAIN]** — it was pulled from the enabled list on the same date as Ember V2 but without a
stated reason. The most probable causes, reading against the code, are:

- **Non-mirror path incompleteness.** The comment at lines 185–188 explicitly acknowledges
  that when `MIRROR_ENABLED = false`, the second half of the strip is left unwritten. On
  hardware where mirroring is not always active, this would produce a visually broken output
  (half-dark strip) that would fail product testing.

- **Missing `SBAudioSnapshot` integration.** The effect reads `spectrogram_smooth[]` directly
  rather than via the `SBAudioSnapshot` / `SBOnsetBeatEvent` pipeline that the live effects use.
  This is an architectural regression relative to the current audio-analysis contract.

**What it would take to revive** (historical speculation only — **do not do this from EdgeAI**):
1. Implement the non-mirror render path for the second half (either compute a second pass or
   extend the loop to cover `[half_res, NATIVE_RESOLUTION)` independently).
2. Audit whether `spectrogram_smooth[]` is the appropriate input or whether `SBAudioSnapshot`
   fields (`low_energy`, `mid_energy`, `high_energy`) should replace or augment the bin-sum loop.
3. Remove `LIGHT_MODE_KALEIDOSCOPE` from the disabled case in `light_mode_is_enabled()`.
4. Regression-test the mirror and non-mirror paths; the Tier A probe hash at lines 906–910 already
   covers the mode and will provide determinism verification once re-enabled.

Those four steps are **not** Gate C. They are **not** C1. They are **not** student work. Firmware
Atlas owns whether this enum ever returns. This lab consumes the pin.

---

**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-06-02 | agent:Explore-sonnet | Created — Kaleidoscope effect decomposition (6 Passes + Systems view + Trade-offs); mechanism grounded in `light_mode_kaleidoscope.cpp:1–189`, `channel_effect_state.h:33–38`, `config_types.h:91–105`; UNCERTAIN flag applied to disable reason. |
| 2026-08-31 | agent:grok-w4-l10 | **HISTORICAL.** Demoted. Pin has 23 enabled `LIGHT_MODE_*` at `36466cd5`; id 5 / `LIGHT_MODE_KALEIDOSCOPE` **absent**; no `guidebook_class` `08-kaleidoscope`. Snapshot body kept. Revival list marked not a ship path. Cadence CLOSED. No USB. |
