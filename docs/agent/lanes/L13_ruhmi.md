---
abstract: "L13: COMPILE_RECEIPT vs D9/D11. PRE-SILICON C99 MATCH. Pin 6c5aad901a1a41e28f6e306bfc35c44659e89502 + gcc-13/libstdc++. ad01 then AdaptiveAvgPool2d smoke on GHA 33319114336. ReduceMean fail 33318864219. Not ON-SILICON."
---

# L13 — RUHMI COMPILE_RECEIPT vs D9 / D11

**HARD FAIL (`SAME_SONG_LOOP_MAX_15MIN`).** No room audio. No USB. Cadence CLOSED. Compiler metrics are not board numbers.

| Field | Value |
| --- | --- |
| STATUS | PASS (MATCH) |
| CLAIM | `docs/ruhmi/COMPILE_RECEIPT.md` MATCH D9 (full SHA pin + MERA `2.6.0+pkg.4815` + gcc-13/libstdc++ in CI + ad01 then smoke) and D11 (AdaptiveAvgPool2d smoke C99; ReduceMean C99 fail). PRE-SILICON. Not ON-SILICON. No latency. |
| EVIDENCE | `docs/ruhmi/COMPILE_RECEIPT.md`; `docs/DECISIONS.md` D9/D11; `.github/workflows/ruhmi-compile.yml` `RUHMI_REF`; `deployment/ra8p1/Dockerfile` same SHA; `src/edgeai/semantic_v0.py` `nn.AdaptiveAvgPool2d((1,1))`; public GHA [33319114336](https://github.com/synqing/SpectraSynq-EdgeAI-Lab/actions/runs/33319114336) Success, [33318864219](https://github.com/synqing/SpectraSynq-EdgeAI-Lab/actions/runs/33318864219) Failure |
| COMMAND | `rg -n '6c5aad901a1a41e28f6e306bfc35c44659e89502|AdaptiveAvgPool2d|33319114336|33318864219|gcc-13' docs/ruhmi/COMPILE_RECEIPT.md docs/DECISIONS.md .github/workflows/ruhmi-compile.yml deployment/ra8p1/Dockerfile src/edgeai/semantic_v0.py` |
| METHOD_RISK | RAM/Flash/MACs are `check_model_metrics.py` restated in both docs — this lane did **not** re-download GHA artefacts or re-run MERA. Equality is document+workflow+public run status, not a new compile. gcc-13/libstdc++ is in D9 + workflow + Dockerfile, not the receipt table — silence, not contradiction. |
| NEXT | Do not treat 768 B / 262414 B RAM as Titan. Cadence stays CLOSED. Revisit D11 only if a later MERA/Vela keeps that MEAN as one NPU region. Do not invent board numbers. |

## D9 vs receipt (pin, host, order)

| D9 chosen | Receipt / CI | Verdict |
| --- | --- | --- |
| Clone RUHMI at `6c5aad9` | Receipt + `RUHMI_REF` + Dockerfile = `6c5aad901a1a41e28f6e306bfc35c44659e89502` (Release-2026-06-19). D9 body: short SHA `grep -qx` died on run 33318276254; pin is full hash + equality | MATCH (short form is docs-only) |
| MERA `2.6.0+pkg.4815` | Receipt pin line; workflow `MERA_WHEEL` | MATCH |
| `ppa:ubuntu-toolchain-r/test` + `libstdc++6`/`libgcc-s1` + gcc-13 | Workflow step “Upgrade libstdc++ / gcc-13”; Dockerfile same PPA. Why: 33317047371 `fe_onnx_cli` missing GLIBCXX_3.4.31/32 | MATCH. Receipt does not repeat gcc-13 |
| Compile `ad01_int8.tflite` **then** `smoke.onnx` | Workflow jobs: ad01 `--npu --ref-data` then smoke `--npu --quantize --ref-data`. Receipt table same order | MATCH |
| Pass run 33319114336 | Receipt: GHA 33319114336 on `03d6352`. Public run: Success, 3m1s, commit `03d6352b062d…` “Replace ReduceMean with AdaptiveAvgPool2d…”, artefacts `ruhmi-ad01` 701 KB, `ruhmi-c99` 3.73 MB, `smoke-onnx` 1.09 MB | MATCH. Artefacts generated, not in git |

## D11 vs receipt (pool, fail, pass numbers)

| D11 | Receipt | Verdict |
| --- | --- | --- |
| Fail 33318864219: ad01 OK; smoke quantized PSNR 27.8, 94.7% NPU ops; Vela `More than one Ethos-U custom operator`; cause `x.mean` → ReduceMean | Receipt “Prior fail (33318864219)… ReduceMean… D11”. Public run: Failure, exit 1 on ruhmi job; only artefact `smoke-onnx` (no `ruhmi-c99`) | MATCH. Fail SRAM 250 KiB / flash 186.92 KiB / 35.6M MACs live in D11 only — not claimed as pass numbers |
| Chosen: `nn.AdaptiveAvgPool2d((1,1))` + flatten | `src/edgeai/semantic_v0.py` `self.pool = nn.AdaptiveAvgPool2d((1, 1))`. `tests/test_shapes.py` forbids ONNX `ReduceMean`, requires `GlobalAveragePool` or `AveragePool` | MATCH |
| Pass 33319114336 smoke: RAM 262,414 B, Flash 188,896 B, 35.56 M MACs, 88.9% node coverage | Receipt table: 262,414 B / 188,896 B / 35.56 M / 88.9% (64/72, 8 CPU fallback) / C99 yes. ad01: 768 B / 217,968 B / 0.26 M / 100% (32/32) | MATCH. Receipt adds 64/72 split + ad01 row; D11 pass paragraph omits ad01 bytes |
| PRE-SILICON; not on-silicon; no latency | Receipt: “These numbers come from `check_model_metrics.py`. They are **not** board measurements.” “Not ON-SILICON. No latency claim.” | MATCH |

## Not a D9/D11 contradiction (adjacent drift)

- `docs/onnx_graph_semantic_v0.json` still lists `ReduceMean: 1` and “NOT_MEASURED” NPU. Stale dump vs live graph + D11. Out of this compare; L14 owns pool grep.
- `docs/MODEL_CONTRACT.md` Deployment “CPU fallback \| NOT_MEASURED” while the **smoke** receipt records 8 CPU nodes. Contract also says U55 accuracy/latency NOT_MEASURED — do not promote smoke 88.9% as product U55.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:grok | L13 contract. Receipt MATCH D9 pin + D11 pool. PRE-SILICON. |
| 2026-08-31 | agent:grok | Re-derived vs public GHA 33319114336 Success / 33318864219 Failure; field table. |
