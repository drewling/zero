import { chromium } from 'playwright';
const BASE = 'http://127.0.0.1:8897';
const browser = await chromium.launch();
for (const width of [320, 390, 760, 761, 1024, 1100, 1279, 1280, 1440]) {
  const context = await browser.newContext({ viewport: { width, height: 900 } });
  const page = await context.newPage();
  await page.goto(BASE + '/', { waitUntil: 'networkidle' });
  const data = await page.evaluate(() => {
    const rows = [...document.querySelectorAll('.zp-rows > li')];
    const visible = rows.filter(r => r.getBoundingClientRect().height > 0 && getComputedStyle(r).display !== 'none');
    const trash = document.querySelector('.trash-cue');
    const caption = document.querySelector('figcaption');
    const trashRect = trash?.getBoundingClientRect();
    const capRect = caption?.getBoundingClientRect();
    const overlapCaptionTrash = trashRect && capRect ? !(capRect.right < trashRect.left || capRect.left > trashRect.right || capRect.bottom < trashRect.top || capRect.top > trashRect.bottom) : null;
    return {
      totalRows: rows.length,
      visibleRows: visible.length,
      clientWidth: document.documentElement.clientWidth,
      scrollWidth: document.documentElement.scrollWidth,
      overlapCaptionTrash,
    };
  });
  console.log(width, JSON.stringify(data));
  await context.close();
}
await browser.close();
