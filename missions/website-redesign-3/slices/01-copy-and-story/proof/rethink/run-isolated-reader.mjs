import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { spawn } from 'node:child_process';

// Explicit one-turn screenshot/copy test, not a persistent peer or a resumed session.
const [outputPrefix, promptFile, copyFile, ...images] = process.argv.slice(2);
if (!outputPrefix || !promptFile || !copyFile || !images.length || !process.env.JCODE_SCRATCH_DIR) {
  throw new Error('Usage: node run-isolated-reader.mjs output-prefix prompt-file full-copy-file image... (set JCODE_SCRATCH_DIR)');
}
const system = 'You are a first-time visitor with no prior knowledge of this product, its author, or their accounts. Use only the supplied user text and attached images. Answer the requested critique directly. Do not call tools or invent capabilities.';
const text = fs.readFileSync(promptFile, 'utf8') + '\n\nFULL PAGE TEXT, IN ORDER:\n' + fs.readFileSync(copyFile, 'utf8');
const sessionId = crypto.randomUUID();
const content = [{ type: 'text', text }];
const media = images.map((file, index) => {
  const bytes = fs.readFileSync(file);
  const mediaType = /\.png$/i.test(file) ? 'image/png' : 'image/jpeg';
  content.push({ type: 'text', text: `Screenshot ${index + 1}` });
  content.push({ type: 'image', source: { type: 'base64', media_type: mediaType, data: bytes.toString('base64') } });
  return { path: path.resolve(file), sha256: crypto.createHash('sha256').update(bytes).digest('hex'), bytes: bytes.length };
});
const output = path.resolve(outputPrefix);
if (['.jsonl', '.metadata.json', '.answer.md'].some(suffix => fs.existsSync(output + suffix))) {
  throw new Error(`Retain prior reader evidence: use a new output prefix, not ${output}`);
}
fs.mkdirSync(path.dirname(output), { recursive: true });
const cwd = fs.mkdtempSync(path.join(process.env.JCODE_SCRATCH_DIR, 'zero-blind-reader-'));
const args = ['-p', '--model', 'claude-sonnet-5', '--session-id', sessionId,
  '--system-prompt', system, '--setting-sources', '', '--tools', '',
  '--strict-mcp-config', '--mcp-config', '{"mcpServers":{}}',
  '--disable-slash-commands', '--no-session-persistence', '--no-chrome',
  '--input-format', 'stream-json', '--output-format', 'stream-json', '--verbose'];
const start = new Date().toISOString();
const child = spawn('claude', args, { cwd, env: { ...process.env, CLAUDE_CODE_DISABLE_AUTO_MEMORY: '1' }, stdio: ['pipe', 'pipe', 'pipe'] });
const raw = fs.createWriteStream(output + '.jsonl');
const errors = fs.createWriteStream(output + '.stderr.txt');
let stdout = '';
child.stdout.on('data', chunk => { stdout += chunk.toString(); raw.write(chunk); });
child.stderr.on('data', chunk => errors.write(chunk));
const timeout = setTimeout(() => child.kill('SIGTERM'), 300000);
child.stdin.end(JSON.stringify({ type: 'user', session_id: sessionId,
  parent_tool_use_id: null, message: { role: 'user', content } }) + '\n');
child.on('error', error => { clearTimeout(timeout); throw error; });
child.on('close', code => {
  clearTimeout(timeout);
  raw.end(); errors.end();
  const records = stdout.trim().split('\n').filter(Boolean).map(line => JSON.parse(line));
  const result = records.findLast(row => row.type === 'result');
  const toolCalls = records.flatMap(row => row.message?.content ?? []).filter(row => row.type === 'tool_use');
  const metadata = { start, finish: new Date().toISOString(), cwd, requestedModel: 'claude-sonnet-5',
    sessionId, args, system, prompt: text, media, exitCode: code,
    resultSessionId: result?.session_id, resultModelUsage: result?.modelUsage,
    numTurns: result?.num_turns, isError: result?.is_error, toolCalls: toolCalls.length };
  fs.writeFileSync(output + '.metadata.json', JSON.stringify(metadata, null, 2) + '\n');
  if (code !== 0 || !result || result.is_error || result.num_turns !== 1 || toolCalls.length || result.session_id !== sessionId || !Object.keys(result.modelUsage ?? {}).every(model => model === 'claude-sonnet-5') || !Object.keys(result.modelUsage ?? {}).length) {
    console.error(`Reader failed isolation/result checks: ${output}`);
    process.exitCode = 1;
    return;
  }
  fs.writeFileSync(output + '.answer.md', result.result + '\n');
  console.log(`JCODE_PROGRESS ${JSON.stringify({ label: path.basename(output), status: 'complete', sessionId: result.session_id })}`);
});
