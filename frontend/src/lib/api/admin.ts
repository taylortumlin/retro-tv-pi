import { get, post, put } from './client';
import type { AdminConfig, SystemStatus, BackupEntry, DiscoveredChannel } from '../types/admin';

export function login(pin: string): Promise<{ ok: boolean }> {
  return post('/admin/api/auth/login', { pin });
}

export function logout(): Promise<{ ok: boolean }> {
  return post('/admin/api/auth/logout');
}

export function checkAuth(): Promise<{ authed: boolean }> {
  return get('/admin/api/auth/check');
}

export function getConfig(): Promise<AdminConfig> {
  return get('/admin/api/config');
}

export function putConfig(config: AdminConfig): Promise<{ saved: boolean; restart_needed: boolean; services: string[] }> {
  return put('/admin/api/config', config);
}

export function putConfigSection(name: string, data: unknown): Promise<{ saved: boolean; restart_needed: boolean; services: string[] }> {
  return put(`/admin/api/config/section/${name}`, data);
}

export function getStatus(): Promise<SystemStatus> {
  return get('/admin/api/status');
}

export function testErsatztv(url?: string): Promise<{ ok: boolean; status_code?: number; channels_found?: number; error?: string }> {
  return post('/admin/api/status/test-ersatztv', url ? { url } : {});
}

export function testWeather(opts?: { latitude?: number; longitude?: number; temperature_unit?: string }): Promise<{ ok: boolean; temperature?: number; condition?: string; unit?: string; error?: string }> {
  return post('/admin/api/status/test-weather', opts || {});
}

export function testFeed(url: string): Promise<{ ok: boolean; entry_count?: number; sample_titles?: string[]; error?: string }> {
  return post('/admin/api/status/test-feed', { url });
}

export function testStream(chNum: number): Promise<{ ok: boolean; latency_ms?: number; bytes?: number; error?: string }> {
  return post(`/admin/api/status/test-stream/${chNum}`);
}

export function discoverChannels(): Promise<{ ok: boolean; channels?: DiscoveredChannel[]; error?: string }> {
  return get('/admin/api/channels/discover');
}

export function restartService(svc: string): Promise<Record<string, { ok: boolean; output: string }>> {
  return post(`/admin/api/services/restart/${svc}`);
}

export function getServiceLogs(svc: string): Promise<{ ok: boolean; lines?: string[]; error?: string }> {
  return get(`/admin/api/services/logs/${svc}`);
}

export function createBackup(): Promise<{ ok: boolean; filename: string }> {
  return post('/admin/api/config/backup');
}

export function listBackups(): Promise<BackupEntry[]> {
  return get('/admin/api/config/backups');
}

export function restoreBackup(filename: string): Promise<{ ok: boolean; restored: string }> {
  return post(`/admin/api/config/restore/${filename}`);
}

export function refreshEpg(): Promise<{ ok: boolean; channels: number; programmes: number; last_update: string }> {
  return post('/admin/api/epg/refresh');
}
