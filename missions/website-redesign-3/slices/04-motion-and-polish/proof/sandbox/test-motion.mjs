import test from 'node:test';
import assert from 'node:assert/strict';
import { createServer } from 'node:http';
import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve, dirname, extname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';

const here = dirname(fileURLToPath(import.meta.url));
const repo = resolve(here, '../../../../../..');
const require = createRequire(process.env.PLAYWRIGHT_PACKAGE || `${process.env.HOME}/.nvm/versions/node/v22.16.0/lib/node_modules/playwright/package.json`);
const { chromium, webkit } = require('playwright');
const engine = process.env.ENGINE === 'webkit' ? webkit : chromium;
const reference = resolve(here, '../../../02-references-and-comps/proof/comps/kit/motion.js');
const mime = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.woff2': 'font/woff2', '.svg': 'image/svg+xml' };
let browser, server, base;
const errors = [];

test.before(async () => {
  server = createServer(async (req, res) => {
    try {
      const url = new URL(req.url, 'http://localhost');
      let path = resolve(repo, '.' + decodeURIComponent(url.pathname));
      if (!path.startsWith(repo + '/')) throw new Error('outside test root');
      if (process.env.BASELINE === '1' && path === resolve(here, 'motion.js')) path = reference;
      const bytes = await readFile(path);
      res.writeHead(200, { 'Content-Type': mime[extname(path)] || 'application/octet-stream' });
      res.end(bytes);
    } catch { res.writeHead(404); res.end('Not found'); }
  });
  await new Promise(r => server.listen(0, '127.0.0.1', r));
  base = `http://127.0.0.1:${server.address().port}/${here.slice(repo.length + 1)}/index.html`;
  browser = await engine.launch({ headless: true, ...(process.env.WEBKIT_EXECUTABLE && engine === webkit ? { executablePath: process.env.WEBKIT_EXECUTABLE } : {}) });
});
test.after(async () => { await browser?.close(); await new Promise(r => server?.close(r)); });

async function open(query = '', options = {}) {
  const context = await browser.newContext({ viewport: { width: 1440, height: 1000 }, ...options });
  const page = await context.newPage();
  page.on('pageerror', e => errors.push(e.message));
  await page.addInitScript(() => {
    window.countSteps = [];
    new MutationObserver(records => {
      for (const r of records) if (r.target.id === 'count') window.countSteps.push(Number(r.target.textContent));
    }).observe(document, { childList: true, subtree: true, characterData: true });
  });
  await page.goto(base + query);
  await page.evaluate(() => document.fonts.ready);
  return { context, page };
}
async function settled(page, expected = 'done') {
  await page.waitForFunction(() => ['done', 'static', 'error', 'cancelled'].includes(document.querySelector('#story').dataset.mode), null, { timeout: 10000 });
  const result = await page.evaluate(() => ({ mode: document.querySelector('#story').dataset.mode, error: window.controller?.error?.message, durationMs: window.controller?.durationMs }));
  assert.equal(result.mode, expected, JSON.stringify(result));
}
async function finalState(page) {
  return page.evaluate(() => ({
    count: document.querySelector('#count').textContent,
    rows: [...document.querySelectorAll('.archive-row')].map(e => getComputedStyle(e).visibility),
    classes: [...document.querySelector('#story').classList].filter(c => /^lt-/.test(c)),
    overlays: document.querySelectorAll('.cursor,.zr,.fly').length,
    label: document.querySelector('#run-label').textContent
  }));
}

test('static and reduced motion are pixel-identical to no-JS HTML', async () => {
  const disabled = await open('', { javaScriptEnabled: false });
  const staticPage = await open('?static');
  const reduced = await open('', { reducedMotion: 'reduce' });
  try {
    const golden = await disabled.page.locator('#story').screenshot();
    assert.deepEqual(await staticPage.page.locator('#story').screenshot(), golden);
    assert.deepEqual(await reduced.page.locator('#story').screenshot(), golden);
    assert.equal((await finalState(staticPage.page)).overlays, 0);
  } finally { await Promise.all([disabled, staticPage, reduced].map(x => x.context.close())); }
});

test('coarse pointers never receive an animated cursor even at desktop width', async () => {
  const { context, page } = await open('?frame=1', { hasTouch: true, isMobile: true });
  try { assert.equal(await page.locator('.cursor:visible').count(), 0); }
  finally { await context.close(); }
});

test('reduced motion takes precedence over QA frame rewinding', async () => {
  const { context, page } = await open('?frame=0', { reducedMotion: 'reduce' });
  try { assert.equal((await finalState(page)).count, '4'); assert.deepEqual((await finalState(page)).classes, []); }
  finally { await context.close(); }
});

test('bad frame input is clamped to a valid static frame without an exception', async () => {
  const { context, page } = await open('?frame=oops');
  try { assert.equal((await finalState(page)).count, '4'); assert.deepEqual(errors, []); }
  finally { await context.close(); errors.length = 0; }
});

test('switching to reduced motion mid-story cancels and settles immediately', async () => {
  const { context, page } = await open();
  try {
    await page.waitForFunction(() => document.querySelector('#story').dataset.mode === 'play');
    await page.emulateMedia({ reducedMotion: 'reduce' });
    await settled(page, 'cancelled');
    const state = await finalState(page);
    assert.equal(state.count, '4'); assert.equal(state.overlays, 0); assert.deepEqual(state.classes, []);
    await page.waitForTimeout(300);
    assert.deepEqual(await finalState(page), state);
  } finally { await context.close(); }
});

test('missing animation target falls back to the complete final state', async () => {
  const { context, page } = await open('?fault=target');
  try { await settled(page, 'error'); assert.equal((await finalState(page)).count, '4'); assert.equal((await finalState(page)).overlays, 0); }
  finally { await context.close(); }
});

test('replay cannot overlap, keyboard replay works, and completed story has no overlays', async () => {
  const { context, page } = await open();
  try {
    await settled(page);
    await page.locator('#replay').focus();
    await page.keyboard.press('Enter');
    await page.waitForFunction(() => document.querySelector('#story').dataset.mode === 'play');
    assert.equal(await page.evaluate(() => Zm.play(document.querySelector('#story'), window.story) === window.controller.pending), true);
    await settled(page);
    assert.equal((await finalState(page)).count, '4'); assert.equal((await finalState(page)).overlays, 0);
    assert.deepEqual(errors, []);
  } finally { await context.close(); errors.length = 0; }
});

test('320 and 390 px playback has no horizontal overflow, no cursor and no layout shift', async () => {
  for (const width of [320, 390]) {
    const { context, page } = await open('', { viewport: { width, height: 920 }, hasTouch: true, isMobile: true });
    try {
      await settled(page);
      const metrics = await page.evaluate(() => ({ cls: window.cls, overflow: document.documentElement.scrollWidth > innerWidth, cursor: document.querySelectorAll('.cursor').length }));
      assert.equal(metrics.overflow, false); assert.equal(metrics.cursor, 0); assert.equal(metrics.cls, 0);
    } finally { await context.close(); }
  }
});

test('zoom rectangles and overlay transforms land on whole CSS pixels', async () => {
  const { context, page } = await open('?frame=1');
  try {
    const geometry = await page.locator('.zr').evaluateAll(es => es.map(e => ({ left: e.style.left, top: e.style.top, width: e.style.width, height: e.style.height })));
    assert.ok(geometry.length > 0);
    for (const rect of geometry) for (const value of Object.values(rect)) assert.equal(Number.parseFloat(value) % 1, 0);
  } finally { await context.close(); }
});

test('visibilitychange cancellation has no late mutations and re-enables replay on return (synthetic visibility event)', async () => {
  const { context, page } = await open();
  try {
    await page.evaluate(() => { Object.defineProperty(document, 'hidden', { configurable: true, value: true }); document.dispatchEvent(new Event('visibilitychange')); });
    await settled(page, 'cancelled');
    const final = await finalState(page);
    await page.waitForTimeout(350);
    assert.deepEqual(await finalState(page), final);
    await page.evaluate(() => { Object.defineProperty(document, 'hidden', { configurable: true, value: false }); document.dispatchEvent(new Event('visibilitychange')); });
    assert.equal(await page.locator('#replay').isDisabled(), false);
  } finally { await context.close(); }
});

test('viewport change aborts a running story rather than using stale geometry', async () => {
  const { context, page } = await open();
  try {
    await page.setViewportSize({ width: 390, height: 920 });
    await settled(page, 'cancelled');
    assert.equal((await finalState(page)).overlays, 0);
  } finally { await context.close(); }
});

test('active playback really lands eight envelopes and completes within six seconds', async () => {
  const timings = [];
  for (const width of [1440, 390]) {
    const { context, page } = await open('', { viewport: { width, height: 1000 } });
    try {
      await settled(page);
      const result = await page.evaluate(() => ({ mode: document.querySelector('#story').dataset.mode, durationMs: controller.durationMs, error: controller.error?.message, steps: countSteps.filter((v, i) => i === 0 || v !== countSteps[i - 1]), cls: window.cls }));
      assert.deepEqual(result.steps.slice(result.steps.indexOf(12)), [12, 11, 10, 9, 8, 7, 6, 5, 4]);
      assert.equal(result.error, undefined); assert.equal(result.cls, 0, JSON.stringify(await page.evaluate(() => window.shifts)));
      assert.ok(result.durationMs >= 3500 && result.durationMs <= 6000, JSON.stringify(result));
      timings.push({ width, ...result });
    } finally { await context.close(); }
  }
  console.log('PLAYBACK_TIMING ' + JSON.stringify(timings));
  if (process.env.CAPTURE === '1') {
    await mkdir(resolve(here, 'evidence'), { recursive: true });
    await writeFile(resolve(here, `evidence/timing-${engine === webkit ? 'webkit' : 'chromium'}.json`), JSON.stringify(timings, null, 2) + '\n');
  }
});

test('time the designer reference in an active local renderer, without asserting an unobserved throttling cause', { skip: process.env.REFERENCE_TIMING !== '1' }, async () => {
  const context = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
  const page = await context.newPage();
  try {
    await page.addInitScript(() => {
      window.referenceTiming = {};
      new MutationObserver(records => { for (const r of records) {
        if (r.target === document.body && r.attributeName === 'data-mode') {
          const mode = document.body.dataset.mode;
          if (mode === 'play' && !referenceTiming.start) referenceTiming.start = performance.now();
          if (mode === 'done') referenceTiming.end = performance.now();
        }
      } }).observe(document, { subtree: true, attributes: true, attributeFilter: ['data-mode'] });
    });
    await page.goto(base.replace(/04-motion-and-polish\/proof\/sandbox\/index.html$/, '02-references-and-comps/proof/comps/hero-a/index.html'));
    await page.waitForFunction(() => document.body.dataset.mode === 'done', null, { timeout: 15000 });
    const timing = await page.evaluate(() => ({ durationMs: Math.round(referenceTiming.end - referenceTiming.start), count: document.querySelector('.zp-count strong').textContent, engine: navigator.userAgent }));
    assert.equal(timing.count, '4'); assert.ok(Number.isFinite(timing.durationMs));
    console.log('REFERENCE_TIMING ' + JSON.stringify(timing));
    await mkdir(resolve(here, 'evidence'), { recursive: true });
    await writeFile(resolve(here, 'evidence/reference-timing.json'), JSON.stringify(timing, null, 2) + '\n');
  } finally { await context.close(); }
});

// One batched frame-strip capture, not a polishing loop. Run CAPTURE=1 after green.
test('capture draft storyboard evidence when explicitly requested', { skip: process.env.CAPTURE !== '1' }, async () => {
  await mkdir(resolve(here, 'evidence'), { recursive: true });
  for (const width of [1440, 390]) {
    for (let frame = 0; frame < 5; frame++) {
      const { context, page } = await open(`?frame=${frame}`, { viewport: { width, height: 1000 } });
      try { await page.locator('#story').screenshot({ path: resolve(here, `evidence/${width}-frame-${frame}.png`) }); }
      finally { await context.close(); }
    }
    const { context, page } = await open('', { viewport: { width, height: 1000 }, reducedMotion: 'reduce' });
    try { await page.locator('#story').screenshot({ path: resolve(here, `evidence/${width}-reduced.png`) }); }
    finally { await context.close(); }
  }
  await writeFile(resolve(here, 'evidence/capture.json'), JSON.stringify({ date: new Date().toISOString(), source: 'draft 3e1b0ac', widths: [1440, 390], engine: await browser.version() }, null, 2) + '\n');
});
