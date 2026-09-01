const { test, expect } = require('@playwright/test');

const mockup = 'file:///Users/spectrasynq/SpectraSynq-EdgeAI-Lab/_scratch/serial_studio_v2_20260831/mockup.html';

for (const viewport of [{ width: 1440, height: 900 }, { width: 1180, height: 720 }]) {
  test(`mission control optical metrics ${viewport.width}x${viewport.height}`, async ({ page }) => {
    await page.setViewportSize(viewport);
    await page.goto(mockup);
    await page.evaluate(() => document.fonts.ready);
    const measured = await page.evaluate(() => {
      const body = document.body;
      const title = document.querySelector('.title');
      const tempo = document.querySelector('.tempo strong');
      const micro = document.querySelector('.eyebrow');
      return {
        viewport: { width: window.innerWidth, height: window.innerHeight },
        scroll: { width: body.scrollWidth, height: body.scrollHeight },
        fonts: {
          countachRegular: document.fonts.check('28px Countach'),
          countachItalic: document.fonts.check('italic 700 12px Countach'),
          berkeleyMono: document.fonts.check('18px Berkeley')
        },
        computed: {
          titleFamily: getComputedStyle(title).fontFamily,
          titleSize: getComputedStyle(title).fontSize,
          tempoFamily: getComputedStyle(tempo).fontFamily,
          tempoSize: getComputedStyle(tempo).fontSize,
          microSize: getComputedStyle(micro).fontSize
        },
        deviceCards: document.querySelectorAll('.device').length,
        instrumentCells: document.querySelectorAll('.instrument > div').length,
        deltaCells: document.querySelectorAll('.delta > div').length
      };
    });
    console.log(`OPTICAL_MEASURED=${JSON.stringify(measured)}`);
    expect(measured.scroll.width).toBeLessThanOrEqual(viewport.width);
    expect(measured.scroll.height).toBeLessThanOrEqual(viewport.height);
    expect(measured.fonts.countachRegular).toBe(true);
    expect(measured.fonts.countachItalic).toBe(true);
    expect(measured.fonts.berkeleyMono).toBe(true);
    expect(measured.deviceCards).toBe(2);
    expect(measured.instrumentCells).toBe(5);
    expect(measured.deltaCells).toBe(6);
  });
}
