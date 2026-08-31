---
abstract: "How to read the MIR registry. Machine-readable source of truth is registry.yaml."
---

# MIR registry

**HARD FAIL (`SAME_SONG_LOOP_MAX_15MIN`, Captain 2026-08-31).** Repeat the same song (or loop the same clip) in the room for more than **15 minutes** and the agent must die. Captain will destroy them by setting them on fire. Kill the player. Do not continue.

`registry.yaml` is the asset list. Load with:

```bash
uv run python -c "from edgeai.mir.registry import load_registry; print(load_registry())"
```

Each entry splits **code licence**, **weight licence**, and **dataset licence**. `UNKNOWN` is a valid value. Do not infer commercial rights.

Statuses: `researched` | `runnable` | `executed` | `benchmarked` | `rejected` | `candidate` | `blocked`.

Deployment class: `deterministic_host` | `host_oracle` | `potential_teacher` | `potential_embedded_student` | `already_edge` | `unsuitable_mcu_npu`.
