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

test('homepage preserves the approved one-bit structure and product truth', () => {
  for (const pattern of [
    /id="hero-title"/,
    /class="desktop-hero"/,
    /class="finder window"/,
    /class="paper-section content-section"/,
    /class="terminal-section content-section"/,
    /id="install-command"/,
    /id="copy-command"/,
    /id="copy-status"/,
    /class="hero-req"/,
    /assets\/panel-cut\.png/,
    /<table>/,
    /<details>/,
    /zero-panel\.png/,
    /href="\/privacy\.html"/,
    /href="\/terms\.html"/,
    /pixelify-400\.woff2/,
  ]) assert.match(homepage, pattern);
  assert.match(homepage, />Archived</);
  assert.match(homepage, /Nothing is deleted/);
  assert.match(homepage, /Auto-Archived YYYY-MM-DD/);
  assert.match(homepage, /curl -fsSL https:\/\/zero\.headless\.com\/install \| bash/);
  assert.doesNotMatch(homepage, /class="hero-facts"/);
  assert.match(styles, /\.folder-current\{animation:folder-drop 900ms steps\(6,end\) 700ms both\}/);
  assert.match(styles, /@media \(prefers-reduced-motion:no-preference\)/);
  const installSteps = homepage.match(/<ol class="install-steps">[\s\S]*?<\/ol>/)?.[0] ?? '';
  assert.equal((installSteps.match(/<li/g) ?? []).length, 4);
  assert.match(installSteps, /<li class="install-step-terminal">[\s\S]*?Run the installer in Terminal\./);
  assert.doesNotMatch(homepage, /fonts\.googleapis\.com/);
});

test('legacy motion and departure-board implementation are absent', () => {
  const combined = `${homepage}\n${styles}\n${source}`;
  for (const pattern of [
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
  assert.match(source, /navigator\.clipboard/);
  assert.doesNotMatch(styles, /canvas/);
});
