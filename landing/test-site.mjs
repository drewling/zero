import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { runInNewContext } from 'node:vm';
import test from 'node:test';

const source = readFileSync(new URL('./site.js', import.meta.url), 'utf8');
const installCommand = 'curl -fsSL https://zero.headless.com/install | bash';

function page(clipboard) {
  const elements = {
    'copy-command': {
      hidden: true,
      disabled: false,
      textContent: 'Copy',
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
  rejected = false;
  await button.click();
  assert.match(status.textContent, /^Copied\./);
});

test('copy is disabled while clipboard write is pending', async () => {
  let finish;
  const { button } = page({ writeText: () => new Promise((resolve) => { finish = resolve; }) });
  const pending = button.click();
  assert.equal(button.disabled, true);
  finish();
  await pending;
  assert.equal(button.disabled, false);
});

test('unavailable clipboard leaves the optional control hidden', () => {
  const { button } = page(undefined);
  assert.equal(button.hidden, true);
  assert.equal(button.click, undefined);
});
