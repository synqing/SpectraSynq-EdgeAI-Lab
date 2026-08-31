---
abstract: "L15: lab pin dual-hash PASS on three JSON files at firmware SHA 36466cd5. Live Atlas worktree HEAD is probe/c0-epoch-v2, not that commit. Four Atlas generated files not imported."
---

# L15 — effect-semantics consume SHA

HOST-ONLY. No USB. Cadence CLOSED.

STATUS: PASS_PIN
CLAIM: Lab pin `docs/mir/effect_semantics/` is consume-only. The three imported JSON files all carry CONSUME required fields: `schema_version=2`, `generation_status=tranche2_grammar_tempo`, `generated_at=2026-08-30T20:10:46Z`, `source_firmware_sha`=`firmware_sha`=`atlas_generation_commit`=`36466cd56c90b9cafa571bc5029b5d38bc0543bb` (D15/D16 pin), plus distinct `atlas_artifact_sha256` — `effect-semantics.json` `ac9552cb8ee4d9b3a65ab60dfdf63a86f12f62967f41d494ac91d7242f630b8d`; `compatibility.json` `fedf156ac4513c74ac424b8737e0aee797472a2203e9fbf5edc67c98b18615c0`; `grammar_coverage.json` `e447e4b636d5ab2a33b79cfe0cdc60c6e7a4c089e25c9870617fa7a244f56971`. Firmware-generated copies at the named Atlas path show the same provenance tail. Branch `docs/effect-response-atlas` is that commit. CONSUME “also” files are **not** in the lab pin: `inventory.json` / `static_levers.json` / `tempo_sweeps.json` exist only in firmware (dual-hash present, `generation_status` absent); `fingerprints.json` is schema 1 with **UNKNOWN** `source_firmware_sha` and **UNKNOWN** `atlas_artifact_sha256`.
EVIDENCE: `/Users/spectrasynq/SpectraSynq-EdgeAI-Lab/docs/mir/EFFECT_SEMANTICS_CONSUME.md`; `/Users/spectrasynq/SpectraSynq-EdgeAI-Lab/docs/mir/effect_semantics/{effect-semantics,compatibility,grammar_coverage}.json`; `/Users/spectrasynq/SpectraSynq-EdgeAI-Lab/docs/DECISIONS.md` D15/D16; `/Users/spectrasynq/SpectraSynq_K1_Firmware/.worktrees/effect-response-atlas/docs/effect-response-atlas/generated/`; `/Users/spectrasynq/SpectraSynq_K1_Firmware/.git/refs/heads/docs/effect-response-atlas`; `/Users/spectrasynq/SpectraSynq_K1_Firmware/.git/worktrees/effect-response-atlas/HEAD`; `/Users/spectrasynq/SpectraSynq_K1_Firmware/.git/refs/heads/probe/c0-epoch-v2`
COMMAND: JSON field-read of lab pin + firmware generated/ + git ref read. No USB. No `k1-flash`. No room audio. No `shasum`.
METHOD_RISK: (1) Live Atlas worktree HEAD is `probe/c0-epoch-v2` @ `349d3cd49fabdc06c6e3c2782abc50d0cc931cf9`, not `36466cd5` — generated JSON still *labels* 36466cd5. (2) `atlas_artifact_sha256` is an in-file field, not a hash of the file-on-disk. (3) Lab vs firmware identity inferred from matching provenance tails, not `shasum -a 256`. (4) `inventory.json` / `static_levers.json` / `tempo_sweeps.json` lack `generation_status` so a recopy would still miss one CONSUME required field.
NEXT: Recopy missing generated files from commit `36466cd5` (not live worktree HEAD). Do not edit mode behaviour in EdgeAI. L16 owns competing-taxonomy grep. Treat `fingerprints.json` SHA as UNKNOWN until a schema-2 export exists.
USB: none (lane closed)
LOOP: none
HARD FAIL: `SAME_SONG_LOOP_MAX_15MIN`

---
**Document Changelog**
| Date | Author | Change |
| --- | --- | --- |
| 2026-08-31 | agent:grok-l15 | Consume SHA vs firmware pin 36466cd5. |
| 2026-08-31 | agent:grok-l15 | Re-read pin + Atlas generated/; dual-hash PASS on three files; four extras unimported / fingerprints UNKNOWN. |
