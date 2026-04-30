<script lang="ts">
  import { epgStore } from '../lib/stores/epg';
  import { formatTime, formatDay } from '../lib/utils/time';
  import BrowseCard from '../components/discovery/BrowseCard.svelte';
  import SkeletonLoader from '../components/shared/SkeletonLoader.svelte';

  $effect(() => {
    if (epgStore.channels.length === 0) epgStore.load();
  });

  let upcoming = $derived.by(() => {
    const now = Date.now() / 1000;
    return epgStore.programmes
      .filter(p => p.start_ts > now)
      .sort((a, b) => a.start_ts - b.start_ts)
      .slice(0, 60);
  });

  // Group by ISO hour bucket (preserves chronological order in iteration).
  let groups = $derived.by(() => {
    const map = new Map<string, typeof upcoming>();
    for (const p of upcoming) {
      const d = new Date(p.start);
      const key = `${d.toDateString()}|${d.getHours()}`;
      const arr = map.get(key) ?? [];
      arr.push(p);
      map.set(key, arr);
    }
    return [...map.entries()].map(([key, items]) => {
      const [, hour] = key.split('|');
      const day = formatDay(items[0].start);
      const label = `${day} · ${formatTime(items[0].start).replace(/:\d+/, '')}`;
      return { label, items };
    });
  });
</script>

<div class="upnext-view">
  <header class="view-header">
    <h2>Up Next</h2>
    <p class="view-sub">What's coming up across all channels</p>
  </header>

  {#if epgStore.loading && upcoming.length === 0}
    <div class="loading-grid">
      {#each Array(8) as _}
        <SkeletonLoader width="100%" height="220px" radius="var(--radius-md)" />
      {/each}
    </div>
  {:else if upcoming.length === 0}
    <p class="empty">No upcoming programmes.</p>
  {:else}
    {#each groups as group}
      <section class="group">
        <h3 class="group-label">{group.label}</h3>
        <div class="group-grid">
          {#each group.items as programme}
            <BrowseCard {programme} />
          {/each}
        </div>
      </section>
    {/each}
  {/if}
</div>

<style>
  .upnext-view {
    padding: var(--sp-5);
    max-width: 1400px;
    margin: 0 auto;
  }

  .view-header {
    margin-bottom: var(--sp-6);
  }

  .view-header h2 {
    font-size: var(--text-2xl);
    font-weight: var(--font-weight-bold);
  }

  .view-sub {
    margin-top: var(--sp-1);
    font-size: var(--text-sm);
    color: var(--color-text-muted);
  }

  .group {
    margin-bottom: var(--sp-8);
  }

  .group-label {
    font-size: var(--text-base);
    font-weight: var(--font-weight-semibold);
    color: var(--color-text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: var(--sp-3);
    padding-bottom: var(--sp-2);
    border-bottom: 1px solid var(--color-border);
  }

  .group-grid, .loading-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: var(--sp-4);
  }

  .empty {
    padding: var(--sp-10);
    text-align: center;
    color: var(--color-text-muted);
  }
</style>
