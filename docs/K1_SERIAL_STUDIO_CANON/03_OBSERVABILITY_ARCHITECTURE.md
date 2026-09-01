# K1 Serial Studio Observability Architecture

## 1. Permanent split

```text
                    K1 DEVICES
                        |
                  passive telemetry
                        v
              +--------------------+
              |   SERIAL STUDIO    |
              | observe / record   |
              | Historian / replay |
              +---------+----------+
                        |
          +-------------+-------------+
          |                           |
          v                           v
 read-only live analytics       frozen SQLite snapshot
  (Painter/plugin/Web)                  |
                                        v
                                offline Python scorer
                                        |
                                        v
                                  immutable receipt
```

Authoritative command/reply tests use:

```text
Serial Studio releases port
        |
        v
exclusive pyserial test harness
        |
        v
       K1
```

## 2. Operating profiles

### PROFILE A — PASSIVE_OBSERVE (canonical/default)

Purpose: ordinary dual-K1 observation and recording with minimum observer effect.

Requirements:
- no auto-execute actions;
- no repeating actions;
- no DUT writes;
- no output controls;
- no command-shuttle table;
- no `deviceWrite*` in project scripts;
- `autoReconnect=false`;
- Session Recording may be enabled;
- API may be enabled localhost-only for read-only analytics;
- read-only plugin allowed if fingerprinted.

### PROFILE B — ACTIVE_POLLING (optional explicit)

Purpose: obtain low-rate metrics not emitted passively.

Requirements:
- separate project/profile or clearly named configuration;
- operator action required to enable it;
- allowlisted commands only;
- poll rate justified;
- record that observer is active;
- never call this profile "passive";
- never use it while another process needs the port.

Recommended starting rule:
- FPS/health queries at ~1 Hz unless a specific engineering question requires faster polling.
- Do not poll duplicate event fields merely because they make the dashboard move.

### PROFILE C — AUTHORITATIVE_COMMAND_TEST

Serial Studio is not connected to the target port.

Pyserial/test harness owns it exclusively.

### PROFILE D — PASSIVE_DUAL_UART_AUDIO_REF (optional, separately admitted)

Purpose: attach an exact host Audio Reference capture to Bench/Main telemetry.

Requirements:
- source 2 is Serial Studio Pro Audio, never K1 parser data;
- an exact Pro-saved device/rate/format/channel binding is hash-frozen;
- Audio normalization is explicit; the first quantitative profile requires it off;
- playback is externally owned;
- host timestamps are `HOST_AUDIO_REFERENCE_TIME`, not device time;
- no AP/device delta without an explicit clock map;
- Mission Control remains one Web View with no native datasets;
- absent Source C does not degrade the default two-UART profile.

Current status: `BLOCKED_UNBOUND`, not a live or HIL claim.

## 3. Source health state machine

For each source report:

```text
DISCONNECTED
OPEN_NO_RX
RX_STALE
RX_HEALTHY
RX_MALFORMED
```

Do not collapse these to a single green "connected" state.

Minimum inputs:
- OS/Serial Studio connection state;
- raw-byte last-arrival time;
- raw-byte rate;
- parser frame rate;
- malformed-frame count if available.

## 4. Metric authority classes

Every metric belongs to one class:

### DEVICE_DIRECT
Value explicitly emitted by firmware.

### PARSER_DERIVED
Derived solely from bytes in the parser.

Examples:
- `record_kind`;
- `update_mask`;
- `host_parse_seq`.

### HOST_DIAGNOSTIC
Depends on host timing/acquisition.

Examples:
- host inter-arrival time;
- transport residual.
- Serial Studio Audio `Elapsed (s)` and Source C arrival/continuity facts.

### DISPLAY_DERIVED
For visual intuition only.

Examples:
- Painter rolling trace;
- dashboard-only effective BPM.

### OFFLINE_DERIVED
Authoritative analytical result calculated from frozen evidence.

## 5. Dataset semantic registry

The canonical project should not be the only place where dataset meaning lives.

Maintain a machine-readable registry with fields such as:

```json
{
  "title": "BPM",
  "semantic_name": "tempo_bpm",
  "authority": "DEVICE_DIRECT",
  "units": "bpm",
  "record_kinds": ["AP"],
  "range": "VERIFY_FROM_FIRMWARE",
  "freshness": "per AP update",
  "plot_class": "tempo",
  "fft_allowed": false,
  "evidence_use": true,
  "description": "Current AP tempo estimate."
}
```

Unknown range is preferable to an invented range.

The project generator/linter consumes this registry.
