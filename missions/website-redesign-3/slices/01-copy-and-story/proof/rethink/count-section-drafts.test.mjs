import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';

const root = path.dirname(fileURLToPath(import.meta.url));

test('selected B count includes all clipboard states and preserves frozen A/B', () => {
  const run = spawnSync(process.execPath, [path.join(root, 'count-section-drafts.mjs')], {
    encoding: 'utf8', env: { ...process.env, SELECTED_COPY: path.join(root, 'SELECTED-B-COPY.md') },
  });
  assert.equal(run.status, 0, run.stderr);
  const report = JSON.parse(run.stdout.slice(0, run.stdout.indexOf('\n]\n') + 2));
  assert.deepEqual(report.map(row => ({ outline: row.outline, states: row.clipboardStateWords, total: row.authoredTotal })),
    [{ outline: 'B', states: 5, total: 549 }]);
});

for (const [name, mutate, error] of [
  ['missing selected clipboard marker fails', text => text.replace('<!-- CLIPBOARD-COPY-START -->', '<!-- REMOVED -->'), /Missing or duplicate CLIPBOARD-COPY marker/],
  ['two added selected B words exceed the ceiling', text => text.replace('<!-- COPY-B-END -->', 'extra extra\n<!-- COPY-B-END -->'), /B: authored draft outside 350–550: 551/],
]) {
  test(name, t => {
    const dir = fs.mkdtempSync(path.join(process.env.JCODE_SCRATCH_DIR, 'zero-selected-count-'));
    t.after(() => fs.rmSync(dir, { recursive: true, force: true }));
    const selected = path.join(dir, 'selected.md');
    fs.writeFileSync(selected, mutate(fs.readFileSync(path.join(root, 'SELECTED-B-COPY.md'), 'utf8')));
    const run = spawnSync(process.execPath, [path.join(root, 'count-section-drafts.mjs')], {
      encoding: 'utf8', env: { ...process.env, SELECTED_COPY: selected },
    });
    assert.notEqual(run.status, 0);
    assert.match(run.stderr, error);
  });
}

test('authored count CLI includes the complete Rules object and extra app-icon label', () => {
  const run = spawnSync(process.execPath, [path.join(root, 'count-section-drafts.mjs')], { encoding: 'utf8' });
  assert.equal(run.status, 0, run.stderr);
  const report = JSON.parse(run.stdout.slice(0, run.stdout.indexOf('\n]\n') + 2));
  assert.deepEqual(report.map(row => ({ outline: row.outline, shared: row.sharedObjects,
    rules: row.rulesObjectWords, total: row.authoredTotal })), [
    { outline: 'A', shared: 56, rules: 0, total: 474 },
    { outline: 'B', shared: 56, rules: 110, total: 544 },
  ]);
  assert.ok(report.every(row => row.finalRenderedInventoryChecked === false));
});

test('B policy excerpt is contiguous source text, not an edited middle-bullet omission', () => {
  const draft = fs.readFileSync(path.join(root, 'SECTION-COPY.md'), 'utf8');
  assert.match(draft, /<!-- RULES-B-COPY-START -->/);
  const object = draft.split('<!-- RULES-B-COPY-START -->')[1].split('<!-- RULES-B-COPY-END -->')[0];
  const source = fs.readFileSync(path.resolve(root, '../../../../../../keep-policy.md'), 'utf8');
  const excerpt = source.split('\n').slice(7, 21).join('\n').trim();
  assert.ok(object.includes(excerpt), 'All lines from first keep heading through Notifications must remain in source order');
  assert.match(draft, /8 set aside · alex@example\.com/);
  assert.match(draft, /five visible rows/);
});

for (const [name, mutate, error] of [
  ['extra Rules words fail the total budget', text => text.replace('<!-- RULES-B-COPY-END -->',
    'extra extra extra extra extra extra extra\n<!-- RULES-B-COPY-END -->'), /B: authored draft outside 350–550: 551/],
  ['missing Rules text fails rather than being silently uncounted', text => text.replace('<!-- RULES-B-COPY-START -->',
    '<!-- REMOVED-RULES-MARKER -->'), /Missing or duplicate RULES-B-COPY marker/],
]) {
  test(name, t => {
    const scratch = process.env.JCODE_SCRATCH_DIR;
    assert.ok(scratch, 'Set JCODE_SCRATCH_DIR for isolated count fixtures');
    const dir = fs.mkdtempSync(path.join(scratch, 'zero-draft-count-'));
    t.after(() => fs.rmSync(dir, { recursive: true, force: true }));
    fs.mkdirSync(path.join(dir, 'before'));
    fs.copyFileSync(path.join(root, 'count-section-drafts.mjs'), path.join(dir, 'count-section-drafts.mjs'));
    fs.copyFileSync(path.join(root, 'before/inventory.json'), path.join(dir, 'before/inventory.json'));
    fs.writeFileSync(path.join(dir, 'SECTION-COPY.md'), mutate(fs.readFileSync(path.join(root, 'SECTION-COPY.md'), 'utf8')));
    const run = spawnSync(process.execPath, [path.join(dir, 'count-section-drafts.mjs')], { encoding: 'utf8' });
    assert.notEqual(run.status, 0);
    assert.match(run.stderr, error);
  });
}
