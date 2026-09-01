"""J2 local loader refuses Titan/no-GO/bad SHA before importing Demucs."""

from __future__ import annotations

import ast
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/demucs_local_probe.py"
LOADER = ROOT / "src/edgeai/mir/demucs_local_loader.py"


def _run(args: list[str], env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )


def test_loader_source_never_constructs_separator_or_uses_repo_none() -> None:
    source = SCRIPT.read_text(encoding="utf-8") + LOADER.read_text(encoding="utf-8")
    assert "Separator(" not in source
    assert "repo=None" not in source
    assert "hf_hub_download" not in source
    assert "snapshot_download" not in source
    tree = ast.parse(LOADER.read_text(encoding="utf-8"))
    imports = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]
    demucs_import_lines = [node.lineno for node in imports if "demucs" in ast.unparse(node)]
    with_lines = [
        node.lineno
        for node in ast.walk(tree)
        if isinstance(node, ast.With) and "demucs_network_forbidden" in ast.unparse(node)
    ]
    assert demucs_import_lines and with_lines
    # The package import is nested inside the guard's with-body.
    assert max(demucs_import_lines) > min(with_lines)


def test_no_named_go_refuses_before_demucs_import(tmp_path: Path) -> None:
    env = os.environ.copy()
    env.pop("SPECTRASYNQ_DEMUCS_NAMED_GO", None)
    env.pop("SPECTRASYNQ_TITAN", None)
    receipt = tmp_path / "receipt.json"
    proc = _run(["--receipt", str(receipt)], env)
    assert proc.returncode == 3
    assert "DEMUCS_NAMED_GO_REQUIRED" in proc.stdout
    assert "ModuleNotFoundError" not in proc.stderr


def test_titan_refuses_even_with_named_go(tmp_path: Path) -> None:
    env = os.environ.copy()
    env["SPECTRASYNQ_DEMUCS_NAMED_GO"] = "D26_HOST_BLITZ_2026-09-01"
    env["SPECTRASYNQ_TITAN"] = "1"
    receipt = tmp_path / "receipt.json"
    proc = _run(["--receipt", str(receipt)], env)
    assert proc.returncode == 3
    assert "DEMUCS_TITAN_REFUSED" in proc.stdout


def test_bad_sha_refuses_before_demucs_import(tmp_path: Path) -> None:
    checkpoint = tmp_path / "955717e8.safetensors"
    checkpoint.write_bytes(b"not the pinned checkpoint")
    env = os.environ.copy()
    env["SPECTRASYNQ_DEMUCS_NAMED_GO"] = "D26_HOST_BLITZ_2026-09-01"
    env.pop("SPECTRASYNQ_TITAN", None)
    receipt = tmp_path / "receipt.json"
    proc = _run(
        ["--checkpoint", str(checkpoint), "--receipt", str(receipt)], env
    )
    assert proc.returncode == 4
    assert "CHECKPOINT_SHA256_MISMATCH" in proc.stdout
