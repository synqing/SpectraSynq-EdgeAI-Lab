---
abstract: "L31: HANDOFF.md vs AGENTS.md. Shared HARD FAILs MATCH (D21 15 min, Cadence CLOSED, C1 OPEN, SS observe-only). HOST serialisation CONTRADICTS D22. AGENTS+D22 win."
---

# L31 — HANDOFF vs AGENTS

**HARD FAIL (`SAME_SONG_LOOP_MAX_15MIN`).** Same song/clip looped >15 min → agent dies. Docs-only. No USB. No ffplay. Cadence CLOSED.

STATUS: FAIL (HOST serialisation). HARD FAILs MATCH.
CLAIM: `docs/agent/HANDOFF.md` is a 2026-08-31 **C1-serial snapshot**. It agrees with `AGENTS.md` on D20 Cadence CLOSED, D21 15 min kill, C1 OPEN (one Captain song, no 8 s loop), D19 Serial Studio observe/record. It **contradicts D22** by stopping HOST student/Demucs/Titan work until after C1. `AGENTS.md` + Amendment 001 + D22 win. Dated HANDOFF does not override.
EVIDENCE: HANDOFF L17–18, L26, L33, L35, L90, L97 vs `AGENTS.md` L19, L26, L35–54; `docs/DECISIONS.md` D20–D22; roster `docs/agent/PARALLEL_LANES.md` L31.
COMMAND: none. Source-read only. Do not edit HANDOFF or AGENTS from this lane. Do not play audio. Do not open `/dev/cu.usbmodem*`. Do not resume `gate_c0_cadence_silicon.py`.
METHOD_RISK: HOST-ONLY. Compared the two files on disk (plus D20–D22 as tie-break). No silicon, no player, no flash. `Agents.md` is the on-disk filename; HANDOFF cites `AGENTS.md` — same file on this host.
NEXT: Patch HANDOFF to D22: HOST lanes OPEN now (streaming sketches, Demucs HOST teacher docs, Titan prep docs); freeze trigger = `SELECTION_GATE.md` (C1 necessary, not a programme lock); add D22 to read order. L32 owns D20–D22 vs AGENTS. Cadence stays CLOSED. Keep D21 kill.

## MATCH — do not treat as drift

| Fact | HANDOFF | AGENTS |
| --- | --- | --- |
| D21 15 min same-song kill | L5–7 HARD FAIL; BoseSession 900 s | L19 HARD FAIL; DEAM row restates no room loop >15 min |
| Cadence silicon CLOSED | L8–9, L30; no more cells; no `holdout_8s_loop.wav` | L35, L45, L53 **CLOSED — do not reopen** |
| C1 LGP OPEN | L33 OPEN; L81–90 one full song Captain chooses | L45, L51 Captain look, one full song, no 8 s loop |
| No 8 s holdout | L8, L71, L87 | L35, L51 |
| Serial Studio observe/record | L32 DEAD/DEMOTED (D19) | L52 observe/record only |
| Exclusive USB if command/reply | L61–62, L91 pyserial after SS releases | L31 no multiplex two owners |
| Do not modify production K1 firmware from this repo | L57 | L4 |
| C0-v2 `ON_SILICON_PIXEL_VALIDATED`; two-clock corpse FAIL | L27–28 | L45–46 |
| Student I/O unfrozen **now** | L34 NOT YET | L47 I/O unfrozen |
| Share recoverability HOST PASS; Gate A/B HOST PASS | L24–26 | L45, L47 |
| Semantic-v0 experiment, not architecture | (not restated) | L25, L49 — no HANDOFF conflict |

## FAIL — HANDOFF serialises work D22 opened

| Topic | HANDOFF (stale as lab authority) | AGENTS + D22 (wins) |
| --- | --- | --- |
| Programme order | L17–18 `C0-v2 PASS → cadence CLOSED → transport frozen → C1 LGP → **only then student/deployment**` | L35 **D22 all HOST lanes OPEN for parallel SSA**. Cadence stays CLOSED. C1 is one open lane, not a HOST lock. |
| C1 as sole job | L33 `OPEN — YOUR JOB`; whole “Next steps” is C1 USB/firmware | C1 is row among 16 programme lanes / 40 SSA files (`PARALLEL_LANES.md`) |
| Streaming student | L26 `Streaming student STOPPED` | L47 streaming **unblocked for HOST sketches/tests**, not Titan (L36) |
| Demucs / extra nets | L35 `More nets / Demucs / Titan STOPPED`; L90 `Still no Demucs` | L50 Demucs **OPEN HOST-only** teacher probe; do not Titan; do not block C1 (L35 docs/licence) |
| Titan | L35 STOPPED | L54 Silicon/PDM/Titan **OPEN for prep docs**; no invented board numbers (L27) |
| Freeze trigger | L13, L90 freeze **after C1** if contract holds | L26 freeze only after `docs/mir/SELECTION_GATE.md`. D20/D22 *Revisit* also say freeze after C1 — C1 is necessary, not a substitute for SELECTION_GATE, and not a reason to STOP HOST work now |
| Read order | L97 cites D19–D21 only | D22 is the unblock that makes HANDOFF STOPPED rows false. Omission is the load-bearing hole |

Not a contradiction if scoped correctly: HANDOFF C1 operator notes (product firmware `acaecaa8`, no rtrace flash, pyserial exclusive, hex-32) remain valid **for a C1 look**. They do not close HOST lanes.

Transport “Frozen for C1” (HANDOFF L31) vs student I/O unfrozen is internally consistent and matches AGENTS: C1 carrier is the C0-v2 ~31.25 Hz / 0 ms extra delay path; student I/O is not a product freeze.

## Authority

1. `AGENTS.md` (Amendment 001 on research sequence) + `docs/DECISIONS.md` D22 — live HOST roster.
2. D20 Cadence CLOSED / C1 OPEN; D21 HARD FAIL — bind both files.
3. `docs/agent/HANDOFF.md` — C1 operator snapshot. Patch it; do not follow STOPPED rows.

PROOF: 15 min (HANDOFF L5 / AGENTS L19), Cadence CLOSED (HANDOFF L8 / AGENTS L53), C1 one-song (HANDOFF L87 / AGENTS L51), SS observe-only (HANDOFF L32 / AGENTS L52) match. Sequence + STOPPED vs OPEN do not.

AUDIO: none played.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:grok | L31: HANDOFF vs AGENTS. HARD FAILs MATCH. HOST STOPPED contradicts D22. |
