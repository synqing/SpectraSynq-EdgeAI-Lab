from pathlib import Path
import importlib.util
import json

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("lint_ssproj", HERE / "lint_ssproj.py")
m = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(m)

def base():
    return {
        "writerVersion": "4.0.3",
        "controlScriptCode": "",
        "actions": [],
        "tables": [],
        "sources": [{"sourceId": 0, "title": "K1", "connection": {"autoReconnect": False}}],
        "groups": [],
        "workspaces": []
    }

def run(tmp_path, d, profile="passive"):
    p = tmp_path / "x.ssproj"
    p.write_text(json.dumps(d))
    return m.lint(p, profile)

def test_clean_minimal_passes(tmp_path):
    e, _ = run(tmp_path, base())
    assert not e

def test_command_shuttle_rejected(tmp_path):
    d = base()
    d["controlScriptCode"] = 'deviceWriteAndWait(":chip_id\\n", 1000, "9087A500", 1);'
    e, _ = run(tmp_path, d)
    assert any("deviceWriteAndWait" in x for x in e)

def test_auto_reconnect_rejected(tmp_path):
    d = base()
    d["sources"][0]["connection"]["autoReconnect"] = True
    e, _ = run(tmp_path, d)
    assert any("autoReconnect" in x for x in e)

def test_auto_poll_rejected_in_passive(tmp_path):
    d = base()
    d["actions"] = [{
        "title": "Poll", "autoExecuteOnConnect": True, "timerMode": 1,
        "timerIntervalMs": 250, "txData": ":fps"
    }]
    e, _ = run(tmp_path, d)
    assert any("autoExecuteOnConnect" in x for x in e)
    assert any("timerMode" in x for x in e)

def test_unused_slot_rejected(tmp_path):
    d = base()
    d["groups"] = [{
        "uniqueId": 1, "title": "G", "widget": "",
        "datasets": [{"title": "unused_slot_17"}]
    }]
    e, _ = run(tmp_path, d)
    assert any("dead-slot" in x for x in e)

def test_virtual_without_dependency_rejected(tmp_path):
    d = base()
    d["groups"] = [{
        "uniqueId": 1, "title": "G", "widget": "",
        "datasets": [{
            "title": "frame_dt_ms", "virtual": True,
            "transformCode": "function transform(value){ return value; }"
        }]
    }]
    e, _ = run(tmp_path, d)
    assert any("virtual transform" in x for x in e)

def test_event_led_rejected(tmp_path):
    d = base()
    d["groups"] = [{
        "uniqueId": 1, "title": "G", "widget": "",
        "datasets": [{"title": "Beat", "led": True}]
    }]
    e, _ = run(tmp_path, d)
    assert any("event configured as LED" in x for x in e)

def test_mixed_multiplot_rejected(tmp_path):
    d = base()
    d["groups"] = [{
        "uniqueId": 1, "title": "Soup", "widget": "multiplot",
        "datasets": [
            {"title": "BPM", "graph": True},
            {"title": "Beat", "graph": True},
            {"title": "Energy", "graph": True}
        ]
    }]
    e, _ = run(tmp_path, d)
    assert any("MultiPlot mixes" in x for x in e)

def test_dangling_workspace_ref_rejected(tmp_path):
    d = base()
    d["workspaces"] = [{
        "title": "Timing", "widgetRefs": [{"groupId": 999, "relativeIndex": 0, "widgetType": 2}]
    }]
    e, _ = run(tmp_path, d)
    assert any("dangling" in x for x in e)

def test_duplicate_shell_workspace_rejected(tmp_path):
    d = base()
    d["groups"] = [{"uniqueId": 1, "title": "G", "widget": "", "datasets": []}]
    refs = [{"groupId": 1, "relativeIndex": 0, "widgetType": 2}]
    d["workspaces"] = [
        {"title": "Timing", "widgetRefs": refs},
        {"title": "Renderer", "widgetRefs": refs},
    ]
    e, _ = run(tmp_path, d)
    assert any("fake shell" in x for x in e)
