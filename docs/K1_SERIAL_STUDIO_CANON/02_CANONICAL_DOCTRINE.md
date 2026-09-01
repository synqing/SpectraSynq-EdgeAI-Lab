# K1 Serial Studio — Canonical Doctrine

This document is intended to be referenced by `AGENTS.md`, execution briefs, tests and project linting.

## D-SS-001 — Instrument, not transport authority

Serial Studio is for:
- observe;
- record;
- visualize;
- Historian;
- replay;
- read-only external analytics.

Serial Studio is not the command/reply transport authority for authoritative K1 silicon tests.

## D-SS-002 — Exclusive CDC ownership

A silicon test requiring interactive command/reply owns the target K1 serial port exclusively.

Serial Studio must release it first.

No two owners on one USB-CDC.

## D-SS-003 — Passive by default

Canonical observability profile:
- no automatic TX on connect;
- no hidden polling;
- no device writes from Control Script;
- no device writes from Painter;
- no device writes from plugins;
- no output controls that can mutate the DUT;
- auto-reconnect off.

Active polling, when explicitly useful, is a separate named profile and must be tagged as observer-active.

## D-SS-004 — One live writer

Exactly one agent/process owns mutations to the live Serial Studio application/project/API at a time.

Parallel lanes may:
- inspect docs;
- analyze project JSON offline;
- write separate reports;
- test pure functions.

Parallel lanes may not concurrently mutate one live Serial Studio instance.

## D-SS-005 — No live instrument surgery during evidence capture

Once an authoritative recording starts:
- no parser edits;
- no project edits;
- no workspace edits;
- no control-script edits;
- no extension installs/updates;
- no source reconnect/reconfigure;
- no plugin version changes.

If configuration must change, end the session and start a new one.

## D-SS-006 — Evidence hierarchy

```text
device time/counters > raw bytes > frozen Historian > structured parser values
> host arrival diagnostics > visual widgets > screenshots
```

Offline Python owns formal verdicts.

## D-SS-007 — Freshness is first-class

Every metric must declare:
- which record kinds can update it;
- whether the current value is fresh or held;
- its last-update age;
- its update cadence if known.

Held values must never inflate statistical sample counts.

## D-SS-008 — Host sequence is not device sequence

`host_parse_seq` proves parser progression only.

It does not prove:
- the device emitted every logical frame;
- the USB transport delivered every frame;
- pre-parser loss did not occur.

A true device frame counter must come from the device.

## D-SS-009 — Host time is not cross-device timing authority

Serial Studio host timestamps are useful for:
- transport jitter;
- buffering;
- host scheduling diagnostics.

They are not sub-ms synchronization authority between K1s.

## D-SS-010 — Host write accepted is not device delivery

Any receipt must distinguish:
1. write accepted/queued by host;
2. bytes observed returning from device;
3. expected device response/acknowledgement observed.

## D-SS-011 — Connected is not healthy

A source is healthy only when its receive path is producing expected traffic.

Dashboard must expose:
- last RX age;
- raw bytes/s;
- parsed frames/s;
- source freshness;
- Historian activity.

## D-SS-012 — Project v1 is historical

Do not destructively "fix" the project used by historical sessions.

Preserve v1. Create v2.

## D-SS-013 — No widget without a question

Every workspace/widget must have:
- operator question;
- data dependencies;
- units/ranges;
- freshness semantics;
- evidence status;
- reason that widget type is appropriate.

If these cannot be stated, the widget is removed.

## D-SS-014 — MultiPlot compatibility

Signals sharing one MultiPlot must share:
- comparable scale;
- compatible units or explicit normalization;
- a common operator question.

BPM must not share an axis with 0/1 Boolean events and normalized AP metrics.

## D-SS-015 — Events are not states

Persistent state -> annunciator/LED/state strip.

Transient event -> timeline/raster/stem/triggered view.

## D-SS-016 — FFT requires declared cadence

FFT/Waterfall is forbidden unless:
- metric has a known fresh sample cadence;
- `fftSamplingRate` matches that cadence;
- diagnostic hypothesis is documented;
- window size/window duration/resolution are documented.

Sparse mixed-cadence last-known values do not qualify.

## D-SS-017 — Virtual transforms declare dependencies

Virtual datasets must use documented accessors such as:
- `datasetGetRaw`;
- `datasetGetFinal`;
- `tableGet`;
- `tableGetH`.

A virtual transform may not assume its `value` argument contains a sibling metric.

## D-SS-018 — No dead slots

No `unused_slot_*` datasets in the canonical project.

No widgets, FFTs or waterfalls attached to dead fields.

## D-SS-019 — No fake workspace shells

Different workspace names must not point to identical widget-reference sets unless explicitly justified.

A "Renderer" workspace requires actual renderer telemetry.

## D-SS-020 — Plugin authority is read-only

K1 observability plugins may:
- read frames;
- read raw data;
- calculate advisory statistics;
- save local state;
- display external analysis.

They may not:
- write raw data;
- issue DUT commands;
- reconnect sources;
- modify project configuration during a run.

## D-SS-021 — Extension versions are part of instrument identity

Receipts must include the running extension/plugin set and version/fingerprint when extensions influence the run.

## D-SS-022 — Active polling is explicit

If Serial Studio sends periodic health requests:
- operator enables a named active-polling profile;
- poll commands are allowlisted;
- rate is justified;
- receipt records active polling;
- duplicate metrics are not treated as independent samples.

## D-SS-023 — One proof obligation per live attempt

A live hardware proof has one question.

If it fails:
- capture evidence;
- classify;
- stop.

Do not improvise five alternative implementations in the same live session.

## D-SS-024 — Support work cannot block the research programme unless explicitly load-bearing

Optional Serial Studio recovery, plugin development or dashboard polish must not block active product/research gates unless a documented dependency says otherwise.
