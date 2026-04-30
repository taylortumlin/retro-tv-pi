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
    // Don't handle shortcuts when typing in inputs
    const tag = (e.target as HTMLElement).tagName;
    if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') return;

    // Global shortcuts
    if (e.key === '/' && !e.ctrlKey && !e.metaKey) {
      e.preventDefault();
      uiStore.navigate('search');
      return;
    }

    if (e.key === 'Escape') {
      if (uiStore.modalProgramme) {
        uiStore.closeProgramme();
        return;
      }
    }

    // Registered shortcuts
    const handler = handlers[e.key];
    if (handler) handler(e);
  });
}
