'use strict';

const copyButton = document.getElementById('copy-command');
const command = document.getElementById('install-command');
const status = document.getElementById('copy-status');

if (copyButton && command && status && navigator.clipboard?.writeText) {
  copyButton.hidden = false;
  let pending = false;
  copyButton.addEventListener('click', async () => {
    if (pending) return;
    pending = true;
    copyButton.setAttribute('aria-disabled', 'true');
    copyButton.setAttribute('aria-busy', 'true');
    try {
      await navigator.clipboard.writeText(command.textContent.trim());
      status.textContent = 'Copied. Paste it into Terminal when you’re ready.';
      copyButton.textContent = 'Copy again';
    } catch {
      status.textContent = 'Couldn’t copy. Select the command above and copy it manually.';
    } finally {
      pending = false;
      copyButton.removeAttribute('aria-disabled');
      copyButton.removeAttribute('aria-busy');
    }
  });
}
