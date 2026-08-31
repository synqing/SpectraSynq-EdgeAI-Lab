---
abstract: "L29 HOST pytest inventory 2026-08-31: 118 passed / 0 failed / 0 skipped / 0 errors. CPython 3.12.11. No USB-CDC. No silicon."
---

STATUS: PASS
CLAIM: HOST pytest inventory 118 passed / 0 failed / 0 skipped / 0 errors / 0 xfailed / 0 xpassed / 0 deselected; 16 files under tests/; no live USB; no ffplay; no silicon.
EVIDENCE: `.venv/bin/python3` is CPython 3.12.11, pytest 9.1.1. Collect 118 == run 118. Per file: gate_c_cadence 24, p3c_visual_engine 20, onset_align 11, share_student 10, source_oracle 10, gate_c0v2 9, serial_studio 8, p3c_quant 8, visual_modulate 4, labels/mir_registry/ruhmi_workflow/semantic_trace/shapes/splits/teachers 2 each. USB: `rg usbmodem|/dev/cu tests` empty. One skip gate (`test_scan_musdb_is_song_level_when_present`) did not fire. Serial Studio tests are localhost mocks + `lsof` on `/dev/does-not-exist-ss-refuse-test`, not CDC.
COMMAND: `cd /Users/spectrasynq/SpectraSynq-EdgeAI-Lab && .venv/bin/python3 -m pytest -q --tb=no --disable-warnings -rs`
METHOD_RISK: HOST-ONLY. No pytest marker for USB/silicon; none collected open `serial.Serial` or `/dev/cu.usbmodem*`. Cadence CLOSED. This lane did not open CDC or Serial Studio. Suite is not a silicon receipt.
NEXT: none for L29. Cadence CLOSED. L38 owns exclusive-port tests; L39 owns Serial Studio vs D19. Do not replay this suite against silicon. Do not USB-test.
PROOF: 9+24+2+2+11+8+20+2+2+8+2+10+10+2+2+4 = 118 collected == 118 passed. CLI exit 0 (~12.6s). Plugin re-count: TESTSCOLLECTED=118 TESTSFAILED=0 STAT_passed=118 STAT_skipped=0 STAT_error=0.
TEST: all collected tests ran; no xfail/xpass; ONNX DeprecationWarning on `tests/test_shapes.py::test_onnx_export_avoids_reducemean` is not a fail. Slowest: share_student buried-vs-solo 5.52s, onset_align 2.21s, serial_studio send_line 1.73s.
DOCTRINE: D22 L29; AGENTS.md no USB multiplex; SAME_SONG_LOOP_MAX_15MIN unused (no audio).
AUDIO: none played.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:grok | Wave 2 re-run: 118 passed / 0 failed / 0 skipped on CPython 3.12.11; no CDC. |
| 2026-08-31 | agent:grok | Wave 1: 118 passed / 0 failed. |
