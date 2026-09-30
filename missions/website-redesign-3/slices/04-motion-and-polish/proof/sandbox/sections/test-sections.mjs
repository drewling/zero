import test from 'node:test';
import assert from 'node:assert/strict';
import { createServer } from 'node:http';
import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve, dirname, extname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';
const here = dirname(fileURLToPath(import.meta.url));
const sandbox = resolve(here, '..');
const require = createRequire(`${process.env.HOME}/.nvm/versions/node/v22.16.0/lib/node_modules/playwright/package.json`);
const { chromium, webkit } = require('playwright');
const engine = process.env.ENGINE === 'webkit' ? webkit : chromium;
const roots = ['#install', '#rules-win', '#undo-win', '#term'];
const command = 'curl -fsSL https://zero.headless.com/install | bash';
let browser, server, base;
test.before(async () => {
  await mkdir(resolve(here, 'evidence'), { recursive: true });
  server = createServer(async (req, res) => {
    try {
      const path = resolve(sandbox, '.' + new URL(req.url, 'http://localhost').pathname);
      if (!path.startsWith(sandbox + '/')) throw new Error('outside sandbox');
      let bytes = await readFile(path);
      if (process.env.BASELINE && path === resolve(here, 'sections.css')) bytes = Buffer.from('');
      if (path === resolve(here, 'index.html') && process.env.BASELINE) {
        bytes = Buffer.from(bytes.toString().replace('../motion.js', `reference/${process.env.BASELINE === 'reference' ? 'motion.js' : 'pre-sections-runner.js'}`).replace('src="sections.js"', 'src="reference/sections.js"'));
      }
      res.writeHead(200, { 'Content-Type': ({'.html':'text/html','.css':'text/css','.js':'text/javascript','.woff2':'font/woff2'})[extname(path)] || 'application/octet-stream' }); res.end(bytes);
    } catch { res.writeHead(404); res.end('Not found'); }
  });
  await new Promise(r => server.listen(0, '127.0.0.1', r));
  base = `http://127.0.0.1:${server.address().port}/sections/index.html`;
  browser = await engine.launch({ headless: true, ...(engine === webkit && process.env.WEBKIT_EXECUTABLE ? { executablePath: process.env.WEBKIT_EXECUTABLE } : {}) });
});
test.after(async () => { await browser?.close(); await new Promise(r => server.close(r)); });
async function open(width = 390, options = {}, suffix = '', init) {
  const context = await browser.newContext({ viewport: {width,height:900}, ...options });
  const page = await context.newPage(); const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  page.on('response', r => { if (r.status() >= 400) errors.push(`HTTP ${r.status()} ${r.url()}`); });
  if (init) await page.addInitScript(init);
  await page.goto(base + suffix); await page.evaluate(() => document.fonts.ready);
  return { context, page, errors };
}
async function state(page) {
  return page.evaluate(() => {
    const vis = e => getComputedStyle(e).visibility !== 'hidden' && e.getClientRects().length > 0;
    const count = s => [...document.querySelectorAll(s)].filter(vis).length;
    return { undo: count('.urows li:not(.peek)'), peek: count('.peek'), balloon: count('.balloon'), rows:count('.info .row'), lines:count('.editor .ln'), tab:document.querySelector('#rules-win .on').textContent,
      cmd:document.querySelector('#term code').textContent, stepping:document.querySelectorAll('.stepping').length, overlays:document.querySelectorAll('[data-zm-overlay]').length };
  });
}
const final = {undo:5,peek:1,balloon:1,rows:5,lines:13,tab:'Settings',cmd:command,stepping:0,overlays:0};
async function reach(page, selector) {
  for (let i = 0; i < 160; i++) {
    const mode = await page.locator(selector).getAttribute('data-mode');
    if (mode === 'play' || mode === 'done') return;
    if (mode === 'seen' || mode === 'static') throw new Error(`${selector} skipped rather than played (${mode})`);
    await page.evaluate(() => scrollBy(0, 100)); await page.waitForTimeout(45);
  }
  throw new Error(`never reached ${selector}`);
}

test('S1: selected B final markup retains 13 Rules lines, 5+cut Undo rows, exact command and static no-JS/reduced parity', async () => {
  for (const width of [320,390,760,1440,2560]) {
    const unavailable = () => Object.defineProperty(navigator,'clipboard',{value:undefined});
    const a = await open(width, {}, '?static', unavailable); assert.deepEqual(await state(a.page), final);
    const png = await a.page.screenshot({fullPage:true});
    for (const [options, suffix] of [[{javaScriptEnabled:false},''],[{reducedMotion:'reduce'},''],[{reducedMotion:'reduce'},'?frame=0']]) {
      const b = await open(width, options, suffix, unavailable); assert.deepEqual(await state(b.page), final);
      assert.ok(png.equals(await b.page.screenshot({fullPage:true})), `static pixel parity ${width} ${JSON.stringify(options)} ${suffix}`);
      assert.deepEqual(b.errors, []); await b.context.close();
    }
    assert.deepEqual(a.errors, []); await a.context.close();
  }
});

test('S2: first-sight hash and real in-page link arrivals stay final, never rewind', async () => {
  for (const selector of roots) {
    const a = await open(390, {}, '#' + selector.slice(1));
    await a.page.waitForTimeout(150);
    assert.equal(await a.page.locator(selector).getAttribute('data-mode'), 'seen');
    assert.equal(await a.page.locator(selector).evaluate(e => [...e.classList].some(c => c.startsWith('lt-')) || !!e.querySelector('.stepping,[data-zm-overlay]')), false);
    const current = await state(a.page), keys = ({'#install':['rows'], '#rules-win':['lines','tab'], '#undo-win':['undo','peek','balloon'], '#term':['cmd']})[selector];
    for (const key of keys) assert.equal(current[key], final[key]);
    await a.context.close();
  }
  const a = await open(1440); await a.page.locator('.acts a[href="#install"]').click(); await a.page.waitForTimeout(150);
  assert.equal(await a.page.locator('#install').getAttribute('data-mode'), 'seen'); assert.equal((await state(a.page)).rows, 5); await a.context.close();
});

test('S3: reader scroll plays every beat once, observes authored intermediate states, zero overflow/CLS and complete final', async () => {
  for (const width of [320,390,760,1440,2560]) {
    const a = await open(width, {}, '', () => {
      window.samples = []; window.shifts = [];
      if (PerformanceObserver.supportedEntryTypes.includes('layout-shift')) new PerformanceObserver(l => { for (const e of l.getEntries()) if (!e.hadRecentInput) window.shifts.push({value:e.value,at:e.startTime,sources:(e.sources||[]).map(s=>({tag:s.node?.nodeName,text:s.node?.textContent?.slice(0,60),previous:s.previousRect,current:s.currentRect}))}); }).observe({type:'layout-shift',buffered:true});
      setInterval(() => {
        const d = document, visible = e => getComputedStyle(e).visibility !== 'hidden';
        window.samples.push({ modes:[...d.querySelectorAll('[data-mode]')].map(e=>[e.id,e.dataset.mode]), tab:d.querySelector('#rules-win .on')?.textContent,
          lines:[...d.querySelectorAll('.editor .ln')].filter(visible).length, undo:[...d.querySelectorAll('.urows li')].filter(visible).length, rows:[...d.querySelectorAll('.info .row')].filter(visible).length,
          typed:[...d.querySelectorAll('.typed-letter')].filter(visible).length, zoom:[...d.querySelectorAll('.zr')].map(e=>({hidden:e.getAttribute('aria-hidden'),pointer:getComputedStyle(e).pointerEvents,box:[e.style.left,e.style.top,e.style.width,e.style.height]})), cursor:d.querySelectorAll('.cursor').length,
          overflow:d.documentElement.scrollWidth-d.documentElement.clientWidth });
      },25);
    });
    const since = await a.page.evaluate(() => performance.now());
    for (const root of roots) { await reach(a.page,root); await a.page.waitForFunction(s=>document.querySelector(s).dataset.mode==='done',root,{timeout:7000}); }
    await a.page.waitForTimeout(3100); // finite terminal blink has stopped
    assert.deepEqual(await state(a.page),final);
    const r = await a.page.evaluate(() => ({samples:window.samples,shifts:window.shifts, durations:[...document.querySelectorAll('[data-duration-ms]')].map(e=>[e.id,+e.dataset.durationMs])}));
    const played = r.samples.filter(s=>s.modes.some(([,m])=>m==='play'));
    assert.ok(played.length); assert.ok(r.samples.some(s=>s.modes.some(([,m])=>m==='armed')));
    for (const tab of ['Open loops','Accounts','Undo','Settings']) assert.ok(r.samples.some(s=>s.tab===tab),tab);
    assert.ok(played.some(s=>s.lines>0&&s.lines<13)); assert.ok(played.some(s=>s.undo>0&&s.undo<6)); assert.ok(played.some(s=>s.rows>0&&s.rows<5));
    assert.ok(played.some(s=>s.typed>0&&s.typed<command.length)); assert.ok(played.some(s=>s.zoom.length));
    assert.ok(r.samples.every(s=>s.cursor===0&&s.overflow===0));
    for (const s of r.samples) for (const z of s.zoom) { assert.equal(z.hidden,'true'); assert.equal(z.pointer,'none'); assert.ok(z.box.every(v=>Number.isInteger(parseFloat(v)))); }
    if (engine===chromium) assert.equal(r.shifts.filter(s=>s.at>=since).reduce((n,s)=>n+s.value,0),0,JSON.stringify(r.shifts));
    assert.ok(r.durations.length===4&&r.durations.every(([,ms])=>ms<6000));
    console.log('SECTION_TIMING',JSON.stringify({width,durations:r.durations,cls:engine===chromium?0:'API unavailable'}));
    await a.page.evaluate(()=>scrollTo(0,0)); await a.page.waitForTimeout(200); assert.deepEqual(await state(a.page),final);
    assert.deepEqual(a.errors,[]); await a.context.close();
  }
});

test('S4: reduced preference mid-reveal cancels to full final with no late DOM mutations', async () => {
  for (const root of roots) {
    const a = await open(); await reach(a.page,root); await a.page.waitForTimeout(400);
    await a.page.emulateMedia({reducedMotion:'reduce'}); await a.page.waitForTimeout(60);
    assert.deepEqual(await state(a.page),final); const html=await a.page.locator(root).innerHTML(); await a.page.waitForTimeout(900); assert.equal(await a.page.locator(root).innerHTML(),html);
    await a.context.close();
  }
});

test('S5: Copy success/denial/no API, keyboard focus and announced status, selectable command', async () => {
  for (const mode of ['success','denial','unavailable']) {
    const a = await open(320, {}, '?static', () => {});
    await a.page.addInitScript(m => Object.defineProperty(navigator,'clipboard',{value:m==='unavailable'?undefined:{writeText:t=>{window.copied=t;return m==='denial'?Promise.reject(new DOMException('denied','NotAllowedError')):Promise.resolve();}}}),mode);
    await a.page.reload(); await a.page.evaluate(()=>document.fonts.ready);
    if (mode==='unavailable') assert.equal(await a.page.locator('#copy').isVisible(),false);
    else {
      await a.page.locator('#copy').focus(); await a.page.keyboard.press('Enter'); await a.page.waitForTimeout(80);
      const r=await a.page.evaluate(()=>({text:document.querySelector('#copy-status').textContent,live:document.querySelector('#copy-status').getAttribute('aria-live'),role:document.querySelector('#copy-status').getAttribute('role'),focus:document.activeElement.id,selected:getSelection().toString(),copied:window.copied}));
      assert.equal(r.text,mode==='success'?'Copied':'Copy manually: press Command-C.'); assert.equal(r.live,'polite');assert.equal(r.role,'status');assert.equal(r.focus,'copy');
      assert.equal(r.copied,command); if(mode==='denial')assert.equal(r.selected,command);
      assert.ok(await a.page.locator('#copy-status').isVisible());
    }
    assert.equal(await a.page.locator('#term code').textContent(),command); await a.context.close();
  }
});

test('S6: missing IntersectionObserver and story errors leave complete final, no overlays', async () => {
  const a=await open(390,{},'',()=>{delete window.IntersectionObserver;}); assert.deepEqual(await state(a.page),final); await a.context.close();
  const b=await open(); await b.page.evaluate(()=>{const app=document.querySelector('.appicon svg');app.remove();}); await reach(b.page,'#install');
  await b.page.waitForFunction(()=>document.querySelector('#install').dataset.mode==='error'); assert.deepEqual(await state(b.page),final);await b.context.close();
});

test('S7: bounded mobile/desktop visual proof of all three frames plus reduced end state',{skip:process.env.CAPTURE!=='1'},async()=>{
  for(const width of [390,1440])for(const frame of [0,1,2]){
    const a=await open(width,{},'?frame='+frame);await a.page.screenshot({path:resolve(here,`evidence/${width}-frame-${frame}.png`),fullPage:true});
    for(const root of roots)await a.page.locator(root).screenshot({path:resolve(here,`evidence/${width}-${root.slice(1)}-frame-${frame}.png`)});
    await a.context.close();
  }
  // The Terminal's last QA frame is intentionally its truthful final state.
  // Capture partial glyphs through actual reader scrolling, not QA rewinding.
  for (const width of [390,1440]) {
    const a = await open(width);
    await reach(a.page,'#term');
    await a.page.waitForFunction(() => [...document.querySelectorAll('.typed-letter')].filter(e => getComputedStyle(e).visibility !== 'hidden').length >= 4);
    const before = await a.page.locator('.typed-letter').evaluateAll(els => els.filter(e => getComputedStyle(e).visibility !== 'hidden').length);
    assert.ok(before >= 4 && before < command.length);
    await a.page.locator('#term').screenshot({path:resolve(here,`evidence/${width}-term-live-partial.png`)});
    await a.page.waitForFunction(() => document.querySelector('#term').dataset.mode === 'done');
    assert.equal((await state(a.page)).cmd, command);
    console.log('LIVE_TERMINAL_CAPTURE', JSON.stringify({width, visibleGlyphsBeforeScreenshot:before}));
    await a.context.close();
  }
});

test('S8: synthetic visibility interruption settles every story without late writes',async()=>{
  for(const root of roots){
    const a=await open();await reach(a.page,root);await a.page.waitForTimeout(400);
    await a.page.evaluate(()=>{Object.defineProperty(document,'hidden',{configurable:true,value:true});document.dispatchEvent(new Event('visibilitychange'));});
    assert.deepEqual(await state(a.page),final);const html=await a.page.locator(root).innerHTML();await a.page.waitForTimeout(900);assert.equal(await a.page.locator(root).innerHTML(),html);await a.context.close();
  }
});

test('S9: denial during typing selects the whole command and preserves it, repeat activation is ignored',async()=>{
  const a=await open(390,{},'',()=>Object.defineProperty(navigator,'clipboard',{value:{writeText:()=>{window.writes=(window.writes||0)+1;return new Promise((resolve,reject)=>{window.deny=()=>reject(new DOMException('denied','NotAllowedError'));});}}}));
  await reach(a.page,'#term');await a.page.waitForTimeout(300);await a.page.locator('#copy').focus();await a.page.keyboard.press('Enter');await a.page.keyboard.press('Enter');
  assert.equal(await a.page.evaluate(()=>window.writes),1);await a.page.evaluate(()=>window.deny());await a.page.waitForTimeout(80);
  assert.equal(await a.page.evaluate(()=>getSelection().toString()),command);assert.equal(await a.page.locator('#term').getAttribute('data-mode'),'cancelled');
  await a.page.waitForTimeout(1000);assert.equal(await a.page.evaluate(()=>getSelection().toString()),command);assert.equal(await a.page.evaluate(()=>document.activeElement.id),'copy');await a.context.close();
});

test('S10: real headless Chromium clipboard API copies the exact command through keyboard activation',{skip:engine!==chromium},async()=>{
  const a=await open(390,{permissions:['clipboard-read','clipboard-write']},'?static');await a.page.locator('#copy').focus();await a.page.keyboard.press('Enter');
  await a.page.waitForFunction(()=>document.querySelector('#copy-status').textContent==='Copied');assert.equal(await a.page.evaluate(()=>navigator.clipboard.readText()),command);await a.context.close();
});

test('S11: actual keyboard order, readable Rules policy, visible focus and finite blink',async()=>{
  const a=await open(1440,{},'?static');
  const expected=await a.page.evaluate(()=>[...document.querySelectorAll('a[href],button')].filter(e=>e.getClientRects().length).map(e=>e.textContent.trim()));const got=[];
  for(let i=0;i<expected.length;i++){await a.page.keyboard.press(engine===webkit?'Alt+Tab':'Tab');got.push(await a.page.evaluate(()=>document.activeElement.textContent.trim()));}
  assert.deepEqual(got,expected);assert.equal(await a.page.locator('.editor pre').evaluate(e=>!!e.closest('[aria-hidden="true"]')),false);
  await a.page.locator('#copy').focus();assert.equal(await a.page.locator('#copy').evaluate(e=>getComputedStyle(e).outlineWidth),'3px');
  assert.equal(await a.page.locator('.peek').getAttribute('aria-hidden'),'true');assert.equal((await a.page.locator('.peek').textContent()).trim(),'');
  await a.page.locator('#term').evaluate(e=>e.classList.add('blink'));const animation=await a.page.locator('.cursorblk').evaluate(e=>{const s=getComputedStyle(e);return [s.animationIterationCount,s.animationTimingFunction];});assert.deepEqual(animation,['3','steps(1)']);await a.context.close();
});

test('S12: resizing an active scene cancels safely, and ledger beats accept changed row counts/words',async()=>{
  const a=await open();await a.page.evaluate(()=>{const row=document.querySelector('.info .row').cloneNode(true);row.querySelector('dd').textContent='Provisional changed row for geometry test';document.querySelector('.info .rows').append(row);});await reach(a.page,'#install');await a.page.waitForTimeout(400);await a.page.setViewportSize({width:760,height:900});await a.page.waitForTimeout(50);
  assert.equal(await a.page.locator('#install').getAttribute('data-mode'),'cancelled');assert.equal((await state(a.page)).rows,6);assert.equal(await a.page.locator('#install [data-zm-overlay]').count(),0);await a.context.close();
});
