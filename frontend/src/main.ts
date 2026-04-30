import { mount } from 'svelte';
import './app.css';
import App from './App.svelte';
import { uiStore } from './lib/stores/ui';
import { themeStore } from './lib/stores/theme.svelte';
import { initKeyboard, registerShortcut } from './lib/utils/keyboard';

themeStore.init();
uiStore.initFromUrl();

// Handle browser back/forward
window.addEventListener('popstate', () => {
  uiStore.initFromUrl();
});

// Detect mobile
const mql = window.matchMedia('(max-width: 768px)');
uiStore.setMobile(mql.matches);
mql.addEventListener('change', (e) => uiStore.setMobile(e.matches));

initKeyboard();

registerShortcut('T', (e) => {
  if (!e.shiftKey) return;
  e.preventDefault();
  themeStore.cycle();
  uiStore.toast(`Theme: ${themeStore.label(themeStore.active)}`, 'info');
});

// View-toggle shortcuts (single lowercase keys, no modifiers).
// The underlying initKeyboard() guard already skips inputs/textareas/selects.
const viewKeys: Record<string, 'guide' | 'upnext' | 'tonight' | 'quad' | 'prevue' | 'weather' | 'discover'> = {
  g: 'guide',
  u: 'upnext',
  t: 'tonight',
  q: 'quad',
  p: 'prevue',
  w: 'weather',
  d: 'discover',
};
for (const [key, view] of Object.entries(viewKeys)) {
  registerShortcut(key, (e) => {
    if (e.ctrlKey || e.metaKey || e.altKey || e.shiftKey) return;
    e.preventDefault();
    uiStore.navigate(view);
  });
}

const app = mount(App, {
  target: document.getElementById('app')!,
});

export default app;
