---
abstract: "L16 HOST-ONLY: firmware effect-semantics.json is the only effect taxonomy. Guidebook tree still competes. No USB."
---

# L16 — no competing taxonomy grep
HOST-ONLY. No USB. Cadence CLOSED.
STATUS: FAIL
CLAIM: D15 consume-only holds in `docs/mir/effect_semantics/` (23 enums, `source_firmware_sha` `36466cd5`). `docs/effect-decomposition/` still competes: README calls the 2026-06-02 9-class / 18-mode table "canonical" (10 LIVE); 01-waveform still WIP on mode 18; 04-comet claims sole onset consumer; LEVERS-MATRIX Gap #1 says tempo unconsumed; 00b proposes Cannonade/Shockwave/Iris. Export has WAVEFORM TEMPO (18, enabled, CURRENT_CHANGED) plus PULSE PRISM (23) and 11 other post-snapshot modes. SNAPSHOT.md already demotes the folder. No BUILDING/DROPPING invented in code. Students stay effect-agnostic.
EVIDENCE: `docs/mir/effect_semantics/effect-semantics.json`; `docs/mir/EFFECT_SEMANTICS_CONSUME.md`; `docs/DECISIONS.md` D15; `docs/effect-decomposition/{README,SNAPSHOT,LEVERS-MATRIX,00b-captivation-transposition,01-waveform-class,04-comet-class}.md`
COMMAND: `rg -n 'canonical reference|Cannonade|supports_tempo|BUILDING|PulsePrism|WaveformTempo|LIGHT_MODE_' docs src mir tests AGENTS.md`
METHOD_RISK: Lab grep only; firmware Atlas tree not opened this lane. Bindings `WaveformTempo`/`PulsePrism` in D15/consume are aliases of export `WAVEFORM TEMPO`/`PULSE PRISM`, not a second inventory. MIR stem/mood ontologies are not lighting-effect taxonomies.
NEXT: Do not author effect families here. Recopy pin if Atlas disagrees. Do not invent BUILDING/DROPPING.
HARD FAIL: `SAME_SONG_LOOP_MAX_15MIN`

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:grok | L16 competing-taxonomy grep vs firmware export. |
