---
name: k1-serial-studio-instrument
version: 1.0.0
status: canonical
target: Serial Studio Pro v4.0.3
---

# K1 Serial Studio Instrument Skill

## Trigger

Use this skill before any work involving:
- Serial Studio;
- `.ssproj`;
- K1 UART observability;
- K1 Historian/session DB;
- Serial Studio Painter/Web View;
- Serial Studio plugins/extensions;
- K1 telemetry parsing/transforms;
- K1 observability dashboards.

## Prime directive

Serial Studio is an instrument, not K1 command transport authority.

A silicon task requiring command/reply owns the target CDC exclusively through the intended test harness. Serial Studio releases that port.

## Preflight

1. Identify target project version.
2. If project is v1/historical, do not mutate it.
3. Read `DOCTRINE.md`.
4. Run `.ssproj` linter.
5. Identify whether task is:
   - OFFLINE_PROJECT_DEV;
   - PASSIVE_OBSERVE;
   - ACTIVE_POLLING;
   - AUTHORITATIVE_COMMAND_TEST.
6. Confirm one live writer.
7. Confirm no other process owns the target CDC when connection is required.

## OFFLINE_PROJECT_DEV

Allowed:
- copy project;
- edit JSON/project;
- write parser;
- write Painter;
- write read-only plugin;
- run linter;
- run parser dryRun;
- replay/simulate.

Forbidden:
- treating a dashboard screenshot as proof;
- changing live DUT state.

Exit criteria:
- linter PASS;
- golden parser tests PASS;
- no forbidden command authority;
- workspace semantic review PASS.

## PASSIVE_OBSERVE

Required:
- no automatic device writes;
- no control-script write calls;
- no output controls;
- no command-shuttle table;
- no autoReconnect;
- Serial Studio is the sole owner of each port it opens;
- recording state known.

Immediately verify:
- raw RX age;
- raw bytes/s;
- parser progression;
- Historian raw-byte delta.

If a source is open but raw RX remains zero:
- classify `OPEN_NO_RX`;
- do not pretend it is connected/healthy;
- do not test higher layers.

## ACTIVE_POLLING

Must be explicitly requested/selected.

Only allowlisted low-rate health commands.

Receipt must say observer is active.

Never use this profile when an authoritative silicon harness needs the port.

## AUTHORITATIVE_COMMAND_TEST

Serial Studio does not own the target port.

Use exclusive pyserial/test harness.

Do not route through TCP 7777, Control Script, Painter, plugin or shared-memory shuttle.

## Dashboard design rules

Before adding a widget, write:
- question;
- metric(s);
- units;
- range;
- freshness;
- why this widget;
- evidence status.

Reject the widget if any answer is missing.

MultiPlot:
- compatible signals only.

Event:
- raster/timeline, not giant persistent lamp.

State/fault:
- annunciator/alarm.

FFT:
- explicit cadence/hypothesis required.

Renderer:
- only if renderer telemetry exists.

## Transform rules

Virtual dataset:
- `value` is not sibling data;
- use dataset/table accessors;
- declare dependencies.

Host timing:
- diagnostic only.

Device timing:
- authority when device emits it.

## Historian rules

Live DB hash = fingerprint only.

Final evidence = frozen consistent snapshot SHA256 + receipt.

Held values are not samples.

## Plugin rules

K1 observability plugins are read-only.

Allowed:
- StreamFrames;
- StreamRawData;
- read API status;
- local analysis.

Forbidden:
- WriteRawData;
- DUT writes;
- source reconnect;
- configuration mutation during recording.

## Failure protocol

One live proof attempt per authorization.

On fail:
1. capture exact evidence;
2. classify layer;
3. stop;
4. return non-claims;
5. do not invent a workaround.

## Mandatory final report

```text
MODE:
PROJECT:
PROJECT_SHA:
SERIAL_STUDIO_VERSION:
PORT OWNERSHIP:
LIVE WRITER:
RX HEALTH:
HISTORIAN:
LINTER:
TESTS:
CHANGES:
EVIDENCE:
NON-CLAIMS:
NEXT:
```
