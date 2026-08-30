"""Interface for later visual A/B. Not a GUI. Not a user-research platform.

A visual engine can consume `SemanticFrame` JSON without knowing which teacher
produced it. BASELINE = existing DSP. TREATMENT = DSP + these optional fields.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class SemanticFrame:
    t_s: float
    provenance: list[str]
    # Optional; omit rather than invent.
    rms: float | None = None
    onset: float | None = None
    novelty: float | None = None
    vocals: float | None = None
    drums: float | None = None
    bass: float | None = None
    arousal: float | None = None
    valence: float | None = None
    extras: dict[str, float] = field(default_factory=dict)

    def to_json(self) -> dict[str, Any]:
        return asdict(self)


MODULATION_WEIGHT = 0.65
FROZEN_MAP_VERSION = "p3b-v1"
FROZEN_PERCENTILES = (5.0, 95.0)


def fit_frozen_map(series: dict[str, Any], *, p_lo: float = 5.0, p_hi: float = 95.0) -> dict[str, dict[str, float]]:
    """Fit one 5th–95th map per signal on the pooled corpus. Not per-song min-max."""
    import numpy as np

    out: dict[str, dict[str, float]] = {}
    for name, xs in series.items():
        a = np.asarray(xs, dtype=np.float64).reshape(-1)
        a = a[np.isfinite(a)]
        if a.size == 0:
            out[name] = {"p_lo": 0.0, "p_hi": 1.0, "percentile_lo": p_lo, "percentile_hi": p_hi}
            continue
        lo = float(np.percentile(a, p_lo))
        hi = float(np.percentile(a, p_hi))
        if hi - lo < 1e-8:
            hi = lo + 1e-8
        out[name] = {"p_lo": lo, "p_hi": hi, "percentile_lo": p_lo, "percentile_hi": p_hi}
    return out


def apply_frozen_map(xs: Any, spec: dict[str, float]) -> list[float]:
    import numpy as np

    a = np.asarray(xs, dtype=np.float64).reshape(-1)
    lo = float(spec["p_lo"])
    hi = float(spec["p_hi"])
    y = (a - lo) / (hi - lo)
    y = np.clip(y, 0.0, 1.0)
    return [float(v) for v in y]


def per_song_norm(xs: list[float]) -> list[float]:
    """Min-max to [0, 1] inside one song. Do not mix songs."""
    lo, hi = min(xs), max(xs)
    span = (hi - lo) or 1.0
    return [(x - lo) / span for x in xs]


def modulate(base: list[float], extra: list[float], weight: float = MODULATION_WEIGHT) -> list[float]:
    """Identical extra degree of freedom for energy control and semantic oracle.

    A = base
    B = (1-w)*base + w*energy
    C = (1-w)*base + w*oracle
    Same w, same mix. If B and C look the same, the oracle is not doing extra work.
    """
    if len(base) != len(extra):
        raise ValueError("base and extra must be the same length")
    w = float(weight)
    return [(1.0 - w) * b + w * e for b, e in zip(base, extra)]


SCHEMA_NOTE = """
Visual utility questions (fill later, on-device or in sim):
- Do transitions look more musically intentional?
- Better large-scale structural correspondence?
- Information not already in energy?
- Fewer inappropriate reactions?
- Genre generalisation?
- Does added lag hurt sync?

MIR correctness ≠ visual usefulness.
"""
