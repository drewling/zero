#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';

const dir = path.dirname(fileURLToPath(import.meta.url));
const copy = fs.readFileSync(path.join(dir, 'COPY.md'), 'utf8');
const primary = copy.split('<!-- PAGE-COPY-START -->')[1].split('<!-- PAGE-COPY-END -->')[0];
const tokens = text => (text.replace(/```sh|```/g, '').match(/[\p{L}\p{N}]+(?:[’'.-][\p{L}\p{N}]+)*/gu) || []).length;
const bold = text => [...text.matchAll(/\*\*([^*]+)\*\*/g)].map(match => match[1]).join('\n');
const panel = copy.split('## Hero panel content')[1].split('## Demo and window strings')[0];
const panelLines = panel.split('\n').filter(line => /^- (Count|Supporting line|List label|Four fictional rows|Action label)/.test(line));
const demo = copy.split('## Demo and window strings')[1].split('## Navigation, footer')[0];
const demoRows = demo.split('\n').filter(line => /^\| (Stays|Archived) \|/.test(line)).map(line => line.split('|').slice(2, 4).join(' '));
const titles = demo.match(/Plain window titles: \*\*([^*]+)\*\*/)[1];
const chrome = demo.match(/Keep extra demonstration chrome within this budget: \*\*([^*]+)\*\*/)[1];
const heroChrome = demo.match(/Extra hero\/motion chrome is \*\*([^*]+)\*\*/)[1];
const nav = copy.match(/Visible navigation: \*\*([^*]+)\*\*/)[1];
const footer = copy.match(/Visible footer: \*\*([^*]+)\*\*/)[1];
const counts = {
  primary: tokens(primary),
  heroPanel: tokens(bold(panelLines.join('\n'))),
  demoRows: tokens(demoRows.join('\n')),
  lastReplyAnnotation: tokens('Last reply: you'),
  windowTitles: tokens(titles),
  extraChrome: tokens(chrome),
  heroMotionChrome: tokens(heroChrome),
  navigation: tokens(nav),
  footer: tokens(footer),
  siteBrand: tokens('zero'),
};
const total = Object.values(counts).reduce((a, b) => a + b, 0);

if (process.argv.includes('--cold-reader')) {
  console.log('# Cold-reader comprehension test\n');
  console.log('Date: 2026-09-29 UTC. Criterion: every reader must describe a Mac app that cleans/manages a Gmail inbox. Model replies are not human usability research or proof of a literal five-second reading time. All nine calls were single-turn, newly created sessions of `claude-sonnet-5`, with no prior conversation resumed. The JSON result files retain actual model ids, session ids, token counts and verbatim replies.\n');
  console.log('## Results and iteration\n\n| Round | Copy | Reader 1 | Reader 2 | Reader 3 | Acceptance |\n|---|---|---|---|---|---|\n| 1 | V1 | Category PASS | Category PASS | FAIL: omitted Mac | FAIL, and invalid isolation |\n| 2 | V2 | Category PASS | Category PASS | Category PASS | Invalid isolation, not accepted |\n| 3 | V2 excerpt unchanged in V3 | PASS | PASS | PASS | Accepted: 3/3 |\n');
  console.log('V1 readers inferred continuous unattended operation, and one did not name Mac. V2 put Mac in the headline and named the manual Run zero now action. Round 2 reader 1 also named an account not supplied in the prompt. That demonstrates unwanted context in the test harness, not a copy result. Both earlier rounds therefore remain in this record but are not accepted as context-free proof.\n');
  console.log('Round 3 used a dedicated empty scratch working directory, an explicit replacement system prompt, disabled auto-memory, an empty setting-source list, no tools, empty strict MCP configuration, disabled skills and no session persistence. The returned usage lists 717 input tokens per reader. No tool calls, denials or extra turns were reported, and no unrelated account/product context appears in the answers. This is stronger practical isolation, not a forensic assertion about all internals of the CLI.\n');
  console.log('Replacement system prompt:\n\n```text\nYou are a first-time visitor with no knowledge of the product or the person requesting this test. Use only the text in the user message. Answer their comprehension questions in plain words. Do not invent product capabilities.\n```\n');
  console.log('Round 3 invocation (run three independent times; no resume flag):\n\n```sh\nCLAUDE_CODE_DISABLE_AUTO_MEMORY=1 claude -p --model claude-sonnet-5 \\\n  --system-prompt "<replacement prompt above>" --setting-sources "" \\\n  --tools "" --strict-mcp-config --mcp-config \'{"mcpServers":{}}\' \\\n  --disable-slash-commands --no-session-persistence --output-format json \\\n  < cold-reader-round2-prompt.txt\n```\n');
  const rounds = [
    { n: 1, prompt: 'cold-reader-prompt.txt', prefix: 'cold-reader-', note: 'Not accepted. Strict category scores were 2/3 and this harness was later shown to carry unrelated context.' },
    { n: 2, prompt: 'cold-reader-round2-prompt.txt', prefix: 'cold-reader-r2-', note: 'Not accepted. All three named Mac and Gmail inbox triage, but reader 1 exposed unrelated account context.' },
    { n: 3, prompt: 'cold-reader-round2-prompt.txt', prefix: 'cold-reader-r3-', note: 'Accepted. Every reader names a Mac app, Gmail inbox sorting, reversible archives and the manual run action.' },
  ];
  for (const round of rounds) {
    console.log(`## Round ${round.n}\n\n${round.note}\n\n### User prompt, verbatim\n\n\`\`\`text\n${fs.readFileSync(path.join(dir, round.prompt), 'utf8').trimEnd()}\n\`\`\`\n`);
    for (let i = 1; i <= 3; i++) {
      const name = `${round.prefix}${i}.json`;
      const result = JSON.parse(fs.readFileSync(path.join(dir, name), 'utf8'));
      console.log(`### Reader ${i}\n\nModel: \`${Object.keys(result.modelUsage).join(', ')}\`. Session: \`${result.session_id}\`. Raw evidence: [${name}](${name}). Turns: ${result.num_turns}. Error: ${result.is_error}.\n\nAnswer below is verbatim, including mistaken assumptions in invalid rounds:\n\n\`\`\`text\n${result.result}\n\`\`\`\n`);
    }
  }
  console.log('## Concerns carried into the rest of the page\n\nReaders consistently asked about errors, email access/data flow, undo scope and costs. The later sections already answer these with editable rules and a model-mistake warning, starred/uncertain protection, individual/day restore, explicit sorting/draft data disclosure, and own-provider costs. We do not put every concern into the hero. This test stops at the first demonstration, as the SPEC requests. V3 only shortens later sections and adds illustration strings outside the tested excerpt. Later independent QA must repeat the test on the built page.\n');
  // A piped stdout can still have queued report bytes after console.log.
  await new Promise(resolve => process.stdout.write('', resolve));
  process.exit(0);
}

console.log('COPY v3 mechanical proof, 2026-09-29 UTC');
console.log('Counter: Unicode letter/number tokens, internal apostrophes/dots/hyphens retained. Markdown, arrows and ornamental separators excluded. Repeated hero/demo rows and controls count again.');
for (const [key, value] of Object.entries(counts)) console.log(`${key}: ${value}`);
console.log(`visible total: ${total}`);
if (total < 350 || total > 550) throw new Error(`Word budget failed: ${total}`);
console.log('Word budget 350–550: PASS');

const phrases = ['open loops', "who's waiting", "who's writing", 'who’s waiting', 'who’s writing', 'ball is in their court', 'Check it with your coffee', 'Two questions', 'set something aside', 'agent CLI', 'Jev model reads each thread'];
for (const phrase of phrases) {
  const result = spawnSync('grep', ['-Fin', '--', phrase, path.join(dir, 'COPY.md')], { encoding: 'utf8' });
  if (![0, 1].includes(result.status)) throw new Error(result.stderr);
  const hits = result.status === 1 ? 0 : result.stdout.trim().split('\n').length;
  console.log(`grep -Fin '${phrase}' COPY.md: ${hits} hits`);
  if (hits) throw new Error(`Banned wording found: ${phrase}`);
}
const normalize = text => text.replace(/[*#]/g, '').replace(/\s+/g, ' ').trim();
const prompt = fs.readFileSync(path.join(dir, 'cold-reader-round2-prompt.txt'), 'utf8').split('What does this product do')[0];
for (const paragraph of prompt.trim().split(/\n\s*\n/)) {
  if (!normalize(primary).includes(normalize(paragraph))) throw new Error('Tested excerpt differs from final copy');
}
console.log('Accepted cold-reader excerpt unchanged in COPY v3: PASS');
const sessions = new Set();
for (let i = 1; i <= 3; i++) {
  const result = JSON.parse(fs.readFileSync(path.join(dir, `cold-reader-r3-${i}.json`), 'utf8'));
  if (result.is_error || result.num_turns !== 1 || !result.result.match(/Mac app/i) || !result.result.match(/Gmail/i) || !result.result.match(/inbox/i)) throw new Error('Cold-reader acceptance failed');
  sessions.add(result.session_id);
}
if (sessions.size !== 3) throw new Error('Readers are not distinct sessions');
console.log('Three distinct successful single-turn Mac/Gmail/inbox readers: PASS');
for (const file of ['COPY.md', 'OUTLINE.md', 'comparables.md', 'truth-trace.md', 'cold-reader.md', 'design-review.md']) {
  if (!fs.existsSync(path.join(dir, file))) throw new Error(`Missing proof: ${file}`);
}
for (const name of ['sanebox', 'superhuman', 'shortwave', 'hey', 'sparkmail', 'clean-email']) {
  const file = fs.readFileSync(path.join(dir, 'comparables', `${name}-first-viewport.png`));
  if (file.subarray(1, 4).toString() !== 'PNG' || file.readUInt32BE(16) !== 2880 || file.readUInt32BE(20) !== 1800) throw new Error('Bad screenshot');
}
console.log('Six retained research screenshots: PASS');
console.log('Required authored proof files exist: PASS');
