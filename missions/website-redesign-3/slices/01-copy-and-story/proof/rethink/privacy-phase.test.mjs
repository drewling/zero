import test from 'node:test';
import assert from 'node:assert/strict';
import path from 'node:path';
import fs from 'node:fs';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';
const root = path.dirname(fileURLToPath(import.meta.url));

for (const expected of ['', '549', '551']) {
  test(`cost-only freeze requires unchanged 550-word hero state: ${expected || 'missing'}`, () => {
    const run = spawnSync(process.execPath, [path.join(root, 'freeze-stable-pages.mjs'), 'HEAD', 'after-b-cost'], {
      encoding: 'utf8', env: { ...process.env, EXPECTED_WORDS: expected },
    });
    assert.notEqual(run.status, 0);
    assert.match(run.stderr, /after-b-cost requires EXPECTED_WORDS=550/);
    assert.doesNotMatch(run.stdout, /Staging freeze|Frozen /);
  });
}

for (const expected of ['', '551', '548', '549oops']) {
  test(`privacy freeze rejects unspecified or invalid exact word expectation: ${expected || 'missing'}`, () => {
    const run = spawnSync(process.execPath, [path.join(root, 'freeze-stable-pages.mjs'), 'HEAD', 'after-b-privacy'], {
      encoding: 'utf8', env: { ...process.env, EXPECTED_WORDS: expected },
    });
    assert.notEqual(run.status, 0);
    assert.match(run.stderr, /after-b-privacy requires EXPECTED_WORDS=549 or 550/);
    assert.doesNotMatch(run.stdout, /Staging freeze|Frozen /);
  });
}

test('privacy reader accepts the named phase but cannot launch without its immutable inputs', t => {
  const isolated = fs.mkdtempSync(path.join(process.env.JCODE_SCRATCH_DIR, 'zero-privacy-reader-guard-'));
  t.after(() => fs.rmSync(isolated, { recursive: true, force: true }));
  fs.copyFileSync(path.join(root, 'run-matched-reader.mjs'), path.join(isolated, 'run-matched-reader.mjs'));
  const run = spawnSync(process.execPath, [path.join(isolated, 'run-matched-reader.mjs'), 'after-b-privacy', '1'], { encoding: 'utf8' });
  assert.notEqual(run.status, 0);
  assert.match(run.stderr, /ENOENT.*after-b-privacy\/reader-images\.json/);
  assert.doesNotMatch(run.stderr, /Usage: node run-matched-reader/);
});
