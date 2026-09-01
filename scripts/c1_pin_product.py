#!/usr/bin/env python3
"""C1 look prep: exclusive identity + Waveform Tempo pin on product firmware.

Does not play audio. Does not inject :c0_hex. Does not flash. Does not stamp
LGP_PERCEPTUAL_VALIDATED. Serial Studio must already have released USB-CDC.
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from edgeai.serial_studio import (  # noqa: E402
    holder_is_serial_studio,
    refuse_if_serial_studio_owns_usb,
)
from gate_c0_silicon import (  # noqa: E402
    EXPECT_CHIP,
    PALETTE_INDEX,
    find_port,
    identity_text,
    open_ser,
    pin_waveform_tempo,
    require_identity,
)

EXPECT_ENV = "k1_main_rpl_im69d"
EXPECT_GIT = "acaecaa8"
OUT = ROOT / "artifacts" / "gate_c1" / "PIN_RECEIPT.json"


def lsof_holders(device: str) -> list[str]:
    proc = subprocess.run(
        ["lsof", "-F", "c", device],
        capture_output=True,
        text=True,
        timeout=5,
    )
    names: list[str] = []
    for line in proc.stdout.splitlines():
        if line.startswith("c"):
            names.append(line[1:])
    return names


def main() -> int:
    port = find_port("/dev/cu.usbmodem12201")
    holders = lsof_holders(port)
    for name in holders:
        refuse_if_serial_studio_owns_usb(name, port)
        if holder_is_serial_studio(name):
            raise SystemExit(f"Serial Studio still owns {port}: {name}")
    ser = None
    try:
        ser = open_ser(port)
        text = identity_text(ser)
        ident = require_identity(text, expect_env=EXPECT_ENV)
        if ident["git"] and ident["git"] != EXPECT_GIT:
            raise SystemExit(f"git mismatch {ident['git']} != {EXPECT_GIT} (no flash from this script)")
        if ident["chip"] and ident["chip"] != EXPECT_CHIP:
            raise SystemExit(f"chip mismatch {ident['chip']} != {EXPECT_CHIP}")
        pin = pin_waveform_tempo(ser)
        receipt = {
            "status": "PINNED",
            "label": "C1_LOOK_PREP",
            "stamp": "not LGP_PERCEPTUAL_VALIDATED",
            "port": port,
            "identity": ident,
            "expect": {"chip": EXPECT_CHIP, "env": EXPECT_ENV, "git": EXPECT_GIT},
            "pin": {
                "mode_ordinal": 18,
                "dense_index": pin["dense_index"],
                "palette": PALETTE_INDEX,
            },
            "serial_studio_holders": holders,
            "audio": False,
            "ffplay": False,
            "c0_hex": False,
            "probe_flash": False,
            "song": {
                "title": "Regard — Ride It",
                "path": "/Users/spectrasynq/Workspace_Management/Software/YT_Saver/Regard_Ride_It.mp3",
                "duration_s": 157.632,
            },
            "unix": time.time(),
        }
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(receipt, indent=2) + "\n")
        print(json.dumps(receipt, indent=2), flush=True)
        return 0
    finally:
        if ser is not None:
            try:
                ser.close()
            except Exception:
                pass
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
