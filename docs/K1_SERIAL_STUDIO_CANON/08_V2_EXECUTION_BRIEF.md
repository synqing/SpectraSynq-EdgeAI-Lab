# SpectraSynq K1 — Serial Studio Pro Observability Instrument
## Comprehensive Re-Architecture & Execution Brief

**Document status:** EXECUTION BRIEF / IMPLEMENTATION AUTHORITY PROPOSAL  
**Serial Studio target:** Pro **v4.0.3**  
**Project under review:** `K1 Dual UART Observability.ssproj`  
**Primary objective:** transform the existing Serial Studio project from a feature-demo collage into a coherent, high-information, low-noise laboratory observability instrument for the two K1 devices.  
**Secondary objective:** preserve the parts that are already valuable — dual-source acquisition, parser provenance, Historian/SQLite, raw bytes, freshness semantics, offline Python scoring — while eliminating every surface or behavior that creates ambiguity, false precision, needless control authority, or visual clutter.

---

# 0. EXECUTIVE ORDER

This project is **not** a showcase of how many Serial Studio widgets can be enabled.

It is an engineering instrument.

Every displayed element must answer at least one of these questions in under five seconds:

1. **Are both K1s alive and producing fresh telemetry?**
2. **What is each K1 currently hearing / detecting / tracking?**
3. **Are the two K1s behaving similarly or materially differently?**
4. **Is the timing / transport / rendering pipeline healthy?**
5. **Did an event actually occur, and when?**
6. **Is a metric fresh, stale, held, missing, or malformed?**
7. **What raw evidence will let us prove or disprove what the dashboard suggests?**

If a widget cannot answer one of those questions, it does not belong on the operational dashboard.

The dashboard is **situational awareness**. The Historian/raw bytes are **evidence**. Offline Python is **verdict**.

---

# 1. STANDING DOCTRINE — NON-NEGOTIABLE

## 1.1 Serial Studio's role

Serial Studio is permanently scoped as:

- telemetry acquisition;
- multi-device observation;
- visualization;
- Session Database / Historian recording;
- raw-byte preservation;
- replay;
- operator awareness;
- optional read-only external analysis.

It is **not** the authoritative command transport for silicon tests.

## 1.2 Exclusive serial-port ownership

A silicon test that requires interactive command/reply owns the target K1 serial port exclusively.

**Serial Studio must release that port first.**

No two owners on one CDC.

No Serial Studio shuttle.
No `k1_gate` command bridge.
No hidden command proxy.
No “just one command through :7777.”

This is architecture, not a temporary hold.

## 1.3 Authority hierarchy

Use this hierarchy everywhere in docs, UI labels, receipts and agent reasoning:

```text
DEVICE CLOCKS / DEVICE COUNTERS    = timing authority
RAW BYTES                          = transport evidence
HISTORIAN SNAPSHOT                 = session evidence
PARSER RAW + FINAL VALUES          = structured evidence
SERIAL STUDIO HOST TIMESTAMPS      = acquisition / transport diagnostic
PLOTS / PAINTER / WEB VIEW         = engineering intuition
SCREENSHOTS                         = awareness / communication only
OFFLINE PYTHON SCORER              = verdict
```

## 1.4 No invented telemetry

The parser may not fabricate fields that the K1 did not emit.

Examples already correctly rejected:

- `firmware_sha` if not on the wire;
- `run_id` if not on the wire;
- device `frame_seq` if not on the wire;
- `audio_frame_seq` if not on the wire;
- `AP_us` if not on the wire;
- device drop count if not on the wire.

Host-derived fields must be clearly named as host-derived.

## 1.5 Fresh values are not held values

Serial Studio's last-known-value behavior is useful for display and dangerous for statistics.

The project already carries `record_kind` and `update_mask` specifically to distinguish fresh updates from held values. Every new visualization or scorer must preserve that distinction.

---

# 2. SOURCE BASIS

This brief is grounded in:

1. The uploaded **actual** `K1 Dual UART Observability.ssproj` written by Serial Studio v4.0.3.
2. The uploaded screenshot of the live Overview workspace.
3. Serial Studio upstream documentation at tag **v4.0.3**, especially:
   - `Project-Editor.md`
   - `Widget-Reference.md`
   - `Plots.md`
   - `Dataset-Transforms.md`
   - `Actions.md`
   - `Control-Script.md`
   - `Session-Database.md`
   - `Extensions.md`
   - `Plugin-Development.md`
   - `API-Reference.md`
   - `gRPC-Server.md`
   - `Data-Flow.md`
   - `Threading-and-Timing.md`
   - `Command-Line-Interface.md`
   - `SerialStudio-SDK.md`
4. The K1 observability doctrine established after the failed Serial Studio command-shuttle experiment.

The brief intentionally distinguishes:

- facts supported by the current project/parser;
- Serial Studio platform capabilities;
- proposed UI/analysis behavior;
- quantities that remain undefined by the K1 telemetry contract.

---

# 3. CURRENT PROJECT — FORENSIC AUDIT

## 3.1 What is already good and should survive

Keep the following architectural wins:

- two independent UART sources;
- Bench = source 0;
- Main RPL = source 1;
- independent parser instances per source;
- parser schema v1.1;
- explicit `record_kind`;
- explicit `update_mask`;
- explicit `host_parse_seq` naming;
- device-side `device_ms` where the firmware emits it;
- `event_tid` where the firmware emits it;
- Historian/Session Database as the primary session archive;
- raw bytes enabled in the Historian path;
- project JSON snapshot embedded in each session;
- offline Python session scoring;
- version-controlled `.ssproj`;
- 0 ms CSV row interval when CSV is used;
- 3D widgets not allowed to influence evidence.

These are not the problem.

The problem is the dashboard/data-model composition built on top of them.

---

## 3.2 Dangerous backend configuration that must be removed

### 3.2.1 The dead command shuttle is still embedded in the project

The current project contains a `controlScriptCode` implementing:

```text
k1_gate.tx
  -> source
  -> deviceWriteAndWait()
  -> last_reply / last_error
```

That shuttle is architecturally dead under D19.

**Required action:** delete the control script from the canonical observability project.

The canonical observability `.ssproj` must contain no device-command bridge.

### 3.2.2 `k1_gate` data table is obsolete

Current table:

```text
k1_gate.tx
k1_gate.source
k1_gate.mode
k1_gate.last_error
k1_gate.last_reply
```

This table exists solely for the demoted shuttle.

**Required action:** remove the entire `k1_gate` table from the canonical observability project.

Do not leave archaeological control surfaces in a passive instrument.

### 3.2.3 Auto-reconnect is unsafe for the permanent exclusive-port doctrine

Both UART sources currently carry:

```json
"autoReconnect": true
```

That is inappropriate for the canonical observability instrument.

If Serial Studio releases a K1 for a pyserial silicon test, it must not later race to reacquire that port automatically.

**Required canonical state:**

```json
"autoReconnect": false
```

for both Bench and Main.

Manual observation connection is intentional. Port ownership must never change behind the operator's back.

### 3.2.4 Serial Studio currently auto-transmits commands every 250 ms

Two actions are configured:

- `Poll B489A500`
- `Poll 9087A500`

Both currently:

- auto-execute on connect;
- use Auto Start timer mode;
- run every 250 ms;
- transmit `:event_status`, `:fps`, and `:led_fps`.

This means the project called “Observability” is actually an active request/response client as soon as it connects.

That must stop being the default.

**Canonical evidence profile:** no automatic device writes.

If health polling remains useful in ordinary bench work, implement it as an explicitly operator-enabled **ACTIVE POLLING** feature, not an invisible default. See Section 14.

---

## 3.3 Current virtual transforms are incorrectly wired

Serial Studio's v4.0.3 transform documentation states that a **virtual dataset receives `value = 0`** and must obtain sibling/other data through `datasetGetRaw()`, `datasetGetFinal()`, or data tables.

The current project defines virtual datasets such as:

- `frame_dt_ms`
- `host_device_skew_ms`
- `transport_residual_ms`

but their transform functions operate directly on the virtual dataset's own `value` argument.

That means they are not calculating from `device_ms` at all.

This is a structural bug, not a cosmetic issue.

### Required action

Delete the broken derived datasets from the active UI until replaced with correctly sourced versions.

No virtual metric is allowed into an operational workspace until its dependency chain is explicit and covered by a fixture test.

---

## 3.4 The Main device has a blanket 4 Hz FFT sampling assumption

Most Main datasets are configured with:

```json
"fftSamplingRate": 4
```

while Bench datasets are mostly configured at 133 Hz.

That is not a valid way to configure FFT.

FFT sampling rate belongs to the **specific metric's fresh sample cadence**, not the device as a whole.

The parser proves that different records update different fields:

### `[AP]`

Updates:

- BPM
- confidence
- lock
- beat
- onset
- bass onset
- silence
- AGC gain
- peak scaled
- SSL
- lightshow

### `EVENT_STATUS`

Updates:

- beat
- onset
- bass onset
- silence
- energy
- novelty
- confidence
- device time
- frame_ms
- event transaction ID

### `SYSTEM_FPS`

Updates only system FPS.

### `LED_FPS`

Updates only LED FPS.

Therefore a blanket per-device FFT rate is semantically wrong.

**Required rule:** FFT is enabled only for a metric with a known, uniform, fresh update cadence. Its configured FFT rate must be proven from the telemetry source or a measured session.

---

## 3.5 The top-left MultiPlot is structurally incapable of being useful in its present form

The current Bench group mixes quantities with unrelated semantics and scales:

- BPM;
- confidence;
- five state/event booleans;
- AGC;
- peak;
- energy;
- novelty;
- plus timing/counter fields in the wider group.

A MultiPlot has **one shared Y axis**.

That is appropriate for comparable channels such as X/Y/Z acceleration or several temperatures. It is not appropriate for BPM + booleans + normalized envelopes + counters.

This is why the widget is unreadable even when the data itself is correct.

The correct remedy is **not** “turn on the other 20 curves.”

The correct remedy is to split the group into homogeneous semantic families.

---

## 3.6 `Envelope FFT (peak_scaled)` is mislabeled and misplaced

An FFT of `peak_scaled` is not an audio spectrum.

It is the frequency content of a **scalar envelope / AP driver** sampled at the telemetry rate.

That can be useful — for example, to expose periodic amplitude modulation or periodic scheduler coupling — but only when:

1. `peak_scaled` is known to be fresh at a stable rate;
2. the sampling rate is correct;
3. the operator knows this is an **envelope modulation spectrum**, not a microphone/audio FFT;
4. the plot lives in a diagnostic workspace.

It does not belong on Overview.

---

## 3.7 The LED Panel wastes space because the data is being visualized with the wrong abstraction

The current LED Panel gives five full-width rows to:

- Lock
- Beat
- Onset
- Bass onset
- Silence

That is a poor use of space for two reasons:

1. `Beat`, `Onset`, and `Bass onset` are temporally meaningful **events**, not merely static lamps.
2. `Lock` and `Silence` are **states**, and can be expressed as compact annunciators.

The correct replacement is a compact **event/state timeline**:

```text
LOCK     [========== LOCKED ================]
BEAT     |  |  |  |  |  |  |  |  |  |
ONSET       |       |            |    |
BASS           |           |          |
SILENCE  ____████______________██______
          -10s                         now
```

That answers “what happened when?” rather than “is this light on this instant?”

Serial Studio Pro's Painter widget is exactly the right tool for this.

---

## 3.8 Several named workspaces are shells, not engineered views

The current project contains named workspaces including:

- Timing
- Audio/AP
- Renderer
- Dual-device sync
- Experiment state

But the project file shows:

- **Timing** points to the same Bench MultiPlot;
- **Audio/AP** points to the same Bench MultiPlot;
- **Renderer** points to the same Bench MultiPlot;
- **Dual-device sync** points essentially to one Main MultiPlot;
- **Experiment state** points to a generic data grid.

The names imply specialization that the widgets do not implement.

These workspaces must be rebuilt, not renamed.

---

## 3.9 Three 3D workspaces are active despite no justified 3-axis K1 quantity

The project currently retains:

- `3D Plot`
- `3D Plot (2)`
- `3D Plot (3)`

There is no current K1 observability requirement that justifies three 3D trajectory plots.

Unless a future telemetry schema supplies a real X/Y/Z physical or semantic vector that benefits from 3D representation, these are demonstration debris.

**Required action:** remove them from the canonical operational project.

---

## 3.10 Overview is overloaded

The current Overview workspace references roughly a dozen heterogeneous widgets, including:

- source MultiPlots;
- LED Panel;
- bar panels;
- FPS;
- FFT;
- individual plots;
- Web View.

An overview is not “everything important-looking.”

An overview is a **decision surface**.

Target: no more than 5–6 major visual blocks.

---

# 4. TARGET SYSTEM ARCHITECTURE

```text
             ┌──────────────────────────────┐
             │ K1 BENCH / K1 MAIN RPL      │
             │ device-owned telemetry       │
             └──────────────┬───────────────┘
                            │ UART
                            ▼
             ┌──────────────────────────────┐
             │ SERIAL STUDIO SOURCES        │
             │ source 0 / source 1          │
             │ manual connect only          │
             └──────────────┬───────────────┘
                            │
                            ▼
             ┌──────────────────────────────┐
             │ FRAME PARSER v1.x           │
             │ raw values                   │
             │ record_kind / update_mask    │
             │ host_parse_seq               │
             └───────────┬─────────┬────────┘
                         │         │
                raw/final│         │raw bytes
                         ▼         ▼
          ┌──────────────────┐   ┌─────────────────┐
          │ LIVE DATA MODEL  │   │ HISTORIAN DB    │
          │ semantic groups  │   │ SQLite + raw    │
          └───────┬──────────┘   │ project snapshot│
                  │              └────────┬────────┘
                  ▼                       │
         ┌───────────────────┐            ▼
         │ WORKSPACES        │     immutable snapshot
         │ plots / painter   │            │
         │ compact status    │            ▼
         └────────┬──────────┘      Python scorer
                  │                       │
                  └──── awareness         └── verdict

Optional later:

Serial Studio gRPC StreamFrames/StreamRawData
             │
             ▼
read-only K1 Live Analyzer plugin
             │
             ├── rolling diagnostics
             └── local WebView @127.0.0.1
```

---

# 5. DATA MODEL — CLASSIFY BEFORE VISUALIZING

Every K1 dataset must be assigned one semantic class.

## 5.1 Classes

| Class | Meaning | Correct visualization |
|---|---|---|
| **STATE** | persists until changed | compact indicator, status chip, state band |
| **EVENT** | momentary occurrence | event raster, stem plot, triggered scope |
| **LEVEL** | bounded continuous quantity | line plot, bar, meter |
| **RATE** | frequency / throughput | digital + bar / trend |
| **COUNTER** | monotonic identity/progression | digital / derivative / forensic table |
| **CLOCK** | monotonic device time | uptime / timing analysis |
| **ENUM** | operating state / mode | decoded text label |
| **PROVENANCE** | parser/record source | forensic grid / freshness logic |
| **UNKNOWN** | semantics not sufficiently defined | keep out of Overview until defined |

## 5.2 Current K1 field classification

| Field | Class | Current source records | Operational meaning |
|---|---|---|---|
| BPM | RATE | `[AP]` | tempo estimate; meaningful only alongside lock/confidence |
| Beat conf | LEVEL | `[AP]`, `EVENT_STATUS` | tracker confidence; likely normalized, confirm contract |
| Lock | STATE | `[AP]` | beat/tempo tracker lock state |
| Beat | EVENT | `[AP]`, `EVENT_STATUS` | beat pulse/event |
| Onset | EVENT | `[AP]`, `EVENT_STATUS` | transient/onset event |
| Bass onset | EVENT | `[AP]`, `EVENT_STATUS` | low-frequency onset event |
| Silence | STATE | `[AP]`, `EVENT_STATUS` | silence detector state |
| AGC gain | LEVEL | `[AP]` | AGC/control gain; **not loudness** |
| Peak scaled | LEVEL | `[AP]` | normalized peak/envelope driver; **not audio waveform** |
| SSL | UNKNOWN | `[AP]` | do not interpret until firmware/schema meaning is explicit |
| Energy | LEVEL | `EVENT_STATUS` | device-reported energy metric |
| Novelty | LEVEL | `EVENT_STATUS` | device-reported novelty metric; exact DSP semantics stay firmware-defined |
| System FPS | RATE | `SYSTEM_FPS` | system/render loop cadence metric |
| LED FPS | RATE | `LED_FPS` | LED output cadence metric |
| Lightshow | ENUM/UNKNOWN | `[AP]` | decode only after numeric meaning is confirmed |
| device_ms | CLOCK | `EVENT_STATUS` | device-side monotonic ms; timing authority at ms resolution |
| frame_ms | UNKNOWN/TIMING | `EVENT_STATUS` | define exact firmware meaning before interpreting |
| host_parse_seq | COUNTER / HOST | every parsed record | parser progress; **not device frame sequence** |
| event_tid | COUNTER / DEVICE | `EVENT_STATUS` | device transaction/event-status ID |
| record_kind | PROVENANCE | parser-derived | which record class created this frame |
| update_mask | PROVENANCE | parser-derived | which fields are fresh in this frame |

### Rule

**UNKNOWN does not mean “delete.”**

It means “do not put it on Mission Control and pretend it has a known engineering meaning.”

---

# 6. RANGE / UNITS POLICY

The current project leaves many plot/widget min/max fields at `0`, which encourages autoscaling and inconsistent visual interpretation.

Use the following policy.

## 6.1 Confirmed booleans

For Lock / Beat / Onset / Bass onset / Silence:

```text
range = 0..1
```

Use event/state rendering, not analog gauges.

## 6.2 Normalized continuous metrics

For fields that the telemetry schema or firmware explicitly proves are normalized:

- Beat confidence
- Peak scaled
- Energy
- Novelty
- AGC gain if proven normalized

use:

```text
plotMin = 0
plotMax = 1
widgetMin = 0
widgetMax = 1
```

Do not assume normalization merely from a current observed value.

If the firmware contract does not state the range, leave the field diagnostic until confirmed.

## 6.3 BPM

Use a broad display range until the firmware's allowed BPM range is explicitly sourced.

Suggested temporary **display-only** range:

```text
0..240 BPM
```

No alarm thresholds until a product acceptance range exists.

## 6.4 FPS

The existing project already uses `0..240 Hz` for system/LED FPS bars.

That is acceptable as a display range.

Do not create warning/critical bands until an engineering threshold is sourced.

## 6.5 Counters and clocks

Do not graph raw `device_ms`, `host_parse_seq`, or `event_tid` on a shared amplitude axis.

Display them as:

- uptime;
- latest counter;
- derived delta/rate;
- forensic data grid.

---

# 7. GLOBAL DASHBOARD SETTINGS

## 7.1 Time range

Set default scrolling plot time range to:

```text
20 s
```

Why:

- long enough to see multiple musical beats/phrases;
- short enough to react to state changes;
- useful for comparing two devices visually.

## 7.2 Point count

Set:

```text
pointCount = 4096
```

At ~133 Hz, 20 seconds requires ~2660 samples.

4096 leaves margin without becoming ridiculous. Serial Studio uses a decimating ring buffer and is designed to handle large plot histories.

## 7.3 Default plot mode

Scrolling **Time** mode is the default.

Do **not** enable Sweep/Trigger globally.

The current Bench widget has Sweep enabled. That should be removed from Mission Control.

Sweep/Trigger is reserved for the dedicated Event Scope workspace.

## 7.4 Interpolation

Use by semantic class:

- LEVEL: linear where it improves readability;
- STATE: zero-order hold;
- EVENT: stem / point / event raster;
- RATE: linear or ZOH depending on update behavior.

Do not smooth event pulses into fake ramps.

---

# 8. WORKSPACE INFORMATION ARCHITECTURE

Create workspace folders to keep the project legible.

```text
LIVE
  01 Mission Control
  02 Audio + Tempo
  03 Event Timeline
  04 Dual-K1 Compare

SYSTEM
  05 Performance
  06 Transport + Freshness
  07 Renderer

DIAGNOSTICS
  08 Event Scope
  09 Modulation Spectrum
  10 Raw / Forensics

ARCHIVE / DEV
  All Data
  Web View (optional)
```

Remove the three generic 3D workspaces unless a real 3-axis quantity later justifies them.

---

# 9. WORKSPACE 01 — MISSION CONTROL

## Purpose

Answer in under five seconds:

- Are both K1s alive?
- What tempo does each believe?
- Are they locked?
- What is each currently hearing?
- Are rates healthy?
- Is data fresh?
- Are the devices disagreeing materially?

## Target layout

```text
┌──────────────────────────────────────────────────────────┐
│ K1 DUAL OBSERVABILITY — session / recording / freshness │
├──────────────────────────┬───────────────────────────────┤
│ BENCH STATUS CARD        │ MAIN RPL STATUS CARD          │
│ BPM / lock / conf        │ BPM / lock / conf             │
│ peak / energy / novelty  │ peak / energy / novelty       │
│ sys/LED FPS              │ sys/LED FPS                   │
│ telemetry age            │ telemetry age                 │
├──────────────────────────┴───────────────────────────────┤
│ DUAL EVENT TIMELINE — beat / onset / bass / silence     │
├──────────────────────────┬───────────────────────────────┤
│ normalized Bench levels  │ normalized Main levels        │
└──────────────────────────┴───────────────────────────────┘
```

## Widgets

### A. Bench compact status card

Preferred implementation:

- **Painter** bound to a Bench status group, or the hardened Web View if the plugin/web backend is already stable.

Must show:

- BPM large numeric;
- Lock compact chip;
- Beat confidence bar;
- Peak bar;
- Energy bar;
- Novelty bar;
- System FPS small numeric;
- LED FPS small numeric;
- telemetry freshness / last-update age;
- source label `B489A500`.

### B. Main compact status card

Same layout and visual ordering as Bench.

The two cards must be visually symmetric so differences are perceptually obvious.

### C. Event timeline

One compact dual-device Painter or two aligned Painters.

Use event lanes, not giant LED rows.

### D/E. Normalized signal panels

Reuse the existing `Bench mix 0-1` and `Main mix 0-1` groups after cleanup.

Recommended displayed levels:

- peak;
- energy;
- novelty;
- confidence;
- AGC only if its range/semantics are confirmed.

## Explicitly prohibited on Mission Control

- raw `device_ms`;
- raw counters;
- raw `update_mask`;
- `record_kind` numeric IDs;
- FFT;
- Waterfall;
- 3D plots;
- giant LED panel;
- more than one broad MultiPlot;
- `SSL` until defined;
- control/output widgets.

---

# 10. WORKSPACE 02 — AUDIO + TEMPO

## Purpose

Understand the AP/tempo system as an audio-analysis instrument rather than a pile of unrelated numbers.

## Layout

### A. Tempo tracker

Per device:

- BPM large numeric;
- confidence 0..1 bar if contract confirms normalized;
- Lock state;
- beat-event count / recent beat raster.

### B. Envelope dynamics MultiPlot — homogeneous only

Per device, one plot containing only normalized level-like channels:

```text
peak_scaled
energy
novelty
```

Do not include BPM or boolean states.

If `energy` and `novelty` are only fresh at `EVENT_STATUS` rate while `peak_scaled` is `[AP]` rate, either:

1. keep separate plots by freshness class; or
2. clearly render held values and freshness markers.

Preferred: separate plots.

### C. AGC panel

AGC deserves its own plot/bar because it is a **control response**, not a direct measurement of sound level.

Useful interpretation:

- Peak rises while AGC falls → expected normalization behavior may be visible.
- Peak and AGC both drift → possible input or calibration issue.

Do not overlay AGC with BPM.

### D. Silence state band

Compact horizontal state strip across the plot time range.

---

# 11. WORKSPACE 03 — EVENT TIMELINE

## Purpose

Make Beat / Onset / Bass Onset / Silence genuinely useful.

## Painter specification

Create one source-specific Painter for Bench and one for Main.

Datasets in each Painter group:

- Lock
- Beat
- Onset
- Bass onset
- Silence
- `record_kind`
- `update_mask`
- optionally `device_ms`

## Required behavior

Painter `onFrame()`:

1. read `update_mask`;
2. determine whether each event/state field was actually updated in this frame;
3. append event pulses only when the corresponding update bit is fresh;
4. keep Lock/Silence as state spans;
5. maintain ~10–20 seconds of history;
6. never send device commands;
7. never infer missing events from held values.

## Visual design

Five horizontal lanes:

- LOCK state band;
- BEAT stems;
- ONSET stems;
- BASS stems;
- SILENCE state band.

Current time at right.

Add small text:

```text
fresh AP age: ... ms
EVENT_STATUS age: ... ms
```

if supplied by the read-only analysis backend.

## Why Painter is justified

Serial Studio Painter is purpose-built for project-specific visualizations and can maintain ring-buffer state with `onFrame()`.

This is exactly the use case.

---

# 12. WORKSPACE 04 — DUAL-K1 COMPARE

## Purpose

Expose differences between Bench and Main without pretending host arrival time is synchronization authority.

## Native comparisons

Show side-by-side:

- BPM;
- beat confidence;
- peak;
- energy;
- novelty;
- system FPS;
- LED FPS;
- lock state;
- silence state.

## Derived comparisons — plugin/web only

A read-only live analyzer may compute:

- `ΔBPM = Main - Bench`;
- `Δpeak`;
- `Δenergy`;
- `Δnovelty`;
- `Δsystem_fps`;
- `Δled_fps`;
- host inter-arrival residual difference;
- event-count differences over rolling windows.

Label every host-time comparison:

```text
TRANSPORT DIAGNOSTIC — NOT DEVICE SYNC
```

## Do not create

- “sync error” from raw host arrival timestamps;
- sub-ms alignment claims;
- automatic PASS/FAIL based on host skew;
- cross-device lag correction hidden inside the dashboard.

---

# 13. WORKSPACE 05 — PERFORMANCE

## Purpose

Monitor whether the product/runtime is meeting its own expected operating cadence.

## Widgets

### FPS panel

Keep and improve the existing group containing:

- Bench System FPS;
- Bench LED FPS;
- Main System FPS;
- Main LED FPS.

Shared unit: Hz.

This is a valid Bar/Meter group because all four quantities are rates.

### Trend plot

Create one MultiPlot for the four FPS rates **only**.

Fixed Y range initially:

```text
0..240 Hz
```

Do not mix audio levels into this plot.

### Alarm bands

Do not invent product thresholds.

Add Warning/Critical bands only after the firmware/product acceptance docs state allowable limits.

Until then, use neutral bars with current values.

---

# 14. WORKSPACE 06 — TRANSPORT + FRESHNESS

## Purpose

Answer:

- Is telemetry arriving?
- Which record types are arriving?
- Are device-side counters progressing?
- Is data stale?
- Is host acquisition jittery?

## Raw fields

Display compactly:

- device uptime (`device_ms` converted to human-readable `HH:MM:SS.mmm` in Painter/WebView);
- `event_tid`;
- `host_parse_seq`;
- `record_kind` decoded to text;
- `update_mask` rendered as named freshness bits, not an integer;
- raw-byte receive rate from plugin/Historian where available.

## Derived diagnostics

Preferred live analyzer outputs:

- parsed frames/s by source;
- raw bytes/s by source;
- AP record rate;
- EVENT_STATUS record rate;
- SYSTEM_FPS reply rate;
- LED_FPS reply rate;
- age of last fresh update for each class;
- host inter-arrival p50/p95/p99;
- device_ms step distribution where fresh;
- `event_tid` increments/gaps.

These are **diagnostics**, not timing authority.

## Broken current transforms

Do not reuse the current `frame_dt_ms`, `host_device_skew_ms`, or `transport_residual_ms` code.

They are not wired to sibling datasets correctly.

Reimplement only after tests prove the data dependency.

---

# 15. WORKSPACE 07 — RENDERER

## Purpose

Show what the rendering engine is doing without pretending the observability schema currently has a full renderer trace.

Use only fields actually present.

Current possible fields:

- Lightshow numeric/enum;
- LED FPS;
- peak_scaled as a renderer driver where appropriate;
- lock/beat state if relevant to current mode.

## Lightshow decoding

If `Lightshow` is a stable numeric mode identifier, map it to a readable name only from the firmware-authoritative effect-semantics export.

Do not invent a second taxonomy.

If the numeric meaning is not proven, display:

```text
Lightshow raw = N
```

and keep it out of Mission Control.

---

# 16. WORKSPACE 08 — EVENT SCOPE (PRO SWEEP/TRIGGER)

This is where Serial Studio Pro can do something the current dashboard completely wastes.

## Purpose

Use oscilloscope-style Sweep/Trigger to inspect the shape of AP metrics around repeating events.

## Recommended scope A — Onset-triggered AP response

Curves:

- peak_scaled;
- energy;
- novelty.

Trigger source:

- Onset.

Trigger:

```text
level = 0.5
edge = rising
mode = Normal or Single
```

Timebase:

```text
~0.5–1.0 s
```

This gives an immediately interpretable “what does the AP response look like around an onset?” instrument.

## Recommended scope B — Bass-onset triggered

Same concept, Bass onset trigger.

## Important

Sweep mode is for intuition/diagnostics.

It does not replace recorded timing evidence.

---

# 17. WORKSPACE 09 — MODULATION SPECTRUM

## Rename the current FFT

Current:

```text
Envelope FFT (peak_scaled)
```

Target title:

```text
Peak Envelope Modulation Spectrum — NOT AUDIO FFT
```

## Sampling rule

FFT sampling rate must equal the **fresh sample cadence of peak_scaled**.

Do not configure `133 Hz` simply because Bench often streams `[AP]` near 133 Hz.

Prove it from either:

- firmware contract;
- recorded `record_kind + update_mask` timestamps;
- a measured Historian session.

## Window

Start with:

```text
256 samples
Blackman-Harris
```

At 133 Hz this is roughly a 1.9 s window.

If you need better low-frequency resolution, consider 512 samples after verifying UI performance.

## Frequency range

For an envelope whose musical modulation is of interest, displaying the full Nyquist range may be less informative than a focused range.

Do not hard-code a narrower range until the diagnostic question is named.

## Waterfall

Use only if repeated modulation over time is useful.

Y axis should remain elapsed time unless a genuine order-tracking variable exists.

---

# 18. WORKSPACE 10 — RAW / FORENSICS

## Purpose

Put the ugly truth somewhere useful instead of contaminating every operational screen.

Include:

- Data Grid of all canonical source fields;
- record_kind;
- update_mask;
- host_parse_seq;
- event_tid;
- device_ms;
- frame_ms;
- SSL;
- raw lightshow value;
- any unknown/reserved fields;
- Terminal/raw console when needed.

This is where engineers go when something looks wrong.

It is not the default dashboard.

---

# 19. ALL DATA WORKSPACE

Keep one complete “everything” workspace for project development.

It must be visually marked:

```text
DEVELOPMENT / FORENSIC — NOT OPERATIONS
```

Do not use it as Overview.

---

# 20. POLLING / ACTIONS POLICY

## 20.1 Canonical passive observability profile

The canonical project must not automatically write to either K1.

Set both existing poll actions to:

```text
autoExecuteOnConnect = false
timerMode = Off
```

Preferred: remove them from the canonical evidence project entirely.

## 20.2 If operator polling is retained

Create explicitly named actions:

```text
Bench Health Snapshot
Main Health Snapshot
```

Manual trigger only.

Or, for ordinary bench sessions only:

```text
Bench ACTIVE Health Polling
Main ACTIVE Health Polling
```

with **Toggle on Trigger**, not Auto Start.

Use a slower interval initially:

```text
1000 ms
```

The UI must make it obvious that ACTIVE polling is enabled.

## 20.3 Separate project is cleaner

Preferred long-term architecture:

```text
K1-Dual-UART-Observability.ssproj       # passive instrument
K1-Dual-UART-Interactive-Bench.ssproj   # explicit active actions/controls
```

Never use the interactive project as an evidence instrument without explicitly documenting its writes.

---

# 21. CONNECTION SETTINGS

For both K1 sources:

```text
bus                 UART
baud                115200
8N1                  yes
flow control         none
DTR                  false (current known-good setting)
auto reconnect       FALSE
```

Serial Studio connection must be intentional/manual.

## Evidence-run preflight

Before connecting Serial Studio:

1. verify no pyserial test owns the port;
2. verify cadence/silicon command harness is not running;
3. manually connect Serial Studio;
4. verify RX before calling the session usable;
5. if RX is dead, do not claim an active observation session merely because the port says open.

---

# 22. PARSER ARCHITECTURE

## 22.1 Keep parser v1.1 provenance model

The current parser's best design choice is the explicit distinction between:

- parsed values;
- parser-derived sequence;
- device counters;
- record kind;
- freshness mask.

Keep that.

## 22.2 Do not make the parser prettier at the expense of evidence

The parser may retain last-known values for dashboard convenience.

The freshness mask remains the source of truth about whether a field was updated this frame.

## 22.3 Record kind enumeration

Keep current mapping documented:

```text
1 = [AP]
2 = EVENT_STATUS
3 = SYSTEM_FPS
4 = LED_FPS
5 = VERSION / build line
```

If a new record class is introduced, bump schema version and parser fixtures.

## 22.4 Reserved/unused slots

Remove meaningless `unused_slot_*` datasets from operational groups.

If parser array position stability requires them, keep them in the parser contract but hide them from all normal workspaces.

---

# 23. FRESHNESS — LIVE UI CONTRACT

A high-quality observability dashboard must answer not only **what value** but **how old is that value**.

## 23.1 Freshness categories

At minimum track age for:

- `[AP]` data;
- EVENT_STATUS data;
- SYSTEM_FPS data;
- LED_FPS data.

## 23.2 Preferred implementation

The read-only live analyzer plugin tracks `record_kind` and timestamps and calculates:

```text
ap_age_ms
event_status_age_ms
system_fps_age_ms
led_fps_age_ms
```

Display compactly in the status cards.

## 23.3 Stale rendering

When a source class exceeds an expected freshness window:

- dim its displayed values;
- show `STALE`;
- do not silently continue to present the last value as current.

Do not choose warning thresholds until the expected source cadence is sourced.

---

# 24. DATASET TRANSFORMS — RULES

## 24.1 Virtual dataset rule

Serial Studio v4.0.3 virtual datasets receive `value = 0`.

Therefore:

**A virtual transform must never assume its `value` argument is a sibling telemetry field.**

Use:

- `datasetGetRaw(uniqueId)`;
- `datasetGetFinal(uniqueId)`;
- table access;
- frame metadata.

## 24.2 Processing-order rule

Dataset transforms are order-dependent.

If dataset B reads dataset A's final value, A must be processed first.

For derived groups, place canonical source datasets before derived metrics.

## 24.3 Change-driven transforms

Do not turn `changeDrivenTransforms` on merely because it exists.

It becomes attractive after the derived-data model is rebuilt and dependency tests exist.

Initial re-architecture target:

```text
changeDrivenTransforms = false
```

Then benchmark/enable later only if it provides a measurable benefit.

## 24.4 Live statistics

Transforms are suitable for cheap per-frame engineering transforms.

Do not make them the authority for:

- p95/p99;
- confidence intervals;
- correlations;
- gate scoring;
- cross-device lag search.

Those belong in Python.

---

# 25. PAINTER DESIGN — SAFETY RULES

Serial Studio Painter scripts can call `deviceWrite()` and `actionFire()`.

The canonical K1 observability project must **never use those functions**.

Add a static lint rule:

```text
Painter source must not contain:
deviceWrite(
actionFire(
apiCall("io.write
WriteRawData
```

Painter code should do only:

- visual rendering;
- ring-buffer maintenance;
- lightweight local state;
- formatting.

Target paint time:

```text
< 10 ms
```

No giant per-frame allocations.

---

# 26. WEB VIEW — KEEP, BUT MAKE IT A REAL SUBSYSTEM

The existing Web View is the only current dashboard element that provides a genuinely useful dual-device at-a-glance view.

Do not throw it away simply because the surrounding dashboard is poor.

But formalize it.

## 26.1 Current dependency

Project points at:

```text
http://127.0.0.1:8765/
```

That means the dashboard depends on an external local web service.

This dependency must be explicit, versioned, testable and read-only.

## 26.2 Target

`K1 Live Web View v2` should show:

- symmetric Bench/Main cards;
- BPM / lock / confidence;
- peak / energy / novelty / AGC;
- sys / LED FPS;
- freshness ages;
- small 10 s sparklines;
- event strip;
- per-device raw frame rate;
- coarse deltas between devices;
- session/recording state if available.

## 26.3 No device control

The Web View backend may consume Serial Studio frame/raw streams.

It must not expose:

- command text boxes;
- device writes;
- reconnect buttons;
- cadence controls;
- hidden RPC to `io.writeData`.

---

# 27. READ-ONLY K1 LIVE ANALYZER PLUGIN

This is the first plugin worth building **after** the native project is clean.

## 27.1 Name

```text
spectrasynq-k1-live-analyzer
```

## 27.2 Transport

Use gRPC `StreamFrames` / optionally `StreamRawData` on localhost:8888.

Why:

- high-rate binary streaming;
- explicit server stream;
- less JSON overhead;
- designed by Serial Studio for real-time plugins.

## 27.3 Hard read-only implementation

The plugin code must not call:

- `WriteRawData`;
- `io.writeData`;
- `deviceWrite`;
- Serial Studio actions;
- `io.connect` / `io.disconnect` as automation.

Ideally the source code does not even define wrappers for write operations.

## 27.4 Plugin responsibilities

Compute live diagnostics only:

- frame arrival rate per source;
- raw byte rate per source;
- record-kind rate per source;
- per-field freshness age;
- rolling inter-arrival p50/p95/p99;
- event counts per 10/60 s;
- event_tid delta/gap diagnostics;
- BPM delta;
- peak/energy/novelty delta;
- system/LED FPS delta;
- host transport residual diagnostics;
- source alive/dead state.

## 27.5 Not verdict

Plugin output is advisory/live.

Offline `session_receipt.py` remains authoritative.

## 27.6 Web View integration

The plugin may serve the local Web View on:

```text
127.0.0.1:8765
```

This makes the Web View backend a formally versioned extension instead of an orphan helper process.

---

# 28. PRIVATE SPECTRASYNQ EXTENSION REPOSITORY

Do this only after the project/parser/plugin interfaces stabilize.

Suggested repository:

```text
SpectraSynq-SerialStudio-Extensions/
  manifest.json

  frame-parser/
    k1-telemetry-v1/
      info.json
      k1_ap_parser.js

  project-template/
    k1-dual-uart-observability/
      info.json
      K1-Dual-UART-Observability.ssproj

  plugin/
    k1-live-analyzer/
      info.json
      run.sh
      plugin.py
      requirements.txt
      web/

  theme/
    optional-lab-theme/
```

Serial Studio Pro supports custom extension repositories, including local folders and private/internal repositories.

## Repository purpose

- reproducible installation;
- versioned parser distribution;
- plugin lifecycle management;
- project template distribution;
- no ad-hoc copying files into Documents.

---

# 29. API SERVER POLICY

## Default

If no plugin or automated read-only consumer is needed:

```text
API Server = OFF
```

## When plugin/web view is used

```text
API Server = ON
External connections = OFF
Bind = localhost only
```

Both 7777 and 8888 start together in the official Pro build.

Remember:

- any local process can connect to the localhost API;
- the API contains hardware-write commands;
- therefore API access is a capability surface, not a harmless status port.

## Static safety

Plugin/repo tests should assert no production observability tool uses hardware-write API commands.

---

# 30. HISTORIAN / SESSION DATABASE

## 30.1 Primary evidence store

Keep Session Recording as the canonical Serial Studio archive for serious observation runs.

It captures:

- parsed raw values;
- transformed/final values;
- raw bytes;
- data-table snapshots;
- project JSON snapshot;
- column layout;
- notes/tags.

## 30.2 Session lifecycle

For serious runs:

1. connect intentionally;
2. verify RX;
3. start/confirm Session Recording;
4. tag/annotate the session with host-side context;
5. record;
6. disconnect/close session;
7. create immutable SQLite snapshot;
8. hash snapshot;
9. run Python receipt/scorer.

## 30.3 Live DB hash

A hash of the growing WAL-mode database is a **live fingerprint**, not final evidence identity.

Final evidence uses a closed/transactionally consistent snapshot.

## 30.4 Session tags

Use tags for host/operator metadata such as:

```text
bench-observe
main-observe
music-session
regression
anomaly
pre-change
post-change
```

Do not treat a host tag as if the device emitted it.

---

# 31. CSV AND MDF4

## CSV

Use when:

- quick pandas/Excel access is desired;
- a simple portable table is useful.

Keep row interval at 0 ms for one row per received frame.

CSV is secondary to the Session DB for canonical project evidence.

## MDF4

Use for:

- long recordings;
- high data volume;
- heterogeneous channel rates;
- external measurement tooling.

Do not enable MDF4 just because Pro supports it.

Use it when the recording problem actually benefits.

---

# 32. PROJECT FILE ORGANIZATION

Recommended repository layout:

```text
tools/serial-studio/
  README.md
  TELEMETRY_SCHEMA.md

  projects/
    K1-Dual-UART-Observability.ssproj
    legacy/
      K1-Dual-UART-Observability-grok-20260831.ssproj

  parsers/
    k1_ap_parser.js

  painters/
    k1_event_timeline.js
    k1_status_card.js

  plugin/
    k1-live-analyzer/
      info.json
      run.sh
      plugin.py
      requirements.txt
      web/

  scripts/
    lint_project.py
    validate_project_api.py
    session_receipt.py
    subscribe_readonly.py

  tests/
    fixtures/
      bench_ap.txt
      main_ap.txt
      event_status.txt
      system_fps.txt
      led_fps.txt
      malformed.txt
    test_project_lint.py
    test_parser_golden.py
    test_plugin_readonly.py

  captures/
    snapshots/
      .gitkeep
```

---

# 33. PROJECT LINTER — MANDATORY

Create `lint_project.py`.

It must parse `.ssproj` JSON and fail on architectural regressions.

## Mandatory checks

### Safety

FAIL if:

- `autoReconnect == true` on either canonical K1 source;
- any action has `autoExecuteOnConnect == true`;
- any action uses Auto Start timer mode in canonical observability project;
- control script contains `deviceWrite`, `deviceWriteAndWait`, `io.writeData`, `actionFire`;
- Painter code contains device writes/actions;
- `k1_gate` table exists;
- output controls exist in canonical passive project.

### Data model

FAIL if:

- a virtual dataset transform uses only `value` and never references a declared dependency;
- a MultiPlot mixes CLOCK/COUNTER fields with LEVEL/RATE fields;
- an FFT is enabled with sampling rate missing/zero;
- an FFT rate is copied from source-level assumptions without a documented metric rate map;
- duplicate unique IDs exist;
- workspace references a missing group/dataset;
- operational workspace contains `unused_slot_*`;
- group title contains generic `3D Plot` without an allowlisted rationale.

### UX

WARN/FAIL if:

- Mission Control contains > 6 major widget groups;
- a dataset displayed in Bar/Gauge/Meter has `widgetMin == widgetMax`;
- operational dataset has no unit where one is meaningful;
- titles are raw internal names instead of readable engineering names.

---

# 34. PARSER GOLDEN TESTS

Use Serial Studio's own `project.frameParser.dryRun` where practical.

Fixtures must cover:

- Bench `[AP]`;
- Main `[AP]`;
- EVENT_STATUS;
- SYSTEM_FPS;
- LED_FPS;
- VERSION;
- malformed line;
- empty line;
- missing optional fields;
- historical slot-shift regression;
- reboot/reset sequence if represented.

Assertions:

- array width correct;
- slots correct;
- `record_kind` correct;
- update_mask exact;
- host_parse_seq behavior correct;
- unknown/malformed returns empty;
- no invented fields.

---

# 35. CURRENT PROJECT — KEEP / REPURPOSE / DELETE MATRIX

| Current element | Decision | Target |
|---|---|---|
| Bench UART source | KEEP | manual connect, autoReconnect off |
| Main UART source | KEEP | manual connect, autoReconnect off |
| parser v1.1 | KEEP | fixtures + versioned file |
| Historian | KEEP | canonical archive |
| CSV | KEEP OPTIONAL | 0 ms row interval |
| Bench giant MultiPlot | REBUILD | homogeneous semantic groups |
| Main giant MultiPlot | REBUILD | homogeneous semantic groups |
| `Bench mix 0-1` | KEEP/IMPROVE | Mission Control + Audio |
| `Main mix 0-1` | KEEP/IMPROVE | Mission Control + Audio |
| FPS bar panel | KEEP/IMPROVE | Performance workspace |
| giant LED Panel | DELETE/REPLACE | Painter event timeline |
| peak_scaled FFT | MOVE/RENAME | Modulation Spectrum diagnostics |
| Waterfall | OPTIONAL | diagnostics only |
| K1 Live Web View | KEEP/FORMALIZE | read-only plugin-backed v2 |
| 3D Plot ×3 | DELETE | no current 3-axis purpose |
| Timing workspace | REBUILD | real transport/timing widgets |
| Audio/AP workspace | REBUILD | real AP metrics |
| Renderer workspace | REBUILD | actual renderer fields |
| Dual-device sync workspace | REBUILD | dual compare, no false sync claims |
| Experiment state | REDEFINE | session/provenance or remove |
| `frame_dt_ms` virtual | DELETE/REIMPLEMENT | correct dependency |
| `host_device_skew_ms` virtual | DELETE/REIMPLEMENT | correct dependency |
| `transport_residual_ms` virtual | DELETE/REIMPLEMENT | correct dependency |
| `k1_gate` table | DELETE | dead architecture |
| control script shuttle | DELETE | dead architecture |
| auto polling | DISABLE | manual/interactive separate profile |

---

# 36. IMPLEMENTATION PHASES

# PHASE 0 — FREEZE THE CURRENT STATE

## Do

1. Copy current project to:

```text
projects/legacy/K1-Dual-UART-Observability-grok-20260831.ssproj
```

2. SHA-256 it.
3. Record current Serial Studio binary version.
4. Do not modify the legacy copy.
5. Work on a new clone.
6. Keep both K1 serial ports disconnected during structural editing.

## PASS

- immutable baseline exists;
- hash recorded;
- canonical working copy separate.

---

# PHASE 1 — SAFETY SANITATION

## Apply

- remove controlScriptCode shuttle;
- remove `k1_gate` table;
- set both sources `autoReconnect=false`;
- disable autoExecuteOnConnect for all actions;
- disable Auto Start action timers;
- remove output/control surfaces from passive project;
- ensure API not required for basic native dashboard.

## Tests

Run project linter.

## PASS

Canonical project cannot automatically write to either K1 merely by opening/connecting.

---

# PHASE 2 — DATA MODEL CLEANUP

## Apply

- preserve parser array contract;
- hide unused slots;
- remove broken virtual transforms;
- assign field class metadata in `TELEMETRY_SCHEMA.md`;
- establish confirmed ranges/units;
- define freshness/source-record mapping;
- stop blanket FFT rates.

## PASS

Every operational dataset has:

```text
meaning
class
source record(s)
range or UNKNOWN
unit
freshness semantics
allowed widget(s)
```

---

# PHASE 3 — REBUILD NATIVE WORKSPACES

Build in this order:

1. Mission Control;
2. Audio + Tempo;
3. Event Timeline;
4. Performance;
5. Transport + Freshness;
6. Dual-K1 Compare;
7. Renderer;
8. Event Scope;
9. Modulation Spectrum;
10. Raw / Forensics.

Delete fake shell workspaces.

## PASS

Each workspace answers one named engineering question and contains only relevant widgets.

---

# PHASE 4 — PAINTERS

Implement:

```text
k1_status_card.js
k1_event_timeline.js
```

## Test

Use simulator or replayed session first.

No live USB required.

## PASS

- paint < 10 ms typical;
- no write APIs;
- freshness respected;
- event pulses don't become held-state bars;
- theme switch works.

---

# PHASE 5 — READ-ONLY PLUGIN + WEB VIEW V2

Only after native UI passes.

Implement gRPC consumer and local web server.

## Static PASS

No hardware write calls anywhere in plugin.

## Runtime PASS

- reconnects to gRPC stream safely;
- handles source loss;
- shows fresh/stale status;
- does not modify project/device;
- Web View degrades clearly if backend absent.

---

# PHASE 6 — REPLAY / SIMULATOR TEST

Before silicon:

- replay known Historian session;
- or feed K1 telemetry simulator;
- verify all workspaces;
- inspect event timeline;
- verify FFT labels/rates;
- verify no command TX occurs.

## PASS

Dashboard works without live hardware and no evidence semantics depend on operator guessing.

---

# PHASE 7 — ONE-SOURCE LIVE SMOKE

Connect Bench only.

Verify:

- raw bytes > 0;
- AP updates;
- freshness;
- Historian;
- no outbound auto commands;
- status card;
- event timeline;
- normalized plots.

Disconnect.

Then repeat for Main.

No command shuttle.

---

# PHASE 8 — DUAL-SOURCE LIVE SMOKE

Connect both intentionally.

Verify:

- raw RX both sources;
- symmetric cards;
- dual compare;
- Historian records both source IDs;
- no automatic TX;
- no false sync claims;
- performance remains responsive.

---

# PHASE 9 — EVIDENCE SNAPSHOT

Record one controlled observation session.

Then:

- close/freeze snapshot;
- hash snapshot;
- run `session_receipt.py`;
- verify `record_kind/update_mask` freshness counts;
- verify project JSON embedded;
- verify raw bytes both sources.

This proves the instrument, not a product gate.

---

# 37. ACCEPTANCE MATRIX

## Safety

- [ ] no control shuttle
- [ ] no `k1_gate`
- [ ] autoReconnect false both sources
- [ ] no auto-on-connect writes
- [ ] no automatic polling in passive profile
- [ ] no Painter device writes
- [ ] no plugin hardware writes
- [ ] exclusive-port doctrine documented

## Parser / provenance

- [ ] parser golden fixtures pass
- [ ] record_kind exact
- [ ] update_mask exact
- [ ] host_parse_seq clearly host-owned
- [ ] malformed lines fail safe
- [ ] unknown telemetry not invented

## UI

- [ ] Mission Control understandable in <5 s
- [ ] no heterogeneous shared-axis MultiPlot
- [ ] no giant LED real-estate waste
- [ ] event timeline communicates event timing
- [ ] normalized levels use meaningful fixed ranges
- [ ] counters/clocks not plotted as signal amplitude
- [ ] FFT lives only in diagnostics
- [ ] FFT semantics and sampling rate labeled
- [ ] no unexplained 3D widgets
- [ ] each workspace has one engineering purpose

## Historian

- [ ] Session Recording captures parsed values
- [ ] raw bytes both sources
- [ ] project snapshot embedded
- [ ] immutable backup snapshot works
- [ ] receipt hashes snapshot, not growing WAL DB

## Plugin/Web

- [ ] read-only gRPC only
- [ ] no write methods
- [ ] freshness age visible
- [ ] web backend failure explicit
- [ ] plugin not a gate scorer

## Performance

- [ ] UI remains responsive with both sources
- [ ] no frame-loss regression caused by visualization
- [ ] Painter paint time acceptable
- [ ] plugin does not perturb capture path materially

---

# 38. VISUAL ACCEPTANCE TEST — THE FIVE-SECOND RULE

Show the finished Mission Control to an engineer who knows K1 but did not build the dashboard.

Within five seconds they should be able to answer:

1. Are Bench and Main both alive?
2. What BPM does each report?
3. Is each tempo tracker locked?
4. Which device has more peak/energy right now?
5. Did an onset/bass event just happen?
6. Are system/LED rates obviously different?
7. Is any major metric stale?

If they need to open legends, decode million-scale axes, remember colors, or ask what the bottom-left graph means, the dashboard fails.

---

# 39. WHAT “GOD TIER” MEANS HERE

It does **not** mean more widgets.

It means:

- every widget has a reason;
- every axis has semantics;
- every rate has provenance;
- every state distinguishes fresh from held;
- every derived metric identifies its authority;
- every Pro feature is used because it solves a K1 problem;
- evidence and intuition never get conflated;
- the UI can be read under pressure;
- the backend cannot quietly violate the serial ownership doctrine.

A beautiful dashboard that lies is trash.

A dense dashboard that cannot be interpreted is trash.

A dashboard that exposes raw truth, semantic structure, timing health and device differences with minimal cognitive load is an instrument.

That is the target.

---

# 40. AGENT EXECUTION RULES

Assign **one writer** to the canonical `.ssproj`.

Do not launch 40 agents against one project file.

Parallel read-only reviewers are fine. Parallel project writers are not.

The project writer must:

1. work from the frozen baseline clone;
2. execute phases in order;
3. run lint/tests after every phase;
4. never use live K1 USB to debug project JSON structure;
5. use replay/simulator first;
6. produce a diff summary after each phase;
7. stop on any safety regression;
8. not “improve” the firmware to make the dashboard easier;
9. not resurrect command transport;
10. not stamp a product/gate PASS from dashboard appearance.

---

# 41. REQUIRED COMPLETION REPORT

The implementing agent returns:

## Baseline

- original project SHA-256
- working project path
- Serial Studio version

## Safety

- autoReconnect state both sources
- auto actions state
- control script absent
- k1_gate absent
- output controls absent
- API/plugin write audit

## Workspaces

For each workspace:

```text
name
question answered
widgets
source(s)
datasets
ranges
freshness behavior
```

## Parser

- schema version
- fixture test count
- dry-run result

## Derived metrics

For every derived metric:

```text
name
inputs
source of inputs
algorithm
authority class
live-only vs evidence
```

## FFT

For every enabled FFT/Waterfall:

```text
metric
fresh sampling rate
how rate was proven
window size
window type
frequency range
interpretation
```

## Historian

- session ID
- raw bytes per source
- readings per source
- project snapshot present
- snapshot SHA-256

## Performance

- both-source live observation duration
- dashboard responsiveness
- Painter timing if available
- frame/drop diagnostics

## Remaining UNKNOWN

List every telemetry meaning/range that remains unresolved.

Do not silently close UNKNOWNs.

---

# 42. UPSTREAM SERIAL STUDIO v4.0.3 REFERENCES

Canonical upstream reading set for the implementing agent:

- https://github.com/Serial-Studio/Serial-Studio/blob/v4.0.3/doc/help/Project-Editor.md
- https://github.com/Serial-Studio/Serial-Studio/blob/v4.0.3/doc/help/Widget-Reference.md
- https://github.com/Serial-Studio/Serial-Studio/blob/v4.0.3/doc/help/Plots.md
- https://github.com/Serial-Studio/Serial-Studio/blob/v4.0.3/doc/help/Dataset-Transforms.md
- https://github.com/Serial-Studio/Serial-Studio/blob/v4.0.3/doc/help/Data-Tables.md
- https://github.com/Serial-Studio/Serial-Studio/blob/v4.0.3/doc/help/Actions.md
- https://github.com/Serial-Studio/Serial-Studio/blob/v4.0.3/doc/help/Output-Controls.md
- https://github.com/Serial-Studio/Serial-Studio/blob/v4.0.3/doc/help/Painter-Widget.md
- https://github.com/Serial-Studio/Serial-Studio/blob/v4.0.3/doc/help/Session-Database.md
- https://github.com/Serial-Studio/Serial-Studio/blob/v4.0.3/doc/help/Extensions.md
- https://github.com/Serial-Studio/Serial-Studio/blob/v4.0.3/doc/help/Plugin-Development.md
- https://github.com/Serial-Studio/Serial-Studio/blob/v4.0.3/doc/help/API-Reference.md
- https://github.com/Serial-Studio/Serial-Studio/blob/v4.0.3/doc/help/gRPC-Server.md
- https://github.com/Serial-Studio/Serial-Studio/blob/v4.0.3/doc/help/Data-Flow.md
- https://github.com/Serial-Studio/Serial-Studio/blob/v4.0.3/doc/help/Threading-and-Timing.md
- https://github.com/Serial-Studio/Serial-Studio/blob/v4.0.3/doc/help/Command-Line-Interface.md
- https://github.com/Serial-Studio/Serial-Studio/blob/v4.0.3/doc/help/SerialStudio-SDK.md

When API command behavior matters, enumerate the running v4.0.3 command registry instead of trusting stale prose documentation.

---

# 43. FINAL SHIP DEFINITION

This redesign is shipped only when all of the following are true:

```text
K1_SERIAL_STUDIO_OBSERVABILITY_V2 = PASS

PASS means:
- passive canonical project
- manual serial ownership
- two healthy source paths
- parser provenance intact
- workspaces semantically real
- compact useful Mission Control
- event timeline replaces giant LEDs
- heterogeneous mega-MultiPlots gone
- misleading FFT removed/reframed
- broken virtual transforms gone
- Historian evidence path intact
- immutable snapshot receipt works
- read-only plugin optional and isolated
- no dashboard surface claims to be verdict
```

Anything less is still implementation work.

