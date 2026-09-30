/* Sandbox Zm runner. Data-driven frames match the comp API, with bounded playback.
   Final HTML is the fallback. All helpers share one AbortSignal per playback.
   No dependencies, easing, opacity fades, rAF tweening or layout animations. */
(function () {
  const q = new URLSearchParams(location.search);
  const reduce = matchMedia('(prefers-reduced-motion: reduce)');
  const fine = matchMedia('(pointer: fine)');
  let jumpedAt = -1e9;
  const markJump = () => { jumpedAt = performance.now(); };
  addEventListener('click', e => { if (e.target.closest?.('a[href^="#"]')) markJump(); }, true);
  addEventListener('hashchange', markJump);
  const controllers = new WeakMap();
  const pick = (root, s) => typeof s === 'function' ? s(root) : typeof s === 'string' ? root.querySelector(s) : s;
  const aborted = signal => { if (signal?.aborted) throw new DOMException('Playback cancelled', 'AbortError'); };
  function wait(ms, signal) {
    aborted(signal);
    return new Promise((resolve, reject) => {
      const done = () => { signal?.removeEventListener('abort', stop); resolve(); };
      const timer = setTimeout(done, Math.max(0, ms));
      const stop = () => { clearTimeout(timer); signal.removeEventListener('abort', stop); reject(new DOMException('Playback cancelled', 'AbortError')); };
      signal?.addEventListener('abort', stop, { once: true });
    });
  }
  function rel(root, el) {
    if (!el || !el.getClientRects().length) throw new Error('Missing or hidden motion target');
    const a = root.getBoundingClientRect(), b = el.getBoundingClientRect();
    return { x: b.left - a.left - root.clientLeft, y: b.top - a.top - root.clientTop, w: b.width, h: b.height };
  }
  function target(root, spec) {
    const b = rel(root, pick(root, spec.sel));
    return { x: b.x + b.w * (spec.fx ?? .5) + (spec.dx || 0), y: b.y + b.h * (spec.fy ?? .5) + (spec.dy || 0) };
  }
  function place(el, x, y) { el.style.transform = `translate(${Math.round(x)}px,${Math.round(y)}px)`; }
  function setFrame(root, k, n) {
    for (let i = 1; i < n; i++) root.classList.toggle('lt-' + i, k < i);
    root.dataset.f = k;
  }
  function overlay(root, name, svg = false) {
    const el = svg ? document.createElementNS('http://www.w3.org/2000/svg', 'svg') : document.createElement('div');
    el.classList.add(name); el.setAttribute('data-zm-overlay', ''); el.setAttribute('aria-hidden', 'true');
    el.style.pointerEvents = 'none'; root.appendChild(el);
    return el;
  }
  async function move(el, a, b, steps, ms, signal) {
    for (let i = 1; i <= steps; i++) {
      aborted(signal); place(el, a.x + (b.x - a.x) * i / steps, a.y + (b.y - a.y) * i / steps);
      await wait(ms / steps, signal);
    }
  }
  function helpers(signal) {
    function envelope(root) {
      const e = overlay(root, 'fly', true);
      e.classList.add('px'); e.setAttribute('viewBox', '0 0 16 11'); e.innerHTML = '<use href="#mail"/>';
      Object.assign(e.style, { position: 'absolute', left: '0', top: '0', width: '32px', height: '22px', zIndex: '38' });
      return e;
    }
    const arc = (a, b, t, lift) => ({ x: a.x + (b.x - a.x) * t - 16, y: a.y + (b.y - a.y) * t - lift * 4 * t * (1 - t) - 11 });
    async function zoom(root, from, to, { steps = 5, ms = 240, still = false } = {}) {
      const a = rel(root, pick(root, from)), b = rel(root, pick(root, to)), rects = [];
      try {
        for (let i = 1; i <= steps; i++) {
          aborted(signal);
          const t = i / (steps + 1), d = overlay(root, 'zr'); rects.push(d);
          // Each rectangle is a discrete sprite, never a width/height tween.
          Object.assign(d.style, { display: 'block', left: Math.round(a.x + (b.x - a.x) * t) + 'px', top: Math.round(a.y + (b.y - a.y) * t) + 'px', width: Math.round(a.w + (b.w - a.w) * t) + 'px', height: Math.round(a.h + (b.h - a.h) * t) + 'px' });
          if (!still) { await wait(ms / steps, signal); if (i > 2) rects[i - 3].remove(); }
        }
      } finally { if (!still) rects.forEach(r => r.remove()); }
      return rects;
    }
    async function hop(root, from, to, { n = 8, steps = 5, ms = 170, gap = 120, lift = 70, onLaunch, onEach } = {}) {
      for (let i = 0; i < n; i++) {
        aborted(signal);
        // Geometry reads happen once per hop, before any DOM writes.
        const a = target(root, from), b = target(root, to), e = envelope(root);
        try {
          const start = arc(a, b, 0, lift); place(e, start.x, start.y); onLaunch?.(i);
          for (let s = 1; s <= steps; s++) {
            await wait(ms / steps, signal); aborted(signal);
            const p = arc(a, b, s / steps, lift); place(e, p.x, p.y);
          }
          e.remove(); onEach?.(i);
          if (i < n - 1) await wait(gap, signal);
        } finally { e.remove(); }
      }
    }
    function hopStill(root, from, to, ts = [.25, .5, .75], lift = 70) {
      const a = target(root, from), b = target(root, to);
      ts.forEach(t => { const e = envelope(root), p = arc(a, b, t, lift); place(e, p.x, p.y); });
    }
    async function drag(root, sources, to, { steps = 7, ms = 560, still, cursorFrom, scale = .5, layer = 2 } = {}) {
      aborted(signal);
      const source = typeof sources === 'function' ? sources(root) : sources;
      // Capture current geometry before overlay writes. No font or container assumptions.
      const boxes = [...source].map(el => rel(root, el));
      const end = rel(root, pick(root, to.sel));
      const aim = { x: end.x + end.w * (to.fx ?? .5), y: end.y + end.h * (to.fy ?? .5) };
      const cur = root.querySelector(':scope > .cursor');
      const start = cur && cursorFrom ? target(root, cursorFrom) : null;
      const outlines = boxes.map(() => overlay(root, 'drop'));
      const draw = t => {
        aborted(signal);
        boxes.forEach((b, i) => {
          const w = b.w + (end.w * scale - b.w) * t, h = b.h + (end.h * scale - b.h) * t;
          Object.assign(outlines[i].style, {
            position: 'absolute', zIndex: String(layer),
            left: '0px', top: '0px',
            width: Math.round(w) + 'px', height: Math.round(h) + 'px'
          });
          place(outlines[i], b.x + (aim.x - w / 2 - b.x) * t, b.y + (aim.y - h / 2 - b.y) * t);
        });
        if (start) place(cur, start.x + (aim.x - start.x) * t, start.y + (aim.y - start.y) * t);
      };
      if (still !== undefined) { draw(still); return; }
      try {
        draw(0);
        for (let step = 1; step <= steps; step++) { draw(step / steps); await wait(ms / steps, signal); }
      } finally { outlines.forEach(el => el.remove()); }
    }
    return { wait: ms => wait(ms, signal), rel, target, place, zoom, hop, hopStill, drag };
  }
  function create(root, story) {
    const frames = story.frames, n = frames.length;
    if (!n) throw new Error('A story needs at least one frame');
    let abort, observer, deadline, disposed = false;
    const replay = pick(root, story.replay);
    const c = { pending: null, error: null, startedAt: 0, durationMs: 0 };
    const updateReplay = () => { if (replay) replay.disabled = disposed || !!c.pending || reduce.matches || q.has('static') || q.has('frame') || document.hidden; };
    function clean() {
      root.querySelectorAll(':scope > [data-zm-overlay]').forEach(e => e.remove());
      root.querySelectorAll('.pressed').forEach(e => e.classList.remove('pressed'));
    }
    function finish(mode) {
      clearTimeout(deadline); clean(); setFrame(root, n - 1, n);
      try { (story.finish || frames[n - 1].set)?.(root, helpers(), mode); } catch (e) { c.error = e; mode = 'error'; }
      root.dataset.mode = mode;
      if (c.startedAt) { c.durationMs = Math.round(performance.now() - c.startedAt); root.dataset.durationMs = c.durationMs; }
      updateReplay();
      root.dispatchEvent(new CustomEvent('motion:finish', { detail: { mode, durationMs: c.durationMs } }));
    }
    c.cancel = () => { observer?.disconnect(); abort?.abort(); finish('cancelled'); };
    c.dispose = () => {
      disposed = true; c.cancel();
      document.removeEventListener('visibilitychange', visibility);
      window.removeEventListener('resize', resized);
      reduce.removeEventListener('change', preference);
      fine.removeEventListener('change', resized);
    };
    const visibility = () => { if (document.hidden) c.cancel(); else updateReplay(); };
    const preference = () => { if (reduce.matches) c.cancel(); else updateReplay(); };
    const resized = () => { if (c.pending) c.cancel(); };
    document.addEventListener('visibilitychange', visibility);
    window.addEventListener('resize', resized);
    reduce.addEventListener('change', preference);
    fine.addEventListener('change', resized);
    function cursor(frame, z) {
      if (!frame.cursor || !fine.matches || innerWidth < (story.cursorMinWidth || 760)) return null;
      let el = root.querySelector(':scope > .cursor');
      if (!el) { el = overlay(root, 'cursor'); el.innerHTML = '<svg class="px" viewBox="0 0 16 17"><use href="#cursor"/></svg>'; }
      el.querySelector('use').setAttribute('href', frame.kind === 'watch' ? '#watch' : '#cursor');
      return { el, point: z.target(root, frame.cursor) };
    }
    c.start = () => {
      if (c.pending) return c.pending;
      observer?.disconnect();
      if (disposed || reduce.matches || q.has('static') || document.hidden) { finish('static'); return Promise.resolve(); }
      if (q.has('frame')) {
        try {
          clean(); const value = Number(q.get('frame'));
          const k = Number.isFinite(value) ? Math.max(0, Math.min(n - 1, Math.trunc(value))) : n - 1;
          if (k === n - 1) { finish('static'); return Promise.resolve(); }
          const z = helpers(); setFrame(root, k, n);
          for (let j = 0; j <= k; j++) frames[j].set?.(root, z);
          const cur = cursor(frames[k], z); if (cur) place(cur.el, cur.point.x, cur.point.y);
          const still = frames[k].still?.(root, z); root.dataset.mode = 'frame';
          return Promise.resolve(still).catch(e => { c.error = e; finish('error'); });
        } catch (e) { c.error = e; finish('error'); }
        return Promise.resolve();
      }
      abort = new AbortController(); const signal = abort.signal, z = helpers(signal);
      c.error = null; c.startedAt = performance.now();
      deadline = setTimeout(c.cancel, story.maxMs || 6000);
      if (replay) replay.disabled = true;
      c.pending = (async () => {
        try {
          clean(); root.dataset.mode = 'play'; setFrame(root, 0, n); frames[0].set?.(root, z);
          let cur = cursor(frames[0], z); if (cur) place(cur.el, cur.point.x, cur.point.y);
          await z.wait(story.delay ?? 700);
          for (let k = 1; k < n; k++) {
            aborted(signal);
            const f = frames[k], next = cursor(f, z);
            if (next && cur && (cur.point.x !== next.point.x || cur.point.y !== next.point.y)) await move(next.el, cur.point, next.point, f.cursorSteps || 6, f.cursorMs || 300, signal);
            else if (next) place(next.el, next.point.x, next.point.y);
            if (!next) root.querySelector(':scope > .cursor')?.remove();
            cur = next; setFrame(root, k, n); f.set?.(root, z);
            if (f.enter) await f.enter(root, z);
            await z.wait(f.hold ?? 0);
          }
          finish('done');
        } catch (e) {
          if (e.name !== 'AbortError') c.error = e;
          if (e.name !== 'AbortError' || root.dataset.mode !== 'cancelled') finish(e.name === 'AbortError' ? 'cancelled' : 'error');
        }
      })().finally(() => { c.pending = null; updateReplay(); });
      return c.pending;
    };
    c.observe = () => {
      if (story.onLoad || q.has('frame') || q.has('static') || reduce.matches) c.start();
      else if (!('IntersectionObserver' in window)) finish('static');
      else {
        let armed = false, started = false;
        const settle = () => { started = true; observer.disconnect(); finish('seen'); };
        const arm = () => {
          if (armed || started) return;
          try {
            armed = true; setFrame(root, 0, n); frames[0].set?.(root, helpers()); root.dataset.mode = 'armed';
          } catch (e) { c.error = e; started = true; observer.disconnect(); finish('error'); }
        };
        const pre = new IntersectionObserver(entries => {
          const e = entries.find(e => e.isIntersecting); if (!e || started) return;
          pre.disconnect();
          if (e.boundingClientRect.top < innerHeight) settle();
          else arm();
        }, { rootMargin: '0px 0px 30% 0px', threshold: 0 });
        const play = new IntersectionObserver(entries => {
          if (!armed || started || !entries.some(e => e.isIntersecting && (e.intersectionRatio >= .35 || e.intersectionRect.height >= innerHeight * .35))) return;
          if (performance.now() - jumpedAt < 1200) settle();
          else { started = true; c.start(); }
        }, { threshold: [0, .1, .2, .35, .5] });
        observer = { disconnect() { pre.disconnect(); play.disconnect(); } };
        const box = root.getBoundingClientRect();
        let hash;
        try { hash = document.getElementById(decodeURIComponent(location.hash.slice(1))); } catch (_) {}
        if (hash && (hash === root || hash.contains(root) || root.contains(hash))) settle();
        else if (box.top < innerHeight && box.bottom > 0) settle();
        else { pre.observe(root); play.observe(root); }
      }
    };
    controllers.set(root, c);
    return c;
  }
  const controller = (root, story) => controllers.get(root) || create(root, story);
  window.Zm = {
    play: (root, story) => controller(root, story).start(),
    when: (root, story) => { const c = controller(root, story); c.observe(); return c; },
    api: helpers()
  };
})();
