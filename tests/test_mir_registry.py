"""Registry structural-honesty tests.

These assert SHAPE, never optimism. `UNKNOWN` must always remain a legal value;
what must be impossible is a silently absent lineage field, an off-vocabulary
lineage value, or a `true` lineage claim contradicted by the entry's own licences.
"""

import copy

import pytest
import yaml

from edgeai.mir.registry import (
    DEFAULT_PATH,
    LINEAGE_VOCAB,
    licensing_matrix,
    lineage_class,
    load_registry,
)

NEW_2026_09_01 = ("basic-pitch", "openmic-2018", "efficientat", "musicfm")


def _write(tmp_path, data):
    p = tmp_path / "registry.yaml"
    p.write_text(yaml.safe_dump(data, sort_keys=False))
    return p


def test_registry_loads_and_unique_ids():
    data = load_registry()
    ids = [e["id"] for e in data["entries"]]
    assert "librosa" in ids
    assert "htdemucs" in ids
    assert "parirset" in ids
    assert "musdb-sample" in ids
    assert "slakh2100" in ids
    assert "medleydb" in ids
    assert "semantic-v0-experiment" in ids
    assert len(ids) == len(set(ids))
    htd = next(e for e in data["entries"] if e["id"] == "htdemucs")
    assert "UNKNOWN" in htd["weight_licence"]
    matrix = licensing_matrix(data)
    assert all("commercial" in row for row in matrix)


def test_semantic_v0_is_experiment_not_authority():
    data = load_registry()
    e = next(x for x in data["entries"] if x["id"] == "semantic-v0-experiment")
    assert e["status"] == "executed"
    assert "not architecture authority" in e["spectrasynq"].lower() or "toolchain" in e["spectrasynq"].lower()


# --- J1D: the registry must be able to go red -------------------------------


def test_every_entry_carries_the_four_lineage_fields():
    data = load_registry()
    for e in data["entries"]:
        for k in ("code_licence", "weight_licence", "dataset_licence", "commercial_training_lineage"):
            assert k in e, f"{e['id']} missing {k}"


def test_lineage_values_are_in_vocabulary():
    data = load_registry()
    for e in data["entries"]:
        assert lineage_class(e) in LINEAGE_VOCAB, f"{e['id']} -> {e['commercial_training_lineage']!r}"


def test_unknown_is_still_a_legal_answer():
    """Structural honesty, not artificial certainty."""
    data = load_registry()
    classes = {lineage_class(e) for e in data["entries"]}
    assert "unknown" in classes


def test_four_new_asset_rows_present():
    data = load_registry()
    ids = {e["id"] for e in data["entries"]}
    for want in NEW_2026_09_01:
        assert want in ids, f"{want} row missing"


def test_basic_pitch_row_bans_the_marketing_memory_claim():
    """The '<20 MB peak memory' figure is Spotify marketing; the ICASSP paper
    measures 490-951 MB. The row must carry that correction, not the claim."""
    data = load_registry()
    e = next(x for x in data["entries"] if x["id"] == "basic-pitch")
    s = e["spectrasynq"]
    assert "490" in s and "951" in s
    assert "BANNED CLAIM" in s


def test_openmic_row_records_the_zenodo_badge_footgun():
    data = load_registry()
    e = next(x for x in data["entries"] if x["id"] == "openmic-2018")
    assert "license_title" in e["dataset_licence"] or "license_title" in e["spectrasynq"]
    assert lineage_class(e) == "conditional"


def test_slakh_records_the_proprietary_sample_library_risk():
    data = load_registry()
    e = next(x for x in data["entries"] if x["id"] == "slakh2100")
    assert "Kontakt" in e["spectrasynq"]
    assert lineage_class(e) == "conditional"


# --- and the loader must actually reject the broken shapes ------------------


def test_loader_rejects_duplicate_id(tmp_path):
    data = copy.deepcopy(load_registry())
    data["entries"].append(copy.deepcopy(data["entries"][0]))
    with pytest.raises(ValueError, match="duplicate"):
        load_registry(_write(tmp_path, data))


def test_loader_rejects_missing_lineage_field(tmp_path):
    data = copy.deepcopy(load_registry())
    del data["entries"][0]["commercial_training_lineage"]
    with pytest.raises(ValueError, match="commercial_training_lineage"):
        load_registry(_write(tmp_path, data))


def test_loader_rejects_missing_dataset_licence(tmp_path):
    data = copy.deepcopy(load_registry())
    del data["entries"][0]["dataset_licence"]
    with pytest.raises(ValueError, match="dataset_licence"):
        load_registry(_write(tmp_path, data))


def test_loader_rejects_prose_in_the_lineage_field(tmp_path):
    data = copy.deepcopy(load_registry())
    data["entries"][0]["commercial_training_lineage"] = "probably fine, ask counsel"
    with pytest.raises(ValueError, match="not in"):
        load_registry(_write(tmp_path, data))


def test_loader_rejects_lineage_true_over_a_noncommercial_dataset(tmp_path):
    data = copy.deepcopy(load_registry())
    e = next(x for x in data["entries"] if x["id"] == "musdb18")
    e["commercial_training_lineage"] = True
    e["commercial_use"] = "yes"
    with pytest.raises(ValueError, match="non-commercial/unknown token"):
        load_registry(_write(tmp_path, data))


def test_loader_rejects_lineage_true_while_commercial_use_no(tmp_path):
    data = copy.deepcopy(load_registry())
    e = next(x for x in data["entries"] if x["id"] == "medleydb")
    e["commercial_training_lineage"] = True
    e["commercial_use"] = "no"
    e["dataset_licence"] = "cleared"
    e["code_licence"] = "MIT"
    e["weight_licence"] = "n/a"
    with pytest.raises(ValueError, match="commercial_use no"):
        load_registry(_write(tmp_path, data))
