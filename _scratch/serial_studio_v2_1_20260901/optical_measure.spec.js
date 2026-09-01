const { test, expect } = require('@playwright/test');

const cropRoot = '_scratch/serial_studio_v2_1_20260901/crops';
const roles = [
  ['mission_kicker', 'http://127.0.0.1:8766/?view=mission-control', '#mode-kicker'],
  ['mission_title', 'http://127.0.0.1:8766/?view=mission-control', '#surface-title'],
  ['project_build', 'http://127.0.0.1:8766/?view=mission-control', '.build'],
  ['instrument_eyebrow', 'http://127.0.0.1:8766/?view=mission-control', '.instrument .eyebrow'],
  ['instrument_status', 'http://127.0.0.1:8766/?view=mission-control', '#audio-ref-state'],
  ['device_role', 'http://127.0.0.1:8766/?view=mission-control', '#source-0 .role'],
  ['tempo_hero', 'http://127.0.0.1:8766/?view=mission-control', '#source-0 .tempo strong'],
  ['metric_value', 'http://127.0.0.1:8766/?view=mission-control', '#source-0 .metric .n'],
  ['delta_title', 'http://127.0.0.1:8766/?view=mission-control', '.delta-title'],
  ['footer_note', 'http://127.0.0.1:8766/?view=mission-control', '.footer span'],
  ['detail_title', 'http://127.0.0.1:8767/?view=audio-reference', '#detail-title'],
  ['detail_label', 'http://127.0.0.1:8767/?view=audio-reference', '.detail-row span:first-child'],
  ['detail_value', 'http://127.0.0.1:8767/?view=audio-reference', '.detail-row span:nth-child(2)'],
];

for (const [role, url, selector] of roles) {
  test(`measure ${role}`, async ({ page }) => {
    await page.setViewportSize({ width: 1440, height: 900 });
    await page.goto(url);
    await page.evaluate(() => document.fonts.ready);
    await page.waitForTimeout(650);
    const node = page.locator(selector).first();
    await expect(node).toBeVisible();
    const measured = await node.evaluate(element => {
      const style = getComputedStyle(element);
      const rect = element.getBoundingClientRect();
      const range = document.createRange();
      range.selectNodeContents(element);
      const textRect = range.getBoundingClientRect();
      return {
        role: element.id || element.className || element.tagName,
        text: element.textContent,
        box: { x: rect.x, y: rect.y, width: rect.width, height: rect.height },
        text_box: { x: textRect.x, y: textRect.y, width: textRect.width, height: textRect.height },
        family: style.fontFamily,
        size_px: Number.parseFloat(style.fontSize),
        line_height_px: Number.parseFloat(style.lineHeight),
        weight: style.fontWeight,
        style: style.fontStyle,
        colour: style.color,
      };
    });
    const crop = `${cropRoot}/${role}.png`;
    await page.screenshot({ path: crop, clip: measured.text_box });
    console.log(`ROLE_MEASURE=${JSON.stringify({ role, crop, ...measured })}`);
  });
}
