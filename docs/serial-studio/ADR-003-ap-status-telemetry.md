# ADR-003 — `[AP]` Status Telemetry Semantics

**Status:** SOURCE CHARACTERISED; RUNNING-BINARY IDENTITY OPEN  
**Date:** 2026-09-01  
**Firmware source inspected:** `36466cd56c90b9cafa571bc5029b5d38bc0543bb`

## Finding

The current `[AP]` line is a low-rate status snapshot, not an event stream.

- `audio/i2s_audio.h:1327-1333` sets the production default publication period
  to 1000 ms and permits a diagnostic compile-time override.
- `audio/i2s_audio.h:1334-1343` reads the current tempo and onset structures at
  publication time and prints those values once. It does not drain an event
  queue or emit accumulated counts.
- `audio/k1_onset_beat.cpp:21-23` documents the internal onset detector at
  133.333 Hz.
- `audio/k1_onset_beat.cpp:372,491-500` keeps onset/bass assertions active for
  an 80 ms window, then clears them.
- `audio/k1_onset_beat.cpp:651-656` confirms the telemetry read is a value-copy
  of the current event structure.

Therefore a fresh 1 Hz `[AP]` observation with `onset=1` means only:

> the status snapshot landed while the onset assertion was active.

It is not a physical event count. A zero does not prove that no onset occurred
since the previous `[AP]` line. Most 80 ms assertions can lawfully begin and end
between 1 s status publications.

## Instrument rules

Historian-derived fields use these names:

```text
onset_high_observations
onset_high_observation_fraction
bass_onset_high_observations
bass_onset_high_observation_fraction
high_observations_per_valid_minute
```

Any per-minute display must say:

```text
HIGH OBSERVATIONS/MIN - NOT EVENT COUNT
```

Mission Control may use `[AP]` for health and coarse state summaries. It must
not use this surface for beat/onset precision, recall, latency, event cadence,
or millisecond AP validation.

## Remaining proof before AP timing work

1. Bind each running K1 binary to a firmware build identity that contains the
   characterised source contract.
2. Define a dedicated high-rate, timestamped, passive event evidence surface.
3. Prove its loss, ordering, freshness and clock semantics independently.
4. Build the reference-to-device clock map before claiming latency.

No cadence runner is involved; the retired cadence silicon path remains closed.
