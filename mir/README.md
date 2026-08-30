---
abstract: "How to read the MIR registry. Machine-readable source of truth is registry.yaml."
---

# MIR registry

`registry.yaml` is the asset list. Load with:

```bash
uv run python -c "from edgeai.mir.registry import load_registry; print(load_registry())"
```

Each entry splits **code licence**, **weight licence**, and **dataset licence**. `UNKNOWN` is a valid value. Do not infer commercial rights.

Statuses: `researched` | `runnable` | `executed` | `benchmarked` | `rejected` | `candidate` | `blocked`.

Deployment class: `deterministic_host` | `host_oracle` | `potential_teacher` | `potential_embedded_student` | `already_edge` | `unsuitable_mcu_npu`.
