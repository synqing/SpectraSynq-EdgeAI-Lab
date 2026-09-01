## Serial Studio / K1 observability — standing doctrine

- Serial Studio is **observe / record / Historian / replay**, not K1 command transport authority.
- Any authoritative silicon test needing interactive command/reply owns that K1 USB-CDC **exclusively**; Serial Studio must release it first. No two owners on one CDC.
- Canonical Serial Studio operation is **PASSIVE_OBSERVE**: no automatic DUT writes, no hidden polling, no command shuttle, no `deviceWrite*`, no auto-reconnect.
- Exactly **one writer** may mutate the live Serial Studio app/project/API at a time.
- Never edit/reconfigure/reconnect the live instrument during an authoritative recording.
- `Connected/Open` is not RX health. Require raw-byte arrival + parser progression.
- Host write enqueue is not device delivery.
- Host arrival timestamps are transport diagnostics, not cross-device timing authority.
- Last-known values are not fresh samples. Preserve `record_kind`/`update_mask`; offline stats use fresh observations only.
- Live Historian DB hash is a fingerprint only. Final evidence uses a frozen SQLite backup snapshot + SHA256 + receipt.
- Preserve historical v1 `.ssproj`; build/lint v2 separately.
- Every changed canonical `.ssproj` must pass `tools/serial-studio/guardrails/lint_ssproj.py --profile passive`.
