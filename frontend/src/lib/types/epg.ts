export interface Channel {
  id: string;
  number: string;
  name: string;
  logo: string | null;
  categories: string[];
}

export interface Programme {
  channel_id: string;
  title: string;
  subtitle: string;
  start: string;
  stop: string;
  start_ts: number;
  stop_ts: number;
  duration_min: number;
  episode: string;
  rating: string;
  categories: string[];
  poster: string | null;
  thumbnail: string | null;
}

export interface EpgData {
  channels: Channel[];
  programmes: Programme[];
  last_update: string | null;
}

export interface NowPlaying {
  channel: Channel;
  now_playing: Programme | null;
}
