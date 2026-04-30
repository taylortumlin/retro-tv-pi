const STORAGE_KEY = 'pitv-favorites';

function loadFromStorage(): Set<string> {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return new Set();
    const parsed = JSON.parse(raw);
    // Defensive: a corrupt entry (null, "oops", 42, {}) parses fine but
    // would crash `new Set(parsed)` and take down the SPA on boot.
    return Array.isArray(parsed) ? new Set(parsed) : new Set();
  } catch {
    return new Set();
  }
}

let favoriteIds = $state<Set<string>>(loadFromStorage());

function persist() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify([...favoriteIds]));
}

export function getFavoritesStore() {
  return {
    get ids() { return favoriteIds; },

    isFavorite(channelId: string): boolean {
      return favoriteIds.has(channelId);
    },

    toggle(channelId: string) {
      const next = new Set(favoriteIds);
      if (next.has(channelId)) next.delete(channelId);
      else next.add(channelId);
      favoriteIds = next;
      persist();
    },

    add(channelId: string) {
      if (!favoriteIds.has(channelId)) {
        favoriteIds = new Set([...favoriteIds, channelId]);
        persist();
      }
    },

    remove(channelId: string) {
      if (favoriteIds.has(channelId)) {
        const next = new Set(favoriteIds);
        next.delete(channelId);
        favoriteIds = next;
        persist();
      }
    },
  };
}

export const favoritesStore = getFavoritesStore();
