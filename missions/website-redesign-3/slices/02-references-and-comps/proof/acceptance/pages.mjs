// Acceptance pass for the whole-page comps (page-a, page-b): real engines, real emulation, real captures.
// Run: COPY_MD=<SECTION-COPY.md> OUT=<dir> ENGINE=chromium|webkit node pages.mjs   (comp server on 127.0.0.1:8941)
// Checks: horizontal overflow and text escaping its section at 320-2560; no-JS and reduced-motion end states
// equal the ?static final frame; scroll-triggered beats play to done; layout shift while they play (Chromium);
// an anchor jump leaves the target section final; keyboard reaches only real links and the Copy button, in order;
// rendered words equal the copywriter's Draft3 blocks (multiset) and the hero equals approved hero B.
import { createRequire } from 'node:module';
import { execSync } from 'node:child_process';
import fs from 'node:fs';
const require = createRequire(execSync('npm root -g').toString().trim() + '/');
const { chromium, webkit } = require('playwright');

const BASE = 'http://127.0.0.1:8941', OUT = process.env.OUT, ENGINE = process.env.ENGINE || 'chromium';
const COPY = fs.readFileSync(process.env.COPY_MD, 'utf8');
const block = n => COPY.split(`<!-- ${n}-START -->`)[1].split(`<!-- ${n}-END -->`)[0];
const visible = t => t.replace(/\[([^\]]+)\]\([^)]+\)/g, '$1').replace(/```sh|```/g, '').replace(/\*\*/g, '').replace(/^#+ /gm, '');
const words = t => (visible(t).replace(/’/g, "'").match(/[\p{L}\p{N}]+(?:['.-][\p{L}\p{N}]+)*/gu) ?? []);
const bag = ws => ws.reduce((m, w) => (m[w] = (m[w] || 0) + 1, m), {});
const diff = (a, b) => { const out = []; for (const k of new Set([...Object.keys(a), ...Object.keys(b)])) if ((a[k] || 0) !== (b[k] || 0)) out.push(`${k}:${a[k] || 0}/${b[k] || 0}`); return out; };
const expected = { 'page-a': [...words(block('COPY-A')), ...words(block('OBJECT-COPY'))],
                   'page-b': [...words(block('COPY-B')), ...words(block('OBJECT-COPY')), ...words(block('RULES-B-COPY'))] };

const log = `${OUT}/pages-${ENGINE}.log`; fs.writeFileSync(log, '');
let pass = 0, fail = 0;
const rec = (ok, name, detail = '') => { ok ? pass++ : fail++; fs.appendFileSync(log, `${ok ? 'PASS' : 'FAIL'} ${name}${detail ? ' :: ' + detail : ''}\n`); };
const engine = ENGINE === 'webkit' ? webkit : chromium;
// WEBKIT_EXECUTABLE: the installed WebKit build when it differs from this Playwright's pinned revision
const b = await engine.launch(ENGINE === 'webkit' && process.env.WEBKIT_EXECUTABLE ? { executablePath: process.env.WEBKIT_EXECUTABLE } : {});
const widths = [320, 390, 768, 1440, 1920, 2560];
const pages = ['page-a', 'page-b'];

// the final-frame fingerprint: what a visitor must see at the end, whatever path got them there
const endState = () => {
  const d = document, v = e => e && getComputedStyle(e).visibility !== 'hidden' && e.getClientRects().length > 0;
  const q = s => [...d.querySelectorAll(s)];
  return {
    lt: q('[class*="lt-"]').filter(e => /\blt-\d/.test(e.className) && !e.matches('body')).length,
    stepping: q('.stepping').length,
    undoRows: q('.urows li').filter(v).length,
    balloon: v(d.querySelector('.balloon')),
    ledgerRows: q('.info .row').filter(v).length,
    info: v(d.querySelector('.info')),
    rulesLines: q('.editor .ln').filter(v).length,
    rulesTab: d.querySelector('#rules-win .tabs .on')?.textContent || null,
    cmd: d.querySelector('#term code')?.textContent,
    zr: q('.zr,.fly,.drop').length,
  };
};
const sectionText = () => {
  // every text node outside the hero, menu bar, proof label and screen-reader-only text, joined by spaces
  // (textContent would glue adjacent elements together, e.g. "Sep" + "8")
  const skip = n => n.parentElement.closest('.sr-only,.draft-flag,svg,script,style,header,#hero');
  const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT); const out = [];
  for (let n; (n = w.nextNode());) if (!skip(n)) out.push(n.nodeValue);
  return out.join(' ');
};
const heroText = () => { const h = document.querySelector('#hero').cloneNode(true); h.querySelectorAll('svg').forEach(e => e.remove()); return h.textContent.replace(/\s+/g, ' ').trim(); };
const layout = () => {
  const d = document, W = d.documentElement.clientWidth;
  const vis = e => { const r = e.getBoundingClientRect(); return r.width > 0 && r.height > 0 && getComputedStyle(e).visibility !== 'hidden' && !e.closest('.sr-only'); };
  const over = [...d.querySelectorAll('body *')].filter(e => vis(e) && e.getBoundingClientRect().right > W + 1 && getComputedStyle(e).position !== 'fixed' && !e.closest('.cursor')).map(e => e.tagName + '.' + e.className).slice(0, 5);
  const escape = [...d.querySelectorAll('main section h2, main section p, main section dd, main section dt, main section li, .editor .ln, #term code')].filter(vis).filter(e => {
    const s = e.closest('section').getBoundingClientRect(), r = e.getBoundingClientRect();
    return r.left < s.left - 1 || r.right > s.right + 1 || r.top < s.top - 1 || r.bottom > s.bottom + 1; }).map(e => e.textContent.trim().slice(0, 30));
  const clip = [...d.querySelectorAll('main section h2, main section p, dd, dt, .us, .uf, .bwhen span, .tabs span, .btn, .editor pre')].filter(vis).filter(e => e.scrollWidth > e.clientWidth + 1 && getComputedStyle(e).overflow !== 'visible').map(e => e.textContent.trim().slice(0, 30));
  const minBody = Math.min(...[...d.querySelectorAll('main section .txt p, dd')].filter(vis).map(e => parseFloat(getComputedStyle(e).fontSize)));
  const measure = Math.max(...[...d.querySelectorAll('main section .txt p, dd')].filter(vis).map(e => e.getBoundingClientRect().width / parseFloat(getComputedStyle(e).fontSize)));
  return { hscroll: d.documentElement.scrollWidth - W, over, escape, clip, minBody, measure: +measure.toFixed(1) };
};

// hero B's own text, for the verbatim check
{ const ctx = await b.newContext({ viewport: { width: 1440, height: 900 } }); const pg = await ctx.newPage();
  await pg.goto(`${BASE}/hero-b/?static`); var HERO = await pg.evaluate(heroText); await ctx.close(); }

for (const p of pages) {
  // 1 · layout at every width, final frame
  for (const w of widths) {
    const ctx = await b.newContext({ viewport: { width: w, height: 900 } }); const pg = await ctx.newPage(); const errs = [];
    pg.on('pageerror', e => errs.push(e.message));
    await pg.goto(`${BASE}/${p}/?static`); await pg.evaluate(() => document.fonts.ready); await pg.waitForTimeout(150);
    const L = await pg.evaluate(layout);
    rec(L.hscroll <= 0 && !L.over.length, `${p} ${w} no horizontal overflow`, L.over.join(' '));
    rec(!L.escape.length, `${p} ${w} every text stays inside its section`, L.escape.join(' | '));
    rec(!L.clip.length, `${p} ${w} no clipped text`, L.clip.join(' | '));
    rec(L.minBody >= 16, `${p} ${w} body text >= 16px`, `min ${L.minBody}`);
    rec(L.measure <= 40, `${p} ${w} prose measure <= 40em (~75ch)`, `max ${L.measure}em`);
    rec(!errs.length, `${p} ${w} no page errors`, errs.join(' | '));
    if (w === 1440) {
      const got = bag(words(await pg.evaluate(sectionText))), want = bag(expected[p]);
      const dd = diff(got, want);
      rec(!dd.length, `${p} rendered section words == Draft3 blocks (${expected[p].length} words)`, dd.join(' '));
      rec((await pg.evaluate(heroText)) === HERO, `${p} hero text == approved hero B`);
    }
    await ctx.close();
  }

  const FINAL = await (async () => { const ctx = await b.newContext({ viewport: { width: 1440, height: 900 } }); const pg = await ctx.newPage();
    await pg.goto(`${BASE}/${p}/?static`); const s = await pg.evaluate(endState); await ctx.close(); return s; })();
  const same = (s, name) => { const d = Object.keys(FINAL).filter(k => JSON.stringify(FINAL[k]) !== JSON.stringify(s[k])).map(k => `${k}=${JSON.stringify(s[k])} want ${JSON.stringify(FINAL[k])}`);
    rec(!d.length, name, d.join(' ')); };
  rec(FINAL.lt === 0 && FINAL.stepping === 0 && FINAL.undoRows === 5 && FINAL.balloon && FINAL.ledgerRows === 5 && FINAL.cmd === 'curl -fsSL https://zero.headless.com/install | bash'
      && (p === 'page-a' || (FINAL.rulesLines === 14 && FINAL.rulesTab === 'Settings')), `${p} ?static is the complete final frame`, JSON.stringify(FINAL));

  for (const w of [390, 1440]) {
    // 2 · no JS
    { const ctx = await b.newContext({ viewport: { width: w, height: 900 }, javaScriptEnabled: false }); const pg = await ctx.newPage();
      await pg.goto(`${BASE}/${p}/`); await pg.waitForTimeout(200);
      const s = await pg.evaluate(endState); same(s, `${p} ${w} no-JS == final frame`);
      await pg.screenshot({ path: `${OUT}/shots/${p}-${w}-nojs.png`, fullPage: true }); await ctx.close(); }
    // 3 · reduced motion, scrolled through
    { const ctx = await b.newContext({ viewport: { width: w, height: 900 }, reducedMotion: 'reduce' }); const pg = await ctx.newPage();
      await pg.goto(`${BASE}/${p}/`); await pg.waitForTimeout(300);
      for (let y = 0; y < 7000; y += 450) { await pg.evaluate(y => scrollTo(0, y), y); await pg.waitForTimeout(40); }
      const s = await pg.evaluate(endState); same(s, `${p} ${w} reduced-motion == final frame`);
      const modes = await pg.evaluate(() => [...document.querySelectorAll('[data-mode]')].map(e => e.dataset.mode));
      rec(modes.every(m => m === 'static'), `${p} ${w} reduced-motion: every story static, nothing played`, modes.join(','));
      await pg.screenshot({ path: `${OUT}/shots/${p}-${w}-reduced.png`, fullPage: true }); await ctx.close(); }
    // 4 · motion on: scroll like a reader, every beat plays to done, measure layout shift
    // python http.server (the proof server) sometimes drops a request under the harness's load. A dropped script is
    // a server fault, not a page fault: that attempt is logged as RETRY and run once more in a fresh context.
    for (let attempt = 1; attempt <= 2; attempt++) {
    { const ctx = await b.newContext({ viewport: { width: w, height: 900 } }); const pg = await ctx.newPage(); const errs = [], dropped = [];
      pg.on('pageerror', e => errs.push(e.message)); pg.on('requestfailed', r => dropped.push(r.url()));
      if (ENGINE === 'chromium') await pg.addInitScript(() => { window.__cls = []; new PerformanceObserver(l => { for (const e of l.getEntries()) if (!e.hadRecentInput)
        window.__cls.push({ v: e.value, t: Math.round(e.startTime), src: (e.sources || []).map(s => { const n = s.node && (s.node.nodeType === 1 ? s.node : s.node.parentElement);
          return n ? (n.closest('header') ? 'menubar' : n.closest('section')?.id || n.className || n.nodeName) : '?'; }).join('+') }); }).observe({ type: 'layout-shift', buffered: true }); });
      await pg.goto(`${BASE}/${p}/`); await pg.waitForTimeout(4200); // hero B plays on load
      if (dropped.length && attempt === 1) { fs.appendFileSync(log, `RETRY ${p} ${w} playback: server dropped ${dropped.join(' ')}\n`); await ctx.close(); continue; }
      errs.push(...dropped.map(u => 'request failed ' + u));
      const H = await pg.evaluate(() => document.documentElement.scrollHeight);
      const seenArmed = new Set();
      for (let y = 0; y <= H; y += 200) {
        await pg.evaluate(y => scrollTo(0, y), y); await pg.waitForTimeout(260);
        (await pg.evaluate(() => [...document.querySelectorAll('[data-mode]')].filter(e => e.dataset.mode === 'armed' || e.dataset.mode === 'play').map(e => e.id || e.className.split(' ')[1]))).forEach(x => seenArmed.add(x));
      }
      await pg.waitForTimeout(2500);
      const modes = await pg.evaluate(() => Object.fromEntries([...document.querySelectorAll('[data-mode]')].map(e => [e.id || e.className.split(' ').slice(0, 2).join('.'), e.dataset.mode])));
      const stories = Object.entries(modes).filter(([k]) => k !== '');
      rec(stories.length >= (p === 'page-a' ? 4 : 5) && stories.every(([, m]) => m === 'done'), `${p} ${w} scrolling: every beat played to done`, JSON.stringify(modes));
      rec(seenArmed.size >= (p === 'page-a' ? 3 : 4), `${p} ${w} section beats were armed before playing (not snapped from final)`, [...seenArmed].join(','));
      same(await pg.evaluate(endState), `${p} ${w} after playback == final frame`);
      rec(!errs.length, `${p} ${w} playback without page errors`, errs.join(' | '));
      if (ENGINE === 'chromium') {
        const shifts = await pg.evaluate(() => window.__cls);
        // hero B (approved, owned by slice 04) is reported, not judged here: its drag outlines and 12-to-4 collapse
        const sections = shifts.filter(s => s.src.split('+').some(x => x !== 'hero' && x !== 'drop'));
        const total = shifts.reduce((a, s) => a + s.v, 0), sec = sections.reduce((a, s) => a + s.v, 0);
        rec(sec < 0.001, `${p} ${w} section beats cause no layout shift`, `sections ${sec.toFixed(4)} ${JSON.stringify(sections).slice(0, 300)}`);
        fs.appendFileSync(log, `INFO ${p} ${w} total CLS incl. hero ${total.toFixed(4)} ${JSON.stringify(shifts.map(s => [s.v.toFixed(4), s.src])).slice(0, 300)}\n`);
      }
      await ctx.close(); }
    break; }
  }

  // 5 · anchor jump (the hero's Install CTA): the ledger is on screen at first sight, so it stays final and never blanks
  { const ctx = await b.newContext({ viewport: { width: 1440, height: 900 } }); const pg = await ctx.newPage();
    await pg.goto(`${BASE}/${p}/`); await pg.waitForTimeout(300);
    await pg.click('.acts .btn.default'); await pg.waitForTimeout(900);
    const r = await pg.evaluate(() => ({ mode: document.querySelector('.ledger').dataset.mode || '', rows: [...document.querySelectorAll('.info .row')].filter(e => getComputedStyle(e).visibility !== 'hidden').length,
      top: Math.round(document.querySelector('#install').getBoundingClientRect().top) }));
    rec(r.rows === 5 && r.mode !== 'play' && r.mode !== 'armed' && Math.abs(r.top) < 2, `${p} Install CTA lands on the ledger, which stays readable`, JSON.stringify(r));
    await ctx.close(); }

  // 6 · keyboard: only real links and the Copy button take focus; illustration controls never do
  { const ctx = await b.newContext({ viewport: { width: 1440, height: 900 } }); const pg = await ctx.newPage();
    await pg.goto(`${BASE}/${p}/?static`);
    const want = await pg.evaluate(() => [...document.querySelectorAll('a[href], button')].filter(e => e.getClientRects().length).map(e => e.textContent.trim()));
    const got = [];
    for (let i = 0; i < want.length + 2; i++) { await pg.keyboard.press(ENGINE === 'webkit' ? 'Alt+Tab' : 'Tab');
      const t = await pg.evaluate(() => { const a = document.activeElement; return a && a !== document.body ? (a.textContent.trim() || a.tagName) + (a.closest('figure') ? ' [in illustration]' : '') : null; });
      if (t === null || got.includes(t) && got[0] === t) break; got.push(t); }
    rec(JSON.stringify(got.slice(0, want.length)) === JSON.stringify(want) && !got.some(t => /illustration/.test(t)), `${p} keyboard order = document order, ${want.length} stops, none in illustrations`, got.join(' > '));
    const ring = await pg.evaluate(() => { const c = document.getElementById('copy'); c.focus(); const s = getComputedStyle(c); return s.outlineStyle + ' ' + s.outlineWidth; });
    rec(/solid 3px/.test(ring), `${p} Copy command has a visible focus ring`, ring);
    // the Rules policy is real text in the accessibility tree (not an aria-hidden picture)
    const ax = await pg.evaluate(() => { const pre = document.querySelector('.editor pre'); return pre ? !pre.closest('[aria-hidden="true"]') : null; });
    if (p === 'page-b') rec(ax === true, `${p} Rules policy text is exposed to assistive tech`);
    await ctx.close(); }
}
await b.close();
fs.appendFileSync(log, `\n${pass} PASS, ${fail} FAIL (${ENGINE})\n`);
console.log(`${ENGINE}: ${pass} PASS, ${fail} FAIL`);
