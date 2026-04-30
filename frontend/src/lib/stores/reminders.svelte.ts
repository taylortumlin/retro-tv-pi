const STORAGE_KEY = 'pitv-reminders';

export interface Reminder {
  programmeTitle: string;
  channelId: string;
  startTs: number;
  notified: boolean;
}

function loadFromStorage(): Reminder[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    // Defensive: a corrupt entry (null, "oops", 42, {}) parses fine but
    // crashes downstream `.some()` / `.map()` calls and takes down the
    // SPA on boot until storage is manually cleared.
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

let reminders = $state<Reminder[]>(loadFromStorage());

function persist() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(reminders));
}

export function getRemindersStore() {
  return {
    get all() { return reminders; },

    hasReminder(channelId: string, startTs: number): boolean {
      return reminders.some(r => r.channelId === channelId && r.startTs === startTs);
    },

    add(r: Omit<Reminder, 'notified'>) {
      if (!this.hasReminder(r.channelId, r.startTs)) {
        reminders = [...reminders, { ...r, notified: false }];
        persist();
      }
    },

    remove(channelId: string, startTs: number) {
      reminders = reminders.filter(r => !(r.channelId === channelId && r.startTs === startTs));
      persist();
    },

    markNotified(channelId: string, startTs: number) {
      reminders = reminders.map(r =>
        r.channelId === channelId && r.startTs === startTs
          ? { ...r, notified: true }
          : r
      );
      persist();
    },

    cleanup() {
      const now = Date.now() / 1000;
      reminders = reminders.filter(r => r.startTs > now - 3600);
      persist();
    },
  };
}

export const remindersStore = getRemindersStore();
