from __future__ import annotations

import ast
import csv
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest
import soundfile as sf


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/serial-studio/audio_reference_validate.py"
SPEC = importlib.util.spec_from_file_location("audio_reference_validate", TOOL)
assert SPEC and SPEC.loader
validator = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = validator
SPEC.loader.exec_module(validator)


def _samples(count: int = 8000) -> np.ndarray:
    index = np.arange(count, dtype=np.float64)
    left = 900 + 10500 * np.sin(2 * np.pi * 173 * index / 8000)
    left += 1700 * ((index.astype(np.int64) % 401) == 17)
    right = -1300 + 6100 * np.sin(2 * np.pi * 311 * index / 8000 + 0.37)
    right += 2700 * ((index.astype(np.int64) % 613) == 41)
    return np.rint(np.column_stack([left, right])).astype(np.int16)


def _write_csv(path: Path, samples: np.ndarray, *, times: np.ndarray | None = None) -> None:
    if times is None:
        times = np.arange(len(samples), dtype=np.float64) / 8000.0
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["Elapsed (s)", "Channel 1", "Channel 2"])
        for timestamp, row in zip(times, samples, strict=True):
            writer.writerow([f"{timestamp:.9f}", str(int(row[0])), str(int(row[1]))])


def _fixture(tmp_path: Path) -> tuple[Path, Path, np.ndarray]:
    samples = _samples()
    capture = tmp_path / "capture.csv"
    reference = tmp_path / "reference.wav"
    _write_csv(capture, samples)
    sf.write(reference, samples, 8000, subtype="PCM_16")
    return capture, reference, samples


def _profile(tmp_path: Path, **thresholds: float | int) -> Path:
    defaults: dict[str, float | int] = {
        "max_abs_rate_error_ppm": 0.01,
        "max_timestamp_error_p99_us": 0.001,
        "max_missing_samples": 0,
        "max_abs_lag_ms": 0.01,
        "max_abs_drift_ppm": 0.01,
        "min_signed_correlation": 0.999999,
        "max_abs_gain_error_db": 0.001,
        "max_interchannel_gain_error_db": 0.001,
        "max_abs_dc_offset_error": 0.000001,
        "max_residual_rms": 0.000001,
        "max_clipped_samples_per_channel": 0,
    }
    defaults.update(thresholds)
    path = tmp_path / "profile.json"
    path.write_text(
        json.dumps(
            {
                "schema": validator.PROFILE_SCHEMA,
                "profile_id": "deterministic-unit-fixture-v1",
                "threshold_authority": "UNIT_FIXTURE_ONLY_NOT_PRODUCT",
                "thresholds": defaults,
                "requirements": {
                    "channel_identity_match": True,
                    "positive_polarity": True,
                    "exact_sample_count": True,
                },
            }
        ),
        encoding="utf-8",
    )
    return path


def _run(
    capture: Path,
    reference: Path,
    *extra: str,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(TOOL),
            str(capture),
            str(reference),
            "--representation",
            "int16_native",
            "--expected-rate-hz",
            "8000",
            *extra,
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_exact_native_capture_is_measured_without_transformation(tmp_path: Path) -> None:
    capture, reference, _ = _fixture(tmp_path)
    receipt = validator.validate(
        capture, reference, "int16_native", expected_rate_hz=8000, max_lag_s=0.02
    )

    assert receipt["integrity_status"] == "VALID"
    assert receipt["score"]["status"] == "NOT_SCORED"
    assert receipt["transform_policy"] == {
        "format_inferred": False,
        "normalisation_applied": False,
        "dc_removed": False,
        "dither_applied": False,
        "clipping_applied": False,
        "malformed_rows_skipped": 0,
        "declared_pcm_affine_decode_only": True,
    }
    assert receipt["alignment"]["lag_samples"] == 0
    assert receipt["claims"]["k1_capture_pipeline_validated"] is False
    assert receipt["time_authority"] == "HOST_AUDIO_REFERENCE_TIME"


def test_named_unit_profile_can_score_exact_fixture(tmp_path: Path) -> None:
    capture, reference, _ = _fixture(tmp_path)
    result = _run(capture, reference, "--max-lag-s", "0.02", "--scoring-profile", str(_profile(tmp_path)))
    receipt = json.loads(result.stdout)

    assert result.returncode == 0
    assert receipt["score"]["status"] == "PASS"
    assert receipt["score"]["profile_id"] == "deterministic-unit-fixture-v1"
    assert len(receipt["score"]["profile_sha256"]) == 64


@pytest.mark.parametrize(
    ("mutator", "failed_check"),
    [
        (lambda values: np.rint(values.astype(np.float64) * 0.5).astype(np.int16), "max_abs_gain_error_db"),
        (
            lambda values: np.rint(
                values.astype(np.float64) - values.astype(np.float64).mean(axis=0)
            ).astype(np.int16),
            "max_abs_dc_offset_error",
        ),
        (lambda values: values[:, ::-1], "channel_identity_match"),
        (
            lambda values: np.column_stack([-values[:, 0].astype(np.int32), values[:, 1]]).astype(np.int16),
            "positive_polarity",
        ),
    ],
)
def test_scoring_rejects_gain_dc_channel_and_polarity_mutants(
    tmp_path: Path, mutator, failed_check: str
) -> None:
    capture, reference, samples = _fixture(tmp_path)
    _write_csv(capture, mutator(samples))
    result = _run(capture, reference, "--max-lag-s", "0.02", "--scoring-profile", str(_profile(tmp_path)))
    receipt = json.loads(result.stdout)

    assert result.returncode == 2
    assert receipt["score"]["status"] == "FAIL"
    checks = {item["name"]: item for item in receipt["score"]["checks"]}
    assert checks[failed_check]["pass"] is False


def test_float_normalised_range_is_strict_but_native_integer_magnitude_is_not_guessed(
    tmp_path: Path,
) -> None:
    capture, reference, samples = _fixture(tmp_path)
    parsed = validator.read_serial_studio_csv(capture, "int16_native")
    assert parsed.raw_samples.max() > 1

    capture.write_text(
        "Elapsed (s),Channel 1\n0.0,0.0\n0.1,1.25\n", encoding="utf-8"
    )
    with pytest.raises(validator.ValidationFailure) as failure:
        validator.read_serial_studio_csv(capture, "float32_normalized")
    assert failure.value.code == "SAMPLE_OUT_OF_RANGE"


@pytest.mark.parametrize(
    ("payload", "reason"),
    [
        ("", "CSV_EMPTY"),
        ("Elapsed (s),Channel 1\n", "CSV_TOO_FEW_ROWS"),
        ("time,Channel 1\n0,0\n1,0\n", "CSV_ELAPSED_HEADER"),
        ("Elapsed (s),Channel 2\n0,0\n1,0\n", "CSV_CHANNEL_IDENTITY"),
        ("Elapsed (s),Channel 1\n0,0\n0,1\n", "TIMESTAMP_DUPLICATE"),
        ("Elapsed (s),Channel 1\n0,0\n-1,1\n", "TIMESTAMP_NON_MONOTONIC"),
        ("Elapsed (s),Channel 1\n0,0\n1,nan\n", "SAMPLE_NONFINITE"),
        ("Elapsed (s),Channel 1\n0,0\n1\n", "CSV_FIELD_COUNT"),
        (
            "Elapsed (s),Channel 1\n0,0\nElapsed (s),Channel 1\n",
            "CSV_REPEATED_HEADER",
        ),
    ],
)
def test_malformed_csv_never_skips_or_repairs_rows(
    tmp_path: Path, payload: str, reason: str
) -> None:
    capture = tmp_path / "bad.csv"
    capture.write_text(payload, encoding="utf-8")
    with pytest.raises(validator.ValidationFailure) as failure:
        validator.read_serial_studio_csv(capture, "int16_native")
    assert failure.value.code == reason


def test_local_timestamp_gap_cannot_hide_behind_endpoint_rate(tmp_path: Path) -> None:
    capture, reference, samples = _fixture(tmp_path)
    times = np.arange(len(samples), dtype=np.float64) / 8000.0
    times[3000:] += 1 / 8000.0
    times[3001:] -= np.linspace(0, 1 / 8000.0, len(times) - 3001)
    _write_csv(capture, samples, times=times)
    receipt = validator.validate(
        capture,
        reference,
        "int16_native",
        expected_rate_hz=8000,
        max_lag_s=0.02,
        profile_path=_profile(tmp_path),
    )

    assert abs(receipt["timing"]["rate_error_ppm"]) < 0.01
    assert receipt["timing"]["gap_count_over_1_5_periods"] == 1
    assert receipt["score"]["status"] == "FAIL"
    checks = {item["name"]: item for item in receipt["score"]["checks"]}
    assert checks["max_missing_samples"]["pass"] is False


def test_receipt_serialisation_is_deterministic(tmp_path: Path) -> None:
    capture, reference, _ = _fixture(tmp_path)
    first = validator.serialise(
        validator.validate(capture, reference, "int16_native", expected_rate_hz=8000)
    )
    second = validator.serialise(
        validator.validate(capture, reference, "int16_native", expected_rate_hz=8000)
    )
    assert first == second


def test_tool_has_no_dependency_bootstrap_or_network_surface() -> None:
    source = TOOL.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported_roots = {
        alias.name.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }
    assert imported_roots.isdisjoint({"subprocess", "venv", "socket", "urllib", "requests"})
    for forbidden in ("pip install", "os.exec", "Popen(", "subprocess.", "socket."):
        assert forbidden not in source
