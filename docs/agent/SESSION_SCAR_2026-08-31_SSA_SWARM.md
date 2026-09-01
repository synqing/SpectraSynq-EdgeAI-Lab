---
abstract: "2026-08-31 session scar. 147 SSAs ≠ lamps. D22 OPEN is HOST work, not Lxx.md waves. Marker SSA_RECEIPT_WAVE_IS_NOT_SHIP. Keep the widget. Own children. Plot3D needs subscribed slots. Cadence retired. Demucs not installed. C1 still OPEN."
---

# Session scar — 2026-08-31 SSA swarm

**HARD FAIL marker: `SSA_RECEIPT_WAVE_IS_NOT_SHIP`.** If an agent launches N explore/docs SSAs whose `DONE_WHEN` is `docs/agent/lanes/L*.md`, that wave is **not work**. Captain will treat it as zero. Test: `tests/test_ssa_wave_not_ship.py`.

This file is the inventory of what that session actually learned. Do not spawn another 40 agents to re-derive it.

## What the session was

One Grok session in EdgeAI-Lab. Captain ordered cadence closed, Serial Studio observe-only, then “launch 40 agents,” then more waves, then a live dashboard. The orchestrator launched **147** children (146 completed, 1 cancelled): four waves (40+40+40+24) plus three Serial Studio JSON reads.

Captain’s verdict on the swarm: **nothing for the lamps.** That verdict is load-bearing. Do not relitigate it with harvest tables.

## Archetype (why it kept happening)

| Pattern | How it showed up | Leverage |
| --- | --- | --- |
| **Shifting the burden** | 40 explore agents writing Lxx receipts instead of doing the HOST job D22 actually unblocked | D22 means **do the lane**, not **census the lane** |
| **Fixes that fail** | 3D plot looked like a scribble → replaced with bar panels. Captain rejected. Binding was the job | Keep the widget. Bind it |
| **Success to the successful** | “40 agents launched” became the success metric; C1 / Demucs / Titan starved | Count artefacts the consumer uses |
| **Map ≠ territory** | 147 `completed` statuses, 118 then 134 pytest, harvest PASS — lamps unchanged | Completions are not the show |

**Steel-man of the swarm:** D22 literally said “target 20–40 independent SSAs.” Parallel HOST work is legal. **Red-team:** independent tasks are scripts/tests/authority files with a command that can go red. Forty files named `L03_contract_vs_receipt.md` are not forty tasks. They are one audit, copied.

**OODA that failed:** Observe (docs exist) → Orient (write another doc) → Decide (wave 2) → Act (overwrite Lxx). The loop never sampled the lamps, a student, or Demucs weights. Next loop MUST include a command the orchestrator re-runs.

## Failures (do not repeat)

1. **Receipt wave as completion.** Waves 1–2 wrote `docs/agent/lanes/L01`…`L40` twice. Wave 1 copies: `docs/agent/lanes/wave1/`. Useful as a punch list. **Not product.**
2. **context-mode-ops / “launch 40” as a default.** Invoking a 10–20 agent army on EdgeAI-Lab to “coordinate” is the same scar. Do **not** spawn a frenzy to document a frenzy.
3. **Widget substitution.** Serial Studio 3D → bar panels because the polyline was peak×energy×novelty in time. Captain: keep 3D, bind musical data.
4. **Plot3D ingest miss.** Parser v1.2 slots 23–24 stayed stale on uniqueIds that used to be Peak. New indices need **graph:true** datasets on the Bench/Main multiplot (EM Wave pattern). `project.activate` after `loadJson`. Duplicate index on the same source is how 3D reads a channel already subscribed.
5. **Children left running.** Web-view `bridge.py` backgrounded for ~70 min. A Codex in the same folder ran `find /Users/spectrasynq` for `bridge.py`. Grok subagents were finished; the orchestrator did not own the other process. Idle ≠ done (`ssa-management` §9a).
6. **Harvest as ship.** `HARVEST.md` / `HARVEST_W3.md` are receipts. Captain asked what the swarm achieved for the lights. Answer: **nothing.**
7. **Prose CLOSED.** Cadence “CLOSED” in docs did not stop the runner until `refuse_if_cadence_closed()` sat **before** argparse. Mechanical or it is a lie.
8. **Re-asking / mid-pipeline status.** Banned (`no-reapprove-already-given`, Captain 2026-08-12 mid-lane report ban).

## Problems that *were* resolved (keep these)

| Problem | Resolution | Proof |
| --- | --- | --- |
| Cadence script still executable | `CADENCE_CLOSED = True`; refuse before argparse | `tests/test_cadence_silicon_retired.py` |
| Demucs might get `uv add` / hub fetch | `try_demucs()` never constructs `Separator`; probe exits 2 | `scripts/demucs_host_probe.py`; `tests/test_demucs_host.py` |
| Invented Titan ms | Prep printer refuses latency/flash/USB | `scripts/titan_prep_check.py` |
| Effect guidebook vs firmware pin | Guidebook demoted; pin `36466cd5` is inventory | `docs/effect-decomposition/README.md`; `EFFECT_SEMANTICS_CONSUME.md` |
| Landscape ≠ registry | 23/23 ids in the map table | `docs/mir/LANDSCAPE.md` |
| 3D scribble | Tempo-phase orbit: `orbit_x = peak * cos(2π phase)` | firmware `tools/serial-studio/parsers/k1_ap_parser.js` schema v1.2 |
| USB multiplex | SS observe/record; cadence runner dies before USB | D19 + D20 |

Git that landed the HOST machinery: `bcfd788`, `bc885bc`.

## Insights (load-bearing)

- **D22 unblocks HOST work. It does not define DONE_WHEN as Lxx.md.**
- **DONE_WHEN** is a command the orchestrator re-runs that can go **red** (pytest, probe exit 2, retire banner). Not “file exists.”
- **One writer per authority file.** Not one writer per receipt about that file.
- **Keep the widget.** If Captain named 3D / Web View / FFT, bind it. Do not swap for bars because the first bind was wrong.
- **Subscribe new parser slots on the source multiplot** (`graph: true`) or Plot3D uniqueIds keep the old channel.
- **Own every child to completion or kill.** Background bash, Codex, Grok SSA — same law.
- **Cliff PASSes (5 Hz, 50 ms) are envelope, not the student.** Joint 5 Hz+50 ms FAIL. C1 plays ~31.25 Hz / 0 ms.
- **Demucs is not C1.** Teacher today is MUSDB STEMS. Weights UNKNOWN until a **named weight GO**. Not Titan.
- **C1 is the last Gate-C action, not the last programme work.** Agent does not invent `LGP_PERCEPTUAL_VALIDATED`.

## Encode (where this lives)

| Surface | What |
| --- | --- |
| This file | Inventory. Read once when resuming the swarm topic |
| `AGENTS.md` | HARD FAIL `SSA_RECEIPT_WAVE_IS_NOT_SHIP` |
| `docs/DECISIONS.md` D23 | D22 ≠ receipt waves |
| `docs/agent/HANDOFF.md` | Remaining lanes, Demucs HOST steps |
| `docs/agent/PARALLEL_LANES.md` | Lxx is receipt, not DONE_WHEN |
| skill `ssa-wave-is-not-ship` | Trigger on “launch 40”, fan-out, Lxx wave |
| `ssa-management` §9 | Stop gate |
| Cursor `ssa-wave-is-not-ship.mdc` | alwaysApply |
| `tests/test_ssa_wave_not_ship.py` | Marker cannot be deleted quietly |

## What this session did **not** teach

It did not teach that parallel SSAs are banned. Independent HOST tasks with one writer and a re-runnable command remain D22-legal. It taught that **census-of-docs is not a task**.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-09-01 | agent:grok | Created from 147-SSA session. Marker SSA_RECEIPT_WAVE_IS_NOT_SHIP. |
