# Passive Observe Checklist

Use before any normal K1 Serial Studio recording.

- [ ] Correct canonical v2 project loaded.
- [ ] v1 historical project not edited.
- [ ] `.ssproj` linter PASS under `--profile passive`.
- [ ] Serial Studio Pro version recorded.
- [ ] API external connections disabled; localhost-only if API is needed.
- [ ] No command shuttle/control-write script present.
- [ ] No `k1_gate` table.
- [ ] No auto-start polling actions.
- [ ] `autoReconnect=false` on both sources.
- [ ] One live Serial Studio owner.
- [ ] No pyserial process owns either CDC.
- [ ] Connect intentionally.
- [ ] Within seconds, verify raw RX bytes for each source.
- [ ] Verify parser progression for each source.
- [ ] Verify last RX age visible.
- [ ] Verify Historian state and session ID.
- [ ] If either source is open but raw RX=0: STOP and classify `OPEN_NO_RX`.
- [ ] Do not fix dashboard/config while this recording is authoritative.
- [ ] At end, create frozen SQLite snapshot.
- [ ] Generate receipt and SHA256.
- [ ] Record project/extension/plugin fingerprints.
