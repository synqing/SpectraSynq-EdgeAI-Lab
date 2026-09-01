# ADR-002 — Host Audio Reference / Stimulus Witness

**Status:** HOST CONTRACT VALIDATED; live Serial Studio Audio profile
`BLOCKED_UNBOUND`  
**Date:** 2026-09-01  
**Authority:** D24 applicability boundary and D27

## Decision

K1 observability admits a third authority domain:

```text
known stimulus/reference file
        |
        +--> external playback owner --> room --> K1 microphones --> K1 AP
        |
        +--> host reference / loopback capture --> strict offline validator
                                                  |
Bench UART --> Serial Studio Historian ------------+
Main UART  --> Serial Studio Historian ------------+--> later named scorer
```

Sources 0 and 1 remain K1 UART telemetry. Source 2, when admitted, is a Serial
Studio Pro Audio input and is labelled `HOST_AUDIO_REFERENCE_CAPTURE`. It is
never decoded by the K1 parser and never inherits K1 metric or clock authority.

The base project is unchanged. `PASSIVE_DUAL_UART_AUDIO_REF` is a separate
profile/project generated only after `capture_audio_source_binding.py` freezes
an actual Pro-saved Source C projection. The binding must include stable device
name, sample-rate value, format name and channel count. Serial Studio's Audio
`normalization` setting must be explicitly `false` for the first quantitative
profile.

## Authority and non-claims

| Fact | Authority |
| --- | --- |
| Reference WAV bytes and sample indices | reference file SHA-256 |
| Serial Studio CSV samples | closed Audio CSV SHA-256 |
| `Elapsed (s)` | `HOST_AUDIO_REFERENCE_TIME` |
| Source C device/rate/format/channels | hash-bound Pro-saved source binding |
| Bench/Main state and device clocks | K1 telemetry/Historian |
| Reference-to-device time relationship | explicit later clock-map artefact |
| Quantitative result | named scoring profile + validator receipt |
| Product/perceptual verdict | existing named product gate |

The host reference does not validate speaker output, room acoustics, microphone
capture, IM69D130, PDM, K1 PCM, K1 device time, or product behaviour.

## `csv2wav.py` boundary

Serial Studio's example is retained as a human-listenable reconstruction aid.
It may reveal gross corruption, channel order, silence, or rate errors. It is
not quantitative evidence because it may skip malformed rows, replace
non-finite values, rescale float input, remove DC, independently normalise
channels, and dither.

`audio_reference_validate.py` is the quantitative lane. It:

- requires an explicit sample representation;
- rejects every malformed/non-finite row;
- applies only the declared PCM affine decode;
- preserves DC and inter-channel gain;
- reports timing deltas, rate error, gaps, channel metrics, signed correlation,
  mapping, polarity, gain, lag, residual, SNR, drift diagnostic, and optional
  tone distortion metrics;
- emits `NOT_SCORED` unless a named profile and profile hash are present;
- never creates a WAV, repairs data, installs dependencies, opens audio, plays a
  stimulus, accesses USB, or writes to a DUT.

## Serial Studio Audio risks

The Audio callback is drained by a host worker and its timestamps are
synthesised from a steady clock. They are not CoreAudio hardware timestamps.
The implementation may request a nominal device sample-rate change, and a
complete queue-drop witness is not yet proven. These facts block timing and
capture-integrity authority until characterised.

The critical path uses the official licensed Serial Studio Pro 4.0.3 runtime.
`official_pro_audio_preflight.py` queries only the running Pro API's fixed
read-only Audio getter allow-list. It resolves the exact device name before
recording the current index, compares selected rate and format by value, and
requires a hash-bound Pro-saved Source C projection for normalisation and
channel identity. Missing, duplicate, drifted, or unprovable identity fails
closed before Connect.

The stock Pro runtime does not contain the local application-level observe-only
patch. That patch remains useful defence-in-depth and vendor/build hardening,
but it is not a prerequisite for Source C qualification. Runtime evidence must
state the boundary explicitly:

```text
PROJECT POLICY     OBSERVE-ONLY
APP EGRESS GUARD   STOCK PRO / NOT PATCHED
TX WITNESS         ARMED | ZERO BYTES | FAIL
```

Any observed host-to-K1 byte quarantines the session. A project configuration,
healthy API, or open port cannot substitute for the independent TX witness.

## Mission Control and drill-down

Mission Control remains one Web View with zero native datasets. It gains one
subordinate `AUDIO REF` health cell. Without a sourced freshness profile,
samples display `LIVE UNVERIFIED`, never green.

The separately generated audio profile adds two Web View workspaces:

- **Audio Reference** — source identity, mode, freshness, continuity,
  provenance and receipt state;
- **AP Validation** — readiness and receipt-bound result. Device deltas are
  suppressed while the reference/device clock map is absent.

The browser remains a GET-only cache consumer. It owns no capture, playback,
calibration, scoring, command or verdict operation.

## Promotion path

1. Captain installs `BlackHole 2ch` with administrator authority and restarts
   macOS when convenient.
2. Run the getter-only official-Pro preflight and resolve the exact device name,
   current index, 48 kHz rate, Float 32-bit format, and two-channel contract.
3. Save source 2 in that exact official Pro runtime and freeze the binding.
4. Generate/lint the separate v2.1 project; prove base v2 bytes are unchanged.
5. Qualify Source C alone with deterministic signals and the strict validator;
   no K1 is required for this gate.
6. Arm the independent UART TX witness, then run passive three-source HIL. Any
   outbound byte quarantines the session.
7. Characterise sample-rate mutation, host timestamp uncertainty and queue drops.
8. Close CSV/reference/receipt/clock-map artefacts and validate their hashes.
9. Only then change the profile from `BLOCKED_UNBOUND` to an admitted runtime
   state. This does not promote the K1 capture pipeline.

Building a custom patched Pro binary is an optional later hardening lane. It
requires separate commercial/vendor and Qt build authority and does not block
steps 1–9.
