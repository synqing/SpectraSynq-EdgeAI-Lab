"""J1.5 Safetensors inspection: bounded header, pinned SHA, no tensor/network load."""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import socket
import struct
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "demucs_checkpoint_inspect.py"


def _load_inspector():
    spec = importlib.util.spec_from_file_location("demucs_checkpoint_inspect", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _fake_safetensors(path: Path, *, valid: bool = True) -> str:
    metadata = {
        "klass": "demucs.htdemucs.HTDemucs",
        "args": "[]",
        "kwargs": json.dumps(
            {
                "sources": ["drums", "bass", "other", "vocals"],
                "samplerate": 44100,
                "audio_channels": 2,
            }
        ),
    }
    header = {
        "__metadata__": metadata,
        "encoder.weight": {
            "dtype": "F16",
            "shape": [2],
            "data_offsets": [0, 4 if valid else 6],
        },
    }
    raw_header = json.dumps(header, separators=(",", ":")).encode("utf-8")
    raw_header += b" " * ((8 - len(raw_header) % 8) % 8)
    path.write_bytes(struct.pack("<Q", len(raw_header)) + raw_header + b"\0" * 4)
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_source_has_no_tensor_loader_network_or_package_install() -> None:
    source = SCRIPT.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports = {
        node.names[0].name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import) and node.names
    }
    from_imports = {
        node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)
    }
    forbidden_imports = {
        "torch",
        "safetensors",
        "socket",
        "urllib",
        "requests",
        "huggingface_hub",
        "subprocess",
        "demucs",
    }
    assert forbidden_imports.isdisjoint(imports | from_imports)
    assert "torch.load" not in source
    assert "safe_open" not in source
    assert "read_bytes" not in source
    assert "config.json\").write" not in source


def test_header_read_is_bounded_and_payload_is_not_read(tmp_path: Path, monkeypatch) -> None:
    module = _load_inspector()
    checkpoint = tmp_path / "model.safetensors"
    _fake_safetensors(checkpoint)
    calls: list[int] = []
    original = module._read_exact

    def _record(handle, size):
        calls.append(size)
        return original(handle, size)

    monkeypatch.setattr(module, "_read_exact", _record)
    header, header_bytes = module.read_safetensors_header(checkpoint)
    assert header["__metadata__"]["klass"] == module.EXPECTED_CLASS
    assert calls == [8, header_bytes]
    assert sum(calls) < checkpoint.stat().st_size


def test_valid_header_is_structurally_plausible_with_exact_companion(
    tmp_path: Path, monkeypatch
) -> None:
    module = _load_inspector()
    checkpoint = tmp_path / "955717e8.safetensors"
    expected_sha = _fake_safetensors(checkpoint)
    (tmp_path / "htdemucs.yaml").write_text(
        "models: ['955717e8']\n", encoding="utf-8"
    )
    monkeypatch.setattr(module, "EXPECTED_SIZE", checkpoint.stat().st_size)
    receipt = module.inspect_checkpoint(checkpoint, expected_sha)
    assert receipt["sha256_match"] is True
    assert receipt["structurally_plausible"] is True
    assert receipt["teacher_source_mapping"] == {
        "vocals": 3,
        "drums": 0,
        "bass": 1,
        "other": 2,
    }
    assert receipt["tensor_load"] is False
    assert receipt["network_attempted"] is False


def test_incomplete_companion_is_legal_fail_closed(tmp_path: Path, monkeypatch) -> None:
    module = _load_inspector()
    checkpoint = tmp_path / "955717e8.safetensors"
    expected_sha = _fake_safetensors(checkpoint)
    monkeypatch.setattr(module, "EXPECTED_SIZE", checkpoint.stat().st_size)
    receipt = module.inspect_checkpoint(checkpoint, expected_sha)
    assert receipt["sha256_match"] is True
    assert receipt["structurally_plausible"] is False
    assert receipt["verdict"] == "LOCAL_CHECKPOINT_INCOMPLETE"
    assert module._exit_code(receipt) == 0


def test_sha_mismatch_goes_red(tmp_path: Path) -> None:
    module = _load_inspector()
    checkpoint = tmp_path / "955717e8.safetensors"
    _fake_safetensors(checkpoint)
    receipt = module.inspect_checkpoint(checkpoint, "0" * 64)
    assert receipt["sha256_match"] is False
    assert receipt["verdict"] == "CHECKPOINT_SHA256_MISMATCH"
    assert module._exit_code(receipt) != 0


def test_invalid_offsets_fail_closed_without_tensor_load(tmp_path: Path, monkeypatch) -> None:
    module = _load_inspector()
    checkpoint = tmp_path / "955717e8.safetensors"
    expected_sha = _fake_safetensors(checkpoint, valid=False)
    (tmp_path / "htdemucs.yaml").write_text(
        "models: ['955717e8']\n", encoding="utf-8"
    )
    monkeypatch.setattr(module, "EXPECTED_SIZE", checkpoint.stat().st_size)
    receipt = module.inspect_checkpoint(checkpoint, expected_sha)
    assert receipt["verdict"] == "LOCAL_CHECKPOINT_INCOMPLETE"
    assert receipt["tensor_index"]["offsets_and_shapes_valid"] is False


def test_inspection_never_connects_or_synthesises_config(
    tmp_path: Path, monkeypatch
) -> None:
    module = _load_inspector()
    checkpoint = tmp_path / "955717e8.safetensors"
    expected_sha = _fake_safetensors(checkpoint)
    (tmp_path / "htdemucs.yaml").write_text(
        "models: ['955717e8']\n", encoding="utf-8"
    )
    monkeypatch.setattr(module, "EXPECTED_SIZE", checkpoint.stat().st_size)

    def _deny(*_args, **_kwargs):
        raise AssertionError("J1.5 must not open a network connection")

    monkeypatch.setattr(socket.socket, "connect", _deny)
    monkeypatch.setattr(socket, "create_connection", _deny)
    before = sorted(item.name for item in tmp_path.iterdir())
    receipt = module.inspect_checkpoint(checkpoint, expected_sha)
    after = sorted(item.name for item in tmp_path.iterdir())
    assert receipt["structurally_plausible"] is True
    assert before == after
    assert not (tmp_path / "config.json").exists()


def test_oversized_header_is_rejected_before_json_read(tmp_path: Path) -> None:
    module = _load_inspector()
    checkpoint = tmp_path / "oversized.safetensors"
    checkpoint.write_bytes(struct.pack("<Q", module.MAX_HEADER_BYTES + 1))
    with pytest.raises(module.InspectionError, match="invalid header length"):
        module.read_safetensors_header(checkpoint)
