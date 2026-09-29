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
