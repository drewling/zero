import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
import test from 'node:test';

const require = createRequire(import.meta.url);
const { chromium, webkit } = require('/Users/light/node_modules/.pnpm/playwright@1.58.2/node_modules/playwright');
const base = process.env.LANDING_URL ?? 'http://127.0.0.1:8877/';
const engines = [['chromium', chromium], ['webkit', webkit]];
const sections = ['.ledger', '#rules-win', '#undo-win', '#term'];

async function finalState(page) {
  return page.evaluate(() => {
    const visible = (el) => {
      if (!el) return false;
      const style = getComputedStyle(el);
      const rect = el.getBoundingClientRect();
      return style.visibility !== 'hidden' && style.display !== 'none' && rect.width > 0 && rect.height > 0;
    };
    const hero = document.querySelector('#hero');
    const folder = hero?.querySelector('.folder');
    const settings = document.querySelector('#rules-win .tabs span.on');
    const copy = document.querySelector('#term code');
    return {
      overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
      bodyOverflow: document.body.scrollWidth - document.body.clientWidth,
      heroMode: hero?.dataset.mode,
      heroSettled: folder?.classList.contains('sel') && visible(folder?.querySelector('.f-full')),
      runPressed: !!hero?.querySelector('.zp-run.pressed'),
      rulesTab: settings?.textContent,
      rulesVisible: [...document.querySelectorAll('#rules-win .editor .ln')].every(visible),
      ants: !!document.querySelector('.bound.ants'),
      undoBalloon: visible(document.querySelector('.undo-obj .balloon')),
      terminalCommand: visible(copy) && copy?.textContent.includes('zero.headless.com/install'),
      terminalOverlays: document.querySelectorAll('#term [data-zm-overlay]').length,
      pressed: document.querySelectorAll('.pressed').length,
    };
  });
}

async function sectionProgress(page, selector) {
  return page.evaluate((sel) => {
    const visible = (el) => {
      if (!el) return false;
      const style = getComputedStyle(el);
      const rect = el.getBoundingClientRect();
      return style.visibility !== 'hidden' && style.display !== 'none' && rect.width > 0 && rect.height > 0;
    };
    const rowsVisible = [...document.querySelectorAll('.ledger .info .row')].every(visible);
    const settings = document.querySelector('#rules-win .tabs span.on')?.textContent?.trim();
    const terminalCode = document.querySelector('#term code');
    const mode = document.querySelector(sel)?.dataset.mode;
    const done = mode === 'done' && (sel === '.ledger'
      ? rowsVisible && !document.querySelector('.bound.ants')
      : sel === '#rules-win'
        ? settings === 'Settings' && [...document.querySelectorAll('#rules-win .editor .ln')].every(visible)
        : sel === '#undo-win'
          ? visible(document.querySelector('.undo-obj .balloon'))
          : visible(terminalCode) && terminalCode.textContent.includes('zero.headless.com/install') &&
            document.querySelectorAll('#term [data-zm-overlay]').length === 0);
    return {
      done,
      mode,
      pressed: document.querySelectorAll('.pressed').length,
      zoom: document.querySelectorAll('#term .zr').length,
    };
  }, selector);
}

async function waitForSection(page, selector, onSample) {
  // Scroll the actual document until the section has a substantial viewport share.
  // This mirrors a reader moving through the page and reliably crosses the runtime's
  // 35% IntersectionObserver threshold in both engines.
  await page.evaluate((sel) => {
    const root = document.querySelector(sel);
    const rect = root.getBoundingClientRect();
    const html = document.documentElement;
    const priorBehavior = html.style.scrollBehavior;
    html.style.scrollBehavior = 'auto';
    window.scrollTo(0, Math.max(0, window.scrollY + rect.top - innerHeight * .1));
    window.scrollBy(0, 1);
    window.scrollBy(0, -1);
    html.style.scrollBehavior = priorBehavior;
  }, selector);
  const deadline = Date.now() + 16000;
  let lastKick = Date.now();
  let last;
  while (Date.now() < deadline) {
    const progress = await sectionProgress(page, selector);
    last = progress;
    onSample(progress);
    if (progress.done) return;
    if (Date.now() - lastKick >= 1000) {
      await page.evaluate(() => { window.scrollBy(0, 1); window.scrollBy(0, -1); });
      lastKick = Date.now();
    }
    await page.waitForTimeout(50);
  }
  throw new Error(`${selector} did not reach its observable final state: ${JSON.stringify(last)}`);
}

for (const [name, browserType] of engines) {
  test(`${name} stronger motion completes real section playback at 320 and 768`, async (t) => {
    const browser = await browserType.launch({ headless: true });
    t.after(() => browser.close());
    for (const width of [320, 768]) {
      const errors = [];
      const context = await browser.newContext({ viewport: { width, height: 844 }, reducedMotion: 'no-preference' });
      const page = await context.newPage();
      page.on('console', (message) => { if (message.type() === 'error') errors.push(message.text()); });
      page.on('pageerror', (error) => errors.push(error.message));
      await page.goto(base, { waitUntil: 'networkidle' });
      let seenPress = false;
      let seenZoom = false;
      for (let i = 0; i < 120; i++) {
        const state = await page.evaluate(() => ({ pressed: document.querySelectorAll('.pressed').length, zoom: document.querySelectorAll('#term .zr').length }));
        seenPress ||= state.pressed > 0;
        seenZoom ||= state.zoom > 0;
        await page.waitForTimeout(50);
      }
      for (const selector of sections) {
        await waitForSection(page, selector, (state) => {
          seenPress ||= state.pressed > 0;
          seenZoom ||= state.zoom > 0;
        });
      }
      const state = await finalState(page);
      assert.equal(state.overflow, 0, `${name} ${width}px document overflow`);
      assert.equal(state.bodyOverflow, 0, `${name} ${width}px body overflow`);
      assert.equal(state.heroSettled, true, `${name} ${width}px hero settled`);
      assert.equal(state.rulesTab, 'Settings', `${name} ${width}px rules final tab`);
      assert.equal(state.rulesVisible, true, `${name} ${width}px rules visible`);
      assert.equal(state.ants, false, `${name} ${width}px ants cleared`);
      assert.equal(state.undoBalloon, true, `${name} ${width}px undo balloon`);
      assert.equal(state.terminalCommand, true, `${name} ${width}px terminal command`);
      assert.equal(state.terminalOverlays, 0, `${name} ${width}px terminal overlays cleared`);
      assert.equal(state.pressed, 0, `${name} ${width}px pressed classes cleared`);
      assert.equal(seenPress, true, `${name} ${width}px observed finite press`);
      assert.equal(seenZoom, true, `${name} ${width}px observed terminal zoom`);
      assert.deepEqual(errors, [], `${name} ${width}px console errors`);
      await context.close();
    }
  });

  test(`${name} static, reduced-motion, and no-JS states keep final public output`, async (t) => {
    const browser = await browserType.launch({ headless: true });
    t.after(() => browser.close());
    for (const variant of ['static', 'reduced', 'nojs']) {
      const context = await browser.newContext({ viewport: { width: 320, height: 700 }, reducedMotion: variant === 'reduced' ? 'reduce' : 'no-preference', javaScriptEnabled: variant !== 'nojs' });
      const page = await context.newPage();
      await page.goto(`${base}${variant === 'static' ? '?static' : ''}`, { waitUntil: 'networkidle' });
      if (variant !== 'nojs') await page.waitForTimeout(250);
      const state = await finalState(page);
      assert.equal(state.overflow, 0, `${name} ${variant} overflow`);
      assert.equal(state.bodyOverflow, 0, `${name} ${variant} body overflow`);
      assert.equal(state.heroSettled, true, `${name} ${variant} hero final frame`);
      assert.equal(state.rulesTab, 'Settings', `${name} ${variant} rules final tab`);
      assert.equal(state.rulesVisible, true, `${name} ${variant} rules visible`);
      assert.equal(state.ants, false, `${name} ${variant} ants absent`);
      assert.equal(state.undoBalloon, true, `${name} ${variant} undo final frame`);
      assert.equal(state.terminalCommand, true, `${name} ${variant} terminal command`);
      assert.equal(state.terminalOverlays, 0, `${name} ${variant} terminal overlays`);
      assert.equal(state.pressed, 0, `${name} ${variant} pressed classes`);
      await context.close();
    }
  });

  test(`${name} hero CTA and End-key navigation settle the terminal`, async (t) => {
    const browser = await browserType.launch({ headless: true });
    t.after(() => browser.close());
    for (const width of [1440, 390]) {
      for (const waitMs of [300, 6000]) {
        for (const useEnd of [false, true]) {
          const context = await browser.newContext({ viewport: { width, height: 844 }, reducedMotion: 'no-preference' });
          const page = await context.newPage();
          await page.goto(base, { waitUntil: 'networkidle' });
          await page.waitForTimeout(waitMs);
          await page.locator('.hero a.btn.default').click();
          if (useEnd) await page.keyboard.press('End');
          await page.waitForTimeout(4000);
          const state = await page.evaluate(() => {
            const term = document.querySelector('#term');
            const code = term?.querySelector('code');
            return {
              hiddenFrame: [...(term?.classList ?? [])].some((name) => /^lt-\d+$/.test(name)),
              codeVisible: !!code && getComputedStyle(code).visibility !== 'hidden' && code.getBoundingClientRect().height > 0,
              overlays: term?.querySelectorAll('[data-zm-overlay]').length ?? -1,
            };
          });
          assert.equal(state.hiddenFrame, false, `${name} ${width}px ${waitMs}ms ${useEnd ? 'End' : 'CTA'} terminal frame`);
          assert.equal(state.codeVisible, true, `${name} ${width}px ${waitMs}ms ${useEnd ? 'End' : 'CTA'} command visible`);
          assert.equal(state.overlays, 0, `${name} ${width}px ${waitMs}ms ${useEnd ? 'End' : 'CTA'} overlays`);
          await context.close();
        }
      }
    }
  });
}
