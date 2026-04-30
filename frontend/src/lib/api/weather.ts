import { get } from './client';
import type { WeatherData, NewsHeadline, TickerData } from '../types/weather';

export function fetchWeather(): Promise<WeatherData> {
  return get<WeatherData>('/api/weather');
}

export function fetchNews(): Promise<NewsHeadline[]> {
  return get<NewsHeadline[]>('/api/news');
}

export function fetchTicker(): Promise<TickerData> {
  return get<TickerData>('/api/ticker');
}
