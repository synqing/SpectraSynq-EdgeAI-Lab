"""P3-C challenge (oracle-ranked) vs holdout (test partition, not oracle-ranked)."""

from __future__ import annotations

import hashlib
from typing import Any

CLASSES = (
    "vocals_ownership_change",
    "drums_ownership_change",
    "bass_dominance",
    "composition_without_loudness",
    "loudness_without_composition",
)


def challenge_ten(selected: list[dict[str, Any]], k_per: int = 2) -> list[dict[str, Any]]:
    """Keep P3-B's ranked 20 as the challenge pool; take k_per per class."""
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for cls in CLASSES:
        n = 0
        for row in selected:
            if row.get("select_class") != cls:
                continue
            name = str(row["track"])
            if name in seen:
                continue
            item = dict(row)
            item["set"] = "challenge"
            out.append(item)
            seen.add(name)
            n += 1
            if n >= k_per:
                break
    return out


def _quartile(duration_s: float, qs: list[float]) -> int:
    return int(duration_s > qs[0]) + int(duration_s > qs[1]) + int(duration_s > qs[2])


def holdout_ten(
    test_tracks: list[dict[str, Any]],
    challenge: list[dict[str, Any]],
    n: int = 10,
    seed: int = 20260831,
) -> list[dict[str, Any]]:
    """MUSDB test tracks, stratified by duration quartile. Not oracle-ranked."""
    exclude = {str(r["track"]) for r in challenge}
    pool = [t for t in test_tracks if str(t["track"]) not in exclude and t.get("subset") == "test"]
    if not pool:
        return []
    durs = [float(t["duration_s"]) for t in pool]
    if len(durs) >= 4:
        import numpy as np

        qs = [float(x) for x in np.quantile(np.asarray(durs, dtype=np.float64), [0.25, 0.5, 0.75])]
    else:
        qs = [min(durs), float(sorted(durs)[len(durs) // 2]), max(durs)]
    buckets: list[list[dict[str, Any]]] = [[] for _ in range(4)]
    for t in pool:
        buckets[_quartile(float(t["duration_s"]), qs)].append(t)
    for b in buckets:
        b.sort(key=lambda r: hashlib.sha256(f"{seed}|{r['track']}".encode()).hexdigest())
    out: list[dict[str, Any]] = []
    i = 0
    while len(out) < n:
        progressed = False
        for b in buckets:
            if i < len(b):
                row = dict(b[i])
                row["ranked_by"] = "duration_quartile+name"
                row["set"] = "holdout"
                dur = float(row["duration_s"])
                row["t"] = min(0.20 * dur, max(0.0, dur - 8.0))
                out.append(row)
                progressed = True
                if len(out) >= n:
                    break
        if not progressed:
            break
        i += 1
    return out[:n]
