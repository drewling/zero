import test from 'node:test';
import assert from 'node:assert/strict';
import { createServer } from 'node:http';
import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve, dirname, extname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';

const here = dirname(fileURLToPath(import.meta.url));
const repo = resolve(here, '../../../../../../..');
const require = createRequire(process.env.PLAYWRIGHT_PACKAGE || `${process.env.HOME}/.nvm/versions/node/v22.16.0/lib/node_modules/playwright/package.json`);
const { chromium, webkit } = require('playwright');
const engine = process.env.ENGINE === 'webkit' ? webkit : chromium;
let browser, server, base;
const kept = [
  ['Alex Rivera', 'Can you approve the quote?', '11h'],
  ['Priya Sharma', 'Which date works for you?', '13h'],
  ['Daniel Kim', 'Your payment failed', '1d'],
  ['Sarah Mitchell', 'Contract changes to review', '1d']
];

test.before(async () => {
  if (process.env.CAPTURE === '1') await mkdir(resolve(here, 'evidence'), { recursive: true });
  server = createServer(async (req, res) => {
    try {
      const path = resolve(repo, '.' + decodeURIComponent(new URL(req.url, 'http://localhost').pathname));
      if (!path.startsWith(repo + '/')) throw new Error('outside test root');
      const bytes = await readFile(process.env.RUNNER_BASELINE === '1' && path === resolve(here, '../motion.js') ? resolve(here, '../sections/reference/pre-sections-runner.js') : path);
      res.writeHead(200, { 'Content-Type': ({ '.html': 'text/html', '.css': 'text/css', '.js': 'text/javascript', '.woff2': 'font/woff2' })[extname(path)] || 'application/octet-stream' });
      res.end(bytes);
    } catch { res.writeHead(404); res.end('Not found'); }
  });
  await new Promise(r => server.listen(0, '127.0.0.1', r));
  const target = process.env.BASELINE === '1' ? 'missions/website-redesign-3/slices/02-references-and-comps/proof/comps/hero-b/index.html' : here.slice(repo.length + 1) + '/index.html';
  base = `http://127.0.0.1:${server.address().port}/${target}`;
  browser = await engine.launch({ headless: true, ...(engine === webkit && process.env.WEBKIT_EXECUTABLE ? { executablePath: process.env.WEBKIT_EXECUTABLE } : {}) });
});
test.after(async () => { await browser?.close(); await new Promise(r => server?.close(r)); });

async function open(query = '', width = 1440, options = {}) {
  const context = await browser.newContext({ viewport: { width, height: 1000 }, ...options });
  const page = await context.newPage();
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  await page.goto(base + query);
  await page.evaluate(() => document.fonts.ready);
  return { context, page, errors };
}
async function settle(page, expected = 'done') {
  await page.waitForFunction(() => ['done', 'static', 'cancelled', 'error'].includes(document.body.dataset.mode), null, { timeout: 10000 });
  assert.equal(await page.evaluate(() => document.body.dataset.mode), expected);
}
async function state(page) {
  return page.evaluate(() => ({
    frame: Number(document.body.dataset.f), mode: document.body.dataset.mode,
    label: document.querySelector('.zp-run').innerText.trim(),
    cursor: [...document.querySelectorAll('.cursor')].filter(el => getComputedStyle(el).display !== 'none').map(el => el.querySelector('use').getAttribute('href')),
    routines: [...document.querySelectorAll('#inbox li.g')].filter(el => getComputedStyle(el).display !== 'none').length,
    selected: document.querySelectorAll('#inbox li.g.sel').length,
    outlines: document.querySelectorAll('.drop').length,
    full: !!document.querySelector('.f-full')?.getClientRects().length,
    folderSelected: document.querySelector('.folder').classList.contains('sel'),
    overlays: document.querySelectorAll('[data-zm-overlay]').length,
    replayDisabled: document.querySelector('#replay')?.disabled,
    cls: window.cls, durationMs: window.controller?.durationMs
  }));
}
async function assertFinal(page) {
  const result = await state(page);
  assert.equal(result.frame, 5); assert.equal(result.label, 'Run zero now');
  assert.deepEqual(result.cursor, []); assert.equal(result.routines, 0);
  assert.equal(result.selected, 0); assert.equal(result.outlines, 0);
  assert.equal(result.full, true); assert.equal(result.folderSelected, true);
  assert.equal(result.overlays, 0);
}

test('B reduced motion overrides QA frames and adds no overlays', async () => {
  const { context, page } = await open('?frame=3', 1440, { reducedMotion: 'reduce' });
  try { await assertFinal(page); }
  finally { await context.close(); }
});

test('B exact hero subjects and ages stay visible and fit at 320, 390, 760 and 1440', async () => {
  for (const width of [320, 390, 760, 1440]) {
    const { context, page } = await open('?static', width);
    try {
      const result = await page.locator('#inbox li:not(.g)').evaluateAll(rows => rows.map(row => [...row.querySelectorAll('.from,.sub,.age')].map(el => {
        const range = document.createRange(); range.selectNodeContents(el);
        const text = range.getBoundingClientRect(), box = el.getBoundingClientRect();
        return { text: el.textContent, visible: !!el.getClientRects().length && getComputedStyle(el).visibility !== 'hidden', fits: text.left >= box.left && text.right <= box.right + .5 && text.top >= box.top - .5 && text.bottom <= box.bottom + .5 };
      })));
      assert.deepEqual(result.map(row => row.map(cell => cell.text)), kept);
      assert.ok(result.flat().every(cell => cell.visible && cell.fits), JSON.stringify({ width, result }));
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false);
    } finally { await context.close(); }
  }
});

test('B real button keyboard replay exists and concurrent activation cannot overlap', async () => {
  const { context, page } = await open();
  try {
    await settle(page); await assertFinal(page);
    assert.equal(await page.locator('#replay').count(), 1);
    assert.equal(await page.locator('#replay').getAttribute('type'), 'button');
    await page.locator('#replay').focus(); await page.keyboard.press('Enter');
    await page.waitForFunction(() => document.body.dataset.mode === 'play');
    assert.equal(await page.evaluate(() => Zm.play(document.body, window.story) === controller.pending), true);
    await settle(page); await assertFinal(page);
  } finally { await context.close(); }
});

test('B no-JS, static and reduced-motion pixels are identical across device widths', async () => {
  for (const width of [320, 390, 760, 1440]) {
    const disabled = await open('', width, { javaScriptEnabled: false });
    const staticPage = await open('?static', width);
    const reduced = await open('', width, { reducedMotion: 'reduce' });
    try {
      const golden = await disabled.page.screenshot({ fullPage: true });
      assert.deepEqual(await staticPage.page.screenshot({ fullPage: true }), golden);
      assert.deepEqual(await reduced.page.screenshot({ fullPage: true }), golden);
      await assertFinal(staticPage.page); await assertFinal(reduced.page);
    } finally { await Promise.all([disabled, staticPage, reduced].map(item => item.context.close())); }
  }
});

test('B six QA frames show no arrow, watch only while Working, eight outlines and truthful final', async () => {
  for (const width of [320, 390, 760, 1240, 1440]) {
    let caption;
    for (let frame = 0; frame <= 5; frame++) {
      const { context, page, errors } = await open(`?frame=${frame}`, width);
      try {
        const result = await state(page);
        const rect = await page.locator('.caption').boundingBox();
        caption ??= rect;
        assert.deepEqual(rect, caption, `caption moves at ${width}px, frame ${frame}`);
        assert.equal(result.frame, frame);
        assert.equal(result.label, frame === 0 ? '' : frame >= 2 && frame <= 4 ? 'Working…' : 'Run zero now');
        assert.deepEqual(result.cursor, width >= 760 && frame >= 2 && frame <= 4 ? ['#watch'] : []);
        assert.equal(result.outlines, frame === 4 ? 8 : 0);
        assert.equal(result.selected, frame === 3 || frame === 4 ? 8 : 0);
        if (frame === 5) await assertFinal(page);
        assert.deepEqual(errors, []);
      } finally { await context.close(); }
    }
  }
});

test('B active playback observes each selection and simultaneous drag, correct actor, empty Trash and zero CLS', async () => {
  const timings = [];
  for (const width of [320, 390, 760, 1440]) {
    const { context, page, errors } = await open('?static', width);
    try {
      const staticPixels = await page.screenshot({ fullPage: true });
      await page.addInitScript(() => {
        window.samples = []; window.violations = [];
        const observe = () => {
          const run = document.querySelector('.zp-run'); if (!run) return;
          const watches = [...document.querySelectorAll('.cursor')].filter(el => getComputedStyle(el).display !== 'none');
          const label = run.innerText.trim();
          const sample = { frame: Number(document.body.dataset.f), selected: document.querySelectorAll('#inbox li.g.sel').length, outlines: document.querySelectorAll('.drop').length };
          const folder = [...document.querySelectorAll('.folder svg')].find(el => el.getClientRects().length)?.getBoundingClientRect();
          sample.landed = sample.outlines === 8 && [...document.querySelectorAll('.drop')].every(el => { const b = el.getBoundingClientRect(); return b.left >= folder.left && b.right <= folder.right && b.top >= folder.top && b.bottom <= folder.bottom; });
          window.samples.push(sample);
          if (watches.some(el => el.querySelector('use').getAttribute('href') !== '#watch') || (watches.length && label !== 'Working…')) window.violations.push('cursor ownership');
          for (const el of document.querySelectorAll('.drop,.zr,.cursor')) {
            if (el.getAttribute('aria-hidden') !== 'true' || getComputedStyle(el).pointerEvents !== 'none') window.violations.push('interactive overlay');
            if (el.matches('.drop,.zr')) for (const key of ['left', 'top', 'width', 'height']) {
              const number = Number.parseFloat(el.style[key]); if (Number.isFinite(number) && number % 1) window.violations.push('fractional geometry');
            }
            if (el.matches('.cursor,.drop')) {
              const matrix = new DOMMatrix(getComputedStyle(el).transform); if (matrix.e % 1 || matrix.f % 1) window.violations.push('fractional cursor');
            }
          }
          const sheet = document.querySelector('.sheet'), trash = document.querySelector('.trash');
          for (const el of document.querySelectorAll('.drop,.zr')) {
            if (Number(getComputedStyle(el).zIndex) >= Number(getComputedStyle(sheet).zIndex)) window.violations.push('outline over headline');
          }
          if (sample.frame === 2 && watches.length && !window.watchStarted) {
            window.watchStarted = true;
            for (const el of watches) {
            const box = run.getBoundingClientRect(), origin = document.body.getBoundingClientRect(), matrix = new DOMMatrix(getComputedStyle(el).transform);
            if (matrix.e !== Math.round(box.left - origin.left + box.width * .5) || matrix.f !== Math.round(box.top - origin.top + box.height * .55)) window.violations.push('watch did not start on Working button');
            }
          }
          for (const el of document.querySelectorAll('.drop')) {
            const box = el.getBoundingClientRect(), bin = trash.getBoundingClientRect();
            if (box.left < bin.right && box.right > bin.left && box.top < bin.bottom && box.bottom > bin.top) window.violations.push('drag enters Trash');
          }
        };
        new MutationObserver(observe).observe(document, { childList: true, subtree: true, attributes: true });
      });
      await page.goto(base); await settle(page); await assertFinal(page);
      const playedPixels = await page.screenshot({ fullPage: true });
      if (!playedPixels.equals(staticPixels)) {
        await mkdir(resolve(here, 'evidence'), { recursive: true });
        await writeFile(resolve(here, `evidence/parity-${width}-static.png`), staticPixels);
        await writeFile(resolve(here, `evidence/parity-${width}-played.png`), playedPixels);
        await page.waitForTimeout(300);
        const late = await page.screenshot({fullPage:true});
        await writeFile(resolve(here, `evidence/parity-${width}-late.png`), late);
        console.log('PARITY_LATE', JSON.stringify({width, equalAfter300ms:late.equals(staticPixels)}));
      }
      assert.ok(playedPixels.equals(staticPixels), `played end differs from static at ${width}px, see evidence/parity-${width}-*.png`);
      const result = await page.evaluate(() => ({ width: innerWidth, durationMs: controller.durationMs, cls: window.cls, shifts: window.shifts, samples, violations }));
      assert.deepEqual([...new Set(result.violations)], []);
      for (let selected = 1; selected <= 8; selected++) assert.ok(result.samples.some(sample => sample.frame === 3 && sample.selected === selected));
      assert.ok(result.samples.some(sample => sample.frame === 4 && sample.outlines === 8));
      assert.ok(result.samples.some(sample => sample.frame === 4 && sample.landed), 'all eight outlines must really reach the folder');
      assert.ok(result.durationMs >= 3000 && result.durationMs <= 6000);
      assert.equal(result.cls, 0, JSON.stringify({width, shifts: result.shifts}));
      assert.deepEqual(errors, []);
      timings.push({ width, durationMs: result.durationMs, cls: result.cls });
    } finally { await context.close(); }
  }
  console.log('B_TIMING ' + JSON.stringify(timings));
  if (process.env.CAPTURE === '1') await writeFile(resolve(here, 'evidence/timing.json'), JSON.stringify(timings, null, 2) + '\n');
});

test('B reduced-motion, resize and synthetic visibility cancellation during the drag have no late mutations', async () => {
  for (const reason of ['reduce', 'resize', 'hidden']) {
    const { context, page } = await open();
    try {
      await page.waitForFunction(() => document.querySelectorAll('.drop').length === 8);
      if (reason === 'reduce') await page.emulateMedia({ reducedMotion: 'reduce' });
      if (reason === 'resize') await page.setViewportSize({ width: 390, height: 1000 });
      if (reason === 'hidden') await page.evaluate(() => { Object.defineProperty(document, 'hidden', { configurable: true, value: true }); document.dispatchEvent(new Event('visibilitychange')); });
      await settle(page, 'cancelled'); await assertFinal(page);
      const final = await state(page); await page.waitForTimeout(700);
      assert.deepEqual(await state(page), final);
    } finally { await context.close(); }
  }
});

test('B missing drag target settles to the final state, and forced deadline cancels safely', async () => {
  for (const query of ['?fault=drop', '?deadline=100']) {
    const { context, page } = await open(query);
    try { await settle(page, query.includes('fault') ? 'error' : 'cancelled'); await assertFinal(page); }
    finally { await context.close(); }
  }
});

test('B coarse pointer never receives the watch even in desktop QA frames', async () => {
  const { context, page } = await open('?frame=4', 1440, { isMobile: true, hasTouch: true });
  try { assert.deepEqual((await state(page)).cursor, []); }
  finally { await context.close(); }
});

test('B geometry follows changed fonts and container widths without runtime constants', async () => {
  const { context, page } = await open('?static', 1440);
  try {
    await page.addInitScript(() => {
      document.addEventListener('DOMContentLoaded', () => {
        const style = document.createElement('style');
        style.textContent = '#inbox{width:38vw!important;right:8vw!important}.sheet h1{font-family:monospace!important;font-size:45px!important}.list{font-family:serif!important}';
        document.head.appendChild(style);
      }, { once: true });
    });
    await page.goto(base); await settle(page); await assertFinal(page);
    assert.equal(await page.evaluate(() => controller.error), null);
  } finally { await context.close(); }
});

test('B captures all six frames and reduced-motion end states', { skip: process.env.CAPTURE !== '1' }, async () => {
  await mkdir(resolve(here, 'evidence'), { recursive: true });
  for (const width of [390, 1440]) {
    for (let frame = 0; frame <= 5; frame++) {
      const { context, page } = await open(`?frame=${frame}`, width);
      try { await page.screenshot({ fullPage: true, path: resolve(here, `evidence/${width}-frame-${frame}.png`) }); }
      finally { await context.close(); }
    }
    const { context, page } = await open('', width, { reducedMotion: 'reduce' });
    try { await page.screenshot({ fullPage: true, path: resolve(here, `evidence/${width}-reduced.png`) }); }
    finally { await context.close(); }
  }
  await writeFile(resolve(here, 'evidence/capture.json'), JSON.stringify({ capturedAt: new Date().toISOString(), spec: 'd0a5685', engine: await browser.version() }, null, 2) + '\n');
});
