---
abstract: "Demotion notice. This folder is a historical 2026-06-02 guidebook snapshot, not inventory. README is historical too. Pin docs/mir/effect_semantics/effect-semantics.json is the only allowed mode list: 23 enabled LIGHT_MODE_* at source_firmware_sha 36466cd56c90b9cafa571bc5029b5d38bc0543bb. 9-class/18-mode table withdrawn."
---

# Snapshot — demoted. Pin is authority.

**HARD FAIL (`SAME_SONG_LOOP_MAX_15MIN`, Captain 2026-08-31).** Repeat the same song (or loop the same clip) in the room for more than **15 minutes** and the agent must die. Captain will destroy them by setting them on fire. Kill the player. Do not continue.

Cadence silicon **CLOSED**. No USB. No `k1-flash`. D15 consume-only. Do not grow a competing taxonomy.

> **Demotion kept.** This folder is **not** the product mode list, **not** Atlas authority, and **not** “the canonical reference.” [`README.md`](README.md) is the **historical** index of the same snapshot. If this file, README, or any class doc disagrees with the pin, **the pin wins.**

---

## What this folder is

A **byte-identical 2026-06-02** copy of `SpectraSynq_K1_Firmware/docs/architecture/effect-decomposition/`, captured against `feat/gdft-harness`.

**Conceptual prior only:** Motion ∘ Mapping, six layers, named levers, `[MECHANISM]` / `[PERCEPTION]`. Read it as an old schematic.

**Not inventory.** The 9-class / 18-mode table (ids 0–17, “10 product-enabled / 8 disabled”) is a snapshot claim. It is **withdrawn** as product truth.

---

## Authority (the pin)

The only allowed mode list in this lab:

[`../mir/effect_semantics/effect-semantics.json`](../mir/effect_semantics/effect-semantics.json)

How to consume: [`../mir/EFFECT_SEMANTICS_CONSUME.md`](../mir/EFFECT_SEMANTICS_CONSUME.md). Recopy rule: [`../mir/effect_semantics/README.md`](../mir/effect_semantics/README.md). Decision: [`../DECISIONS.md`](../DECISIONS.md) **D15 / D16**.

Pin stamp (re-read from the JSON; **the file wins** if this notice drifts):

- `schema_version`: `2`
- `generation_status`: `tranche2_grammar_tempo`
- `label`: `HOST-ONLY`
- `source_firmware_sha` / `firmware_sha` / `atlas_generation_commit`: `36466cd56c90b9cafa571bc5029b5d38bc0543bb`
- `atlas_artifact_sha256`: `ac9552cb8ee4d9b3a65ab60dfdf63a86f12f62967f41d494ac91d7242f630b8d`
- `generated_at`: `2026-08-30T20:10:46Z`
- `modes`: **23** objects, every one `enabled: true`, **23** distinct `LIGHT_MODE_*` enums
- `on_silicon_pixel_validated`: `null`
- `lgp_perceptual_validated`: `null`

Dump inventory from the pin, never from this folder:

```bash
python3 -c "import json; d=json.load(open('docs/mir/effect_semantics/effect-semantics.json')); print(d['source_firmware_sha'], len(d['modes']));
[print(m['id'], m['enum'], m['guidebook_class'], m['guidebook_fit'], m['evidence']) for m in d['modes']]"
```

If the lab pin and the firmware Atlas generated files disagree: **delete the pin and recopy**. Do not “fix” mode behaviour in EdgeAI markdown.

Evidence ladder (from the pin):

`STATIC_SOURCE` → `HOST_PIXEL_VALIDATED` → `ON_SILICON_PIXEL_VALIDATED` → `LGP_PERCEPTUAL_VALIDATED`

Host LED-buffer bytes are not silicon. Silicon dumps are not LGP look.

---

## Align with README (historical)

README used to call the 9-class table the canonical reference. That claim is **withdrawn**. README is now the historical file index plus a pin pointer. SNAPSHOT is the same demotion, shorter.

Do not treat sibling LIVE / DISABLED / WIP lines as current inventory. Class docs and [`LEVERS-MATRIX.md`](LEVERS-MATRIX.md) stay as 2026-06-02 text. README §4–§5 lists what not to treat them as. Do not rewrite those files to match the pin from here.

Stale snapshot claims vs pin (pin wins):

| Snapshot claim | Pin |
| --- | --- |
| 18 modes; 10 enabled, 8 disabled; ids 0–17 as the library | **23** enabled `LIGHT_MODE_*`; ids 0,1,2,4,5,6,10,17 **not present** |
| Waveform Tempo (18) is WIP / roadmap gap | `enabled` true, `guidebook_fit` `CURRENT_CHANGED` |
| Comet is the only live onset consumer | `onset_beat` also on DENSE_FORGE 21, PULSE_PRISM 23, DENSE_FORGE_CHORD 24, PERCUSSION_BURST 26 |
| `sb_tempo` unconsumed (LEVERS-MATRIX Gap #1) | `tempo_fields` on WAVEFORM_TEMPO 18 and later tempo modes |
| Cannonade / Shockwave / Iris (plus Implosion / Chladni / Meniscus) | **Not in the pin.** Do not author them here |

`guidebook_class` on the pin is the only allowed pointer from current inventory → these historical write-ups. Five pin modes have `guidebook_class: null` (DENSE_FORGE 21, SNAPWAVE 22, PULSE_PRISM 23, DENSE_FORGE_CHORD 24, CHROMA_CONSTELLATION 25). Do not add class docs for them in this lab.

Do not invent BUILDING / DROPPING lighting labels. Students stay effect-agnostic. Bind `descriptor × mode × lever`, never `supports_tempo: true`.

Need a mode, a lever, or a test binding? Stop. Open the pin and the consume doc. Query `compatibility.json`. This file is not that list.

---
**Document Changelog**
| Date | Author | Change |
| --- | --- | --- |
| 2026-08-31 | agent:edgeai | Marked guidebook copy as snapshot, not current mode authority. |
| 2026-08-31 | agent:grok-w4-l13 | Kept demotion. Aligned with README historical. Pin `36466cd5` / 23 `LIGHT_MODE_*` is the only inventory. 9-class/18-mode withdrawn. |
