---
abstract: "Pinned import of firmware effect-semantics at 36466cd5. Firmware file is authority if they disagree."
---

# Pinned firmware export

Copied from the Atlas worktree after tranche-1 generation.

- `firmware_sha`: `36466cd56c90b9cafa571bc5029b5d38bc0543bb`
- `generation_status`: `tranche2_grammar_tempo`
- Also pinned: `compatibility.json`, `grammar_coverage.json`
- Source: `SpectraSynq_K1_Firmware/.worktrees/effect-response-atlas/docs/effect-response-atlas/generated/`
- Consume with `source_firmware_sha` **and** `atlas_artifact_sha256` (Atlas can move while firmware SHA stays put).

If this folder and the firmware generated files disagree, **delete this pin and recopy**. Do not edit mode behaviour here.

How to use: [../EFFECT_SEMANTICS_CONSUME.md](../EFFECT_SEMANTICS_CONSUME.md)

---
**Document Changelog**
| Date | Author | Change |
| --- | --- | --- |
| 2026-08-31 | agent:edgeai | First pin of firmware Atlas export. |
