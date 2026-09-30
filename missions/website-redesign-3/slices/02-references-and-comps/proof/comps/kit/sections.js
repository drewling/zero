/* Section beats for page-a / page-b (MOTION-SPEC §5). One stepped, one-bit beat per section, on the Zm runner.
   The HTML is the final frame. These stories only describe earlier frames, and every hidden part keeps its space
   (visibility, never display), so no beat moves the page. Reduced motion and no JS: the final frame, nothing plays.
   A section already on screen at first sight (an anchor jump, a reload mid-page) stays final (motion.js when()). */
(function () {
  const $$ = (r, s) => [...r.querySelectorAll(s)];
  const hide = els => els.forEach(e => e.classList.add('stepping'));
  const show = els => els.forEach(e => e.classList.remove('stepping'));
  const reveal = async (els, z, ms, per = 1) => { for (let i = 0; i < els.length; i += per) { show(els.slice(i, i + per)); await z.wait(ms); } };

  /* Undo: the day's batch is collapsed · it expands and its 5 rows step in · the balloon names the put-back button */
  const undo = document.getElementById('undo-win');
  if (undo) Zm.when(undo, { delay: 350, frames: [
    {},
    { hold: 380, set: r => show($$(r, '.urows li')),
      enter: (r, z) => { const li = $$(r, '.urows li'); hide(li); return reveal(li, z, 80); } },
    { hold: 0 }
  ]});

  /* Rules: zero's tabs step from Open loops to Settings · the Rules pane draws, policy lines stepping in */
  const rules = document.getElementById('rules-win');
  if (rules) {
    const tab = k => $$(rules, '.tabs span').forEach((s, i) => s.classList.toggle('on', i === k));
    Zm.when(rules, { delay: 350, frames: [
      { set: () => tab(0) },
      { hold: 160, enter: async (r, z) => { for (const k of [1, 2, 3]) { await z.wait(170); tab(k); } }, still: () => tab(3) },
      { hold: 0, set: r => { tab(3); show($$(r, '.editor .ln')); },
        enter: (r, z) => { const ln = $$(r, '.editor .ln'); hide(ln); return reveal(ln, z, 45, 2); } }
    ]});
  }

  /* Ledger: zero's app icon is selected · Get Info zooms out of it · the five rows fill in, one at a time */
  const ledger = document.querySelector('.ledger');
  if (ledger) Zm.when(ledger, { delay: 300, frames: [
    {},
    { hold: 120, enter: (r, z) => z.zoom(r, '.appicon svg', '.info', { steps: 6, ms: 300 }),
      still: (r, z) => z.zoom(r, '.appicon svg', '.info', { still: true, steps: 3 }) },
    { hold: 0, set: r => show($$(r, '.info .row')),
      enter: (r, z) => { const rows = $$(r, '.info .row'); hide(rows); return reveal(rows, z, 110); } }
  ]});

  /* Terminal: the command types in, two characters a step, then the block cursor blinks 3 times and rests */
  const term = document.getElementById('term');
  if (term) {
    const code = term.querySelector('code'), full = code.textContent;
    const typed = n => { code.innerHTML = ''; const a = document.createElement('span'), c = document.createElement('span'), b = document.createElement('span');
      a.textContent = full.slice(0, n); c.className = 'tcur'; b.className = 'stepping'; b.textContent = full.slice(n); code.append(a, c, b); };
    Zm.when(term, { delay: 250, frames: [
      { set: () => typed(0) },
      { hold: 0, set: () => { code.textContent = full; term.classList.add('blink'); },
        enter: async (r, z) => { for (let n = 0; n <= full.length; n += 2) { typed(n); await z.wait(28); } code.textContent = full; },
        still: () => typed(24) }
    ]});
    /* Copy: the button ships hidden and is shown only where the clipboard API exists, so no JS or no API leaves just
       the selectable command. Success and denial are both said in a polite live region and shown on screen.
       On denial the command is selected for Command-C and focus stays on the button. Strings: copywriter, approved. */
    const btn = document.getElementById('copy'), status = document.getElementById('copy-status');
    if (btn && status && window.isSecureContext && navigator.clipboard && navigator.clipboard.writeText) {
      btn.hidden = false; let t;
      btn.addEventListener('click', async () => {
        clearTimeout(t); status.textContent = '';
        try {
          await navigator.clipboard.writeText(full);
          status.textContent = 'Copied'; btn.classList.add('hit');
          t = setTimeout(() => { status.textContent = ''; btn.classList.remove('hit'); }, 4000);
        } catch (_) {
          const code = term.querySelector('code'), range = document.createRange(), sel = getSelection();
          range.selectNodeContents(code); sel.removeAllRanges(); sel.addRange(range);
          status.textContent = 'Copy manually: press Command-C.';
        }
      });
    }
  }
})();
