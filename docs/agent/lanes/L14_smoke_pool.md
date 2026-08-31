---
abstract: "L14: AdaptiveAvgPool2d is NOT banned for U55 smoke/student export. D11 requires it. ReduceMean and STFT-in-graph are banned. 1 s pool is a streaming-latency ban (L36), not a U55 op ban. PRE-SILICON."
---

# L14 — smoke.onnx AdaptiveAvgPool (D11)

HOST-ONLY / PRE-SILICON. No USB. Cadence CLOSED. No train. No 8 s loop.

| Field | Value |
| --- | --- |
| STATUS | **PASS** — AdaptiveAvgPool is **not** banned for U55 student/smoke export. It is the **required** pooling for the witness graph. |
| CLAIM | `nn.AdaptiveAvgPool2d((1,1))` is the D11 U55 export. Ban is `tensor.mean` / ONNX **ReduceMean** (Vela split, GHA 33318864219). Ban is also **STFT inside the NPU graph** (D3: export CNN on log-mel; golden tensors first, PDM last). A **1 s** AdaptiveAvgPool is banned only as a *streaming* student (L36 ~1 Hz latency), not as a U55 op. Semantic-v0 I/O is unfrozen (D8). |
| EVIDENCE | `docs/DECISIONS.md` D3 + D11; `src/edgeai/semantic_v0.py:67` `self.pool = nn.AdaptiveAvgPool2d((1, 1))` + header forbids `tensor.mean(dim=(2,3))`; `src/edgeai/share_student.py:162` same pool; `src/edgeai/frontend.py` STFT/mel stays off U55; `src/edgeai/golden.py` “Feed these log-mel tensors into the NPU before introducing live PDM”; `tests/test_shapes.py:24–35` asserts no `ReduceMean`, requires `GlobalAveragePool` or `AveragePool`; `tests/test_share_student.py:154–160`; `docs/ruhmi/COMPILE_RECEIPT.md` GHA 33319114336 AdaptiveAvgPool2d smoke C99 (RAM 262,414 B, Flash 188,896 B, 35.56 M MACs, 88.9%); `experiments/semantic_v0/AUTHORITY.md` ReduceMean banned; `docs/MODEL_CONTRACT.md` graph row AdaptiveAvgPool2d×1; `artifacts/smoke/smoke.onnx` present (receipt `ok: true`, opset 14, input `(1,1,64,100)`). Stale: `docs/onnx_graph_semantic_v0.json` still `ReduceMean: 1`; `docs/HOST_RECEIPTS.md` bootstrap table still lists ReduceMean (2026-08-31 update corrects). |
| COMMAND | not executed this SSA (docs+src+onnx presence only, no train). Gate that would load the live graph: `uv run pytest tests/test_shapes.py::test_onnx_export_avoids_reducemean tests/test_share_student.py::test_student_four_sources_adaptive_avg_pool_not_tensor_mean` |
| METHOD_RISK | Did not `onnx.load` `artifacts/smoke/smoke.onnx` (protobuf; Read refused binary). PyTorch AdaptiveAvgPool2d exports as ONNX GlobalAveragePool/AveragePool, not an AdaptiveAvgPool node. Stale JSON dump is ReduceMean — do not treat it as the live graph. GHA C99 is PRE-SILICON compiler metrics, not ON-SILICON. ShareStudent 1 s pool is experiment I/O, not a frozen student. |
| NEXT | Keep D11. Do not reintroduce `x.mean(dim=(2,3))`. Do not export STFT onto U55. Refresh `docs/onnx_graph_semantic_v0.json` from a live AdaptiveAvgPool export when someone next dumps the graph. Do not freeze student I/O. Cadence stays CLOSED. |

GRAPH (live PyTorch / MODEL_CONTRACT, BN folded): Conv / ReLU / AdaptiveAvgPool2d / Gemm / Sigmoid. Input log-mel `(1,1,64,100)`, not PCM.

SCOPE: U55-shaped **smoke** graph. Not architecture authority. Not Titan. Not ON-SILICON.

---
**Document Changelog**
| Date | Author | Change |
|------|--------|--------|
| 2026-08-31 | agent:edgeai | L14: AdaptiveAvgPool not banned for U55 export; ReduceMean + STFT-in-graph are. |
