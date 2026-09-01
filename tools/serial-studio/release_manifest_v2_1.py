#!/usr/bin/env python3
"""Generate the deterministic host identity for Audio Reference v2.1."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
SERIAL_STUDIO_REPO = Path("/Users/spectrasynq/Serial-Studio")
DEFAULT_OUTPUT = HERE / "projects/v2.1.release-manifest.json"
BINARY_IDENTITY = HERE / "projects/serial-studio-binary.v1.json"
AR0_RUNTIME_RECEIPT = HERE / "projects/ar0-runtime-promotion.v1.json"

EDGE_FILES = [
    "tools/serial-studio/audio_reference_validate.py",
    "tools/serial-studio/capture_audio_source_binding.py",
    "tools/serial-studio/generate_audio_profile.py",
    "tools/serial-studio/lint_audio_profile.py",
    "tools/serial-studio/release_manifest_v2_1.py",
    "tools/serial-studio/projects/ar0-runtime-promotion.v1.json",
    "tools/serial-studio/validate_bundle.py",
    "tools/serial-studio/profiles/capture-profiles.v1.json",
    "tools/serial-studio/schemas/audio-reference-validation.schema.json",
    "tools/serial-studio/schemas/audio-reference-scoring-profile.schema.json",
    "tools/serial-studio/schemas/audio-source-binding.schema.json",
    "tools/serial-studio/schemas/bench-session.v2.schema.json",
    "tools/serial-studio/schemas/evidence-bundle.v2.schema.json",
    "tools/serial-studio/webview/bridge.py",
    "tools/serial-studio/webview/index.html",
    "tools/serial-studio/webview/styles.css",
    "tools/serial-studio/webview/app.js",
    "tools/serial-studio/webview/font-assets.json",
    "tools/serial-studio/fixtures/audio-reference-live-unverified.json",
    "tools/serial-studio/fixtures/audio-reference-receipt-pass.json",
    "tests/test_audio_reference_validate.py",
    "tests/test_serial_studio_audio_profile.py",
    "tests/test_serial_studio_bundle.py",
    "tests/test_serial_studio_webview.py",
    "docs/serial-studio/ADR-002-host-audio-reference.md",
]

WEBVIEW_FILES = [
    "tools/serial-studio/webview/bridge.py",
    "tools/serial-studio/webview/index.html",
    "tools/serial-studio/webview/styles.css",
    "tools/serial-studio/webview/app.js",
]

AUDIO_POLICY_FILES = [
    "app/src/IO/Drivers/Audio.cpp",
    "app/src/IO/Drivers/Audio/AudioDeviceCatalog.cpp",
    "tests/scripts/test_audio_saved_binding_policy.py",
]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def inventory(root: Path, files: list[str]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for relative in files:
        path = root / relative
        if not path.is_file():
            raise FileNotFoundError(path)
        output.append(
            {"path": relative, "sha256": sha256_file(path), "bytes": path.stat().st_size}
        )
    return output


def tree_sha(files: list[dict[str, Any]]) -> str:
    digest = hashlib.sha256()
    for item in files:
        digest.update(str(item["path"]).encode() + b"\0")
        digest.update(str(item["sha256"]).encode() + b"\n")
    return digest.hexdigest()


def git_value(*args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=SERIAL_STUDIO_REPO,
        text=True,
        capture_output=True,
        check=True,
    ).stdout.strip()


def binary_identity() -> dict[str, Any]:
    identity = json.loads(BINARY_IDENTITY.read_text(encoding="utf-8"))
    binary_path = Path(str(identity["binary_path"]))
    if not binary_path.is_file():
        raise FileNotFoundError(binary_path)
    if sha256_file(binary_path) != identity.get("binary_sha256"):
        raise ValueError("identified GPL binary drift")
    return identity


def generate() -> dict[str, Any]:
    edge_files = inventory(REPO, EDGE_FILES)
    webview_files = inventory(REPO, WEBVIEW_FILES)
    audio_policy_files = inventory(SERIAL_STUDIO_REPO, AUDIO_POLICY_FILES)
    profile_catalogue = HERE / "profiles/capture-profiles.v1.json"
    profile = json.loads(profile_catalogue.read_text(encoding="utf-8"))["profiles"]
    fonts = json.loads((HERE / "webview/font-assets.json").read_text(encoding="utf-8"))
    ar0_runtime = json.loads(AR0_RUNTIME_RECEIPT.read_text(encoding="utf-8"))
    dirty = git_value("status", "--porcelain", "--", *AUDIO_POLICY_FILES)
    return {
        "schema": "spectrasynq.serial-studio.v2.1-release-manifest.v1",
        "status": "HOST_CONTRACT_VALIDATED_AUDIO_RUNTIME_BLOCKED",
        "base_project": {
            "path": "tools/serial-studio/projects/K1-Dual-UART-Observability-v2.ssproj",
            "sha256": sha256_file(
                HERE / "projects/K1-Dual-UART-Observability-v2.ssproj"
            ),
            "changed_by_v2_1": False,
        },
        "profiles": {
            "catalogue_path": "tools/serial-studio/profiles/capture-profiles.v1.json",
            "catalogue_sha256": sha256_file(profile_catalogue),
            "passive_dual_uart": profile["PASSIVE_DUAL_UART"],
            "passive_dual_uart_audio_ref": profile["PASSIVE_DUAL_UART_AUDIO_REF"],
        },
        "audio_project": {
            "status": "BLOCKED_UNBOUND",
            "path": None,
            "sha256": None,
            "reason_codes": profile["PASSIVE_DUAL_UART_AUDIO_REF"]["blockers"],
        },
        "host_components": {
            "aggregate_sha256": tree_sha(edge_files),
            "files": edge_files,
            "webview_aggregate_sha256": tree_sha(webview_files),
        },
        "application_audio_binding_policy": {
            "repository": str(SERIAL_STUDIO_REPO),
            "branch": git_value("branch", "--show-current"),
            "base_commit": git_value("rev-parse", "HEAD"),
            "working_tree_state": "PATCHED_UNCOMMITTED" if dirty else "COMMITTED",
            "working_tree_status": dirty.splitlines(),
            "source_tree_sha256": tree_sha(audio_policy_files),
            "files": audio_policy_files,
            "source_guard": "AUDIO_SAVED_BINDING_POLICY=PASS",
            "identified_pro_binary_contains_patch": False,
        },
        "runtime_promotion": {
            "receipt_path": "tools/serial-studio/projects/ar0-runtime-promotion.v1.json",
            "receipt_sha256": sha256_file(AR0_RUNTIME_RECEIPT),
            "gate": ar0_runtime["gate"],
            "status": ar0_runtime["status"],
            "reason_codes": ar0_runtime["reason_codes"],
        },
        "prior_gpl_binary": binary_identity(),
        "local_fonts": {
            "policy": fonts["policy"],
            "redistribution_permitted": fonts["redistribution_permitted"],
            "manifest_sha256": sha256_file(HERE / "webview/font-assets.json"),
        },
        "capabilities": {
            "host_audio_reference": {
                "status": "HOST_CONTRACT_VALIDATED",
                "optional": True,
                "authority": "HOST_AUDIO_REFERENCE",
                "time_authority": "HOST_AUDIO_REFERENCE_TIME",
                "serial_studio_required": False,
                "dut_egress": False,
            },
            "serial_studio_audio_source_c": {
                "status": "BLOCKED_UNBOUND",
                "optional": True,
                "requires_pro": True,
                "runtime_validated": False,
            },
        },
        "non_claims": [
            "No Audio Source C project was generated without an exact Pro-saved binding.",
            "No loopback input is admitted or claimed present by this manifest.",
            "The fail-closed Audio identity patch is not in an identified Pro binary.",
            "No audio playback, USB, firmware, live capture or HIL was performed.",
            "Host Audio Reference does not validate acoustic delivery or the K1 microphone/PDM/PCM path.",
            "The prior optical receipt does not formally validate the changed six-cell Mission Control geometry."
        ],
    }


def serialise(value: dict[str, Any]) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = serialise(generate())
    if args.check:
        if not args.output.is_file() or args.output.read_bytes() != payload:
            raise SystemExit(f"v2.1 release manifest drift: {args.output}")
        print(f"SSV2_1_RELEASE_MANIFEST=PASS SHA256={hashlib.sha256(payload).hexdigest()}")
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(payload)
    print(f"WROTE={args.output} SHA256={hashlib.sha256(payload).hexdigest()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
