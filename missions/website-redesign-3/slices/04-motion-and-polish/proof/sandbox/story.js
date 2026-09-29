/* Data is deliberately separate from the runner: gate B may pick another hero. */
(function () {
  const root = document.querySelector('#story');
  const count = root.querySelector('#count');
  const label = root.querySelector('#run-label');
  const rows = [...root.querySelectorAll('.archive-row')];
  const folder = root.querySelector('.folder');
  const tray = root.querySelector('#replay');
  const q = new URLSearchParams(location.search);
  const hide = n => rows.forEach((row, i) => { row.style.visibility = i < n ? 'hidden' : ''; });
  const from = { sel: () => innerWidth >= 760 ? rows.find(row => getComputedStyle(row).visibility !== 'hidden') : count, fx: .5 };
  const destination = { sel: () => [...folder.querySelectorAll('svg')].find(el => el.getClientRects().length), fy: .45 };
  const story = {
    onLoad: true, delay: 700, cursorMinWidth: 760, replay: tray,
    finish: () => { hide(8); count.textContent = '4'; label.textContent = 'Run zero now'; folder.classList.remove('got'); },
    frames: [
      { cursor: { sel: '#replay', dx: -120, dy: 140 }, set: () => { hide(0); count.textContent = '12'; label.textContent = 'Run zero now'; folder.classList.remove('got'); } },
      { cursor: { sel: '#replay' }, cursorSteps: 6, cursorMs: 300, hold: 250,
        enter: (r, z) => z.zoom(r, q.has('fault') ? '#missing-target' : '#replay', '#panel', { steps: 5, ms: 240 }),
        still: (r, z) => z.zoom(r, '#replay', '#panel', { still: true, steps: 3 }) },
      { cursor: { sel: '.zp-run' }, kind: 'watch', cursorSteps: 7, cursorMs: 380, hold: 350,
        set: () => { label.textContent = 'Working…'; } },
      { cursor: { sel: '.zp-run' }, kind: 'watch', hold: 200,
        enter: (r, z) => z.hop(r, from, destination, { n: 8, steps: 5, ms: 170, gap: 120, lift: 70,
          onLaunch: i => { rows[i].style.visibility = 'hidden'; },
          onEach: i => { count.textContent = String(11 - i); folder.classList.add('got'); } }),
        still: (r, z) => { hide(4); count.textContent = '8'; folder.classList.add('got'); z.hopStill(r, from, destination, [.3, .7], 70); } },
      { cursor: { sel: '.zp-rows li:first-child', fy: 1.35 }, cursorSteps: 5, cursorMs: 220, hold: 0,
        set: () => story.finish() }
    ]
  };
  window.story = story;
  window.controller = Zm.when(root, story);
  // Real button supports Enter and Space. Runner ignores concurrent starts.
  tray.addEventListener('click', () => Zm.play(root, story));
})();
