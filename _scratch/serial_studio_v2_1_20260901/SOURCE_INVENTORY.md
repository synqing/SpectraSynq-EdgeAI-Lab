# Source inventory — Serial Studio Audio Reference v2.1 Web View

Tier: **T0 — full optical lock**  
Surface IDs: `k1.serial-studio.mission-control.v2.1`,
`k1.serial-studio.audio-reference.v2.1`,
`k1.serial-studio.ap-validation.v2.1`

| Role | Call site / selector | CSS token | Face |
| --- | --- | --- | --- |
| Mission mode kicker | `#mode-kicker` | `.kicker` 12 px / 700 italic | Countach Bold Italic |
| Surface title | `#surface-title` | `.title` 28 px | Countach Regular |
| Build identity | `.build` | `.build` 10 px | Berkeley Mono Regular |
| Instrument eyebrow | `.instrument .eyebrow` | `.eyebrow` 9 px | Berkeley Mono Regular |
| Instrument state | `#audio-ref-state` | `.status` 12 px | Berkeley Mono Regular |
| Device role | `.device .role` | `.role` 18 px | Countach Regular |
| Tempo hero | `.tempo strong` | `.tempo strong` 62 px / 0.82 line | Berkeley Mono Regular |
| Metric value | `.metric .n` | `.metric .n` 18 px | Berkeley Mono Regular |
| Delta title | `.delta-title` | `.delta-title` 11 px / 700 italic | Countach Bold Italic |
| Footer note | `.footer span` | `.footer` 9 px | Berkeley Mono Regular |
| Detail surface title | `#detail-title` | `.detail-head > span:first-child` 18 px | Countach Regular |
| Detail label | `.detail-row span:first-child` | `.detail-row` 11 px | Berkeley Mono Regular |
| Detail value | `.detail-row span:nth-child(2)` | `.detail-row` 11 px | Berkeley Mono Regular |

Files in the optical source boundary:

- `/Users/spectrasynq/SpectraSynq-EdgeAI-Lab/tools/serial-studio/webview/bridge.py`
- `/Users/spectrasynq/SpectraSynq-EdgeAI-Lab/tools/serial-studio/webview/app.js`
- `/Users/spectrasynq/SpectraSynq-EdgeAI-Lab/tools/serial-studio/webview/index.html`
- `/Users/spectrasynq/SpectraSynq-EdgeAI-Lab/tools/serial-studio/webview/styles.css`
- `/Users/spectrasynq/SpectraSynq-EdgeAI-Lab/tools/serial-studio/webview/font-assets.json`
- the three fixture JSON files SHA-pinned by `MEASURED.json`

Layout audit: each parent uses one positioning system. The shell and instrument
rail use CSS Grid; cards use Grid/Flex within their own parent. There are no
negative margins, transforms, floating stacks, or mixed absolute/Flex repairs.
