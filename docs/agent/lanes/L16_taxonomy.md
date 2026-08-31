---
abstract: "L16 HOST-ONLY: firmware effect-semantics.json is the only allowed effect inventory. 9-class/18-mode guidebook still published as canonical. No USB."
---

# L16 — no competing taxonomy grep
HOST-ONLY. No USB. Cadence CLOSED.
STATUS: FAIL
CLAIM: Firmware pin is the only allowed inventory: `docs/mir/effect_semantics/effect-semantics.json` (`schema_version` 2, `source_firmware_sha` `36466cd56c90b9cafa571bc5029b5d38bc0543bb`, `generation_status` `tranche2_grammar_tempo`) lists **23** enabled `LIGHT_MODE_*` enums. D15 consume-only holds in that pin and in `docs/mir/EFFECT_SEMANTICS_CONSUME.md`. Competing **9-class / 18-mode** taxonomy is **still published**: `docs/effect-decomposition/README.md` abstract still calls the 2026-06-02 guidebook “the canonical reference” and the body still states “18 modes total; 10 product-enabled, 8 disabled” (table ids 0–17). SNAPSHOT.md already demotes the folder to conceptual prior; README was not updated. Stale claims vs pin: `01-waveform-class.md` still WIP on mode 18 (export: WAVEFORM TEMPO id 18, `enabled` true, `guidebook_fit` CURRENT_CHANGED); `04-comet-class.md` still claims sole live onset consumer (export `onset_beat` also on DENSE FORGE 21, PULSE PRISM 23, DENSE FORGE CHORD 24, PERCUSSION BURST 26); `LEVERS-MATRIX.md` Gap #1 still says `sb_tempo` unconsumed (export `tempo_fields` on WAVEFORM TEMPO and later tempo modes). `00b-captivation-transposition.md` still proposes Cannonade/Shockwave/Iris (plus Implosion/Chladni/Meniscus) — none appear in the pin. Export post-snapshot enabled modes (id≥18): WAVEFORM TEMPO (18) + PULSE PRISM (23) + 11 others (19,20,21,22,24,25,26,27,28,29,32). No BUILDING/DROPPING invented as lighting labels (prohibition text only). Students stay effect-agnostic.
EVIDENCE: `docs/mir/effect_semantics/effect-semantics.json`; `docs/mir/EFFECT_SEMANTICS_CONSUME.md`; `docs/DECISIONS.md` D15; `docs/effect-decomposition/{README,SNAPSHOT,LEVERS-MATRIX,00b-captivation-transposition,01-waveform-class,04-comet-class}.md`; `AGENTS.md` Effect-semantics lane
COMMAND: `rg -n 'canonical reference|18 modes total|Cannonade|supports_tempo|BUILDING|PulsePrism|WaveformTempo|LIGHT_MODE_' docs src mir tests AGENTS.md`
METHOD_RISK: Lab grep + JSON field-read only. Cadence CLOSED. No USB. Firmware Atlas tree not opened this lane. Bindings `WaveformTempo`/`PulsePrism` in D15/consume are aliases of export `WAVEFORM TEMPO`/`PULSE PRISM`, not a second inventory. MIR stem/mood ontologies are not lighting-effect taxonomies. `00b` already notes Gap #1 stale (2026-07-11) while README/LEVERS-MATRIX still publish unconsumed tempo.
NEXT: Do not author effect families here. Do not invent BUILDING/DROPPING. Recopy pin if Atlas disagrees. Competing 9-class/18-mode stays FAIL until README stops claiming canonical inventory.
HARD FAIL: `SAME_SONG_LOOP_MAX_15MIN`

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:grok | L16 competing-taxonomy grep vs firmware export. |
| 2026-08-31 | agent:grok-l16 | Re-grep: 9-class/18-mode still published; pin 23 enums @ 36466cd5. |
