<script lang="ts">
  import { epgStore } from '../../lib/stores/epg';
  import { favoritesStore } from '../../lib/stores/favorites';
  import TimeRuler from './TimeRuler.svelte';
  import GuideRow from './GuideRow.svelte';
  import Icon from '../shared/Icon.svelte';
  import type { Channel } from '../../lib/types/epg';

  interface Props {
    category?: string | null;
    favoritesOnly?: boolean;
  }

  let { category = null, favoritesOnly = false }: Props = $props();

  const pixelsPerHour = 300;
  const gridHours = 4;

  // Time shift state
  let shiftHours = $state(0);

  let now = $derived(new Date());
  let gridStartDate = $derived.by(() => {
    const d = new Date(now);
    d.setMinutes(0, 0, 0);
    d.setHours(d.getHours() + shiftHours);
    return d;
  });
  let gridStartTs = $derived(gridStartDate.getTime() / 1000);
  let startHour = $derived(gridStartDate.getHours());

  let filteredChannels = $derived.by(() => {
    let chs: Channel[] = epgStore.channels;

    if (favoritesOnly) {
      chs = chs.filter(ch => favoritesStore.isFavorite(ch.id));
    }

    if (category) {
      const channelIds = new Set(
        epgStore.programmes
          .filter(p => p.categories.includes(category!))
          .map(p => p.channel_id)
      );
      chs = chs.filter(ch => channelIds.has(ch.id));
    }

    return chs;
  });

  function shift(dir: number) {
    shiftHours += dir;
  }
</script>

<section class="guide-grid-section" aria-label="TV Guide Grid">
  <div class="grid-controls">
    <button onclick={() => shift(-1)} aria-label="Go back 1 hour"><Icon name="chevron-left" size={16} /></button>
    <span class="grid-time-label">
      {gridStartDate.toLocaleDateString([], { weekday: 'short', month: 'short', day: 'numeric' })}
    </span>
    <button onclick={() => shift(1)} aria-label="Go forward 1 hour"><Icon name="chevron-right" size={16} /></button>
    {#if shiftHours !== 0}
      <button class="reset-btn" onclick={() => { shiftHours = 0; }}>Now</button>
    {/if}
  </div>

  <div class="grid-scroll" role="grid" aria-label="Programme grid">
    <div class="grid-inner">
      <div class="ruler-row">
        <div class="channel-spacer"></div>
        <TimeRuler {startHour} hours={gridHours} {pixelsPerHour} />
      </div>

      {#each filteredChannels as channel (channel.id)}
        <GuideRow
          {channel}
          programmes={epgStore.getProgrammesForChannel(channel.id)}
          {pixelsPerHour}
          {gridStartTs}
          {gridHours}
        />
      {/each}
    </div>
  </div>
</section>

<style>
  .guide-grid-section {
    padding: 0 var(--sp-5);
  }

  .grid-controls {
    display: flex;
    align-items: center;
    gap: var(--sp-3);
    padding: var(--sp-3) 0;
  }

  .grid-controls button {
    padding: var(--sp-1) var(--sp-3);
    background: var(--color-surface);
    border-radius: var(--radius-sm);
    font-weight: var(--font-weight-semibold);
    font-size: var(--text-sm);
    transition: background var(--duration-fast) var(--ease-out);
  }

  .grid-controls button:hover {
    background: var(--color-surface-hover);
  }

  .reset-btn {
    color: var(--color-accent) !important;
  }

  .grid-time-label {
    font-size: var(--text-sm);
    color: var(--color-text-secondary);
    font-weight: var(--font-weight-semibold);
  }

  .grid-scroll {
    overflow-x: auto;
    overflow-y: auto;
    max-height: calc(100vh - var(--header-height) - 500px);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
    background: var(--color-bg-elevated);
  }

  .grid-inner {
    display: flex;
    flex-direction: column;
    min-width: fit-content;
  }

  .ruler-row {
    display: flex;
    position: sticky;
    top: 0;
    z-index: 10;
  }

  .channel-spacer {
    width: 160px;
    flex-shrink: 0;
    background: var(--color-bg-elevated);
    border-right: 1px solid var(--color-border);
    border-bottom: 1px solid var(--color-border);
    position: sticky;
    left: 0;
    z-index: 11;
  }
</style>
