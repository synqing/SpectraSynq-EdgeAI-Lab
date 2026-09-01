# Canonization Plan — Where This Must Live

Do not rely on one giant postmortem file alone.

Encode the knowledge at the layer where future mistakes occur.

## A. K1 firmware/instrument repository

Recommended canonical tree:

```text
tools/serial-studio/
├── README.md
├── DOCTRINE.md
├── POSTMORTEM_2026-08-31.md
├── TELEMETRY_SCHEMA.md
├── K1-Dual-UART-Observability-v1.ssproj       # frozen historical
├── K1-Dual-UART-Observability-v2.ssproj       # canonical new instrument
├── parsers/
│   └── k1_ap_parser.js
├── guardrails/
│   ├── serial_studio_policy.json
│   └── lint_ssproj.py
├── tests/
│   ├── fixtures/
│   └── test_serial_studio_project.py
├── scorer/
│   ├── session_receipt.py
│   └── ...
└── plugins/
    └── k1-live-analyzer/                      # later, read-only
```

## B. `AGENTS.md`

Keep only high-signal standing rules:
- Serial Studio is observe/record only.
- Exclusive CDC ownership.
- One live writer.
- No live project mutation during evidence capture.
- Passive profile default.
- Linter required before canonical project changes.

Do not paste the entire postmortem into `AGENTS.md`.

## C. Decision ledger

Record one durable decision:

> K1 Serial Studio observability is a passive instrument architecture. Command/reply silicon tests use exclusive pyserial ownership. v1 remains historical; v2 is built under linted semantic rules.

## D. Pre-commit / CI

Every changed `.ssproj` must run:

```bash
python tools/serial-studio/guardrails/lint_ssproj.py \
  tools/serial-studio/K1-Dual-UART-Observability-v2.ssproj \
  --profile passive
```

CI fails on errors.

## E. Agent skill

Install/reference `skills/k1-serial-studio-instrument/SKILL.md` in the agent skill router.

Any task containing:
- Serial Studio;
- `.ssproj`;
- K1 dashboard;
- Historian;
- K1 UART observability;
- Serial Studio plugin/extension;
- Painter;
- K1 telemetry parser;

must route through this skill before execution.

## F. Project generator, not hand-edit sprawl

Longer term:
- maintain telemetry semantics in machine-readable schema;
- generate project groups/datasets from schema where practical;
- lint generated output;
- keep manual layout as the thin human layer.

## G. Private extension repository after stabilization

When v2 is stable, package:
- K1 frame parser;
- K1 project template;
- read-only K1 live analyzer plugin.

Do not package experimental/shuttle code.

## H. Historical evidence

Do not rewrite old Session Database records.

Keep old v1 project for replay compatibility.

New v2 sessions must carry v2 embedded project JSON and new receipts.
