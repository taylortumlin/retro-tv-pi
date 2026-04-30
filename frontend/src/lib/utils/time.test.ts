import { describe, it, expect, beforeAll, afterAll, vi } from 'vitest';
import {
  formatDuration,
  getProgress,
  isLive,
  tonightWindow,
} from './time';

describe('formatDuration', () => {
  it('renders minutes only when < 60', () => {
    expect(formatDuration(0)).toBe('0m');
    expect(formatDuration(30)).toBe('30m');
    expect(formatDuration(59)).toBe('59m');
  });

  it('renders hours when divisible', () => {
    expect(formatDuration(60)).toBe('1h');
    expect(formatDuration(180)).toBe('3h');
  });

  it('renders hours + minutes', () => {
    expect(formatDuration(75)).toBe('1h 15m');
    expect(formatDuration(150)).toBe('2h 30m');
  });
});

describe('getProgress', () => {
  it('returns 0 before start', () => {
    const now = Date.now() / 1000;
    expect(getProgress(now + 100, now + 200)).toBe(0);
  });

  it('returns 100 after stop', () => {
    const now = Date.now() / 1000;
    expect(getProgress(now - 200, now - 100)).toBe(100);
  });

  it('returns ~50 mid-program', () => {
    const now = Date.now() / 1000;
    const start = now - 50;
    const stop = now + 50;
    const p = getProgress(start, stop);
    expect(p).toBeGreaterThanOrEqual(49);
    expect(p).toBeLessThanOrEqual(51);
  });
});

describe('isLive', () => {
  it('true while currently airing', () => {
    const now = Date.now() / 1000;
    expect(isLive(now - 10, now + 10)).toBe(true);
  });

  it('false before start', () => {
    const now = Date.now() / 1000;
    expect(isLive(now + 60, now + 120)).toBe(false);
  });

  it('false at exactly stop_ts', () => {
    const now = Date.now() / 1000;
    expect(isLive(now - 60, now)).toBe(false);
  });
});

describe('tonightWindow', () => {
  // Force a deterministic "now" so the boundary cases are testable.
  beforeAll(() => {
    vi.useFakeTimers();
  });
  afterAll(() => {
    vi.useRealTimers();
  });

  it('uses today when called before primetime', () => {
    // 4 PM local
    vi.setSystemTime(new Date(2026, 4, 1, 16, 0, 0));
    const [start, stop] = tonightWindow(19, 23);
    expect(new Date(start * 1000).getDate()).toBe(1);
    expect(new Date(start * 1000).getHours()).toBe(19);
    expect(new Date(stop * 1000).getHours()).toBe(23);
  });

  it('advances to tomorrow when called after primetime', () => {
    // 1 AM local — past tonight's 11 PM end
    vi.setSystemTime(new Date(2026, 4, 2, 1, 0, 0));
    const [start] = tonightWindow(19, 23);
    expect(new Date(start * 1000).getDate()).toBe(2);
    expect(new Date(start * 1000).getHours()).toBe(19);
  });

  it('honors custom start/end hours', () => {
    vi.setSystemTime(new Date(2026, 4, 1, 12, 0, 0));
    const [start, stop] = tonightWindow(20, 22);
    expect(new Date(start * 1000).getHours()).toBe(20);
    expect(new Date(stop * 1000).getHours()).toBe(22);
  });
});
