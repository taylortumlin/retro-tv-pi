import { get, post } from './client';
import type { EpgData, NowPlaying } from '../types/epg';

export function fetchEpg(): Promise<EpgData> {
  return get<EpgData>('/api/epg');
}

export function fetchNowPlaying(): Promise<NowPlaying[]> {
  return get<NowPlaying[]>('/api/now');
}

export function refreshEpg(): Promise<{ status: string; last_update: string }> {
  return post('/api/epg/refresh');
}
