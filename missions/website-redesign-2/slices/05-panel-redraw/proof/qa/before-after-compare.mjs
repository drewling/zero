import { chromium } from 'playwright';

const CASES = [
  { label: 'before (c53bf91)', url: 'http://127.0.0.1:8899/' },
  { label: 'after (c32f10d)', url: 'http://127.0.0.1:8898/' },
];
const WIDTHS = [1440, 1024, 761, 390, 320];

const browser = await chromium.launch();
const report = {};

for (const { label, url } of CASES) {
  report[label] = {};
  for (const w of WIDTHS) {
    const page = await browser.newPage({ viewport: { width: w, height: 900 } });
    await page.goto(url, { waitUntil: 'load' });
    const data = await page.evaluate(() => {
      const rows = [...document.querySelectorAll('.zp-rows li')];
      return rows.map((li) => {
        const b = li.querySelector('.zp-line b');
        if (!b) return null;
        const cs = getComputedStyle(b);
        return {
          text: b.textContent,
          textOverflow: cs.textOverflow,
          whiteSpace: cs.whiteSpace,
          scrollWidthExceedsClient: b.scrollWidth > b.clientWidth + 1, // true clipping signal when overflow:hidden
          hasEllipsisChar: b.textContent.includes('\u2026'),
        };
      }).filter(Boolean);
    });
    report[label][w] = data;
    await page.close();
  }
}
await browser.close();

// Compare "Sarah Mitchell" specifically at 1440, the exact reported defect.
const before1440 = report['before (c53bf91)'][1440].find(r => r.text.includes('Sarah'));
const after1440 = report['after (c32f10d)'][1440].find(r => r.text.includes('Sarah'));

console.log(JSON.stringify(report, null, 2));
console.log('\n=== Direct before/after comparison for the reported defect (Sarah Mitchell @ 1440) ===');
console.log('BEFORE (c53bf91):', JSON.stringify(before1440));
console.log('AFTER  (c32f10d):', JSON.stringify(after1440));

let regressions = 0;
for (const w of WIDTHS) {
  const beforeRows = report['before (c53bf91)'][w];
  const afterRows = report['after (c32f10d)'][w];
  for (let i = 0; i < afterRows.length; i++) {
    const b = beforeRows[i], a = afterRows[i];
    if (!b || !a) continue;
    // Regression = after has clipping signal that before didn't, for the same row/width.
    if (a.scrollWidthExceedsClient && !b.scrollWidthExceedsClient) {
      regressions++;
      console.log(`REGRESSION at w${w} row "${a.text}": before ok, after clips`);
    }
  }
}
console.log('\nRegressions introduced by the fix:', regressions);
console.log('Defect fixed (before had textOverflow=ellipsis on the truncated name, after does not):',
  before1440.textOverflow === 'ellipsis' && after1440.textOverflow !== 'ellipsis');
