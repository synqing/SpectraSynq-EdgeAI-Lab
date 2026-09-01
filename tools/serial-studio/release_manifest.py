#!/usr/bin/env python3
"""Generate the deterministic source manifest for Serial Studio observability v2."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
SERIAL_STUDIO_REPO = Path("/Users/spectrasynq/Serial-Studio")
DEFAULT_OUTPUT = HERE / "projects/v2.release-manifest.json"
BINARY_IDENTITY = HERE / "projects/serial-studio-binary.v1.json"
TIER_B_RECEIPT = HERE / "projects/tier-b-gpl-policy.v1.json"
LINTER_VERSION = "1.1.0"

WEBVIEW_FILES = [
    "tools/serial-studio/webview/bridge.py",
    "tools/serial-studio/webview/index.html",
    "tools/serial-studio/webview/styles.css",
    "tools/serial-studio/webview/app.js",
]

EDGE_FILES = [
    "src/edgeai/serial_studio.py",
    "src/edgeai/serial_studio_parser.py",
    "tools/serial-studio/generate_project.py",
    "tools/serial-studio/lint_project.py",
    "tools/serial-studio/historian.py",
    "tools/serial-studio/validate_bundle.py",
    "tools/serial-studio/parsers/k1_observe_v1_2.js",
    "tools/serial-studio/parsers/event_raster.js",
    "tools/serial-studio/projects/K1-Dual-UART-Observability-v2.ssproj",
    "tools/serial-studio/projects/v1.manifest.json",
    "tools/serial-studio/projects/v2.workspace-manifest.json",
    "tools/serial-studio/projects/entity-ids.v1.json",
    "tools/serial-studio/projects/tier-b-gpl-policy.v1.json",
    "tools/serial-studio/fixtures/historian/session-19-project-drift.instrument-receipt.json",
    "tools/serial-studio/schemas/telemetry-catalogue.v1.json",
    "tools/serial-studio/schemas/bench-session.schema.json",
    "tools/serial-studio/schemas/evidence-bundle.schema.json",
    "tools/serial-studio/webview/bridge.py",
    "tools/serial-studio/webview/index.html",
    "tools/serial-studio/webview/styles.css",
    "tools/serial-studio/webview/app.js",
    "tools/serial-studio/webview/font-assets.json",
]

POLICY_FILES = [
    "app/src/API/GRPC/GRPCServer.cpp",
    "app/src/API/GRPC/GRPCServer.h",
    "app/src/API/Handlers/BluetoothLEHandler.cpp",
    "app/src/API/Handlers/IOManagerHandler.cpp",
    "app/src/API/Server.cpp",
    "app/src/API/Server.h",
    "app/src/API/Server/ClientReception.cpp",
    "app/src/API/Server/ClientReception.h",
    "app/src/API/Server/ServerAuth.cpp",
    "app/src/DataModel/FrameKeys.h",
    "app/src/DataModel/Project/ProjectLoader.cpp",
    "app/src/DataModel/Project/ProjectPersistence.cpp",
    "app/src/DataModel/ProjectModel.cpp",
    "app/src/DataModel/ProjectModel.h",
    "app/src/DataModel/Scripting/DeviceWriteApi.cpp",
    "app/src/DataModel/Scripting/ScriptDeviceWait.cpp",
    "app/src/IO/ConnectionManager.cpp",
    "app/src/IO/ConnectionManager.h",
    "app/src/IO/ConnectionManager/EgressPolicy.h",
    "app/src/Misc/CLI.cpp",
    "app/src/Misc/CLI.h",
    "app/src/main.cpp",
    "app/tests/CMakeLists.txt",
    "app/tests/tst_observe_only_policy.cpp",
    "app/tests/tst_server_auth.cpp",
    "tests/scripts/test_observe_only_policy.py",
]


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inventory(root: Path, files: list[str]) -> list[dict[str, object]]:
    result = []
    for relative in files:
        path = root / relative
        if not path.is_file():
            raise FileNotFoundError(path)
        result.append(
            {"path": relative, "sha256": sha256_file(path), "bytes": path.stat().st_size}
        )
    return result


def tree_sha(files: list[dict[str, object]]) -> str:
    digest = hashlib.sha256()
    for entry in files:
        digest.update(str(entry["path"]).encode("utf-8") + b"\0")
        digest.update(str(entry["sha256"]).encode("ascii") + b"\n")
    return digest.hexdigest()


def git_value(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=SERIAL_STUDIO_REPO, text=True, capture_output=True, check=True
    ).stdout.strip()


def binary_identity() -> dict[str, object]:
    if not BINARY_IDENTITY.is_file():
        return {
            "status": "OPEN",
            "identity_path": None,
            "binary_path": None,
            "binary_sha256": None,
            "runtime_validated": False,
        }

    identity = json.loads(BINARY_IDENTITY.read_text(encoding="utf-8"))
    binary_path = Path(str(identity["binary_path"]))
    if not binary_path.is_file():
        raise FileNotFoundError(binary_path)
    actual = sha256_file(binary_path)
    if actual != identity.get("binary_sha256"):
        raise ValueError(f"Serial Studio binary drift: {binary_path}")
    return identity


def generate() -> dict[str, object]:
    edge_paths = list(EDGE_FILES)
    if BINARY_IDENTITY.is_file():
        edge_paths.append("tools/serial-studio/projects/serial-studio-binary.v1.json")
    edge_files = inventory(REPO, edge_paths)
    policy_files = inventory(SERIAL_STUDIO_REPO, POLICY_FILES)
    webview_files = inventory(REPO, WEBVIEW_FILES)
    font_manifest = json.loads(
        (HERE / "webview/font-assets.json").read_text(encoding="utf-8")
    )
    serial_studio_binary = binary_identity()
    binary_identified = serial_studio_binary.get("status") == "TIER_A_BINARY_IDENTIFIED"
    runtime_validated = bool(serial_studio_binary.get("runtime_validated"))
    non_claims = [
        "No v2 project was opened against live hardware by this manifest.",
        "Local font files are referenced and verified, not redistributed.",
    ]
    if not binary_identified:
        non_claims.append(
            "The observe-only source patch was not built into an identified application binary by this manifest."
        )
    if not runtime_validated:
        non_claims.append(
            "The GPL binary passed the bounded Tier B policy probe, but full Pro-workspace and installed-binary runtime validation remain open."
        )

    return {
        "schema": "spectrasynq.serial-studio.v2-release-manifest.v1",
        "status": "TIER_A_BINARY_IDENTIFIED" if binary_identified else "HOST_SOURCE_VALIDATED",
        "project": {
            "path": "tools/serial-studio/projects/K1-Dual-UART-Observability-v2.ssproj",
            "sha256": sha256_file(
                HERE / "projects/K1-Dual-UART-Observability-v2.ssproj"
            ),
            "writer_version": "4.0.3",
            "observe_only_required": True,
        },
        "component_identity": {
            "webview_application": {
                "aggregate_sha256": tree_sha(webview_files),
                "files": webview_files,
            },
            "font_assets_manifest_sha256": sha256_file(HERE / "webview/font-assets.json"),
            "parser_sha256": sha256_file(HERE / "parsers/k1_observe_v1_2.js"),
            "semantic_linter": {
                "version": LINTER_VERSION,
                "sha256": sha256_file(HERE / "lint_project.py"),
            },
            "session_19_invalid_fixture_sha256": sha256_file(
                HERE / "fixtures/historian/session-19-project-drift.instrument-receipt.json"
            ),
            "tier_b_host_policy_receipt_sha256": sha256_file(TIER_B_RECEIPT),
            "serial_studio_binary": serial_studio_binary,
        },
        "edgeai_source_tree_sha256": tree_sha(edge_files),
        "edgeai_files": edge_files,
        "serial_studio_policy": {
            "repository": str(SERIAL_STUDIO_REPO),
            "branch": git_value("branch", "--show-current"),
            "source_commit": git_value("rev-parse", "HEAD"),
            "source_tree_sha256": tree_sha(policy_files),
            "files": policy_files,
            "runtime_validated": runtime_validated,
        },
        "local_fonts": {
            "policy": font_manifest["policy"],
            "redistribution_permitted": font_manifest["redistribution_permitted"],
            "assets": [
                {key: asset[key] for key in ("path", "sha256", "family", "style", "weight")}
                for asset in font_manifest["assets"]
            ],
        },
        "non_claims": non_claims,
    }


def serialise(value: dict[str, object]) -> bytes:
    return (json.dumps(value, indent=2) + "\n").encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = serialise(generate())
    if args.check:
        if not args.output.is_file() or args.output.read_bytes() != payload:
            raise SystemExit(f"release manifest drift: {args.output}")
        print(f"SSV2_RELEASE_MANIFEST=PASS SHA256={hashlib.sha256(payload).hexdigest()}")
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(payload)
    print(f"WROTE={args.output} SHA256={hashlib.sha256(payload).hexdigest()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
