import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import test from 'node:test';

const proof = path.dirname(fileURLToPath(import.meta.url));
const scratch = process.env.JCODE_SCRATCH_DIR;
assert.ok(scratch, 'Set JCODE_SCRATCH_DIR to keep fixtures outside owner state');
fs.mkdirSync(scratch, { recursive: true });

function runFixture(t, mutate = () => {}, args = []) {
  const dir = fs.mkdtempSync(path.join(scratch, 'zero-copy-check-'));
  t.after(() => fs.rmSync(dir, { recursive: true, force: true }));
  fs.cpSync(proof, dir, { recursive: true });
  mutate(dir);
  const result = spawnSync(process.execPath, [path.join(dir, 'verify-copy.mjs'), ...args], {
    encoding: 'utf8', timeout: 10000,
  });
  assert.equal(result.error, undefined);
  return result;
}

function changeCopy(dir, oldText, newText) {
  const file = path.join(dir, 'COPY.md');
  const text = fs.readFileSync(file, 'utf8');
  assert.ok(text.includes(oldText));
  fs.writeFileSync(file, text.replace(oldText, newText));
}

function rejects(t, mutate, reason) {
  const result = runFixture(t, mutate);
  assert.notEqual(result.status, 0);
  assert.match(result.stderr, reason);
}

test('public verifier accepts the complete authored package and measured inventory', t => {
  const result = runFixture(t);
  assert.equal(result.status, 0, result.stderr);
  assert.match(result.stdout, /primary: 425/);
  assert.match(result.stdout, /visible total: 549/);
  assert.match(result.stdout, /Three distinct successful single-turn Mac\/Gmail\/inbox readers: PASS/);
});

test('cold-reader public output reproduces the committed verbatim record', t => {
  const result = runFixture(t, undefined, ['--cold-reader']);
  assert.equal(result.status, 0, result.stderr);
  assert.equal(result.stdout.trim(), fs.readFileSync(path.join(proof, 'cold-reader.md'), 'utf8').trim());
});

test('over-budget copy fails rather than treating authored count as advisory', t => {
  rejects(t, dir => changeCopy(dir, '<!-- PAGE-COPY-END -->', 'extra extra extra\n<!-- PAGE-COPY-END -->'), /Word budget failed: 552/);
});

test('case-insensitive banned wording fails even outside visible-copy markers', t => {
  rejects(t, dir => fs.appendFileSync(path.join(dir, 'COPY.md'), '\nOPEN LOOPS\n'), /Banned wording found: open loops/);
});

test('a final-copy change in the tested excerpt invalidates reader reuse', t => {
  rejects(t, dir => changeCopy(dir, 'Click **Run zero now** on your Mac', 'Click **Run zero later** on your Mac'), /Tested excerpt differs/);
});

test('duplicate reader sessions fail despite matching category keywords', t => {
  rejects(t, dir => {
    const first = JSON.parse(fs.readFileSync(path.join(dir, 'cold-reader-r3-1.json'), 'utf8'));
    const file = path.join(dir, 'cold-reader-r3-2.json');
    const second = JSON.parse(fs.readFileSync(file, 'utf8'));
    second.session_id = first.session_id;
    fs.writeFileSync(file, JSON.stringify(second));
  }, /Readers are not distinct sessions/);
});

test('a failed reader call cannot pass from keywords alone', t => {
  rejects(t, dir => {
    const file = path.join(dir, 'cold-reader-r3-1.json');
    const reader = JSON.parse(fs.readFileSync(file, 'utf8'));
    reader.is_error = true;
    fs.writeFileSync(file, JSON.stringify(reader));
  }, /Cold-reader acceptance failed/);
});

test('missing disclosure evidence fails the whole package check', t => {
  rejects(t, dir => fs.rmSync(path.join(dir, 'truth-trace.md')), /Missing proof: truth-trace.md/);
});

test('wrong screenshot dimensions fail even with a valid PNG signature', t => {
  rejects(t, dir => {
    const file = path.join(dir, 'comparables', 'sanebox-first-viewport.png');
    const bytes = fs.readFileSync(file);
    bytes.writeUInt32BE(1, 16);
    fs.writeFileSync(file, bytes);
  }, /Bad screenshot/);
});
