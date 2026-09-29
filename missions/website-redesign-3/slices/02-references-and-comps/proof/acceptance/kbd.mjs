// WebKit keyboard-only pass (the main run already covered WebKit pages)
import { createRequire } from 'node:module'; import { execSync } from 'node:child_process';
const require = createRequire(execSync('npm root -g').toString().trim() + '/'); const { webkit } = require('playwright');
const b = await webkit.launch({ executablePath: process.env.WEBKIT_EXECUTABLE });
for (const pg of ['hero-a', 'hero-b', 'hero-c', 'sections']) {
  const ctx = await b.newContext({ viewport: { width: 1440, height: 900 }, reducedMotion: 'reduce' }); const k = await ctx.newPage();
  await k.goto(`http://127.0.0.1:8941/${pg}/index.html`);
  const total = await k.$$eval('a[href],button:not([disabled])', els => els.filter(e => e.getBoundingClientRect().width).length);
  const seen = new Set(), noRing = [];
  for (let i = 0; i < total + 3; i++) { await k.keyboard.press('Alt+Tab');
    const f = await k.evaluate(() => { const e = document.activeElement; if (!e || e === document.body) return null; const s = getComputedStyle(e); return { id: e.outerHTML.slice(0, 60), ring: s.outlineStyle !== 'none' && parseFloat(s.outlineWidth) > 0 || s.boxShadow !== 'none' }; });
    if (f) { seen.add(f.id); if (!f.ring) noRing.push(f.id); } }
  console.log(`${seen.size >= total ? 'PASS' : 'FAIL'} webkit/keyboard/${pg} reached ${seen.size}/${total}; ${noRing.length ? 'FAIL focus ' + [...new Set(noRing)].slice(0,3).join(' | ') : 'PASS focus'}`);
  await ctx.close(); }
await b.close();
