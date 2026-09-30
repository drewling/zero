/* Selected page B interaction contracts. This file is the tiny interaction layer for the static page. */
(function () {
  const $$ = (r, s) => [...r.querySelectorAll(s)];
  const hide = els => els.forEach(e => e.classList.add('stepping'));
  const show = els => els.forEach(e => e.classList.remove('stepping'));
  const pulse = async (el, z, ms) => {
    if (!el) return;
    el.classList.add('pressed');
    try { await z.wait(ms); } finally { el.classList.remove('pressed'); }
  };
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
        enter: async (r, z) => {
          const rows = $$(r, '.info .row'), bound = r.querySelector('.bound');
          hide(rows); bound?.classList.add('ants');
          try { await reveal(rows, z, 90); await z.wait(2400); }
          finally { bound?.classList.remove('ants'); }
        } }
    ] });
  const rules = document.getElementById('rules-win');
  if (rules) {
    const tab = k => $$(rules, '.tabs span').forEach((s, i) => s.classList.toggle('on', i === k));
    Zm.when(rules, { delay: 350,
      finish: r => { tab(3); show($$(r, '.editor .ln')); },
      frames: [ { set: () => tab(0) },
        { hold: 160, enter: async (r, z) => {
            const tabs = $$(r, '.tabs span');
            for (const k of [1, 2, 3]) { await z.wait(110); await pulse(tabs[k], z, 60); tab(k); }
          }, still: () => tab(3) },
        { hold: 0, set: r => { tab(3); show($$(r, '.editor .ln')); },
          enter: async (r, z) => {
            const lines = $$(r, '.editor .ln'); hide(lines); await reveal(lines, z, 45, 2);
            await pulse(r.querySelector('.save .btn'), z, 80);
          } }
      ] });
  }
  const undo = document.getElementById('undo-win');
  if (undo) Zm.when(undo, { delay: 350,
    finish: r => { show($$(r, '.urows li')); r.classList.remove('balloon-wait'); },
    frames: [ {},
      { hold: 380, set: r => show($$(r, '.urows li')),
        enter: (r, z) => { const rows = $$(r, '.urows li'); hide(rows); return reveal(rows, z, 80); } },
      { cursor: { sel: '.ub.hot', fx: .5, fy: .5 }, cursorSteps: 6, cursorMs: 300, hold: 0,
        set: r => r.classList.add('balloon-wait'),
        enter: async (r, z) => {
          try { await pulse(r.querySelector('.ub.hot'), z, 80); }
          finally { r.classList.remove('balloon-wait'); }
        } }
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
    const terminal = Zm.when(term, { delay: 0,
      finish: (r, z, mode) => { clearTyping(); term.classList.toggle('blink', mode === 'done'); },
      frames: [ { set: (r) => { r.classList.remove('lt-1'); typed(0); r.classList.add('lt-1'); } },
        { hold: 0, set: () => { typed(0); },
          enter: async (r, z) => {
            await z.zoom(r, '.p', r, { steps: 5, ms: 240 });
            for (let n = 0; n <= full.length; n += 4) { typed(n); await z.wait(45); }
            typed(full.length); await z.wait(45); clearTyping();
            await pulse(r.querySelector('#copy'), z, 80);
          },
          still: () => typed(24) }
      ] });
    const btn = document.getElementById('copy'), status = document.getElementById('copy-status');
    if (btn && status && window.isSecureContext && typeof navigator.clipboard?.writeText === 'function') {
      btn.hidden = false; let timer, pending = false;
      btn.addEventListener('click', async () => {
        if (pending) return;
        pending = true; btn.setAttribute('aria-disabled', 'true'); btn.setAttribute('aria-busy', 'true');
        clearTimeout(timer); status.textContent = ''; btn.classList.remove('hit');
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
        } finally { pending = false; btn.removeAttribute('aria-disabled'); btn.removeAttribute('aria-busy'); }
      });
    }
  }
})();
