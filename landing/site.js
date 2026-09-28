'use strict';

const copyButton = document.getElementById('copy-command');
const command = document.getElementById('install-command');
const status = document.getElementById('copy-status');

if (copyButton && command && status && navigator.clipboard?.writeText) {
  copyButton.hidden = false;
  copyButton.addEventListener('click', async () => {
    copyButton.disabled = true;
    try {
      await navigator.clipboard.writeText(command.textContent.trim());
      status.textContent = 'Copied. Paste it into Terminal when you’re ready.';
      copyButton.textContent = 'Copy again';
    } catch {
      status.textContent = 'Couldn’t copy. Select the command above and copy it manually.';
    } finally {
      copyButton.disabled = false;
    }
  });
}

(() => {
  if (typeof document.querySelector !== 'function') return;

  const reduced = typeof matchMedia === 'function'
    && matchMedia('(prefers-reduced-motion: reduce)').matches;
  const COLORS = {
    signal: '#ffc72c',
    ink: '#0a1f44',
    glyph: '#f4efe2',
    dim: '#9c958a',
  };
  const ease = (x) => 1 - Math.pow(1 - Math.min(Math.max(x, 0), 1), 4);
  const clamp01 = (x) => Math.min(Math.max(x, 0), 1);

  function getContext(canvas) {
    try {
      return canvas.getContext('2d');
    } catch {
      return null;
    }
  }

  function sizeCanvas(canvas, ctx, width, height) {
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    canvas.width = Math.round(width * dpr);
    canvas.height = Math.round(height * dpr);
    canvas.style.width = `${width}px`;
    canvas.style.height = `${height}px`;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }

  function timeline(duration, draw) {
    let raf = 0;
    let start = 0;
    let elapsed = duration;
    let playing = false;
    let paused = false;

    const frame = (now) => {
      if (!start) start = now - elapsed;
      elapsed = Math.min(duration, Math.max(0, now - start));
      draw(elapsed);
      if (elapsed < duration && !document.hidden) {
        raf = requestAnimationFrame(frame);
      } else {
        playing = false;
        if (document.hidden && elapsed < duration) paused = true;
      }
    };

    const api = {
      play(from = 0) {
        cancelAnimationFrame(raf);
        elapsed = Math.min(duration, Math.max(0, from));
        start = 0;
        paused = false;
        playing = true;
        raf = requestAnimationFrame(frame);
      },
      pause() {
        if (!playing) return;
        cancelAnimationFrame(raf);
        start = 0;
        playing = false;
        paused = true;
      },
      resume() {
        if (!paused) return;
        paused = false;
        playing = true;
        start = 0;
        raf = requestAnimationFrame(frame);
      },
      seek(time) {
        cancelAnimationFrame(raf);
        elapsed = Math.min(duration, Math.max(0, time));
        start = 0;
        playing = false;
        paused = false;
        draw(elapsed);
      },
      get time() { return elapsed; },
      get playing() { return playing; },
      get paused() { return paused; },
      duration,
    };

    document.addEventListener('visibilitychange', () => {
      if (document.hidden) api.pause();
      else api.resume();
    });
    return api;
  }

  function playOnceOnView(element, timelineInstance, play) {
    if (!('IntersectionObserver' in window)) {
      play();
      return;
    }
    let started = false;
    const observer = new IntersectionObserver((entries) => {
      const visible = entries.some((entry) => entry.isIntersecting);
      if (visible) {
        if (!started) {
          started = true;
          play();
        } else {
          timelineInstance.resume();
        }
      } else if (started) {
        timelineInstance.pause();
      }
    }, { threshold: 0.25 });
    observer.observe(element);
  }

  function roundRect(ctx, x, y, width, height, radius) {
    ctx.beginPath();
    ctx.moveTo(x + radius, y);
    ctx.arcTo(x + width, y, x + width, y + height, radius);
    ctx.arcTo(x + width, y + height, x, y + height, radius);
    ctx.arcTo(x, y + height, x, y, radius);
    ctx.arcTo(x, y, x + width, y, radius);
    ctx.closePath();
  }

  const timelines = [];

  function setupSortTrack() {
    const board = document.querySelector('.sorting-board');
    const canvas = board?.querySelector('.sort-track');
    const replay = board?.querySelector('.sort-replay');
    if (!board || !canvas || !replay || reduced) return;
    const ctx = getContext(canvas);
    if (!ctx) return;

    canvas.hidden = false;
    replay.hidden = false;
    board.classList.add('has-track');
    const rows = [...board.querySelectorAll('tbody tr')].map((tr) => {
      const statusNode = tr.querySelector('.status');
      const textNode = [...statusNode.childNodes].find((node) => node.nodeType === 3 && node.textContent.trim());
      const word = document.createElement('span');
      word.className = 'status-word';
      word.textContent = textNode.textContent.trim();
      textNode.replaceWith(word);
      return {
        tr,
        status: statusNode,
        word,
        stays: statusNode.classList.contains('stays'),
        key: null,
      };
    });
    let geometry = [];
    let width = 0;
    let height = 0;
    const stagger = 170;
    const travel = 520;
    const settle = 620;
    const duration = stagger * (rows.length - 1) + travel + settle;

    const measure = () => {
      const boardBox = board.getBoundingClientRect();
      width = boardBox.width;
      height = boardBox.height;
      sizeCanvas(canvas, ctx, width, height);
      geometry = rows.map((row) => {
        const rowBox = row.tr.getBoundingClientRect();
        const dotBox = row.status.querySelector('i').getBoundingClientRect();
        return {
          x0: rowBox.left - boardBox.left,
          x1: dotBox.left - boardBox.left + dotBox.width / 2,
          xEnd: rowBox.right - boardBox.left,
          y: rowBox.bottom - boardBox.top - 0.5,
          cy: dotBox.top - boardBox.top + dotBox.height / 2,
        };
      });
    };

    const setStatus = (row, time) => {
      const local = time - row.index * stagger - travel;
      const next = local < 0 ? 'pending' : 'final';
      if (row.key === next) return;
      const arriving = row.key === 'pending' && next === 'final' && local < 200;
      row.key = next;
      if (next === 'pending') {
        row.status.dataset.pending = '';
        row.word.classList.remove('flap');
      } else {
        delete row.status.dataset.pending;
        if (arriving) {
          row.word.classList.remove('flap');
          void row.word.offsetWidth;
          row.word.classList.add('flap');
        }
      }
    };

    rows.forEach((row, index) => { row.index = index; });

    const draw = (time) => {
      ctx.clearRect(0, 0, width, height);
      rows.forEach((row, index) => {
        const geo = geometry[index];
        if (!geo) return;
        setStatus(row, time);
        const local = time - index * stagger;
        if (local <= 0) return;
        const travelProgress = ease(local / travel);
        const settleProgress = clamp01((local - travel) / settle);
        const headX = geo.x0 + (geo.x1 - geo.x0) * travelProgress;
        const decided = local >= travel;
        const color = decided ? (row.stays ? COLORS.signal : COLORS.dim) : COLORS.glyph;
        const trailLength = Math.min(140, headX - geo.x0);
        const fade = decided ? (row.stays ? 0.35 + 0.65 * (1 - settleProgress) : 1 - settleProgress) : 1;

        if (trailLength > 0 && fade > 0.01) {
          const gradient = ctx.createLinearGradient(headX - trailLength, 0, headX, 0);
          gradient.addColorStop(0, 'rgba(0,0,0,0)');
          gradient.addColorStop(1, color);
          ctx.globalAlpha = fade;
          ctx.fillStyle = gradient;
          ctx.fillRect(headX - trailLength, geo.y - 1, trailLength, 2);
        }
        if (decided && row.stays) {
          ctx.globalAlpha = 0.28 * ease(settleProgress);
          ctx.fillStyle = COLORS.signal;
          ctx.fillRect(geo.x0, geo.y - 1, geo.xEnd - geo.x0, 2);
        }
        if (!decided || !row.stays) {
          const drop = decided ? ease(settleProgress) * 14 : 0;
          ctx.globalAlpha = decided ? 1 - settleProgress : 1;
          ctx.fillStyle = color;
          roundRect(ctx, headX - 7, geo.y - 4 + drop, 14, 8, 2);
          ctx.fill();
        }
        if (decided && row.stays) {
          const pulse = 1 - settleProgress;
          const radius = 6 + 16 * ease(Math.min(settleProgress * 2, 1)) * (0.5 + 0.5 * pulse);
          const bloom = ctx.createRadialGradient(geo.x1, geo.cy, 0, geo.x1, geo.cy, radius);
          bloom.addColorStop(0, 'rgba(255,199,44,0.55)');
          bloom.addColorStop(1, 'rgba(255,199,44,0)');
          ctx.globalAlpha = 0.45 + 0.55 * pulse;
          ctx.fillStyle = bloom;
          ctx.beginPath();
          ctx.arc(geo.x1, geo.cy, radius, 0, Math.PI * 2);
          ctx.fill();
        }
      });
      ctx.globalAlpha = 1;
      board.classList.toggle('sorted', time >= duration);
    };

    measure();
    const instance = timeline(duration, draw);
    timelines.push(instance);
    instance.seek(0);

    const run = () => {
      board.classList.remove('sorted');
      instance.seek(0);
      instance.play(0);
    };
    playOnceOnView(board, instance, run);
    replay.addEventListener('click', run);
    if ('ResizeObserver' in window) {
      new ResizeObserver(() => {
        measure();
        draw(instance.time);
      }).observe(board);
    }
  }

  function setupRail() {
    const wrap = document.querySelector('.rail-wrap');
    const canvas = wrap?.querySelector('.rail-diagram');
    const button = wrap?.querySelector('.rail-replay');
    if (!wrap || !canvas || !button) return;
    const ctx = getContext(canvas);
    if (!ctx) return;

    wrap.hidden = false;
    const count = 7;
    const archived = new Set([1, 3, 4, 6]);
    const height = 150;
    const duration = 900;
    const stagger = 80;
    let width = 0;
    let direction = 1;
    let archivedState = true;

    const measure = () => {
      width = wrap.getBoundingClientRect().width;
      sizeCanvas(canvas, ctx, width, height);
    };

    const draw = (time) => {
      ctx.clearRect(0, 0, width, height);
      const left = 4;
      const right = width - 4;
      const inboxY = 40;
      const mailY = 112;
      ctx.font = '700 11px Archivo, system-ui, sans-serif';
      ctx.fillStyle = COLORS.ink;
      ctx.textBaseline = 'alphabetic';
      ctx.fillText('INBOX', left, inboxY - 14);
      ctx.fillText('ALL MAIL · DATED RECOVERY LABEL', left, mailY + 28);
      ctx.textAlign = 'right';
      ctx.font = '600 11px "Geist Mono", monospace';
      ctx.fillText(`illustration · same ${count} · none deleted`, right, inboxY - 14);
      ctx.textAlign = 'left';
      ctx.fillStyle = COLORS.ink;
      ctx.fillRect(left, inboxY, right - left, 2);
      ctx.globalAlpha = 0.45;
      ctx.fillRect(left, mailY, right - left, 2);
      ctx.globalAlpha = 1;

      const span = (right - left - 40) / (count - 1);
      for (let index = 0; index < count; index += 1) {
        const x = left + 20 + span * index;
        let progress = 0;
        if (archived.has(index)) {
          const order = [...archived].indexOf(index);
          const local = clamp01((time - order * stagger) / (duration - stagger * (archived.size - 1)));
          const eased = ease(local);
          progress = direction === 1 ? eased : 1 - eased;
        }
        const y = inboxY + 1 + (mailY - inboxY) * progress;
        const xOffset = Math.sin(progress * Math.PI) * 10;
        ctx.fillStyle = COLORS.ink;
        roundRect(ctx, x - 9 + xOffset, y - 6, 18, 12, 3);
        if (progress > 0.5) {
          ctx.lineWidth = 2;
          ctx.strokeStyle = COLORS.ink;
          ctx.stroke();
          ctx.globalAlpha = clamp01((progress - 0.5) * 2);
          ctx.fillRect(x + 11 + xOffset, y - 4, 10, 8);
          ctx.globalAlpha = 1;
        } else {
          ctx.fill();
        }
      }
    };

    measure();
    const instance = timeline(duration, draw);
    timelines.push(instance);
    const play = (nextDirection) => {
      direction = nextDirection;
      archivedState = nextDirection === 1;
      button.textContent = archivedState ? 'Show a restore' : 'Show the archive again';
      if (reduced) instance.seek(duration);
      else instance.play(0);
    };

    if (reduced) {
      instance.seek(duration);
    } else {
      instance.seek(0);
      playOnceOnView(wrap, instance, () => play(1));
    }
    button.addEventListener('click', () => play(archivedState ? -1 : 1));
    if ('ResizeObserver' in window) {
      new ResizeObserver(() => {
        measure();
        draw(instance.time);
      }).observe(wrap);
    }
  }

  function setupBoarding() {
    const band = document.querySelector('.install-band');
    const steps = band?.querySelector('.install-steps');
    if (!band || !steps || reduced) return;
    band.classList.add('will-board');
    const reveal = () => band.classList.add('boarding');
    steps.addEventListener('focusin', reveal);
    playOnceOnView(steps, { resume() {}, pause() {} }, reveal);
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
    const list = document.querySelector('.faq-list');
    if (!list) return;
    requestAnimationFrame(() => list.classList.add('faq-ready'));
  }

  if (reduced) document.documentElement.classList.add('motion-reduced');
  setupSortTrack();
  setupRail();
  setupBoarding();
  setupCopyFlap();
  setupFaq();
  document.fonts?.ready.then(() => timelines.forEach((instance) => {
    if (!instance.playing && !instance.paused) instance.seek(instance.time);
  }));
})();
