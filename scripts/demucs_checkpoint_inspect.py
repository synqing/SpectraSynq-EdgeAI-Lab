#!/usr/bin/env python3
"""J1.5: inspect the pinned HT-Demucs Safetensors header without loading tensors.

HOST-ONLY. Standard library only. No import/install of Demucs, Torch, Safetensors,
hub clients, or network code. The tensor payload is streamed only for SHA256; it
is never decoded or materialised. The only write is the named JSON receipt.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from collections import Counter
from pathlib import Path
from typing import Any, BinaryIO, Mapping

CHECKPOINT_ID = "955717e8"
EXPECTED_SHA256 = "d9fa14133cfcc034a6758923bb3a8ca9f8dfd0b582134643bbf83f72c17576dd"
EXPECTED_SIZE = 84_025_440
EXPECTED_CLASS = "demucs.htdemucs.HTDemucs"
TEACHER_SOURCES = ("vocals", "drums", "bass", "other")
DEFAULT_CHECKPOINT = (
    Path.home()
    / ".cache/huggingface/hub/models--adefossez--HTDemucs"
    / "snapshots/bf35a81b663819a8255c8fefee17f9d812b786b5"
    / f"{CHECKPOINT_ID}.safetensors"
)
DEFAULT_RECEIPT = (
    Path(__file__).resolve().parents[1]
    / "docs/mir/receipts/demucs/J15_INSPECT.json"
)
MAX_HEADER_BYTES = 16 * 1024 * 1024
SHA_CHUNK_BYTES = 1024 * 1024

_DTYPE_BYTES = {
    "BOOL": 1,
    "U8": 1,
    "I8": 1,
    "F8_E4M3": 1,
    "F8_E5M2": 1,
    "I16": 2,
    "U16": 2,
    "F16": 2,
    "BF16": 2,
    "I32": 4,
    "U32": 4,
    "F32": 4,
    "F64": 8,
    "I64": 8,
    "U64": 8,
}


class InspectionError(ValueError):
    """A bounded structural read could not validate the local object."""


def sha256_file(path: Path) -> str:
    """Stream a file into SHA256 without retaining the tensor payload."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(SHA_CHUNK_BYTES), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_exact(handle: BinaryIO, size: int) -> bytes:
    data = handle.read(size)
    if len(data) != size:
        raise InspectionError(f"truncated read: expected {size}, got {len(data)}")
    return data


def read_safetensors_header(path: Path) -> tuple[dict[str, Any], int]:
    """Read only the 8-byte prefix and bounded JSON header."""
    file_size = path.stat().st_size
    with path.open("rb") as handle:
        raw_length = _read_exact(handle, 8)
        (header_length,) = struct.unpack("<Q", raw_length)
        if header_length <= 0 or header_length > MAX_HEADER_BYTES:
            raise InspectionError(f"invalid header length: {header_length}")
        if 8 + header_length > file_size:
            raise InspectionError(
                f"header exceeds file: header={header_length}, file={file_size}"
            )
        raw_header = _read_exact(handle, header_length)
    try:
        header = json.loads(raw_header.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise InspectionError(f"invalid JSON header: {exc}") from exc
    if not isinstance(header, dict):
        raise InspectionError("Safetensors header must be a JSON object")
    return header, header_length


def _tensor_nbytes(spec: Mapping[str, Any]) -> int | None:
    dtype = spec.get("dtype")
    shape = spec.get("shape")
    if dtype not in _DTYPE_BYTES or not isinstance(shape, list):
        return None
    elements = 1
    for dimension in shape:
        if not isinstance(dimension, int) or isinstance(dimension, bool) or dimension < 0:
            return None
        elements *= dimension
    return elements * _DTYPE_BYTES[dtype]


def validate_tensor_index(
    header: Mapping[str, Any], payload_bytes: int
) -> dict[str, Any]:
    """Validate tensor metadata and offsets without reading tensor values."""
    errors: list[str] = []
    intervals: list[tuple[int, int, str]] = []
    dtype_counts: Counter[str] = Counter()
    tensor_keys: list[str] = []

    for key, raw_spec in header.items():
        if key == "__metadata__":
            continue
        tensor_keys.append(key)
        if not isinstance(raw_spec, dict):
            errors.append(f"{key}: tensor entry is not an object")
            continue
        dtype = raw_spec.get("dtype")
        offsets = raw_spec.get("data_offsets")
        if isinstance(dtype, str):
            dtype_counts[dtype] += 1
        if (
            not isinstance(offsets, list)
            or len(offsets) != 2
            or any(not isinstance(v, int) or isinstance(v, bool) for v in offsets)
        ):
            errors.append(f"{key}: invalid data_offsets")
            continue
        start, end = offsets
        if start < 0 or end < start or end > payload_bytes:
            errors.append(f"{key}: offsets [{start}, {end}] outside payload")
            continue
        expected_nbytes = _tensor_nbytes(raw_spec)
        if expected_nbytes is None:
            errors.append(f"{key}: unsupported dtype or invalid shape")
        elif end - start != expected_nbytes:
            errors.append(
                f"{key}: byte span {end - start} != shape/dtype {expected_nbytes}"
            )
        intervals.append((start, end, key))

    intervals.sort()
    previous_end = 0
    for start, end, key in intervals:
        if start != previous_end:
            relation = "overlap" if start < previous_end else "gap"
            errors.append(f"{key}: payload {relation} at {start}, expected {previous_end}")
        previous_end = max(previous_end, end)
    if intervals and previous_end != payload_bytes:
        errors.append(f"payload coverage ends at {previous_end}, expected {payload_bytes}")
    if not tensor_keys:
        errors.append("no tensors in header")

    key_digest = hashlib.sha256("\0".join(sorted(tensor_keys)).encode("utf-8")).hexdigest()
    return {
        "tensor_count": len(tensor_keys),
        "dtype_counts": dict(sorted(dtype_counts.items())),
        "tensor_key_sha256": key_digest,
        "offsets_and_shapes_valid": not errors,
        "errors": errors[:20],
    }


def _parse_metadata(header: Mapping[str, Any]) -> dict[str, Any]:
    raw_metadata = header.get("__metadata__")
    if not isinstance(raw_metadata, dict):
        raise InspectionError("missing Safetensors __metadata__ object")
    klass = raw_metadata.get("klass")
    raw_args = raw_metadata.get("args")
    raw_kwargs = raw_metadata.get("kwargs")
    if not all(isinstance(value, str) for value in (klass, raw_args, raw_kwargs)):
        raise InspectionError("metadata must contain string klass, args, and kwargs")
    try:
        args = json.loads(raw_args)
        kwargs = json.loads(raw_kwargs)
    except json.JSONDecodeError as exc:
        raise InspectionError(f"metadata args/kwargs are not JSON: {exc}") from exc
    if not isinstance(args, list) or not isinstance(kwargs, dict):
        raise InspectionError("metadata args must be a list and kwargs an object")
    return {"klass": klass, "args": args, "kwargs": kwargs}


def _companion_inventory(checkpoint: Path) -> dict[str, Any]:
    snapshot = checkpoint.parent
    entries: list[dict[str, Any]] = []
    for entry in sorted(snapshot.iterdir(), key=lambda item: item.name):
        resolved = entry.resolve(strict=False)
        entries.append(
            {
                "name": entry.name,
                "is_symlink": entry.is_symlink(),
                "symlink_target": str(entry.readlink()) if entry.is_symlink() else None,
                "resolved_size": resolved.stat().st_size if resolved.is_file() else None,
            }
        )

    companion = snapshot / "htdemucs.yaml"
    companion_text = companion.read_text(encoding="utf-8") if companion.is_file() else ""
    normalised = "".join(companion_text.split())
    expected_forms = {
        f"models:['{CHECKPOINT_ID}']",
        f'models:["{CHECKPOINT_ID}"]',
    }
    references_checkpoint = normalised in expected_forms
    invented_config_absent = not (snapshot / "config.json").exists()
    return {
        "snapshot_entries": entries,
        "htdemucs_yaml_present": companion.is_file(),
        "htdemucs_yaml_sha256": (
            hashlib.sha256(companion_text.encode("utf-8")).hexdigest()
            if companion_text
            else None
        ),
        "htdemucs_yaml_references_checkpoint": references_checkpoint,
        "config_json_absent": invented_config_absent,
    }


def inspect_checkpoint(checkpoint: Path, expected_sha256: str) -> dict[str, Any]:
    """Return the J1.5 receipt body. This function never writes."""
    checkpoint = checkpoint.expanduser()
    receipt: dict[str, Any] = {
        "job": "J1.5",
        "label": "HOST-ONLY",
        "teacher_schema": "DEMUCS_TEACHER_SCHEMA_V1",
        "checkpoint_id": CHECKPOINT_ID,
        "checkpoint_path": str(checkpoint),
        "expected_sha256": expected_sha256,
        "tensor_load": False,
        "network_attempted": False,
        "package_installed": False,
        "config_synthesised": False,
        "student_io_frozen": False,
        "titan": False,
    }
    if not checkpoint.is_file():
        return {
            **receipt,
            "sha256_match": False,
            "structurally_plausible": False,
            "verdict": "LOCAL_CHECKPOINT_MISSING",
            "errors": ["checkpoint file is missing"],
        }

    file_size = checkpoint.stat().st_size
    actual_sha256 = sha256_file(checkpoint)
    receipt.update(
        {
            "file_size": file_size,
            "expected_size": EXPECTED_SIZE,
            "size_match": file_size == EXPECTED_SIZE,
            "actual_sha256": actual_sha256,
            "sha256_match": actual_sha256 == expected_sha256,
            "sha256_stream_chunk_bytes": SHA_CHUNK_BYTES,
        }
    )
    if actual_sha256 != expected_sha256:
        return {
            **receipt,
            "structurally_plausible": False,
            "verdict": "CHECKPOINT_SHA256_MISMATCH",
            "errors": ["checkpoint SHA256 does not match the D26 pin"],
        }

    try:
        header, header_length = read_safetensors_header(checkpoint)
        payload_bytes = file_size - 8 - header_length
        tensor_index = validate_tensor_index(header, payload_bytes)
        model_metadata = _parse_metadata(header)
        companions = _companion_inventory(checkpoint)
        kwargs = model_metadata["kwargs"]
        source_order = kwargs.get("sources")
        source_set_valid = (
            isinstance(source_order, list)
            and len(source_order) == len(TEACHER_SOURCES)
            and set(source_order) == set(TEACHER_SOURCES)
        )
        source_mapping = (
            {name: source_order.index(name) for name in TEACHER_SOURCES}
            if source_set_valid
            else None
        )
        checks = {
            "size_match": file_size == EXPECTED_SIZE,
            "class_match": model_metadata["klass"] == EXPECTED_CLASS,
            "source_set_valid": source_set_valid,
            "tensor_index_valid": tensor_index["offsets_and_shapes_valid"],
            "companion_references_checkpoint": companions[
                "htdemucs_yaml_references_checkpoint"
            ],
            "model_definition_in_metadata": bool(
                model_metadata["klass"] and isinstance(kwargs, dict) and kwargs
            ),
        }
        plausible = all(checks.values())
        receipt.update(
            {
                "safetensors_header_bytes": header_length,
                "tensor_payload_bytes": payload_bytes,
                "model_class": model_metadata["klass"],
                "model_args": model_metadata["args"],
                "model_source_order": source_order,
                "teacher_source_mapping": source_mapping,
                "samplerate": kwargs.get("samplerate"),
                "audio_channels": kwargs.get("audio_channels"),
                "segment": kwargs.get("segment"),
                "model_definition_source": "SAFETENSORS_METADATA",
                "tensor_index": tensor_index,
                "companions": companions,
                "checks": checks,
                "structurally_plausible": plausible,
                "verdict": (
                    "STRUCTURALLY_PLAUSIBLE_FOR_OFFLINE_LOAD_PROBE"
                    if plausible
                    else "LOCAL_CHECKPOINT_INCOMPLETE"
                ),
                "errors": tensor_index["errors"],
            }
        )
    except (InspectionError, OSError) as exc:
        receipt.update(
            {
                "structurally_plausible": False,
                "verdict": "LOCAL_CHECKPOINT_INCOMPLETE",
                "errors": [str(exc)],
            }
        )
    return receipt


def _exit_code(receipt: Mapping[str, Any]) -> int:
    if not receipt.get("sha256_match", False):
        return 1
    if receipt.get("structurally_plausible") is True:
        return 0
    if receipt.get("verdict") == "LOCAL_CHECKPOINT_INCOMPLETE":
        return 0
    return 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Inspect the pinned HT-Demucs Safetensors header without tensor load."
    )
    parser.add_argument("--checkpoint", type=Path, default=DEFAULT_CHECKPOINT)
    parser.add_argument("--expected-sha256", default=EXPECTED_SHA256)
    parser.add_argument("--receipt", type=Path, default=DEFAULT_RECEIPT)
    args = parser.parse_args(argv)

    receipt = inspect_checkpoint(args.checkpoint, args.expected_sha256)
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(receipt["verdict"], flush=True)
    print(json.dumps(receipt, sort_keys=True), flush=True)
    return _exit_code(receipt)


if __name__ == "__main__":
    raise SystemExit(main())
