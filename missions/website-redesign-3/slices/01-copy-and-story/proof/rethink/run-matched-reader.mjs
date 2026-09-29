import { spawnSync } from 'node:child_process';
import path from 'node:path';
const [phase, reader] = process.argv.slice(2);
if (!['before', 'after'].includes(phase) || !/^[123]$/.test(reader ?? '')) throw new Error('Usage: node run-matched-reader.mjs before|after 1|2|3');
const root = path.dirname(new URL(import.meta.url).pathname);
const base = path.join(root, phase);
const images = ['page-full-1440.jpg', 'page-full-390.jpg',
  'hero-b/hero-b-1440.jpg', 'sections/shots/demo-1440.jpg', 'sections/shots/decisions-1440.jpg',
  'sections/shots/undo-1440.jpg', 'sections/shots/before-1440.jpg', 'sections/shots/install-1440.jpg',
  'hero-b/hero-b-390.jpg', 'sections/shots/demo-390.jpg', 'sections/shots/decisions-390.jpg',
  'sections/shots/undo-390.jpg', 'sections/shots/before-390.jpg', 'sections/shots/install-390.jpg'];
const result = spawnSync(process.execPath, [path.join(root, 'run-isolated-reader.mjs'),
  path.join(root, 'readers', phase, `matched-${reader}`), path.join(root, 'reader-prompt.md'),
  path.join(base, 'PAGE-TEXT.txt'), ...images.map(file => path.join(base, file))], { stdio: 'inherit' });
process.exitCode = result.status ?? 1;
