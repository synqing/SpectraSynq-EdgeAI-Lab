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
