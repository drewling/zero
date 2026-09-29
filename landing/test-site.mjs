import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { runInNewContext } from 'node:vm';
import test from 'node:test';

const source = readFileSync(new URL('./site.js', import.meta.url), 'utf8');
const homepage = readFileSync(new URL('./index.html', import.meta.url), 'utf8');
const styles = readFileSync(new URL('./site.css', import.meta.url), 'utf8');
const installCommand = 'curl -fsSL https://zero.headless.com/install | bash';

function page(clipboard) {
  const elements = {
    'copy-command': {
      hidden: true,
      disabled: false,
      textContent: 'Copy',
      attributes: {},
      setAttribute(name, value) {
        this.attributes[name] = value;
      },
      removeAttribute(name) {
        delete this.attributes[name];
      },
      addEventListener(type, callback) {
        assert.equal(type, 'click');
        this.click = callback;
      },
    },
    'install-command': { textContent: installCommand },
    'copy-status': { textContent: '' },
  };
  runInNewContext(source, {
    document: { getElementById: (id) => elements[id] },
    navigator: { clipboard },
  });
  return { button: elements['copy-command'], status: elements['copy-status'] };
}

test('copy writes the exact install command and announces success', async () => {
  let written;
  const { button, status } = page({ writeText: async (text) => { written = text; } });
  assert.equal(button.hidden, false);
  await button.click();
  assert.equal(written, installCommand);
  assert.match(status.textContent, /^Copied\./);
  assert.equal(button.disabled, false);
  assert.equal(button.attributes['aria-disabled'], undefined);
  assert.equal(button.attributes['aria-busy'], undefined);
  assert.equal(button.textContent, 'Copy again');
});

test('clipboard denial offers manual recovery and allows retry', async () => {
  let rejected = true;
  const { button, status } = page({ writeText: async () => {
    if (rejected) throw new Error('NotAllowedError');
  } });
  await button.click();
  assert.match(status.textContent, /copy it manually/);
  assert.equal(button.disabled, false);
  assert.equal(button.attributes['aria-disabled'], undefined);
  assert.equal(button.attributes['aria-busy'], undefined);
  rejected = false;
  await button.click();
  assert.match(status.textContent, /^Copied\./);
});

test('clipboard is guarded while pending without blurring focusable control', async () => {
  let finish;
  let calls = 0;
  const { button } = page({ writeText: () => {
    calls += 1;
    return new Promise((resolve) => { finish = resolve; });
  } });
  const pending = button.click();
  assert.equal(button.disabled, false);
  assert.equal(button.attributes['aria-disabled'], 'true');
  assert.equal(button.attributes['aria-busy'], 'true');
  await button.click();
  assert.equal(calls, 1);
  finish();
  await pending;
  assert.equal(button.disabled, false);
  assert.equal(button.attributes['aria-disabled'], undefined);
  assert.equal(button.attributes['aria-busy'], undefined);
});

test('unavailable clipboard leaves the optional control hidden', () => {
  const { button } = page(undefined);
  assert.equal(button.hidden, true);
  assert.equal(button.click, undefined);
});

test('homepage follows the approved visitor-first six-section order', () => {
  for (const pattern of [
    /<title>zero — Only the mail that still needs you\.<\/title>/,
    /id="decides"[\s\S]*?id="morning"[\s\S]*?id="undo"[\s\S]*?id="before"[\s\S]*?id="install"/,
    /id="hero-title"[\s\S]*?Only the mail[\s\S]*?needs you\./,
    /class="hero-req">Apple Silicon · macOS 26 or later · Gmail<\//,
    /<div class="zp" aria-hidden="true" inert>/,
    /zero’s real layout, redrawn\. Names and subjects are made up\./,
    /id="decides"[\s\S]*?It asks who’s[\s\S]*?waiting, not[\s\S]*?who’s writing\./,
    /class="signals"[\s\S]*?Was the last message yours\?[\s\S]*?Have you ever written to this sender\?/,
    /id="morning"[\s\S]*?Check it with[\s\S]*?your coffee\.[\s\S]*?Then close it\./,
    /id="undo"[\s\S]*?Nothing is[\s\S]*?deleted\./,
    /id="before"[\s\S]*?What it needs, sends and costs/,
    /id="install"[\s\S]*?Install zero\./,
    /href="\/privacy\.html"/,
    /href="\/terms\.html"/,
    /pixelify-400\.woff2/,
    /assets\/zero-panel\.png/,
  ]) assert.match(homepage, pattern);
  assert.match(homepage, /Across every account you connect/);
  assert.match(homepage, /Every archive can be undone/);
  assert.match(homepage, /The zero project runs no server that receives your email/);
  assert.match(homepage, /zero is free and open source/);
  assert.match(homepage, /curl -fsSL https:\/\/zero\.headless\.com\/install \| bash/);
  const installSteps = homepage.match(/<ol class="install-steps">[\s\S]*?<\/ol>/)?.[0] ?? '';
  assert.equal((installSteps.match(/<li/g) ?? []).length, 4);
  assert.match(installSteps, /<li class="install-step-terminal">[\s\S]*?Run the installer in Terminal\./);
});

test('retired table, FAQ, motion hooks, and dead implementation assets are absent', () => {
  const combined = `${homepage}\n${styles}\n${source}`;
  for (const pattern of [
    /class="finder window"/,
    /class="questions content-section"/,
    /<table>/,
    /<details>/,
    /hero-facts/,
    /sort-track/,
    /rail-diagram/,
    /sorting-board/,
    /flap-board/,
    /ticket-section/,
    /install-band/,
    /motion-reduced/,
    /Archivo/,
    /getContext/,
    /requestAnimationFrame/,
    /IntersectionObserver/,
    /ResizeObserver/,
    /Run the sort again/,
    /Show the archive again/,
  ]) assert.doesNotMatch(combined, pattern);
  assert.match(styles, /\.folder-current\{animation:folder-drop 900ms steps\(6,end\) 700ms both\}/);
  assert.match(styles, /@media \(prefers-reduced-motion:no-preference\)/);
  assert.match(styles, /@media \(prefers-reduced-motion:reduce\)/);
  assert.match(source, /navigator\.clipboard/);
  assert.doesNotMatch(styles, /canvas/);
});

test('hero panel is a faithful, decorative one-bit redraw of the real Open loops panel', () => {
  const panel = homepage.match(/<figure class="app-window">[\s\S]*?<\/figure>/)?.[0] ?? '';
  assert.ok(panel, 'hero figure present');
  // Replaces the dark raster crop; the source screenshot stays as og:image evidence only.
  assert.doesNotMatch(homepage, /panel-cut\.png/);
  assert.doesNotMatch(panel, /<img\b/);
  assert.match(homepage, /og:image" content="https:\/\/zero\.headless\.com\/assets\/zero-panel\.png"/);
  // Real app structure (macapp/Sources/PanelView.swift, KeeperModel.swift Tab titles).
  for (const pattern of [
    /zp-mark[\s\S]*?zero</,
    /zp-av zp-ta">TA<b>99\+<\/b>/,
    /zp-av zp-li">LI<b>25<\/b>/,
    /zp-tabs"><span class="zp-on">Open loops<\/span><span>Accounts<\/span><span>Undo<\/span><span>Settings<\/span>/,
    /<strong>416<\/strong>\s*<span class="zp-need">things still need you<\/span>/,
    /Across 2 accounts\. Tap any to open it in Gmail\./,
    /class="zp-label">Waiting on you</,
    /Action required/,
    /Needs reply/,
    /Tidies every inbox to only what needs you\./,
    /class="zp-run">[\s\S]*?Run zero now/,
  ]) assert.match(panel, pattern);
  const rows = panel.match(/<ul class="zp-rows">[\s\S]*?<\/ul>/)?.[0] ?? '';
  const items = rows.match(/<li>[\s\S]*?<\/li>/g) ?? [];
  assert.equal(items.length, 6);
  for (const row of items) {
    assert.match(row, /class="zp-who"[\s\S]*?<b>[^<]+<\/b>[\s\S]*?class="zp-subj">[^<]+</, 'sender + subject');
    assert.match(row, /class="zp-age">(\d+[mhdw]|now)</, 'age uses relTime units');
    assert.match(row, /#zp-reply[\s\S]*?#zp-spark[\s\S]*?#zp-archive/, 'Reply, AI archive, Archive in app order');
  }
  // Only tags that exist as default categories (lib/review_open_loops.py).
  const tags = [...rows.matchAll(/<svg><use href="#zp-(?:bolt|mail)"\/><\/svg>([^<]+)<\/em>/g)].map((m) => m[1]);
  assert.deepEqual([...new Set(tags)].sort(), ['Action required', 'Needs reply']);
  // Decorative: hidden from AT, inert, nothing focusable; an sr-only summary carries the meaning.
  assert.match(panel, /<div class="zp" aria-hidden="true" inert>/);
  // The panel's markup depends on new CSS; a versioned href stops a heuristically cached site.css
  // from rendering the new markup unstyled for returning visitors (nginx sends no Cache-Control).
  assert.match(homepage, /<link rel="stylesheet" href="\/site\.css\?v=[\w.-]+">/);
  assert.doesNotMatch(panel, /<(a|button|input|select|textarea)\b|tabindex=/);
  assert.match(panel, /<p class="sr-only">Illustration of zero’s Open loops panel: [^<]{80,}<\/p>/);
  assert.match(panel, /<figcaption>zero’s real layout, redrawn\. Names and subjects are made up\.<\/figcaption>/);
  // One-bit: the redraw introduces no hue.
  const zpCss = styles.split('\n').filter((line) => /\.zp/.test(line)).join('\n');
  assert.ok(zpCss.length > 500);
  const hexes = [...zpCss.matchAll(/#[0-9a-f]{3,8}\b/gi)].map((m) => m[0].toLowerCase());
  assert.deepEqual([...new Set(hexes)], ['#3d3d3d'], 'only the neutral secondary-ink grey');
  assert.doesNotMatch(zpCss, /\b(rgb|rgba|hsl|hsla|oklch|lab)\(/i);
  assert.doesNotMatch(zpCss, /animation|transition/);
});
