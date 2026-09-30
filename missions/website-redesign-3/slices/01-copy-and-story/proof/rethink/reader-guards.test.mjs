import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';
const root = path.dirname(fileURLToPath(import.meta.url));

for (const [phase, reader, expected] of [
  ['after-b-tightened', '1', /ENOENT.*after-b-tightened\/reader-images\.json/],
  ['after-b-tightened', '4', /Usage:/],
  ['../after-b-tightened', '1', /Usage:/],
]) {
  test(`reader guard ${phase} ${reader} never launches on absent or invalid evidence`, t => {
    const dir = fs.mkdtempSync(path.join(process.env.JCODE_SCRATCH_DIR, 'zero-reader-guard-'));
    t.after(() => fs.rmSync(dir, { recursive: true, force: true }));
    fs.copyFileSync(path.join(root, 'run-matched-reader.mjs'), path.join(dir, 'run-matched-reader.mjs'));
    const run = spawnSync(process.execPath, [path.join(dir, 'run-matched-reader.mjs'), phase, reader], { encoding: 'utf8' });
    assert.notEqual(run.status, 0);
    assert.match(run.stderr, expected);
    assert.equal(fs.existsSync(path.join(dir, 'readers')), false);
  });
}

test('public verifier refuses to overwrite retained evidence before opening browser', t => {
  const dir = fs.mkdtempSync(path.join(process.env.JCODE_SCRATCH_DIR, 'zero-edge-guard-'));
  t.after(() => fs.rmSync(dir, { recursive: true, force: true }));
  const file = path.join(dir, 'retained.json');
  fs.writeFileSync(file, 'retained proof');
  const run = spawnSync(process.execPath, [path.join(root, 'check-public-edges.mjs'), file], { encoding: 'utf8' });
  assert.notEqual(run.status, 0);
  assert.match(run.stderr, /Do not overwrite public-edge evidence/);
  assert.equal(fs.readFileSync(file, 'utf8'), 'retained proof');
});
