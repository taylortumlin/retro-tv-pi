<script lang="ts">
  import type { HourlyForecast } from '../../lib/types/weather';
  import { formatHour } from '../../lib/utils/time';

  interface Props {
    hourly: HourlyForecast[];
    unit: 'F' | 'C';
  }

  let { hourly, unit }: Props = $props();

  let items = $derived(hourly.slice(0, 12));
  let maxTemp = $derived(Math.max(...items.map(h => h.temperature ?? 0)));
  let minTemp = $derived(Math.min(...items.map(h => h.temperature ?? 0)));
  let range = $derived(maxTemp - minTemp || 1);
</script>

<div class="hourly-chart">
  <h3>Next 12 Hours</h3>
  <div class="chart-scroll">
    {#each items as hour}
      {@const temp = hour.temperature ?? 0}
      {@const pct = ((temp - minTemp) / range) * 100}
      <div class="chart-bar">
        <span class="bar-temp tabular-nums">{Math.round(temp)}°</span>
        <div class="bar-track">
          <div class="bar-fill" style:height="{Math.max(pct, 8)}%"></div>
        </div>
        <span class="bar-time tabular-nums">{formatHour(hour.time)}</span>
        {#if hour.precip_probability > 0}
          <span class="bar-precip">{hour.precip_probability}%</span>
        {/if}
      </div>
    {/each}
  </div>
</div>

<style>
  .hourly-chart {
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

  .chart-scroll {
    display: flex;
    gap: var(--sp-3);
    overflow-x: auto;
    scrollbar-width: none;
  }

  .chart-scroll::-webkit-scrollbar { display: none; }

  .chart-bar {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: var(--sp-1);
    min-width: 40px;
    flex-shrink: 0;
  }

  .bar-temp {
    font-size: var(--text-xs);
    font-weight: var(--font-weight-semibold);
  }

  .bar-track {
    width: 24px;
    height: 80px;
    background: var(--color-surface);
    border-radius: var(--radius-sm);
    display: flex;
    align-items: flex-end;
    overflow: hidden;
  }

  .bar-fill {
    width: 100%;
    background: linear-gradient(to top, var(--color-accent), var(--color-accent-hover));
    border-radius: var(--radius-sm);
    transition: height var(--duration-normal) var(--ease-out);
  }

  .bar-time {
    font-size: var(--text-xs);
    color: var(--color-text-muted);
  }

  .bar-precip {
    font-size: 0.5625rem;
    color: var(--color-accent);
  }
</style>
