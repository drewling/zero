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

if (typeof document.querySelectorAll === 'function') {
  const alphabet = 'ABCDEFGHIJKLMNOPRSTUVWY.';
  const mobile = typeof matchMedia === 'function' && matchMedia('(max-width: 760px)').matches;
  const boardSelector = mobile ? '.mobile-board' : '.desktop-board';
  const tiles = [...document.querySelectorAll(`${boardSelector} .tile[data-final]:not(.blank)`)];
  const reducedMotion = typeof matchMedia === 'function' && matchMedia('(prefers-reduced-motion: reduce)').matches;

  if (!reducedMotion) {
    tiles.forEach((tile, index) => {
      const startDelay = index * 18;
      setTimeout(() => {
        let ticks = 0;
        const finalText = tile.dataset.final;
        tile.classList.add('flip');
        const timer = setInterval(() => {
          tile.textContent = alphabet[Math.floor(Math.random() * alphabet.length)];
          ticks += 1;
          if (ticks >= 4) {
            clearInterval(timer);
            tile.textContent = finalText;
            tile.classList.remove('flip');
          }
        }, 32);
      }, startDelay);
    });
  }
}
