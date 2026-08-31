# L14 — smoke.onnx AdaptiveAvgPool (D11)
HOST-ONLY. No USB. Cadence CLOSED.
STATUS: PASS
CLAIM: SemanticV0 (smoke.onnx) and ShareStudent use nn.AdaptiveAvgPool2d((1,1)); neither uses spatial tensor.mean / ONNX ReduceMean (D11).
EVIDENCE: src/edgeai/semantic_v0.py:67; src/edgeai/share_student.py:162; tests/test_shapes.py:24–35; tests/test_share_student.py:154–160; docs/DECISIONS.md §D11
COMMAND: pytest tests/test_shapes.py::test_onnx_export_avoids_reducemean tests/test_share_student.py::test_student_four_sources_adaptive_avg_pool_not_tensor_mean
METHOD_RISK: src/ grep + existing tests; AdaptiveAvgPool2d exports as GlobalAveragePool/AveragePool. Stale docs/onnx_graph_semantic_v0.json still counts ReduceMean.
NEXT: Keep D11. Do not reintroduce x.mean(dim=(2,3)). GHA 33319114336 C99 is PRE-SILICON, not ON-SILICON.
GRAPH: smoke = Conv/ReLU/AdaptiveAvgPool2d/Gemm/Sigmoid (BN folded).
SCOPE: experiment/toolchain graph, not frozen student I/O.
