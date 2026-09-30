'use strict';

(function () {
  const root = document.body;
  const query = new URLSearchParams(location.search);
  if (query.has('static')) document.documentElement.classList.add('static');

  const routine = () => [...root.querySelectorAll('#inbox li.g')];
  const folder = root.querySelector('.folder');
  if (!folder || !window.Zm) return;

  const replay = root.querySelector('#replay');
  const shownIcon = () => [...folder.querySelectorAll('svg')].find((el) => el.getClientRects().length);
  const source = { sel: () => routine()[0], fx: .35, fy: .5 };
  const destination = { sel: () => query.has('fault') ? null : shownIcon(), fx: .6, fy: .5 };
  const clear = () => {
    routine().forEach((row) => { row.classList.remove('sel'); row.style.visibility = ''; });
    folder.classList.remove('got', 'over', 'sel');
  };
  const selectAll = () => routine().forEach((row) => row.classList.add('sel'));
  const pulse = async (element, z, ms) => {
    if (!element) return;
    element.classList.add('pressed');
    try { await z.wait(ms); } finally { element.classList.remove('pressed'); }
  };
  const story = {
    onLoad: true,
    delay: 600,
    cursorMinWidth: 760,
    replay,
    maxMs: query.has('deadline') ? Math.max(1, Number(query.get('deadline')) || 6000) : 6000,
    finish: () => { clear(); folder.classList.add('sel'); },
    frames: [
      { set: clear },
      {
        hold: 450,
        enter: (r, z) => z.zoom(r, '.tray', '.zp', { steps: 5, ms: 240 }),
        still: (r, z) => z.zoom(r, '.tray', '.zp', { steps: 3, still: true }),
      },
      { cursor: { sel: '.zp-run', fx: .5, fy: .55 }, kind: 'watch', hold: 420,
        enter: (r, z) => pulse(r.querySelector('.zp-run'), z, 80) },
      {
        cursor: source,
        kind: 'watch',
        cursorSteps: 6,
        cursorMs: 320,
        hold: 250,
        enter: async (r, z) => {
          for (const row of routine()) { row.classList.add('sel'); await z.wait(70); }
        },
        still: selectAll,
      },
      {
        cursor: source,
        kind: 'watch',
        hold: 260,
        set: selectAll,
        enter: async (r, z) => {
          folder.classList.add('over');
          await z.drag(r, routine, destination, { steps: 7, ms: 560, cursorFrom: source, layer: 2 });
          routine().forEach((row) => { row.style.visibility = 'hidden'; });
          folder.classList.remove('over');
          folder.classList.add('got', 'sel');
          await pulse(folder, z, 80);
          await z.wait(80);
          await pulse(folder, z, 80);
        },
        still: (r, z) => {
          folder.classList.add('over');
          return z.drag(r, routine, destination, { still: .5, cursorFrom: source, layer: 2 });
        },
      },
      { set: () => story.finish(), hold: 0 },
    ],
  };

  window.story = story;
  window.controller = Zm.when(root, story);
  if (replay) replay.addEventListener('click', () => Zm.play(root, story));
})();
