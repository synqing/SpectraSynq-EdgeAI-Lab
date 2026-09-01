# ADR-001: Serial Studio observability sidecar

Status: accepted by Captain, 2026-09-01

## Decision

Serial Studio Pro is the standard live-observation, Historian, replay, and forensic sidecar for applicable SpectraSynq hardware and firmware workflows.

It is not the command, flash, calibration, clock, statistical-verdict, or perceptual-verdict authority. Integration into every workflow means that each run either produces a passive live Serial Studio capture or a replayable post-run bundle. It does not mean that Serial Studio shares a command CDC with another process.

The operating states are:

1. `PASSIVE_OBSERVE`: Serial Studio owns the telemetry endpoint, records raw and decoded data, and emits zero device-bound bytes.
2. `RELEASED_FOR_TEST`: Serial Studio releases the endpoint. One identity-bound runner owns command/reply exclusively and records its transcript.
3. `REPLAY_FORENSICS`: no hardware connection; closed evidence is replayed and inspected.
4. `DEDICATED_TELEMETRY`: future only, after a physically or logically separate telemetry channel is proven.

The former `GATE` profile, `k1_gate` table, command shuttle, transmit actions, and `open_k1_serial()` API are not part of v2.

The application egress gate covers K1's passive UART project. Request/response drivers such as Modbus, S7, EtherNet/IP, OPC UA, IEC-104, and MQTT may emit protocol traffic merely to acquire data. They are not admitted under a literal zero-egress profile until connection itself is refused or separately qualified. The v2 linter therefore requires passive UART sources.

## Why the old Cadence path is closed

D20 retired one particular Cadence runner and its already-consumed cells. That was a containment decision after the workflow monopolised the room, mixed transport ownership, and repeated a short stimulus. It was not a claim that latency/cadence evidence is impossible in principle.

If a future product decision genuinely needs cadence evidence, it receives a new named decision, capture profile, scoring profile, stimulus budget, identity-bound transport lease, and evidence bundle. The retired runner and closed cells are not reopened. Serial Studio participates through passive capture when a separate telemetry path exists, or through deterministic release and replay when it does not.

## Data and authority flow

```text
build / flash / runner ----> exclusive transport lease ----> DUT mutation
          |                                                   |
          +---------------- run manifest ---------------------+
                                                              |
DUT telemetry -> Serial Studio -> parser/freshness -> Historian snapshot
                                     |                 |
                                     +----- cockpit ---+
                                                       |
rig + calibration + witness + identity receipts -------+
                                                       |
                                              evidence bundle
                                                       |
                                             named offline scorer
```

Device clocks and counters remain device authority. Host arrival time is a transport diagnostic. The dashboard is operational awareness. A closed SQLite snapshot plus its manifest is acquisition evidence. A named offline scorer owns a machine verdict. Captain owns only genuinely perceptual acceptance that cannot be instrumented.

## Kill conditions

A capture is quarantined immediately when any of the following is true:

- `PASSIVE_OBSERVE` produces any outbound byte.
- Device identity is missing, duplicated, swapped, or changes across the run.
- The expected source is absent, stale, reset without a new epoch, or contributes zero raw bytes.
- Parser publication, Historian progression, project hash, or parser hash disagrees with the run manifest.
- An exclusive lease conflicts with another owner.
- A live/WAL database hash is presented as final evidence.
- The same song reaches 900 cumulative seconds in the room.

## Consequences

v1 remains frozen by hash for replay compatibility. v2 is separately named, generated, linted, write-free, and source-controlled. Polling is not silently reduced to a guessed rate: it is absent from `PASSIVE_OBSERVE`. A later active-probe project is admissible only after its exact commands and observer effect are qualified by a named contract.
