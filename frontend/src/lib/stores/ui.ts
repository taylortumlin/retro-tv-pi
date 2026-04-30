import type { Programme } from '../types/epg';

export type ViewName = 'guide' | 'discover' | 'player' | 'weather' | 'admin' | 'search';

let activeView = $state<ViewName>('guide');
let searchQuery = $state('');
let modalProgramme = $state<Programme | null>(null);
let toasts = $state<Toast[]>([]);
let isMobile = $state(false);

let _toastId = 0;

export interface Toast {
  id: number;
  message: string;
  type: 'info' | 'success' | 'error' | 'warning';
}

export function getUiStore() {
  return {
    get activeView() { return activeView; },
    get searchQuery() { return searchQuery; },
    get modalProgramme() { return modalProgramme; },
    get toasts() { return toasts; },
    get isMobile() { return isMobile; },

    navigate(view: ViewName) {
      activeView = view;
      const path = view === 'guide' ? '/' : `/${view}`;
      history.pushState({ view }, '', path);
    },

    setSearch(q: string) { searchQuery = q; },

    openProgramme(p: Programme) { modalProgramme = p; },
    closeProgramme() { modalProgramme = null; },

    toast(message: string, type: Toast['type'] = 'info') {
      const id = ++_toastId;
      toasts = [...toasts, { id, message, type }];
      setTimeout(() => {
        toasts = toasts.filter(t => t.id !== id);
      }, 4000);
    },

    setMobile(m: boolean) { isMobile = m; },

    initFromUrl() {
      const path = window.location.pathname;
      if (path === '/' || path === '') activeView = 'guide';
      else if (path === '/discover') activeView = 'discover';
      else if (path === '/player') activeView = 'player';
      else if (path === '/weather') activeView = 'weather';
      else if (path === '/admin') activeView = 'admin';
      else if (path === '/search') activeView = 'search';
      else activeView = 'guide';
    },
  };
}

export const uiStore = getUiStore();
