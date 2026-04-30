export interface CurrentWeather {
  temperature: number | null;
  feels_like: number | null;
  condition: string;
  weather_code: number;
  wind_speed: number | null;
  humidity: number | null;
  uv_index: number | null;
  unit: 'F' | 'C';
  location: string;
}

export interface HourlyForecast {
  time: string;
  temperature: number | null;
  weather_code: number;
  condition: string;
  precip_probability: number;
}

export interface DailyForecast {
  date: string;
  high: number | null;
  low: number | null;
  weather_code: number;
  condition: string;
  precip_probability: number;
  uv_index: number | null;
}

export interface WeatherData {
  current: CurrentWeather | null;
  hourly: HourlyForecast[];
  daily: DailyForecast[];
  forecast_days: number;
}

export interface NewsHeadline {
  source: string;
  title: string;
  summary: string;
  published: string;
}

export interface TickerData {
  weather: CurrentWeather | null;
  now_playing: TickerNowPlaying[];
  messages: string[];
  speed: number;
  news: NewsHeadline[];
}

export interface TickerNowPlaying {
  channel_number: string;
  channel_name: string;
  title: string;
  episode: string;
}
