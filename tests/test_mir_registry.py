from edgeai.mir.registry import licensing_matrix, load_registry


def test_registry_loads_and_unique_ids():
    data = load_registry()
    ids = [e["id"] for e in data["entries"]]
    assert "librosa" in ids
    assert "htdemucs" in ids
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
