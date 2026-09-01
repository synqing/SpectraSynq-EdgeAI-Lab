#!/usr/bin/env python3
"""Lint a Serial Studio .ssproj against K1 observability doctrine.

This is intentionally conservative. It rejects known-dangerous states even if
Serial Studio itself can load them.
"""
from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
POLICY = json.loads((HERE / "serial_studio_policy.json").read_text())

def cls(title: str) -> str:
    return POLICY.get("semantic_classes", {}).get(title, "unknown")

def compatible(classes: set[str]) -> bool:
    if len(classes) <= 1:
        return True
    for allowed in POLICY.get("multiplot_compatible_classes", []):
        if classes.issubset(set(allowed)):
            return True
    return False

def lint(path: Path, profile: str) -> tuple[list[str], list[str]]:
    d = json.loads(path.read_text())
    errors: list[str] = []
    warnings: list[str] = []

    prof = POLICY["profiles"][profile]
    version = str(d.get("writerVersion") or "")
    target = str(POLICY["target_serial_studio"])
    if version and version != target:
        warnings.append(f"writerVersion={version}, target={target}; verify version-specific behavior")

    # 1. Control script authority
    script = str(d.get("controlScriptCode") or "")
    if not prof["device_write_in_scripts_allowed"]:
        for tok in POLICY["forbidden_script_tokens"]:
            if tok in script:
                errors.append(f"controlScriptCode contains forbidden token {tok!r}")

    # 2. Tables
    for table in d.get("tables", []) or []:
        name = str(table.get("name") or "")
        if name in POLICY["forbidden_tables"]:
            errors.append(f"forbidden shared table present: {name}")

    # 3. Sources
    for src in d.get("sources", []) or []:
        title = src.get("title", f"source{src.get('sourceId')}")
        conn = src.get("connection", {}) or {}
        if conn.get("autoReconnect") and not prof["auto_reconnect_allowed"]:
            errors.append(f"{title}: autoReconnect=true forbidden in profile {profile}")

    # 4. Actions
    for act in d.get("actions", []) or []:
        title = act.get("title", "<action>")
        if act.get("autoExecuteOnConnect") and not prof["auto_execute_actions_allowed"]:
            errors.append(f"{title}: autoExecuteOnConnect=true forbidden in profile {profile}")
        tm = int(act.get("timerMode") or 0)
        if tm != 0 and not prof["timer_actions_allowed"]:
            errors.append(f"{title}: timerMode={tm} forbidden in profile {profile}")
        if tm != 0 and profile == "active-polling":
            interval = int(act.get("timerIntervalMs") or 0)
            if interval < int(prof.get("min_timer_interval_ms", 1000)):
                errors.append(f"{title}: timer interval {interval} ms below active-polling minimum")
            payload = str(act.get("txData") or "")
            for line in [x.strip() for x in payload.replace("\\n", "\n").splitlines() if x.strip()]:
                if not any(line.startswith(tok) for tok in prof.get("allowed_action_payload_tokens", [])):
                    errors.append(f"{title}: non-allowlisted active-poll command {line!r}")

    groups = d.get("groups", []) or []
    group_ids = {}
    for g in groups:
        gid = g.get("uniqueId")
        if gid in group_ids:
            errors.append(f"duplicate group uniqueId={gid}")
        group_ids[gid] = g

        # 5. Datasets
        ds = g.get("datasets", []) or []
        for x in ds:
            title = str(x.get("title") or "")
            for pat in POLICY["forbidden_dataset_title_regex"]:
                if re.search(pat, title, re.I):
                    errors.append(f"{g.get('title')}/{title}: forbidden dead-slot dataset")
            if x.get("virtual"):
                code = str(x.get("transformCode") or "")
                deps = ("datasetGetRaw(", "datasetGetFinal(", "tableGet(", "tableGetH(")
                explicit = "SS_LINT_ALLOW_VIRTUAL_NO_DEP" in code
                if code and not any(k in code for k in deps) and not explicit:
                    errors.append(
                        f"{g.get('title')}/{title}: virtual transform has no explicit dataset/table dependency; "
                        "virtual value is not sibling telemetry"
                    )
            if x.get("fft") or x.get("waterfall"):
                allow = POLICY["fft_allowlist"].get(title)
                if not allow:
                    errors.append(f"{g.get('title')}/{title}: FFT/Waterfall enabled without cadence allowlist")
                else:
                    got = float(x.get("fftSamplingRate") or 0)
                    exp = float(allow["expected_hz"])
                    if abs(got - exp) > max(1e-6, exp * 0.001):
                        errors.append(f"{g.get('title')}/{title}: fftSamplingRate={got}, expected={exp}")
            if x.get("led") and title in POLICY["event_titles"]:
                errors.append(
                    f"{g.get('title')}/{title}: transient event configured as LED annunciator; use event timeline/raster"
                )

        # 6. MultiPlot semantic compatibility
        if str(g.get("widget") or "").lower() == "multiplot":
            plotted = [x for x in ds if x.get("graph")]
            classes = {cls(str(x.get("title") or "")) for x in plotted}
            if len(plotted) > 1 and not compatible(classes):
                errors.append(
                    f"{g.get('title')}: MultiPlot mixes incompatible semantic classes {sorted(classes)} "
                    f"from {[x.get('title') for x in plotted]}"
                )

    # 7. Workspaces and dangling refs
    sigs = {}
    for ws in d.get("workspaces", []) or []:
        title = str(ws.get("title") or "<workspace>")
        refs = ws.get("widgetRefs", []) or []
        for r in refs:
            gid = r.get("groupId")
            if gid not in group_ids:
                errors.append(f"{title}: dangling widgetRef groupId={gid}")
        sig = tuple(sorted((r.get("groupId"), r.get("relativeIndex"), r.get("widgetType")) for r in refs))
        if sig:
            if sig in sigs and title not in POLICY.get("workspace_duplicate_refs_allowed", []):
                errors.append(f"{title}: identical widget-ref set to workspace {sigs[sig]!r}; fake shell workspace")
            sigs[sig] = title

    # 8. Generic warnings
    if d.get("changeDrivenTransforms") is False:
        warnings.append("changeDrivenTransforms=false; acceptable, but revisit if v2 becomes transform-heavy")

    return errors, warnings

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("project", type=Path)
    ap.add_argument("--profile", choices=sorted(POLICY["profiles"]), default="passive")
    ns = ap.parse_args()
    errors, warnings = lint(ns.project, ns.profile)
    for w in warnings:
        print("WARN:", w)
    for e in errors:
        print("ERROR:", e)
    print(f"RESULT errors={len(errors)} warnings={len(warnings)}")
    return 1 if errors else 0

if __name__ == "__main__":
    raise SystemExit(main())
