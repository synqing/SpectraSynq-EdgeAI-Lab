#!/usr/bin/env python3
"""Thin wrapper so the Docker image always calls the pinned mcu_compile.py."""

from __future__ import annotations

import runpy
import sys
from pathlib import Path

SCRIPT = Path("/opt/ruhmi-framework-mcu/scripts/mcu_compile.py")
if not SCRIPT.is_file():
    sys.stderr.write(f"missing {SCRIPT}\n")
    raise SystemExit(2)
sys.argv = [str(SCRIPT), *sys.argv[1:]]
runpy.run_path(str(SCRIPT), run_name="__main__")
