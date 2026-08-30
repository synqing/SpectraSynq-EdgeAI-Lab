"""Blind Version 1/2/3 assignment. Key is sealed until after judging."""

from __future__ import annotations

import hashlib
from typing import Any, Iterable

import numpy as np


def permute_conditions(
    conditions: Iterable[str],
    *,
    clip_id: str,
    salt: str,
) -> tuple[list[str], dict[str, Any]]:
    conds = [str(c) for c in conditions]
    digest = hashlib.sha256(f"{salt}|{clip_id}".encode()).digest()
    rng = np.random.default_rng(int.from_bytes(digest[:8], "little"))
    order = [str(x) for x in rng.permutation(np.array(conds, dtype=object))]
    labels = version_labels(order)
    key = {
        "clip_id": clip_id,
        "order": order,
        "labels": labels,
        "map": {labels[i]: order[i] for i in range(len(order))},
    }
    return order, key


def version_labels(order: list[str]) -> list[str]:
    return [f"Version {i + 1}" for i in range(len(order))]


def sealed_key(clip_keys: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return {
        "open_after_judging": True,
        "instruction": "Do not open until Version 1/2/3 have been scored.",
        "clips": clip_keys,
    }
