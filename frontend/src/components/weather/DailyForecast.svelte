<script lang="ts">
  import type { DailyForecast } from '../../lib/types/weather';
  import { formatDay } from '../../lib/utils/time';

  interface Props {
    daily: DailyForecast[];
    unit: 'F' | 'C';
  }

  let { daily, unit }: Props = $props();

  const weatherIcons: Record<number, string> = {
    0: '☀️', 1: '🌤️', 2: '⛅', 3: '☁️',
    45: '🌫️', 48: '🌫️',
    51: '🌦️', 53: '🌧️', 55: '🌧️',
    61: '🌧️', 63: '🌧️', 65: '🌧️',
    71: '🌨️', 73: '🌨️', 75: '🌨️',
    80: '🌦️', 81: '🌧️', 82: '⛈️',
    95: '⛈️', 96: '⛈️', 99: '⛈️',
  };
</script>

<div class="daily-forecast">
  <h3>Daily Forecast</h3>
  <div class="forecast-list">
    {#each daily as day}
      <div class="forecast-day">
        <span class="day-name">{formatDay(day.date)}</span>
        <span class="day-icon">{weatherIcons[day.weather_code] || '🌡️'}</span>
        <span class="day-high tabular-nums">{Math.round(day.high ?? 0)}°</span>
        <span class="day-low tabular-nums">{Math.round(day.low ?? 0)}°</span>
        {#if day.precip_probability > 0}
          <span class="day-precip">{day.precip_probability}%</span>
        {:else}
          <span class="day-precip"></span>
        {/if}
      </div>
    {/each}
  </div>
</div>

<style>
  .daily-forecast {
    background: var(--color-bg-card);
    border-radius: var(--radius-lg);
    border: 1px solid var(--color-border);
    padding: var(--sp-5);
  }

  h3 {
    font-size: var(--text-base);
    font-weight: var(--font-weight-semibold);
    margin-bottom: var(--sp-4);
  }

  .forecast-list {
    display: flex;
    flex-direction: column;
    gap: var(--sp-1);
  }

  .forecast-day {
    display: flex;
    align-items: center;
    gap: var(--sp-3);
    padding: var(--sp-2) 0;
    border-bottom: 1px solid var(--color-border);
  }

  .forecast-day:last-child {
    border-bottom: none;
  }

  .day-name {
    width: 60px;
    font-size: var(--text-sm);
    font-weight: var(--font-weight-semibold);
  }

  .day-icon {
    font-size: 1.25rem;
  }

  .day-high {
    font-weight: var(--font-weight-bold);
    font-size: var(--text-sm);
    width: 32px;
    text-align: right;
  }

  .day-low {
    font-size: var(--text-sm);
    color: var(--color-text-muted);
    width: 32px;
    text-align: right;
  }

  .day-precip {
    font-size: var(--text-xs);
    color: var(--color-accent);
    width: 32px;
    text-align: right;
  }
</style>
