export function formatTime(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });
}

export function formatDate(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleDateString([], { weekday: 'short', month: 'short', day: 'numeric' });
}

export function formatDay(iso: string): string {
  const d = new Date(iso);
  const today = new Date();
  const tomorrow = new Date(today);
  tomorrow.setDate(today.getDate() + 1);

  if (d.toDateString() === today.toDateString()) return 'Today';
  if (d.toDateString() === tomorrow.toDateString()) return 'Tomorrow';
  return d.toLocaleDateString([], { weekday: 'short' });
}

export function formatHour(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleTimeString([], { hour: 'numeric' });
}

export function getProgress(startTs: number, stopTs: number): number {
  const now = Date.now() / 1000;
  if (now < startTs) return 0;
  if (now >= stopTs) return 100;
  return ((now - startTs) / (stopTs - startTs)) * 100;
}

export function formatDuration(minutes: number): string {
  if (minutes < 60) return `${minutes}m`;
  const h = Math.floor(minutes / 60);
  const m = minutes % 60;
  return m > 0 ? `${h}h ${m}m` : `${h}h`;
}

export function isLive(startTs: number, stopTs: number): boolean {
  const now = Date.now() / 1000;
  return now >= startTs && now < stopTs;
}

export function clockTime(): string {
  return new Date().toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });
}

// Returns [startTs, stopTs] (unix seconds) for tonight's primetime block.
// If the current time is past the end of today's window, returns tomorrow's.
export function tonightWindow(startHour = 19, endHour = 23): [number, number] {
  const now = new Date();
  const start = new Date(now);
  start.setHours(startHour, 0, 0, 0);
  const stop = new Date(now);
  stop.setHours(endHour, 0, 0, 0);
  if (now.getTime() >= stop.getTime()) {
    start.setDate(start.getDate() + 1);
    stop.setDate(stop.getDate() + 1);
  }
  return [Math.floor(start.getTime() / 1000), Math.floor(stop.getTime() / 1000)];
}
