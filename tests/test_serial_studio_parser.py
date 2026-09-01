"""Differential tests for the frozen Serial Studio parser."""

from __future__ import annotations

import json
import math
import shutil
import subprocess
from pathlib import Path

import pytest

from edgeai.serial_studio_parser import LegacyK1ParserV12


ROOT = Path(__file__).resolve().parents[1]
JS_PARSER = ROOT / "tools/serial-studio/parsers/k1_observe_v1_2.js"
JS_RUNNER = ROOT / "tools/serial-studio/parsers/run_parser.js"
FIXTURE = ROOT / "tools/serial-studio/fixtures/parser-v1.2.json"


def _js_results(frames: list[object]) -> list[list[float]]:
    node = shutil.which("node")
    if not node:
        pytest.skip("node is unavailable")
    result = subprocess.run(
        [node, str(JS_RUNNER), str(JS_PARSER)],
        input=json.dumps(frames),
        text=True,
        capture_output=True,
        check=True,
    )
    return json.loads(result.stdout)


def test_python_oracle_matches_javascript_statefully() -> None:
    frames = json.loads(FIXTURE.read_text(encoding="utf-8"))["frames"]
    parser = LegacyK1ParserV12()
    python_results = [parser.parse(frame) for frame in frames]
    javascript_results = _js_results(frames)
    assert len(python_results) == len(javascript_results)
    for python_frame, javascript_frame in zip(python_results, javascript_results, strict=True):
        assert len(python_frame) == len(javascript_frame)
        for python_value, javascript_value in zip(python_frame, javascript_frame, strict=True):
            assert math.isclose(python_value, javascript_value, rel_tol=1e-12, abs_tol=1e-12)


def test_freshness_mask_does_not_mark_held_energy_as_new_ap_data() -> None:
    parser = LegacyK1ParserV12()
    event = parser.parse("EVENT_STATUS energy=0.42 nov=0.1 t=1 frame_ms=8 tid=2")
    assert event[10] == 0.42
    ap = parser.parse("[AP] bpm=120 peak_scaled=0.3")
    assert ap[10] == 0.42
    mask = int(ap[20])
    assert not mask & (1 << 10)
    assert mask & (1 << 0)


def test_parser_state_is_per_source_when_instances_are_separate() -> None:
    bench = LegacyK1ParserV12()
    main = LegacyK1ParserV12()
    assert bench.parse("SYSTEM_FPS: 140")[17] == 1
    assert main.parse("LED_FPS: 150")[17] == 1
    assert bench.last[13] == 0
    assert main.last[12] == 0


def test_painter_requires_fresh_bit_before_drawing_held_high_event() -> None:
    painter = (ROOT / "tools/serial-studio/parsers/event_raster.js").read_text(encoding="utf-8")
    assert "bitFresh(mask, 4) && datasets[0].value >= 0.5" in painter
    fixture = json.loads(
        (ROOT / "tools/serial-studio/fixtures/held-event.json").read_text(encoding="utf-8")
    )
    marks = sum(
        1
        for frame in fixture["frames"]
        if int(frame["update_mask"]) & (1 << 3) and frame["beat"] >= 0.5
    )
    assert marks == fixture["expected_total_marks"]
