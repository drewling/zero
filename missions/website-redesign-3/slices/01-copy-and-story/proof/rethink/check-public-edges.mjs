import fs from 'node:fs';
import crypto from 'node:crypto';
import { createRequire } from 'node:module';
import { execFileSync } from 'node:child_process';
const require = createRequire(execFileSync('npm', ['root', '-g'], { encoding: 'utf8' }).trim() + '/');
const { chromium } = require('playwright');
const out = process.argv[2];
if (!out) throw new Error('Pass an output JSON path');
if (fs.existsSync(out)) throw new Error('Do not overwrite public-edge evidence');
const sourceCommit = execFileSync('git', ['rev-parse', process.env.SOURCE_SHA || 'cdfee91'], { encoding: 'utf8' }).trim();
const outlines = process.env.OUTLINE === 'b' ? ['b'] : ['a', 'b'];
const hash = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
const checkedDestinations = [];
const browser = await chromium.launch();
const records = [];
const rec = (ok, name, observed) => records.push({ ok, name, observed });
const command = 'curl -fsSL https://zero.headless.com/install | bash';
try {
  for (const outline of outlines) {
    const ctx = await browser.newContext({ viewport: { width: 390, height: 900 } });
    const page = await ctx.newPage(), resources = [], errors = [];
    page.on('response', r => { if (r.status() >= 400) resources.push({ url: r.url(), status: r.status() }); });
    page.on('requestfailed', r => resources.push({ url: r.url(), failure: r.failure()?.errorText }));
    page.on('pageerror', e => errors.push(e.message));
    const served = await page.goto(`http://127.0.0.1:8941/page-${outline}/?static`); await page.evaluate(() => document.fonts.ready);
    const source = execFileSync('git', ['show', `${sourceCommit}:missions/website-redesign-3/slices/02-references-and-comps/proof/comps/page-${outline}/index.html`]);
    if (hash(source) !== hash(await served.body())) throw new Error('Served public page differs from requested source commit');
    rec(!resources.length && !errors.length, `${outline}: loaded assets and script status`, { resources, errors });
    const semantic = await page.evaluate(() => ({ h1: document.querySelectorAll('h1').length, main: document.querySelectorAll('main').length,
      headings: [...document.querySelectorAll('h1,h2,h3')].map(e => ({ level: e.tagName, text: e.textContent.trim() })),
      copyName: document.querySelector('#copy')?.textContent.trim(), exposedPolicy: document.querySelector('.editor') ? !document.querySelector('.editor').closest('[aria-hidden="true"]') : null }));
    rec(semantic.h1 === 1 && semantic.main === 1 && semantic.copyName === 'Copy command' && semantic.exposedPolicy !== false, `${outline}: semantics and policy exposure`, semantic);
    const links = await page.locator('a[href]').evaluateAll(els => els.map(e => ({ text: e.textContent.trim(), href: e.getAttribute('href') })));
    for (const link of links.filter(l => l.href.startsWith('#') && l.href !== '#')) {
      const target = page.locator(link.href); rec(await target.count() === 1, `${outline}: target ${link.href}`, link.text);
    }
    for (const route of [...new Set(links.map(l => l.href).filter(h => h.startsWith('/')))]) {
      const response = await ctx.request.get(`http://127.0.0.1:8941${route}`);
      rec(response.ok(), `${outline}: proof-server linked route ${route}`, response.status());
    }
    if (process.env.OUTLINE === 'b') {
      rec(!links.some(l => l.href.startsWith('/')), `${outline}: no proof-only root-relative destinations`, links.filter(l => l.href.startsWith('/')));
      for (const url of ['https://zero.headless.com/privacy.html', 'https://zero.headless.com/terms.html', 'https://zero.headless.com/install.sh']) {
        const linked = links.some(l => l.href === url);
        const response = await ctx.request.get(url, { timeout: 30000 });
        const observed = { requested: url, final: response.url(), status: response.status(), contentType: response.headers()['content-type'], linked };
        checkedDestinations.push(observed);
        rec(linked && response.ok(), `${outline}: canonical readonly destination ${url}`, observed);
      }
    }
    const focus = await page.evaluate(() => {
      const controls = [...document.querySelectorAll('a[href],button:not([disabled])')].filter(e => e.getClientRects().length && getComputedStyle(e).visibility !== 'hidden');
      return controls.map(e => { e.focus(); const s = getComputedStyle(e), r = e.getBoundingClientRect(); return { text: e.textContent.trim(), outline: s.outlineStyle, width: s.outlineWidth, widthPx: r.width }; });
    });
    rec(focus.every(e => e.outline !== 'none' && parseFloat(e.width) > 0 && e.widthPx > 0), `${outline}: every real control has visible focus outline`, focus);
    for (const mode of ['success', 'denied', 'unavailable']) {
      const fault = await browser.newContext({ viewport: { width: 390, height: 900 } });
      await fault.addInitScript(mode => {
        window.__written = null;
        Object.defineProperty(navigator, 'clipboard', { configurable: true, value: mode === 'unavailable' ? undefined : { writeText: async text => {
          if (mode === 'denied') throw new DOMException('Denied', 'NotAllowedError'); window.__written = text;
        } } });
      }, mode);
      const pg = await fault.newPage(); await pg.goto(`http://127.0.0.1:8941/page-${outline}/?static`);
      const copy = pg.locator('#copy');
      if (mode !== 'unavailable') { await copy.focus(); await pg.keyboard.press(mode === 'success' ? 'Enter' : 'Space'); await pg.waitForTimeout(80); }
      const result = await pg.evaluate(() => ({ written: window.__written, selection: getSelection().toString(), focused: document.activeElement?.id,
        status: [...document.querySelectorAll('[role="status"],[aria-live="polite"]')].map(e => e.textContent.trim()).join(' '),
        hidden: !document.querySelector('#copy') || getComputedStyle(document.querySelector('#copy')).display === 'none' || document.querySelector('#copy').hidden,
        command: document.querySelector('#term code')?.textContent }));
      const ok = mode === 'success' ? result.written === command && /Copied/i.test(result.status) && result.focused === 'copy' :
        mode === 'denied' ? result.selection === command && /Copy manually: press Command-C\./.test(result.status) && result.focused === 'copy' :
        result.hidden && result.command === command;
      rec(ok, `${outline}: clipboard ${mode} keyboard action and accessible feedback`, result);
      await fault.close();
    }
    await ctx.close();
  }
} finally { await browser.close(); }
fs.writeFileSync(out, JSON.stringify({ sourceCommit, checkedAt: new Date().toISOString(), checkedDestinations, scope: 'Public local comp interfaces and linked canonical URLs, readonly HTTP only. Clipboard fault injection tests environmental success/denial/unavailability without installer execution.', records,
  pass: records.filter(r => r.ok).length, fail: records.filter(r => !r.ok).length }, null, 2) + '\n');
for (const row of records) console.log(`${row.ok ? 'PASS' : 'FAIL'} ${row.name}: ${JSON.stringify(row.observed)}`);
console.log(`${records.filter(r => r.ok).length} PASS, ${records.filter(r => !r.ok).length} FAIL`);
process.exitCode = records.some(r => !r.ok) ? 1 : 0;
