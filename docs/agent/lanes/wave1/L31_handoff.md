STATUS: FAIL
CLAIM: `docs/agent/HANDOFF.md` is a C1-serial snapshot that contradicts `AGENTS.md` D22 on HOST work: HANDOFF stops streaming/Demucs/Titan and defers student until after C1; AGENTS opens those HOST lanes now. Shared HARD FAILs (15 min, cadence CLOSED, no 8 s loop, SS observe-only, C1 OPEN) agree. AGENTS + D22 win.
EVIDENCE: HANDOFF L17–18 `only then student/deployment`; L26 `Streaming student STOPPED`; L35 `Demucs / Titan STOPPED`; L90 `Still no Demucs`. AGENTS L35 D22 HOST OPEN; L47 streaming HOST-unblocked; L50 Demucs HOST OPEN; L54 Titan prep OPEN; L26 freeze only after `SELECTION_GATE.md` (not C1).
COMMAND: not executed; L31 is source-read only. Do not play audio. Do not USB. Do not edit HANDOFF or AGENTS from this lane.
METHOD_RISK: HOST-ONLY. Compared the two files on disk. No silicon, no player, no flash.
NEXT: Patch HANDOFF to D22 (streaming HOST-ok, Demucs HOST-ok, Titan docs-ok, freeze = SELECTION_GATE not C1-auto). L32 owns D20–D22 vs AGENTS. Cadence stays CLOSED.
PROOF: Same-song 15 min (HANDOFF L5 / AGENTS L19), cadence CLOSED (HANDOFF L8 / AGENTS L53), C1 one-song look (HANDOFF L87 / AGENTS L51), SS observe-only (HANDOFF L32 / AGENTS L52) match. Sequence + STOPPED vs OPEN do not.
TEST: none. Contradiction is line-level; no pytest in this lane.
DOCTRINE: AGENTS.md + Amendment 001 + D22 govern research sequence. Dated HANDOFF does not override. D21 HARD FAIL still binds both.
AUDIO: none played.
