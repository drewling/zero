import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
import test from 'node:test';

const require = createRequire(import.meta.url);
const { chromium, webkit } = require('/Users/light/node_modules/.pnpm/playwright@1.58.2/node_modules/playwright');
const base = process.env.LANDING_URL ?? 'http://127.0.0.1:8877/';

const engines = [
  ['chromium', chromium],
  ['webkit', webkit],
];

const stateAt = async (page) => page.evaluate(() => {
  const code = document.querySelector('#term code');
  const overlays = [...document.querySelectorAll('#term .typed-letter')];
  const visible = (element) => {
    if (!element) return false;
    const style = getComputedStyle(element);
    const rect = element.getBoundingClientRect();
    return style.visibility !== 'hidden' && style.display !== 'none' && rect.width > 0 && rect.height > 0;
  };
  const copy = document.querySelector('#copy');
  const term = document.querySelector('#term');
  return {
    codeVisible: visible(code),
    overlayCount: overlays.filter(visible).length,
    overlayPositions: overlays.map((element) => getComputedStyle(element).position),
    caretVisible: visible(document.querySelector('#term .tcur')),
    copyHidden: copy?.hidden ?? true,
    copyRect: copy && term ? (() => {
      const copyRect = copy.getBoundingClientRect();
      const termRect = term.getBoundingClientRect();
      return { x: copyRect.x - termRect.x, y: copyRect.y - termRect.y, width: copyRect.width, height: copyRect.height };
    })() : null,
  };
});

for (const [name, browserType] of engines) {
  test(`${name} terminal typing keeps one visible command at 1440 and 390`, async (t) => {
    const browser = await browserType.launch({ headless: true });
    t.after(() => browser.close());

    for (const width of [1440, 390]) {
      const context = await browser.newContext({
        viewport: { width, height: width === 1440 ? 900 : 844 },
        reducedMotion: 'no-preference',
        colorScheme: 'light',
      });
      const page = await context.newPage();
      await page.goto(base, { waitUntil: 'networkidle' });
      await page.locator('#term').evaluate((element) => {
        const top = element.getBoundingClientRect().top + window.scrollY;
        window.scrollTo(0, Math.max(0, top - (window.innerHeight - element.getBoundingClientRect().height) / 2));
      });
      await page.evaluate(() => { scrollBy(0, 1); scrollBy(0, -1); });
      await page.waitForTimeout(100);
      for (let attempt = 0; attempt < 4; attempt++) {
        if (await page.evaluate(() => ['play', 'done'].includes(document.querySelector('#term').dataset.mode))) break;
        await page.mouse.wheel(0, -1000);
        await page.waitForTimeout(150);
        await page.mouse.wheel(0, 1000);
        await page.waitForTimeout(350);
      }
      await page.waitForFunction(() => ['play', 'done'].includes(document.querySelector('#term').dataset.mode), undefined, { timeout: 5000 });
      const baseline = await page.evaluate(() => {
        const copy = document.querySelector('#copy'), term = document.querySelector('#term');
        if (!copy || copy.hidden || !term) return null;
        const copyRect = copy.getBoundingClientRect(), termRect = term.getBoundingClientRect();
        return { x: copyRect.x - termRect.x, y: copyRect.y - termRect.y, width: copyRect.width, height: copyRect.height };
      });

      for (const elapsed of [150, 500, 850, 1600]) {
        await page.waitForTimeout(elapsed === 150 ? 150 : elapsed === 500 ? 350 : elapsed === 850 ? 350 : 750);
        const state = await stateAt(page);
        assert.equal(state.codeVisible && state.overlayCount > 0, false, `${name} ${width}px ${elapsed}ms duplicated command`);
        assert.equal(state.overlayPositions.every((position) => position === 'absolute'), true, `${name} ${width}px ${elapsed}ms overlay position`);
        if (baseline) {
          assert.equal(state.copyHidden, false, `${name} ${width}px copy control unexpectedly hidden`);
          assert.deepEqual(state.copyRect, baseline, `${name} ${width}px copy slot moved at ${elapsed}ms`);
        } else {
          assert.equal(state.copyHidden, true, `${name} ${width}px copy control unexpectedly exposed`);
        }
        if (elapsed < 1600 && !state.caretVisible) {
          assert.equal(state.codeVisible, true, `${name} ${width}px caret missing before command settled at ${elapsed}ms`);
          assert.equal(state.overlayCount, 0, `${name} ${width}px caret missing with active overlay at ${elapsed}ms`);
        }
      }

      await page.waitForFunction(() => {
        const code = document.querySelector('#term code');
        const overlays = [...document.querySelectorAll('#term .typed-letter')];
        const codeVisible = getComputedStyle(code).visibility !== 'hidden';
        const overlaysVisible = overlays.some((element) => getComputedStyle(element).visibility !== 'hidden');
        return codeVisible && !overlaysVisible;
      }, undefined, { timeout: 3000 });
      const final = await stateAt(page);
      assert.equal(final.codeVisible, true, `${name} ${width}px final command visible`);
      assert.equal(final.overlayCount, 0, `${name} ${width}px final overlays cleared`);
      await context.close();
    }
  });
}
