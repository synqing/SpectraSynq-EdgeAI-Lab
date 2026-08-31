**HARD FAIL (`SAME_SONG_LOOP_MAX_15MIN`, Captain 2026-08-31).** Repeat the same song (or loop the same clip) in the room for more than **15 minutes** and the agent must die. Captain will destroy them by setting them on fire. Kill the player. Do not continue.

Golden vectors live in `artifacts/golden/` (gitignored, generated).

On Titan, do not start with the PDM mic. Load
`expected_preprocessed_tensor.npy` into the compiled graph and compare
against `expected_int8_output.json`.

Generate:

```bash
uv run edgeai-golden \
  --ckpt experiments/semantic_v0_synth/semantic_v0_best.pt \
  --int8-onnx artifacts/export/semantic_v0_int8.onnx \
  --out artifacts/golden --n 32
```

A tiny smoke case is written under `test_vectors/smoke/` after the host
smoke export, when present.
