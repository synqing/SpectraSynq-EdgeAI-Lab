#!/usr/bin/env python3
"""Establish the ACTUAL Arm Ethos-U Vela identity behind the pinned RUHMI/MERA
compile path, by introspection. Never by assumption.

Why this exists: `docs/ruhmi/COMPILE_RECEIPT.md` pins ruhmi-framework-mcu
6c5aad90... (Release-2026-06-19) and MERA 2.6.0+pkg.4815, but records NOTHING
about the Vela version underneath. Vela 5.0.0 (26/02/2026) changed the U55
operator set (it added INT8 BATCH_MATMUL for U55/U65). "June 2026 postdates
February 2026" is an inference, not a pin. This script refuses to guess.

Exit codes
  0  a Vela identity was established (printed as JSON on stdout)
  1  no Vela identity could be established -> the CI step must fail

Usage
  python scripts/vela_identity.py [--ruhmi-dir DIR] [--json-out FILE]
"""

from __future__ import annotations

import argparse
import importlib
import importlib.metadata as md
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

MAX_SCAN_FILES = 200_000


def _probe_distributions() -> list[dict]:
    found = []
    for dist in md.distributions():
        try:
            name = (dist.metadata["Name"] or "").strip()
        except Exception:
            continue
        if not name:
            continue
        low = name.lower()
        if "vela" in low or "ethos" in low:
            found.append({"method": "importlib.metadata", "name": name, "version": dist.version})
    return found


def _probe_import() -> list[dict]:
    out = []
    for mod in ("ethosu.vela", "ethosu.vela.vela"):
        try:
            m = importlib.import_module(mod)
        except Exception:
            continue
        ver = getattr(m, "__version__", None)
        if ver is None:
            try:
                ver = md.version("ethos-u-vela")
            except Exception:
                ver = None
        out.append(
            {
                "method": "import",
                "name": mod,
                "version": ver,
                "path": getattr(m, "__file__", None),
            }
        )
    return out


def _probe_cli() -> list[dict]:
    exe = shutil.which("vela")
    if not exe:
        return []
    try:
        v = subprocess.check_output([exe, "--version"], encoding="utf-8", timeout=60).strip()
    except Exception as exc:  # noqa: BLE001
        return [{"method": "cli", "name": exe, "version": None, "error": repr(exc)}]
    return [{"method": "cli", "name": exe, "version": v}]


def _probe_bundled_in_mera() -> list[dict]:
    try:
        mera = importlib.import_module("mera")
    except Exception:
        return []
    out: list[dict] = []
    roots = [Path(p) for p in getattr(mera, "__path__", [])]
    seen = 0
    hits: list[Path] = []
    for root in roots:
        for f in root.rglob("*"):
            seen += 1
            if seen > MAX_SCAN_FILES:
                break
            n = f.name.lower()
            if "vela" in n or ("ethos" in n and f.is_file()):
                hits.append(f)
    for h in hits[:40]:
        entry = {"method": "bundled-in-mera", "name": str(h), "version": None}
        if h.is_file() and h.suffix in {".py", ".txt", ".json", ".cfg", ".ini", ".dist-info"}:
            try:
                blob = h.read_text(errors="ignore")[:200_000]
                m = re.search(r"(?:version|__version__)\s*[:=]\s*[\"']?([0-9]+\.[0-9]+\.[0-9]+)", blob, re.I)
                if m:
                    entry["version"] = m.group(1)
            except Exception:  # noqa: BLE001
                pass
        out.append(entry)
    if roots:
        out.append({"method": "mera-root", "name": str(roots[0]), "version": getattr(mera, "__version__", None)})
    return out


def _ruhmi_vela_config(ruhmi_dir: Path | None) -> dict:
    """The compile path's own Vela knobs, read from the pinned mcu_compile.py."""
    if not ruhmi_dir:
        return {}
    src = ruhmi_dir / "scripts" / "mcu_compile.py"
    if not src.is_file():
        return {"error": f"not found: {src}"}
    blob = src.read_text(errors="ignore")
    out: dict = {"source": str(src)}
    m = re.search(r"['\"]accel_config['\"]\s*:\s*['\"]([^'\"]+)['\"]", blob)
    if m:
        out["accel_config"] = m.group(1)
    m = re.search(r"default\s*=\s*['\"](Sram_Only|Shared_Sram|Dedicated_Sram[^'\"]*)['\"]", blob)
    if m:
        out["default_memory_mode"] = m.group(1)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ruhmi-dir", type=Path, default=None)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args()

    probes: list[dict] = []
    for fn in (_probe_distributions, _probe_import, _probe_cli, _probe_bundled_in_mera):
        try:
            probes.extend(fn())
        except Exception as exc:  # noqa: BLE001
            probes.append({"method": fn.__name__, "error": repr(exc)})

    versioned = [p for p in probes if p.get("version")]
    established = bool(versioned)

    try:
        mera_version = importlib.import_module("mera").__version__
    except Exception:
        mera_version = None

    result = {
        "label": "PRE-SILICON",
        "established": established,
        "vela_identity": versioned[0] if versioned else None,
        "all_probes": probes,
        "mera_version": mera_version,
        "ruhmi_vela_config": _ruhmi_vela_config(args.ruhmi_dir),
        "note": (
            "Vela version alone never promotes an operator into an architectural "
            "assumption. Candidate graphs still compile or fail."
        ),
    }
    text = json.dumps(result, indent=2, sort_keys=True)
    print(text)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(text + "\n")

    if not established:
        print(
            "\nFAIL: no Ethos-U Vela identity/version could be established from the "
            "installed compile path. Do NOT record a guessed value in "
            "docs/ruhmi/COMPILE_RECEIPT.md.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
