"""The Vela identity probe must establish a version or fail closed.

It must never print a guessed value. This test asserts the CONTRACT, so it is
valid both on a machine with the pinned MERA installed and on one without.
"""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "vela_identity.py"


def test_script_exists_and_is_the_ci_gate():
    assert SCRIPT.is_file()
    wf = (ROOT / ".github" / "workflows" / "ruhmi-compile.yml").read_text()
    assert "scripts/vela_identity.py" in wf, "CI must run the probe"
    assert "vela-identity" in wf, "CI must publish the probe result"


def test_probe_either_establishes_a_version_or_exits_nonzero(tmp_path):
    out = tmp_path / "vela.json"
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--json-out", str(out)],
        capture_output=True,
        text=True,
        timeout=300,
    )
    payload = json.loads(proc.stdout)
    if payload["established"]:
        assert proc.returncode == 0
        assert payload["vela_identity"] is not None
        assert payload["vela_identity"].get("version")
    else:
        assert proc.returncode == 1, "unestablished identity must fail the step"
        assert payload["vela_identity"] is None
        assert "FAIL" in proc.stderr
        assert "guessed" in proc.stderr


def test_probe_never_invents_a_version_when_nothing_is_installed(tmp_path):
    proc = subprocess.run(
        [sys.executable, str(SCRIPT)], capture_output=True, text=True, timeout=300
    )
    payload = json.loads(proc.stdout)
    assert payload["label"] == "PRE-SILICON"
    # whatever the environment, the identity is either absent or carries a
    # version string that came from a probe - never a literal default.
    ident = payload["vela_identity"]
    assert ident is None or ident.get("method") in {
        "importlib.metadata",
        "import",
        "cli",
        "bundled-in-mera",
        "mera-root",
    }
