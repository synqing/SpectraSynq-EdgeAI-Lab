---
abstract: "HOST parse of firmware Serial Studio project vs live Documents copy. Dashboard groups/widgets/dataset count/parser contract. Why firmware .ssproj is ~81k vs live ~112k. No USB. No Documents edit."
---

# SS firmware project vs live Documents copy

HOST-ONLY file parse. Cadence silicon **CLOSED**. Serial Studio observe/record only (D19). This lane did **not** open USB, `:7777`, pyserial, or Serial Studio. Documents copy was **read, not edited**.

HARD FAIL: `SAME_SONG_LOOP_MAX_15MIN`. No 8 s loop. No firmware C++.

STATUS: PASS (parse complete; sizes from line/indent evidence, not `stat`)

CLAIM: The firmware tree copy is the **same dashboard design** as the live Documents project (dual-UART K1 observability, 62 datasets, schema v1.1 parser), exported with **2-space JSON**. The live copy is Serial Studio 4.0.3’s **native 4-space save** plus later shuttle/table/timer drift. That indent — not missing LED/FFT/3D widgets — is why the firmware file is ~81 kB and the live file ~112 kB. Dashboard is still not evidence. Parser contract is v1.1 (21 slots). Dataset **titles** for clocks are mis-indexed on both copies.

## Designed groups (firmware copy)

Path: `/Users/spectrasynq/SpectraSynq_K1_Firmware/tools/serial-studio/K1-Dual-UART-Observability.ssproj`  
Title: `K1 Dual UART Observability`. `schemaVersion` 3. `writerVersion` / `writerVersionAtCreation` **4.0.3**. `nextUniqueId` 70.

Intent from `README.md` + `apply_engineering_project.py` + `TELEMETRY_SCHEMA.md`: dual UART acquire/parse/plot/record. Dashboard = awareness. Device clocks + offline Python = authority. `SCHEMA_V2.md` is **design-only** (`device_us` + `frame_seq` hot) and is **not** in either `.ssproj`.

| # | Group title | uniqueId | widget | datasets | source |
| --- | --- | --- | --- | --- | --- |
| 0 | K1 Bench B489A500 | 1 | `multiplot` | 27 | sourceId 0, USB serial `B4:3A:45:A5:89:B4`, stored port `cu.usbmodem1401` |
| 1 | K1 Main RPL 9087A500 | 17 | `multiplot` | 25 | sourceId 1, USB serial `B4:3A:45:A5:87:90`, stored port `cu.usbmodem12201` |
| 2 | 3D Plot | 35 | `plot3d` | 3 (X/Y/Z) | dummy; not K1 slots |
| 3 | 3D Plot (2) | 39 | `plot3d` | 3 (X/Y/Z) | dummy |
| 4 | Data Grid | 43 | `datagrid` | **0** | empty placeholder |
| 5 | 3D Plot (3) | 44 | `plot3d` | 3 (X/Y/Z) | dummy; firmware `groupId` 5 |
| 6 | Multiple Plot | 48 | `multiplot` | 1 (`New FFT Plot`) | spectacle leftover |

**Designed workspaces** (`apply_engineering_project.py` `ensure_workspaces`): Timing, Audio/AP, Renderer (Bench `multiplot`), Dual-device sync (Main `multiplot`), Experiment state (`datagrid`). Exported file also keeps Serial Studio defaults: Overview, All Data, plus one workspace per group (including empty Data Grid). Experiment state in the export points at **uniqueId 43** (empty Data Grid), not Bench.

**Actions (both copies):** Poll B489A500 / Poll 9087A500, `txData` `:event_status\n:fps\n:led_fps`, 250 ms, `repeatCount` 3, `autoExecuteOnConnect` true. Firmware `timerMode` **0**. Live `timerMode` **1**. GATE vs OBSERVE: README says GATE disables the 250 ms polls; neither copy was re-classified here.

## LED / FFT / 3D widgets

Not a real LED plate, not an FFT instrument, not a 3D K1 view.

**LED (`led: true`, two datasets only):**

1. Bench `unused_slot_17` — `index` 0 (unwired remnant), `led` true, `waterfall` true. Golden fixture `historical_slot_bug.json` names these unused slots as leftover “New Dataset” rows. They must **not** take parser slot 16/17 (`device_ms` / `frame_ms`).
2. `Multiple Plot` / `New FFT Plot` — `led` true, `fft` true, `waterfall` true, `index` 27.

No group uses widget type `led`. **LED FPS** is a numeric dataset (parser slot 14), not an LED widget.

**FFT:** `fft: true` only on `New FFT Plot`. `apply_engineering_project.py` `pin_fft_rates` forces `fft: false` on Bench/Main and stamps **declared** `fftSamplingRate` 133 (Bench AP) / 4 (Main poll). Dummy 3D/FFT groups stay at 100. `TELEMETRY_SCHEMA.md`: that number is an axis label, not a measured sample rate. Authoritative spectra stay offline.

**3D:** three `plot3d` groups, each X/Y/Z with widget `x`/`y`/`z`. No alias, no K1 field, `index` 18–26. `SCHEMA_V2.md` “Not now: dashboard spectacle.” Matches.

## Dataset count

**62 datasets** in both copies (`datasetId` grep = 62).

| Group | n | Titles (Bench/Main measurement set) |
| --- | --- | --- |
| Bench | 27 | BPM, Beat conf, Lock, Beat, Onset, Bass onset, Silence, AGC gain, Peak scaled, SSL, Energy, Novelty, System FPS, LED FPS, Lightshow, **unused_slot_16, unused_slot_17**, device_ms, frame_ms, parse_seq, event_tid, frame_dt_ms, host_device_skew_ms, host_parse_seq, record_kind, update_mask, transport_residual_ms |
| Main | 25 | same measurements **without** unused_slot_16/17 |
| 3D × 3 | 9 | X, Y, Z each |
| Multiple Plot | 1 | New FFT Plot |

Virtual (both copies, both UARTs): `frame_dt_ms`, `host_device_skew_ms`, `transport_residual_ms`. No `alias` keys persisted (`s0_` / `s1_` from the apply script did not survive export).

## Parser contract (schema v1.1)

Canonical JS: `tools/serial-studio/parsers/k1_ap_parser.js`. **Byte-identical** `frameParserCode` is embedded on **both sources in both** `.ssproj` files. `var SCHEMA = 1.1`. Array length **21**. Empty / unknown / `[APCAP]` → `[]`, no seq bump.

| 1-based slot | Name | Class | Wire |
| --- | --- | --- | --- |
| 1–15 | bpm … lightshow | device | `[AP]` / `EVENT_STATUS` / `SYSTEM_FPS:` / `LED_FPS:` as in `SCHEMA_LOCK.md` |
| 16 | device_ms | device clock | `EVENT_STATUS t=` |
| 17 | frame_ms | device clock | `EVENT_STATUS frame_ms=` |
| 18 | host_parse_seq | parser-derived | every publish; **not** device `frame_seq` |
| 19 | event_tid | device | `EVENT_STATUS tid=` |
| 20 | record_kind | parser-derived | 1=AP 2=EVENT_STATUS 3=SYSTEM_FPS 4=LED_FPS 5=BUILD(`VERSION:`) |
| 21 | update_mask | parser-derived | bit *i* iff slot *i*+1 written this line |

Never invent: `firmware_sha`, `run_id`, `audio_frame_seq`, `AP_us`, `drop_count`, `device_us`, `frame_seq`. No `POLL` kind. Frame detection: delimited, `frameEnd` `\n`, `frameStart` `$` (legacy template; JS parser does not require `$`).

**Dashboard index bug (both copies, same):** Serial Studio `index` is 1-based parser slot. Bench leftover unused rows sit at `index` 0. Clocks then bind correctly at 16–19 **under the old title `parse_seq`**. Extra datasets titled `host_parse_seq` / `record_kind` / `update_mask` are at **index 20 / 21 / 22**. Parser only emits 21 slots, so:

- title `parse_seq` @ index 18 = actual `host_parse_seq` (right slot, wrong name)
- title `host_parse_seq` @ index 20 = actual `record_kind`
- title `record_kind` @ index 21 = actual `update_mask`
- title `update_mask` @ index 22 = **nothing** from the parser

Scorer must use `update_mask` / `record_kind` from the **parser vector**, not from those mis-titled dashboard rows. Held last-known in slots 1–19 is not a new measurement (`SCHEMA_LOCK.md`).

`k1_gate` table (firmware export): `tx`, `source`=1, `mode`=`OBSERVE`. Control script: `deviceWrite` shuttle, `delay(20)`, comment “replies via `io.getLatestFrame`”. **D19 demoted this shuttle.** Do not run it.

## Live Documents copy (read only)

Path: `/Users/spectrasynq/Documents/Serial Studio/Projects/K1 Dual UART Observability.ssproj`

Same title, schema 3, writer 4.0.3, `nextUniqueId` 70, **same 62 datasets**, same parser JS, same USB serial bind, same FFT rates, same LED/FFT/3D leftovers, same clock-title collision, same 14 workspace names.

**Intent match:** both are the K1 Dual UART observability instrument. Live is not a different dashboard product.

**Live-only drift (do not write back from this lane):**

| Item | Firmware export | Live Documents |
| --- | --- | --- |
| JSON indent | 2 spaces (`json.dumps(..., indent=2)` in `apply_engineering_project.py`) | 4 spaces (Serial Studio native save) |
| Lines | 2992 | 3014 |
| Groups | 7 (includes empty Data Grid uniqueId 43) | **6** (Data Grid **group object removed**; treeExpansion + workspace still name it) |
| 3D Plot (3) `groupId` | 5 | 4 (array shifted after drop) |
| Multiple Plot `groupId` | 6 | 5 |
| `timerMode` | 0 | **1** |
| `k1_gate` | tx, source, mode | + `last_error`, `last_reply` |
| Control script | generic `deviceWrite` / `getLatestFrame` shuttle | Cadence-era **`:chip_id` only**, `deviceWriteAndWait(..., "9087A500")`, `delay(50)` |
| Apply aliases | intended `s0_`/`s1_`, not in file | not in file |
| Documents writes | apply script writes firmware path + `Serial-Studio/examples/...`, **not** this Documents path | app-owned live project |

Workspace `Experiment state` still `groupId` 43 on both. Live **no longer has** that group in `groups[]` — dangling widget ref. Firmware still has the empty `datagrid`.

## Why firmware ~81 kB vs live ~112 kB

Not “firmware is missing widgets.” Dataset count is **identical (62)**. Parser is duplicated on two sources in **both** files.

1. **Pretty-print indent (load-bearing).** Firmware = Python `indent=2` API export. Live = app `indent=4`. That roughly doubles JSON whitespace. 2992 vs 3014 lines with ~10 extra spaces on each nested dataset field is tens of kilobytes — the observed ~81 kB → ~112 kB (~+38%) is that class, not a second dashboard.
2. **Live control script is one long string** (chip_id shuttle + wait contract). Firmware script is shorter (`deviceWrite` + `restart 1788153686`). Adds a few kilobytes, not the whole gap.
3. **Live table extras** (`last_error`, `last_reply`) and `timerMode` 1: small.
4. **Opposite tiny term:** firmware still stores the empty Data Grid group object; live dropped it. That makes firmware **slightly larger** in groups, so it cannot explain firmware being **smaller**.

This lane did not `stat` the files (no shell). Byte figures ~81 kB / ~112 kB are the operator sizes; line count + indent + script/table extras are the parsed cause.

`apply_engineering_project.py` `export_project()` is the reason a slimmer 2-space copy exists in the firmware repo at all. It never overwrites the Documents project. Re-running it would talk `:7777` — **forbidden** this lane (D19/D20).

## Authority vs this dashboard

| Layer | Job |
| --- | --- |
| Parser v1.1 | 21-slot vector; no invented device fields |
| Dashboard | awareness; may hold last-known; spectacle 3D/FFT/LED leftovers |
| Historian / CSV / raw bytes | record |
| Offline `scorer/` | verdict |
| `SCHEMA_V2.md` | not implemented |

EVIDENCE:

- Firmware project groups/widgets/workspaces/parser: `.../K1-Dual-UART-Observability.ssproj` (ends line 2992, indent 2, 7 groups, 62 `datasetId`, `timerMode` 0, `k1_gate` 3 registers, `deviceWrite` control script).
- Live project: `~/Documents/Serial Studio/Projects/K1 Dual UART Observability.ssproj` (ends line 3014, indent 4, 6 groups, 62 `datasetId`, `timerMode` 1, `k1_gate` 5 registers, chip_id `deviceWriteAndWait` script). Documents not modified.
- Parser + lock: `parsers/k1_ap_parser.js`, `SCHEMA_LOCK.md`, `TELEMETRY_SCHEMA.md` v1.1. Slot remnant: `tests/fixtures/historical_slot_bug.json`.
- Apply/export: `apply_engineering_project.py` `CLOCK_FIELDS`, `pin_fft_rates`, `ensure_workspaces`, `json.dumps(cfg, indent=2)` → firmware path + Serial-Studio examples, **not** Documents.
- Policy: firmware `README.md` (dashboard ≠ evidence); `SCHEMA_V2.md` (no dashboard spectacle; not flashed); EdgeAI `docs/mir/SERIAL_STUDIO.md` OBSERVE/RECORD; D19 shuttle demoted.

COMMAND: none. File reads + grep only. Do **not** `python3 apply_engineering_project.py`. Do **not** connect `:7777`. Do **not** open `/dev/cu.usbmodem*`. Do **not** edit Documents. Do **not** edit firmware C++. Do **not** run `scripts/gate_c0_cadence_silicon.py`.

METHOD_RISK: HOST-ONLY. Byte sizes ~81 kB/~112 kB not re-`stat`’d this process — cause is indent+live extras from the JSON itself. `timerMode` 0 vs 1 meaning was not re-derived from Serial Studio source this lane (poll enable vs one-shot is [INFERENCE] from README GATE/OBSERVE). Parser-vs-title index collision is in **both** copies; fixing it needs an orchestrator pass, not this read. Live USB `portName` strings are stored project fields, not a live `ioreg`. Cadence stays CLOSED.

NEXT: Leave Serial Studio as observe/record. Do not sync Documents ← firmware (would clobber live shuttle/table/timer and is not this lane). Do not repair the `:7777` shuttle (D19). Parser/scorer already know unused_slot_16/17. Clock **title** remap (parse_seq vs host_parse_seq vs record_kind) is a later HOST dashboard fix if Captain wants plots to match SCHEMA_LOCK names — not C1, not silicon.

Ship path: (1) already on disk: this receipt + both `.ssproj` as parsed. (2) remaining: no project copy, no USB, no apply script. (3) who: nobody this lane. (4) shipped for this ask when this file exists; product flash is out of scope.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:grok | Parse firmware vs live SS project; 62 datasets; v1.1 parser; indent explains 81k vs 112k. |
