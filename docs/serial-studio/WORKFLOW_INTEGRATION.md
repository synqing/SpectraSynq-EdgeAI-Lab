# Serial Studio workflow integration

This is the common contract for hardware and firmware evaluation. It does not authorise a live device run from this repository.

## Workflow adapters

| Workflow | Live owner | Serial Studio integration | Verdict owner |
| --- | --- | --- | --- |
| Passive product observation | Serial Studio | live raw, parser, Historian, Mission Control | named offline profile or physical gate |
| Dual-device comparison | Serial Studio | two source-qualified streams; never align solely by host arrival | offline comparison profile |
| Build and flash | verified flash tool | pre/post identity and settled post-flash observation | build/identity gate |
| Interactive probe | probe runner, exclusive | SS releases CDC; transcript is imported into the same evidence bundle | probe scorer |
| Calibration | calibration harness, exclusive | passive before/after capture; SS never initiates calibration | calibration contract |
| Acoustic bench | playback/witness controller | run/stimulus manifest joins Historian by session ID | acoustic/evaluation profile |
| Audio Reference witness | external playback owner | optional Pro Audio Source C or closed host reference; never K1 parser slots | hash-bound offline Audio Reference profile |
| LED-buffer/pixel dump | dump runner or passive telemetry | telemetry joined by device time/markers | pixel scorer |
| Scope/logic/power/camera | instrument owner | raw vendor artefact and clock map join the bundle | named instrument/profile |
| MIR/evaluation | no hardware owner | normalised fresh-only rows from closed evidence | evaluation suite |
| CI | no hardware owner | schema, parser, project, bridge, receipt, replay, visual fixtures | contract gates |

## Session lifecycle

### Preflight

1. Name the engineering question, capture profile, and scoring profile.
2. Bind the target by chip identity and USB serial, never by port path alone.
3. Bind firmware git/environment/epoch/image, mic route, LED route, rig, calibration, stimulus, witness, and power.
4. Hash the project, parser, catalogue, rig, and scoring profile.
5. Refuse a planned same-song cumulative duration above 900 seconds.

### Settle

Require both expected sources, non-zero raw ingress, fresh parser publication, progressing Historian rows, no configuration drift, monotonic device clocks where available, and no reset. A successful API response is not source liveness.

### Capture

Freeze the project, parser, source bindings, fixture, calibration, and output route. Record every ownership transition and stimulus marker. Monitor source age, raw bytes/s, parser rate, update-mask freshness, sequence gaps, recording progression, device-time continuity, reset epochs, and song exposure.

### Close

Stop playback first. End recording. Release the endpoint. Recheck identity. Create a SQLite backup using `sqlite3.Connection.backup()`, close it, run `PRAGMA integrity_check`, and hash the closed file. A failed run is preserved as quarantined evidence with explicit reasons.

### Offline handoff

Bundle the run manifest, rig, identities, raw bytes, closed SQLite snapshot, project/parser/catalogue, normalised fresh-only rows, action timeline, witness artefacts, instrument receipt, and scoring profile. The instrument receipt proves capture integrity, not product correctness.

## Profiles

| Profile | Device TX | Purpose |
| --- | ---: | --- |
| `PASSIVE_DUAL_UART` | 0 | Bench/Main comparison; Audio Reference optional/absent |
| `PASSIVE_DUAL_UART_AUDIO_REF` | 0 | Bench/Main plus exact host Audio capture binding; currently `BLOCKED_UNBOUND` |
| `EXCLUSIVE_PROBE` | runner only | command/reply, buffered dumps, timing experiments |
| `EXCLUSIVE_CALIBRATION` | calibration harness only | explicit silence-controlled calibration |
| `REPLAY_FORENSICS` | 0 | historical replay and offline scoring |

`OBSERVE_HEALTH_POLLED` is not admitted. Its command set, rate, response cadence, egress ledger, and observer effect must first be qualified against a named threshold set. Until then, missing passive health telemetry displays `NOT INSTRUMENTED`.

The versioned v2 session and evidence-bundle contracts make instrumentation
conditional on the capture profile. An exclusive probe/calibration bundle does
not require Serial Studio evidence; passive UART profiles do. Audio Reference is
optional unless the exact audio profile names it as required. If optional
evidence is present but malformed or hash-invalid, validation still fails.

## Required future firmware hooks

These are append-only firmware-lane requirements, not fields this repository may invent:

- boot/session identity: telemetry schema, build SHA/environment/epoch, chip ID, boot ID;
- every authoritative record: `device_us` and device `frame_seq`;
- low-rate health: reset, drop, queue, I2S and error counters;
- calibration provenance: namespace/profile identity, source, validity and route;
- probe-only timings behind compile guards with telemetry-off/on perturbation proof.
