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

const app = mount(App, {
  target: document.getElementById('app')!,
});

export default app;
