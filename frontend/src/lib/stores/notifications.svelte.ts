import { remindersStore } from './reminders.svelte';
import { epgStore } from './epg.svelte';
import { formatTime } from '../utils/time';

const CHECK_INTERVAL_MS = 30_000;
const FIRE_LEAD_SECONDS = 60;     // notify when programme starts within next 60s
const STALE_AFTER_SECONDS = 60;   // don't fire if we missed the window by > 60s

type Permission = NotificationPermission | 'unsupported';

let permission = $state<Permission>(
  typeof window !== 'undefined' && 'Notification' in window
    ? Notification.permission
    : 'unsupported'
);

let intervalId: ReturnType<typeof setInterval> | null = null;

function check() {
  if (permission !== 'granted') return;
  if (typeof Notification === 'undefined') return;

  const now = Date.now() / 1000;
  for (const r of remindersStore.all) {
    if (r.notified) continue;
    const delta = r.startTs - now;
    if (delta > FIRE_LEAD_SECONDS) continue;       // not yet
    if (delta < -STALE_AFTER_SECONDS) continue;    // missed it

    const ch = epgStore.channels.find(c => c.id === r.channelId);
    const title = `${r.programmeTitle} is starting`;
    const body = ch
      ? `Ch ${ch.number} ${ch.name} · ${formatTime(new Date(r.startTs * 1000).toISOString())}`
      : `Starts at ${formatTime(new Date(r.startTs * 1000).toISOString())}`;

    try {
      new Notification(title, {
        body,
        icon: '/static/icons/icon-192.png',
        tag: `pitv-reminder-${r.channelId}-${r.startTs}`,
        requireInteraction: false,
      });
    } catch {
      // Some browsers throw when Notification is constructed without
      // a service worker on mobile; swallow and try again next tick.
      continue;
    }

    remindersStore.markNotified(r.channelId, r.startTs);
  }
}

export const notificationsStore = {
  get permission() { return permission; },
  get supported() { return permission !== 'unsupported'; },

  async request(): Promise<Permission> {
    if (typeof Notification === 'undefined') {
      permission = 'unsupported';
      return permission;
    }
    try {
      const result = await Notification.requestPermission();
      permission = result;
    } catch {
      // Older Safari throws if you call requestPermission outside a user
      // gesture; fall back to the current value.
      permission = Notification.permission;
    }
    return permission;
  },

  init() {
    if (typeof window === 'undefined') return;
    if (!('Notification' in window)) {
      permission = 'unsupported';
      return;
    }
    permission = Notification.permission;
    if (intervalId) clearInterval(intervalId);
    intervalId = setInterval(check, CHECK_INTERVAL_MS);
    // Run once immediately so reminders that came due while the tab was
    // backgrounded fire as soon as it gains focus again.
    check();
    // Also tick right when the tab regains focus.
    window.addEventListener('focus', check);
    document.addEventListener('visibilitychange', () => {
      if (document.visibilityState === 'visible') check();
    });
  },

  // Expose for tests.
  _check: check,
};
