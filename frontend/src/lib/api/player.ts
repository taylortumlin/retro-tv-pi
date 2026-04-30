import { get, post } from './client';
import type { PlayerStatus } from '../types/player';

export function getPlayerStatus(): Promise<PlayerStatus> {
  return get<PlayerStatus>('/api/player/status');
}

export function tuneChannel(ch: number): Promise<PlayerStatus> {
  return post<PlayerStatus>(`/api/player/channel/${ch}`);
}

export function toggleMute(): Promise<PlayerStatus> {
  return post<PlayerStatus>('/api/player/mute');
}

export function togglePause(): Promise<PlayerStatus> {
  return post<PlayerStatus>('/api/player/pause');
}

export function channelUp(): Promise<PlayerStatus> {
  return post<PlayerStatus>('/api/player/channel/up');
}

export function channelDown(): Promise<PlayerStatus> {
  return post<PlayerStatus>('/api/player/channel/down');
}
