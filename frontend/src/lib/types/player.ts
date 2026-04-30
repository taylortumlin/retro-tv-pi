export interface PlayerStatus {
  channel: string | number;
  channel_name: string;
  muted: boolean;
  paused: boolean;
  error?: string;
}
