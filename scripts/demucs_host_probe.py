#!/usr/bin/env python3
"""HOST teacher probe for Demucs.

weights UNKNOWN; named GO required to install.

Never downloads. Never opens USB. Never Titan. Never ffplay.

If the demucs package is missing, print HOST-NOT-INSTALLED and exit 2.
Package presence is not a licence to construct Separator() (hub fetch).
"""

from __future__ import annotations

import argparse
import importlib.util
import json

EXIT_NOT_INSTALLED = 2
EXIT_REFUSED_NO_GO = 3


def demucs_package_present() -> bool:
    """True iff importlib can see a demucs distribution. Does not import it."""
    return importlib.util.find_spec("demucs") is not None


def probe_install_state() -> tuple[str, int]:
    """Presence-only. Never constructs a separator. Never fetches weights."""
    if not demucs_package_present():
        return "HOST-NOT-INSTALLED", EXIT_NOT_INSTALLED
    return "HOST-INSTALLED-NO-NAMED-GO", EXIT_REFUSED_NO_GO


def _receipt(status: str, installed: bool) -> dict[str, object]:
    return {
        "status": status,
        "label": "HOST-ONLY",
        "demucs_installed": installed,
        "weight_licence": "UNKNOWN",
        "named_go": False,
        "download": False,
        "separator_constructed": False,
        "usb": False,
        "titan": False,
        "ffplay": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "HOST Demucs teacher probe. Weights UNKNOWN. "
            "Named GO required to install. Never downloads."
        )
    )
    parser.parse_args(argv)

    status, code = probe_install_state()
    print(status, flush=True)
    print(json.dumps(_receipt(status, installed=code != EXIT_NOT_INSTALLED)), flush=True)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
