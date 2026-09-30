import assert from 'node:assert/strict';
import { existsSync, readFileSync } from 'node:fs';
import test from 'node:test';

const root = new URL('./', import.meta.url);
const read = (name) => readFileSync(new URL(name, root), 'utf8');
const homepage = read('index.html');
const styles = read('site.css');
const motion = read('assets/motion.js');
const sections = read('assets/sections.js');
const story = read('site.js');
const installCommand = 'curl -fsSL https://zero.headless.com/install | bash';

const sectionIds = [...homepage.matchAll(/<section\b[^>]*\bid="([^"]+)"/g)].map((match) => match[1]);

test('production document uses approved page B metadata and section order', () => {
  assert.match(homepage, /<title>zero — Clean up your Gmail inbox on your Mac\.<\/title>/);
  assert.match(homepage, /<meta name="theme-color" content="#ffffff">/);
  assert.match(homepage, /<meta name="color-scheme" content="light">/);
  assert.match(homepage, /<link rel="canonical" href="https:\/\/zero\.headless\.com\/">/);
  assert.match(homepage, /<meta property="og:type" content="website">/);
  assert.match(homepage, /<meta property="og:url" content="https:\/\/zero\.headless\.com\/">/);
  assert.match(homepage, /<meta property="og:title" content="zero — Clean up your Gmail inbox on your Mac\.\">/);
  assert.match(homepage, /<meta property="og:description" content="zero is a Mac app that keeps the emails you need to deal with and archives the rest\. Undo any archive\.\">/);
  assert.match(homepage, /<meta property="og:image" content="https:\/\/zero\.headless\.com\/assets\/og-image\.png">/);
  assert.match(homepage, /<meta property="og:image:width" content="1200">/);
  assert.match(homepage, /<meta property="og:image:height" content="630">/);
  assert.match(homepage, /<meta property="og:image:alt" content="zero landing page hero illustration\.\">/);
  assert.match(homepage, /<meta name="twitter:card" content="summary_large_image">/);
  assert.match(homepage, /<link rel="icon" href="data:image\/svg\+xml,/);
  assert.equal(existsSync(new URL('assets/og-image.png', root)), true, 'og image');
  assert.deepEqual(sectionIds, ['hero', 'install', 'how-band', 'undo', 'command']);
  assert.match(homepage, /<h1 id="h1">Clean up your Gmail inbox on your Mac\.<\/h1>/);
  assert.match(homepage, /zero is a Mac app that keeps the emails you need to deal with and archives the rest\. Undo any archive\. Keep using Gmail or Apple Mail\./);
  assert.match(homepage, /class="req">Apple Silicon\. macOS 26 or later\. Gmail only\.<\/p>/);
});

test('approved disclosures and recovery copy remain visible in the public document', () => {
  for (const phrase of [
    'Sorting data.',
    'Sent to TypeSafe (Jev):',
    'Optional drafts.',
    'Sent to your coding tool’s provider:',
    'Drafts never send automatically.',
    'TypeSafe receives sorting data. Your tool’s provider receives draft data. Neither goes to zero’s servers.',
    'Jev 1.13: $0.042/million input tokens, outputs free (2026-09-30).',
    'Google may show an unverified-app warning',
    'zero is not notarized by Apple.',
    'Starred mail stays untouched.',
    'AI can make mistakes.',
    'Nothing is deleted.',
    'All Mail',
    'Ready to install?',
    'GitHub Releases',
  ]) assert.match(homepage, new RegExp(phrase.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')));
  assert.match(homepage, new RegExp(installCommand.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')));
  assert.match(homepage, /href="\/privacy\.html"/);
  assert.match(homepage, /href="\/terms\.html"/);
});

test('hero has a single compact requirement line and one dated drop target', () => {
  assert.equal((homepage.match(/class="req"/g) ?? []).length, 1);
  assert.match(homepage, /class="icon folder sel"/);
  assert.doesNotMatch(homepage, /folder-current/);
  assert.doesNotMatch(styles, /folder-current|folder-drop|translate\(260px,-40px\)/);
  assert.doesNotMatch(homepage, /hero-facts|DRAFT comp|not the live site/);
});

test('copy control contract preserves focus during pending clipboard writes', () => {
  assert.match(homepage, /id="copy"[^>]*hidden/);
  assert.match(homepage, /id="copy-status"[^>]*role="status"[^>]*aria-live="polite"/);
  assert.match(sections, /let timer, pending = false/);
  assert.match(sections, /pending = true; btn\.setAttribute\('aria-disabled', 'true'\); btn\.setAttribute\('aria-busy', 'true'\)/);
  assert.match(sections, /if \(pending\) return/);
  assert.match(sections, /Copy manually: press Command-C\./);
  assert.match(sections, /finally \{ pending = false; btn\.removeAttribute\('aria-disabled'\); btn\.removeAttribute\('aria-busy'\); \}/);
  assert.doesNotMatch(sections, /btn\.disabled\s*=/);
});

test('motion is bounded, reduced-motion safe, and has no prohibited rendering APIs', () => {
  assert.match(story, /maxMs/);
  assert.match(motion, /prefers-reduced-motion: reduce/);
  assert.match(motion, /q\.has\('static'\)/);
  assert.match(sections, /Copy manually: press Command-C\./);
  for (const source of [homepage, styles, motion, sections, story]) {
    assert.doesNotMatch(source, /getContext\s*\(|ResizeObserver|AudioContext|scrollTo\s*\(/);
  }
});

test('production assets are self-contained and obsolete comp paths are gone', () => {
  for (const name of [
    'assets/kit.css', 'assets/page.css', 'assets/chicagoflf.woff2',
    'assets/geist.woff2', 'assets/geist-mono.woff2', 'assets/motion.js', 'assets/sections.js',
    'assets/og-image.png', 'privacy.html', 'terms.html', 'Dockerfile', 'nginx.conf', 'robots.txt', 'sitemap.xml', 'llms.txt',
  ]) assert.equal(existsSync(new URL(name, root)), true, name);
  assert.doesNotMatch(homepage, /\.\.\/kit\//);
  assert.doesNotMatch(`${homepage}\n${styles}\n${story}\n${sections}`, /missions\/website-redesign/);
  assert.doesNotMatch(`${homepage}\n${styles}`, /pixelify|zero-panel\.png/i);
});

test('accessible structure exposes real headings, labels, and decorative boundaries', () => {
  assert.match(homepage, /<main id="top">/);
  assert.match(homepage, /aria-labelledby="h1"/);
  assert.match(homepage, /aria-labelledby="before"/);
  assert.match(homepage, /<dl class="rows">/);
  assert.match(homepage, /<p class="sr-only">Illustration:/);
  assert.match(homepage, /aria-hidden="true"/);
  assert.match(homepage, /<footer>/);
});
