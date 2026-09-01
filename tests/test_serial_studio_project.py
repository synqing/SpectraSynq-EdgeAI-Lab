from __future__ import annotations

import copy
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "tools/serial-studio/projects/K1-Dual-UART-Observability-v2.ssproj"
LINTER = ROOT / "tools/serial-studio/lint_project.py"


def load_project() -> dict[str, object]:
    return json.loads(PROJECT.read_text(encoding="utf-8"))


def test_mission_control_is_one_dominant_web_view() -> None:
    project = load_project()
    workspaces = {workspace["title"]: workspace for workspace in project["workspaces"]}
    groups = {group["uniqueId"]: group for group in project["groups"]}

    refs = workspaces["Mission Control"]["widgetRefs"]
    assert len(refs) == 1
    group = groups[refs[0]["groupId"]]
    assert group["widget"] == "webview"
    assert group["title"] == "K1 Mission Control"
    assert group["datasets"] == []


def test_linter_rejects_native_spectacle_on_mission_control(tmp_path: Path) -> None:
    project = load_project()
    mutant = copy.deepcopy(project)
    workspaces = {workspace["title"]: workspace for workspace in mutant["workspaces"]}
    workspaces["Mission Control"]["widgetRefs"].append(
        copy.deepcopy(workspaces["Rhythm & Events"]["widgetRefs"][0])
    )
    mutant_path = tmp_path / "mission-control-spectacle.ssproj"
    mutant_path.write_text(json.dumps(mutant), encoding="utf-8")

    result = subprocess.run(
        ["python3", str(LINTER), str(mutant_path)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 1
    assert "exactly one dominant Web View" in result.stdout
