---
abstract: "HOST contract: Serial Studio Pro 4 dashboard JSON for LED panel, FFT, 3D plot, multiplot. No yAxis/zAxis keys. 3D axes are dataset.widget x|y|z. K1 Dual UART example. No USB."
---

# Serial Studio Pro 4 widget JSON contract

HOST-ONLY. Cadence CLOSED. Serial Studio observe/record. This file is a field map, not a USB or `:7777` procedure.

STATUS: PASS

CLAIM: Pro 4 binds LED, FFT, 3D, and multiplot from **group** `widget` + **dataset** flags, not from `yAxis` / `zAxis` JSON keys. Those two keys **do not exist** on group or dataset. 3D axes are `dataset.widget` `"x"` / `"y"` / `"z"`. LED and FFT are dataset booleans; LED is then auto-aggregated into a synthetic panel. Multiplot is `group.widget: "multiplot"` and plots **every** dataset in that group.

EVIDENCE: Serial Studio `app/src/DataModel/FrameKeys.h`; `Generated/DatasetSerialization.cpp`; `Frame.h` group `serialize`/`read`; `SerialStudio.cpp` `getDashboardWidget` / `getDashboardWidgets`; `UI/Dashboard/WidgetMapBuilder.cpp`; `UI/Dashboard.cpp` `configurePlot3DSeries`; `doc/help/Widget-Reference.md`; examples `K1 Dual UART/K1-Dual-Observability.ssproj`, `EM Wave Simulator/EMWaveSimulator.ssproj`, `LorenzAttractor/LorenzAttractor.ssproj`, `HexadecimalADC/HexadecimalADC.ssproj`, `Sparkplug Example/Sparkplug Edge Node.ssproj`.

COMMAND: none. Do not open Serial Studio. Do not bind `:7777`. Do not touch USB-CDC.

METHOD_RISK: HOST file read of Serial Studio + this repo. Not live dashboard. Widget-Reference still says LED config is `graph: true` for multiplot in one table and “plots every dataset” in Plots.md; C++ `configureMultiLineSeries` walks **all** `group.datasets` and does not filter on `graph`. Help `graph` vs C++ `plt` is the same flag: JSON key is `graph`.

NEXT: When an EdgeAI `.ssproj` needs these tiles, set the fields below. Do not invent `yAxis` / `zAxis`. Do not treat K1 Dual UART’s extra 3D/FFT groups as wired K1 spatial/spectrum channels.

---

## Two layers

| Layer | JSON home | What it does |
| --- | --- | --- |
| Group widget | `groups[].widget` | One composite tile for the group: `multiplot`, `plot3d`, `datagrid`, `accelerometer`, `gyro`/`gyroscope`, `gps`/`map`, `barpanel`, `webview`, `image`, `painter`, or `""` |
| Dataset flags / widget | `groups[].datasets[]` | Per-channel tiles and axis tags |

Parser values land in `datasets[].index` (**1-based** column in the parsed frame). Identity for XY / waterfall / workspace refs is `uniqueId`, not `datasetId` (reorder-stable).

C++ field names that differ from JSON:

| JSON | C++ |
| --- | --- |
| `graph` | `Dataset.plt` |
| `xAxis` | `Dataset.xAxisId` |
| `plotMin` / `plotMax` | `pltMin` / `pltMax` |
| `widgetMin` / `widgetMax` | `wgtMin` / `wgtMax` |
| `led` / `fft` | same |

There is **no** `Keys::YAxis` or `Keys::ZAxis`. Closest relatives: `xAxis` (2D plot X source) and `waterfallYAxis` (Pro waterfall Y source).

---

## Field dictionary (the names you asked)

### `groups[].widget`

String. Selects the **group** dashboard widget.

| Value | Dashboard tile | Licence |
| --- | --- | --- |
| `"multiplot"` | Multi-Plot | GPL |
| `"plot3d"` | 3D Plot | **Pro**. Without Pro, WidgetMapBuilder remaps the group to Multi-Plot titled `"(title) (Fallback)"` |
| `"datagrid"` | Data Grid | GPL |
| `""` / omitted | no group tile (`DashboardNoWidget`) | — |

LED Panel is **not** a value you write here. Runtime synthetic widget string is `"led-panel"` after aggregation.

### `groups[].datasets[]`

Array of dataset objects. Group serialize always writes this array (`Frame.h` `serialize(Group)`).

### `datasets[].widget`

String. Two unrelated uses:

1. **Dataset-scope tiles** (editor combo): `""`, `"bar"`, `"gauge"`, `"compass"`, `"meter"`. These spawn Bar/Gauge/Compass/Meter. They do **not** spawn FFT, LED, Plot, or 3D.
2. **Axis / role tags** consumed by a group widget:
   - 3D Plot / Accelerometer: `"x"` / `"y"` / `"z"` (case-insensitive X/Y/Z)
   - GPS: `"lat"` / `"lon"` / `"alt"`
   - Gyroscope: `"x"`/`"pitch"`, `"y"`/`"roll"`, `"z"`/`"yaw"`

3D binding is **only** this tag. Not `xAxis`/`yAxis`/`zAxis`.

### `datasets[].fft`

Bool. Default false. `true` auto-creates an **FFT Plot** (KissFFT). Companion fields:

| JSON | Default | Meaning |
| --- | --- | --- |
| `fftSamples` | 256 | Window, power of 2, 8…262144 |
| `fftWindow` | 5 | 5 = Blackman-Harris |
| `fftSamplingRate` | 100 | Hz for the frequency axis (must match real rate) |
| `fftMin` / `fftMax` | 0 / 0 | Frequency-axis range; if equal, dashboard copies `plotMin`/`plotMax` |
| `waterfall` | omitted/false | Pro spectrogram; reuses FFT settings |
| `waterfallYAxis` | 0 (time) | Other dataset `uniqueId` for order tracking |

### `datasets[].led`

Bool. Default false. `true` contributes one lamp to a **LED Panel** auto-built per owning group (`WidgetMapBuilder`: title `LED Panel ({group.title})`).

| JSON | Default | Meaning |
| --- | --- | --- |
| `ledHigh` | 80 | On-threshold **only if** `alarmBands` is empty |
| `alarmBands[]` | omitted | `{min, max, severity, color?, label?, blink?}`. Severity 0 Info / 1 OK / 2 Warning / 3 Critical. First matching band wins. `blink` flashes the LED |

Without bands: on (dataset colour) when value ≥ `ledHigh`. With bands: colour/label/blink from the active band; outside every band the LED is off.

### `datasets[].xAxis`

Int. C++ `xAxisId`. **2D Plot X source only.** Multi-Plot shared X is Time or Samples from the **first** dataset; custom XY is Plot-only (`Plots.md`).

| Value | Meaning |
| --- | --- |
| `-2` | Time (default, `kXAxisTime`) |
| `-1` | Sample index (`kXAxisSamples`) |
| `≥ 0` | `uniqueId` of another dataset (XY / scatter) |

### `yAxis` / `zAxis`

**Not project keys.** Do not write them. 3D Y/Z = `datasets[].widget` `"y"` / `"z"`. Waterfall Y = `waterfallYAxis`.

### `datasets[].graph`

Bool. Default false. `true` auto-creates a **single-curve Plot**. Multi-Plot does **not** require it: C++ plots every dataset in a `multiplot` group. Help still recommends setting `graph: true` so the same channels also get individual plots.

### Other group keys that bind data

| JSON | Meaning |
| --- | --- |
| `title` | Group name (required on load) |
| `uniqueId` | Stable group id |
| `sourceId` | I/O source (omitted = 0). K1 Dual UART Main group sets `1` |
| `index` (dataset) | 1-based parser slot. `0` = unused / virtual |
| `virtual` | Transform-only; not a parser column |

---

## How each target widget is instantiated

```
.ssproj groups[]
        │
        ├─ group.widget == "multiplot"  → DashboardMultiPlot  (all datasets in group)
        ├─ group.widget == "plot3d"     → DashboardPlot3D     (Pro; else MultiPlot fallback)
        │                                 axes from dataset.widget x|y|z; missing axis = 0
        └─ for each dataset:
              fft:true  → DashboardFFT  (one FFT tile per such dataset)
              led:true  → collected into synthetic DashboardLED group "led-panel"
              graph:true → DashboardPlot
```

Code: `SerialStudio::getDashboardWidget(Group)` and `getDashboardWidgets(Dataset)`; `WidgetMapBuilder::buildWidgetGroups` / `processDatasetIntoWidgetMaps`; `Dashboard::configurePlot3DSeries` matches `dataset.widget` to `"x"`/`"X"`, `"y"`/`"Y"`, `"z"`/`"Z"` and points at `numericValue`.

Control-script `ensureDashboard` uses JS flags `plot` / `fft` / `led` (not the JSON names). API `project.dataset.setOptions` slugs: `plot`, `fft`, `bar`, `gauge`, `compass`, `led`, `waterfall`. Bitfield 1=Plot, 2=FFT, 4=Bar, 8=Gauge, 16=Compass, 32=LED, 64=Waterfall.

---

## Minimal JSON shapes

### Multi-Plot

```json
{
  "title": "K1 Bench",
  "widget": "multiplot",
  "datasets": [
    { "title": "BPM", "index": 1, "uniqueId": 2, "graph": true, "fft": false, "led": false, "widget": "", "xAxis": -2 }
  ]
}
```

### LED Panel (no group.widget for LED)

```json
{
  "title": "Flags",
  "widget": "datagrid",
  "datasets": [
    { "title": "Lock", "index": 3, "led": true, "ledHigh": 1, "widget": "", "xAxis": -2 }
  ]
}
```

Sparkplug example uses `led: true` + `ledHigh: 1` on booleans.

### FFT Plot

```json
{
  "title": "ADC",
  "widget": "multiplot",
  "datasets": [
    {
      "title": "ADC 0",
      "index": 1,
      "fft": true,
      "fftSamples": 256,
      "fftSamplingRate": 200,
      "fftWindow": 5,
      "fftMin": 0,
      "fftMax": 5,
      "graph": false,
      "led": false,
      "widget": "",
      "xAxis": -2
    }
  ]
}
```

HexadecimalADC sets `fft: true` on six ADC channels inside a `multiplot` group.

### 3D Plot (Pro)

```json
{
  "title": "3D Visualization",
  "widget": "plot3d",
  "datasets": [
    { "title": "X", "index": 1, "widget": "x", "graph": false, "fft": false, "led": false, "xAxis": -2 },
    { "title": "Y", "index": 2, "widget": "y", "graph": false, "fft": false, "led": false, "xAxis": -2 },
    { "title": "Z", "index": 3, "widget": "z", "graph": false, "fft": false, "led": false, "xAxis": -2 }
  ]
}
```

Lorenz + EM Wave Simulator match this. EM Wave also sets `xAxis` on 3D datasets to **other uniqueIds**; 3D ingest **ignores** `xAxis` and only reads `widget` tags + `numericValue`. Those `xAxis` values are leftover / unused for the 3D tile.

---

## K1 Dual UART (`examples/K1 Dual UART/K1-Dual-Observability.ssproj`)

Parser `k1_ap_parser.js` publishes 21 0-based slots → dataset `index` 1…21 (BPM…update_mask). Schema comment: 1–15 device, 16–17 clocks, 18 host_parse_seq, 19 event_tid, 20 record_kind, 21 update_mask.

| Group `title` | `widget` | `sourceId` | Binding |
| --- | --- | --- | --- |
| K1 Bench B489A500 | `multiplot` | omitted → 0 | `graph: true` on telemetry; `fftSamplingRate` 133 |
| K1 Main RPL 9087A500 | `multiplot` | `1` | same layout |
| 3D Plot | `plot3d` | 0 | datasets `widget` x/y/z, `index` 18/19/20 = host_parse_seq / tid / record_kind — **not** spatial XYZ |
| 3D Plot (2) | `plot3d` | 0 | `index` 21/22/23 |
| 3D Plot (3) | `plot3d` | 0 | `index` 24/25/26 — **past** parser length |
| Data Grid | `datagrid` | 0 | `datasets: []` |
| Multiple Plot | `multiplot` | 0 | one dataset `"New FFT Plot"`: `fft: true`, `led: true`, `waterfall: true`, `graph: true`, `index`: 27 — **unwired** |

LED: `led: true` on Bench `unused_slot_17` (`index` 0) and on `"New FFT Plot"`. Not on Lock/Beat/Onset. FFT: only that extra dataset. 3D groups are editor shells, not K1 IMU.

---

## What not to do

- Do not add `"yAxis"` / `"zAxis"` to `.ssproj` expecting 3D binding.
- Do not set `groups[].widget` to `"led"`, `"fft"`, or `"led-panel"` in the project file. LED panel is synthesized; FFT is a dataset flag.
- Do not set `dataset.widget` to `"fft"` or `"led"`; those strings are dashboard icon ids, not dataset combo values.
- Do not treat `xAxis` as the 3D X coordinate.
- Do not multiplex USB with Serial Studio (D19). This contract does not open a port.

---

**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:grok | Created: Pro 4 LED/FFT/3D/multiplot JSON bind from Serial Studio source + K1 Dual UART. |
