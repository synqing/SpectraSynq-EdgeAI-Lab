---
abstract: "EdgeAI consumes firmware effect-semantics.json. Do not grow a competing taxonomy here. Bind visual evidence as descriptor × mode × lever. Waveform Tempo is a continuity carrier."
---

# Effect semantics — consume, do not own

**HARD FAIL (`SAME_SONG_LOOP_MAX_15MIN`, Captain 2026-08-31).** Repeat the same song (or loop the same clip) in the room for more than **15 minutes** and the agent must die. Captain will destroy them by setting them on fire. Kill the player. Do not continue.

Canonical mode behaviour lives in K1 firmware.

Firmware Atlas lane (do not touch `lane/colourlab-bench`):

`/Users/spectrasynq/SpectraSynq_K1_Firmware/.worktrees/effect-response-atlas`

Branch: `docs/effect-response-atlas`  
Pinned SHA: `36466cd56c90b9cafa571bc5029b5d38bc0543bb`

Export (firmware-generated):

`docs/effect-response-atlas/generated/effect-semantics.json`

Also: `inventory.json`, `static_levers.json`, `fingerprints.json`, `compatibility.json`.

Lab pin (import only): `docs/mir/effect_semantics/`.

## Import rule

When a copy is pinned into this lab, it must carry:

- `schema_version`
- `source_firmware_sha` (effect implementation)
- `atlas_generation_commit` (Atlas docs/tooling revision)
- `atlas_artifact_sha256` (hash of this export)
- `generated_at`
- `generation_status`

Firmware SHA alone is not enough: fingerprints can change while firmware stays `36466cd5`. Pin both. If this folder and the firmware generated files disagree, **firmware Atlas export wins**. Do not “fix” mode behaviour in EdgeAI markdown.

Evidence levels on each claim:

`STATIC_SOURCE` → `HOST_PIXEL_VALIDATED` → `ON_SILICON_PIXEL_VALIDATED` → `LGP_PERCEPTUAL_VALIDATED`

Host pixels are not silicon. Silicon dumps are not LGP look. Gate C is the last one.

The `docs/effect-decomposition/` copy in this repo is a **byte-identical snapshot** of the 2026-06-02 guidebook. It is conceptual prior, not current implementation authority.

## How to pick a test mode

1. Name the descriptor and its temporal shape (impulse / cyclic / continuous / sparse macro).
2. Query `compatibility.json` rows for that descriptor.
3. Reject rows with `INCOMPATIBLE` or `INCOMPATIBLE_FOR_THIS_USE`.
4. Prefer `HOST_VALIDATED` over `STATIC_SOURCE`.
5. Score the named lever, never mean brightness by default.

Current HOST-validated examples:

| Binding | Stamp |
| --- | --- |
| `source_share × WaveformTempo × head_position` | PASS |
| `composition_change × Comet × impact-launch` | FAIL this comparator |
| Waveform Tempo extra drive → luminance | trap (polarity inverted) |

## Bindings must be specific. Do not store `"supports_tempo": true`. Prefer:

```text
beat_phase × WaveformTempo × transport_position
beat_tick  × PulsePrism    × pulse_event
BPM        × WaveformTempo × transport_rate
source_share × WaveformTempo × head_position
```

Student outputs stay effect-agnostic

A student may emit `vocals_share` / `drums_share` / …. It must not emit “Waveform Tempo head position”. Binding is a separate layer.

The share recoverability experiment may proceed without waiting for every enabled mode to be fingerprinted.

---
**Document Changelog**
| Date | Author | Change |
| --- | --- | --- |
| 2026-08-31 | agent:edgeai | Created. Firmware is authority; this lab consumes the SHA-pinned export. |
| 2026-08-31 | agent:edgeai | Provenance: firmware SHA + atlas artifact hash; four evidence levels. |
