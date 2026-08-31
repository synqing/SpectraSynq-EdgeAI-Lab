---
abstract: "Wave-2 harvest 2026-08-31. 40/40 SSAs finished. Cadence CLOSED. No USB. Claims are provisional unless the orchestrator re-ran them."
---

# Harvest — 40 HOST lanes wave 2

**HARD FAIL (`SAME_SONG_LOOP_MAX_15MIN`).** Cadence silicon **CLOSED**. No ffplay. No K1 USB.

Wave-2 IDs: `docs/agent/lanes/LAUNCHED.md`. Wave-1 copies: `docs/agent/lanes/wave1/`.

Orchestrator re-ran: HOST pytest 118 passed / 0 failed (L29). Other lanes **CONSUMED AS provisional** unless noted.

| ID | File | SSA status | One-line |
| --- | --- | --- | --- |
| L01 | L01_c1_scorecard.md | OPEN | Scorecard written. Stamp not applied. |
| L02 | L02_c1_protocol.md | MATCH | GATE_C1 is Captain-eyes, one full song, product firmware, ~31 Hz / 0 ms. |
| L03 | L03_contract_vs_receipt.md | MATCH | Frozen cadence numbers match cells. extra_gain range is in contract JSON, not cells. |
| L04 | L04_joint_fail.md | PASS | Must not assume 5 Hz and 50 ms together. r5_d50 Q1 0.245 FAIL. |
| L05 | L05_share_other.md | MATCH | Four-source including other. Verdict scores V/D/B; other kept. |
| L06 | L06_share_io.md | UNFROZEN | Student I/O open. Transport frozen for C1. Streaming student STOPPED. |
| L07 | L07_deam.md | CONSISTENT | Arousal r(RMS)=0.37 is not Gate A. |
| L08 | L08_parirset.md | MATCH | Onset delayed ~100 ms, not killed, 3 short IRs. |
| L09 | L09_registry.md | FAIL | 0 SHA pins; 13/23 UNKNOWN; YAML never stamps C0-v2 / cadence CLOSED. |
| L10 | L10_landscape.md | FAIL_MISMATCH | Landscape ≠ registry 1:1. MERT/MuQ/MAEST/Demucs still off Titan. |
| L11 | L11_essentia.md | CONSISTENT | MusiCNN arousal ≠ DEAM human. HOST-ONLY. |
| L12 | L12_source_activity.md | STALE→patched | File still said Gate C next. Orchestrator patched silicon close. |
| L13 | L13_ruhmi.md | PASS | Compile receipt matches D9/D11. PRE-SILICON. |
| L14 | L14_smoke_pool.md | PASS | AdaptiveAvgPool required. ReduceMean banned. STFT not on NPU. |
| L15 | L15_effect_sha.md | PASS_PIN | Lab pin has both consume SHAs. fingerprints.json SHA UNKNOWN. |
| L16 | L16_taxonomy.md | FAIL | 9-class/18-mode guidebook still claims canonical. Firmware pin is authority. |
| L17 | L17_serial_studio.md | PASS | D19: observe/record. Shuttle demoted. |
| L18 | L18_cadence_docs.md | MATCH | GATE_C0_CADENCE + AGENTS match CADENCE_RESULT. |
| L19 | L19_bose_cap.md | PASS | SAME_SONG_LOOP_MAX_S = 15*60. Test exists. |
| L20 | L20_hex32.md | PASS | load_trace is 32-char / 0.35 s. |
| L21 | L21_c0_corpse.md | PASS | Corpse FAIL vs live C0-v2 PASS. |
| L22 | L22_gate_c_stale.md | FAIL→patched | GATE_C FAIL paragraph looked live. Orchestrator labelled corpse. |
| L23 | L23_share_gate.md | CONSISTENT | Recoverability stamps match. SELECTION_GATE still has cadence-wait wording. |
| L24 | L24_semantic_v0.md | PASS | Still experiment. Do not freeze 16 kHz / 1 s / 3 sigmoids. |
| L25 | L25_model_contract.md | PASS | Semantic-v0 sheet blanks ≠ FROZEN_FOR_C1. |
| L26 | L26_licences.md | PASS | 13/23 UNKNOWN. None cleared. |
| L27 | L27_titan.md | PASS | PRE-SILICON. Ban 1 ms / 100 ms / 50 ms as Titan latency. |
| L28 | L28_host_py.md | PASS_WITH_GAPS | Pin 3.12.11 inside range. HOST.md names zero extras. |
| L29 | L29_pytest.md | PASS **verified** | 118 passed / 0 failed / 0 skipped. Orchestrator re-ran. |
| L30 | L30_pyproject.md | PASS | extras match lock. silicon extra = pyserial, not a port. |
| L31 | L31_handoff.md | FAIL→patched | HANDOFF serialised HOST until C1. Orchestrator applied D22. |
| L32 | L32_decisions.md | PASS | D20–D22 match AGENTS.md. |
| L33 | L33_host_vs_si.md | PASS | Host rehearsal ≠ silicon clock. |
| L34 | L34_p3c_q.md | MATCH | Holdout Q1–Q3 PASS both sides. Silicon stronger. |
| L35 | L35_demucs.md | PASS | Code MIT. Weights UNKNOWN. Not installed. Not Titan. |
| L36 | L36_stream_sketch.md | SKETCH | R XOR D. Never 5 Hz and 50 ms. Ban 1 s pool. |
| L37 | L37_comp_change.md | PARKED | Not next. C1 is next. |
| L38 | L38_usb_exclusive.md | GAP | Owned-USB raise untested. Do not live-USB-test. |
| L39 | L39_ss_tests.md | PASS | Tests match D19. Shuttle not reopened. |
| L40 | L40_cell_table.md | TABLE | Ten complete cells. Cadence CLOSED. |

## Orchestrator edits after harvest

- `docs/mir/GATE_C.md` — live C0 is C0-v2 PASS; two-clock FAIL labelled corpse; cadence CLOSED numbers.
- `docs/agent/HANDOFF.md` — D22 HOST sketches OPEN.
- `docs/mir/SOURCE_ACTIVITY.md` — silicon close recorded.

Left as FAIL for a later writer (not this harvest): registry SHA pins (L09), landscape map (L10), effect-decomposition “canonical” README (L16), optional owned-USB unit (L38).

## Still true

Cadence CLOSED. C1 OPEN. Do not stamp `LGP_PERCEPTUAL_VALIDATED` without Captain’s look. No 8 s loop. No USB steal.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:grok | Wave-2 40/40 harvest. |
