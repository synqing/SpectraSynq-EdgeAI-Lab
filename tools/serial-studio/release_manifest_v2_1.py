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
OFFICIAL_PRO_PREFLIGHT = HERE / "projects/official-pro-audio-preflight.v1.json"
OPTICAL_MEASUREMENT = REPO / "_scratch/serial_studio_v2_1_20260901/MEASURED.json"

EDGE_FILES = [
    "tools/serial-studio/audio_reference_validate.py",
    "tools/serial-studio/official_pro_audio_preflight.py",
    "tools/serial-studio/capture_audio_source_binding.py",
    "tools/serial-studio/capture_diagnostics.py",
    "tools/serial-studio/generate_audio_profile.py",
    "tools/serial-studio/lint_audio_profile.py",
    "tools/serial-studio/release_manifest_v2_1.py",
    "tools/serial-studio/projects/official-pro-audio-preflight.v1.json",
    "tools/serial-studio/validate_bundle.py",
    "tools/serial-studio/zero_tx_witness.py",
    "tools/serial-studio/profiles/capture-profiles.v1.json",
    "tools/serial-studio/schemas/audio-reference-validation.schema.json",
    "tools/serial-studio/schemas/audio-reference-scoring-profile.schema.json",
    "tools/serial-studio/schemas/audio-source-binding.schema.json",
    "tools/serial-studio/schemas/official-pro-audio-preflight.schema.json",
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
    "tests/test_serial_studio_official_pro_preflight.py",
    "tests/test_serial_studio_audio_profile.py",
    "tests/test_serial_studio_bundle.py",
    "tests/test_serial_studio_capture_diagnostics.py",
    "tests/test_serial_studio_webview.py",
    "tests/test_serial_studio_zero_tx_witness.py",
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
    official_pro = json.loads(OFFICIAL_PRO_PREFLIGHT.read_text(encoding="utf-8"))
    optical = json.loads(OPTICAL_MEASUREMENT.read_text(encoding="utf-8"))
    dirty = git_value("status", "--porcelain", "--", *AUDIO_POLICY_FILES)
    return {
        "schema": "spectrasynq.serial-studio.v2.1-release-manifest.v1",
        "status": "HOST_CONTRACT_VALIDATED_OFFICIAL_PRO_IDENTITY_PASS_AUDIO_BINDING_BLOCKED",
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
        "optional_patched_pro_hardening": {
            "repository": str(SERIAL_STUDIO_REPO),
            "branch": git_value("branch", "--show-current"),
            "base_commit": git_value("rev-parse", "HEAD"),
            "working_tree_state": "PATCHED_UNCOMMITTED" if dirty else "COMMITTED",
            "working_tree_status": dirty.splitlines(),
            "source_tree_sha256": tree_sha(audio_policy_files),
            "files": audio_policy_files,
            "source_guard": "AUDIO_SAVED_BINDING_POLICY=PASS",
            "critical_path": False,
            "identified_official_pro_binary_contains_patch": False,
        },
        "official_pro_runtime": {
            "receipt_path": "tools/serial-studio/projects/official-pro-audio-preflight.v1.json",
            "receipt_sha256": sha256_file(OFFICIAL_PRO_PREFLIGHT),
            "runtime_identity": official_pro["runtime_identity"],
            "application_policy": official_pro["application_policy"],
            "audio_binding_preflight": official_pro["audio_binding_preflight"],
            "overall_status": official_pro["overall_status"],
        },
        "optical_validation": {
            "measurement_path": "_scratch/serial_studio_v2_1_20260901/MEASURED.json",
            "measurement_sha256": sha256_file(OPTICAL_MEASUREMENT),
            "tier": optical["tier"],
            "verdict": optical["verdict"],
            "stills": optical["stills"],
            "fonts_verified": optical["fonts_verified"],
            "p0_inversions": optical["p0_inversions"],
        },
        "optional_prior_gpl_policy_proof": {
            "critical_path": False,
            **binary_identity(),
        },
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
                "official_pro_runtime_identity_validated": True,
                "audio_binding_validated": False,
                "app_egress_guard": "STOCK_PRO_NOT_PATCHED",
                "independent_tx_witness": "REQUIRED_PENDING",
            },
        },
        "non_claims": [
            "No Audio Source C project was generated without an exact Pro-saved binding.",
            "No loopback input is admitted or claimed present by this manifest.",
            "The official Pro runtime identity and read-only Audio API surface are validated; Source C is not yet bound.",
            "The fail-closed application patch is optional hardening and is not in the official Pro binary.",
            "No audio playback, USB, firmware, live capture or HIL was performed.",
            "Host Audio Reference does not validate acoustic delivery or the K1 microphone/PDM/PCM path.",
            "The optical receipt validates layout and typography, not device, Audio, or product behaviour."
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
