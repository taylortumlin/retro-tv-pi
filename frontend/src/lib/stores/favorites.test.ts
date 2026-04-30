import { describe, it, expect, beforeEach } from 'vitest';

describe('favorites store - corrupt localStorage', () => {
  beforeEach(() => localStorage.clear());

  it('survives non-array JSON', async () => {
    localStorage.setItem('pitv-favorites', 'null');
    const mod = await import('./favorites.svelte?t=' + Date.now());
    // Set is what the rest of the app expects; never an undefined.
    expect(mod.favoritesStore.ids instanceof Set).toBe(true);
    expect(mod.favoritesStore.ids.size).toBe(0);
  });

  it('survives object payload', async () => {
    localStorage.setItem('pitv-favorites', '{"foo":"bar"}');
    const mod = await import('./favorites.svelte?t=' + Date.now());
    expect(mod.favoritesStore.ids instanceof Set).toBe(true);
  });
});
