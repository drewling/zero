import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';
const root = path.dirname(fileURLToPath(import.meta.url));
const repo = execFileSync('git', ['rev-parse', '--show-toplevel'], { encoding: 'utf8' }).trim();
const sha = execFileSync('git', ['rev-parse', process.argv[2] || 'cdfee91'], { encoding: 'utf8' }).trim();
const tightened = process.argv[3] === 'after-b-tightened';
if (process.argv[3] && !tightened) throw new Error('Only after-b-tightened is an additional freeze phase');
const comps = 'missions/website-redesign-3/slices/02-references-and-comps/proof/comps';
const require = createRequire(execFileSync('npm', ['root', '-g'], { encoding: 'utf8' }).trim() + '/');
const { chromium } = require('playwright');
const hash = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
const readGit = file => execFileSync('git', ['show', `${sha}:${file}`], { cwd: repo, maxBuffer: 30 * 1024 * 1024 });
const files = execFileSync('git', ['ls-tree', '-r', '--name-only', sha, comps], { encoding: 'utf8', cwd: repo }).trim().split('\n');
const browser = await chromium.launch();
try {
  for (const outline of tightened ? ['b'] : ['a', 'b']) {
    const phaseName = tightened ? 'after-b-tightened' : `after-${outline}`;
    const destination = path.join(root, phaseName);
    if (fs.existsSync(destination)) throw new Error(`Do not overwrite frozen evidence: ${destination}`);
    if (!process.env.JCODE_SCRATCH_DIR) throw new Error('JCODE_SCRATCH_DIR required for staged freeze');
    const phase = fs.mkdtempSync(path.join(process.env.JCODE_SCRATCH_DIR, `zero-freeze-${phaseName}-`));
    console.log(`Staging freeze at ${phase}. A failure retains this attempt, not a reader-ready snapshot.`);
    const hashes = {};
    const saveGit = (file, destination) => {
      const bytes = readGit(file); fs.mkdirSync(path.dirname(destination), { recursive: true }); fs.writeFileSync(destination, bytes);
      hashes[path.relative(phase, destination)] = { source: file, sha256: hash(bytes), bytes: bytes.length };
    };
    for (const file of files.filter(f => f.startsWith(`${comps}/kit/`) || f === `${comps}/page-${outline}/index.html`)) {
      saveGit(file, path.join(phase, 'source', path.relative(comps, file)));
    }
    for (const width of [320, 390, 1440, 1920]) saveGit(`${comps}/page-${outline}/shots/full-${width}.jpg`, path.join(phase, `original/full-${width}.jpg`));
    const layouts = {};
    let textNodes;
    for (const width of [1440, 390]) {
      const ctx = await browser.newContext({ viewport: { width, height: 900 } });
      const page = await ctx.newPage();
      const response = await page.goto(`http://127.0.0.1:8941/page-${outline}/?static`);
      const served = Buffer.from(await response.body());
      if (hash(served) !== hashes[`source/page-${outline}/index.html`].sha256) throw new Error('Served page differs from frozen Git source');
      for (const [file, evidence] of Object.entries(hashes).filter(([file]) => file.startsWith('source/kit/'))) {
        const result = await ctx.request.get(`http://127.0.0.1:8941/${file.slice('source/'.length)}`);
        if (!result.ok() || hash(await result.body()) !== evidence.sha256) throw new Error(`Served asset differs from frozen Git: ${file}`);
      }
      await page.evaluate(() => document.fonts.ready);
      const extraction = await page.evaluate(() => {
        const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT), nodes = [];
        for (let n; (n = walker.nextNode());) if (!n.parentElement.closest('svg,script,style,.draft-flag,.sr-only') && n.nodeValue.trim()) nodes.push(n.nodeValue.replace(/\s+/g, ' ').trim());
        return { nodes, sections: [...document.querySelectorAll('main section')].map(el => ({ id: el.id, top: el.getBoundingClientRect().top + scrollY, height: el.getBoundingClientRect().height })), height: document.documentElement.scrollHeight };
      });
      if (textNodes && JSON.stringify(textNodes) !== JSON.stringify(extraction.nodes)) throw new Error('Authored text changes across widths');
      textNodes = extraction.nodes; layouts[width] = extraction;
      await ctx.close();
    }
    const clipboardStates = [];
    if (tightened) {
      const selectedFile = 'missions/website-redesign-3/slices/01-copy-and-story/proof/rethink/SELECTED-B-COPY.md';
      saveGit(selectedFile, path.join(phase, 'SELECTED-B-COPY.md'));
      const selected = readGit(selectedFile).toString();
      const expected = selected.split('<!-- CLIPBOARD-COPY-START -->')[1].split('<!-- CLIPBOARD-COPY-END -->')[0].split('\n').map(s => s.trim()).filter(Boolean);
      for (const mode of ['success', 'denied']) {
        const ctx = await browser.newContext({ viewport: { width: 390, height: 900 } });
        await ctx.addInitScript(mode => Object.defineProperty(navigator, 'clipboard', { configurable: true, value: { writeText: async () => {
          if (mode === 'denied') throw new DOMException('Denied', 'NotAllowedError');
        } } }), mode);
        const page = await ctx.newPage(); await page.goto('http://127.0.0.1:8941/page-b/?static');
        await page.locator('#copy').click();
        await page.waitForFunction(() => document.querySelector('[role="status"],[aria-live="polite"]')?.textContent.trim());
        const status = await page.locator('[role="status"],[aria-live="polite"]').first().textContent();
        clipboardStates.push(status.trim()); await ctx.close();
      }
      if (JSON.stringify(clipboardStates) !== JSON.stringify(expected)) throw new Error('Rendered clipboard states differ from counted copy');
    }
    const text = [...textNodes, ...clipboardStates].join('\n') + '\n';
    const count = (text.replace(/’/g, "'").match(/[\p{L}\p{N}]+(?:['.-][\p{L}\p{N}]+)*/gu) || []).length;
    if (count !== (tightened ? 549 : outline === 'a' ? 474 : 544)) throw new Error(`Unexpected full authored count ${outline}: ${count}`);
    fs.writeFileSync(path.join(phase, 'PAGE-TEXT.txt'), text);
    fs.writeFileSync(path.join(phase, 'layout.json'), JSON.stringify(layouts, null, 2) + '\n');
    fs.writeFileSync(path.join(phase, 'freeze.json'), JSON.stringify({ commit: sha, frozenAt: new Date().toISOString(), sourceHashes: hashes, textSha256: hash(text), authoredWords: count,
      exclusions: ['author-only draft flag', 'screen-reader-only hero description duplicates illustrated content', 'SVG, scripts, styles and document title'],
      clipboardStates,
      includes: ['one header and footer', 'all hero states including Working…', 'hidden mobile subjects', 'all editor lines even if clipped', 'object dates, row ages, fictional addresses and labels', ...(tightened ? ['all clipboard statuses observed through success/denial fault paths'] : [])] }, null, 2) + '\n');
    execFileSync('python3', [path.join(root, 'prepare-reader-images.py'), phase], { stdio: 'inherit' });
    fs.renameSync(phase, destination);
    console.log(`Frozen ${phaseName}: ${count} authored words, ${sha}`);
  }
} finally { await browser.close(); }
