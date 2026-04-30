export interface AdminConfig {
  admin: { pin: string; session_timeout_minutes: number };
  channels: ConfigChannel[];
  default_channel: number;
  default_theme: string;
  ersatztv_url: string;
  guide_port: number;
  player_url: string;
  mpv_options: Record<string, unknown>;
  mpv_socket: string;
  ticker: TickerConfig;
  web_port: number;
}

export interface ConfigChannel {
  number: number;
  name: string;
}

export interface TickerConfig {
  forecast_days: number;
  messages: string[];
  news: {
    feeds: NewsFeed[];
    max_headlines: number;
    show_headlines: boolean;
  };
  show_now_playing: boolean;
  speed: number;
  weather: {
    latitude: number;
    longitude: number;
    location_name: string;
    temperature_unit: string;
  };
  weatherstar_music_url: string;
  weatherstar_playlist: { title: string; url: string }[];
}

export interface NewsFeed {
  name: string;
  url: string;
}

export interface SystemStatus {
  uptime: string;
  memory: { total_mb: number; available_mb: number; used_mb: number };
  disk: { total_gb: number; free_gb: number; used_gb: number };
  cpu_temp_c: number | null;
  load_average: number[];
  tv_guide_status: string;
  tv_player_status: string;
  ersatztv_reachable: boolean;
  epg_last_update: string | null;
  epg_channels: number;
  epg_programmes: number;
  weather_ok: boolean;
  weather_last_fetch: number;
}

export interface BackupEntry {
  filename: string;
  size: number;
  created: string;
}

export interface DiscoveredChannel {
  id: string;
  number: string;
  name: string;
}
