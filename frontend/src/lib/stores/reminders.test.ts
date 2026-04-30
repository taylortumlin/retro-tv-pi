import { describe, it, expect, beforeEach } from 'vitest';

describe('reminders store - corrupt localStorage', () => {
  beforeEach(() => localStorage.clear());

  it('handles non-array JSON without throwing', async () => {
    localStorage.setItem('pitv-reminders', 'null');
    // Re-import to retrigger module-eval-time loadFromStorage. The
    // ?t= query keeps the resolver from returning a cached module.
    const mod = await import('./reminders.svelte?t=' + Date.now());
    expect(Array.isArray(mod.remindersStore.all)).toBe(true);
    expect(mod.remindersStore.all.length).toBe(0);
  });

  it('handles object payload without throwing', async () => {
    localStorage.setItem('pitv-reminders', '{"foo":"bar"}');
    const mod = await import('./reminders.svelte?t=' + Date.now());
    expect(Array.isArray(mod.remindersStore.all)).toBe(true);
  });

  it('handles plain string without throwing', async () => {
    localStorage.setItem('pitv-reminders', '"oops"');
    const mod = await import('./reminders.svelte?t=' + Date.now());
    expect(Array.isArray(mod.remindersStore.all)).toBe(true);
  });
});
