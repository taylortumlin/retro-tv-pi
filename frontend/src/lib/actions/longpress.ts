export function longpress(node: HTMLElement, duration = 500) {
  let timer: ReturnType<typeof setTimeout>;

  function start() {
    timer = setTimeout(() => {
      node.dispatchEvent(new CustomEvent('longpress'));
    }, duration);
  }

  function cancel() {
    clearTimeout(timer);
  }

  node.addEventListener('pointerdown', start);
  node.addEventListener('pointerup', cancel);
  node.addEventListener('pointerleave', cancel);

  return {
    destroy() {
      clearTimeout(timer);
      node.removeEventListener('pointerdown', start);
      node.removeEventListener('pointerup', cancel);
      node.removeEventListener('pointerleave', cancel);
    },
  };
}
