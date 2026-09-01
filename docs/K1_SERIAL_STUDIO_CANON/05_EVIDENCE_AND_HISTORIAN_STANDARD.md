# K1 Serial Studio — Evidence and Historian Standard

## 1. Never hash the growing live database as final evidence

A hash of the active WAL-backed DB is a live fingerprint only.

Terminology:

```text
LIVE_DB_FINGERPRINT != EVIDENCE_SNAPSHOT_SHA256
```

## 2. Authoritative snapshot procedure

1. Identify the target session.
2. Use SQLite backup API to create a consistent standalone snapshot.
3. Close snapshot.
4. Hash closed snapshot.
5. Generate receipt against that exact snapshot.
6. Never mutate the snapshot afterward.

## 3. Receipt minimum fields

- Serial Studio version/build;
- project title;
- canonical `.ssproj` SHA256;
- embedded `sessions.project_json` SHA256;
- project drift status;
- source IDs/titles/devices;
- session ID;
- session start/end;
- snapshot path/name;
- snapshot SHA256;
- readings count by source where possible;
- raw byte row/count by source;
- first/last device clock per source;
- first/last host parser sequence;
- detected clock regressions/resets;
- freshness counts by metric/record kind;
- active profile: PASSIVE_OBSERVE or ACTIVE_POLLING;
- running plugin list/version/hash;
- scorer version/hash if a gate result is produced;
- explicit statement whether recording was still active at snapshot time.

## 4. Freshness rule

If a parsed frame does not update metric X, that frame is not a sample of X.

Use:
- `record_kind`;
- `update_mask`;
- metric's declared record-kind contract.

Never compute p95/p99/correlation from held values as though they were new observations.

## 5. Parser provenance rule

Parser must not invent:
- firmware SHA;
- run ID;
- device sequence;
- AP timing;
- drop count.

If host metadata is attached externally, label it `HOST_METADATA`.

## 6. Timing rule

Use:
- device clocks/counters for device temporal claims;
- host monotonic time for acquisition/transport diagnostics.

Do not claim cross-device sub-ms sync from host UART arrival timestamps.

## 7. Screenshots and reports

Screenshot:
- communication;
- operator awareness;
- bug illustration.

Not evidence.

Session report:
- convenient summary of recorded session;
- not a substitute for raw bytes/frozen DB when the verdict is load-bearing.

## 8. Replay caveat

Historian replay uses stored parsed values. It does not re-run a newer parser against archived raw bytes.

Therefore:
- old session meaning is tied to embedded project/parser snapshot;
- parser upgrades do not retroactively fix old readings;
- raw bytes may be separately reprocessed by explicit offline tooling if desired, but that is a new derived analysis with its own provenance.

## 9. Host Audio Reference evidence

A host Audio Reference is a separate authority domain. Its bundle must bind the
reference bytes, strict Audio CSV, declared sample representation, Source C
device/rate/format/channel identity, validator version, scoring profile and all
SHA-256 values. Host Audio `Elapsed (s)` is
`HOST_AUDIO_REFERENCE_TIME`.

Human-listenable reconstruction is diagnostic only. Quantitative evidence may
not remove DC, independently normalise channels, dither, clip, skip malformed
rows, replace non-finite values or infer sample format from magnitude.

The receipt must explicitly deny acoustic-delivery, K1 microphone/PDM/PCM,
device-time-alignment and product-verdict claims. Reference-to-device timing
requires a separate clock-map artefact with method and uncertainty.
