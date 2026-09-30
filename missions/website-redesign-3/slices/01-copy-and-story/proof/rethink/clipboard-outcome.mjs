export function clipboardOutcome(mode, result, command, context) {
 if (!context.sectionScriptLoaded || context.resources.length || context.errors.length) return false;
 return mode === 'success' ? result.written === command && /Copied/i.test(result.status) && result.focused === 'copy' :
  mode === 'denied' ? result.selection === command && /Copy manually: press Command-C\./.test(result.status) && result.focused === 'copy' :
  result.hidden && result.command === command;
}
