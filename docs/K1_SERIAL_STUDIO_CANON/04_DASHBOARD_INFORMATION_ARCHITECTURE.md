# K1 Serial Studio — Dashboard Information Architecture Canon

## Rule zero

A dashboard is a compressed decision surface.

Every tile must answer a question faster than reading raw logs.

## Information-depth gradient

**Diagnostic sophistication must decrease toward the default workspace.**

The permanent hierarchy is:

```text
MISSION CONTROL
simple, high-confidence, immediately actionable

  -> DOMAIN WORKSPACES
     detailed, question-specific instruments

       -> DIAGNOSTICS
          specialised or experimental analysis

            -> RAW / FORENSICS
               complete provenance and wire-level detail
```

Mission Control should look almost boring when healthy. Failures must scream;
specialised instruments must wait behind an intentional drill-down. Feature
utilisation means using the right Serial Studio capability in the workspace
where it answers a real question, not keeping every capability visible.

## Canonical workspaces

### 1. Mission Control

Composition: one dominant, responsive, read-only K1 Web View. A compact event
raster may be added only if it remains subordinate and improves the under-five-
second comparison. Native FFT, 3D, generic MultiPlot, and LED-panel widgets are
forbidden here.

Questions:
- Are both K1s alive?
- Is telemetry fresh?
- Is Historian recording?
- Are the two devices broadly behaving?

Show:
- Bench/Main RX state;
- last RX age;
- parsed frame rate;
- raw bytes/s;
- BPM;
- lock state;
- confidence;
- normalized peak/energy/novelty when their ranges are proven;
- system FPS;
- LED FPS;
- current Historian session;
- running read-only plugin state if any;
- cross-device deltas.

Do not show:
- raw device clocks;
- bit masks;
- giant FFTs;
- raw counters;
- five huge event bulbs.

### 2. Rhythm & Events

Questions:
- Is tempo stable?
- Are events occurring at expected times?
- Do Main/Bench detect similar events?

Use:
- BPM time plot(s), fixed sensible range once proven;
- confidence plot 0..1;
- persistent Lock/Silence state strip;
- Painter event raster for Beat/Onset/Bass;
- optional triggered/sweep view for event-aligned analysis only when justified.

### 3. Audio Dynamics

Questions:
- What is AP responding to?
- Are Main/Bench dynamics comparable?

Use separate normalized MultiPlots only for metrics with compatible range, e.g.:
- Peak;
- Energy;
- Novelty;
- possibly AGC after its semantic/range contract is documented.

Fixed 0..1 axes only if firmware semantics prove 0..1.

Unknown-range metrics remain out until documented.

### 4. Timing & Transport

Questions:
- Is acquisition temporally healthy?
- Is the host receiving regularly?
- Is buffering/jitter occurring?

Show:
- last RX age;
- host inter-arrival;
- parser frame rate;
- device-time delta, not raw monotonically increasing device clock;
- event TID continuity;
- transport residual labeled HOST DIAGNOSTIC;
- device sequence continuity when future firmware emits it.

### 5. System Health

Questions:
- Are runtime rates within known contracts?
- Is observer/instrument healthy?

Use:
- Sys FPS;
- LED FPS;
- raw throughput;
- Historian activity;
- source staleness;
- alarm bands where thresholds are evidence-backed.

### 6. Raw / Forensics

Use Data Grid(s) and terminal/raw stream for:
- record kind;
- update mask;
- device clock;
- parser sequence;
- event TID;
- exact dataset values;
- raw textual traffic.

### 7. Spectral Lab (diagnostic, optional)

All FFT/Waterfall work lives here.

Each FFT title must state what spectrum it actually is, e.g.:

> Peak Envelope Modulation Spectrum — NOT AUDIO FFT

Document:
- input metric;
- fresh cadence;
- FFT rate;
- window samples;
- window seconds;
- bin resolution;
- diagnostic hypothesis.

## Widget selection law

### MultiPlot
Use only for semantically comparable signals.

### Plot
Use for one trend or explicit custom X/Y relationship.

### LED Panel
Use for persistent state/fault/limit annunciation.

Do not use large LEDs for transient events.

### Painter
Use for:
- event rasters;
- compact K1-specific summaries;
- topology mimic;
- freshness/staleness strip.

Painter is not evidence.

### Bar/Gauge/Meter
Use for bounded values with proven min/max and meaningful thresholds.

### FFT/Waterfall
Diagnostic only unless a specific analysis contract elevates it.

### 3D
Forbidden by default. Requires a real 3D data question and three meaningful dimensions.

### Web View
Allowed for high-information custom cockpit views. The web view must expose freshness and instrument health, not merely attractive last-known values.
