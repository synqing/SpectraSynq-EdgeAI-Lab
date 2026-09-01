# K1 Serial Studio — Agent Operating Rules

## 1. Single-writer rule

One agent owns live Serial Studio.

Other agents:
- read docs;
- inspect copied `.ssproj`;
- run offline lint/tests;
- write lane reports.

They do not touch the live app/API/project.

## 2. Live-action budget

Any action that can change the live state must be named in advance:
- connect;
- disconnect;
- reconnect;
- source setting change;
- parser apply;
- project load;
- project save;
- plugin install/update/start/stop;
- action enable;
- polling enable;
- physical reset.

Do not treat GUI operations as harmless.

## 3. One proof obligation

A hardware attempt has exactly one principal question.

Example:
> "Does Main RPL receive path produce raw bytes after one physical reset?"

Not:
> "Fix Serial Studio."

## 4. Failure discipline

On failure:
1. record evidence;
2. independently verify the symptom;
3. classify the fault layer;
4. stop;
5. return the blocker.

No automatic retry.

## 5. Instrument development lifecycle

```text
copy v1
  -> edit v2 offline
  -> lint
  -> parser golden tests
  -> telemetry simulator/replay
  -> visual review
  -> passive live shadow session
  -> frozen snapshot
  -> promote v2
```

Do not skip directly from JSON editing to authoritative silicon.

## 6. Never trust labels

A workspace named "Timing" does not prove it shows timing.

An LED called "Lock" does not prove it is fresh.

A green connection icon does not prove raw RX.

Inspect causal data path.

## 7. Do not broaden scope while blocked

If a command shuttle is blocked, do not:
- redesign dashboard;
- add plugins;
- add MCP;
- change cadence;
- invent a second shuttle.

Close the blocker or demote the feature.

## 8. Read the exact version

Target v4.0.3.

Do not silently import behavior from later master docs.

When using API commands, enumerate the running v4.0.3 command registry.

## 9. No support-tool sunk cost

If a support tool becomes more expensive than the product/research task it was meant to support, re-evaluate architecture immediately.

## 10. Exit report contract

Every live-instrument task returns:

- state before;
- exact allowed action;
- observed result;
- evidence path/hash;
- state after;
- explicit non-claims;
- next blocker;
- whether the active research/product programme is blocked.
