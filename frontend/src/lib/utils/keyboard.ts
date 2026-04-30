import { uiStore } from '../stores/ui';

type KeyHandler = (e: KeyboardEvent) => void;

const handlers: Record<string, KeyHandler> = {};

export function registerShortcut(key: string, handler: KeyHandler) {
  handlers[key] = handler;
}

export function unregisterShortcut(key: string) {
  delete handlers[key];
}

export function initKeyboard() {
  window.addEventListener('keydown', (e) => {
    // Don't handle shortcuts when typing in inputs.
    const tag = (e.target as HTMLElement).tagName;
    if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') return;

    // Escape always handled, even with a modal open -- it closes the modal.
    if (e.key === 'Escape') {
      if (uiStore.modalProgramme) {
        uiStore.closeProgramme();
        return;
      }
    }

    // While a modal is open, suppress every other shortcut. Otherwise
    // pressing g/u/t/q/p/w/d/'/' navigates the SPA underneath the modal,
    // and on PlayerView 'g' fires both the global "go to guide" handler
    // and PlayerView's own MiniGuide toggle.
    if (uiStore.modalProgramme) return;

    if (e.key === '/' && !e.ctrlKey && !e.metaKey) {
      e.preventDefault();
      uiStore.navigate('search');
      return;
    }

    const handler = handlers[e.key];
    if (handler) handler(e);
  });
}
