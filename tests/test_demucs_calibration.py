"""J3/J4 scientific and provenance invariants independent of the real model run."""

from __future__ import annotations

import importlib.util
import warnings
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
CALIBRATION = ROOT / "scripts/demucs_musdb_calibrate.py"
WITNESS = ROOT / "scripts/demucs_unstemmed_envelope.py"


def _load_calibration():
    spec = importlib.util.spec_from_file_location("demucs_musdb_calibrate", CALIBRATION)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_witness():
    spec = importlib.util.spec_from_file_location("demucs_unstemmed_envelope", WITNESS)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_frozen_musdb_five_is_exact() -> None:
    module = _load_calibration()
    assert module.FROZEN_TRACKS == (
        ("vocal_dominant", "Side Effects Project - Sing With Me"),
        ("drum_dominant", "PR - Happy Daze"),
        ("bass_heavy", "Skelpolu - Resurrection"),
        ("other_heavy", "Timboz - Pony"),
        ("balanced", "Cristina Vane - So Easy"),
    )


def test_source_order_swap_goes_red() -> None:
    module = _load_calibration()
    rng = np.random.default_rng(7)
    oracle = {source: rng.random(400) for source in module.SOURCES}
    predicted = {
        "vocals": oracle["drums"],
        "drums": oracle["vocals"],
        "bass": oracle["bass"],
        "other": oracle["other"],
    }
    mapping = module.best_source_mapping(predicted, oracle)
    assert mapping["valid"] is False
    assert mapping["best_assignment"]["vocals"] == "drums"
    assert mapping["best_assignment"]["drums"] == "vocals"


def test_identity_mapping_passes() -> None:
    module = _load_calibration()
    rng = np.random.default_rng(11)
    oracle = {source: rng.random(400) for source in module.SOURCES}
    predicted = {source: oracle[source] + 0.001 * rng.random(400) for source in module.SOURCES}
    assert module.best_source_mapping(predicted, oracle)["valid"] is True


def test_channel_first_demucs_output_is_transposed_before_power() -> None:
    source = (ROOT / "src/edgeai/mir/demucs_teacher.py").read_text(encoding="utf-8")
    assert ".detach().cpu().numpy().T" in source
    calibration = CALIBRATION.read_text(encoding="utf-8")
    assert "frame_mean_square(waveform.T, HOP)" in calibration


def test_authority_metrics_do_not_apply_lag_or_use_sdr() -> None:
    source = CALIBRATION.read_text(encoding="utf-8")
    assert '"lag_corrected": False' in source
    assert '"sdr_used_for_pass": False' in source
    assert "np.roll" not in source


def test_simplex_js_handles_zero_components_without_warnings() -> None:
    module = _load_calibration()
    predicted = np.array([[1.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0]])
    oracle = np.array([[0.5, 0.5, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0]])
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        value = module._simplex_js(predicted, oracle)
    assert np.isfinite(value)


def test_ride_it_witness_is_research_only_json_and_never_wav() -> None:
    source = WITNESS.read_text(encoding="utf-8")
    assert "HOST_RESEARCH_WITNESS_ONLY" in source
    assert '"commercial_training_lineage": False' in source
    assert '"not_training_dataset": True' in source
    assert "ride_it_share.json" in source
    assert "write_wav" not in source
    assert "save_audio" not in source
    assert "ffplay" not in source


def test_ride_it_witness_rejects_output_outside_research_only(tmp_path: Path) -> None:
    module = _load_witness()
    with pytest.raises(RuntimeError, match="outside research_only"):
        module.validate_research_output(tmp_path / "ride_it_share.json")


def test_ride_it_witness_forbids_common_audio_and_stem_media(tmp_path: Path) -> None:
    module = _load_witness()
    (tmp_path / "forbidden.flac").write_bytes(b"not audio")
    assert module.forbidden_media(tmp_path) == [tmp_path / "forbidden.flac"]
