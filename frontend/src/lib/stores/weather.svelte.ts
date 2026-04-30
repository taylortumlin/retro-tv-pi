import { fetchWeather, fetchNews } from '../api/weather';
import type { CurrentWeather, HourlyForecast, DailyForecast } from '../types/weather';
import type { NewsHeadline } from '../types/weather';

let current = $state<CurrentWeather | null>(null);
let hourly = $state<HourlyForecast[]>([]);
let daily = $state<DailyForecast[]>([]);
let news = $state<NewsHeadline[]>([]);
let loading = $state(false);

export function getWeatherStore() {
  return {
    get current() { return current; },
    get hourly() { return hourly; },
    get daily() { return daily; },
    get news() { return news; },
    get loading() { return loading; },

    async load() {
      loading = true;
      try {
        const data = await fetchWeather();
        current = data.current;
        hourly = data.hourly;
        daily = data.daily;
      } catch {
        // weather is non-critical
      } finally {
        loading = false;
      }
    },

    async loadNews() {
      try {
        news = await fetchNews();
      } catch {
        // news is non-critical
      }
    },
  };
}

export const weatherStore = getWeatherStore();
