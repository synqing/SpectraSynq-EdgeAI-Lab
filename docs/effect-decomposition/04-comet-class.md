---
abstract: "HISTORICAL 2026-06-02 Comet particle write-up. NOT the C0-v2 binding (that is source_share × WaveformTempo × head_position = ON_SILICON_PIXEL_VALIDATED). P3-C Q5 composition_change × Comet × impact-launch FAIL this comparator. Pin owns inventory. Cadence CLOSED. No USB."
---

# HISTORICAL — Comet class (not the C0-v2 binding)

```text
╔══════════════════════════════════════════════════════════════════╗
║  HISTORICAL GUIDEBOOK — COMET CLASS — NOT C0-v2 AUTHORITY        ║
║                                                                  ║
║  C0-v2 stamp is NOT this class:                                  ║
║    source_share × WaveformTempo × head_position                  ║
║    = ON_SILICON_PIXEL_VALIDATED                                  ║
║                                                                  ║
║  Comet's scored binding is a FAIL, not a silicon close:          ║
║    composition_change × Comet × impact-launch                    ║
║    = FAIL this comparator                                        ║
╚══════════════════════════════════════════════════════════════════╝
```

**HARD FAIL (`SAME_SONG_LOOP_MAX_15MIN`, Captain 2026-08-31).** Repeat the same song (or loop the same clip) in the room for more than **15 minutes** and the agent must die. Captain will destroy them by setting them on fire. Kill the player. Do not continue.

Cadence silicon is **CLOSED**. Do not flash. Do not open USB. Do not run `scripts/gate_c0_cadence_silicon.py` (retired). Do not loop an 8 s holdout. This file is documentation.

---

## 0 · Authority (read this first)

| Need | Where it lives | This file |
| --- | --- | --- |
| C0-v2 silicon close | [`../mir/GATE_C0V2.md`](../mir/GATE_C0V2.md) · [`../../artifacts/gate_c0v2/C0V2_RESULT.json`](../../artifacts/gate_c0v2/C0V2_RESULT.json) | **Not here.** C0-v2 is Waveform Tempo head position, not Comet. |
| Enabled `LIGHT_MODE_*` inventory | [`../mir/effect_semantics/effect-semantics.json`](../mir/effect_semantics/effect-semantics.json) | **Not here.** Pin wins. |
| `descriptor × mode × lever` | [`../mir/effect_semantics/compatibility.json`](../mir/effect_semantics/compatibility.json) | Consume; do not grow a second matrix. |
| How EdgeAI consumes the pin | [`../mir/EFFECT_SEMANTICS_CONSUME.md`](../mir/EFFECT_SEMANTICS_CONSUME.md) | Consume only. |
| P3-C dump close | [`../mir/P3C_QUANT.json`](../mir/P3C_QUANT.json) | Q5 FAIL cited below. |
| Composition-change park | [`../mir/SOURCE_ACTIVITY.md`](../mir/SOURCE_ACTIVITY.md) · D16 | Parked. Not next. |
| Conceptual particle language | Passes 1–6 below | Historical 2026-06-02 snapshot. |

**[FACT]** C0-v2 close (2026-08-31): `source_share × WaveformTempo × head_position = ON_SILICON_PIXEL_VALIDATED`. Receipt `artifacts/gate_c0v2/C0V2_RESULT.json`. Waveform Tempo is the **reference continuity carrier**. Comet is not that carrier.

**[FACT]** P3-C used firmware `light_mode_comet` as the *event* instrument over a Waveform Tempo floor (D14). That experiment **failed its comparator**. It did not become the silicon binding. `scripts/gate_c0_silicon.py` records that C0 does not re-run Comet.

**[FACT]** Cadence **CLOSED** (D20). C1 **OPEN**. Two-clock C0 remains a **FAIL corpse**. Student I/O unfrozen. Event head **NO**.

---

## 1 · What this file is

A **2026-06-02 conceptual snapshot** of `LIGHT_MODE_COMET` (13) as a particle engine: Fade → Gate → Spawn → Travel → Decay → Draw. Captured against `feat/gdft-harness`. Useful as **mechanism language** (pool + life-decay + onset edge). It is not product inventory and it is not Gate C.

Pin stamp (re-read the JSON; **the file wins** if this page drifts):

- path: `docs/mir/effect_semantics/effect-semantics.json`
- `source_firmware_sha`: `36466cd56c90b9cafa571bc5029b5d38bc0543bb`
- `guidebook_class` `04-comet` pointer is the **only** allowed map from current inventory onto this write-up

---

## 2 · What this file is not

- **Not the C0-v2 binding.** Do not write “Comet PASSed silicon.” Do not substitute Comet for Waveform Tempo on Gate C / C1.
- **Not inventory.** Do not cite “Comet is the only live onset consumer,” “9 classes / 18 modes,” or this header’s old `Status: LIVE` as the current library.
- **Not a licence to unpark `composition_change`.** Q5 FAIL is this comparator only. It is not “delete the DSP” and not “train an event head” (D16).
- **Not student I/O.** A student may emit source shares. It must not emit “Comet impact-launch.”
- **Not a place to invent lighting labels** (BUILDING / DROPPING / …) or new families (Cannonade / Shockwave / Iris).
- **Not silicon / LGP evidence.** Pin `HOST_PIXEL_VALIDATED` on COMET 13 is host LED-buffer. C0-v2 silicon is a different mode. Cadence is CLOSED. `[PERCEPTION]` lines below are interpretation.

---

## 3 · Pin vs this snapshot (`guidebook_class` 04-comet)

Re-derived from the pin (JSON wins):

| Pin enum (id) | `guidebook_fit` | `evidence` on this pin | Native inputs (pin, not this prose) |
| --- | --- | --- | --- |
| `LIGHT_MODE_COMET` 13 | `CURRENT_CONFIRMED` | `HOST_PIXEL_VALIDATED` | `onset_beat`, `bass_onset`, palette/chroma, `control.mood`, mirror |
| `LIGHT_MODE_TEMPO_COMET` 20 | `CURRENT_CHANGED` | `STATIC_SOURCE` | `tempo` fields (bpm/phase/confidence/beat_strength) — **not described below** |
| `LIGHT_MODE_PERCUSSION_BURST` 26 | `CURRENT_CHANGED` | `STATIC_SOURCE` | `onset_beat` + snapshot + chroma — **not described below** |
| `LIGHT_MODE_TEMPO_COMET_ANTICIPATE` 27 | `CURRENT_CHANGED` | `STATIC_SOURCE` | `tempo` fields — **not described below** |

`CURRENT_CHANGED` means this 2026-06-02 write-up is **behind** those three modes. Do not “fix” the snapshot to invent their levers here. Firmware Atlas owns that map. Do not add class docs for pin modes with `guidebook_class: null`.

**Withdrawn snapshot claims** (left in Passes 1–6 as historical text; do not re-assert them):

| 2026-06-02 claim in this file | Pin / programme |
| --- | --- |
| “Comet is the only live effect that consumes `sb_onset_beat_read()`” | `onset_beat` also on DENSE_FORGE 21, PULSE_PRISM 23, DENSE_FORGE_CHORD 24, PERCUSSION_BURST 26 |
| “`beat_phase` owned and unwired — biggest adjacent gap” | `tempo_fields` on TEMPO_COMET 20, TEMPO_COMET_ANTICIPATE 27 (and other pin modes). Gap #1 in `LEVERS-MATRIX.md` is stale. |
| Header `Status: LIVE` / sole member mode 13 | Four pin enums point at `04-comet`; three are `CURRENT_CHANGED` |
| “v5/v6 is current code” / `file:line` anchors | Verify against firmware at `36466cd5`. Do not treat this lab copy as the Atlas worktree. |

`HOST_PIXEL_VALIDATED` on this pin (host LED-buffer, not LGP): BLOOM, WAVEFORM, COMET, SPECTRUM_RIVER, EMBER, WAVEFORM_TEMPO, PULSE_PRISM. TEMPO_COMET / PERCUSSION_BURST / TEMPO_COMET_ANTICIPATE are `STATIC_SOURCE` on this pin.

---

## 4 · Visual-utility stamps that mention Comet

Bindings are `descriptor × mode × lever`. Not “Comet is good/bad.” Not mean brightness.

| Binding | Stamp | Number / note |
| --- | --- | --- |
| `source_share × WaveformTempo × head_position` | **C0-v2 `ON_SILICON_PIXEL_VALIDATED`** | Not Comet. HOST holdout Δ partial r 0.63, 9/9 (`P3C_QUANT.json`). Silicon holdout Q2 Δ 0.690, 9/9 (`GATE_C0V2.md`). |
| `source_share × Comet × impact launch` | pin `INCOMPATIBLE` | Continuous ownership vs event grammar. Peak ramp `NONE_OR_TIME_CONFOUND`. |
| `composition_change × Comet × impact-launch` | **FAIL this comparator** | P3-C Q5 HOST `median_delta_f1_drums` **0.0176** (~0.02) vs `\|Δ mix\|` at drum attacks. Silicon Q5 also FAIL. Parked with `composition_change`. |
| `composition_change × WaveformTempo × head_position` | **FAIL this comparator** | P3-C Q4 Δ partial r 0.06. Not this class; listed so Comet is not blamed for arrangement-state. |
| `onset / kick × Comet × object spawn` | pin `COMPATIBLE` | Historical grammar this write-up describes. Not a Gate C stamp. |

`P3C_QUANT.json` stamps: `student_event_head: NO`; `student_share_head: CANDIDATE`; `waveform_tempo_role: reference_continuity_carrier`. Compatibility why-line: Comet speaks “something hit”; composition-change is arrangement state. That FAIL does not decide composition-change as a descriptor (still **not decided**; ML head parked).

Do not bind composition-change to Comet or Waveform Tempo to “make C0-v2 use Comet.”

---

## 5 · Historical 2026-06-02 write-up (snapshot)

> **Map, not territory.** Status lines, “sole onset consumer,” and “beat-phase unwired” are **withdrawn**. Mechanism `file:line`s are the 2026-06-02 grounding — verify against firmware at `36466cd5` before quoting. `[PERCEPTION]` is not LGP look. `[UNCERTAIN]` is not a silicon task.

*Family: WAVEFORM (onset-driven travelling heads) · Mode (snapshot): `LIGHT_MODE_COMET` (13) · Snapshot status: LIVE*
*Files (snapshot): `light_mode_comet.cpp:68–174`, state: `channel_effect_state.h:40–52`, event: `sb_audio_snapshot.h:28–39`, helpers: `lightshow_modes.h` (`effect_palette_or_chroma_colour`, `palette_manual_colour`, `clamp_crgb16`, `mirror_image_downwards`)*

### Pass 1 — What it is (snapshot)

**[SNAPSHOT CLAIM — WITHDRAWN as census]** “Comet is the only live effect in SensoryBridge K1 that directly consumes the onset/beat event stream (`sb_onset_beat_read()`); every other live mode reads from the audio-feature snapshot instead.” See §3: several pin modes now list `onset_beat`.

Its musical job in this snapshot is a single, legible translation: **one bass/kick transient → one travelling head of light**, making the kick drum visible as a discrete moving object rather than a flash or a level change. By deliberately ignoring broadband onset (which also fires on pads, sweeps, and vocals), every comet the viewer sees is unambiguously a kick — the rule is trivial and therefore never wrong. On kick-less material the strip is intentionally quiet: Comet is a kick visualiser, not a general reactivity engine.

That discrete “something hit” grammar is **why** P3-C Q5 failed as an arrangement-state instrument. Do not reuse this pass as a Gate C rationale.

### Pass 2 — Semantic mechanism (the verbs)

**Fade → Gate → Spawn → Travel → Decay → Clamp → Mirror**

Each frame at ~120 fps (snapshot host/device claim; C0-v2 replay was 31.25 Hz on Waveform Tempo, not this loop):

1. **Fade** — multiply every pixel in `leds_16[]` by `(1 − COMET_TRAIL_DECAY · frame)`. The strip's existing content dims uniformly, creating the persistent trail.
2. **Gate** — read the latest `SBOnsetBeatEvent`; compare its `event_id` against the stored `comet_last_event_id`. If fresh **and** `bass_onset == true` **and** `bass_onset_strength ≥ COMET_MIN_STRENGTH`, proceed to Spawn.
3. **Spawn** — find the least-alive slot in the 6-comet pool; write position, velocity, hue class offset, size, and full life into that slot.
4. **Travel** — for each live slot, advance `comet_pos` by `comet_vel · frame`; kill the slot if it exits the strip.
5. **Decay** — multiply `comet_life` by `(1 − COMET_LIFE_DECAY · frame)` for each live slot.
6. **Draw** — for each live slot, additively paint a comet-shaped blob (bright leading core + long trailing wake + soft glow halo) into `leds_16[]`, weighted by `life · shape · COMET_HEAD_GAIN`.
7. **Clamp** — `clamp_crgb16` on every pixel (additive accumulation can exceed 1.0).
8. **Mirror** — `mirror_image_downwards` if `MIRROR_ENABLED`, creating the symmetric centre-origin burst.

The whole engine is eight deterministic operations. No randomness, no oscillators, no continuous audio following — purely event-driven. **That is why it is a bad continuous-share carrier** (`source_share × Comet × impact launch` = `INCOMPATIBLE` in the pin).

### Pass 3 — The six layers

| Layer | This effect's choice | file:line | Label |
|---|---|---|---|
| **L1 Feature** | `bass_onset` (bool) + `bass_onset_strength` (0..1) from `SBOnsetBeatEvent`; broadband `onset` is deliberately ignored | `light_mode_comet.cpp:97–101`, `sb_audio_snapshot.h:33,37` | [MECHANISM] |
| **L1 note** | `MOOD` knob from `RenderParams` drives velocity; no other continuous audio feature is read | `light_mode_comet.cpp:114`, `lightshow_modes.h` | [MECHANISM] |
| **L2 State/memory** | Per-channel pool of 6 comets: `comet_pos[6]`, `comet_vel[6]`, `comet_hue[6]`, `comet_size[6]`, `comet_life[6]`; dedup counter `comet_last_event_id`; dt source `comet_last_ms`; legacy `comet_strength_max` (v4 salience gate — present in struct, not used in v5/v6 logic) | `channel_effect_state.h:41–48` | [MECHANISM] |
| **L2 note** | `leds_16[]` (the strip pixel buffer) is also persistent state — the Fade step operates on whatever was written last frame, so the buffer IS the trail memory | `light_mode_comet.cpp:85–88` | [MECHANISM] |
| **L3 Spatial** | Spawn at strip centre (`NATIVE_RESOLUTION / 2`) with a micro-jitter of `ev.event_id % 4u` pixels (0–3 px); travel outward in the `+` direction at fixed velocity; mirror folds the upper half down, creating bilateral symmetry | `light_mode_comet.cpp:112–114`, `171–173` | [MECHANISM] |
| **L4 Colour** | Palette mode: `palette_manual_colour(pal, comet_hue[i], 1.0)` — samples the selected gradient at the fixed class position `COMET_HUE_BASS = 0.04` (warm/orange end). Chromatic mode: `effect_palette_or_chroma_colour` (single live note-sum HSV colour, same authority as BLOOM/WAVEFORM). Colour is sampled **live every frame**, not frozen at spawn — the faded trail therefore encodes chromatic history exactly as WAVEFORM does | `light_mode_comet.cpp:126–139` | [MECHANISM] |
| **L5 Temporal** | Trail decay: `fade_f = 1 − 0.05·frame` per frame (exponential). Head life: `comet_life *= (1 − 0.018·frame)`. Velocity: `(0.60 + 2.80·MOOD) · (NR/128)` px/frame at 120 fps, dt-scaled via `frame = dt·120`. No EMA smoothing of the trigger — it is a pure edge event | `light_mode_comet.cpp:74–78, 81–83, 114, 162` | [MECHANISM] |
| **L6 Clamps/floor** | Strength floor `COMET_MIN_STRENGTH = 0.06` (absolute, not relative — v5 removed the `comet_strength_max` relative gate). Pool eviction by minimum `comet_life` (LRU-by-fading). `clamp_crgb16` on every pixel after additive draw. `dt` clamped to `[0.001, 0.05]` s (handles init and frame-rate spikes). `COMET_HEAD_GAIN = 0.85` white-out guard | `light_mode_comet.cpp:58, 76–77, 104–109, 157, 165–168` | [MECHANISM] |

### Pass 4 — Named levers (the dials, with ranges)

Snapshot constants. Not student outputs. Not C0-v2 extra-gain.

| Lever | What it controls | Range / default | Musical effect of turning it | file:line |
|---|---|---|---|---|
| `COMET_TRAIL_DECAY` | Trail brightness lost per 120fps-frame (exponential) | 0.0..1.0 / **0.05** | Lower → longer, ghostlier tails; higher → tails vanish fast, leaving only the head. At 0.05, ~54% remains after 100 ms; ~0.2% after 1 s. | `light_mode_comet.cpp:48` |
| `COMET_LIFE_DECAY` | Head life fraction lost per frame | 0.0..1.0 / **0.018** | Controls how long each bright head is visible. Half-life ≈ 38 frames (318 ms at 120 fps). Lower → head persists longer, head is visible across multiple beats; higher → head flashes and vanishes. | `light_mode_comet.cpp:49` |
| `COMET_GLOW` | Soft halo radius beyond `comet_size` (pixels) | 0..N / **2 px** | Adds a diffuse aura. Increase for a blurrier, more glowing head; reduce to 0 for a hard-edged comet. | `light_mode_comet.cpp:50` |
| `COMET_WAKE_STRETCH` | Trailing-wake span multiplier vs leading-edge span | 1.0..N / **2.0×** | Controls comet shape. 2.0 = wake is twice as wide as the leading edge, producing the classic comet silhouette. Set to 1.0 for a symmetric dot; increase for a very long tail. | `light_mode_comet.cpp:51` |
| `COMET_HEAD_GAIN` | Additive weight of the head draw (white-out guard) | 0.0..1.0 / **0.85** | Peak head brightness. Below 1.0 prevents full white-out even at maximum life. Decrease for a dimmer head; increase toward 1.0 for full saturation. | `light_mode_comet.cpp:52` |
| `COMET_MIN_STRENGTH` | Absolute minimum `bass_onset_strength` to spawn | 0.0..1.0 / **0.06** | The kick sensitivity floor. Lower → responds to very soft kicks; higher → only loud hits spawn a comet. At 0.06, virtually every audible bass transient passes. | `light_mode_comet.cpp:58` |
| `COMET_HUE_BASS` | Palette position for the single kick class | 0.0..1.0 / **0.04** | In palette mode, selects which end of the gradient kick comets use. 0.04 maps to the warm/orange end of most palettes. Change to shift the kick's characteristic colour. | `light_mode_comet.cpp:59` |
| `COMET_SPEED_MIN` | Base velocity at `MOOD=0`, in px/frame @120fps (×NR/128 for strip-length normalisation) | 0.0..N / **0.60 px/fr** | Minimum comet speed — the slowest/dwelliest setting. At NR=128: 72 px/s. Increase for a faster baseline; decrease toward 0 for an almost-stationary glow. | `light_mode_comet.cpp:63` |
| `COMET_SPEED_MOOD` | Velocity added per unit of MOOD | 0.0..N / **2.80 px/fr** | The MOOD knob's speed range. Full-MOOD speed = `COMET_SPEED_MIN + 2.80` = 3.40 px/fr (408 px/s at NR=128). Increase for a wider MOOD range; decrease to compress it. | `light_mode_comet.cpp:64` |
| `COMET_SIZE_BASS` | Base head radius (px), scaled by `bass_onset_strength` | 0.0..N / **3.5 px** | Base kick-comet size. Actual radius = `3.5 · (0.80 + 0.40 · strength)` → **2.88 px** (quiet kick) to **4.20 px** (loud kick). Increase for bigger, more dramatic heads. | `light_mode_comet.cpp:65` |
| `COMET_LIFE_BASS` | Initial `comet_life` on spawn | 0.0..1.0 / **1.0** | Maximum dwell. Always 1.0 in current code; reducing it would spawn dimmer/shorter-lived comets. | `light_mode_comet.cpp:66` |
| `MOOD` knob (user) | Scales `comet_vel` via `COMET_SPEED_MIN + COMET_SPEED_MOOD · MOOD` | 0.0..1.0 | The universal pace dial. MOOD=0 → slow, drifting comets (dwelly, contemplative). MOOD=1 → fast zipping comets (energetic, punchy). Strip-length normalised: same visual speed regardless of NR. | `light_mode_comet.cpp:114` |
| `COMET_MAX` | Pool size — maximum simultaneous comets per channel | 1..N / **6** | How many kicks can be in-flight at once. At tempos with kick intervals < half-life (318 ms ≈ BPM > 189), pool slots begin to be recycled. | `channel_effect_state.h:24` |

### Pass 5 — Maths → perception → musical meaning

#### 5.1 — The onset/beat event stream (snapshot uniqueness — withdrawn as census)

**[SNAPSHOT CLAIM — WITHDRAWN as census]** “Every other live mode in K1 reads from `SBAudioSnapshot`. Comet is the **sole live mode that calls `sb_onset_beat_read()`**.” Pin: `onset_beat` is also on DENSE_FORGE 21, PULSE_PRISM 23, DENSE_FORGE_CHORD 24, PERCUSSION_BURST 26.

The snapshot still describes mode 13's edge detector: the event carries a monotonically incrementing `event_id` (`sb_audio_snapshot.h:29`) — a sequence number, not a timestamp — and Comet compares it to `fx.comet_last_event_id` each frame (`light_mode_comet.cpp:98`).

[MECHANISM] This comparison is a **rising-edge detector**: `fresh = (ev.event_id != comet_last_event_id)`. Because the event ring holds one event at a time, and Comet runs at ~120 fps while onsets arrive at most a few per second, the same event will be read many times across frames. The `event_id` guard ensures the spawn logic runs exactly once per onset, regardless of frame rate. Without it, a single kick would spawn up to 120 comets per second, saturating the pool instantly.

[PERCEPTION] To the viewer, this means each kick produces exactly one new comet. There is no "stutter" or double-flash even if the effect is rendering fast. The response is crisp and one-to-one with the music's attack events. **HOST-ONLY interpretation. Not C0-v2. Not LGP.**

#### 5.2 — Why `bass_onset`, not broadband `onset`

`SBOnsetBeatEvent` carries two onset flags: `onset` (broadband, fires on any transient including pads, sweeps, and vocals) and `bass_onset` (low-band attack, fires only when the detector sees a real bass/low-frequency transient with sufficient strength and attack gradient). Comet reads `bass_onset` exclusively (`light_mode_comet.cpp:100`).

[MECHANISM] `onset` fires on any rapid spectral flux; `bass_onset` is already gated by the detector on real low-band transients. Comet's `COMET_MIN_STRENGTH` gate adds a second, independent floor (`bass_onset_strength ≥ 0.06`).

[PERCEPTION] The perceptual contract is: **every comet the viewer sees is a kick drum hit** (or a heavy bass transient). On electronic music with a clean four-on-the-floor pattern, the comets fire with metronomic regularity. On a track with pads and string sweeps but no kick, the strip is quiet — intentionally and honestly so. Trying to fire on broadband onset produces a mode that "never stops" on dense material and "reads as not tracking" because the viewer cannot form a stable mental rule about what each comet means. `bass_onset` trades breadth for **decodability**.

That contract is kick-timing, not arrangement-state. Do not retarget spawn to `composition_change` because Q5 failed.

#### 5.3 — Salience gate: v4 vs v5 architecture

`channel_effect_state.h:48` retains the field `comet_strength_max` with the comment *"v4: salience running-max (decays toward floor) for the relative-trigger gate"*. In v4, a relative gate compared each kick's strength against the running maximum — only kicks above, say, 60% of the recent maximum would spawn a comet. This was intended to suppress weak transitional kicks in favour of the dominant kick in the track.

[MECHANISM] In v5/v6 (the snapshot code), `comet_strength_max` is **not read or updated in `light_mode_comet.cpp`**. The gate is purely absolute: `strength >= COMET_MIN_STRENGTH` (`light_mode_comet.cpp:104`). The field is retained in the struct for potential re-use.

[PERCEPTION] The v4 relative gate produced a perceptual problem: if a track's kick varied in dynamics (e.g. ghost notes vs accent hits), the mode would sometimes silently ignore audible kicks that the listener clearly heard, making it feel unresponsive. The v5 absolute floor catches every clear transient — even quiet kicks get a comet, just a smaller one — preserving the "comet == kick" contract at the cost of slightly noisier behaviour on very dynamic bass lines. **UNCERTAIN** — the practical threshold of when the relative gate would have been preferable has not been validated on-device. **Do not open USB to resolve it.**

#### 5.4 — `bass_onset_strength` → comet size (the only modulation)

**The maths:** `comet_size[slot] = COMET_SIZE_BASS · (0.80 + 0.40 · strength)` (`light_mode_comet.cpp:116`).

This is a linear scale from `3.5 · 0.80 = 2.88 px` (strength at floor, 0.06) to `3.5 · 1.20 = 4.20 px` (strength = 1.0). The modulation range is narrow by design: a 1.46× range from quietest to loudest kick, not a 10× range.

[MECHANISM] The narrowness is deliberate. `COMET_SIZE_BASS` with its fixed bass-class identity means all comets look like variations of the same object, not qualitatively different objects. A soft kick gets a slightly smaller head; a loud kick gets a slightly bigger one.

[PERCEPTION] The viewer reads "louder kicks = bigger comets" without the comets ever becoming tiny specks or giant blobs. The constraint preserves the single-class identity ("all comets are kicks") while encoding kick dynamics as a subtle visual intensity difference. This is the **Information ↔ Clarity** archetype resolved in favour of clarity: one modulated dimension, not two or three.

#### 5.5 — MOOD knob → velocity (speed as musical pacing)

**The maths:** `comet_vel[slot] = (COMET_SPEED_MIN + COMET_SPEED_MOOD · MOOD) · (NR / 128)` = `(0.60 + 2.80 · MOOD) · (NR/128)` px/frame at 120 fps (`light_mode_comet.cpp:114`).

- MOOD=0: 0.60 px/frame → 72 px/s at NR=128.
- MOOD=1: 3.40 px/frame → 408 px/s at NR=128.
- The `(NR/128)` factor normalises velocity to strip length: a comet traverses the same fraction of the strip per second regardless of whether the strip is 64 or 300 pixels long.

[MECHANISM] MOOD is the standard K1 "motion character" knob, shared with BLOOM, WAVEFORM, and Aurora. Comet was fixed at 0.45 px/frame in v5 (ignoring MOOD entirely) until a v6 fix aligned it with the family convention.

[PERCEPTION] MOOD=0 → comets drift slowly outward, overlapping trails from successive kicks, building a dense layered glow. MOOD=1 → comets zip to the strip edge and vanish before the next kick, leaving sparse punctuation. The user is dialling the "density of the light grammar": slow MOOD makes kick-timing legible as overlapping arcs; fast MOOD makes each kick a brief, clean flash. Both are musically meaningful; neither is wrong.

#### 5.6 — Trail as residual fade (no trail buffer)

**The maths:** `fade_f = 1.0 − COMET_TRAIL_DECAY · frame = 1.0 − 0.05 · frame` (`light_mode_comet.cpp:81`), applied multiplicatively to every pixel each frame.

[MECHANISM] The trail is not drawn explicitly; it is the *residual* of past comet-head draws left in `leds_16[]` and dimmed each frame. There is no dedicated trail data structure: the pixel buffer is the trail's memory.

[PERCEPTION] The trail decay rate sets the subjective "hangover" of each kick. A slow decay (low `COMET_TRAIL_DECAY`) means successive kicks' trails blend and layer, producing a warm glow that accumulates across beats — the strip records recent kick history as a colour wash. A fast decay means each kick is a clean, isolated event. Unlike WAVEFORM (where the trail breathes reactively with amplitude), Comet's trail decay is fixed — **UNCERTAIN** whether a `bass_onset_strength`-linked trail decay (louder kicks → longer trails) would be perceptually better. That is not a C0-v2 task and not a licence to author a new family in this lab.

#### 5.7 — Asymmetric head shape

**The maths** (inner draw loop, `light_mode_comet.cpp:146–161`): for each pixel `d` away from the head centre:

- `span = trailing ? radius · COMET_WAKE_STRETCH : radius · 0.7`
- Weight: `w = life · f · COMET_HEAD_GAIN`.

[MECHANISM] The trailing side gets a span of `radius · 2.0 = 7.0 px` (at `COMET_SIZE_BASS = 3.5` px, strength=1.0); the leading edge gets `radius · 0.7 = 2.94 px`. The centre pixel is always the brightest point (`f=1.0`), regardless of shape.

[PERCEPTION] The asymmetric shape is what makes these objects read as "comets" rather than "glowing dots": the sharp leading edge suggests speed and direction; the long trailing wake reads as momentum. A symmetrical Gaussian would be a pulsing blob. The direction of the wake implicitly tells the viewer "this comet is moving outward" — motion direction is encoded in the shape, not just the position over time.

Pin metric trap: “spearman vs sparse impulse understates trail memory”; “mean_luminance is not the primary carrier (and may invert).” Do not score Comet by mean brightness.

#### 5.8 — Six-slot pool lifecycle

Six slots per channel (`COMET_MAX = 6`, `channel_effect_state.h:24`). Each slot has:

- `comet_pos`: head position in pixels, updated each frame by `+= comet_vel · frame`.
- `comet_vel`: fixed at spawn, never modified after.
- `comet_hue`: fixed palette position (always `COMET_HUE_BASS = 0.04` in v5/v6 — single kick class).
- `comet_size`: fixed at spawn by `COMET_SIZE_BASS · (0.80 + 0.40 · strength)`.
- `comet_life`: starts at 1.0, decays multiplicatively by `(1 − 0.018 · frame)` each frame. Half-life ≈ 38 frames (318 ms at 120 fps).

**Eviction policy:** when a new onset arrives and needs a slot, the loop scans all 6 entries and picks `argmin(comet_life)` (`light_mode_comet.cpp:106–109`). This is a least-alive LRU: the oldest/faintest comet is recycled first. There is no explicit "free list" — a slot is considered dead when `comet_life ≤ 0.01` (skipped in the draw loop, `line 130`).

**Out-of-bounds kill:** if `comet_pos` exits `[0, NATIVE_RESOLUTION)`, `comet_life` is set to 0.0 immediately (`light_mode_comet.cpp:132–134`). At MOOD=1 on a 128-px strip, a comet reaches the far end in approximately `128 / 3.40 ≈ 38 frames` (318 ms) — coincidentally the same as the life half-life, so life and travel both "expire" around the same time at high MOOD, giving a clean ending.

**Spawn micro-jitter:** `comet_pos[slot] = float(centre_px + (ev.event_id % 4u))` (`light_mode_comet.cpp:113`). The spawn position is not a pure `NATIVE_RESOLUTION/2`; it dithers ±0–3 pixels based on the event's ID. [MECHANISM] This ensures consecutive kicks on the same strip position do not perfectly superimpose at the pixel level. [PERCEPTION] **UNCERTAIN** — the 0–3 px jitter is sub-perceptual at arm's length; its practical impact on visual distinctness has not been verified on-device.

#### 5.9 — Event-id deduplication

`ev.event_id` is a `uint32_t` monotonic counter in `SBOnsetBeatEvent` (`sb_audio_snapshot.h:29`). Comet stores the last-seen value in `fx.comet_last_event_id` (`channel_effect_state.h:47`) and sets `fresh = (ev.event_id != comet_last_event_id)` (`light_mode_comet.cpp:98`). The stored value is updated unconditionally each frame (`line 99`), so even frames where `bass_onset` is false advance the cursor.

[MECHANISM] At 120 fps with onsets arriving at most a few per second, the same `SBOnsetBeatEvent` is read ~40–120 times before the next one arrives. Without the dedup guard, the onset gate (`ev.bass_onset == true`) would pass on all ~40 frames, spawning ~40 comets per kick. The `event_id` check reduces 40 spurious passes to exactly 1.

#### 5.10 — Beat-lock: deferred stub (snapshot — pin has moved)

The header comment (`light_mode_comet.cpp:40`) notes: *"Deferred: continuous baseline; beat-lock (lite-stub tracker)"*. `SBOnsetBeatEvent` carries `beat` (bool), `beat_phase` (0..1), and `beat_confidence` (0..1) fields (`sb_audio_snapshot.h:35–38`). These are **not read anywhere in `light_mode_comet.cpp`** (snapshot). Beat-lock — spawning or brightening comets in phase with detected BPM, not just on detected onsets — is named as a planned extension but not implemented in v5/v6 mode 13.

**[SNAPSHOT CLAIM — WITHDRAWN as gap census]** “No live effect consumes `beat_phase`.” Pin: TEMPO_COMET 20 and TEMPO_COMET_ANTICIPATE 27 list `tempo.phase` (and bpm/confidence/beat_strength), `guidebook_fit` `CURRENT_CHANGED`. That is firmware inventory, not a brief to author beat-lock in this lab. Bind named levers (`beat_phase × LIGHT_MODE_TEMPO_COMET × <pin lever>`), never `supports_tempo: true`.

### Systems view — stocks, flows, feedback, emergence

**Stocks:**
- `leds_16[]` — the pixel buffer, holding accumulated light from all past comet draws, dimming continuously.
- `comet_life[6]` — 6 parallel energy stores, each draining at a fixed exponential rate.
- `comet_pos[6]` — 6 spatial integrators, each advancing at fixed velocity.

**Inflows:**
- **Spawn** writes `comet_life = 1.0` into the chosen slot — a step impulse that refills one life store fully.
- **Draw** adds comet-shaped light into `leds_16[]` proportional to `life · shape` — the inflow to the pixel buffer stock.

**Outflows:**
- **Fade** (`1 − 0.05·frame`) multiplicatively drains `leds_16[]` each frame — the balancing outflow from the pixel buffer stock.
- **Life-decay** (`1 − 0.018·frame`) drains `comet_life[i]` each frame — the balancing outflow from each head's energy store.
- **Out-of-bounds kill** instantly zeros `comet_life[i]` when position exits the strip.

**Feedback loops:**
- The pixel buffer carries no feedback into the spawn decision — Comet does not read `leds_16[]` to modulate its behaviour. There is no "brightness pressure" that throttles spawning when the strip is full.
- `comet_life` feeds back into the draw weight (`w = life · f · COMET_HEAD_GAIN`), creating a reinforcing decay: the dimmer the head, the less it contributes to the pixel buffer, so the trail from old comets fades proportionally.

**Emergence:**
- **The trail is emergent** — no line of code draws a comet trail. It arises from the superposition of the Draw inflow (writing a head-shaped blob each frame) and the Fade outflow (dimming it). Because the head moves, its past positions are represented by successively dimmer copies: the trail is a temporal record of position history, stored as a brightness gradient.
- **Overlap glows** — when multiple comets cross the same pixel region (e.g. two rapid kicks at similar MOOD), their additive draw weight exceeds what any single comet produces, creating a bright burst. This is not coded explicitly; it falls out of the additive accumulation + clamp architecture. [PERCEPTION] At moderate tempo and MOOD≈0.5, overlapping comets produce brighter regions that correspond to rhythmic density, making the kick groove visible as a texture rather than just individual events — **UNCERTAIN** pending on-device capture. **Not a USB task from this file.**

### Trade-offs chosen (archetype dials)

| Tension | Comet's choice (snapshot) | Rationale |
|---|---|---|
| **Responsiveness ↔ Grace** | Hard toward Responsiveness | Onset trigger is not smoothed — each kick fires immediately. No EMA on the trigger. Grace is delivered by the trail (smooth fade) and the life-decay curve, not by smoothing the event. |
| **Information ↔ Clarity** | Hard toward Clarity | One musical dimension encoded (kick timing). Kick dynamics encoded as size, but within a narrow range (1.46×). No pitch, no harmony, no spectral texture. The single decodable rule ("comet == kick") is the whole point. |
| **Reactivity ↔ Stability** | Reactivity on kick-dense material; intentional silence otherwise | No idle fill, no ambient baseline. Kick-less material → dark strip. This is the honest trade: Comet is a kick visualiser, not a keep-the-strip-lit engine. `COMET_MIN_STRENGTH = 0.06` ensures even soft kicks register. |
| **Motion ↔ Legibility** | User-controlled via MOOD | MOOD=0 → slow, overlapping, gestalt glow; MOOD=1 → fast, discrete, legible individual events. Neither extreme is forced; the user places this dial. |
| **Per-note detail ↔ Gestalt** | Gestalt entirely | No per-pitch encoding at all. Colour is the current ambient note-sum (chromatic mode) or the fixed palette class position (palette mode). Comet does not attempt to show which note the kick is on. |

### Pass 6 — Reusable principles (method language, not a build list)

**1. Choose one musical event and do it right.**
A *discrete object* effect demands a *decodable trigger*. The viewer's mental model of "what spawns an object" must be consistent and simple. `bass_onset` works because it fires on one class of musical event; broadband `onset` fails because it fires on too many classes. Principle: **when an effect uses discrete objects, the spawn trigger must be unambiguous to the viewer**. Do not author a new onset effect in this lab; firmware owns semantics.

**2. Event-id deduplication is mandatory for any onset-consuming effect.**
Running at ~120 fps against an event ring that updates at onset rates (~0.5–5 Hz), any onset-driven effect will read the same event ~24–240 times without a dedup guard. The `event_id != last_event_id` pattern (`light_mode_comet.cpp:98`) is a zero-cost edge detector.

**3. Pool-with-LRU-eviction is the natural data structure for particle-like effects.**
A fixed-size pool (no heap, no dynamic allocation), evicted by `argmin(life)`, is appropriate for any effect with a bounded number of simultaneous objects. It degrades gracefully: at high-tempo, the oldest/faintest comets are silently overwritten, not dropped.

**4. Additive draw + per-frame fade = emergent trail, no trail state required.**
The trail is an architectural consequence, not a designed subsystem. Any effect that accumulates additively into the pixel buffer and then fades the buffer each frame will produce persistent trails for free. The trail length is entirely controlled by `TRAIL_DECAY` — a single lever, not a trail-length counter.

**5. MOOD as the universal pace lever.**
Expressing velocity as `MIN + RANGE · MOOD` (with `NR/128` normalisation for strip-length independence) is the K1 convention for motion-speed control. An effect that ignores MOOD (as Comet v5 did) is inconsistent with the user's learnt model.

**6. Fixed palette-class position = viewer-decodable comet taxonomy.**
`comet_hue[i]` stores not a random hue, but a fixed class position — `COMET_HUE_BASS = 0.04` for kicks. If future versions add snare or hi-hat classes, assigning each a fixed distinct palette position lets the viewer read "which class is this object?" from colour alone. **Do not invent those classes here.**

**7. Beat-phase — snapshot gap, pin has consumers.**
**[WITHDRAWN as “unwired”]** Mode 13 still does not read `beat_phase` in the snapshot source. The pin already ships TEMPO_COMET 20 and TEMPO_COMET_ANTICIPATE 27 as `CURRENT_CHANGED` members of this guidebook class. Do not treat §7 of `00-the-method.md` / LEVERS-MATRIX Gap #1 as current. Do not design “Comet v7” in EdgeAI.

---

## 6 · Programme next (not this file)

C1 LGP look on the **already-proven C0-v2 carrier** (Waveform Tempo head position), one full song Captain chooses, no 8 s loop. Keep `composition_change` **parked**. Keep cadence **CLOSED**. Keep this class **historical**.

---

**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-06-02 | agent:Explore-sonnet | Created — Comet class decomposition (6 Passes + §9 template); grounded in `light_mode_comet.cpp` v5/v6, `channel_effect_state.h`, `sb_audio_snapshot.h`; documents salience-gate evolution (v4 relative → v5 absolute), bass_onset exclusivity, pool lifecycle, event-id dedup, MOOD velocity formula, beat-lock stub. |
| 2026-08-31 | agent:grok-w4-l06 | **HISTORICAL.** Banner: Comet is not the C0-v2 binding (`source_share × WaveformTempo × head_position`). Cite P3-C Q5 FAIL, pin 13/20/26/27, withdrawn “sole onset consumer” / “beat-phase unwired.” Cadence CLOSED. No USB. |
