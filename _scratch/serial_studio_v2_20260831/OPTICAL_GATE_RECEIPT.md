# Optical gate receipt

STATUS: PASS

The Mission Control Web View may proceed to production code in this repository.

- Primary still: `output/playwright/k1-mission-control-final-1440x900.png`.
- Minimum viewport still: `output/playwright/k1-mission-control-final-1180x720.png`.
- Source inventory, measured facts, font-role lock, forbidden fixes, and skill-lens notes are present beside this receipt.
- Both viewports preserve the instrument rail, the Bench/Main comparison, units, ages, record provenance, delta strip, and the absence of alarm thresholds.
- Red-team still `k1-redteam-api-up-main-rx-dead-1440x900.png` proves API availability cannot false-green Main RX and exposed/fixed a null-age-to-zero coercion.
- Red-team still `k1-redteam-missing-metrics-1440x900.png` preserves missing metrics and session identity as missing rather than zero.
- `held-event.json` plus the parser/Painter test proves one fresh-high Beat produces one mark and the held-high follow-up produces none.
- No external imagery or transparency-sensitive asset is present.
- This receipt approves the UI composition only. It does not claim live device, USB, Historian-integrity, or firmware proof.
