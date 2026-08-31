STATUS: PASS
CLAIM: Two-clock C0 corpse stays FAIL (`INVALID_TEMPORAL_EXECUTION`); C0-v2 is the PASS (`ON_SILICON_PIXEL_VALIDATED`). Same binding. Do not promote corpse via lag.
EVIDENCE: `artifacts/gate_c0/C0_RESULT.json` (`c0=FAIL`, Q1 0.13, Q2/Q3 6/9, `+14 hops` diagnosis-only); `artifacts/gate_c0/CORPSE_MANIFEST.json` (89 files); `artifacts/gate_c0v2/C0V2_RESULT.json` (`c0v2=PASS`, Q1 0.83, Q2 Δ 0.69 9/9, Q3 Δ 0.58 9/9, `lag_corrected=false`, `retired_c0_untouched=true`).
COMMAND: none. HOST JSON read only. Did not run `gate_c0_silicon.py` / `p3c_quant` / lag search on corpse dumps.
METHOD_RISK: HOST-ONLY restatement of frozen receipts. Chip both `9087A500`. C0 probe git `acaecaa8`; C0-v2 probe git `349d3cd4`. Cadence CLOSED elsewhere — not this lane.
NEXT: leave `artifacts/gate_c0/` frozen. Authority is C0-v2. L22 owns GATE_C prose. No USB. No rescore.
PROOF: C0 `stamp=not ON_SILICON_PIXEL_VALIDATED` vs C0-v2 `stamp=source_share × WaveformTempo × head_position = ON_SILICON_PIXEL_VALIDATED`. Runner `scripts/gate_c0_silicon.py` RETIRED; successor `scripts/gate_c0v2_silicon.py`.
DOCTRINE: D17 two-clock FAIL; GATE_C0V2.md “Do not rescore it with +14 hops. Do not overwrite those dumps.” AGENTS.md source-ownership: two-clock corpse stays FAIL.
CORPSE: not rescored. Manifest SHA `C0_RESULT.json` `35075e7d244c20b5fd45e5969469d74d7e70fc04962ea593c58394e731265161`.
USB: none. No `/dev/cu.usbmodem*`. No audio. No 8 s loop.
