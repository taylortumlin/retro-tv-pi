import { fetchEpg, fetchNowPlaying } from '../api/epg';
import type { Channel, Programme, EpgData, NowPlaying } from '../types/epg';

let channels = $state<Channel[]>([]);
let programmes = $state<Programme[]>([]);
let lastUpdate = $state<string | null>(null);
let nowPlaying = $state<NowPlaying[]>([]);
let loading = $state(false);
let error = $state<string | null>(null);

export function getEpgStore() {
  return {
    get channels() { return channels; },
    get programmes() { return programmes; },
    get lastUpdate() { return lastUpdate; },
    get nowPlaying() { return nowPlaying; },
    get loading() { return loading; },
    get error() { return error; },

    async load() {
      loading = true;
      error = null;
      try {
        const data: EpgData = await fetchEpg();
        channels = data.channels;
        programmes = data.programmes;
        lastUpdate = data.last_update;
      } catch (e) {
        error = e instanceof Error ? e.message : 'Failed to load EPG';
      } finally {
        loading = false;
      }
    },

    async loadNowPlaying() {
      try {
        nowPlaying = await fetchNowPlaying();
      } catch {
        // silently fail — now playing is supplementary
      }
    },

    getProgrammesForChannel(channelId: string): Programme[] {
      return programmes.filter(p => p.channel_id === channelId);
    },

    getCurrentProgramme(channelId: string): Programme | undefined {
      const now = Date.now() / 1000;
      return programmes.find(
        p => p.channel_id === channelId && p.start_ts <= now && p.stop_ts > now
      );
    },

    getUpcoming(channelId: string, limit = 5): Programme[] {
      const now = Date.now() / 1000;
      return programmes
        .filter(p => p.channel_id === channelId && p.stop_ts > now)
        .sort((a, b) => a.start_ts - b.start_ts)
        .slice(0, limit);
    },

    getAllCategories(): string[] {
      const cats = new Set<string>();
      for (const p of programmes) {
        for (const c of p.categories) cats.add(c);
      }
      return [...cats].sort();
    },
  };
}

export const epgStore = getEpgStore();
