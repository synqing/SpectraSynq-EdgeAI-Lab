"""The J2 lineage map and mir/registry.yaml must never disagree.

The memo is a Captain decision input; the registry is the enforceable surface.
If someone upgrades an asset in one place and not the other, this goes red.
"""

import json
from pathlib import Path

import pytest

from edgeai.mir.registry import lineage_class, load_registry

ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / "_scratch" / "mi_programme_review_20260901" / "lineage_map.json"
MEMO = ROOT / "_scratch" / "mi_programme_review_20260901" / "LINEAGE_MAP_2026-09-01.md"

# memo class -> the registry lineage values it is allowed to sit on top of
COMPATIBLE = {
    "CLEAN_CANDIDATE": {"true"},
    "CONDITIONAL_PER_ASSET": {"conditional"},
    "RESEARCH_ONLY": {"false"},
    "UNKNOWN": {"unknown"},
    "NOT_APPLICABLE": {"n/a"},
}
LAYERS = ("source_audio", "annotations", "teacher_weights", "pseudo_labels", "derived_student")


@pytest.fixture(scope="module")
def lmap():
    assert MAP.is_file(), "J2 lineage map missing"
    return json.loads(MAP.read_text())


def test_memo_and_machine_readable_twin_both_exist(lmap):
    assert MEMO.is_file()
    assert lmap["schema"] == "spectrasynq.lineage_map.v1"
    assert lmap["not_legal_advice"] is True


def test_every_mapped_asset_exists_in_the_registry(lmap):
    ids = {e["id"] for e in load_registry()["entries"]}
    for a in lmap["assets"]:
        assert a["registry_id"] in ids, f"{a['registry_id']} not in mir/registry.yaml"


def test_every_asset_separates_the_five_layers(lmap):
    for a in lmap["assets"]:
        for layer in LAYERS:
            assert layer in a, f"{a['registry_id']} missing layer {layer}"


def test_memo_class_agrees_with_registry_lineage(lmap):
    reg = {e["id"]: e for e in load_registry()["entries"]}
    bad = []
    for a in lmap["assets"]:
        cls = a["class"]
        assert cls in COMPATIBLE, f"{a['registry_id']}: unknown class {cls}"
        got = lineage_class(reg[a["registry_id"]])
        if got not in COMPATIBLE[cls]:
            bad.append(f"{a['registry_id']}: memo {cls} vs registry {got}")
    assert not bad, "memo and registry disagree:\n  " + "\n  ".join(bad)


def test_nothing_is_called_commercially_clean_for_musical_supervision(lmap):
    """The headline finding. If this ever flips, it must flip deliberately."""
    clean = [a["registry_id"] for a in lmap["assets"] if a["class"] == "CLEAN_CANDIDATE"]
    assert clean == ["parirset"], (
        f"lineage map now claims {clean} is commercially clean. "
        "Update the memo headline and tell Captain - this is a strategy change."
    )


def test_openmic_filtering_verdict_is_recorded_with_numbers(lmap):
    v = lmap["openmic_fma_filtered_subset"]
    assert v["verdict"] in {
        "FEASIBLE",
        "FEASIBLE_WITH_CONDITIONS",
        "NOT_FEASIBLE_FROM_AVAILABLE_METADATA",
        "UNKNOWN",
    }
    assert v["non_nc_clips"] + 1 <= v["total_clips"]
    assert v["non_nc_excluding_by_nd"] <= v["non_nc_clips"]
    assert v["conditions"], "a FEASIBLE_WITH_CONDITIONS verdict must state its conditions"
