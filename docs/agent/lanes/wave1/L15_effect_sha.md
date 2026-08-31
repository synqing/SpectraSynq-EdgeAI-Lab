---
abstract: "L15: lab effect-semantics pin vs firmware SHA 36466cd5. Dual-hash PASS on three files; live Atlas worktree HEAD is not that commit."
---

# L15 — effect-semantics consume SHA

STATUS: PASS_PIN
CLAIM: `docs/mir/effect_semantics/{effect-semantics,compatibility,grammar_coverage}.json` all carry `schema_version=2`, `generation_status=tranche2_grammar_tempo`, `generated_at=2026-08-30T20:10:46Z`, and `source_firmware_sha`=`atlas_generation_commit`=`36466cd56c90b9cafa571bc5029b5d38bc0543bb` (D15/D16 pin). Artifact SHA256s: `ac9552cb8ee4d9b3…` / `fedf156ac4513c74…` / `e447e4b636d5ab2a…`. Branch `docs/effect-response-atlas` is that commit. CONSUME dual-hash rule holds on the three pinned files. Firmware-generated copies at the named Atlas path show the same provenance tail.
EVIDENCE: `/Users/spectrasynq/SpectraSynq-EdgeAI-Lab/docs/mir/EFFECT_SEMANTICS_CONSUME.md`; `/Users/spectrasynq/SpectraSynq-EdgeAI-Lab/docs/mir/effect_semantics/`; `/Users/spectrasynq/SpectraSynq_K1_Firmware/.worktrees/effect-response-atlas/docs/effect-response-atlas/generated/`; `/Users/spectrasynq/SpectraSynq_K1_Firmware/.git/refs/heads/docs/effect-response-atlas`
COMMAND: JSON field-read + git ref read. No USB. No `k1-flash`. No shasum this SSA (no shell).
METHOD_RISK: (1) Live worktree HEAD is `probe/c0-epoch-v2` @ `349d3cd49fabdc06c6e3c2782abc50d0cc931cf9`, not `36466cd5` — generated JSON still *labels* 36466cd5. (2) `atlas_artifact_sha256` is an in-file field, not a hash of the file-on-disk. (3) Byte-identity of lab vs firmware files inferred from first/last windows + line counts, not `shasum -a 256`.
NEXT: Recopy missing generated files (`inventory.json`, `static_levers.json`, `fingerprints.json`, `tempo_sweeps.json`) from commit `36466cd5`, not from live worktree HEAD. `fingerprints.json` is schema 1 and has no dual-SHA. Do not edit mode behaviour in EdgeAI. L16 owns competing-taxonomy grep.
USB: none (lane closed)
LOOP: none

---
**Document Changelog**
| Date | Author | Change |
| --- | --- | --- |
| 2026-08-31 | agent:grok-l15 | Consume SHA vs firmware pin 36466cd5. |
