export function clickOutside(node: HTMLElement, callback: () => void) {
  function handler(e: MouseEvent) {
    if (!node.contains(e.target as Node)) {
      callback();
    }
  }

  document.addEventListener('click', handler, true);

  return {
    destroy() {
      document.removeEventListener('click', handler, true);
    },
  };
}
