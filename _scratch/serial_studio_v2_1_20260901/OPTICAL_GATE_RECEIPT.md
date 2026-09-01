# Optical gate receipt — Serial Studio Audio Reference v2.1

**Tier:** T0 — full optical lock  
**Verdict:** PASS  
**Surface:** `k1.serial-studio.observability.v2.1`

Primary still:
`/Users/spectrasynq/SpectraSynq-EdgeAI-Lab/output/playwright/k1-v2-1-mission-control-1440x900.png`  
SHA-256: `ae9906c6bc69c07723420efe12799e9a832b95b26964650634e726a4b7b3dc3f`

Normative measurements:
`/Users/spectrasynq/SpectraSynq-EdgeAI-Lab/_scratch/serial_studio_v2_1_20260901/MEASURED.json`

The final pack contains six full-surface stills, thirteen tight role crops,
thirteen mechanically annotated ink boxes, absolute source paths and SHA-256
pins. Headless tests proved zero horizontal/vertical overflow at 1440×900 and
1180×720, all three elected font faces loaded, Mission Control retained two
device cards/six delta cells, and both detail surfaces rendered eight rows.

The locked optical ladder is 45, 21, 15, 14, 14, 11, 10, 9, 8, 8, 7, 7, 7 px.
It is sorted in `MEASURED.json`; P0 inversions are empty. HTML/CSS measurements
are authority only for this Web View and are explicitly not LVGL authority.

## Red-team bypasses

1. **Reuse the old five-cell PASS.** Rejected: source/still hashes and geometry
   changed, and the old measurement lacked normative role/crop fields.
2. **Call the host-capture receipt an AP PASS.** Rejected by the final optical
   pass: the first render exposed that false authority. The final AP still says
   `BLOCKED`, names missing AP inputs, and labels the existing PASS only as
   `HOST CAPTURE RECEIPT PASS`.
3. **Make live Audio samples green because age is 18 ms.** Rejected: no sourced
   freshness/binding threshold exists; the final surface remains
   `LIVE UNVERIFIED` with a neutral indicator.
4. **Hide the sixth cell overflow.** Rejected: both required viewports report
   exact viewport scroll dimensions; overflow hiding is listed as forbidden.

Independent production/adversarial inputs were supplied by the UI optical lane
and the root implementation lane. Vision-read of all three 1440×900 stills was
performed. Craft conclusion: the K1 tempo/RX cards retain dominance; the Audio
cell is subordinate; the specialist surfaces expose authority/failure before
diagnostic detail.

This PASS covers fixture-rendered Web View composition only. It does not prove
Serial Studio Pro runtime, a loopback device, Audio Source C, live capture,
Bench/Main RX, Historian integrity, HIL, acoustic delivery, K1 PCM, or a product
verdict.
