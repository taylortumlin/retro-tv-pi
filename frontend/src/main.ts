import { mount } from 'svelte';
import './app.css';
import App from './App.svelte';
import { uiStore } from './lib/stores/ui';
import { initKeyboard } from './lib/utils/keyboard';

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

const app = mount(App, {
  target: document.getElementById('app')!,
});

export default app;
