export type ThemeName = 'modern' | 'prevue' | 'comcast' | 'crt';

export const THEME_LABELS: Record<ThemeName, string> = {
  modern: 'Modern Dark',
  prevue: 'Prevue Classic',
  comcast: 'Comcast Blue',
  crt: 'CRT Retro',
};

const THEMES: ThemeName[] = ['modern', 'prevue', 'comcast', 'crt'];
const STORAGE_KEY = 'pi-tv-theme';

let active = $state<ThemeName>('modern');

function apply(t: ThemeName) {
  active = t;
  if (typeof document === 'undefined') return;
  if (t === 'modern') {
    document.documentElement.removeAttribute('data-theme');
  } else {
    document.documentElement.setAttribute('data-theme', t);
  }
  try { localStorage.setItem(STORAGE_KEY, t); } catch {}
}

export const themeStore = {
  get active() { return active; },
  get themes() { return THEMES; },
  label(t: ThemeName) { return THEME_LABELS[t]; },
  set(t: ThemeName) { apply(t); },
  cycle() {
    const i = THEMES.indexOf(active);
    apply(THEMES[(i + 1) % THEMES.length]);
  },
  init() {
    try {
      const saved = localStorage.getItem(STORAGE_KEY) as ThemeName | null;
      if (saved && THEMES.includes(saved)) apply(saved);
    } catch {}
  },
};
