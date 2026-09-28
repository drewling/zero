'use strict';

/*
 * zero motion prototype, slice OPR.99.0.2.1 (design direction only, not production).
 *
 * Thesis: "The board sorts." Two Canvas effects, each with one job:
 *   1. sort-track (focal): each rule row on the timetable is routed. A pulse runs the
 *      row's track, the verdict flaps in, kept rows stay lit, archived rows drop aside.
 *   2. rail-diagram: the same conversations move between the Inbox and All Mail rails.
 *      The count never changes, so "nothing is deleted" is shown, not only said.
 * Supporting beats (DOM/CSS): hero flap settle (existing site.js), install-step boarding,
 * copy-button flap acknowledgement, FAQ sign flap and height ease.
 *
 * Every animation is a pure function of elapsed time, so frames can be seeked for
 * storyboards: window.zeroMotion.seek('sort', 900) or ?seek=sort:900,rail:400.
 * Prototype-only overrides: ?rm=1 simulates prefers-reduced-motion, ?nocanvas=1 simulates
 * Canvas failure, ?slow=4 slows time for review.
 */

(() => {
  const params = new URLSearchParams(location.search);
  const media = (q) => typeof matchMedia === 'function' && matchMedia(q).matches;
  const reduced = params.has('rm') || media('(prefers-reduced-motion: reduce)');
  const slow = Math.max(1, Number(params.get('slow')) || 1);
  const perf = []; // prototype instrument: per-frame draw cost and timestamps while playing
  const seekPlan = Object.fromEntries((params.get('seek') || '').split(',').filter(Boolean).map((s) => {
    const [k, v] = s.split(':');
    return [k, Number(v) || 0];
  }));

  const COLORS = {
    signal: '#ffc72c',
    ink: '#0a1f44',
    glyph: '#f4efe2',
    dim: '#9c958a',
  };
  const ease = (x) => 1 - Math.pow(1 - Math.min(Math.max(x, 0), 1), 4); // ease-out-quart
  const clamp01 = (x) => Math.min(Math.max(x, 0), 1);

  function getContext(canvas) {
    if (params.has('nocanvas')) return null;
    try {
      return canvas.getContext('2d');
    } catch {
      return null;
    }
  }

  function sizeCanvas(canvas, ctx, w, h) {
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    canvas.width = Math.round(w * dpr);
    canvas.height = Math.round(h * dpr);
    canvas.style.width = `${w}px`;
    canvas.style.height = `${h}px`;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }

  /* A timeline runs requestAnimationFrame only while playing, pauses when the tab is
     hidden, and never runs while offscreen after it settles. */
  function timeline(duration, draw) {
    let raf = 0;
    let start = 0;
    let elapsed = duration; // unplayed timelines rest in their settled state
    let playing = false;
    const frame = (now) => {
      if (!start) start = now - elapsed * slow;
      elapsed = (now - start) / slow;
      const t0 = performance.now();
      draw(Math.min(elapsed, duration));
      perf.push({ now, cost: performance.now() - t0 });
      if (elapsed < duration) raf = requestAnimationFrame(frame);
      else playing = false;
    };
    const api = {
      play(from = 0) {
        cancelAnimationFrame(raf);
        elapsed = from;
        start = 0;
        playing = true;
        raf = requestAnimationFrame(frame);
      },
      pause() {
        if (!playing) return;
        cancelAnimationFrame(raf);
        start = 0;
        playing = false;
        api.paused = true;
      },
      resume() {
        if (!api.paused) return;
        api.paused = false;
        playing = true;
        raf = requestAnimationFrame(frame);
      },
      seek(t) {
        cancelAnimationFrame(raf);
        playing = false;
        elapsed = t;
        draw(Math.min(t, duration));
      },
      get time() {
        return elapsed;
      },
      get playing() {
        return playing;
      },
      duration,
      paused: false,
    };
    document.addEventListener('visibilitychange', () => (document.hidden ? api.pause() : api.resume()));
    return api;
  }

  function onceVisible(el, threshold, fn) {
    if (!('IntersectionObserver' in window)) {
      fn();
      return;
    }
    const io = new IntersectionObserver((entries) => {
      if (entries.some((e) => e.isIntersecting)) {
        io.disconnect();
        fn();
      }
    }, { threshold });
    io.observe(el);
  }

  const registry = {};

  /* ---------- 1. Focal: the sorting board routes each rule ---------- */
  function setupSortTrack() {
    const board = document.querySelector('.sorting-board');
    const canvas = board?.querySelector('.sort-track');
    const replay = board?.querySelector('.sort-replay');
    if (!board || !canvas || reduced) return;
    const ctx = getContext(canvas);
    if (!ctx) return;

    canvas.hidden = false;
    board.classList.add('has-track');
    const rows = [...board.querySelectorAll('tbody tr')].map((tr) => {
      const status = tr.querySelector('.status');
      // Wrap the verdict word so the visual scramble overlays it; the real text stays in
      // the DOM for assistive tech and is never replaced.
      const textNode = [...status.childNodes].find((n) => n.nodeType === 3 && n.textContent.trim());
      const word = document.createElement('span');
      word.className = 'status-word';
      word.textContent = textNode.textContent.trim();
      textNode.replaceWith(word);
      return { tr, status, word, stays: !!status.classList.contains('stays'), final: word.textContent };
    });
    let geo = [];
    let w = 0;
    let h = 0;

    const measure = () => {
      const b = board.getBoundingClientRect();
      w = b.width;
      h = b.height;
      sizeCanvas(canvas, ctx, w, h);
      geo = rows.map((r) => {
        const tr = r.tr.getBoundingClientRect();
        const dot = r.status.querySelector('i').getBoundingClientRect();
        return {
          x0: tr.left - b.left,
          x1: dot.left - b.left + dot.width / 2,
          xEnd: tr.right - b.left,
          y: tr.bottom - b.top - 0.5,
          cy: dot.top - b.top + dot.height / 2,
        };
      });
    };

    const STAGGER = 170;
    const TRAVEL = 520;
    const SETTLE = 620;
    const DURATION = STAGGER * (rows.length - 1) + TRAVEL + SETTLE;
    const scramble = 'ABCDEHIKNORSTVY';

    function setStatus(i, t) {
      const r = rows[i];
      const local = t - i * STAGGER - TRAVEL;
      // DOM is only written when a row's visible state changes (at most ~6 writes per row
      // per run), so style recalculation never runs on every frame.
      let key;
      if (local < 0) key = 'pending';
      else if (local < 160) key = `s${Math.floor(local / 40)}`;
      else key = 'final';
      if (r.key === key) return;
      r.key = key;
      if (local < 0) {
        r.status.dataset.pending = '';
        r.word.dataset.scramble = '·'.repeat(r.final.length);
      } else if (local < 160) {
        const tick = Math.floor(local / 40);
        delete r.status.dataset.pending;
        r.word.dataset.scramble = [...r.final].map((c, k) => scramble[(c.charCodeAt(0) + tick * 7 + k * 3) % scramble.length]).join('');
      } else {
        delete r.status.dataset.pending;
        delete r.word.dataset.scramble;
      }
    }

    function draw(t) {
      ctx.clearRect(0, 0, w, h);
      rows.forEach((r, i) => {
        const g = geo[i];
        if (!g) return;
        setStatus(i, t);
        const local = t - i * STAGGER;
        if (local <= 0) return;
        const travel = ease(local / TRAVEL);
        const settle = clamp01((local - TRAVEL) / SETTLE);
        const headX = g.x0 + (g.x1 - g.x0) * travel;
        const decided = local >= TRAVEL;
        const color = decided ? (r.stays ? COLORS.signal : COLORS.dim) : COLORS.glyph;

        // Track trail along the row's divider.
        const trailLen = Math.min(140, headX - g.x0);
        const fade = decided ? (r.stays ? 0.35 + 0.65 * (1 - settle) : 1 - settle) : 1;
        if (trailLen > 0 && fade > 0.01) {
          const grad = ctx.createLinearGradient(headX - trailLen, 0, headX, 0);
          grad.addColorStop(0, 'rgba(0,0,0,0)');
          grad.addColorStop(1, color);
          ctx.globalAlpha = fade;
          ctx.fillStyle = grad;
          ctx.fillRect(headX - trailLen, g.y - 1, trailLen, 2);
        }
        // Kept rows keep a lit track across the full row once decided.
        if (decided && r.stays) {
          ctx.globalAlpha = 0.28 * ease(settle);
          ctx.fillStyle = COLORS.signal;
          ctx.fillRect(g.x0, g.y - 1, g.xEnd - g.x0, 2);
        }

        // The travelling ticket.
        if (!decided || !r.stays) {
          const drop = decided ? ease(settle) * 14 : 0;
          const alpha = decided ? 1 - settle : 1;
          ctx.globalAlpha = alpha;
          ctx.fillStyle = color;
          roundRect(ctx, headX - 7, g.y - 4 + drop, 14, 8, 2);
          ctx.fill();
        }

        // Verdict bloom around the status dot.
        if (decided && r.stays) {
          const pulse = 1 - settle;
          const radius = 6 + 16 * ease(Math.min(settle * 2, 1)) * (0.5 + 0.5 * pulse);
          const bloom = ctx.createRadialGradient(g.x1, g.cy, 0, g.x1, g.cy, radius);
          bloom.addColorStop(0, 'rgba(255,199,44,0.55)');
          bloom.addColorStop(1, 'rgba(255,199,44,0)');
          ctx.globalAlpha = 0.45 + 0.55 * pulse;
          ctx.fillStyle = bloom;
          ctx.beginPath();
          ctx.arc(g.x1, g.cy, radius, 0, Math.PI * 2);
          ctx.fill();
        }
      });
      ctx.globalAlpha = 1;
      const done = t >= DURATION;
      if (done !== board.classList.contains('sorted')) board.classList.toggle('sorted', done);
    }

    measure();
    const tl = timeline(DURATION, draw);
    registry.sort = tl;

    const run = () => {
      board.classList.remove('sorted');
      tl.play(0);
    };
    if ('sort' in seekPlan) tl.seek(seekPlan.sort);
    else {
      tl.seek(0); // unsorted until the board is actually seen, so the sort is witnessed
      onceVisible(board, 0.45, run);
    }

    if (replay) {
      replay.hidden = false;
      replay.addEventListener('click', run);
    }
    if ('ResizeObserver' in window) {
      new ResizeObserver(() => {
        measure();
        draw(Math.min(tl.time, DURATION));
      }).observe(board);
    }
  }

  function roundRect(ctx, x, y, w, h, r) {
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.arcTo(x + w, y, x + w, y + h, r);
    ctx.arcTo(x + w, y + h, x, y + h, r);
    ctx.arcTo(x, y + h, x, y, r);
    ctx.arcTo(x, y, x + w, y, r);
    ctx.closePath();
  }

  /* ---------- 2. Reversibility: Inbox and All Mail rails ---------- */
  function setupRail() {
    const wrap = document.querySelector('.rail-wrap');
    const canvas = wrap?.querySelector('.rail-diagram');
    const button = wrap?.querySelector('.rail-replay');
    if (!wrap || !canvas) return;
    const ctx = getContext(canvas);
    if (!ctx) return;
    wrap.hidden = false;

    const N = 7;
    const archived = new Set([1, 3, 4, 6]);
    let w = 0;
    const h = 150;
    const DURATION = 900;
    const STAGGER = 80;
    let direction = 1; // 1 = archive (inbox -> all mail), -1 = restore
    let settledArchived = true;

    const measure = () => {
      w = wrap.getBoundingClientRect().width;
      sizeCanvas(canvas, ctx, w, h);
    };

    function draw(t) {
      ctx.clearRect(0, 0, w, h);
      const left = 4;
      const right = w - 4;
      const yTop = 40;
      const yBottom = 112;
      ctx.font = '700 11px Archivo, system-ui, sans-serif';
      ctx.fillStyle = COLORS.ink;
      ctx.textBaseline = 'alphabetic';
      ctx.fillText('INBOX', left, yTop - 14);
      ctx.fillText('ALL MAIL · DATED RECOVERY LABEL', left, yBottom + 28);
      ctx.textAlign = 'right';
      ctx.font = '600 11px "Geist Mono", monospace';
      ctx.fillText(`illustration · same ${N} · none deleted`, right, yTop - 14);
      ctx.textAlign = 'left';

      ctx.fillStyle = COLORS.ink;
      ctx.fillRect(left, yTop, right - left, 2);
      ctx.globalAlpha = 0.45;
      ctx.fillRect(left, yBottom, right - left, 2);
      ctx.globalAlpha = 1;

      const span = (right - left - 40) / (N - 1);
      for (let k = 0; k < N; k += 1) {
        const x = left + 20 + span * k;
        let p = 0; // 0 = in inbox, 1 = in all mail with label
        if (archived.has(k)) {
          const order = [...archived].indexOf(k);
          const local = clamp01((t - order * STAGGER) / (DURATION - STAGGER * (archived.size - 1)));
          const e = ease(local);
          p = direction === 1 ? e : 1 - e;
        }
        const y = yTop + 1 + (yBottom - yTop) * p;
        const xOff = Math.sin(p * Math.PI) * 10;
        ctx.fillStyle = COLORS.ink;
        roundRect(ctx, x - 9 + xOff, y - 6, 18, 12, 3);
        if (p > 0.5) {
          ctx.globalAlpha = 1;
          ctx.lineWidth = 2;
          ctx.strokeStyle = COLORS.ink;
          ctx.stroke();
          // The dated label tag travels with the conversation.
          ctx.globalAlpha = clamp01((p - 0.5) * 2);
          ctx.fillRect(x + 11 + xOff, y - 4, 10, 8);
          ctx.globalAlpha = 1;
        } else {
          ctx.fill();
        }
      }
    }

    measure();
    const tl = timeline(DURATION, draw);
    registry.rail = tl;
    draw(DURATION);

    const play = (dir) => {
      direction = dir;
      settledArchived = dir === 1;
      button.textContent = settledArchived ? 'Show a restore' : 'Show the archive again';
      if (reduced) {
        wrap.classList.add('instant');
        tl.seek(DURATION);
        requestAnimationFrame(() => wrap.classList.remove('instant'));
      } else {
        tl.play(0);
      }
    };

    if (params.get('raildir') === '-1') {
      direction = -1;
      settledArchived = false;
      button.textContent = 'Show the archive again';
    }
    if ('rail' in seekPlan) tl.seek(seekPlan.rail);
    else if (!reduced) {
      direction = 1;
      tl.seek(0);
      onceVisible(wrap, 0.6, () => play(1));
    }
    button.addEventListener('click', () => play(settledArchived ? -1 : 1));
    if ('ResizeObserver' in window) {
      new ResizeObserver(() => {
        measure();
        draw(Math.min(tl.time, DURATION));
      }).observe(wrap);
    }
  }

  /* ---------- 3. Supporting beats ---------- */
  function setupBoarding() {
    const band = document.querySelector('.install-band');
    if (!band || reduced) return;
    band.classList.add('will-board');
    onceVisible(band.querySelector('.install-steps') || band, 0.25, () => band.classList.add('boarding'));
  }

  function setupCopyFlap() {
    const button = document.getElementById('copy-command');
    if (!button || !('MutationObserver' in window)) return;
    new MutationObserver(() => {
      if (reduced) return;
      button.classList.remove('flapped');
      void button.offsetWidth;
      button.classList.add('flapped');
    }).observe(button, { childList: true, characterData: true, subtree: true });
  }

  function setupFaq() {
    // Gate the sign flap so it only runs on a real toggle, never on page load.
    requestAnimationFrame(() => document.querySelector('.faq-list')?.classList.add('faq-ready'));
  }

  if (reduced) document.documentElement.classList.add('motion-reduced');
  setupSortTrack();
  setupRail();
  setupBoarding();
  setupCopyFlap();
  setupFaq();
  // Prototype-only: ?at=<selector> jumps instantly so storyboard captures are deterministic.
  // Runs after setup so blocks unhidden by script (the rail) have layout.
  const at = params.get('at');
  if (at) {
    const target = document.querySelector(at);
    if (target) {
      document.documentElement.style.scrollBehavior = 'auto';
      target.scrollIntoView({ block: 'start', behavior: 'instant' });
    }
  }
  // Canvas text needs the self-hosted faces; redraw settled frames once they load.
  document.fonts?.ready.then(() => Object.values(registry).forEach((tl) => {
    if (!tl.playing && !tl.paused) tl.seek(Math.min(tl.time, tl.duration));
  }));
  window.zeroMotion = {
    seek(name, ms) {
      registry[name]?.seek(ms);
    },
    play(name) {
      registry[name]?.play(0);
    },
    // Prototype instrument: script cost per drawn frame and gaps between drawn frames.
    stats() {
      const costs = perf.map((p) => p.cost);
      const gaps = perf.slice(1).map((p, i) => p.now - perf[i].now).filter((g) => g < 200);
      const max = (a) => (a.length ? Math.max(...a) : 0);
      const mean = (a) => (a.length ? a.reduce((x, y) => x + y, 0) / a.length : 0);
      return { frames: perf.length, drawMeanMs: mean(costs), drawMaxMs: max(costs), gapMeanMs: mean(gaps), gapMaxMs: max(gaps) };
    },
    // Prototype instrument: time N seeked draws across the timeline, synchronously.
    bench(name, n = 200) {
      const tl = registry[name];
      if (!tl) return null;
      const t0 = performance.now();
      for (let k = 0; k < n; k += 1) tl.seek((tl.duration * k) / n);
      const perDraw = (performance.now() - t0) / n;
      tl.seek(tl.duration);
      return { name, n, perDrawMs: perDraw };
    },
    reduced,
  };
})();
