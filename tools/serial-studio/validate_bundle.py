#!/usr/bin/env python3
"""Fail-closed validator for a closed Serial Studio evidence bundle index."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
CAPTURE_PROFILES = HERE / "profiles/capture-profiles.v1.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate(index_path: Path) -> list[str]:
    errors: list[str] = []
    try:
        index = json.loads(index_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return [f"bundle index cannot be read: {error}"]
    if not isinstance(index, dict):
        return ["bundle index must be a JSON object"]
    schema = index.get("schema")
    if schema not in {"k1.evidence-bundle.v1", "k1.evidence-bundle.v2"}:
        errors.append("schema must be k1.evidence-bundle.v1 or k1.evidence-bundle.v2")
    status = index.get("status")
    if status not in {"VALID", "INVALID", "UNKNOWN", "QUARANTINED"}:
        errors.append("status is invalid")
    reasons = index.get("reasons") or []
    if status == "VALID" and reasons:
        errors.append("VALID bundle must have no rejection reasons")

    root = index_path.resolve().parent
    by_role: dict[str, list[dict[str, Any]]] = {}
    files = index.get("files")
    if not isinstance(files, list) or not files:
        return errors + ["files must be a non-empty array"]
    for position, entry in enumerate(files):
        if not isinstance(entry, dict):
            errors.append(f"files[{position}] is not an object")
            continue
        role = entry.get("role")
        relative = entry.get("path")
        expected_hash = entry.get("sha256")
        expected_bytes = entry.get("bytes")
        if not isinstance(role, str) or not role:
            errors.append(f"files[{position}] has no role")
            continue
        if not isinstance(relative, str) or not relative:
            errors.append(f"files[{position}] has no path")
            continue
        path_value = Path(relative)
        if path_value.is_absolute():
            errors.append(f"{role} path must be relative")
            continue
        unresolved = root / path_value
        if unresolved.is_symlink():
            errors.append(f"{role} file must not be a symlink")
            continue
        resolved = unresolved.resolve()
        if resolved != root and root not in resolved.parents:
            errors.append(f"{role} path escapes the bundle root")
            continue
        if not resolved.is_file():
            errors.append(f"{role} file is missing: {relative}")
            continue
        actual_hash = sha256_file(resolved)
        actual_bytes = resolved.stat().st_size
        if actual_hash != expected_hash:
            errors.append(f"{role} SHA-256 mismatch")
        if actual_bytes != expected_bytes:
            errors.append(f"{role} byte count mismatch")
        by_role.setdefault(role, []).append(entry)

    for role, entries in by_role.items():
        if len(entries) > 1:
            errors.append(f"bundle contains duplicate {role} files")

    def require_bound(role: str, field: str) -> None:
        entries = by_role.get(role) or []
        if len(entries) != 1:
            errors.append(f"bundle requires exactly one {role} file")
            return
        if index.get(field) != entries[0].get("sha256"):
            errors.append(f"{field} does not bind the {role} file")

    if schema == "k1.evidence-bundle.v1":
        require_bound("historian_snapshot", "snapshot_sha256")
        require_bound("instrument_receipt", "instrument_receipt_sha256")
        if status == "VALID":
            if not index.get("scoring_profile_id"):
                errors.append("VALID bundle requires scoring_profile_id")
            if not index.get("scoring_profile_sha256"):
                errors.append("VALID bundle requires scoring_profile_sha256")
        return errors

    profiles_raw = CAPTURE_PROFILES.read_bytes()
    profiles_sha = hashlib.sha256(profiles_raw).hexdigest()
    if index.get("capture_profile_catalogue_sha256") != profiles_sha:
        errors.append("capture_profile_catalogue_sha256 does not bind the profile catalogue")
    profiles_doc = json.loads(profiles_raw)
    profile_id = index.get("capture_profile_id")
    profile = (profiles_doc.get("profiles") or {}).get(profile_id)
    if not isinstance(profile, dict):
        errors.append(f"unknown capture profile: {profile_id}")
        return errors
    if status == "VALID" and str(profile.get("status", "")).startswith("BLOCKED"):
        errors.append(f"capture profile {profile_id} is not admitted: {profile.get('status')}")

    required_roles = set(profile.get("required_bundle_roles") or [])
    optional_roles = set(profile.get("optional_bundle_roles") or [])
    forbidden_roles = set(profile.get("forbidden_bundle_roles") or [])
    allowed_roles = required_roles | optional_roles
    for role in sorted(required_roles):
        if len(by_role.get(role) or []) != 1:
            errors.append(f"profile {profile_id} requires exactly one {role} file")
    for role in sorted(forbidden_roles):
        if by_role.get(role):
            errors.append(f"profile {profile_id} forbids {role}")
    for role in sorted(set(by_role) - allowed_roles - forbidden_roles):
        errors.append(f"profile {profile_id} does not declare file role {role}")

    bindings = index.get("bindings")
    if not isinstance(bindings, dict):
        errors.append("v2 bundle bindings must be an object")
        bindings = {}
    for role, entries in by_role.items():
        if len(entries) == 1 and bindings.get(role) != entries[0].get("sha256"):
            errors.append(f"bindings.{role} does not bind the {role} file")
    for role in bindings:
        if role not in by_role:
            errors.append(f"bindings.{role} has no corresponding file")

    scoring_entries = by_role.get("scoring_profile") or []
    if scoring_entries:
        if not index.get("scoring_profile_id"):
            errors.append("scoring_profile file requires scoring_profile_id")
        if index.get("scoring_profile_sha256") != scoring_entries[0].get("sha256"):
            errors.append("scoring_profile_sha256 does not bind the scoring_profile file")
    elif index.get("scoring_profile_id") or index.get("scoring_profile_sha256"):
        errors.append("scoring profile identity is present without a scoring_profile file")

    audio_receipts = by_role.get("audio_reference_validation") or []
    if audio_receipts:
        receipt_path = root / Path(str(audio_receipts[0]["path"]))
        try:
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            errors.append(f"audio_reference_validation cannot be read: {error}")
        else:
            if receipt.get("schema") != "spectrasynq.audio-reference-validation.v1":
                errors.append("audio_reference_validation schema mismatch")
            if receipt.get("integrity_status") != "VALID":
                errors.append("audio_reference_validation is not VALID")
            if receipt.get("authority") != "HOST_AUDIO_REFERENCE":
                errors.append("audio_reference_validation authority mismatch")
            if receipt.get("time_authority") != "HOST_AUDIO_REFERENCE_TIME":
                errors.append("audio_reference_validation time authority mismatch")
            claims = receipt.get("claims") or {}
            for forbidden_claim in (
                "k1_capture_pipeline_validated",
                "acoustic_delivery_validated",
                "device_time_alignment_validated",
                "product_verdict",
            ):
                if claims.get(forbidden_claim) is not False:
                    errors.append(
                        f"audio_reference_validation must explicitly deny {forbidden_claim}"
                    )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("index", type=Path)
    args = parser.parse_args()
    errors = validate(args.index)
    if errors:
        print("EVIDENCE_BUNDLE=FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("EVIDENCE_BUNDLE=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
