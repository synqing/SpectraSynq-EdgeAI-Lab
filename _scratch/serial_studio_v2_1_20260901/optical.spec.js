const { test, expect } = require('@playwright/test');

const surfaces = [
  ['mission-control', 'http://127.0.0.1:8766/?view=mission-control'],
  ['audio-reference', 'http://127.0.0.1:8767/?view=audio-reference'],
  ['ap-validation', 'http://127.0.0.1:8768/?view=ap-validation'],
];
const viewports = [
  { width: 1440, height: 900 },
  { width: 1180, height: 720 },
];

for (const [surface, url] of surfaces) {
  for (const viewport of viewports) {
    test(`${surface} ${viewport.width}x${viewport.height}`, async ({ page }) => {
      await page.setViewportSize(viewport);
      await page.goto(url);
      await page.evaluate(() => document.fonts.ready);
      await page.waitForTimeout(650);
      const measured = await page.evaluate(() => {
        const title = document.querySelector('.title');
        const tempo = document.querySelector('.tempo strong');
        const micro = document.querySelector('.eyebrow');
        const body = document.body;
        return {
          viewport: { width: window.innerWidth, height: window.innerHeight },
          scroll: { width: body.scrollWidth, height: body.scrollHeight },
          fonts: {
            countachRegular: document.fonts.check('28px Countach'),
            countachItalic: document.fonts.check('italic 700 12px Countach'),
            berkeleyMono: document.fonts.check('18px Berkeley'),
          },
          computed: {
            titleFamily: title ? getComputedStyle(title).fontFamily : null,
            titleSize: title ? getComputedStyle(title).fontSize : null,
            tempoFamily: tempo ? getComputedStyle(tempo).fontFamily : null,
            tempoSize: tempo ? getComputedStyle(tempo).fontSize : null,
            microSize: micro ? getComputedStyle(micro).fontSize : null,
          },
          structure: {
            instrumentCells: document.querySelectorAll('.instrument > div').length,
            deviceCards: document.querySelectorAll('.device').length,
            detailRows: document.querySelectorAll('.detail-row').length,
            deltaCells: document.querySelectorAll('.delta > div').length,
          },
          labels: [...document.querySelectorAll('.instrument .eyebrow')].map(node => node.textContent),
          audioState: document.querySelector('#audio-ref-state')?.textContent,
        };
      });
      console.log(`V2_1_OPTICAL=${JSON.stringify({ surface, ...measured })}`);
      expect(measured.scroll.width).toBeLessThanOrEqual(viewport.width);
      expect(measured.scroll.height).toBeLessThanOrEqual(viewport.height);
      expect(measured.fonts.countachRegular).toBe(true);
      expect(measured.fonts.countachItalic).toBe(true);
      expect(measured.fonts.berkeleyMono).toBe(true);
      expect(measured.structure.instrumentCells).toBe(6);
      expect(measured.labels).toContain('AUDIO REF');
      if (surface === 'mission-control') {
        expect(measured.structure.deviceCards).toBe(2);
        expect(measured.structure.deltaCells).toBe(6);
      } else {
        expect(measured.structure.detailRows).toBe(8);
      }
      await page.screenshot({
        path: `output/playwright/k1-v2-1-${surface}-${viewport.width}x${viewport.height}.png`,
        fullPage: true,
      });
    });
  }
}
