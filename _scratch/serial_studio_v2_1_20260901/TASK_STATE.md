# Serial Studio Audio Reference v2.1 task state

## Objective

Add a first-class but optional host Audio Reference / Stimulus Witness lane that
can be aligned offline with Bench and Main K1 telemetry.  It must remain a host
reference, never evidence that the K1 microphone/PDM/PCM capture path is
bit-perfect.

## Frozen boundaries

- Preserve `K1-Dual-UART-Observability-v2.ssproj` byte-for-byte.
- Preserve Mission Control as exactly one Web View with zero native datasets.
- Preserve sources 0 and 1, parser v1.2, telemetry catalogue v1 and Historian.
- Source C is optional and must not become a prerequisite for unrelated work.
- Serial Studio remains observe/record only and never owns playback or DUT TX.
- `HOST_AUDIO_REFERENCE_TIME` is not K1 device time.
- No dependency bootstrap, network install, GUI, playback, USB or firmware work.
- Cadence remains closed and its retired runner is not touched.

## Implementation decision

Ship two separately governed host-reference inputs:

1. `STIMULUS_FILE`: exact, sample-indexed reference file.  This is immediately
   reproducible and independent of Serial Studio.
2. `SERIAL_STUDIO_AUDIO_CAPTURE`: optional Source C capture.  This is admitted
   only by an exact, hash-bound Pro Audio source binding.  Missing or mismatched
   device identity is a hard failure; fallback to a default microphone is
   forbidden.

The quantitative validator consumes strict Serial Studio Audio CSV plus a known
reference WAV.  It performs no DC removal, normalisation, dither, clipping,
repair, row skipping or format inference.

## Required outputs

- `tools/serial-studio/audio_reference_validate.py`
- `tools/serial-studio/schemas/audio-reference-validation.schema.json`
- deterministic tests and hostile mutants
- versioned optional profile catalogue and Source C binding contract
- Web View Audio Reference state with explicit freshness/provenance/non-claims
- D24 addendum / ADR and v2.1 release identity
- a fail-closed Serial Studio Audio saved-binding source patch and tests where
  the local source tree permits it

## Red-team risks

- Upstream `csv2wav.py` silently skips malformed rows, zeroes NaN/Inf, rescales
  float input, removes DC, normalises channels and can dither.
- Serial Studio Audio timestamps are host-synthesised, not CoreAudio hardware
  timestamps or K1 clock authority.
- Audio callback queue overflow is not currently a complete drop witness.
- The Audio driver may change nominal CoreAudio sample rate.
- A missing saved device can currently leave a default input selected.
- No BlackHole input is installed on this host at task start.
- No installed Pro binary containing any new fail-closed patch is available.

## Proof boundary

Host code/tests may earn `HOST_CONTRACT_VALIDATED`.  They cannot earn live
Source C capture, Pro runtime, acoustic presentation, K1 PCM, HIL or product
validation.  Those remain explicit later gates.
