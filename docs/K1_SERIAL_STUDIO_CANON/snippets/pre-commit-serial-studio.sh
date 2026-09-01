#!/usr/bin/env bash
set -euo pipefail

PROJECT="${1:-tools/serial-studio/K1-Dual-UART-Observability-v2.ssproj}"
python3 tools/serial-studio/guardrails/lint_ssproj.py "$PROJECT" --profile passive
python3 -m pytest -q tools/serial-studio/guardrails/test_lint_ssproj.py
