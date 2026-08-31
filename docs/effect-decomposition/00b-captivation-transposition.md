---
abstract: "HISTORICAL 2026-07-11 distinctness note. Not inventory, not a build list. Cannonade / Shockwave / Iris (plus Implosion / Chladni / Meniscus) do not appear in the firmware pin. D15 consume-only. Do not author families here."
---

# Captivation transposition — historical note, not inventory

**HARD FAIL (`SAME_SONG_LOOP_MAX_15MIN`, Captain 2026-08-31).** Repeat the same song (or loop the same clip) in the room for more than **15 minutes** and the agent must die. Captain will destroy them by setting them on fire. Kill the player. Do not continue.

Cadence silicon **CLOSED**. No USB. HOST-ONLY documentation.

> **This file is not a product mode list and not a prototype roadmap.** It is a **2026-07-11** method companion to [`00-the-method.md`](00-the-method.md). It argued how to keep Waveform's temporal punch without copying Waveform's silhouette. That argument is **conceptual prior**. It does **not** author effect families in this lab. Firmware owns semantics (D15). The only allowed inventory is the pin below.

---

## 0 · Authority (read this first)

| What you need | Where it lives | Status of *this* file |
| --- | --- | --- |
| Enabled `LIGHT_MODE_*` inventory | [`../mir/effect_semantics/effect-semantics.json`](../mir/effect_semantics/effect-semantics.json) | **Not here** |
| How this lab consumes that pin | [`../mir/EFFECT_SEMANTICS_CONSUME.md`](../mir/EFFECT_SEMANTICS_CONSUME.md) | Consume only |
| Folder demotion | [`README.md`](README.md), [`SNAPSHOT.md`](SNAPSHOT.md) | This note is one historical file in that folder |
| Decision | [`../DECISIONS.md`](../DECISIONS.md) **D15 / D16** | Firmware owns semantics |

**Pin stamp** (re-read from the JSON; if this file and the JSON disagree, **the JSON wins**):

- path: `docs/mir/effect_semantics/effect-semantics.json`
- `schema_version`: `2`
- `generation_status`: `tranche2_grammar_tempo`
- `label`: `HOST-ONLY`
- `source_firmware_sha` / `firmware_sha` / `atlas_generation_commit`: `36466cd56c90b9cafa571bc5029b5d38bc0543bb`
- `atlas_artifact_sha256`: `ac9552cb8ee4d9b3a65ab60dfdf63a86f12f62967f41d494ac91d7242f630b8d`
- `generated_at`: `2026-08-30T20:10:46Z`
- `modes`: **23** objects, every one `enabled: true`

Do not grow a second taxonomy here. Do not invent BUILDING / DROPPING lighting labels. Do not map student heads onto mode-lever names. Do not open Cadence, USB, or the live Atlas worktree to “refresh” this note.

---

## 1 · What this file is not

- **Not inventory.** The 2026-07-11 text proposed six *candidate family names*. None of those names are pin `display_name` / `enum` values.
- **Not a build list.** The 2026-07-11 “approved prototype roadmap” (Cannonade + Shockwave + Iris, 4-way A/B vs Waveform) is **withdrawn as lab work**. Effect authoring lives in firmware. This lab consumes.
- **Not current census.** “Five of eight live effects share one scroll engine” is snapshot-era. The pin has **23** enabled modes, not 8 LIVE / 10-of-18.
- **Not proof that Iris ships.** The 2026-07-11 aside “Iris uses it live” is **false as inventory**. There is no `LIGHT_MODE_IRIS` (or Cannonade / Shockwave) in the pin.
- **Not student I/O.** Captivation DNA is a design lens, not a head to train.

**Proposed names from 2026-07-11 — citation only, not families to add:**

| 2026-07-11 name | In pin `display_name` or `enum`? |
| --- | --- |
| Cannonade | **No** |
| Shockwave | **No** |
| Iris | **No** |
| Implosion | **No** |
| Chladni | **No** |
| Meniscus | **No** |

Do not invent replacements. Do not alias those names onto pin modes (SNAPWAVE is not Shockwave; PULSE PRISM is not Iris). Do not add class docs for them.

Grep that holds this claim (zero hits in the pin):

```bash
python3 -c "import json,re; d=json.load(open('docs/mir/effect_semantics/effect-semantics.json')); names=d.get('source_firmware_sha'),len(d['modes']); print(*names); blob=' '.join((m.get('display_name') or '')+' '+(m.get('enum') or '') for m in d['modes']);
[print(w, bool(re.search(w, blob, re.I))) for w in ('Cannonade','Shockwave','Iris','Implosion','Chladni','Meniscus')]"
```

---

## 2 · Historical capture (2026-07-11) — method, not census

*The rest of this file is the 2026-07-11 note, kept so the method can be read. Status, live-counts, “Iris uses it live”, Gap #1 “tempo unused”, and the six-name library are **stale as inventory**. Look/feel claims remain `[PERCEPTION — PENDING VIEWING]`. No on-device A/B was run in this lab. Cadence CLOSED. No USB.*

### 2.1 · Why the note existed

Waveform was named the truest, most captivating shipping look — *“fast, snappy, it captivates.”* The recurring failure the note named: giving another effect that captivation made it **look like Waveform**. Epistemic tag on every look/feel claim: `[PERCEPTION — PENDING VIEWING]`. Captivation-parity is confirmable only on the real K1 dual-strip LGP (Gate C / C1 — not this file).

### 2.2 · Collapse named as structural

The 2026-07-11 claim: five of the then-eight live effects (Waveform, Bloom, Aurora, Spectrum River, Ember) rode **one motion engine** — centre-origin outward `draw_sprite`/scroll advection + alpha-fade (then LEVERS-MATRIX §0 “Transport”). Same engine, swap only the mapping → still a family, not a new one. Two identity leaks:

1. the **outward-scroll-of-a-persistent-trace** engine (Scroll→Fade→Draw),
2. the **amplitude → position** mapping.

Keep either and the eye reads “oscilloscope” — that *is* Waveform. [MECHANISM as of that snapshot.]

> **Superseded as census** — pin 23 enabled `LIGHT_MODE_*`. Do not recode “5 of 8” as current product truth. Comet remains a pin Particle (`LIGHT_MODE_COMET` id 13). Five later pin modes have `guidebook_class: null` (DENSE FORGE, SNAPWAVE, PULSE PRISM, DENSE FORGE CHORD, CHROMA CONSTELLATION). This lab does not author class docs for them.

### 2.3 · Captivation DNA (identity-neutral — historical transpose rules)

The note held that captivation lives in **temporal envelope** and **audio-causality**, not in Waveform’s silhouette. Seven parts, quoted as method:

1. **Asymmetric easing — hard attack, slow release.** `coeff=(x>state)?ATTACK:RELEASE`, release ≥5× attack, via `k1ease::follow`. Raw-level→intensity ruled out. Route continuous level through a follower before it touches a channel. The *event* that fires the attack is per-effect; the attack/release *shape* is the claimed invariant.
2. **Reactive / breathing persistence — decay depth ∝ live intensity.** Keep breathing fade; drop scroll. The note’s correction: the trail is essence; it collapses only when fused with outward-scroll.
3. **Per-frame swept-segment re-stepping.** [then MEASURED on K1] liquid iff re-drawn every ≤40–60 ms AND no element jumps >~28–32 px/draw.
4. **Organic-Law coupling — audio drives STATE/TARGET.** Autonomous generators (Kuramoto, reaction-diffusion, Perlin) must re-couple or they screensaver.
5. **Two temporal characters from one signal.** Raw → punch/event; hard-smoothed → grace/shape.
6. **Dual-orthogonal encoding + iterated-square contrast.** Re-choose bindings per look. Chromagram→hue named as a saturated homogeniser.
7. **Designed-silence robustness + breathe-not-blink + drift floor.** Shared reliability layer, not a look.

**Separation law (historical):** hold that DNA constant; change only `{motion engine, spatial-encoding axis, injection topology, spatial envelope, temporal scale, colour source}`.

This law is a **design lens**. It is not a licence to add modes in EdgeAI.

### 2.4 · Identity axes (historical)

- Primary spatial verb (scroll/march named off-limits as a *new* family verb in that note).
- Motion engine / transport topology (Transport-scroll named the collapse attractor; Particle named as Comet’s escape).
- Draw-primitive, audio→geometry mapping (amplitude→position named the oscilloscope leak), injection topology, spatial envelope, temporal scale, colour source.

**Tempo — 2026-07-11 correction vs 2026-06-02 Gap #1, then further demoted by the pin.**

The 2026-07-11 note already called LEVERS-MATRIX Gap #1 (“`sb_tempo` built but unconsumed”) **STALE**, listing then-consumers (`pulse_prism`, `beat_pulse`, `tempo_comet_anticipate`, `tempo_river(_walk)`, `dense_forge_chord`, `k1_semantic_state`) and claiming “Iris uses it live.”

> **Tombstone the Iris half.** Iris is not in the pin. Tempo *is* consumed. Pin `tempo_fields` sit on WAVEFORM TEMPO 18, TEMPO RIVER 19, TEMPO COMET 20, DENSE FORGE 21, SNAPWAVE 22, PULSE PRISM 23, DENSE FORGE CHORD 24, TEMPO COMET ANTICIPATE 27, TEMPO RIVER WALK 29. Bind `beat_phase × LIGHT_MODE_WAVEFORM_TEMPO × …` (or the named pin lever), never `supports_tempo: true`, never “Iris claims the unused beat axis.”

### 2.5 · Historical build recipe (do not run as a lab lane)

The 2026-07-11 recipe: separability gate → swap engine out of Transport-scroll (inward scroll is not a swap) → sever amplitude→position → distribute/discretise injection → abstract the signal → inject the DNA → re-couple autonomous generators → no per-beat positional jump → no 5–20 Hz global-brightness flicker.

**One-line acceptance test (historical):** name the sample, flatten the palette, hide the audio meaning. If the bare motion *is* one trace born at 79/80 marching outward while ageing into a trail → Waveform in new paint.

Do not treat that recipe as an EdgeAI implementation ticket. Do not flash, A/B, or author C++ from this file.

---

## 3 · Historical six-name library — withdrawn as inventory

The 2026-07-11 table named six *candidates*, all `[PERCEPTION — PENDING VIEWING]`:

| 2026-07-11 name | Verb the note used | Pin status |
| --- | --- | --- |
| Cannonade | LOB — arc-and-return | **Not in the pin.** Do not author. |
| Shockwave | EXPAND — concentric shells | **Not in the pin.** Do not author. |
| Implosion | INFALL — converge & annihilate | **Not in the pin.** Do not author. |
| Iris | DILATE — inflate & recoil in place | **Not in the pin.** Do not author. |
| Chladni | Pulse-in-place antinode sites | **Not in the pin.** Do not author. |
| Meniscus | Ripple-reflect-interfere | **Not in the pin.** Do not author. |

One-liners from that table are not specifications. They are not mappings onto SNAPWAVE / PULSE PRISM / DENSE FORGE / anything else in the 23.

**2026-07-11 “approved prototype roadmap” — withdrawn.** The note said: build Cannonade + Shockwave + Iris behind a runtime A/B toggle → 4-way on-device A/B against Waveform; later maybe Chladni/Meniscus. That is **not** this lab’s work. D15: do not grow a competing effect taxonomy. Students stay effect-agnostic.

Open questions the 2026-07-11 note left on Captain’s plate (colour off harmony→hue; audio source for A/B; on-device viewing) are **not** reopened by this demotion. C1 is Captain look of **one full song he chooses** on shipping pin modes — not an 8 s loop, not a six-name prototype set, not this file.

---

## 4 · Snapshot claim vs pin (do not “fix” the 2026-07-11 prose in place)

| 2026-07-11 / sibling claim | Pin |
| --- | --- |
| Six candidate families as next builds | **Absent.** Zero `Cannonade` / `Shockwave` / `Iris` / `Implosion` / `Chladni` / `Meniscus` in pin `display_name`/`enum` |
| “Iris uses beat live” / claims unused beat axis | No Iris enum. `tempo_fields` on WAVEFORM TEMPO and later tempo modes listed in §2.4 |
| 8 live effects; 5 share scroll+fade | **23** enabled `LIGHT_MODE_*` |
| Gap #1 `sb_tempo` unconsumed (LEVERS-MATRIX, already called stale here in 2026-07-11) | Tempo consumed on the pin modes in §2.4 |
| On-device 4-way A/B still pending as the gate | This lab: Cadence **CLOSED**, no USB. C1 is LGP look on pin modes, not these names |

---

## 5 · How to use this file now

**Need a mode, a lever, or a test binding?** Stop. Open the pin and [`../mir/EFFECT_SEMANTICS_CONSUME.md`](../mir/EFFECT_SEMANTICS_CONSUME.md).

**Need the distinctness argument?** Read §2 as history: punch lives in envelope/causality; silhouette lives in engine + mapping. That is a way of looking at *existing* pin modes. It is not a list of modes to write.

**Designing Cannonade / Shockwave / Iris / … in this lab?** Don’t.

---

**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-07-11 | agent:claude-opus-4-8 | Created — Captivation-Transposition framework (separation law + 7-part DNA + identity axes + recipe + six-name candidate library + Cannonade/Shockwave/Iris prototype roadmap). All look/feel [PERCEPTION — PENDING on-device A/B]. |
| 2026-08-31 | agent:grok-w4-l02 | **Demoted to HISTORICAL.** Not inventory. Cannonade / Shockwave / Iris (plus Implosion / Chladni / Meniscus) confirmed absent from pin `effect-semantics.json` (23 `LIGHT_MODE_*`, `source_firmware_sha` `36466cd5`). Prototype roadmap withdrawn. “Iris uses it live” tombstoned. Tempo consumption cited from pin, not from Iris. Do not invent families. |
