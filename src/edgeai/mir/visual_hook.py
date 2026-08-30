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
