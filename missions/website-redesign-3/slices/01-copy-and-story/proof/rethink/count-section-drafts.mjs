import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const root = path.dirname(fileURLToPath(import.meta.url));
const draft = fs.readFileSync(path.join(root, 'SECTION-COPY.md'), 'utf8');
const block = name => {
  const start = `<!-- ${name}-START -->`;
  const end = `<!-- ${name}-END -->`;
  if (draft.split(start).length !== 2 || draft.split(end).length !== 2) throw new Error(`Missing or duplicate ${name} marker`);
  return draft.split(start)[1].split(end)[0];
};
const visible = text => text.replace(/\[([^\]]+)\]\([^)]+\)/g, '$1').replace(/```sh|```/g, '');
const words = text => (visible(text).match(/[\p{L}\p{N}]+(?:[’'.-][\p{L}\p{N}]+)*/gu) ?? []).length;
const inventory = JSON.parse(fs.readFileSync(path.join(root, 'before/inventory.json')));
const frozenHeroWords = words(inventory.hero.textNodes.join('\n'));
const actorDelta = words('zero Run zero now Working…');
const hero = frozenHeroWords + actorDelta;
const objectWords = words(block('OBJECT-COPY'));
const rulesObjectWords = words(block('RULES-B-COPY'));
const banned = ['open loops', "who's waiting", "who’s waiting", "who's writing", "who’s writing", 'ball is in their court', 'check it with your coffee', 'two questions', 'set something aside', 'agent cli', 'jev model reads each thread'];
const output = ['A', 'B'].map(outline => {
  const text = visible(block(`COPY-${outline}`));
  for (const phrase of banned) if (text.toLowerCase().includes(phrase)) throw new Error(`${outline}: banned explanation ${phrase}`);
  if (!text.includes('curl -fsSL https://zero.headless.com/install | bash')) throw new Error(`${outline}: missing exact command`);
  const primary = words(text);
  const rules = outline === 'B' ? rulesObjectWords : 0;
  const total = hero + primary + objectWords + rules;
  if (total > 550 || total < 350) throw new Error(`${outline}: authored draft outside 350–550: ${total}`);
  return { outline, hero, primarySections: primary, sharedObjects: objectWords, rulesObjectWords: rules, authoredTotal: total,
    pendingRulesObject: false, finalRenderedInventoryChecked: false, proseBanHits: 0 };
});
console.log(JSON.stringify(output, null, 2));
console.log('Authored Draft3 only, including the proposed Rules object. Any added comp strings and actual rendered inventory must be checked before final signoff. Actual Open loops tab is UI nomenclature, not banned prose.');
