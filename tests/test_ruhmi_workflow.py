from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WF = ROOT / ".github" / "workflows" / "ruhmi-compile.yml"

# Release-2026-06-19. Short "6c5aad9" is not what `git rev-parse HEAD` prints.
FULL = "6c5aad901a1a41e28f6e306bfc35c44659e89502"


def test_ruhmi_ref_is_full_sha_not_short_grep():
    text = WF.read_text()
    assert f"RUHMI_REF: {FULL}" in text
    assert 'grep -qx "${RUHMI_REF}"' not in text
    assert "rev-parse HEAD)\" = \"${RUHMI_REF}\"" in text
    assert "ad01_int8.tflite" in text
    assert "ppa:ubuntu-toolchain-r/test" in text


def test_dockerfile_pins_same_sha():
    docker = (ROOT / "deployment" / "ra8p1" / "Dockerfile").read_text()
    assert f"RUHMI_REF={FULL}" in docker
    assert "rev-parse HEAD)" in docker
