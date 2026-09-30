import test from 'node:test';
import assert from 'node:assert/strict';
import { clipboardOutcome } from './clipboard-outcome.mjs';
const command = 'curl -fsSL https://zero.headless.com/install | bash';
const context = { resources: [], errors: [], sectionScriptLoaded: true };
const unavailable = { hidden: true, command };
test('unavailable clipboard cannot pass when section script did not load', () => {
 assert.equal(clipboardOutcome('unavailable', unavailable, command, { ...context, sectionScriptLoaded: false }), false);
});
test('any resource failure or runtime error fails a clipboard fault context', () => {
 assert.equal(clipboardOutcome('unavailable', unavailable, command, { ...context, resources: ['reset'] }), false);
 assert.equal(clipboardOutcome('unavailable', unavailable, command, { ...context, errors: ['ReferenceError'] }), false);
});
test('completed unavailable state keeps the exact command selectable', () => {
 assert.equal(clipboardOutcome('unavailable', unavailable, command, context), true);
 assert.equal(clipboardOutcome('unavailable', { ...unavailable, command: 'different' }, command, context), false);
});
test('success requires the exact clipboard content, announced success and retained focus', () => {
 const result = { written: command, status: 'Copied', focused: 'copy' };
 assert.equal(clipboardOutcome('success', result, command, context), true);
 assert.equal(clipboardOutcome('success', { ...result, written: 'different' }, command, context), false);
});
test('denial requires exact selection, announced fallback and retained focus', () => {
 const result = { selection: command, status: 'Copy manually: press Command-C.', focused: 'copy' };
 assert.equal(clipboardOutcome('denied', result, command, context), true);
 assert.equal(clipboardOutcome('denied', { ...result, focused: '' }, command, context), false);
});
