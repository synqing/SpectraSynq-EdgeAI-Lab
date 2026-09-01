# Product

## Register

product

## Users

The primary operators are Captain and SpectraSynq agents working at the K1 hardware and firmware bench. They use the instrument while diagnosing real-time audio, renderer, transport, runtime-health, calibration, and cross-device behaviour under time pressure. They need to answer a named engineering question in under five seconds, preserve replayable evidence, and distinguish an unhealthy instrument from a product defect.

## Product Purpose

K1 Serial Studio Observability is the common acquisition and operational-awareness layer for applicable SpectraSynq hardware and firmware evaluation workflows. It binds each observation to device identity, parser schema, freshness, record provenance, rig configuration, session identity, and Historian evidence. It supports live awareness, replay, comparison, calibration, and offline evaluation without becoming command authority or verdict authority.

Success means operators can immediately tell whether the instrument is alive, whether both K1s are comparable, which record refreshed each value, whether evidence is durable, and which specialised workspace answers the current question. Stale, ungrounded, mixed-scale, or missing data must fail visibly.

## Brand Personality

Forensic, calm, uncompromising.

The interface should feel like a precise bench instrument: dense where density earns its keep, quiet when the system is healthy, and unmistakable when evidence becomes stale or invalid.

## Anti-references

- Widget catalogues presented as engineering dashboards.
- Generic mission-control theatre, glowing cards, oversized status lamps, and decorative FFTs.
- Mixed units on a shared axis, autoscaled numeric soup, and state lamps used for transient events.
- Workspaces whose titles promise a subsystem while their contents repeat generic telemetry.
- Last-known values presented without source record, update freshness, or age.
- Derived metrics without explicit equations, units, and provenance.
- Hidden device writes, command shuttles, or any route that confuses observability with transport authority.

## Design Principles

1. Every visible instrument answers one named engineering question.
2. Freshness, identity, and evidence health precede product metrics.
3. Comparable signals share explicit units and fixed scales; incompatible signals are separated.
4. Events are shown in time, states are shown as states, and raw evidence stays one step away.
5. Serial Studio observes and records; authoritative commands and offline verdicts retain separate owners.
6. Missing or unhealthy instrumentation is louder than a plausible stale value.
7. The v1 project remains replayable while v2 becomes generated, tested, and source-controlled.
8. Diagnostic sophistication decreases toward Mission Control: the default is simple and actionable; domain, diagnostic, and raw detail appear only on drill-down.

## Accessibility & Inclusion

Target WCAG 2.2 AA. Colour is never the only carrier of health or state; labels, symbols, and numeric age accompany it. The interface supports reduced motion, keyboard navigation, high-contrast text, colour-vision-safe state encoding, and responsive layouts that preserve information hierarchy rather than shrinking type fluidly.
