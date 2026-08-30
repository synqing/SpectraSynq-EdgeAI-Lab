#!/usr/bin/env python3
"""P2: Essentia TF oracles. Uses maintained wheels, not TF1 musicnn."""

from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    try:
        import essentia  # noqa: F401
        from essentia.standard import MonoLoader  # noqa: F401
    except ImportError:
        print(
            json.dumps(
                {
                    "status": "blocked",
                    "reason": "essentia not installed",
                    "install": (
                        "uv pip install essentia-tensorflow "
                        "(official cp312 macosx arm64 wheels exist; "
                        "do not revive TF1 musicnn)"
                    ),
                }
            )
        )
        return 2
    info = {"status": "runnable", "essentia": getattr(essentia, "__version__", "unknown")}
    try:
        import essentia.standard as es

        names = [n for n in dir(es) if n.startswith("TensorflowPredict")]
        info["tf_predictors"] = names
    except Exception as exc:
        info["tf_predictors_error"] = str(exc)
    print(json.dumps(info, indent=2))
    Path("artifacts/essentia_probe.json").parent.mkdir(parents=True, exist_ok=True)
    Path("artifacts/essentia_probe.json").write_text(json.dumps(info, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
