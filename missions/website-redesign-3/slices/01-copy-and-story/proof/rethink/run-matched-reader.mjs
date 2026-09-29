import { spawnSync } from 'node:child_process';
import path from 'node:path';
import fs from 'node:fs';
import { fileURLToPath } from 'node:url';
const [phase, reader] = process.argv.slice(2);
if (!['before', 'after-a', 'after-b'].includes(phase) || !/^[123]$/.test(reader ?? '')) throw new Error('Usage: node run-matched-reader.mjs before|after-a|after-b 1|2|3');
const root = path.dirname(fileURLToPath(import.meta.url));
const base = path.join(root, phase);
const baselineImages = ['page-full-1440.jpg', 'page-full-390.jpg',
  'hero-b/hero-b-1440.jpg', 'sections/shots/demo-1440.jpg', 'sections/shots/decisions-1440.jpg',
  'sections/shots/undo-1440.jpg', 'sections/shots/before-1440.jpg', 'sections/shots/install-1440.jpg',
  'hero-b/hero-b-390.jpg', 'sections/shots/demo-390.jpg', 'sections/shots/decisions-390.jpg',
  'sections/shots/undo-390.jpg', 'sections/shots/before-390.jpg', 'sections/shots/install-390.jpg'];
const images = phase === 'before' ? baselineImages : JSON.parse(fs.readFileSync(path.join(base, 'reader-images.json')));
if (!Array.isArray(images) || images.length < 2 || images.some(file => typeof file !== 'string' || path.isAbsolute(file) || file.split('/').includes('..'))) throw new Error('Use a relative ordered image list inside the frozen phase snapshot');
const result = spawnSync(process.execPath, [path.join(root, 'run-isolated-reader.mjs'),
  path.join(root, 'readers', phase, `matched-${reader}`), path.join(root, 'reader-prompt.md'),
  path.join(base, 'PAGE-TEXT.txt'), ...images.map(file => path.join(base, file))], { stdio: 'inherit' });
process.exitCode = result.status ?? 1;
