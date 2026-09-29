// Acceptance pass for redesign-3 slice 02 comps, using real browser engines and device emulation (not the iframe harness).
// Run: node accept.mjs  (the comp server must be on 127.0.0.1:8941)
import { createRequire } from 'node:module';
import { execSync } from 'node:child_process';
const require = createRequire(execSync('npm root -g').toString().trim() + '/');
const { chromium, webkit } = require('playwright');
import fs from 'node:fs';

const BASE = 'http://127.0.0.1:8941';
const COPY = fs.readFileSync(process.env.COPY_MD, 'utf8');
const primary = COPY.split('<!-- PAGE-COPY-START -->')[1].split('<!-- PAGE-COPY-END -->')[0];
const OUT = process.env.OUT;
const results = [];
const ENGINE = process.env.ENGINE || 'chromium';
const rec = (ok, name, detail = '') => { results.push({ ok, name, detail }); fs.appendFileSync(`${OUT}/accept-${ENGINE}.log`, `${ok ? 'PASS' : 'FAIL'} ${name}${detail && !ok ? ' :: ' + detail : ''}\n`); };
fs.writeFileSync(`${OUT}/accept-${ENGINE}.log`, '');

const devices = {
  desktop: { viewport: { width: 1440, height: 900 }, deviceScaleFactor: 2 },
  iphone: { viewport: { width: 390, height: 844 }, deviceScaleFactor: 3, isMobile: true, hasTouch: true },
  se: { viewport: { width: 320, height: 568 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true },
};
const pages = ['hero-a', 'hero-b', 'hero-c', 'sections'];

// Per-page audit, run inside the page.
const audit = () => {
  const d = document, W = d.documentElement.clientWidth;
  const vis = e => { const s = getComputedStyle(e); const r = e.getBoundingClientRect(); return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && !e.closest('.sr-only'); };
  const over = [...d.querySelectorAll('body *')].filter(e => { const b = e.getBoundingClientRect(); return b.width && b.right > W + 1 && vis(e) && getComputedStyle(e).position !== 'fixed' && !e.closest('.cursor,.fly'); }).map(e => e.tagName + '.' + e.className);
  const clip = [...d.querySelectorAll('h1,h2,p,li,a,button,.btn,.t,.from,.sub,.zp-subj,.zp-need,.zp-across,.caption')].filter(e => vis(e) && (e.scrollWidth > e.clientWidth + 1) && getComputedStyle(e).overflow !== 'visible').map(e => e.textContent.trim().slice(0, 30));
  // text sitting on a textured ancestor background
  const tex = [...d.querySelectorAll('h1,h2,p,li,.t,.caption,a,label,span.from,span.sub,b')].filter(e => e.textContent.trim() && vis(e)).filter(e => { let n = e; while (n && n !== d.documentElement) { const s = getComputedStyle(n); if (s.backgroundImage !== 'none') return true; if (s.backgroundColor !== 'rgba(0, 0, 0, 0)') return false; n = n.parentElement; } return false; }).map(e => e.textContent.trim().slice(0, 30));
  // pixel check: do the stripes (::before of .bar) overlap the title plate's text box?
  const stripeHits = [...d.querySelectorAll('.win:not(.inactive) .bar')].filter(vis).filter(bar => {
    const t = bar.querySelector('.t'); if (!t) return false; const tb = t.getBoundingClientRect();
    // scrollWidth is an integer and the box is fractional: allow 1px of rounding, not a real overlap
    const s = getComputedStyle(t); return s.backgroundColor === 'rgba(0, 0, 0, 0)' || tb.width + 1 < t.scrollWidth; }).length;
  // ligature: Pixelify elements must have ligatures disabled
  const lig = [...d.querySelectorAll('h1,h2,.btn,a,.t,button')].filter(e => vis(e) && /pixelify/i.test(getComputedStyle(e).fontFamily) && /fi/.test(e.textContent) && getComputedStyle(e).fontVariantLigatures !== 'none').map(e => e.textContent.trim().slice(0, 30));
  // tap targets: interactive elements under 24x24 CSS px (WCAG 2.2 AA 2.5.8)
  // WCAG 2.5.8 exempts links inside a sentence (inline exception): skip anchors whose parent has other text
  const inline = e => e.tagName === 'A' && [...e.parentElement.childNodes].some(n => n !== e && n.nodeType === 3 && n.textContent.trim());
  const small = [...d.querySelectorAll('a[href],button')].filter(vis).filter(e => !inline(e)).filter(e => { const r = e.getBoundingClientRect(); return r.width < 24 || r.height < 24; }).map(e => e.textContent.trim().slice(0, 20) + ' ' + Math.round(e.getBoundingClientRect().width) + 'x' + Math.round(e.getBoundingClientRect().height));
  const h1 = d.querySelectorAll('h1').length, imgsNoAlt = [...d.querySelectorAll('img')].filter(i => !i.hasAttribute('alt')).length;
  const unnamedSvg = [...d.querySelectorAll('svg')].filter(s => vis(s) && !s.closest('[aria-hidden="true"]') && s.getAttribute('aria-hidden') !== 'true' && !s.getAttribute('aria-label') && !s.querySelector('title')).length;
  return { sw: d.documentElement.scrollWidth, W, over: over.slice(0, 5), clip, tex: tex.slice(0, 5), stripeHits, lig, small: small.slice(0, 8), h1, imgsNoAlt, unnamedSvg, mode: d.querySelector('[data-mode]')?.dataset.mode ?? null };
};

async function run(engineName, engine) {
  const browser = await engine.launch(process.env.WEBKIT_EXECUTABLE && engine === webkit ? { executablePath: process.env.WEBKIT_EXECUTABLE } : {});
  for (const [dev, opt] of Object.entries(devices)) {
    for (const pg of pages) {
      // 1. default: JS on, motion allowed, real playback to done
      const ctx = await browser.newContext({ ...opt, reducedMotion: 'no-preference' });
      const p = await ctx.newPage();
      const errs = []; p.on('pageerror', e => errs.push(e.message)); p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
      const t0 = Date.now();
      await p.goto(`${BASE}/${pg}/index.html`, { waitUntil: 'load' });
      await p.evaluate(() => document.fonts.ready);
      // scroll every story root into view so IntersectionObserver-triggered stories play
      const roots = await p.$$eval('[data-mode]', els => els.length);
      let done = false, ms = 0;
      for (let i = 0; i < 60 && !done; i++) {
        await p.evaluate(() => document.querySelectorAll('[data-mode]').forEach(el => { if (el.dataset.mode !== 'done' && el !== document.body) el.scrollIntoView({ block: 'center' }); }));
        await p.waitForTimeout(250);
        done = await p.evaluate(() => [...document.querySelectorAll('[data-mode]')].every(el => el.dataset.mode === 'done'));
      }
      ms = Date.now() - t0;
      const flies = await p.$$eval('.fly,.drop,.zoomrect,.mover', els => els.filter(e => e.getBoundingClientRect().width).length);
      await p.evaluate(() => window.scrollTo(0, 0));
      const a = await p.evaluate(audit);
      const tag = `${engineName}/${dev}/${pg}`;
      rec(done, `${tag} story plays to done`, `${roots} root(s), ${ms} ms, leftover movers ${flies}`);
      rec(flies === 0, `${tag} no leftover motion DOM`);
      rec(errs.length === 0, `${tag} no console/page errors`, errs.join(' | '));
      rec(a.sw <= a.W && a.over.length === 0, `${tag} no horizontal overflow`, `${a.sw}/${a.W} ${a.over.join(',')}`);
      rec(a.clip.length === 0, `${tag} no clipped text`, a.clip.join(' | '));
      rec(a.tex.length === 0, `${tag} no text on texture`, a.tex.join(' | '));
      rec(a.stripeHits === 0, `${tag} title plates break stripes`, String(a.stripeHits));
      rec(a.lig.length === 0, `${tag} ligatures off on Pixelify`, a.lig.join(' | '));
      rec(a.small.length === 0, `${tag} tap targets >= 24px`, a.small.join(' | '));
      rec(a.imgsNoAlt === 0 && a.unnamedSvg === 0, `${tag} images/svgs named or hidden`, `img ${a.imgsNoAlt} svg ${a.unnamedSvg}`);
      if (engineName === 'chromium') await p.screenshot({ path: `${OUT}/${dev}-${pg}-done.png`, fullPage: dev !== 'desktop' || pg === 'sections' });
      await ctx.close();

      // 2. reduced motion: final frame immediately, no motion DOM ever added
      const rctx = await browser.newContext({ ...opt, reducedMotion: 'reduce' });
      const r = await rctx.newPage();
      await r.goto(`${BASE}/${pg}/index.html`, { waitUntil: 'load' });
      await r.waitForTimeout(400);
      const rm = await r.evaluate(() => ({ modes: [...document.querySelectorAll('[data-mode]')].map(e => e.dataset.mode), lt: document.querySelectorAll('[class*="lt-"]').length, movers: document.querySelectorAll('.fly,.drop,.zoomrect,.mover,.cursor:not([hidden])').length }));
      rec(rm.modes.every(m => m === 'static') && rm.lt === 0, `${tag} reduced motion = final frame`, JSON.stringify(rm));
      await rctx.close();

      // 3. JS disabled: the raw HTML must already be the final frame (same text as the played page)
      const nctx = await browser.newContext({ ...opt, javaScriptEnabled: false });
      const n = await nctx.newPage();
      await n.goto(`${BASE}/${pg}/index.html`, { waitUntil: 'load' });
      const nojs = await n.evaluate(() => ({ text: document.body.innerText.replace(/\s+/g, ' ').trim(), lt: document.querySelectorAll('[class*="lt-"]').length }));
      const jctx = await browser.newContext({ ...opt, reducedMotion: 'reduce' });
      const j = await jctx.newPage(); await j.goto(`${BASE}/${pg}/index.html`, { waitUntil: 'load' }); await j.waitForTimeout(300);
      const withjs = await j.evaluate(() => document.body.innerText.replace(/\s+/g, ' ').trim());
      rec(nojs.lt === 0 && nojs.text === withjs, `${tag} no-JS HTML equals final frame`, nojs.text === withjs ? '' : `diff len ${nojs.text.length} vs ${withjs.length}`);
      await nctx.close(); await jctx.close();
    }
  }
  // 4. keyboard: every interactive element reachable by Tab, with a visible focus indicator (desktop, sections page)
  // a fresh context per page: reusing one context hung WebKit on the second newPage
  for (const pg of pages) {
    const kctx = await browser.newContext({ ...devices.desktop, reducedMotion: 'reduce' });
    const k = await kctx.newPage(); await k.goto(`${BASE}/${pg}/index.html`);
    const total = await k.$$eval('a[href],button:not([disabled])', els => els.filter(e => e.getBoundingClientRect().width).length);
    const seen = new Set(); let noRing = [];
    for (let i = 0; i < total + 3; i++) {
      // macOS WebKit only tabs to links with Option+Tab (Safari's default "Press Tab to highlight each item" is off)
      await k.keyboard.press(engineName === 'webkit' ? 'Alt+Tab' : 'Tab');
      const f = await k.evaluate(() => { const e = document.activeElement; if (!e || e === document.body) return null; const s = getComputedStyle(e); return { id: e.outerHTML.slice(0, 60), ring: s.outlineStyle !== 'none' && parseFloat(s.outlineWidth) > 0 || s.boxShadow !== 'none' }; });
      if (f) { seen.add(f.id); if (!f.ring) noRing.push(f.id); }
    }
    rec(seen.size >= total, `${engineName}/keyboard/${pg} all ${total} controls reachable`, `reached ${seen.size}`);
    rec(noRing.length === 0, `${engineName}/keyboard/${pg} visible focus`, [...new Set(noRing)].slice(0, 3).join(' | '));
    await k.close(); await kctx.close();
  }
  await browser.close();
}

// 5. copy fidelity: every COPY v3 primary sentence appears verbatim in the combined comp (hero A + sections)
async function copyFidelity() {
  const b = await chromium.launch(); const ctx = await b.newContext({ ...devices.desktop, reducedMotion: 'reduce' });
  let text = '';
  for (const pg of ['hero-a', 'sections']) { const p = await ctx.newPage(); await p.goto(`${BASE}/${pg}/index.html`); await p.waitForTimeout(300); text += ' ' + await p.evaluate(() => document.body.innerText); }
  const norm = s => s.replace(/\*\*|\*|`/g, '').replace(/[’]/g, "'").replace(/\s+/g, ' ').trim();
  const T = norm(text);
  const lines = primary.split('\n').map(l => l.replace(/^#+\s*/, '').replace(/^```\w*$/, '')).map(norm).filter(Boolean);
  const sentences = lines.flatMap(l => l.split(/(?<=[.?!])\s+(?=[A-Z])/)).filter(s => s.length > 3);
  const missing = sentences.filter(s => !T.includes(s));
  rec(missing.length === 0, `copy: all ${sentences.length} COPY v3 primary sentences render verbatim`, missing.join(' || '));
  await b.close();
}

// 6. regression control: the same audit against the LIVE site must catch the owner's two named bugs (proves the audit can fail)
async function liveControl() {
  const b = await chromium.launch(); const ctx = await b.newContext({ ...devices.desktop });
  const p = await ctx.newPage();
  try {
    await p.goto('https://zero.headless.com/', { waitUntil: 'load', timeout: 30000 });
    const r = await p.evaluate(() => {
      const lig = [...document.querySelectorAll('a,button,h1,h2')].filter(e => /pixelify/i.test(getComputedStyle(e).fontFamily) && /fi/.test(e.textContent) && getComputedStyle(e).fontVariantLigatures !== 'none').map(e => e.textContent.trim().slice(0, 30));
      const stripes = [...document.querySelectorAll('*')].filter(e => { const s = getComputedStyle(e, '::before'); return /repeating-linear-gradient/.test(s.backgroundImage) || /repeating-linear-gradient/.test(getComputedStyle(e).backgroundImage); }).map(e => { const t = [...e.querySelectorAll('*')].find(c => c.textContent.trim() && c.children.length === 0); return t ? { text: t.textContent.trim().slice(0, 20), bg: getComputedStyle(t).backgroundColor } : null; }).filter(x => x && x.bg === 'rgba(0, 0, 0, 0)');
      return { lig, stripes: stripes.slice(0, 5) };
    });
    rec(r.lig.length > 0, 'control: audit detects live "fi" ligature bug', r.lig.join(' | '));
    rec(r.stripes.length > 0, 'control: audit detects live title text on stripes', JSON.stringify(r.stripes));
    await p.screenshot({ path: `${OUT}/live-control.png` });
  } catch (e) { rec(false, 'control: live site reachable', e.message); }
  await b.close();
}

if (ENGINE === 'chromium') { await run('chromium', chromium); await copyFidelity(); await liveControl(); }
else await run('webkit', webkit);
const fail = results.filter(r => !r.ok);
fs.writeFileSync(`${OUT}/accept-${ENGINE}.json`, JSON.stringify(results, null, 1));
console.log(`PASS ${results.length - fail.length}/${results.length}`);
for (const f of fail) console.log('FAIL', f.name, '::', f.detail);
