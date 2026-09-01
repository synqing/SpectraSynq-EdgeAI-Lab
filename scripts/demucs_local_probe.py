#!/usr/bin/env python3
"""J2: SHA-bound local HT-Demucs construction under the network tripwire."""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from edgeai.mir.demucs_local_loader import (  # noqa: E402
    CHECKPOINT,
    CHECKPOINT_SHA256,
    NAMED_GO,
    DemucsLoadRefused,
    pinned_demucs_model,
)
DEFAULT_RECEIPT = ROOT / "docs/mir/receipts/demucs/J2_LOCAL_LOAD.json"


def _refusal(verdict: str, detail: str) -> dict[str, object]:
    return {
        "job": "J2",
        "label": "HOST-ONLY",
        "verdict": verdict,
        "detail": detail,
        "model_constructed": False,
        "network_fetch": False,
        "titan": False,
        "student_io_frozen": False,
    }


def load_local(checkpoint: Path) -> tuple[dict[str, object], int]:
    try:
        with pinned_demucs_model(checkpoint) as model:
            source_order = list(model.sources)
            expected = ["vocals", "drums", "bass", "other"]
            mapping_valid = len(source_order) == 4 and set(source_order) == set(expected)
            if not mapping_valid:
                return _refusal("DEMUCS_SOURCE_MAPPING_INVALID", repr(source_order)), 4
            source_mapping = {name: source_order.index(name) for name in expected}
            state = model.state_dict()
            receipt: dict[str, object] = {
                "job": "J2",
                "label": "HOST-ONLY",
                "verdict": "LOCAL_CHECKPOINT_LOAD_PASS",
                "named_go": NAMED_GO,
                "checkpoint_path": str(checkpoint),
                "checkpoint_sha256": CHECKPOINT_SHA256,
                "demucs_version": importlib.metadata.version("demucs"),
                "torch_version": importlib.metadata.version("torch"),
                "safetensors_version": importlib.metadata.version("safetensors"),
                "model_class": f"{model.__class__.__module__}.{model.__class__.__name__}",
                "model_constructed": True,
                "model_eval": not model.training,
                "state_tensor_count": len(state),
                "parameter_count": sum(parameter.numel() for parameter in model.parameters()),
                "samplerate": int(model.samplerate),
                "audio_channels": int(model.audio_channels),
                "model_source_order": source_order,
                "teacher_source_mapping": source_mapping,
                "mapping_valid": True,
                "network_guard": "ACTIVE_DURING_IMPORT_AND_LOAD",
                "network_fetch": False,
                "separator_constructed": False,
                "repo_none": False,
                "waveform_persisted": False,
                "titan": False,
                "student_io_frozen": False,
            }
    except DemucsLoadRefused as exc:
        code = 3 if exc.code in {"DEMUCS_TITAN_REFUSED", "DEMUCS_NAMED_GO_REQUIRED"} else 4
        return _refusal(exc.code, exc.detail), code
    except Exception as exc:
        return _refusal(
            "LOCAL_CHECKPOINT_LOAD_FAILED", f"{type(exc).__name__}: {exc}"
        ), 4
    return receipt, 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Load the exact local HT-Demucs model offline.")
    parser.add_argument("--checkpoint", type=Path, default=CHECKPOINT)
    parser.add_argument("--receipt", type=Path, default=DEFAULT_RECEIPT)
    args = parser.parse_args(argv)
    receipt, code = load_local(args.checkpoint)
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(receipt["verdict"], flush=True)
    if code:
        print(receipt.get("detail", "refused"), flush=True)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
