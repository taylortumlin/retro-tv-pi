export function focusTrap(node: HTMLElement) {
  const focusable = 'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])';

  function handler(e: KeyboardEvent) {
    if (e.key !== 'Tab') return;

    const elements = node.querySelectorAll<HTMLElement>(focusable);
    if (elements.length === 0) return;

    const first = elements[0];
    const last = elements[elements.length - 1];

    if (e.shiftKey && document.activeElement === first) {
      e.preventDefault();
      last.focus();
    } else if (!e.shiftKey && document.activeElement === last) {
      e.preventDefault();
      first.focus();
    }
  }

  node.addEventListener('keydown', handler);

  // Focus first focusable element
  const first = node.querySelector<HTMLElement>(focusable);
  if (first) first.focus();

  return {
    destroy() {
      node.removeEventListener('keydown', handler);
    },
  };
}
