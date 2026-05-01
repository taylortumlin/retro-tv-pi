import { describe, it, expect, beforeEach, afterEach } from 'vitest';

// jsdom has no Notification API, so we install a fake constructor with a
// mutable `permission` static. The store reads `Notification.permission`
// each time -- the bug being fixed is that previously it cached the value
// at init time and never refreshed on focus.

class FakeNotification {
  static permission: NotificationPermission = 'default';
  static async requestPermission(): Promise<NotificationPermission> {
    return FakeNotification.permission;
  }
  constructor(_title: string, _opts?: NotificationOptions) {
    /* no-op for tests; we don't assert on construction here */
  }
}

describe('notifications store - permission re-sync on focus', () => {
  beforeEach(() => {
    FakeNotification.permission = 'default';
    (globalThis as any).Notification = FakeNotification;
    // Make `'Notification' in window` true under jsdom.
    (window as any).Notification = FakeNotification;
  });

  afterEach(() => {
    delete (globalThis as any).Notification;
    delete (window as any).Notification;
  });

  it('refreshes cached permission when window regains focus', async () => {
    const mod = await import('./notifications.svelte?t=' + Date.now());
    mod.notificationsStore.init();
    expect(mod.notificationsStore.permission).toBe('default');

    // User unblocks notifications in browser settings -> Notification.permission
    // flips to 'granted' but the store doesn't know yet.
    FakeNotification.permission = 'granted';
    expect(mod.notificationsStore.permission).toBe('default');

    // Focus event should pull the latest value from the live API.
    window.dispatchEvent(new Event('focus'));
    expect(mod.notificationsStore.permission).toBe('granted');
  });

  it('refreshes when document becomes visible', async () => {
    const mod = await import('./notifications.svelte?t=' + Date.now());
    mod.notificationsStore.init();
    expect(mod.notificationsStore.permission).toBe('default');

    FakeNotification.permission = 'denied';
    Object.defineProperty(document, 'visibilityState', {
      configurable: true,
      get: () => 'visible',
    });
    document.dispatchEvent(new Event('visibilitychange'));
    expect(mod.notificationsStore.permission).toBe('denied');
  });
});
