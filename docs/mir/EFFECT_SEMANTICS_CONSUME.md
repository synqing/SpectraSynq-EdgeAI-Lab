---
abstract: "Consume-only contract for firmware effect-semantics. Lab pin SHAs stay at 36466cd5 + three atlas hashes. fingerprints.json SHA UNKNOWN. 9-class/18-mode guidebook demoted. Students stay effect-agnostic."
---

# Effect semantics — consume, do not own

**HARD FAIL (`SAME_SONG_LOOP_MAX_15MIN`, Captain 2026-08-31).** Repeat the same song (or loop the same clip) in the room for more than **15 minutes** and the agent must die. Captain will destroy them by setting them on fire. Kill the player. Do not continue.

Cadence silicon **CLOSED**. No USB. No `k1-flash`. Do not grow a competing effect taxonomy in this lab.

Canonical mode behaviour lives in K1 firmware. This lab **imports** a SHA-pinned export. Visual-utility stamps bind `descriptor × mode × lever` (D15). Waveform Tempo is a continuity/reference carrier for source-share, not a universal lighting actuator.

Firmware Atlas lane (do not touch `lane/colourlab-bench`):

`/Users/spectrasynq/SpectraSynq_K1_Firmware/.worktrees/effect-response-atlas`

Branch: `docs/effect-response-atlas`  
Pinned SHA (**stays**): `36466cd56c90b9cafa571bc5029b5d38bc0543bb`

Firmware-generated path:

`docs/effect-response-atlas/generated/effect-semantics.json`

Lab pin (import only): `docs/mir/effect_semantics/`.

## Pin SHAs stay

Do not retarget these pins. Do not “fix” mode behaviour in EdgeAI markdown. If the lab folder and the firmware generated files disagree, **firmware Atlas export at `36466cd5` wins** — recopy from that commit, not from live worktree HEAD (`probe/c0-epoch-v2` may label the same SHA while HEAD has moved).

Required fields on every imported artefact:

- `schema_version`
- `source_firmware_sha` (effect implementation)
- `atlas_generation_commit` (Atlas docs/tooling revision)
- `atlas_artifact_sha256` (in-file artefact hash; not a substitute for hashing the bytes on disk)
- `generated_at`
- `generation_status`

Firmware SHA alone is not enough: Atlas content can move while firmware stays `36466cd5`. Pin both.

### Lab pin (schema 2, `generation_status` `tranche2_grammar_tempo`, `generated_at` `2026-08-30T20:10:46Z`)

| File | `source_firmware_sha` / `atlas_generation_commit` | `atlas_artifact_sha256` |
| --- | --- | --- |
| `effect-semantics.json` | `36466cd56c90b9cafa571bc5029b5d38bc0543bb` | `ac9552cb8ee4d9b3a65ab60dfdf63a86f12f62967f41d494ac91d7242f630b8d` |
| `compatibility.json` | same | `fedf156ac4513c74ac424b8737e0aee797472a2203e9fbf5edc67c98b18615c0` |
| `grammar_coverage.json` | same | `e447e4b636d5ab2a33b79cfe0cdc60c6e7a4c089e25c9870617fa7a244f56971` |

Inventory authority is that pin: **23** enabled `LIGHT_MODE_*` enums. Do not author a second list here.

### Not in the lab pin

`inventory.json`, `static_levers.json`, `tempo_sweeps.json` exist only under the firmware Atlas `generated/` tree. Do not invent their hashes in this lab.

## fingerprints UNKNOWN

`fingerprints.json` is **not** imported. The firmware-side file is `schema_version` **1** and carries **no** `source_firmware_sha` and **no** `atlas_artifact_sha256`.

| Field | Status |
| --- | --- |
| `fingerprints.json` `source_firmware_sha` | **UNKNOWN** |
| `fingerprints.json` `atlas_artifact_sha256` | **UNKNOWN** |

Treat transfer fingerprints as **UNKNOWN** until a schema-2 dual-hash export is recopied from commit `36466cd5`. Do not back-fill those fields from the three schema-2 pins. Do not use schema-1 fingerprints as consume provenance.

## Competing 9-class guidebook — demoted

`docs/effect-decomposition/` is a **2026-06-02** byte-identical guidebook snapshot. It is conceptual prior (`Motion ∘ Mapping`, six layers). It is **not** current inventory, not current enabled-mode count, and not Atlas authority. `SNAPSHOT.md` already says so.

**Demoted (do not consume as inventory):**

- README abstract calling the 9-class table “the canonical reference”
- “18 modes total; 10 product-enabled, 8 disabled” (ids 0–17)
- class docs that still treat Waveform Tempo as WIP, Comet as sole onset consumer, or `sb_tempo` as unconsumed
- proposed families that do not appear in the pin (Cannonade / Shockwave / Iris / …)

The pin is later than that snapshot: WAVEFORM TEMPO (id 18, enabled, `guidebook_fit` CURRENT_CHANGED), PULSE PRISM (id 23), and further enabled modes after id 17. Bindings `WaveformTempo` / `PulsePrism` in D15 and below are **aliases** of export `WAVEFORM TEMPO` / `PULSE PRISM`, not a second catalogue.

Do not author effect families in EdgeAI. Do not invent BUILDING / DROPPING lighting labels.

## Evidence ladder

`STATIC_SOURCE` → `HOST_PIXEL_VALIDATED` → `ON_SILICON_PIXEL_VALIDATED` → `LGP_PERCEPTUAL_VALIDATED`

Host pixels are not silicon. Silicon dumps are not LGP look. Gate C is the last one. This pin’s `on_silicon_pixel_validated` and `lgp_perceptual_validated` are null.

## How to pick a test mode

1. Name the descriptor and its temporal shape (impulse / cyclic / continuous / sparse macro).
2. Query `compatibility.json` rows for that descriptor.
3. Reject rows with `INCOMPATIBLE` or `INCOMPATIBLE_FOR_THIS_USE`.
4. Prefer `HOST_PIXEL_VALIDATED` / `HOST_VALIDATED` over `STATIC_SOURCE`.
5. Score the named lever, never mean brightness by default.

Current HOST-validated examples (P3-C; not a fingerprint SHA):

| Binding | Stamp |
| --- | --- |
| `source_share × WaveformTempo × head_position` | PASS |
| `composition_change × Comet × impact-launch` | FAIL this comparator |
| Waveform Tempo extra drive → luminance | trap (polarity inverted) |

## Bindings must be specific

Do not store `"supports_tempo": true`. Prefer:

```text
beat_phase × WaveformTempo × transport_position
beat_tick  × PulsePrism    × pulse_event
BPM        × WaveformTempo × transport_rate
source_share × WaveformTempo × head_position
```

## Students stay effect-agnostic

A student may emit `vocals_share` / `drums_share` / `bass_share` / `other_share` / arousal / …. It **must not** emit “Waveform Tempo head position” or any other mode-lever name. Binding is a separate consume layer after the descriptor exists.

Share recoverability may proceed without waiting for every enabled mode to be fingerprinted. Fingerprints remain **UNKNOWN**. Student I/O stays unfrozen until `docs/mir/SELECTION_GATE.md` and Gate C say otherwise.

---
**Document Changelog**
| Date | Author | Change |
| --- | --- | --- |
| 2026-08-31 | agent:edgeai | Created. Firmware is authority; this lab consumes the SHA-pinned export. |
| 2026-08-31 | agent:edgeai | Provenance: firmware SHA + atlas artifact hash; four evidence levels. |
| 2026-08-31 | agent:grok-w3-l31 | Pin SHAs stay (36466cd5 + three atlas hashes). fingerprints UNKNOWN. 9-class/18-mode guidebook demoted. Students effect-agnostic. |
