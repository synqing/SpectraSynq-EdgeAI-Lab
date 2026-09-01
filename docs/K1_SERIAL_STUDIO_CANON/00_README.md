# K1 Serial Studio Canon

**Status:** CANONICALIZATION PACKAGE  
**Target:** Serial Studio Pro v4.0.3, K1 dual-UART observability  
**Purpose:** make the lessons from the 2026-08-31 / 2026-09-01 Serial Studio integration session durable, searchable, agent-readable, and mechanically enforceable.

This package exists because prose memory is not enough.

The session demonstrated that a technically promising observability platform can become a time sink when:
- an observability tool is promoted into a command-transport role before that role is proven;
- multiple agents mutate one live, stateful GUI/instrument concurrently;
- project configuration is judged by "it loads" instead of semantic correctness;
- last-known dashboard values are mistaken for fresh samples;
- a host-side "connected" state is mistaken for healthy receive traffic;
- one dead live path is worked around rather than isolated;
- attractive widgets are enabled without asking what engineering question they answer.

The package therefore has four layers:

1. **History:** what happened and why.
2. **Doctrine:** rules future work must obey.
3. **Workflow/skill:** exact operating procedure for future agents.
4. **Guardrails:** executable checks that reject known bad project states.

## Files

- `01_SESSION_POSTMORTEM_2026-08-31.md` — chronological incident history and root-cause inventory.
- `02_CANONICAL_DOCTRINE.md` — permanent Serial Studio/K1 rules.
- `03_OBSERVABILITY_ARCHITECTURE.md` — authority boundaries and passive/active profiles.
- `04_DASHBOARD_INFORMATION_ARCHITECTURE.md` — widget selection and semantic display rules.
- `05_EVIDENCE_AND_HISTORIAN_STANDARD.md` — Historian, snapshot, freshness and receipt rules.
- `06_AGENT_OPERATING_RULES.md` — live-instrument governance and agent process constraints.
- `07_CANONIZATION_PLAN.md` — where this knowledge should live in the real repos.
- `skills/k1-serial-studio-instrument/SKILL.md` — agent-executable skill specification.
- `guardrails/serial_studio_policy.json` — machine-readable policy.
- `guardrails/lint_ssproj.py` — linter for `.ssproj` files.
- `guardrails/test_lint_ssproj.py` — unit tests for the linter.
- `workflow/PASSIVE_OBSERVE_CHECKLIST.md` — normal Serial Studio observation workflow.
- `workflow/AUTHORITATIVE_SILICON_CHECKLIST.md` — command/reply silicon workflow with exclusive pyserial ownership.
- `snippets/AGENTS_CANONICAL_INSERT.md` — concise standing doctrine for `AGENTS.md`.
- `snippets/pre-commit-serial-studio.sh` — pre-commit/CI invocation.

## Canonical architectural sentence

> **Serial Studio is an instrument, not K1 command transport authority. A silicon test that needs interactive command/reply owns the target K1 serial port exclusively; Serial Studio must release it first.**

Everything else in this package follows from that sentence plus the evidence hierarchy.

## Evidence hierarchy

```text
DEVICE CLOCKS / DEVICE COUNTERS = timing authority
RAW DRIVER BYTES                = transport evidence
FROZEN HISTORIAN SNAPSHOT       = session evidence
PARSER RAW + FINAL VALUES       = structured evidence
HOST ARRIVAL TIMESTAMPS         = acquisition/transport diagnostic
PAINTER / PLOTS / WEB VIEW      = operator awareness / engineering intuition
SCREENSHOTS                     = communication only
OFFLINE PYTHON SCORER           = verdict
```

## Historical project handling

Do not mutate the old `K1 Dual UART Observability.ssproj` into the new instrument.

Preserve it as **v1 / historical replay compatibility**.

Build a clean v2 project. Old Historian sessions embed their original project JSON and should remain replayable as originally captured.
