---
abstract: "HOST JSON parse of Serial Studio project K1 Dual UART Observability.ssproj (writer 4.0.3). LED Panel is unused_slot_17 because only that Bench dataset has led=true. 3D plots bind past/miswired parser slots. FFT dataset is titled New FFT Plot and also has led=true. Y-axis ~1.9e6 is update_mask bits on record_kind index 21. No USB."
---

# SS_LIVE_PROJECT — live `.ssproj` inventory

HOST-ONLY. Cadence CLOSED. No USB. Project file was **read**, not edited. Serial Studio was not launched. No `usbmodem`. No `:7777`.

**File:** `/Users/spectrasynq/Documents/Serial Studio/Projects/K1 Dual UART Observability.ssproj`  
**Stamp on disk:** `title` = `K1 Dual UART Observability`; `writerVersion` = `4.0.3`; `schemaVersion` = 3; `nextUniqueId` = 70; `plotTimeRange` = 10; `pointCount` = 100.

STATUS: PASS (inventory). Visual defects below are **project wiring**, not a live USB sample.

CLAIM: The dashboard looks empty/wrong because the JSON itself wires LED/FFT/3D to leftover and out-of-range slots, then autoscales a bitmask that sits near 1.9 million. Real AP/event fields are on the two `multiplot` groups; they are not the LED, FFT, or 3D widgets.

---

## 1. Top-level keys

[FACT] Eighteen keys, in file order:

| Key | What it is |
| --- | --- |
| `actions` | Two poll timers (Bench source 0, Main source 1) |
| `changeDrivenTransforms` | `false` |
| `controlScriptCode` | Parked `k1_gate` `:chip_id` shuttle (D19 demoted) |
| `customizeWorkspaces` | `true` |
| `groups` | Six dashboard groups |
| `hexadecimalDelimiters` | `false` |
| `mqttPublisher` | Present, `enabled: false` |
| `nextUniqueId` | 70 |
| `plotTimeRange` | 10 |
| `pointCount` | 100 |
| `schemaVersion` | 3 |
| `sources` | Two UART sources |
| `tables` | One table `k1_gate` |
| `title` | `K1 Dual UART Observability` |
| `treeExpansion` | UI tree open/closed flags |
| `widgetSettings` | Three stored widget configs |
| `workspaces` | 13 named windows |
| `writerVersion` / `writerVersionAtCreation` | `4.0.3` / `4.0.3` |

[FACT] `actions`: both `autoExecuteOnConnect: true`, `timerMode: 1`, `timerIntervalMs: 250`, `repeatCount: 3`, `txData: ":event_status\\n:fps\\n:led_fps"`. Source 0 titled `Poll B489A500`. Source 1 titled `Poll 9087A500`.

[FACT] `sources[0]`: title `K1 Bench B489A500`, `sourceId` 0, `cu.usbmodem1401`, serial `B4:3A:45:A5:89:B4`, VID `303A` PID `1001`.  
[FACT] `sources[1]`: title `K1 Main RPL 9087A500`, `sourceId` 1, `cu.usbmodem12201`, serial `B4:3A:45:A5:87:90`. Same parser body. `dtr: false` on both.

[FACT] Group-level `sourceId` appears **only** on `K1 Main RPL 9087A500` (`sourceId: 1`). Bench, all three 3D groups, and `Multiple Plot` omit `sourceId` → Serial Studio default **source 0 (Bench)**.

---

## 2. Groups and datasets

Parser return is 21 floats (`last` length 21, 0-based indices 0–20). Serial Studio `index` is **1-based** into that array, so valid `index` is 1–21. Parser comment in the project (both sources):

> 1-based slots: 1–15 device fields, 16–17 device clocks, 18 host_parse_seq, 19 event_tid, 20 record_kind, 21 update_mask.

Every dataset: `plotMin`/`plotMax`/`widgetMin`/`widgetMax`/`fftMin`/`fftMax` = **0** (autoscale). `ledHigh` = 80. Dataset `widget` is `""` except 3D `x`/`y`/`z`.

### Group 0 — `K1 Bench B489A500`

`uniqueId` 1 · `widget` `multiplot` · no `sourceId` (Bench) · 27 datasets.

| ds | title | index | units | graph | widget | fft | led | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | BPM | 1 | | true | | false | false | |
| 1 | Beat conf | 2 | | true | | false | false | |
| 2 | Lock | 3 | | true | | false | false | |
| 3 | Beat | 4 | | true | | false | false | |
| 4 | Onset | 5 | | true | | false | false | |
| 5 | Bass onset | 6 | | true | | false | false | |
| 6 | Silence | 7 | | true | | false | false | |
| 7 | AGC gain | 8 | | true | | false | false | |
| 8 | Peak scaled | 9 | | true | | false | false | |
| 9 | SSL | 10 | | true | | false | false | |
| 10 | Energy | 11 | | true | | false | false | |
| 11 | Novelty | 12 | | true | | false | false | |
| 12 | System FPS | 13 | Hz | true | | false | false | |
| 13 | LED FPS | 14 | Hz | true | | false | false | |
| 14 | Lightshow | 15 | | true | | false | false | |
| 15 | unused_slot_16 | **0** | | **false** | | false | false | unbound |
| 16 | unused_slot_17 | **0** | | **true** | | false | **true** | `waterfall: true` |
| 17 | device_ms | 16 | ms | true | | false | false | parser `t` |
| 18 | frame_ms | 17 | ms | true | | false | false | |
| 19 | parse_seq | 18 | | true | | false | false | **is** parser `parseSeq` (`last[17]`) |
| 20 | event_tid | 19 | | true | | false | false | |
| 21 | frame_dt_ms | **0** | | true | | false | false | virtual |
| 22 | host_device_skew_ms | **0** | | true | | false | false | virtual |
| 23 | host_parse_seq | **20** | | true | | false | false | **wires to record_kind** (`last[19]`) |
| 24 | record_kind | **21** | | true | | false | false | **wires to update_mask** (`last[20]`) |
| 25 | update_mask | **22** | | true | | false | false | **OOB** (array max index 21) |
| 26 | transport_residual_ms | **28** | | true | | false | false | virtual + **OOB** |

`fftSamplingRate` 133 on this group.

Title vs parser slot (Bench/Main, same shift):

| Dataset title | `index` | Actual parser cell |
| --- | --- | --- |
| parse_seq | 18 | host `parseSeq` |
| host_parse_seq | 20 | `record_kind` (1–5) |
| record_kind | 21 | `update_mask` bitmask |
| update_mask | 22 / 29 | past end of `last` |

### Group 1 — `K1 Main RPL 9087A500`

`uniqueId` 17 · `widget` `multiplot` · `sourceId` 1 · 25 datasets. **No** `unused_slot_*`. Same names/indices as Bench minus the two unused slots. `transport_residual_ms` is `index` **29** (worse OOB). `fftSamplingRate` **4** (not 133). All listed telemetry `graph: true`. Same virtual trio. Same title/index miswire.

### Group 2 — `3D Plot`

`uniqueId` 35 · `widget` `plot3d` · no `sourceId` → Bench · `graph: false` on all three.

| ds | title | index | widget | fft | led |
| --- | --- | --- | --- | --- | --- |
| 0 | X | **18** | x | false | false |
| 1 | Y | **19** | y | false | false |
| 2 | Z | **20** | z | false | false |

X = `parseSeq` (monotonic). Y = `event_tid`. Z = `record_kind` (1–5).

### Group 3 — `3D Plot (2)`

`uniqueId` 39 · `widget` `plot3d` · Bench default.

| ds | title | index | widget |
| --- | --- | --- | --- |
| 0 | X | **21** | x |
| 1 | Y | **22** | y |
| 2 | Z | **23** | z |

X = `update_mask`. Y and Z **OOB**.

### Group 4 — `3D Plot (3)`

`uniqueId` 44 · `widget` `plot3d` · Bench default.

| ds | title | index | widget |
| --- | --- | --- | --- |
| 0 | X | **24** | x |
| 1 | Y | **25** | y |
| 2 | Z | **26** | z |

All three **OOB**. Empty plot.

### Group 5 — `Multiple Plot`

`uniqueId` 48 · `widget` `multiplot` · Bench default · one dataset.

| ds | title | index | graph | fft | led | extra |
| --- | --- | --- | --- | --- | --- | --- |
| 0 | **New FFT Plot** | **27** | true | **true** | **true** | `waterfall: true` |

Index 27 is past the 21-cell frame. This is the **only** `fft: true` dataset in the whole project.

[FACT] There is **no** group with `widget` `led` / `fft` / `datagrid`. LED, FFT, and waterfall windows are spawned from dataset flags. Data Grid workspace refs `groupId` **43**, which is **not** in `groups[]` (uniqueIds present: 1, 17, 35, 39, 44, 48). That window is a dangling ref.

---

## 3. Dashboard widgets / windows

[FACT] `customizeWorkspaces: true`. Thirteen workspaces.

Workspace `widgetType` inferred from which `group.widget` / flag they attach to (not a named enum in the JSON):

| widgetType | Meaning in this file | Evidence |
| --- | --- | --- |
| 1 | Data Grid | workspaces titled Data Grid / Experiment state; `groupId` 43 missing |
| 2 | MultiPlot | groups with `"widget": "multiplot"` |
| 6 | 3D Plot | groups with `"widget": "plot3d"` |
| 7 | FFT Plot | only group 48, dataset with `fft: true` |
| 8 | LED Panel | groups that have a `led: true` dataset |
| 9 | per-dataset plot | one ref per `graph: true` dataset |
| 21 | Waterfall | datasets with `waterfall: true` |

| Workspace | What it mounts |
| --- | --- |
| Overview (5005) | Bench MultiPlot + **Bench LED** + Main MultiPlot + 3D×3 + Data Grid (dead 43) + Multiple Plot MultiPlot + **Multiple Plot LED** |
| All Data (5006) | Both MultiPlots, all per-dataset plots, Bench waterfall + LED, three 3D, dead Data Grid, Multiple Plot MultiPlot + **FFT (7)** + waterfall + **LED (8)** |
| K1 Bench B489A500 (5007) | Bench MultiPlot, dataset plots, waterfall, **LED** |
| K1 Main RPL 9087A500 (5008) | Main MultiPlot + dataset plots. **No LED, no FFT, no 3D** |
| 3D Plot (5009) | group 35, type 6 |
| 3D Plot (2) (5010) | group 39, type 6 |
| Data Grid (5011) | group 43, type 1 — **group missing** |
| 3D Plot (3) (5012) | group 44, type 6 |
| Multiple Plot (5013) | MultiPlot + FFT + waterfall + **LED** + leftover type-9 plots |
| Timing / Audio/AP / Renderer (5000–5002) | Bench MultiPlot only |
| Dual-device sync (5003) | Main MultiPlot only |
| Experiment state (5004) | dead Data Grid 43 |

[FACT] LED Panel appears in Overview, All Data, K1 Bench, and Multiple Plot — not as its own group.

[FACT] FFT (`widgetType` 7) appears **only** in All Data and Multiple Plot, always `groupId` 48.

[FACT] `widgetSettings` only stores MultiPlot `2:0:-1` (sweep on), MultiPlot `2:1:-1`, 3D `6:2:-1` (`autoCenter: true`). No LED/FFT settings.

---

## 4. Datasets titled `unused_slot_*`

[FACT] Exactly two, both on Bench only:

| title | uniqueId | index | graph | fft | led | waterfall |
| --- | --- | --- | --- | --- | --- | --- |
| unused_slot_16 | 33 | 0 | false | false | false | absent |
| unused_slot_17 | 34 | 0 | true | false | **true** | **true** |

They do **not** map to parser slots 16–17. Those slots are `device_ms` / `frame_ms`. `index: 0` is unbound. Names are leftover 16-slot chrome. Tree flags exist under `Dashboard Widgets/K1 Bench B489A500/unused_slot_16` and `.../unused_slot_17`.

---

## 5. Datasets with `graph: true`

[FACT] `graph: false` only on: `unused_slot_16` and all nine 3D X/Y/Z fields.

Everything else is `graph: true`, including `unused_slot_17`, `New FFT Plot`, `parse_seq`, miswired `record_kind`, OOB `update_mask`, virtual timing fields.

So each device MultiPlot autoscales **BPM (~tens–hundreds)** on the **same Y axis** as `parseSeq` (unbounded), `device_ms` (uptime), and `record_kind` (actually the bitmask).

---

## 6. Y-axis / min/max that can explode to ~1.9 million

[FACT] No dataset stores a 1.9e6 `plotMax`. All mins/maxes are 0 → **autoscale**.

[FACT] Parser `publish()` always does:

```
mask |= (1 << 17) | (1 << 19) | (1 << 20);
```

That is `131072 + 524288 + 1048576 = 1,703,936`.

On `EVENT_STATUS`, `tid` sets bit 18 (`1 << 18 = 262144`):

`1,703,936 + 262,144 = 1,966,080` ≈ **1.9 million**.

Other EVENT_STATUS keys add smaller bits (beat/onset/t/frame_ms/…). Ceiling if bits 0–20 all set: `2,097,151`.

[FACT] Dataset titled `record_kind` is `index` **21** → `last[20]` → **that bitmask**, `graph: true`, on both MultiPlots.

[INFERENCE] The live Y-axis that jumps to ~1.9e6 is that series (and 3D Plot (2) X, same index 21), not BPM. `update_mask` the dataset is index 22/29, off the end, so the **named** mask plot may sit at 0 while the **named** `record_kind` plot carries 1.9e6.

Secondary large series if autoscale shares an axis: `parse_seq` (monotonic parse count) and `device_ms` (`t` in ms; ~32 min uptime is also ~1.9e6). Those are real clocks/counters, not a 1.9e6 *limit* baked in JSON.

---

## 7. Why an LED Panel shows only `unused_slot_17`

[FACT] `led: true` exists on **two** datasets in the whole project: Bench `unused_slot_17`, and `New FFT Plot` in group `Multiple Plot`.

[FACT] Serial Studio does not define an LED group. It builds an LED Panel from `led: true` inside a group.

[FACT] Bench workspaces (Overview, All Data, K1 Bench) mount `widgetType` 8 on `groupId` 1. That group’s only LED dataset is `unused_slot_17`. Every real AP/event field has `led: false`. `unused_slot_16` is `led: false`, so it does not appear.

[FACT] `unused_slot_17` has `index: 0` (no parser cell). The LED is leftover chrome, not a K1 status bit. `ledHigh: 80` never meets a bound slot.

[INFERENCE] Captain sees one LED labeled `unused_slot_17` because that is the only LED the Bench group is allowed to emit. The Main group has zero `led: true` datasets, so Main never gets an LED Panel.

---

## 8. Why 3D plots are empty except one squiggle

[FACT] Three `plot3d` groups, all defaulting to Bench (no `sourceId`). None of X/Y/Z is a spatial field. Parser never writes accelerometer-style X/Y/Z.

| Window | Indices | What the 21-cell frame actually supplies |
| --- | --- | --- |
| 3D Plot | 18, 19, 20 | X = rising `parseSeq`; Y = `event_tid` (0 or sparse); Z = kind 1–5 |
| 3D Plot (2) | 21, 22, 23 | X = bitmask ~1.7–2.1e6; Y,Z off the array |
| 3D Plot (3) | 24, 25, 26 | all off the array |

[INFERENCE] Plot 1 is the squiggle: a line walking out the X axis as parse count grows, with Y/Z almost flat. Plot 2 has at most one live axis. Plot 3 is empty. `graph: false` on XYZ only hides them from MultiPlot; the 3D widget still consumes those indices.

---

## 9. Why FFT appears as “New FFT Plot” inside an LED Panel

[FACT] There is no group titled FFT. The only FFT-enabled dataset is titled **`New FFT Plot`** (`uniqueId` 49), inside group **`Multiple Plot`**.

[FACT] That one dataset sets **all four** of `fft: true`, `led: true`, `graph: true`, `waterfall: true`. `index: 27` is off the 21-cell frame.

[FACT] Workspaces All Data and Multiple Plot mount, from `groupId` 48, `widgetType` 7 (FFT), 21 (waterfall), and 8 (LED) together. Overview mounts the same group’s LED (`widgetType` 8) **without** the FFT pane.

[INFERENCE] Serial Studio names the FFT window after the dataset (`New FFT Plot`). Because `led: true` is on that same dataset, the LED Panel for `Multiple Plot` is a single LED **also labeled `New FFT Plot`**. Overview/All Data place that LED next to other panes, so the FFT series appears to live inside an LED Panel. The FFT is not a K1 spectrum: it is an unbound slot 27 on Bench, `fftSamplingRate` 100, 256 samples.

---

## Parser slot map (both sources, identical JS)

`last = [21 zeros]`. `[AP]` writes bpm, conf, lock, beat, onset, bass, silence, agc_gain, peak_scaled, SSL, lightshow. `EVENT_STATUS` writes beat, onset, bass, sil, energy, nov, conf, `t`, `frame_ms`, `tid`. `SYSTEM_FPS:` → slot 13. `LED_FPS:` → slot 14. `VERSION:` publishes kind 5 with no extra cells. Empty/unknown → `[]` (no seq bump).

This inventory did not execute the parser. It did not open a port.

---

## STATUS / CLAIM / EVIDENCE / COMMAND / METHOD_RISK / NEXT

STATUS: PASS as a JSON inventory. Dashboard LED/3D/FFT behaviour is explained by this file alone.

CLAIM: Live Serial Studio chrome is leftover: one Bench LED (`unused_slot_17`), three 3D plots bound to parseSeq/mask/OOB, one FFT dataset named `New FFT Plot` that is also an LED, and MultiPlot Y autoscaling a bitmask (~1,966,080) sitting on the dataset titled `record_kind`.

EVIDENCE: Path above. `led: true` count = 2 (`unused_slot_17`, `New FFT Plot`). `fft: true` count = 1 (`New FFT Plot`). `plot3d` groups = 3, indices 18–26 vs frame length 21. `publish()` mask bits 17+19+20 = 1,703,936; plus tid bit 18 = 1,966,080. `groups[].sourceId` only on Main. `groupId` 43 referenced, not defined.

COMMAND: none. `python3 -c` was not required; the file is JSON and was read in place. Do not open Serial Studio. Do not connect USB. Do not edit the `.ssproj` from this lane.

METHOD_RISK: HOST-ONLY parse. `widgetType` numbers are inferred from group flags in *this* project, not from Serial Studio C++ headers. `index: 0` treated as unbound per SS convention and this parser’s 1-based comment — not re-derived against the 4.0.3 binary. Port names in `sources` are last-saved device IDs, not a live `lsof`. Shuttle script in `controlScriptCode` is parked (D19); this lane did not call it.

NEXT: Leave the `.ssproj` as evidence. Do not “fix” Serial Studio in this lane. Observe/record only (`docs/mir/SERIAL_STUDIO.md`). Cadence stays CLOSED. If someone later rebuilds the dashboard, drop `unused_slot_*`, clear `led`/`fft`/`waterfall` off junk datasets, bind 3D to real XYZ or delete those groups, split MultiPlot so bitmask/counters do not share BPM’s axis, and retitle `parse_seq`/`host_parse_seq`/`record_kind`/`update_mask` to the parser cells they actually read.

HARD FAIL: `SAME_SONG_LOOP_MAX_15MIN`. No USB multiplex. Cadence runner retired.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:grok | Created: full `.ssproj` inventory; LED/3D/FFT/1.9e6 wiring from JSON only. |
