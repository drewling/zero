/* Zm: a stepped, one-bit storyboard runner for the zero redesign 3 comps.

   Contract (slice 04 must keep it):
   - The HTML + CSS default IS the final frame. With no JS, or with prefers-reduced-motion, the visitor sees it.
   - A story is a list of frames. At frame k, the root gets the class `lt-K` for every K > k, so CSS writes earlier states
     as `.lt-K selector {...}` ("before frame K"). Deleting every `lt-*` class gives the final frame.
   - All movement is stepped: positions jump in whole-pixel steps, and nothing is eased or faded.
   - ?frame=N renders frame N still (storyboard captures). ?static renders the final frame.
*/
(function () {
  const q = new URLSearchParams(location.search);
  const rmq = matchMedia('(prefers-reduced-motion: reduce)');
  let reduce = rmq.matches;
  // turning Reduce Motion on mid-visit settles every armed or playing story on its final frame (the no-JS HTML)
  const live = new Set();
  rmq.addEventListener && rmq.addEventListener('change', e => { reduce = e.matches; if (reduce) [...live].forEach(stop => stop()); });
  const fine = matchMedia('(pointer: fine)').matches;
  const wait = ms => new Promise(r => setTimeout(r, ms));
  const $ = (root, s) => (typeof s === 'function' ? s(root) : typeof s === 'string' ? root.querySelector(s) : s);

  function setFrame(root, k, n) {
    for (let K = 1; K < n; K++) root.classList.toggle('lt-' + K, k < K);
    root.dataset.f = k;
  }
  function rel(root, el) {
    const r = root.getBoundingClientRect(), b = el.getBoundingClientRect();
    return { x: b.left - r.left, y: b.top - r.top, w: b.width, h: b.height };
  }
  function place(el, x, y) { el.style.transform = `translate(${Math.round(x)}px,${Math.round(y)}px)`; }
  function target(root, spec) {
    const el = $(root, spec.sel); if (!el) return null;
    const b = rel(root, el);
    return { x: b.x + b.w * (spec.fx ?? .5) + (spec.dx || 0), y: b.y + b.h * (spec.fy ?? .5) + (spec.dy || 0) };
  }
  async function stepMove(el, from, to, steps, ms) {
    for (let i = 1; i <= steps; i++) {
      place(el, from.x + (to.x - from.x) * i / steps, from.y + (to.y - from.y) * i / steps);
      await wait(ms / steps);
    }
  }

  /* classic Mac zoom: outline rectangles stepping from one box to another, trail erased */
  async function zoom(root, fromEl, toEl, { steps = 5, ms = 260, still = false } = {}) {
    const a = rel(root, $(root, fromEl)), b = rel(root, $(root, toEl));
    const rects = [];
    for (let i = 1; i <= steps; i++) {
      const t = i / (steps + 1), d = document.createElement('div');
      d.className = 'zr';
      Object.assign(d.style, {
        display: 'block', left: Math.round(a.x + (b.x - a.x) * t) + 'px', top: Math.round(a.y + (b.y - a.y) * t) + 'px',
        width: Math.round(a.w + (b.w - a.w) * t) + 'px', height: Math.round(a.h + (b.h - a.h) * t) + 'px'
      });
      root.appendChild(d); rects.push(d);
      if (!still) { await wait(ms / steps); if (i > 2) rects[i - 3].remove(); }
    }
    if (!still) { await wait(ms / steps); rects.forEach(r => r.remove()); }
    return rects;
  }

  /* an envelope hopping from one element to another along a stepped arc */
  function envelope(root) {
    const s = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    s.setAttribute('class', 'px fly'); s.setAttribute('aria-hidden', 'true'); s.setAttribute('viewBox', '0 0 16 11');
    s.innerHTML = '<use href="#mail"/>';
    Object.assign(s.style, { position: 'absolute', left: 0, top: 0, width: '32px', height: '22px', zIndex: 38 });
    root.appendChild(s); return s;
  }
  function arcPoint(a, b, t, lift) {
    return { x: a.x + (b.x - a.x) * t - 16, y: a.y + (b.y - a.y) * t - lift * 4 * t * (1 - t) - 11 };
  }
  async function hop(root, fromSpec, toSpec, { n = 8, steps = 5, ms = 150, gap = 90, lift = 90, onEach } = {}) {
    for (let i = 0; i < n; i++) {
      const a = target(root, fromSpec), b = target(root, toSpec), e = envelope(root);
      (async () => {
        for (let s = 0; s <= steps; s++) { const p = arcPoint(a, b, s / steps, lift); place(e, p.x, p.y); await wait(ms / steps); }
        e.remove(); onEach && onEach(i);
      })();
      await wait(gap);
    }
    await wait(ms + 40);
  }
  function hopStill(root, fromSpec, toSpec, ts = [.25, .5, .75], lift = 90) {
    const a = target(root, fromSpec), b = target(root, toSpec);
    ts.forEach(t => { const e = envelope(root), p = arcPoint(a, b, t, lift); place(e, p.x, p.y); });
  }

  function cursor(root) {
    let c = root.querySelector(':scope > .cursor');
    if (!c) {
      c = document.createElement('div'); c.className = 'cursor'; c.setAttribute('aria-hidden', 'true');
      c.innerHTML = '<svg class="px" viewBox="0 0 16 17"><use href="#cursor"/></svg>';
      root.appendChild(c);
    }
    return c;
  }
  function setCursorKind(c, kind) {
    c.querySelector('use').setAttribute('href', kind === 'watch' ? '#watch' : '#cursor');
    c.classList.toggle('watch', kind === 'watch');
  }

  const api = { wait, rel, zoom, hop, hopStill, target, place };

  async function play(root, story) {
    const frames = story.frames, n = frames.length;
    const fq = q.get('frame');
    // ?frame=N forces the cursor on for storyboard captures; live playback needs a fine pointer and a wide viewport
    const wide = () => (fine || fq !== null) && (!story.cursorMinWidth || innerWidth >= story.cursorMinWidth);

    if (q.has('static') || (reduce && fq === null)) {
      // the final frame is the no-JS HTML: add nothing (no cursor, no overlays)
      setFrame(root, n - 1, n);
      root.dataset.mode = 'static';
      return;
    }
    // only stories that have a cursor frame get a cursor element (section stories add no stray DOM)
    const c = frames.some(f => f.cursor) ? cursor(root) : { style: {}, remove() {}, querySelector: () => ({ setAttribute() {} }), classList: { toggle() {} } };
    const showCursor = f => { c.style.display = f.cursor && wide() ? 'block' : 'none'; };
    const putCursor = f => { const p = f.cursor && target(root, f.cursor); if (p) place(c, p.x, p.y); setCursorKind(c, f.kind); };

    if (fq !== null) {
      const k = fq !== null ? Math.max(0, Math.min(n - 1, +fq)) : n - 1;
      const f = frames[k];
      setFrame(root, k, n); showCursor(f); putCursor(f);
      // a still frame K is the result of every set() up to K, then K's still() overlay
      for (let j = 0; j <= k; j++) if (frames[j].set) frames[j].set(root, api);
      if (fq !== null && f.still) f.still(root, api);
      root.dataset.mode = fq !== null ? 'frame' : 'static';
      return;
    }
    // any error mid-story jumps to the final frame (the no-JS state) instead of leaving a half-played scene
    const finish = () => {
      live.delete(stopNow);
      root.querySelectorAll(':scope > .zr, :scope > .fly').forEach(e => e.remove());
      c.remove(); setFrame(root, n - 1, n);
      for (const f of frames) if (f.set) try { f.set(root, api); } catch (_) {}
      root.dataset.mode = 'done';
    };
    let stopped = false;
    const stopNow = () => { stopped = true; finish(); root.dataset.mode = 'static'; };
    live.add(stopNow);
    try {
    root.dataset.mode = 'play';
    setFrame(root, 0, n); if (frames[0].set) frames[0].set(root, api);
    showCursor(frames[0]); putCursor(frames[0]);
    await wait(story.delay ?? 500);
    if (stopped) return;
    let at = frames[0].cursor && target(root, frames[0].cursor);
    for (let k = 1; k < n; k++) {
      const f = frames[k];
      if (f.cursor && wide()) {
        const to = target(root, f.cursor);
        showCursor(f); setCursorKind(c, f.kind);
        if (at && to) await stepMove(c, at, to, f.cursorSteps || 6, f.cursorMs || 240);
        else if (to) place(c, to.x, to.y); // the cursor's first appearance: put it there, don't slide in from 0,0
        at = to;
      } else showCursor(f);
      if (stopped) return;
      setFrame(root, k, n);
      if (f.set) f.set(root, api);
      if (f.enter) await f.enter(root, api);
      if (stopped) return;
      await wait(f.hold ?? 300);
      if (stopped) return;
    }
    live.delete(stopNow);
    root.dataset.mode = 'done';
    } catch (err) { if (stopped) return; console.error('Zm story failed, showing final frame', err); finish(); }
  }

  /* start when the element first enters the viewport (sections), or on load (heroes).
     Sections are ARMED (put on frame 0) while still below the fold, then PLAYED once 35% of the element, or 35% of
     the viewport, is visible. So a visitor never sees the final frame snap back to frame 0. */
  function when(root, story) {
    if (story.onLoad || q.has('frame') || q.has('static') || reduce || !('IntersectionObserver' in window)) {
      return play(root, story);
    }
    let armed = false, started = false;
    // put an armed story straight onto its final frame (the no-JS HTML), without playing it
    const settle = mode => { started = true; live.delete(stopArmed); io.disconnect(); pre.disconnect(); const n = story.frames.length;
      setFrame(root, n - 1, n); for (const f of story.frames) if (f.set) try { f.set(root, api); } catch (_) {}
      root.dataset.mode = mode; };
    const stopArmed = () => settle('static');
    live.add(stopArmed);
    const arm = () => { if (armed || started) return; armed = true;
      setFrame(root, 0, story.frames.length); if (story.frames[0].set) story.frames[0].set(root, api); root.dataset.mode = 'armed'; };
    // first sighting: if the element is already on screen (an anchor jump such as the hero's Install link, a reload
    // mid-page, a fast fling), it stays on its final frame and never plays, so nothing the visitor is reading vanishes.
    const pre = new IntersectionObserver(es => {
      const e = es.find(x => x.isIntersecting); if (!e) return;
      pre.disconnect();
      if (e.boundingClientRect.top < innerHeight) { started = true; live.delete(stopArmed); io.disconnect(); root.dataset.mode = 'seen'; return; }
      arm();
    },
      { rootMargin: '0px 0px 30% 0px', threshold: 0 });
    const io = new IntersectionObserver(es => {
      if (!armed || started || !es.some(e => e.isIntersecting && (e.intersectionRatio >= .35 || e.intersectionRect.height >= innerHeight * .35))) return;
      // arrived by an in-page link (the hero's Install CTA, the menu bar): the visitor came to read, so show it final
      if (performance.now() - jumpedAt < 1200) return settle('seen');
      io.disconnect(); pre.disconnect(); started = true; live.delete(stopArmed); play(root, story);
    }, { threshold: [0, .1, .2, .35, .5] });
    pre.observe(root);
    io.observe(root);
  }
  let jumpedAt = -1e9;
  const markJump = () => { jumpedAt = performance.now(); };
  addEventListener('click', e => { const a = e.target.closest && e.target.closest('a[href^="#"]'); if (a) markJump(); }, true);
  addEventListener('hashchange', markJump);

  window.Zm = { play, when, api };
})();
