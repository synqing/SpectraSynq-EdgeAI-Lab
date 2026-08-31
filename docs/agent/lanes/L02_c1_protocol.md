---
abstract: "L02: GATE_C1.md protocol MATCHES C1 (Captain-eyes LGP look, one full song he chooses, product firmware, C0-v2 ~31 Hz/0 ms carrier, no 8 s loop, dumps do not answer). Wording-only: GATE_C1 says ~31 Hz, contract says ~31.25 Hz. Stamp not applied."
---
STATUS: MATCH
CLAIM: `docs/mir/GATE_C1.md` is the C1 protocol named in AGENTS/D20/D22: Captain is the viewer of an LGP look on one full song he chooses, on product firmware, on the already-proven C0-v2 carrier (~31 Hz / 0 ms extra delay), with no 8 s holdout loop, and dumps do not answer C1. Stamp `LGP_PERCEPTUAL_VALIDATED` is not applied.
EVIDENCE: docs/mir/GATE_C1.md:2,9,13,17-23,27,29,31 ; AGENTS.md:51 ; docs/DECISIONS.md D20/D22 ; docs/mir/SEMANTIC_TRANSPORT_CONTRACT.md:19
COMMAND: python3 -c "from pathlib import Path; t=Path('docs/mir/GATE_C1.md').read_text(); keys=('Captain is the viewer','one full song','the viewer chooses','product firmware','~31 Hz','31.25','0 ms extra delay','8 s','Dumps do not answer','LGP_PERCEPTUAL_VALIDATED'); print({k: (t.find(k)>=0) for k in keys})"
METHOD_RISK: GATE_C1 never writes `31.25`. A reader who treats `~31 Hz` as a new freeze, or who plays the 5 Hz envelope because that sentence sits next to C1 playback, is wrong. C1 playback in the same sentence is the C0-v2 carrier at 0 ms extra delay on product firmware. Dumps, MAD, and C0 Q1–Q3 still do not answer C1.
NEXT: Do not stamp. Do not start `holdout_8s_loop` / ffplay. Do not USB / flash / rtrace. Optional later: align GATE_C1 `~31 Hz` to contract `~31.25 Hz`. C1 stays OPEN until Captain looks.

# C1 protocol vs GATE_C1

**HARD FAIL (`SAME_SONG_LOOP_MAX_15MIN`).** Same song/clip looped >15 min → kill the player. Do not continue.

Cadence **CLOSED**. This lane is document compare only. No audio. No USB. No flash. No stamp.

Definition under test (AGENTS C1 row, D20, D22): C1 is a **Captain-eyes LGP look** on **one full song he chooses**, **product firmware**, **~31.25 Hz 0 ms carrier**, **no 8 s loop**, and **dumps do not answer C1**.

## Criterion table

| Required C1 | GATE_C1.md | Verdict |
| --- | --- | --- |
| Captain-eyes LGP look | Abstract: “LGP look is the gate.” L23: “Captain is the viewer.” Three questions “through the LGP, with music.” | MATCH |
| One full song he chooses | L29: “Play **one full song** the viewer chooses. Not the test-slice loop.” Viewer bound at L23 as Captain. | MATCH |
| Product firmware | L13 + L27: product firmware on Main RPL `k1_main_rpl_im69d` @ `acaecaa8`. “No probe flash. No rtrace concert.” | MATCH |
| ~31.25 Hz, 0 ms carrier | L13: “already-proven carrier (**~31 Hz**, **0 ms extra delay**) on **product firmware**.” String `31.25` absent. Same C0-v2 native hop as contract `~31.25 Hz`. | MATCH (wording delta) |
| No 8 s loop | L2, L9, L23, L29: no 8 s / 8-second holdout; agent does not start the 8 s loop; not the test-slice loop. | MATCH |
| Dumps do not answer C1 | L23: “Dumps do not answer this.” L27 forbids rtrace concert. Stamp only after the three questions (L31). | MATCH |

## What GATE_C1 is not

- Not a dump-scored gate. C0-v2 `ON_SILICON_PIXEL_VALIDATED` stays a prior stamp; it is not C1.
- Not cadence. L9 forbids re-running rate/delay silicon. L13 records 5 Hz / 50 ms / joint FAIL as **transport envelope**, then names C1 playback as the proven carrier, not 5 Hz+50 ms.
- Not probe firmware. L27 names `k1_main_rpl_im69d`, not `k1_main_rpl_rtrace_probe`.
- Not a stamp. L31: C1 OPEN until the three questions are answered. This lane did not write `LGP_PERCEPTUAL_VALIDATED`.

## Adjacent docs (not GATE_C1)

| Doc | C1 wording | vs GATE_C1 |
| --- | --- | --- |
| AGENTS.md C1 row | “Captain look, one full song he chooses, no 8 s loop” | Same |
| D20 | C1 LGP perceptual; C0-v2 carrier on product firmware; no 8 s loop | Same |
| D22 | “C1 stays the LGP look (Captain, one full song he chooses, no 8 s loop)” | Same |
| SEMANTIC_TRANSPORT_CONTRACT.md L19 | “C0-v2 carrier, **~31.25 Hz**, 0 ms extra delay, product firmware” | Hz spelling only |
| GATE_C.md C1 | Same three questions; “dumps … do not answer C1”; also “Blinded where practical” | Extra blindness not in GATE_C1 and not in the definition under test |

## Wording delta (not a protocol fail)

`docs/mir/GATE_C1.md` L13 writes `~31 Hz`. `docs/mir/SEMANTIC_TRANSPORT_CONTRACT.md` L19 and `docs/agent/HANDOFF.md` write `~31.25 Hz`. Host hop is 512/16000 = 31.25 Hz in cadence docs. GATE_C1 still forbids the slow envelope as C1 playback. Align later if anyone edits GATE_C1; do not reopen cadence to “confirm 31 vs 31.25”.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:grok | Created. GATE_C1 protocol MATCH vs C1 definition. No stamp. |
