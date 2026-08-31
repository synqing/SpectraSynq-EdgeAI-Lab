---
abstract: "Wave-3 harvest 2026-08-31. 40/40 authority lanes wrote. Cadence runner RETIRED. Demucs HOST-NOT-INSTALLED. Titan PRE-SILICON. C1 OPEN. 5 Hz / 50 ms cliff PASSes are envelope, not student target. Registry SHA still 0/23."
---

# Harvest — 40 HOST authority lanes wave 3

**HARD FAIL (`SAME_SONG_LOOP_MAX_15MIN`).** Cadence silicon **CLOSED**. Runner **RETIRED**. No ffplay. No K1 USB.

Wave-3 IDs: `docs/agent/lanes/LAUNCHED_W3.md`. Wave-2 harvest: `docs/agent/lanes/HARVEST.md`. Wave-1 copies: `docs/agent/lanes/wave1/`. This wave wrote the **authority files** named in `LAUNCHED_W3.md`, not the wave-2 `Lxx_*.md` receipts.

Wave-3 was the remaining-authority pass: retire cadence in source, lock Demucs as uninstalled HOST docs, keep Titan PRE-SILICON, keep C1 OPEN, and stop reading the 5 Hz / 50 ms cadence cliffs as a student target.

## STATUS

**40/40 W3 files exist.** Cadence runner **RETIRED** (source + execution). Demucs **HOST-NOT-INSTALLED**. Titan **PRE-SILICON**. C1 **OPEN** (`LGP_PERCEPTUAL_VALIDATED` not applied). Cliff PASSes (5 Hz @ 0 ms Q1 0.414; 20 Hz + 50 ms Q1 0.402) are **envelope edges, not the student target**. Registry SHA pins still **0/23**. Harvest did **not** reopen cadence, open USB, install Demucs, or play a song.

## CLAIM

Wave 3 did **not** ship a student, freeze I/O, stamp C1, flash Titan, or download Demucs.

What it did:

1. **Cadence CLOSED is mechanical.** `scripts/gate_c0_cadence_silicon.py` `main()` calls `refuse_if_cadence_closed()` **before** argparse. `--resume` is not an escape. Proof: `tests/test_cadence_silicon_retired.py`.
2. **Demucs is a HOST teacher probe that is not installed.** Code MIT ≠ weights (UNKNOWN, scientific-use). `try_demucs()` returns `None`. Probe prints `HOST-NOT-INSTALLED` and exits 2. No `demucs` extra. Not Titan.
3. **Titan is PRE-SILICON prep.** Golden tensors exist HOST-ONLY (32 cases). RUHMI C99 pin exists. p50/p95/µs stay empty. 1 ms NPU / ~100 ms PaRIRset / 50 ms K1 cadence are lookalikes, not board clocks. MERT / MuQ / MAEST / Demucs stay off the board.
4. **C1 is still OPEN.** Only remaining Gate-C action. Product firmware, one full song Captain chooses, C0-v2 carrier ~31.25 Hz / 0 ms. Agent does not invent PASS.
5. **Cliff PASSes are not the student target.** Slowest 0-delay PASS 5 Hz and largest added-delay PASS 50 ms at 20 Hz sit on the 0.40 Q1 bar. Joint 5 Hz + 50 ms FAIL. After C1, do not design to either cliff. Do not AND them. C1 playback is the interior carrier, not the envelope bound.
6. **C1 PASS would still not freeze a student.** Selection, provenance (0 SHA pins), licensing (13/23 UNKNOWN), and architecture remain. Amendment 001 still owns model selection.

## EVIDENCE

| What | Where |
| --- | --- |
| Launch roster | `docs/agent/lanes/LAUNCHED_W3.md` (40 SSA IDs) |
| Cadence retire source | `scripts/gate_c0_cadence_silicon.py` `CADENCE_CLOSED = True`; `refuse_if_cadence_closed()` before `ap.parse_args()` |
| Cadence retire test | `tests/test_cadence_silicon_retired.py` |
| Cadence receipt | `artifacts/gate_c0_cadence_silicon/CADENCE_RESULT.json` (`gate_c0_cadence=CLOSED`, `cadence_close=CAPTAIN_CLOSE_2026-08-31`) |
| Git-visible silicon copy | `docs/mir/SILICON_RECEIPTS.md` |
| C0-v2 receipt | `artifacts/gate_c0v2/C0V2_RESULT.json` (`ON_SILICON_PIXEL_VALIDATED`) |
| C1 method (unstamped) | `docs/mir/GATE_C1.md` **STATUS: OPEN** |
| Cliff language | `docs/mir/GATE_C.md`, `GATE_C0_CADENCE.md`, `GATE_C1.md`, `SEMANTIC_TRANSPORT_CONTRACT.md`, `SELECTION_GATE.md`, `SHARE_STUDENT.md` |
| Demucs contract | `docs/mir/DEMUCS_HOST.md`; `src/edgeai/mir/teachers.py`; `scripts/demucs_host_probe.py`; `tests/test_demucs_host.py` |
| Titan prep | `docs/titan/PREP.md`; `GOLDEN_TENSORS.md`; `NOT_ON_BOARD.md`; `docs/TITAN_BRINGUP.md`; `scripts/titan_prep_check.py` |
| Programme wrapper | `AGENTS.md`; `docs/DECISIONS.md` D20–D22; `docs/agent/HANDOFF.md` |

**SHA-256 re-derived this harvest (HOST, no USB), MATCH `SILICON_RECEIPTS.md`:**

```
57b408be9d9941735b42c09fba7e174488ddcd02b81494c3eb84f29e72391928  artifacts/gate_c0v2/C0V2_RESULT.json
371573dc9e5769629dae5dc1c572fb57c0a0884d9239a8c0245a8576f9b4449d  artifacts/gate_c0_cadence_silicon/CADENCE_RESULT.json
```

## COMMAND

Harvest re-ran (HOST only). No USB. No Bose. No `uv add demucs`. No cadence cells.

```text
uv run pytest tests/test_cadence_silicon_retired.py tests/test_demucs_host.py tests/test_serial_studio.py -q
# 14 passed

python3 scripts/demucs_host_probe.py
# HOST-NOT-INSTALLED  exit 2
# demucs_installed: false

python3 scripts/titan_prep_check.py
# PRE-SILICON  golden_dir PRESENT  compile_receipt_pin PRESENT
# latency REFUSED  flash REFUSED  usb REFUSED  exit 0

python3 -c "import hashlib,importlib.util,yaml; from pathlib import Path
print(importlib.util.find_spec('demucs'))
print(hashlib.sha256(Path('artifacts/gate_c0v2/C0V2_RESULT.json').read_bytes()).hexdigest())
print(hashlib.sha256(Path('artifacts/gate_c0_cadence_silicon/CADENCE_RESULT.json').read_bytes()).hexdigest())
print('n', len(yaml.safe_load(Path('mir/registry.yaml').read_text())['entries']))"
# demucs None; SHAs match; registry n=23
```

Other W3 lanes **CONSUMED AS provisional** unless listed above.

## METHOD_RISK

- File existence + changelog + a HOST re-run of three test modules ≠ a second silicon campaign.
- `LANDSCAPE.md` 1:1 is “all 23 registry `id:` strings appear in the map table,” not a new visual-utility experiment.
- Registry W3 write is **programme comments**, not SHA pins. 0 SHA/md5/git pins remain. Do not invent hashes.
- `test_refuse_if_serial_studio_owns_usb_raises_when_holder_is_serial_studio` **mocks** the holder. It is not a live USB-CDC test. Do not live-USB-test.
- `try_demucs()` returning `None` proves `ImportError`, not an empty hub cache. We did not fetch.
- `artifacts/golden/` and silicon JSON live under gitignored `artifacts/`. Another clone may be HOST-MISSING. Git-visible copy is `docs/mir/SILICON_RECEIPTS.md`.
- `docs/onnx_graph_semantic_v0.json` still says ReduceMean. Live code is AdaptiveAvgPool2d (D11). The dump is stale.
- C0-v2 JSON still contains receipt-time `cadence: OPEN — not this run`. Live programme cadence is CLOSED (D20).
- Wave-4 launched in parallel (`LAUNCHED_W4.md`). This harvest describes W3 targets as they stood at harvest. It does not harvest W4.

## NEXT

1. **C1 stays OPEN.** Captain names **one** full song. Product firmware `k1_main_rpl_im69d` @ `acaecaa8`. Carrier ~31.25 Hz / 0 ms. No 8 s loop. No probe. Agent stamps `LGP_PERCEPTUAL_VALIDATED` only after that look.
2. **Do not treat cliff PASSes as the student.** If I/O later freezes, freeze the contract region (four-source including `other`, hold policy, PASS envelope). Never emit-at-5 Hz and never budget-50 ms as the design centre. Never AND them.
3. **Do not install Demucs** until a named weight GO. MUSDB STEMS on disk are today’s teacher.
4. **Do not invent Titan latency.** Fill p50/p95 only from a flashed image labelled `ON-SILICON`.
5. **HOST leftovers (not C1):** registry SHA pins (still 0/23); optional later owned-USB unit on a real holder (do not live-test this wave); stale ReduceMean ONNX dump.
6. Cadence runner stays **RETIRED**. Do not un-retire it to “finish” 10 Hz + 25 ms.

---

## Per-lane harvest

IDs from `LAUNCHED_W3.md`. Status is the **file after W3**, not a new silicon stamp.

| ID | Wrote | Status | One-line |
| --- | --- | --- | --- |
| L01 | `docs/mir/SELECTION_GATE.md` | PATCHED | Nine criteria still open. I/O unfrozen until those **and** C1 (freeze not automatic). Cadence 5 Hz / 50 ms are **edges, not student target**. |
| L02 | `docs/mir/GATE_C0V2.md` | HISTORICAL | Banner: C0-v2 close-state only. Stamp `ON_SILICON_PIXEL_VALIDATED`. Not cadence/C1 authority. Do not reopen cells. |
| L03 | `docs/mir/GATE_C0_SILICON_PATH.md` | RETIRED | Two-clock C0 FAIL corpse. Not a live inject/flash recipe. Successor already PASS (`GATE_C0V2.md`). C1 is next Gate-C. |
| L04 | `docs/mir/GATE_C.md` | OPEN | Live wrapper: C0-v2 PASS, cadence CLOSED, C1 OPEN unstamped. 5 Hz / 50 ms are **1-D cliff PASSes, not the student target**. Product/Titan nets wait; HOST sketches OPEN. |
| L05 | `docs/DECISIONS.md` | MATCH | D20: runner dies before argparse; `--resume` rejected. D22: Demucs HOST probe + Titan PRE-SILICON docs remain OPEN. C1 OPEN. |
| L06 | `docs/mir/SILICON_RECEIPTS.md` | CREATED | Git-visible copy of gitignored C0-v2 + cadence JSON. SHA-256 filled; harvest re-derived MATCH. Cadence CLOSED. |
| L07 | `mir/registry.yaml` | COMMENTS_ONLY | 23 ids. Programme stamps in comments (C0-v2 PASS, cadence CLOSED, C1 OPEN). **0 SHA pins remain.** 13/23 UNKNOWN. `htdemucs` not executed. |
| L08 | `docs/mir/LANDSCAPE.md` | MATCH_1:1 | All 23 registry ids mapped. Dropped landscape-only names (madmom / MERT-330M / Open-Unmix / QSCNet). Teachers off Titan. No BUILDING/DROPPING. |
| L09 | `docs/effect-decomposition/README.md` | DEMOTED | 9-class/18-mode table is **not** canonical. Inventory is firmware pin `effect-semantics.json` (23 `LIGHT_MODE_*`, SHA `36466cd5`). |
| L10 | `docs/TITAN_BRINGUP.md` | PRE-SILICON | Arrival sequence. 1 ms / 100 ms / 50 ms stamped lookalikes. Teachers off board. p50 empty. |
| L11 | `docs/HOST.md` | PASS | CPython 3.12.11. Four extras `musdb/mir/dev/silicon`. `silicon` = pyserial package, not a port. Demucs is **not** an extra. Cadence CLOSED. |
| L12 | `docs/mir/SHARE_STUDENT.md` | UNFROZEN | HOST recoverability PASS. C1 stamp does not auto-freeze I/O. 5 Hz and 50 ms exclusive cliffs, not design centre. |
| L13 | `docs/mir/GATE_C0_CADENCE.md` | CLOSED | Runner retired. Cliffs: 5 Hz Q1 **0.414**; 20 Hz+50 ms Q1 **0.402**. 100 ms FAIL. 5 Hz+50 ms FAIL. 10 Hz+25 ms NOT_COMPLETED — no interpolation. |
| L14 | `docs/mir/SEMANTIC_TRANSPORT_CONTRACT.md` | FROZEN_FOR_C1 | Four-source. 50 ms requested = 64 ms / 2 hops. 5 Hz XOR 50 ms. After C1 pick margin **inside** the envelope; do not design to either cliff. |
| L15 | `docs/agent/HANDOFF.md` | PATCHED | C1 is the last Gate-C action, **not** the last work before a production student. D22 HOST OPEN now. Runner retired. |
| L16 | `AGENTS.md` | MATCH | Hard rule: cadence runner RETIRED. Demucs: no weight download this lane. Titan: OPEN PRE-SILICON prep. C1 OPEN. |
| L17 | `docs/MODEL_CONTRACT.md` | UNFROZEN | Semantic-v0 HOST sheet ≠ `FROZEN_FOR_C1`. Do not copy 16 kHz / 1 s / 3-sigmoid onto C1. Transport freeze lives in the contract file. |
| L18 | `experiments/semantic_v0/AUTHORITY.md` | EXPERIMENT | D22 HOST-open ≠ architecture. Do not freeze 16 kHz / 1 s / 3 sigmoids. Synthetic F1 is not Gate A. |
| L19 | `docs/mir/SOURCE_ACTIVITY.md` | MATCH | C0-v2 PASS / cadence CLOSED / C1 OPEN kept. Demucs HOST probe OPEN: **not installed**, weights UNKNOWN, not Titan, no download. |
| L20 | `README.md` | MATCH | Landing: C0-v2 PASS, cadence CLOSED + retired runner, C1 OPEN, D22 HOST Demucs+Titan-prep OPEN. C1 is not the only remaining work. |
| L21 | `mir/README.md` | MATCH | Map to live GATE_C / GATE_C1 / SELECTION_GATE. Demucs HOST-only not installed. Do not reopen cadence. |
| L22 | `docs/AMENDMENT_001_DELTA.md` | MATCH | Amendment 001 still owns model selection. Sequence: C0-v2 done, cadence CLOSED, C1 next Gate-C. HOST Demucs/Titan-prep unblocked. |
| L23 | `tests/test_serial_studio.py` | UNIT_MOCK | Added mocked `refuse_if_serial_studio_owns_usb` raise (`SERIAL_STUDIO_NOT_TRANSPORT`). D19. **Not a live USB test.** |
| L24 | `src/edgeai/mir/teachers.py` | PASS | `try_demucs()` does **not** construct `Separator`. Titan env → None. Auto-download refused. ImportError → None. |
| L25 | `tests/test_demucs_host.py` | CREATED | `find_spec("demucs") is None`; `try_demucs() is None`; Titan env false; no USB/ffplay in the hook. Harvest re-ran PASS. |
| L26 | `docs/mir/DEMUCS_HOST.md` | CREATED | Envelopes not waveforms. MUSDB STEMS are today’s teacher. Weights UNKNOWN scientific-use. Does not block C1. |
| L27 | `docs/titan/PREP.md` | CREATED | PRE-SILICON: BSP NPU example → golden tensor → WAV frontend → PDM last. No board latency. Teachers off U55. |
| L28 | `docs/titan/GOLDEN_TENSORS.md` | CREATED | 32 HOST-ONLY cases under `artifacts/golden/`. CNN on log-mel, not STFT. AdaptiveAvgPool, not ReduceMean. Band HOST-ONLY until ON-SILICON. |
| L29 | `docs/mir/GATE_C1.md` | OPEN | Stamp **not applied**. Product firmware. One full song Captain chooses. Carrier ~31.25 Hz / 0 ms. Cliff PASSes are envelope, not nominal student. I/O freeze after C1 is not automatic. |
| L30 | `docs/ruhmi/COMPILE_RECEIPT.md` | PRE-SILICON | GHA 33319114336 ad01 then AdaptiveAvgPool smoke. Compiler RAM/Flash/MACs **≠ Titan latency**. Points at `docs/titan/PREP.md`. |
| L31 | `docs/mir/EFFECT_SEMANTICS_CONSUME.md` | PIN_HELD | Lab pin SHAs stay (`36466cd5` + atlas hashes). `fingerprints.json` SHA UNKNOWN. 9-class/18-mode guidebook demoted. Students effect-agnostic. |
| L32 | `docs/mir/GATE_C_CADENCE_HOST.md` | HOST-ONLY | Host rehearsal ≠ silicon clock. Do not freeze I/O from host 20 Hz or host 50 ms FAIL. Silicon owns 5 Hz / 50 ms / joint FAIL. Cadence CLOSED. |
| L33 | `datasets/README.md` | PATCHED | Stale “not downloaded” killed. MUSDB18 STEMS on disk (100 train / 50 test). HOST share uses those stems; Demucs not required. Audio gitignored. |
| L34 | `docs/dsp/M85_GOLDENS.md` | HOST-ONLY | 16 kHz rFFT / Goertzel-440 / Hann vectors. PRE-SILICON: no M85/Helium latency. Independent of U55 goldens. Not Titan board numbers. |
| L35 | `docs/HOST_RECEIPTS.md` | PASS_INDEX | Mac bootstrap HOST-ONLY/SYNTHETIC. Live pooling AdaptiveAvgPool2d; ReduceMean dump stale. C0-v2 PASS. Cadence CLOSED. Demucs not installed. |
| L36 | `docs/AMENDMENT_002.md` | MATCH | Onset delayed ~100 ms (HOST-ONLY, 3 short IRs), not killed. Acoustic-path 100 ms ≠ cadence 100 ms FAIL. Cadence CLOSED. C1 OPEN. |
| L37 | `scripts/demucs_host_probe.py` | CREATED | Presence-only. Harvest re-ran: `HOST-NOT-INSTALLED`, exit 2, `separator_constructed: false`. Never downloads. Never USB. Never Titan. |
| L38 | `scripts/titan_prep_check.py` | CREATED | PRE-SILICON printer. Harvest re-ran: golden PRESENT, pin PRESENT, latency/flash/usb REFUSED, exit 0. Does not invoke the retired cadence runner. |
| L39 | `docs/mir/SERIAL_STUDIO.md` | PASS | SS observe/record. Because the cadence runner dies before a port, SS is **never cadence transport**. Exclusive USB-CDC still binds. Shuttle stays demoted. |
| L40 | `docs/titan/NOT_ON_BOARD.md` | CREATED | Ban lock: MERT / MuQ / MAEST / Demucs never on Titan/U55/PDM. HOST Demucs Mac-only, not installed. Student = CNN-on-log-mel after C1 **and** SELECTION_GATE freeze. |

## Orchestrator-owned (not an SSA)

Named in `LAUNCHED_W3.md`. Harvest re-ran.

| File | Status | One-line |
| --- | --- | --- |
| `scripts/gate_c0_cadence_silicon.py` | RETIRED | `CADENCE_CLOSED = True`. `refuse_if_cadence_closed()` is the first line of `main()`. Raises `SystemExit("RETIRED: D20 CADENCE CLOSED.\nDo not run more silicon cells. Use existing cadence receipts.")` before argparse, flash, USB, or Bose. |
| `tests/test_cadence_silicon_retired.py` | PASS **verified** | Banner in source; refuse sits before `parse_args()`; `--resume --skip-flash --skip-restore` dies non-zero with the banner and without `usbmodem` / `ffplay` / `AUDIO:`. |

## Cliff PASSes — not the student target

Cadence 1-D envelope (CLOSED; do not re-measure):

```text
~31.25 / 20 / 15 / 10 / 5 Hz @ 0 ms     PASS
20 Hz + 25 ms                           PASS
20 Hz + 50 ms requested (64 ms / 2 hops) PASS   ← delay cliff  Q1 0.402
20 Hz + 100 ms                          FAIL (Q1)
20 Hz + 200 ms                          FAIL
5 Hz + 50 ms                            FAIL (Q1)  ← AND-ban
10 Hz + 25 ms                           NOT_COMPLETED — do not interpolate
```

| Measured | What it is | What it is not |
| --- | --- | --- |
| Slowest 0-delay PASS **5 Hz** (`r5_d0`, Q1 **0.414**) | Rate **cliff** at 0 extra delay | Nominal student emit |
| Largest added-delay PASS **50 ms** at **20 Hz** (`r20_d50`, Q1 **0.402**) | Delay **cliff** at a comfortable rate | Nominal student latency |
| Combined **5 Hz + 50 ms FAIL** (`r5_d50`, Q1 0.245) | Measured AND-ban | A fill-in of 10 Hz+25 ms |
| C1 playback ~**31.25 Hz, 0 ms** (C0-v2 Q1 0.83) | Already-proven **carrier** on product firmware | A student I/O freeze |

Both cliff Q1 scores sit on the 0.40 floor. Sitting on a cliff is sitting on the fail line. A student that ANDs the two cliffs rebuilds `r5_d50`. A student that treats 5 Hz **or** 50 ms as the post-C1 design point is reading an envelope bound as a target.

**After C1 the cliffs stay edges.** Freeze the contract region if/when SELECTION_GATE is satisfied — never “emit at 5 Hz” and never “budget 50 ms extra” as the nominal net.

## Demucs HOST — not installed

Harvest re-ran:

- `importlib.util.find_spec("demucs")` → `None`
- `python3 scripts/demucs_host_probe.py` → `HOST-NOT-INSTALLED` exit 2
- `uv.lock` / `pyproject.toml` → zero `demucs` hits
- `teachers.try_demucs()` → `None`; `Separator` is not constructed

Weights **UNKNOWN — not MIT** (scientific-use, `facebookresearch/demucs#327` comment `1134828611`). Teacher use does not clear a derived student. MUSDB18 STEMS (100/50 `.stem.mp4`) are the teacher on disk. Named weight GO required before any install. Does not block C1. Not Titan / U55 / PDM.

## Titan — PRE-SILICON

No RA8P1 on the desk. Harvest re-ran `scripts/titan_prep_check.py`: golden dir PRESENT (32 HOST-ONLY cases), RUHMI pin `6c5aad901a1a41e28f6e306bfc35c44659e89502` PRESENT, latency cells empty, flash/USB refused.

Ban: MERT, MuQ, MAEST, Demucs off Titan. Export CNN not STFT. AdaptiveAvgPool2d required (D11). Golden tensors first, PDM last.

## C1 — still OPEN

`docs/mir/GATE_C1.md` **STATUS: OPEN.** `LGP_PERCEPTUAL_VALIDATED` is **not** in `AGENTS.md`. D20 revisit is still “after the look.” Dumps do not answer. One full song Captain chooses. No 8 s loop. Same-song cap 15 minutes → kill the player.

A C1 PASS would close Gate C for **this** binding through the LGP. It would **not** freeze Student-v0 I/O and would **not** select a production net.

## Wave-2 leftovers after W3

| Wave-2 leftover | After W3 |
| --- | --- |
| Registry SHA pins (L09 FAIL) | **Still FAIL.** W3 L07 added comments only. 0/23 pins. |
| Landscape ≠ registry (L10 FAIL_MISMATCH) | **Closed as map.** W3 L08 23/23 ids in the table. Visual-utility experiment not re-run. |
| Effect-decomposition “canonical” (L16 FAIL) | **Demoted.** W3 L09 + L31. Firmware pin is inventory. |
| Owned-USB unit (L38 GAP) | **Mocked unit only** (W3 L23). Do not live-USB-test. Real holder still untested. |

## Files W3 created

`docs/mir/SILICON_RECEIPTS.md` · `docs/mir/DEMUCS_HOST.md` · `docs/titan/{PREP,GOLDEN_TENSORS,NOT_ON_BOARD}.md` · `scripts/demucs_host_probe.py` · `scripts/titan_prep_check.py` · `tests/test_demucs_host.py` · `tests/test_cadence_silicon_retired.py` (orchestrator)

## Still true

Cadence CLOSED. Runner RETIRED. C1 OPEN. Cliff PASSes are not the student target. Demucs not installed. Titan PRE-SILICON. No 8 s loop. No USB steal. Do not stamp `LGP_PERCEPTUAL_VALIDATED` without Captain’s look.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:grok | Wave-3 40/40 harvest. Cadence retired verified. Demucs HOST-NOT-INSTALLED. Titan PRE-SILICON. C1 OPEN. Cliff PASSes not student target. |
