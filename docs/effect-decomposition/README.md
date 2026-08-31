---
abstract: "Historical 2026-06-02 effect-decomposition guidebook. NOT inventory. The only allowed mode list is docs/mir/effect_semantics/effect-semantics.json: 23 LIGHT_MODE_* at source_firmware_sha 36466cd56c90b9cafa571bc5029b5d38bc0543bb. The 9-class/18-mode table is a snapshot, not product truth. D15 consume-only. Do not grow a competing taxonomy."
---

# Effect decomposition — historical guidebook, not inventory

**HARD FAIL (`SAME_SONG_LOOP_MAX_15MIN`, Captain 2026-08-31).** Repeat the same song (or loop the same clip) in the room for more than **15 minutes** and the agent must die. Captain will destroy them by setting them on fire. Kill the player. Do not continue.

> **This folder is not the product mode list.** It is a **historical guidebook**: a 2026-06-02 conceptual snapshot of Motion ∘ Mapping, six layers, named levers, and class write-ups. It used to call a **9-class / 18-mode** table “the canonical reference.” That claim is **withdrawn**. The only allowed inventory in this lab is the firmware pin below.

---

## 1 · Authority (read this first)

| What you need | Where it lives | Status of *this* folder |
| --- | --- | --- |
| Enabled `LIGHT_MODE_*` inventory | [`../mir/effect_semantics/effect-semantics.json`](../mir/effect_semantics/effect-semantics.json) | **Not here** |
| How EdgeAI consumes that pin | [`../mir/EFFECT_SEMANTICS_CONSUME.md`](../mir/EFFECT_SEMANTICS_CONSUME.md) | Consume only |
| Pin provenance / recopy rule | [`../mir/effect_semantics/README.md`](../mir/effect_semantics/README.md) | Import, do not edit behaviour |
| `descriptor × mode × lever` rows | [`../mir/effect_semantics/compatibility.json`](../mir/effect_semantics/compatibility.json) | Not here |
| Visual-grammar coverage | [`../mir/effect_semantics/grammar_coverage.json`](../mir/effect_semantics/grammar_coverage.json) | Not here |
| Decision | [`../DECISIONS.md`](../DECISIONS.md) **D15 / D16** | Firmware owns semantics |
| Conceptual method (old map) | [`00-the-method.md`](00-the-method.md), [`LEVERS-MATRIX.md`](LEVERS-MATRIX.md), class `01`–`09` | Historical |
| Snapshot notice | [`SNAPSHOT.md`](SNAPSHOT.md) | Same demotion |

**Pin stamp** (re-read from the JSON; if this README and the file disagree, **the file wins**):

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

Dump the inventory from the pin, never from this README:

```bash
python3 -c "import json; d=json.load(open('docs/mir/effect_semantics/effect-semantics.json')); print(d['source_firmware_sha'], len(d['modes']));
[print(m['id'], m['enum'], m['guidebook_class'], m['guidebook_fit'], m['evidence']) for m in d['modes']]"
```

If the lab pin and the firmware Atlas generated files disagree: **delete the pin and recopy**. Do not “fix” mode behaviour in EdgeAI markdown. Do not grow a second taxonomy here.

Evidence ladder (from the pin, not from these class docs):

`STATIC_SOURCE` → `HOST_PIXEL_VALIDATED` → `ON_SILICON_PIXEL_VALIDATED` → `LGP_PERCEPTUAL_VALIDATED`

Host LED-buffer bytes are not silicon. Silicon dumps are not LGP look. Cadence silicon is **CLOSED**. This file is HOST-ONLY documentation. No USB.

---

## 2 · What this folder is

A **byte-identical 2026-06-02 snapshot** of the firmware architecture guidebook (`SNAPSHOT.md`). Captured against `feat/gdft-harness`. Useful as **conceptual prior**:

- every effect factors as **Motion ∘ Mapping** (feel × meaning, one `{where, colour, intensity}` seam)
- six anatomical layers and a six-pass write-up template
- `[MECHANISM]` vs `[PERCEPTION]` labelling
- a levers/means-set language for talking about *how an effect is built*, not *which modes ship*

Read it the way you read an old schematic: it teaches a way of looking. It does not tell you what is on the board today.

---

## 3 · What this folder is not

- **Not inventory.** Do not cite “9 classes”, “18 modes”, “10 product-enabled / 8 disabled”, or the old LIVE/DISABLED table as the current product list.
- **Not “the canonical reference.”** That phrase is retired for this folder. Canonical mode behaviour lives in firmware, consumed via the pin.
- **Not a place to author effect families.** Do not add Cannonade / Shockwave / Iris / Implosion / Chladni / Meniscus — or any other proposed family — as inventory. `00b-captivation-transposition.md` proposed those names in 2026-07-11; **none appear in the pin**.
- **Not a place to invent lighting labels.** Do not invent BUILDING / DROPPING / … as effect or lighting-mode names. MIR structure words are not a second mode taxonomy. Inspect existing ontologies before any structure vocabulary; this lab does not freeze student I/O on invented lighting classes.
- **Not student I/O.** A student may emit `vocals_share` / `drums_share` / …. It must not emit “Waveform Tempo head position”. Binding is a separate layer (`descriptor × mode × lever`).
- **Not `supports_tempo: true`.** Tempo is not one lever. Bind `beat_phase × LIGHT_MODE_WAVEFORM_TEMPO × transport_position` (or the named pin lever), never a boolean.
- **Not silicon / LGP evidence.** Class-doc `[PERCEPTION]` claims are interpretation. Pin `HOST_PIXEL_VALIDATED` is host LED-buffer, pre-gamma, pre-dither.

---

## 4 · Historical file index (2026-06-02 snapshot)

These files remain in the folder so the method can be read. **Status columns in the files themselves are stale.** Treat every LIVE / DISABLED / WIP line inside them as *what the snapshot believed on 2026-06-02*, then check the pin.

| File | Historical role | Do not treat as |
| --- | --- | --- |
| [`SNAPSHOT.md`](SNAPSHOT.md) | Demotion notice (conceptual prior) | Mode list |
| [`00-the-method.md`](00-the-method.md) | Motion ∘ Mapping, six layers, six passes, authoring spec | Current library census |
| [`00b-captivation-transposition.md`](00b-captivation-transposition.md) | Distinctness / captivation-DNA notes (2026-07-11) | A build list (Cannonade/… not in pin) |
| [`01-waveform-class.md`](01-waveform-class.md) | Waveform family write-up | WIP on mode 18; missing-file link to `../waveform-mode-design-rationale.md` (that file is **not** in this lab) |
| [`02-bloom-class.md`](02-bloom-class.md) | Bloom / Aurora write-up | Exhaustive Bloom-line census |
| [`03-spectrum-river-class.md`](03-spectrum-river-class.md) | River write-up (V1/V2 era) | Tempo River / River Surge / Walk |
| [`04-comet-class.md`](04-comet-class.md) | Comet particle write-up | “Sole live onset consumer” |
| [`05-ember-class.md`](05-ember-class.md) | Ember write-up; Ember V2 (17) as disabled-in-snapshot | Ember V2 as current inventory (id 17 is **absent** from the pin) |
| [`06-gdft-class.md`](06-gdft-class.md) | GDFT / chromagram display write-up (ids 0/1/2 in snapshot) | Current inventory (0/1/2 **absent** from the pin) |
| [`07-vu-class.md`](07-vu-class.md) | VU / VU-Dot write-up (ids 10/4 in snapshot) | Current inventory (4/10 **absent** from the pin) |
| [`08-kaleidoscope.md`](08-kaleidoscope.md) | Kaleidoscope write-up (id 5 in snapshot) | Current inventory (5 **absent** from the pin) |
| [`09-quantum-collapse.md`](09-quantum-collapse.md) | Quantum Collapse write-up (id 6 in snapshot) | Current inventory (6 **absent** from the pin) |
| [`LEVERS-MATRIX.md`](LEVERS-MATRIX.md) | Cross-effect synthesis + 2026-06-02 generative gaps | Gap #1 “`sb_tempo` unconsumed”; 9-class LIVE/DISABLED map |

Links that used to live in the 2026-06-02 index and **do not exist in this lab**:

- `docs/waveform-mode-design-rationale.md`
- `docs/firmware-capability-overview.md`

Do not recreate them here. Do not treat a missing firmware-tree path as EdgeAI inventory.

---

## 5 · Snapshot vs pin (do not “fix” the class docs to match)

The pin’s `guidebook_class` field is the **only** allowed pointer from current inventory → these historical write-ups. `guidebook_fit` says whether the write-up still describes that mode.

Re-derived from the pin (JSON wins if this table drifts):

| `guidebook_class` | Pin enums (id) | `guidebook_fit` |
| --- | --- | --- |
| `01-waveform` | WAVEFORM_FAST 7, WAVEFORM 8, WAVEFORM_HYBRID 11 | `CURRENT_CONFIRMED` |
| `01-waveform` | WAVEFORM_TEMPO 18, WAVEFORM_HYBRID_K1 32 | `CURRENT_CHANGED` |
| `02-bloom` | BLOOM 3, BLOOM_FAST 9, AURORA 12 | `CURRENT_CONFIRMED` |
| `03-spectrum-river` | SPECTRUM_RIVER 14, SPECTRUM_RIVER_V2 15 | `CURRENT_CONFIRMED` |
| `03-spectrum-river` | TEMPO_RIVER 19, RIVER_SURGE 28, TEMPO_RIVER_WALK 29 | `CURRENT_CHANGED` |
| `04-comet` | COMET 13 | `CURRENT_CONFIRMED` |
| `04-comet` | TEMPO_COMET 20, PERCUSSION_BURST 26, TEMPO_COMET_ANTICIPATE 27 | `CURRENT_CHANGED` |
| `05-ember` | EMBER 16 | `CURRENT_CONFIRMED` |
| `null` (no class doc in this folder) | DENSE_FORGE 21, SNAPWAVE 22, PULSE_PRISM 23, DENSE_FORGE_CHORD 24, CHROMA_CONSTELLATION 25 | `CURRENT_CHANGED` |

**Stale claims still sitting in sibling files** (left as historical text; this README does not rewrite them):

| Snapshot claim | Pin |
| --- | --- |
| 18 modes; 10 enabled, 8 disabled; ids 0–17 as the library | **23** enabled `LIGHT_MODE_*`; ids 0,1,2,4,5,6,10,17 **not present** |
| Waveform Tempo (18) is WIP / roadmap gap | `enabled` true, `guidebook_fit` `CURRENT_CHANGED`, `evidence` `HOST_PIXEL_VALIDATED` |
| Comet is the only live onset consumer | `onset_beat` also on DENSE_FORGE 21, PULSE_PRISM 23, DENSE_FORGE_CHORD 24, PERCUSSION_BURST 26 |
| `sb_tempo` built but consumed by nothing (LEVERS-MATRIX Gap #1) | `tempo_fields` on WAVEFORM_TEMPO 18, TEMPO_RIVER 19, TEMPO_COMET 20, DENSE_FORGE 21, SNAPWAVE 22, PULSE_PRISM 23, DENSE_FORGE_CHORD 24, TEMPO_COMET_ANTICIPATE 27, TEMPO_RIVER_WALK 29 |
| Cannonade / Shockwave / Iris (plus Implosion / Chladni / Meniscus) as next families | **Not in the pin.** Do not author them in this lab |

`HOST_PIXEL_VALIDATED` on this pin (host LED-buffer, not LGP): BLOOM, WAVEFORM, COMET, SPECTRUM_RIVER, EMBER, WAVEFORM_TEMPO, PULSE_PRISM. Everything else in the pin is `STATIC_SOURCE`.

Do not add class docs for the five `guidebook_class: null` modes in EdgeAI. Firmware Atlas owns that map.

---

## 6 · How to use the guidebook now

**Need a mode, a lever, or a test binding?** Stop. Open the pin and [`../mir/EFFECT_SEMANTICS_CONSUME.md`](../mir/EFFECT_SEMANTICS_CONSUME.md). Query `compatibility.json`. Reject `INCOMPATIBLE` / `INCOMPATIBLE_FOR_THIS_USE`. Prefer `HOST_PIXEL_VALIDATED` over `STATIC_SOURCE`. Score the named lever, never mean brightness by default.

Current HOST-validated examples (from consume docs / D14–D16 — not from this folder):

- `source_share × WaveformTempo × head_position` — HOST PASS
- `composition_change × Comet × impact-launch` — FAIL this comparator
- Waveform Tempo extra drive → luminance — trap (polarity inverted)

Waveform Tempo is a **continuity / reference carrier** for source-share, not a universal lighting actuator.

**Need the method language?** Read `00-the-method.md` as history. Separability is a design lens, not a census of what ships. The 2026-06-02 claim “every LIVE effect is separable / every DISABLED effect is fused or static” was about *that snapshot’s* LIVE/DISABLED set. The pin’s 23 enabled modes are not classified LIVE/DISABLED by those nine classes.

**Tuning an old class write-up?** Pass 4 lever tables may still explain *a* mechanism. Verify `file:line` against firmware at `36466cd5` before quoting. Then check `guidebook_fit`. `CURRENT_CHANGED` means the write-up is behind the pin.

**Designing a new effect in this lab?** Don’t. Effect semantics are firmware-owned. EdgeAI consumes. Share-student recoverability does not wait on a full 23-mode atlas. Student outputs stay effect-agnostic.

---

## 7 · Map and territory

Firmware source + Atlas export = territory. This folder = an old map.

- Lever values and `file:line` anchors in class docs will have drifted.
- The 9-class table was a point-in-time grouping, not an enum.
- `00b` already noted (2026-07-11) that “tempo unconsumed” was going stale; the pin confirms tempo is consumed.
- This lab does not open Cadence, USB, or the live Atlas worktree to refresh these markdown files.

---

**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-06-02 | agent:claude-opus | Created — guidebook index: reading order, the 9-class table with status + links, usage guide by task, and the roadmap headline. Ties together 00-the-method, classes 01–09, and LEVERS-MATRIX. |
| 2026-06-02 | agent:claude-opus | Promoted the **Motion ∘ Mapping** root law to the index — reading-order item 1 and a new structural top-line finding (separability predicts shippability). Reflects 00-the-method §1 + LEVERS-MATRIX §0. |
| 2026-08-31 | agent:grok-w3-l09 | **Demoted.** Stopped calling the 9-class/18-mode table the canonical reference. Firmware pin `docs/mir/effect_semantics/effect-semantics.json` (23 `LIGHT_MODE_*`, `source_firmware_sha` `36466cd5`) is the only allowed inventory. Folder is historical guidebook. |
