STATUS: PASS
CLAIM: BoseSession 15 min cap present; SAME_SONG_LOOP_MAX_S == 900.
EVIDENCE: scripts/gate_c0v2_silicon.py:69 `SAME_SONG_LOOP_MAX_S = 15 * 60` (equals 900).
COMMAND: not executed; L19 is source-read only. Do not play audio.
METHOD_RISK: HOST-ONLY. Cap is wall-clock in BoseSession; this lane did not start ffplay.
NEXT: none for L19. Cadence CLOSED. Keep D21 HARD FAIL.
PROOF: 15*60=900. BoseSession uses the const at assert_alive L187, _expired L196, _run deadline L199; kill on expiry L211/L219/L231.
TEST: tests/test_gate_c0v2.py::test_same_song_loop_max_is_fifteen_minutes exists (L218–222: assert SAME_SONG_LOOP_MAX_S == 15 * 60).
DOCTRINE: D21 SAME_SONG_LOOP_MAX_15MIN; AGENTS.md HARD FAIL; no 8 s room loop this lane.
AUDIO: none played.
