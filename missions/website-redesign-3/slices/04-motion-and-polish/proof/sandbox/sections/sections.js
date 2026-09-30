/* Selected page B section contracts: e58ff8f, reference 39aa729.
   Every story owns a complete finalizer, including interruption/error paths.
   The markup is final. No dependencies, wording assumptions or animated layout. */
(function () {
  const $$ = (r, s) => [...r.querySelectorAll(s)];
  const hide = els => els.forEach(e => e.classList.add('stepping'));
  const show = els => els.forEach(e => e.classList.remove('stepping'));
  const reveal = async (els, z, ms, per = 1) => {
    for (let i = 0; i < els.length; i += per) { show(els.slice(i, i + per)); await z.wait(ms); }
  };
  const ledger = document.querySelector('.ledger');
  if (ledger) Zm.when(ledger, { delay: 300,
    finish: r => show($$(r, '.info .row')),
    frames: [ {},
      { hold: 120, enter: (r, z) => z.zoom(r, '.appicon svg', '.info', { steps: 6, ms: 300 }),
        still: (r, z) => z.zoom(r, '.appicon svg', '.info', { still: true, steps: 3 }) },
      { hold: 0, set: r => show($$(r, '.info .row')),
        enter: (r, z) => { const rows = $$(r, '.info .row'); hide(rows); return reveal(rows, z, 110); } }
    ] });
  const rules = document.getElementById('rules-win');
  if (rules) {
    const tab = k => $$(rules, '.tabs span').forEach((s, i) => s.classList.toggle('on', i === k));
    Zm.when(rules, { delay: 350,
      finish: r => { tab(3); show($$(r, '.editor .ln')); },
      frames: [ { set: () => tab(0) },
        { hold: 160, enter: async (r, z) => { for (const k of [1, 2, 3]) { await z.wait(170); tab(k); } }, still: () => tab(3) },
        { hold: 0, set: r => { tab(3); show($$(r, '.editor .ln')); },
          enter: (r, z) => { const lines = $$(r, '.editor .ln'); hide(lines); return reveal(lines, z, 45, 2); } }
      ] });
  }
  const undo = document.getElementById('undo-win');
  if (undo) Zm.when(undo, { delay: 350,
    finish: r => show($$(r, '.urows li')),
    frames: [ {},
      { hold: 380, set: r => show($$(r, '.urows li')),
        enter: (r, z) => { const rows = $$(r, '.urows li'); hide(rows); return reveal(rows, z, 80); } },
      { hold: 0 }
    ] });
  const term = document.getElementById('term');
  if (term) {
    const code = term.querySelector('code'), full = code.textContent;
    const pre = code.closest('pre'); let glyphs, caret, positions;
    const clearTyping = () => {
      pre.querySelectorAll('[data-zm-overlay]').forEach(e => e.remove());
      code.classList.remove('typing'); glyphs = null; caret = null;
    };
    const typed = n => {
      if (!glyphs) {
        // Read the real complete command's line wrapping once before any writes.
        const box = pre.getBoundingClientRect(), text = code.firstChild, range = document.createRange();
        positions = [...full].map((c, i) => {
          range.setStart(text, i); range.setEnd(text, i + 1); const rect = range.getBoundingClientRect();
          return { x: Math.round(rect.left - box.left), y: Math.round(rect.top - box.top), w: rect.width };
        });
        const sprite = name => {
          const e = document.createElement('span'); e.className = name;
          e.setAttribute('data-zm-overlay', ''); e.setAttribute('aria-hidden', 'true'); pre.append(e); return e;
        };
        glyphs = [...full].map((c, i) => { const e = sprite('typed-letter'); e.textContent = c;
          e.style.transform = `translate(${positions[i].x}px,${positions[i].y}px)`; return e; });
        caret = sprite('tcur'); code.classList.add('typing');
      }
      glyphs.forEach((e, i) => e.classList.toggle('stepping', i >= n));
      const p = positions[Math.min(n, positions.length - 1)];
      caret.style.transform = `translate(${Math.round(p.x + (n >= full.length ? p.w : 0))}px,${p.y}px)`;
    };
    const terminal = Zm.when(term, { delay: 250,
      finish: (r, z, mode) => { clearTyping(); term.classList.toggle('blink', mode === 'done'); },
      frames: [ { set: () => typed(0) },
        { hold: 0, set: () => { clearTyping(); },
          enter: async (r, z) => { for (let n = 0; n <= full.length; n += 2) { typed(n); await z.wait(28); } clearTyping(); },
          still: () => typed(24) }
      ] });
    const btn = document.getElementById('copy'), status = document.getElementById('copy-status');
    if (btn && status && window.isSecureContext && typeof navigator.clipboard?.writeText === 'function') {
      btn.hidden = false; let timer, pending = false;
      btn.addEventListener('click', async () => {
        if (pending) return;
        pending = true; clearTimeout(timer); status.textContent = ''; btn.classList.remove('hit');
        try {
          await navigator.clipboard.writeText(full);
          status.textContent = 'Copied'; btn.classList.add('hit');
          timer = setTimeout(() => { status.textContent = ''; btn.classList.remove('hit'); }, 4000);
        } catch (_) {
          // Stop typing before selecting, so later frames cannot destroy the manual-copy selection.
          terminal.cancel();
          const range = document.createRange(), selection = getSelection();
          range.selectNodeContents(code); selection.removeAllRanges(); selection.addRange(range);
          status.textContent = 'Copy manually: press Command-C.';
        } finally { pending = false; }
      });
    }
  }
})();
