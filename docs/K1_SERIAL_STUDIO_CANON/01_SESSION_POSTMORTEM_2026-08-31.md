# K1 Serial Studio Integration — Session Postmortem

**Incident window:** 2026-08-31 → 2026-09-01  
**System:** K1 Main RPL + K1 Bench, Serial Studio Pro v4.0.3  
**Outcome:** observability role retained; command-shuttle role rejected; dashboard architecture found substantially under-engineered; permanent guardrails defined.

---

# 1. Executive summary

The initial Serial Studio discovery was sound.

The tool proved genuinely useful as:
- a dual-device telemetry acquisition surface;
- a live visualization environment;
- a Historian/SQLite recorder;
- a raw-byte archive;
- a replay system;
- a bridge to offline Python scoring.

The failure came from **scope inflation**.

A capability that had been proven in one direction:

```text
K1 -> Serial Studio -> dashboard/Historian
```

was prematurely promoted into an unproven bidirectional control architecture:

```text
cadence test -> TCP API -> Serial Studio -> K1 command/reply
```

That new role became a critical dependency before it had a single successful end-to-end proof.

The live Serial Studio application was then mutated repeatedly while connected to real K1 hardware. Multiple agents/subtasks touched one stateful GUI/API surface. The UARTs were disconnected/reconnected. The later sessions became RX-silent even though the operating system ports existed and Serial Studio showed them as open.

The correct architectural rollback was:

```text
Serial Studio = observe / record / replay
pyserial      = command/reply silicon tests
device clocks = timing authority
Python        = verdict
```

This rollback preserved all valuable observability work while removing the dangerous unproven dependency.

---

# 2. What genuinely worked

## 2.1 Dual-source acquisition was real

A known-good Serial Studio session captured live Main telemetry. The Historian accumulated tens of thousands of raw source-1 rows. Parsed `[AP]` and polled values were visible. Device clocks advanced. This established that Serial Studio could be a useful K1 laboratory instrument.

## 2.2 Historian architecture was valuable

The Session Database provided:
- parsed raw values;
- parsed transformed/final values;
- raw driver bytes;
- session metadata;
- an embedded project JSON snapshot;
- replay;
- SQLite access from Python.

That remains a high-leverage capability.

## 2.3 Parser provenance work was correct

Parser v1.1 introduced:
- `record_kind`;
- `update_mask`;
- `host_parse_seq`.

These fields solved an important problem: Serial Studio displays last-known values, but last-known values are not necessarily fresh measurements.

The parser correctly refused to fabricate fields that were not present on the wire.

## 2.4 Frozen database snapshots were the correct evidence mechanism

The live SQLite database is WAL-backed and mutable. Hashing the growing `.db` file is not an immutable run identity.

The corrected process:
1. creates a transactionally consistent SQLite backup snapshot;
2. closes it;
3. hashes the snapshot;
4. produces a receipt tied to that frozen artifact.

This distinction must remain permanent.

## 2.5 Offline Python remained the correct statistical authority

Serial Studio transforms and widgets are useful for visualization and low-cost live derivations. They are not the correct authority for p95/p99, regression, gate scoring, or formal experiment verdicts.

---

# 3. Failures and lessons, in chronological/causal order

## F-001 — Feature success was mistaken for architectural authority

**Failure:** Serial Studio was good at recording, so it was assumed it should also become the exclusive USB command owner.

**Why wrong:** observation and command transport are separate proof obligations.

**Permanent lesson:** never promote a support tool into the critical path because an adjacent capability worked.

**Guardrail:** architecture promotion requires a named end-to-end proof receipt before downstream code may depend on the new path.

---

## F-002 — Cadence was wired to an unproven shuttle

**Failure:** cadence tooling was modified to rely on a Serial Studio shuttle before one typed command/reply roundtrip had passed.

**Risk:** a real silicon run could have been invalidated by transport failure.

**Permanent lesson:** downstream consumers must remain fail-closed until the exact dependency they require has a PASS receipt.

**Guardrail:** `SERIAL_STUDIO_NOT_TRANSPORT` is architecture, not a temporary hold.

---

## F-003 — Wrong scripting surface/API assumptions

**Failure:** early control-script work used APIs inappropriate to that scripting surface and experimented around response capture.

**Key discovery:** `deviceWriteAndWait(...)` existed as the purpose-built per-source raw request/reply primitive, whereas latest-frame polling was the wrong abstraction for replies under continuous `[AP]` traffic.

**Permanent lesson:** read the exact versioned implementation/API surface before inventing a bridge.

**Guardrail:** Serial Studio version is pinned; API behavior is derived from v4.0.3 docs/source, not memory or current master.

---

## F-004 — `io.getLatestFrame` / latest-value reasoning was unsuitable for command replies

**Failure:** transient replies could be overwritten by later continuous telemetry.

**Permanent lesson:** latest-value storage is a dashboard abstraction, not a reliable request/reply mailbox.

**Guardrail:** command/reply transport is outside Serial Studio for K1 authoritative tests.

---

## F-005 — "first non-empty reply" is unsafe under continuous telemetry

**Failure mode:** if a reply primitive completes on the first bytes seen, ordinary `[AP]` traffic can satisfy the wait before the command's actual response arrives.

**Permanent lesson:** completion must be matched to a command-specific marker if a request/reply mechanism is ever tested.

**Guardrail:** no generic newline/first-byte completion for command proof.

---

## F-006 — Too many writers touched one live instrument

**Failure:** multiple agents/subtasks interacted with one Serial Studio instance/API/project.

**Effects:**
- shared state became difficult to reason about;
- control tables/registers multiplied;
- project state changed under observation;
- it became unclear which writer caused which live behavior.

**Permanent lesson:** a stateful GUI instrument gets exactly one live writer.

**Guardrail:** `ONE_LIVE_INSTRUMENT_OWNER = true`. Parallel agents may perform read-only/offline audits only.

---

## F-007 — The instrument was modified while it was being used

**Failure:** parser/project/control changes were applied to the same live application connected to real DUTs.

**Permanent lesson:** configuration development and authoritative measurement are distinct phases.

**Guardrail:** no live project mutation during an authoritative capture. Build offline, lint, dry-run, replay/simulate, then connect.

---

## F-008 — Reconnect changed the hardware/CDC state

**Failure:** reconnecting real UART sources changed the previously working condition.

A working session had shown ESP-ROM reset/boot behavior on connection. Later API reconnects opened ports without producing the same device reset behavior.

**Permanent lesson:** "same project + same port path" does not guarantee the same native-USB/CDC device state.

**Guardrail:** reconnect is a state-changing experimental action, not a harmless UI operation.

---

## F-009 — "Port open" was mistaken for "receive path healthy"

**Failure:** both macOS serial devices existed and Serial Studio held them, yet the Historian recorded zero raw bytes.

**Permanent lesson:**

```text
PORT EXISTS != PORT OPEN != RX HEALTHY != DEVICE ALIVE
```

These are separate states.

**Required live indicators:**
- last RX age;
- raw bytes/s;
- parsed frames/s;
- Historian raw-byte delta;
- parser progression.

---

## F-010 — Host TX enqueue was mistaken for device delivery

**Failure:** `QSerialPort::write()` accepting bytes was described too strongly as healthy TX.

**Permanent lesson:**

```text
host write accepted/queued != bytes reached firmware != firmware parsed command
```

**Guardrail:** receipts distinguish:
- host write accepted;
- raw reply observed;
- device acknowledgement observed.

---

## F-011 — Zero-byte reply capture was initially treated too narrowly

**Discovery:** `deviceWriteAndWait` returned `bytesRead=0`, and Historian also showed no incoming source bytes during the interval.

This proved the problem was not a marker mismatch. RX itself was dead.

**Permanent lesson:** use independent evidence paths to classify the failure before changing code.

**Guardrail:** every live failure is classified before any repair attempt.

---

## F-012 — Retry culture was dangerous

**Failure pattern:** repeated changes/attempts threatened to turn one clear failure into an archaeology exercise.

**Corrected behavior:** one authorized attempt; on fail, stop and produce a receipt.

**Permanent lesson:** one proof obligation per live attempt.

**Guardrail:** no automatic retries for hardware authority proofs unless explicitly designed into the experiment before the first attempt.

---

## F-013 — Support-tool archaeology began consuming the research programme

**Failure:** Serial Studio transport debugging started competing with Gate C/cadence work.

**Permanent lesson:** a support tool must never become the project.

**Guardrail:** every instrumentation task must answer: "Does this directly unblock the active research gate?" If no, backlog it.

---

# 4. Dashboard/backend audit failures

After the transport role was demoted, the actual `.ssproj` was audited. This revealed a second class of failures: **feature enablement without information architecture**.

## F-014 — Heterogeneous MultiPlot

One MultiPlot combined:
- BPM;
- confidence;
- Boolean states/events;
- AGC;
- peak;
- energy;
- novelty.

These values do not share units, scale, or semantic meaning.

**Lesson:** MultiPlot is for comparable channels, not "all the things."

**Guardrail:** MultiPlot groups must share semantic class/range/units or be explicitly normalized.

---

## F-015 — Oscilloscope Sweep mode used on unrelated application metrics

The top-left graph was configured with Sweep mode, causing traces to march and reset.

Sweep/trigger is valuable for repeatable waveforms. It was not justified for a soup of K1 application metrics.

**Lesson:** advanced widget capability is not automatically useful.

**Guardrail:** Sweep mode requires an explicit trigger hypothesis and compatible signal.

---

## F-016 — FFT existed without a named engineering question

`peak_scaled` had FFT + Waterfall settings. The display looked authoritative but lacked semantic framing.

**Correct interpretation:** it is an envelope-modulation spectrum, not an audio spectrum.

**Lesson:** every FFT must declare:
- exact source metric;
- exact fresh sampling cadence;
- window duration;
- frequency resolution;
- engineering hypothesis;
- whether it is diagnostic or evidential.

**Guardrail:** FFT is disabled unless the dataset is in an explicit allowlist with a declared cadence.

---

## F-017 — Blanket Main "4 Hz" sampling assumption

Main datasets inherited 4 Hz FFT settings even though their values come from mixed `[AP]`, event-status and poll paths.

**Lesson:** a group/source does not have one meaningful sample rate when individual metrics update on different record kinds.

**Guardrail:** sampling cadence is a per-metric/freshness property.

---

## F-018 — LED Panel wasted space and conflated state with event

Huge indicators were used for:
- Lock;
- Beat;
- Onset;
- Bass onset;
- Silence.

`Lock` and `Silence` are persistent states. Beat/Onset/Bass are transient events.

**Lesson:** state and event need different visual grammar.

**Replacement:** compact annunciators for states; temporal event raster for events.

---

## F-019 — Named workspaces were shells

Workspaces called Timing, Audio/AP and Renderer pointed at essentially the same generic Bench MultiPlot. "Dual-device sync" was not an actual dual-device comparison surface.

**Lesson:** a workspace name is not architecture.

**Guardrail:** duplicate workspace widget-reference sets are rejected unless explicitly allowed.

---

## F-020 — Dangling/obsolete project references

The project accumulated group/workspace/widget IDs that no longer corresponded cleanly to the current group model.

**Lesson:** GUI-generated JSON still needs structural linting.

**Guardrail:** every workspace `groupId` must resolve; IDs must be unique; dead references fail CI.

---

## F-021 — `unused_slot_*` became permanent project debris

Unused parser slots existed as datasets; one even had Waterfall enabled.

**Lesson:** dead fields create false affordances and accidental future dependencies.

**Guardrail:** dataset titles matching `unused_slot` fail the canonical project linter.

---

## F-022 — Virtual transforms were wired incorrectly

Serial Studio virtual datasets receive `value=0`; they must read dependencies through dataset/table APIs.

The project's virtual timing transforms operated on their own `value` input as though it were a sibling metric.

**Lesson:** transforms must be written to the documented execution model, not intuition.

**Guardrail:** a virtual transform without an explicit dependency accessor fails lint unless an override annotation is present.

---

## F-023 — Renderer workspace existed without renderer telemetry

A "Renderer" workspace was created despite the wire not providing the actual renderer metrics needed to justify it.

**Lesson:** never name a workspace after data you do not possess.

**Guardrail:** every workspace declares its question and required fields. Missing fields mean the workspace is omitted, not filled with unrelated telemetry.

---

## F-024 — Instrument health was absent from the front page

When RX died, the dashboard did not visibly scream that raw bytes had stopped.

**Lesson:** an observability dashboard must observe the observer.

**Required metrics:**
- last raw RX age;
- raw bytes/s;
- parsed frame rate;
- source freshness;
- Historian recording state;
- session identity;
- optional plugin/scorer health.

---

## F-025 — Polling made "observability" active by default

Both sources auto-polled every 250 ms for event status/FPS/LED FPS.

**Problems:**
- observer effect;
- duplicate fields;
- mixed freshness cadences;
- hidden TX activity;
- harder evidence interpretation.

**Lesson:** passive observation must be the default. Active polling is a separate explicit profile.

---

# 5. Serial Studio platform insights that must be retained

## P-001 — Multi-source parsing is valuable

Each source has an independent parser and source identity. This is a good fit for dual K1 observation.

## P-002 — Session DB is the primary archive

It records raw/final readings, raw bytes, table snapshots, metadata and embedded project JSON.

## P-003 — Replay uses stored parsed values

Raw bytes remain archived, but replay does not re-parse them. Parser changes therefore do not retroactively change old sessions.

## P-004 — CSV is secondary

0 ms row interval gives one row per received frame, but CSV is less rich than Historian for provenance/replay.

## P-005 — Painter is ideal for K1-specific visual instruments

Use it for:
- event rasters;
- compact state strips;
- K1 topology displays;
- freshness indicators;
- instrument mimics.

Do not use Painter output as evidence.

## P-006 — Alarm bands can provide actual annunciation

Use warnings/critical states for:
- stale RX;
- FPS outside a proven contract;
- drop counts;
- queue health;
- other thresholded system conditions.

Thresholds must come from evidence/contracts, not guesswork.

## P-007 — gRPC is the preferred high-rate plugin feed

Use port 8888 for read-only live analytics. TCP/JSON remains useful for command/query tooling.

## P-008 — API prose can drift

The running command registry is authoritative. Enumerate it from the running version instead of assuming documentation command names are perfect.

## P-009 — Extension repositories are the right packaging mechanism after stabilization

Serial Studio Pro supports private/local repositories for:
- frame parsers;
- project templates;
- plugins;
- themes.

Do not package unstable experiments prematurely.

## P-010 — Plugin state and auto-relaunch are hidden state

A plugin that was running can be relaunched automatically later.

Therefore authoritative receipts must include:
- enabled/running plugin list;
- plugin versions;
- plugin configuration fingerprint.

## P-011 — Project folders/workspaces are powerful but semantic

Use them to encode operator questions, not to make the tree look impressive.

---

# 6. Process lessons beyond Serial Studio

## A-001 — Map vs territory

"Connected", "open", "green", "PASS" and "widget visible" are representations.

Always identify the physical/causal claim behind them.

Examples:
- green connection icon = host software believes driver open;
- raw byte delta = device->host traffic actually observed;
- device sequence = device-side production evidence;
- plot line = last-known display state.

## A-002 — Model selection: use the simplest authority that satisfies the job

Serial Studio is excellent at observation. Pyserial is simpler and more trustworthy for exclusive command/reply silicon work.

Do not route a simple job through a more complex layer because that layer already exists.

## A-003 — OODA: observe before acting

On failure:
1. Observe independent evidence.
2. Orient/classify the fault layer.
3. Decide one discriminating test.
4. Act once.
5. Stop and update the model.

Do not patch first and investigate afterward.

## A-004 — Steel-man the boring explanation

Before inventing parser bugs, marker bugs, plugin bugs or timing bugs, check:
- is raw RX present at all?
- is the source actually fresh?
- did the port re-enumerate?
- did the project change?
- is the metric held rather than new?

## A-005 — Red-team every instrumentation promotion

Before making a new path authoritative, ask:
- What happens if it silently drops data?
- What independent evidence would expose that?
- Can it change the DUT?
- Can it reconnect/reconfigure behind us?
- Is its clock authoritative?
- Can a dashboard hold a stale value and look healthy?
- What is the fail-closed behavior?

---

# 7. Final root-cause statement

The session was not wasted because Serial Studio was a bad tool.

The session was expensive because:

> **A real observability success was overgeneralized into an unproven transport architecture, then a stateful live instrument was mutated by too many writers without machine-enforced semantic guardrails.**

The permanent response is therefore not "never use Serial Studio."

It is:

> **Use Serial Studio aggressively where it is strongest, keep authority boundaries explicit, and mechanically prevent the project/configuration/process mistakes that allowed the support tool to become a source of ambiguity.**
