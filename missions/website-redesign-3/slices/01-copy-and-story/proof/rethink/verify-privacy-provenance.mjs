import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
const root = path.dirname(fileURLToPath(import.meta.url));
const base = path.join(root, 'after-b-privacy');
const hash = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
const freeze = JSON.parse(fs.readFileSync(path.join(base, 'freeze.json')));
assert.equal(freeze.commit, execFileSync('git', ['rev-parse', '65463b8'], { encoding: 'utf8' }).trim());
assert.equal(freeze.authoredWords, 550);
const text = fs.readFileSync(path.join(base, 'PAGE-TEXT.txt'));
assert.equal(hash(text), freeze.textSha256);
assert.equal((text.toString().replace(/’/g, "'").match(/[\p{L}\p{N}]+(?:['.-][\p{L}\p{N}]+)*/gu) || []).length, 550);
for (const [file, metadata] of Object.entries(freeze.sourceHashes)) {
  const bytes = fs.readFileSync(path.join(base, file));
  assert.equal(hash(bytes), metadata.sha256, file);
  assert.equal(bytes.length, metadata.bytes, file);
  const gitBytes = execFileSync('git', ['show', `${freeze.commit}:${metadata.source}`], { maxBuffer: 16 * 1024 * 1024 });
  assert.equal(hash(gitBytes), metadata.sha256, file);
}
console.log(`PASS immutable Git/source/original-capture parity: ${freeze.commit}, ${Object.keys(freeze.sourceHashes).length} files, 550 authored words`);
const prompt = fs.readFileSync(path.join(root, 'reader-prompt.md'), 'utf8');
const ids = [];
for (let i = 1; i <= 3; i++) {
  const metadata = JSON.parse(fs.readFileSync(path.join(root, `readers/after-b-privacy/matched-${i}.metadata.json`)));
  assert.equal(metadata.requestedModel, 'claude-sonnet-5');
  assert.deepEqual(Object.keys(metadata.resultModelUsage), ['claude-sonnet-5']);
  assert.equal(metadata.exitCode, 0);
  assert.equal(metadata.numTurns, 1);
  assert.equal(metadata.isError, false);
  assert.equal(metadata.toolCalls, 0);
  assert.equal(metadata.sessionId, metadata.resultSessionId);
  ids.push(metadata.sessionId);
  assert(metadata.prompt.startsWith(prompt));
  assert(metadata.prompt.endsWith(text.toString()));
  assert.equal(metadata.media.length, 12);
  for (const media of metadata.media) {
    const bytes = fs.readFileSync(media.path);
    assert.equal(hash(bytes), media.sha256);
    assert.equal(bytes.length, media.bytes);
  }
  console.log(`PASS reader ${i}: requested/actual claude-sonnet-5, session ${metadata.sessionId}, one turn, zero tools, 12 image hashes/bytes, unchanged prompt and frozen text`);
}
assert.equal(new Set(ids).size, 3);
const publicEdges = JSON.parse(fs.readFileSync(path.join(root, 'acceptance/public-edges-privacy-b.json')));
assert.equal(publicEdges.sourceCommit, freeze.commit);
assert.equal(publicEdges.fail, 0);
console.log(`PASS source-matched public boundaries: ${publicEdges.pass} pass, ${publicEdges.fail} fail`);
console.log('PASS all privacy evidence checks. Initial ad hoc verifiers failed on guessed original-image source paths and default Git output buffer. This version uses manifest source paths and a sufficient read buffer.');
