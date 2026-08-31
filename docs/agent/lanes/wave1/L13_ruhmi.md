---
abstract: "L13: COMPILE_RECEIPT vs D9/D11. PRE-SILICON C99 MATCH. Pin 6c5aad901a1a41e28f6e306bfc35c44659e89502. AdaptiveAvgPool2d smoke, not ReduceMean. Not ON-SILICON."
---

# L13 — RUHMI COMPILE_RECEIPT vs D9 / D11

**HARD FAIL (`SAME_SONG_LOOP_MAX_15MIN`).** No room audio. PRE-SILICON only. Compiler metrics are not board numbers.

| Field | Value |
| --- | --- |
| STATUS | PASS |
| CLAIM | `docs/ruhmi/COMPILE_RECEIPT.md` matches D9 (full SHA pin + MERA 2.6.0+pkg.4815 + ad01 then smoke on GHA 33319114336) and D11 (AdaptiveAvgPool2d smoke C99; ReduceMean fail 33318864219). Still PRE-SILICON. Not ON-SILICON. No latency. |
| EVIDENCE | `docs/ruhmi/COMPILE_RECEIPT.md`; `docs/DECISIONS.md` D9/D11; `.github/workflows/ruhmi-compile.yml` `RUHMI_REF`; `src/edgeai/semantic_v0.py` `nn.AdaptiveAvgPool2d((1,1))` |
| COMMAND | `rg -n '6c5aad901a1a41e28f6e306bfc35c44659e89502|AdaptiveAvgPool2d|33319114336|33318864219' docs/ruhmi/COMPILE_RECEIPT.md docs/DECISIONS.md .github/workflows/ruhmi-compile.yml` |
| METHOD_RISK | Receipt restates compiler `check_model_metrics.py` output, not silicon. gcc-13/libstdc++ lives in D9 + workflow, not the receipt table — not a contradiction. smoke 8/72 CPU fallback is recorded, not invented SRAM. |
| NEXT | Do not treat 768 B / 262414 B RAM as Titan. Cadence silicon stays CLOSED. Revisit D11 only if a later MERA/Vela accepts ReduceMean as one NPU region. |

D9 vs receipt: pin `6c5aad901a1a41e28f6e306bfc35c44659e89502` (short `6c5aad9` is docs-only; D9 records `grep -qx 6c5aad9` fail on 33318276254). MERA `2.6.0+pkg.4815`. Order ad01 then smoke. Workflow installs `ppa:ubuntu-toolchain-r/test` + gcc-13 as D9 chose.

D11 vs receipt: fail 33318864219 ReduceMean / Vela split; pass 33319114336 AdaptiveAvgPool2d smoke RAM 262,414 B, Flash 188,896 B, 35.56 M MACs, 88.9% (64/72). ad01 768 B / 217,968 B / 0.26 M / 100% (32/32). Those bytes are compiler-reported.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:grok | L13 contract. Receipt MATCH D9 pin + D11 pool. PRE-SILICON. |
