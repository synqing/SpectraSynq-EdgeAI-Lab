#!/usr/bin/env bash
# PRE-SILICON. Compile an ONNX/TFLite model with RUHMI inside linux/amd64 Docker.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
MODEL="${1:-$ROOT/artifacts/export/semantic_v0_fp32.onnx}"
OUT="${2:-$ROOT/artifacts/ruhmi}"
CALIB="${3:-$ROOT/artifacts/export/calib_logmel.npy}"
IMAGE="${RUHMI_IMAGE:-spectrasynq-ruhmi:2.6.0}"

if [[ ! -f "$MODEL" ]]; then
  echo "missing model: $MODEL" >&2
  echo "run: uv run edgeai-export --ckpt experiments/semantic_v0_synth/semantic_v0_best.pt --out artifacts/export" >&2
  exit 2
fi

mkdir -p "$OUT"
MODEL_ABS="$(cd "$(dirname "$MODEL")" && pwd)/$(basename "$MODEL")"
OUT_ABS="$(cd "$OUT" && pwd)"
CALIB_ARGS=()
if [[ -f "$CALIB" ]]; then
  CALIB_ABS="$(cd "$(dirname "$CALIB")" && pwd)/$(basename "$CALIB")"
  CALIB_ARGS+=(--calib-data "/work/in/$(basename "$CALIB_ABS")")
fi

if ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
  echo "building $IMAGE (linux/amd64)…"
  docker build --platform linux/amd64 -t "$IMAGE" "$ROOT/deployment/ra8p1"
fi

WORKDIR_IN="$(dirname "$MODEL_ABS")"
docker run --rm --platform linux/amd64 \
  -v "$WORKDIR_IN:/work/in:ro" \
  -v "$OUT_ABS:/work/out" \
  "$IMAGE" \
  "/work/in/$(basename "$MODEL_ABS")" /work/out \
  --npu --quantize --ref-data \
  "${CALIB_ARGS[@]}"

echo "PRE-SILICON compile finished → $OUT_ABS"
echo "Inspect build/MCU/model_subgraphs.json and compilation/src/ before claiming U55 coverage."
