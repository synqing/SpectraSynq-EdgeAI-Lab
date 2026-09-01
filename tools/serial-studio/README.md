# K1 Serial Studio observability v2

This folder is the generated, hardware-free authority for the v2 Serial Studio instrument.

- `projects/v1.manifest.json` freezes the original live v1 and backup by hash and carries the reviewed two-source identity projection; neither project is overwritten.
- `schemas/telemetry-catalogue.v1.json` defines slots, provenance, semantics, freshness, and safe surfaces.
- `schemas/bench-session.schema.json` joins target, rig, calibration, stimulus, instrument, and evidence identity.
- `parsers/k1_observe_v1_2.js` is the canonical 24-slot parser used by both v2 sources.
- `generate_project.py` generates a separately named, zero-action v2 `.ssproj`.
- `lint_project.py` rejects writes, dangling references, dead slots, mixed-scale plots, and parser drift.
- `webview/` is a localhost-only, read-only, cached Mission Control surface with deterministic fixture mode.
- `historian.py` freezes one explicit session with SQLite backup and emits a fail-closed acquisition receipt.
- `validate_bundle.py` verifies closed bundle files, paths, byte counts, hashes, and receipt/profile bindings.
- `release_manifest.py` binds the project, bridge, evidence tooling, and Serial Studio observe-only source patch.
- `audio_reference_validate.py` strictly compares a Serial Studio Audio CSV with a known WAV without normalisation, DC removal, dither, repair, or dependency installation.
- `capture_audio_source_binding.py` freezes an exact Pro-saved Audio Source C; `generate_audio_profile.py` and `lint_audio_profile.py` generate/lint the separate optional profile without mutating base v2.
- `official_pro_audio_preflight.py` interrogates the official Pro 4.0.3 runtime through a fixed getter-only API allow-list and fails closed on exact BlackHole/rate/format/binding drift. It never configures Audio or touches a DUT.
- `profiles/capture-profiles.v1.json` makes Serial Studio and Audio Reference requirements conditional rather than universal.
- `fixtures/historian/session-19-project-drift.instrument-receipt.json` permanently preserves a real invalid capture where substantial two-source data could not overcome project-identity drift.

## Host validation

```sh
python3 tools/serial-studio/generate_project.py --check
python3 tools/serial-studio/lint_project.py
python3 docs/K1_SERIAL_STUDIO_CANON/guardrails/lint_ssproj.py \
  tools/serial-studio/projects/K1-Dual-UART-Observability-v2.ssproj --profile passive
python3 tools/serial-studio/release_manifest_v2_1.py --check
.venv/bin/python -m pytest -q tests/test_audio_reference_validate.py \
  tests/test_serial_studio_audio_profile.py
.venv/bin/python -m pytest -q
```

V2 generation is hermetic and does not read the mutable live v1 project. Audit
the frozen v1 separately with `generate_project.py --verify-v1 --check`; a
failure reports external v1 drift and does not rewrite either project.

## Mission Control fixture

```sh
python3 tools/serial-studio/webview/bridge.py \
  --fixture tools/serial-studio/fixtures/healthy.json
```

Open `http://127.0.0.1:8765/?view=mission-control`. Fixture mode labels itself as not device evidence. Live mode samples Serial Studio through one fixed read allow-list and a single cache-owning thread; browser requests never call Serial Studio directly.

The elected Countach and Berkeley Mono files are served from their fixed local paths only after SHA-256 verification. Their binaries are never copied into this repository or evidence bundles.

The release manifest identifies the `.ssproj`, aggregate Web View application,
font-assets manifest, parser, semantic linter, observe-only policy source, and
the built Serial Studio binary once Tier A creates its identity receipt.

`projects/tier-b-gpl-policy.v1.json` records an isolated GPL runtime proof of
the local application-level observe-only implementation. It is optional
defence-in-depth evidence, not a prerequisite for the official Pro Source C
path.

## Promotion boundary

The generated v2 project must not replace v1. Source C uses the identified
official Pro 4.0.3 runtime, an external exact-identity preflight, an
observe-only project with no write surfaces, and an independent zero-TX
witness. A custom patched Pro build is optional hardening and is not on the
critical path. Promotion requires exact Source C binding, deterministic Audio
qualification, then passive three-source HIL proving identities, ingress,
Historian progression, zero host-to-DUT bytes, and clean close/snapshot
behaviour.

No command here opens USB, flashes firmware, plays audio, or launches Serial Studio.

## Optional Audio Reference profile

`PASSIVE_DUAL_UART` remains the two-source default. The separately generated
`PASSIVE_DUAL_UART_AUDIO_REF` profile adds Pro Audio source 2 only after an
actual Pro-saved source binding is supplied. No canonical v2.1 `.ssproj` is
written while the loopback device/binding is absent; the profile is
`BLOCKED_UNBOUND` rather than retargeted to the default microphone.

The Audio Reference receipt uses `HOST_AUDIO_REFERENCE_TIME`. It can validate a
host capture against a known file under a named scoring profile. It cannot
validate K1 microphone/PDM/PCM capture, acoustic delivery, device-time
alignment, or a product verdict.
