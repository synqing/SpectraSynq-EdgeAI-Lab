# Current v1 Project — Guardrail Audit

This audit is expected to FAIL because the existing project contains historical/shuttle-era configuration.

Guardrail unit tests: **10 passed**.

```text
WARN: changeDrivenTransforms=false; acceptable, but revisit if v2 becomes transform-heavy
ERROR: controlScriptCode contains forbidden token 'deviceWrite('
ERROR: controlScriptCode contains forbidden token 'deviceWriteAndWait('
ERROR: controlScriptCode contains forbidden token 'k1_gate'
ERROR: forbidden shared table present: k1_gate
ERROR: K1 Bench B489A500: autoReconnect=true forbidden in profile passive
ERROR: K1 Main RPL 9087A500: autoReconnect=true forbidden in profile passive
ERROR: Poll B489A500: autoExecuteOnConnect=true forbidden in profile passive
ERROR: Poll B489A500: timerMode=1 forbidden in profile passive
ERROR: Poll 9087A500: autoExecuteOnConnect=true forbidden in profile passive
ERROR: Poll 9087A500: timerMode=1 forbidden in profile passive
ERROR: K1 Bench B489A500/Beat: transient event configured as LED annunciator; use event timeline/raster
ERROR: K1 Bench B489A500/Onset: transient event configured as LED annunciator; use event timeline/raster
ERROR: K1 Bench B489A500/Bass onset: transient event configured as LED annunciator; use event timeline/raster
ERROR: K1 Bench B489A500/unused_slot_16: forbidden dead-slot dataset
ERROR: K1 Bench B489A500/unused_slot_17: forbidden dead-slot dataset
ERROR: K1 Bench B489A500/unused_slot_17: FFT/Waterfall enabled without cadence allowlist
ERROR: K1 Bench B489A500/frame_dt_ms: virtual transform has no explicit dataset/table dependency; virtual value is not sibling telemetry
ERROR: K1 Bench B489A500/host_device_skew_ms: virtual transform has no explicit dataset/table dependency; virtual value is not sibling telemetry
ERROR: K1 Bench B489A500/unused_slot_22: forbidden dead-slot dataset
ERROR: K1 Bench B489A500/transport_residual_ms: virtual transform has no explicit dataset/table dependency; virtual value is not sibling telemetry
ERROR: K1 Bench B489A500: MultiPlot mixes incompatible semantic classes ['boolean_event', 'boolean_state', 'normalized', 'normalized_or_unknown', 'tempo'] from ['BPM', 'Beat conf', 'Lock', 'Beat', 'Onset', 'Bass onset', 'Silence', 'AGC gain', 'Peak scaled', 'Energy', 'Novelty']
ERROR: K1 Main RPL 9087A500/Beat: transient event configured as LED annunciator; use event timeline/raster
ERROR: K1 Main RPL 9087A500/Onset: transient event configured as LED annunciator; use event timeline/raster
ERROR: K1 Main RPL 9087A500/Bass onset: transient event configured as LED annunciator; use event timeline/raster
ERROR: K1 Main RPL 9087A500/frame_dt_ms: virtual transform has no explicit dataset/table dependency; virtual value is not sibling telemetry
ERROR: K1 Main RPL 9087A500/host_device_skew_ms: virtual transform has no explicit dataset/table dependency; virtual value is not sibling telemetry
ERROR: K1 Main RPL 9087A500/unused_slot_22: forbidden dead-slot dataset
ERROR: K1 Main RPL 9087A500/transport_residual_ms: virtual transform has no explicit dataset/table dependency; virtual value is not sibling telemetry
ERROR: K1 Main RPL 9087A500: MultiPlot mixes incompatible semantic classes ['boolean_event', 'boolean_state', 'normalized', 'normalized_or_unknown', 'tempo'] from ['BPM', 'Beat conf', 'Lock', 'Beat', 'Onset', 'Bass onset', 'Silence', 'AGC gain', 'Peak scaled', 'Energy', 'Novelty']
ERROR: Overview: dangling widgetRef groupId=43
ERROR: All Data: dangling widgetRef groupId=43
ERROR: Data Grid: dangling widgetRef groupId=43
ERROR: Audio/AP: identical widget-ref set to workspace 'Timing'; fake shell workspace
ERROR: Renderer: identical widget-ref set to workspace 'Audio/AP'; fake shell workspace
ERROR: Experiment state: dangling widgetRef groupId=43
ERROR: Experiment state: identical widget-ref set to workspace 'Data Grid'; fake shell workspace
RESULT errors=36 warnings=1
```
