import type { Channel } from '../types/epg';

let currentChannel = $state<Channel | null>(null);
let muted = $state(false);
let paused = $state(false);
let volume = $state(100);
let isFullscreen = $state(false);

export function getPlayerStore() {
  return {
    get currentChannel() { return currentChannel; },
    get muted() { return muted; },
    get paused() { return paused; },
    get volume() { return volume; },
    get isFullscreen() { return isFullscreen; },

    setChannel(ch: Channel | null) { currentChannel = ch; },
    setMuted(m: boolean) { muted = m; },
    toggleMute() { muted = !muted; },
    setPaused(p: boolean) { paused = p; },
    togglePause() { paused = !paused; },
    setVolume(v: number) { volume = Math.max(0, Math.min(100, v)); },
    setFullscreen(f: boolean) { isFullscreen = f; },
  };
}

export const playerStore = getPlayerStore();
