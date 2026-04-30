import { describe, it, expect, vi, beforeEach } from 'vitest';

// We mock the mpegts.js module so the test never reaches the network and
// we can introspect what config was passed to createPlayer().
const mockPlayer = {
  attachMediaElement: vi.fn(),
  load: vi.fn(),
  play: vi.fn(),
  pause: vi.fn(),
  unload: vi.fn(),
  detachMediaElement: vi.fn(),
  destroy: vi.fn(),
};

vi.mock('mpegts.js', () => ({
  default: {
    isSupported: vi.fn(() => true),
    createPlayer: vi.fn(() => mockPlayer),
  },
}));

import mpegts from 'mpegts.js';
import { createStreamPlayer } from './video';

describe('createStreamPlayer (mpegts path)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  function videoEl(): HTMLVideoElement {
    return document.createElement('video');
  }

  it('passes an absolute URL so the Web Worker loader can resolve it', () => {
    createStreamPlayer(videoEl(), 5);
    const cfg = (mpegts.createPlayer as any).mock.calls[0][0];
    // Must include the document origin — relative '/stream/5.ts' would
    // throw 'Failed to parse URL' inside the mpegts.js worker context.
    expect(cfg.url).toMatch(/^https?:\/\/[^/]+\/stream\/5\.ts$/);
    expect(cfg.url).not.toMatch(/^\/stream/);
  });

  it('uses the live MPEG-TS type', () => {
    createStreamPlayer(videoEl(), 12);
    const cfg = (mpegts.createPlayer as any).mock.calls[0][0];
    expect(cfg.type).toBe('mpegts');
    expect(cfg.isLive).toBe(true);
  });

  it('uses the proven low-stall buffer config (not the aggressive defaults)', () => {
    createStreamPlayer(videoEl(), 3);
    const opts = (mpegts.createPlayer as any).mock.calls[0][1];
    // The aggressive (broken) version we shipped briefly used:
    //   liveBufferLatencyChasing: true, MaxLatency 3, MinRemain 0.5.
    // That stalled continuously against the Flask proxy chunk pattern.
    // The proven config disables chasing and runs with generous remain.
    expect(opts.liveBufferLatencyChasing).toBe(false);
    expect(opts.liveBufferLatencyMaxLatency).toBeGreaterThanOrEqual(15);
    expect(opts.liveBufferLatencyMinRemain).toBeGreaterThanOrEqual(2);
    expect(opts.enableStashBuffer).toBe(true);
    expect(opts.stashInitialSize).toBeGreaterThanOrEqual(256 * 1024);
  });

  it('attaches to the provided <video> element and starts playback on play()', () => {
    const v = videoEl();
    const player = createStreamPlayer(v, 6);
    player.play();
    expect(mockPlayer.attachMediaElement).toHaveBeenCalledWith(v);
    expect(mockPlayer.load).toHaveBeenCalled();
    expect(mockPlayer.play).toHaveBeenCalled();
  });

  it('destroy() tears down in the correct order', () => {
    const player = createStreamPlayer(videoEl(), 8);
    player.destroy();
    const order = [
      mockPlayer.pause,
      mockPlayer.unload,
      mockPlayer.detachMediaElement,
      mockPlayer.destroy,
    ].map(fn => fn.mock.invocationCallOrder[0]);
    // Order matters: pause -> unload -> detach -> destroy. Out-of-order
    // calls leak the underlying fetch and keep ErsatzTV ffmpeg pinned.
    expect(order).toEqual([...order].sort((a, b) => a - b));
  });

  it('mute() and setVolume() forward to the video element', () => {
    const v = videoEl();
    const player = createStreamPlayer(v, 1);
    player.mute(true);
    expect(v.muted).toBe(true);
    player.mute(false);
    expect(v.muted).toBe(false);
    player.setVolume(50);
    expect(v.volume).toBeCloseTo(0.5);
  });
});

describe('createStreamPlayer (HLS fallback)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    (mpegts.isSupported as any).mockReturnValueOnce(false);
  });

  it('uses HLS URL when canPlayType reports MSE-HLS support', () => {
    const v = document.createElement('video');
    // jsdom does not implement HTMLMediaElement.canPlayType — stub it.
    Object.defineProperty(v, 'canPlayType', {
      value: vi.fn(() => 'maybe'),
      writable: true,
    });
    Object.defineProperty(v, 'play', {
      value: vi.fn(() => Promise.resolve()),
      writable: true,
    });
    const player = createStreamPlayer(v, 9);
    player.play();
    expect((v as any).src).toMatch(/\/stream\/9\.m3u8$/);
  });

  it('also uses an absolute URL on the HLS fallback path', () => {
    const v = document.createElement('video');
    Object.defineProperty(v, 'canPlayType', {
      value: vi.fn(() => 'maybe'),
      writable: true,
    });
    Object.defineProperty(v, 'play', {
      value: vi.fn(() => Promise.resolve()),
      writable: true,
    });
    const player = createStreamPlayer(v, 7);
    player.play();
    expect((v as any).src).toMatch(/^https?:\/\/[^/]+\/stream\/7\.m3u8$/);
  });
});
