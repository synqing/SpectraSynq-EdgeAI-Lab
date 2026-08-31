---
abstract: "Historical 2026-07-11 Waveform-class write-up. NOT inventory. Pin LIGHT_MODE_WAVEFORM_TEMPO id 18 is enabled, guidebook_fit CURRENT_CHANGED, evidence HOST_PIXEL_VALIDATED at SHA 36466cd5. WIP/roadmap-gap labels withdrawn. Missing rationale file is not in this lab."
---

# Waveform class — historical write-up, not inventory

**HARD FAIL (`SAME_SONG_LOOP_MAX_15MIN`, Captain 2026-08-31).** Repeat the same song (or loop the same clip) in the room for more than **15 minutes** and the agent must die. Captain will destroy them by setting them on fire. Kill the player. Do not continue.

Cadence silicon **CLOSED**. No USB. No `k1-flash`. HOST-ONLY documentation.

> **This file is not the product mode list.** It is a **2026-07-11** class write-up (Motion ∘ Mapping exemplar). It used to treat Waveform-Tempo (18) as **WIP** and a roadmap gap. That inventory claim is **withdrawn**. `LIGHT_MODE_WAVEFORM_TEMPO` is a firmware enum in the lab pin. Canonical mode behaviour lives in firmware; this lab consumes the pin.

---

## 0 · Authority (read this first)

| What you need | Where it lives | Status of *this* file |
| --- | --- | --- |
| Enabled `LIGHT_MODE_*` inventory | [`../mir/effect_semantics/effect-semantics.json`](../mir/effect_semantics/effect-semantics.json) | **Not here** |
| How EdgeAI consumes that pin | [`../mir/EFFECT_SEMANTICS_CONSUME.md`](../mir/EFFECT_SEMANTICS_CONSUME.md) | Consume only |
| Folder demotion | [`README.md`](README.md), [`SNAPSHOT.md`](SNAPSHOT.md) | Historical guidebook |
| Decision | [`../DECISIONS.md`](../DECISIONS.md) **D14 / D15 / D16** | Firmware owns semantics |
| Method language | [`00-the-method.md`](00-the-method.md) | Historical |

**Pin stamp** (re-read from the JSON; if this file and the JSON disagree, **the JSON wins**):

- path: `docs/mir/effect_semantics/effect-semantics.json`
- `schema_version`: `2`
- `generation_status`: `tranche2_grammar_tempo`
- `source_firmware_sha` / `firmware_sha` / `atlas_generation_commit`: `36466cd56c90b9cafa571bc5029b5d38bc0543bb`
- `atlas_artifact_sha256`: `ac9552cb8ee4d9b3a65ab60dfdf63a86f12f62967f41d494ac91d7242f630b8d`
- `modes`: **23** objects, every one `enabled: true`

Pin rows with `guidebook_class` `01-waveform` (pointer only — not a second catalogue):

| id | `enum` | `guidebook_fit` | `enabled` | `evidence` | `tempo_fields` |
| --- | --- | --- | --- | --- | --- |
| 7 | `LIGHT_MODE_WAVEFORM_FAST` | `CURRENT_CONFIRMED` | true | `STATIC_SOURCE` | none |
| 8 | `LIGHT_MODE_WAVEFORM` | `CURRENT_CONFIRMED` | true | `HOST_PIXEL_VALIDATED` | none |
| 11 | `LIGHT_MODE_WAVEFORM_HYBRID` | `CURRENT_CONFIRMED` | true | `STATIC_SOURCE` | none |
| 18 | `LIGHT_MODE_WAVEFORM_TEMPO` | `CURRENT_CHANGED` | true | `HOST_PIXEL_VALIDATED` | `tempo.bpm`, `tempo.phase`, `tempo.confidence` |
| 32 | `LIGHT_MODE_WAVEFORM_HYBRID_K1` | `CURRENT_CHANGED` | true | `STATIC_SOURCE` | none |

Dump from the pin, never from this markdown:

```bash
python3 -c "import json; d=json.load(open('docs/mir/effect_semantics/effect-semantics.json')); print(d['source_firmware_sha'], len(d['modes']));
[print(m['id'], m['enum'], m['enabled'], m['guidebook_fit'], m['evidence'], m.get('tempo_fields')) for m in d['modes'] if m.get('guidebook_class')=='01-waveform']"
```

`CURRENT_CHANGED` means this write-up is **behind** the pin. Do not “fix” `file:line` here to chase firmware. Do not grow a second taxonomy.

**Withdrawn as inventory (still true as 2026-07-11 history):**

- Waveform-Tempo (18) is WIP / the #1 roadmap gap / `sb_tempo` unconsumed.
- `Status: LIVE` on a 9-class family as the current library census.
- The missing link [`../waveform-mode-design-rationale.md`](../waveform-mode-design-rationale.md) as a lab authority. **That file is not in this lab.** Do not recreate it here.

**Not student I/O.** A student may emit `vocals_share` / `drums_share` / …. It must not emit “Waveform Tempo head position”. Binding is a separate consume layer (`descriptor × mode × lever`).

**Not `supports_tempo: true`.** Tempo is not one lever. Prefer a named pin binding, e.g. `beat_phase × LIGHT_MODE_WAVEFORM_TEMPO × transport_position`, never a boolean.

**Waveform Tempo is a continuity / reference carrier** for source-share (D14–D16), not a universal lighting actuator. Host LED-buffer `HOST_PIXEL_VALIDATED` is not silicon and not LGP look. Pin `on_silicon_pixel_validated` and `lgp_perceptual_validated` are null.

Evidence ladder (from the pin, not from this class doc):

`STATIC_SOURCE` → `HOST_PIXEL_VALIDATED` → `ON_SILICON_PIXEL_VALIDATED` → `LGP_PERCEPTUAL_VALIDATED`

---

## Historical write-up (2026-07-11)

The remainder is the original class decomposition. LIVE / WIP / “roadmap gap” lines inside it are **what that draft believed**, not what ships. Native `file:line`s were inherited from a 2026-06-02 exemplar — verify against firmware at `36466cd5` before quoting. Map is not territory.

*Historical header (stale as inventory): Family WAVEFORM · modes 8 / 7 / 11 plus siblings 18 and 32 · files `effects/light_mode_waveform*.cpp` plus helpers in `visual/`.*

> Class 01 originated the method. The deep design/perception rationale was meant to live in the prose exemplar `docs/waveform-mode-design-rationale.md`. That path is **absent from EdgeAI-Lab**. This formal decomposition added what that exemplar predated: the Pass-3 six-layer table, the Pass-4 named-lever table, and the 2026-07 additions (asymmetric-easing treatment + Hybrid-K1 finding).

---

### Pass 1 — What it is

The Waveform class is the K1's **seismograph of the music**: it stops trying to show the
present moment and instead scrolls a *window of recent history* through space. Each frame draws
one new sample whose **position encodes dynamics** and whose **colour encodes harmony**, then
scrolls the whole strip so that sample travels outward as it ages. The strip becomes a *time
axis* — a kick is not a flash, it is a bright spike you then watch travel away from centre.
Members share one motion DNA (Scroll → Fade → Draw) and differ only in *what gets drawn* and
*how fast time scrolls*:

- **Waveform (8)** — draws one dot at the smoothed-amplitude position; ~1 px/frame scroll.
- **Waveform-Fast (7)** — same dot, `dt`-scaled scroll up to ~8 px/frame; history rushes past.
- **Waveform-Hybrid (11)** — draws the **real raw-audio scope trace** (a symmetric centre seed
  sampled from `waveform_history`), harmony-coloured, with an *inverted* louder-lingers fade.
- **Waveform-Tempo (18)** — historical draft: scroll *velocity* locked to beat phase, labelled WIP
  as the method’s #1 roadmap gap. **Pin:** `LIGHT_MODE_WAVEFORM_TEMPO`, `enabled` true,
  `guidebook_fit` `CURRENT_CHANGED`, `evidence` `HOST_PIXEL_VALIDATED`, `tempo_fields` present.
  Binding used in this lab: `source_share × WaveformTempo × head_position` (alias of export
  `WAVEFORM TEMPO`, not a second catalogue).
- **Waveform Hybrid K1 (32, ported)** — a fw-v3 `0x1313` port: an amplitude-bouncing **dot** + a
  decaying scroll trail with 0.163 s colour inertia, and the class's clean **asymmetric-easing
  exemplar** (§4.1). Note the shared "Hybrid" name is misleading: `0x1313` is a *dot* effect,
  mechanically distinct from mode 11's raw-scope *seed*. Its envelope is reconstructed from
  `peak_scaled` rather than the raw `waveform_history` global mode 11 uses — a provenance note,
  not a ranking. **Pin:** `enabled` true, `guidebook_fit` `CURRENT_CHANGED`, `evidence` `STATIC_SOURCE`.

---

### Pass 2 — Semantic mechanism (the verbs)

**Scroll → Fade → Draw.** Repeat at ~120–185 fps. [MECHANISM `light_mode_waveform.cpp:78–101`]

1. **Scroll** — shift the whole strip one step outward (`shift_leds_up` / `waveform_shift_outward`): space becomes time.
2. **Fade** — multiply the existing pixels down slightly; the *depth* of the fade breathes with amplitude (see L5).
3. **Draw** — stamp the new sample. Waveform: one pixel at the amplitude position. Hybrid: a multi-pixel scope seed whose per-pixel brightness follows the genuine signal shape.

Trails are **emergent** — no line "draws a trail"; it is the compounded residue of Scroll + Fade + Draw (Systems view).

---

### Pass 3 — The six layers

| Layer | This class's choice | file:line | Label |
|---|---|---|---|
| **L1 Feature** | Dynamics via `waveform_peak_scaled` (pre-smoothed asymmetric env upstream); harmony via `chromagram_smooth[12]` centroid. Hybrid adds the raw `waveform_history[frame][idx]` (4 frames × 5 taps). K1 port: `snap.peak_scaled` only. | `light_mode_waveform.cpp:9,19–47`; `light_mode_waveform_hybrid.cpp:141–192`; `light_mode_waveform_hybrid_k1.cpp:112` | [MECHANISM] |
| **L2 State / memory** | Per-channel `leds_prev_buffer` (whole prior frame = scroll source). K1 port adds scalar envelope state in `ChannelEffectState` (`wfhyb_peak_ema1/_last`, `wfhyb_dot_{r,g,b}`, `wfhyb_hold_env`, `wfhyb_sil_scale`). | `light_mode_waveform.cpp:3`; `channel_effect_state.h` (`wfhyb_*`) | [MECHANISM] |
| **L3 Spatial mapping** | `pos = centre + amp·(NR/2)` (`waveform_full_strip_position`); centre-origin, mirrored outward. Hybrid: symmetric seed radius `3 + seed_level·7`. | `lightshow_modes.h:~426`; `light_mode_waveform_hybrid.cpp:141–192` | [MECHANISM] |
| **L4 Colour mapping** | Chromagram centroid → hue (the note-sum). Hybrid blends note-sum against a `CHROMA` fallback ∝ chromagram energy. K1 port: chroma-anchored `effect_particle_colour`, then a **0.163 s RGB EMA** (`wfhyb_dot_*`) — the "hybrid" colour inertia. | `light_mode_waveform.cpp:19–47`; `light_mode_waveform_hybrid.cpp:82–100`; `light_mode_waveform_hybrid_k1.cpp:130–160` | [MECHANISM] |
| **L5 Temporal dynamics (MOTION)** | Scroll: 1 px/frame (Waveform) / `VP_WAVEFORM_SHIFT_RATE·dt` up to 8 px (Fast, dt-scaled) / `waveform_shift_outward` (Hybrid). Fade: `1 − 0.10·|amp|` (Waveform, *louder→shorter*); Hybrid *inverts* it (`1 − REDUCTION·(1−seed_level)`, *louder→longer*). K1 port: `expf(−decay·dt)`, `decay = 0.8 + 3.5·|amp|`. | `light_mode_waveform.cpp:74–82`; `light_mode_waveform_fast.cpp:148–150`; `light_mode_waveform_hybrid.cpp:103–109`; `light_mode_waveform_hybrid_k1.cpp` | [MECHANISM] |
| **L6 Clamps / floor (SHARED)** | Calibrated silence floor (`waveform_reactive`), VU failsafe (sound-but-no-pitch → not black). K1 port: dual eased envelope — `wfhyb_hold_env` (presence, 0.02/0.50 s) × `wfhyb_sil_scale` (silence, 0.05/0.30 s) → `col_gain`; true silence *accelerates* the trail rather than blanking. | `light_mode_waveform_fast.cpp:50`; `light_mode_waveform.cpp:49–56`; `light_mode_waveform_hybrid_k1.cpp:119–126` | [MECHANISM] |

→ **MAPPING = L1+L3+L4** (dynamics→where, harmony→colour) · **MOTION = L2+L5** (scroll/fade) · **SHARED = L6** (floor/failsafe). Swap the MAPPING (amplitude→position for frequency→position) and the same motion engine becomes River — this is the seam proof of §1.3.

---

### Pass 4 — Named levers (the dials, with ranges)

Historical named-lever table. For a test binding, stop and query `compatibility.json`. Score the named lever, never mean brightness by default. Waveform Tempo extra drive → luminance is a documented trap (polarity inverted).

| Lever | What it controls | Range / default | Musical effect of turning it up | file:line |
|---|---|---|---|---|
| Amplitude EMA coeff (Waveform/Fast) | "Smooth for grace" — new-fraction per frame | 0.08 (Waveform) / 0.05 (Fast) | Lower → more lag, more liquid curves; higher → snappier but twitchier | `light_mode_waveform.cpp:9` |
| Dynamic fade base `0.10·|amp|` | Trail length vs loudness (Waveform: louder→shorter) | fixed 0.10 coeff | Higher coeff → trails collapse harder on hits (aggressive); lower → longer memory | `light_mode_waveform.cpp:76` |
| `VP_WAVEFORM_SHIFT_RATE` (Fast) | dt-scaled scroll velocity | ~up to 8 px/frame | Faster → history rushes past, trace thin and racing (suits dense music) | `light_mode_waveform_fast.cpp:148–150` |
| Hybrid seed radius `3 + seed_level·7` | Width of the scope seed | 3–10 px | Louder → wider scope trace at centre; the seed "opens up" on hits | `light_mode_waveform_hybrid.cpp:141–192` |
| Hybrid inverted-fade `REDUCTION` | Trail length vs loudness (Hybrid: louder→longer) | — | Higher → quiet passages clear faster, hits *bloom and linger* | `light_mode_waveform_hybrid.cpp:103–109` |
| `WFHYB_TAU_PEAK1/2` (K1 port) | Two-stage peak-envelope reconstruction | 0.016 / 0.023 s | Longer → smoother dot motion, more lag | `light_mode_waveform_hybrid_k1.cpp:130–131` |
| `WFHYB_*` hold/silence taus (K1 port) | Asymmetric presence + silence envelopes (§4.1) | 0.02/0.50 s, 0.05/0.30 s | Longer release → the dot & trail *breathe out* instead of snapping dark | `light_mode_waveform_hybrid_k1.cpp:119–126` |
| Colour EMA 0.163 s (K1 port) | RGB colour inertia — the "hybrid" tell | fixed ~0.163 s | Longer → colour drifts slowly and organically instead of flickering per-note | `light_mode_waveform_hybrid_k1.cpp` |
| Silence floor / VU failsafe | Idle behaviour | calibrated | Keeps it from drawing garbage in silence / collapsing to black on pitchless sound | `light_mode_waveform_fast.cpp:50`; `light_mode_waveform.cpp:49–56` |

---

### Pass 5 — Maths → perception → musical meaning

The five impact mechanisms — **time-as-space**, **dual-channel encoding** (position=dynamics,
colour=harmony), **breathing (reactive) trails**, **smooth-for-grace**, **graceful degradation**
— were decomposed in the missing exemplar. Two additions this
doc grounds:

#### 5.1 · The class is the archetype of the Responsiveness↔Grace resolution (§4.1)
[MECHANISM] Waveform separates the two temporal characters *across the seam*: the **MAPPING**
position uses the *smoothed* amplitude (0.08/0.92 EMA — grace), while the **MOTION** fade depth
uses the *raw* amplitude (`1−0.10·|amp|` — reactive snap). [PERCEPTION] So "the shape is liquid
while the trail-length snaps on transients" — two temporal feels from one signal, one per layer,
on purpose. The K1 port (32) instead uses the newer **asymmetric follower** (`wfhyb_follow`,
attack 0.02 s / release 0.50 s) on one signal to get *both* — the clean §4.1 exemplar. Both are
valid resolutions of the same dial; the class demonstrates the two idioms side by side.

#### 5.2 · Two different "Hybrids" — the scope seed (11) vs the bouncing dot (32)
[MECHANISM] Native **Waveform-Hybrid (11)** samples the firmware's raw-audio history
(`waveform_history[frame][idx]`), abs-mean-envelopes it, `sqrt`-compands for visibility, and
paints a symmetric centre **seed** whose *per-pixel brightness is the genuine signal shape*
(`light_mode_waveform_hybrid.cpp:141–192`) — a literal mini-oscilloscope at the strip's heart.
[MECHANISM] The ported **Waveform Hybrid K1 (32)** is a *different effect* — a faithful port of
fw-v3 `0x1313`: it reconstructs an amplitude *envelope* from `snap.peak_scaled` (a two-stage EMA)
and plots a bouncing **dot** with a trailing wake — *position*, not per-pixel shape. The
`peak_scaled` reconstruction is a factual input choice (the snapshot carries no raw samples; the
raw `waveform_history` global was an available alternative the port did not use).
[PERCEPTION — PENDING VIEWING] Whether the seed reads "more like the sound" or the dot reads
"cleaner" is **not decidable here.** The exemplar itself warns the raw signal at audio rate is
jittery and the *envelope-over-time* is often what the eye finds beautiful — so neither
representation is a priori superior. Rank them on-device; do not assume. This lab does not open
USB or Cadence to do that ranking.

---

### Systems view — stocks, flows, feedback, emergence

- **Stock:** `leds_prev_buffer` — the whole prior frame; the only inter-frame memory (plus the K1 port's scalar envelope stocks).
- **Inflow:** the per-frame Draw (one pixel, or the Hybrid seed) at the mapped position.
- **Transport:** the scroll displaces the stock outward (neither in- nor out-flow — spatial displacement); centre-origin + mirror gives bilateral symmetry from one draw.
- **Outflow:** the fade multiplier drains brightness each frame; its depth is *audio-modulated* (breathing trail).
- **Feedback:** this frame's drawn sample is next frame's scroll seed; the fade coefficient is the only thing preventing saturation-and-freeze.
- **Emergence:** the **coloured ribbon** — a continuous read of the last N seconds of dynamics×harmony — is authored by no single line; it is Scroll + Fade + Draw compounded. The eye reads the moving, symmetric, breathing trace as *alive* in a way no instantaneous pulse matches.

---

### Trade-offs chosen (archetype dials)

| Tension | Waveform class position | Mechanism |
|---|---|---|
| **Responsiveness ↔ Grace** | The class *is* the resolution (§4.1) | smoothed position (grace) + raw-driven fade (snap) across the seam; K1 port uses an asymmetric follower to get both on one signal |
| **Information ↔ Clarity** | Clarity-rich | position=dynamics + colour=harmony — two orthogonal dimensions in one travelling point, never cluttered |
| **Reactivity ↔ Stability** | Designed for both | calibrated floor + VU failsafe (native); dual eased silence gate (K1 port) — never garbage in silence, never dead |
| **Motion ↔ Legibility** | Explicitly tunable | scroll rate is the dial (Waveform slow / Fast racing); dt-stable so character holds across FPS drift |
| **Per-note detail ↔ Gestalt** | Toward detail (uniquely) | Hybrid draws the *actual* signal shape — the class's most literal "show me the sound" |

---

### Pass 6 — Reusable principles

1. **Render time, not just now.** A scrolling history reads as motion + narrative; an instantaneous response reads as a pulse. The class's founding insight, and the reason `Motion ∘ Mapping` was extracted from it.
2. **Encode two orthogonal musical dimensions** on one element (position=dynamics, colour=harmony) — information-rich without clutter.
3. **Make persistence reactive** — a fade depth that breathes with intensity feels alive; a fixed fade feels mechanical.
4. **Smooth for grace, then tune the lag** — and prefer the **asymmetric follower** (§4.1) when you want both immediacy *and* grace on a single signal; reserve the symmetric-EMA-across-the-seam idiom for when the two temporal feels genuinely belong to different layers.
5. **Design the silence and the failure case** — floor + failsafe are what make an effect "always look good." (The K1 port's dual eased gate is the modern form.)
6. **Reach for the highest-fidelity input the platform already exposes, before reconstructing one** — the Hybrid-K1 provenance note: the raw `waveform_history` global was available, yet the port reconstructed its envelope from `peak_scaled` (the snapshot path). Whether the raw source renders *better* is unvalidated — the discipline is simply to *know what exists* before rebuilding it, not to assume the reconstruction is inferior.

---

### Class members (historical table — pin wins)

| Mode | Draws | Input source | 2026-07-11 draft | Pin (JSON wins) |
|---|---|---|---|---|
| Waveform (8) / Fast (7) | dot at amplitude position | `peak` envelope | native, LIVE | 8 `HOST_PIXEL_VALIDATED`; 7 `STATIC_SOURCE`; both `CURRENT_CONFIRMED`, `enabled` true |
| Waveform-Hybrid (11) | raw-PCM **scope seed** | `waveform_history` global | native, LIVE | `CURRENT_CONFIRMED`, `STATIC_SOURCE`, `enabled` true |
| Waveform-Tempo (18) | scroll velocity ∝ beat phase | tempo phase | labelled WIP / roadmap gap | **`LIGHT_MODE_WAVEFORM_TEMPO`**, `enabled` true, `CURRENT_CHANGED`, `HOST_PIXEL_VALIDATED` |
| Waveform Hybrid K1 (32) | bouncing amplitude **dot** + trail | `snap.peak_scaled` | ported 2026-07-11 | `CURRENT_CHANGED`, `STATIC_SOURCE`, `enabled` true |

[MECHANISM] Modes 11 and 32 are **different effects** despite the shared "Hybrid" name: 11 paints
the *raw signal shape* as a centre seed; 32 (a faithful port of fw-v3 `0x1313`) plots a *bouncing
amplitude dot* with a decaying trail + 0.163 s colour inertia. By the method's own test — a
different `{where, colour, intensity}` = a different effect — they are **not redundant**, no more
than Waveform (dot) and Waveform-Hybrid (seed) are redundant with each other.

[MECHANISM] Provenance note: 32's envelope is reconstructed from `snap.peak_scaled` because the
audio *snapshot* carries no raw samples; the raw `waveform_history` **global** (which 11 reads) was
an available alternative the port did not use. IF a sharper envelope is ever wanted for 32, that
global is the source — an **optional, unvalidated refinement**, not a correctness fix. Firmware
owns that change. Do not author it here.

> [PERCEPTION — PENDING VIEWING] **Which of 8 / 11 / 32 to keep, and how they rank, is not
> decidable from source.** An earlier draft asserted 32 was "inferior / redundant" and recommended
> binning it; that was a **perception-stated-as-fact error with no visual benchmark, and is retracted.**
> This lab does not open the plate, USB, or Cadence to re-rank them.

Do not invent BUILDING / DROPPING lighting labels. Do not add Cannonade / Shockwave / Iris here.

---

**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-07-11 | agent:claude-opus-4-8 | Created — formal §9 Waveform-class decomposition (Pass 1–6 + six-layer & lever tables + systems + trade-offs), completing the guidebook's missing Class 01 doc alongside the prose exemplar. Adds the §4.1 asymmetric-easing treatment the class exemplifies, and a provenance note on the ported Hybrid-K1 (mode 32). Native `file:line`s inherited from the 2026-06-02 exemplar — verify against source. |
| 2026-07-11 | agent:claude-opus-4-8 | **CORRECTION** (Captain adversarial fact-check) — retracted the claim that Waveform Hybrid K1 (mode 32) is "inferior / redundant" to native Hybrid (mode 11) and the "bin it" recommendation. That was a perception-stated-as-fact error (violates §8) with no on-device benchmark: 11 (raw-scope seed) and 32 (bouncing dot) are *different* effects, and ranking needs a hardware A/B. Reframed Pass 5.2 + the members section to facts + [PERCEPTION-PENDING]; kept only the defensible provenance note (32 reconstructs from `peak_scaled`; raw `waveform_history` was an unused available input). |
| 2026-08-31 | agent:grok-w4-l03 | **Demoted.** This file is historical, not inventory. `LIGHT_MODE_WAVEFORM_TEMPO` id 18 is enabled in the firmware pin (`CURRENT_CHANGED`, `HOST_PIXEL_VALIDATED`). WIP / roadmap-gap labels withdrawn. Missing `waveform-mode-design-rationale.md` is not in this lab. |
