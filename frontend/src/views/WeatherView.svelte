<script lang="ts">
  import { weatherStore } from '../lib/stores/weather';
  import CurrentWeatherCard from '../components/weather/CurrentWeather.svelte';
  import HourlyChart from '../components/weather/HourlyChart.svelte';
  import DailyForecast from '../components/weather/DailyForecast.svelte';
  import NewsHeadlines from '../components/weather/NewsHeadlines.svelte';
  import NewsTicker from '../components/weather/NewsTicker.svelte';
  import Spinner from '../components/shared/Spinner.svelte';

  $effect(() => {
    weatherStore.load();
    weatherStore.loadNews();
    const interval = setInterval(() => {
      weatherStore.load();
      weatherStore.loadNews();
    }, 300_000);
    return () => clearInterval(interval);
  });
</script>

<div class="weather-view">
  {#if weatherStore.loading && !weatherStore.current}
    <div class="loading"><Spinner size={32} /></div>
  {:else if weatherStore.current}
    <div class="weather-grid">
      <CurrentWeatherCard weather={weatherStore.current} />
      <HourlyChart hourly={weatherStore.hourly} unit={weatherStore.current.unit} />
      <DailyForecast daily={weatherStore.daily} unit={weatherStore.current.unit} />
      <NewsHeadlines headlines={weatherStore.news} />
    </div>
  {:else}
    <div class="empty">
      <p>Weather data unavailable</p>
    </div>
  {/if}

  {#if weatherStore.news.length > 0}
    <NewsTicker headlines={weatherStore.news} />
  {/if}
</div>

<style>
  .weather-view {
    padding: var(--sp-5);
    max-width: 1200px;
    margin: 0 auto;
  }

  .weather-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: var(--sp-5);
  }

  @media (max-width: 768px) {
    .weather-grid {
      grid-template-columns: 1fr;
    }
  }

  .loading, .empty {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 300px;
    color: var(--color-text-muted);
  }
</style>
