<script lang="ts">
  import type { CurrentWeather } from '../../lib/types/weather';

  interface Props {
    weather: CurrentWeather;
  }

  let { weather }: Props = $props();

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

<div class="current-weather glass">
  <div class="weather-main">
    <span class="weather-icon">{weatherIcons[weather.weather_code] || '🌡️'}</span>
    <div class="temp-wrap">
      <span class="temperature">{Math.round(weather.temperature ?? 0)}°</span>
      <span class="unit">{weather.unit}</span>
    </div>
  </div>

  <div class="weather-details">
    <h3 class="condition">{weather.condition}</h3>
    <p class="location">{weather.location}</p>
    <div class="detail-grid">
      <div class="detail">
        <span class="detail-label">Feels Like</span>
        <span class="detail-value">{Math.round(weather.feels_like ?? 0)}°</span>
      </div>
      <div class="detail">
        <span class="detail-label">Humidity</span>
        <span class="detail-value">{weather.humidity ?? '--'}%</span>
      </div>
      <div class="detail">
        <span class="detail-label">Wind</span>
        <span class="detail-value">{weather.wind_speed ?? '--'} mph</span>
      </div>
      <div class="detail">
        <span class="detail-label">UV Index</span>
        <span class="detail-value">{weather.uv_index ?? '--'}</span>
      </div>
    </div>
  </div>
</div>

<style>
  .current-weather {
    grid-column: 1 / -1;
    display: flex;
    align-items: center;
    gap: var(--sp-8);
    padding: var(--sp-8);
    border-radius: var(--radius-lg);
  }

  .weather-main {
    display: flex;
    align-items: center;
    gap: var(--sp-4);
  }

  .weather-icon {
    font-size: 4rem;
  }

  .temp-wrap {
    display: flex;
    align-items: flex-start;
  }

  .temperature {
    font-size: 4rem;
    font-weight: var(--font-weight-bold);
    line-height: 1;
  }

  .unit {
    font-size: var(--text-xl);
    color: var(--color-text-secondary);
    margin-top: 0.5rem;
  }

  .weather-details {
    flex: 1;
  }

  .condition {
    font-size: var(--text-xl);
    font-weight: var(--font-weight-semibold);
  }

  .location {
    font-size: var(--text-sm);
    color: var(--color-text-secondary);
    margin-bottom: var(--sp-4);
  }

  .detail-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: var(--sp-3);
  }

  .detail {
    display: flex;
    flex-direction: column;
    gap: 2px;
  }

  .detail-label {
    font-size: var(--text-xs);
    color: var(--color-text-muted);
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  .detail-value {
    font-size: var(--text-base);
    font-weight: var(--font-weight-semibold);
  }

  @media (max-width: 768px) {
    .current-weather {
      flex-direction: column;
      text-align: center;
    }
    .detail-grid {
      grid-template-columns: 1fr 1fr;
    }
  }
</style>
