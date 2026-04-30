<script lang="ts">
  import { epgStore } from '../lib/stores/epg';
  import BrowseRow from '../components/discovery/BrowseRow.svelte';
  import SearchBar from '../components/discovery/SearchBar.svelte';
  import SearchResults from '../components/discovery/SearchResults.svelte';
  import { uiStore } from '../lib/stores/ui';
  import type { Programme } from '../lib/types/epg';

  let searchActive = $state(false);

  $effect(() => {
    if (epgStore.channels.length === 0) epgStore.load();
  });

  // Group programmes by category for browse rows
  let categoryGroups = $derived.by(() => {
    const now = Date.now() / 1000;
    const upcoming = epgStore.programmes.filter(p => p.stop_ts > now);
    const groups = new Map<string, Programme[]>();

    // "On Now" section
    const onNow = upcoming.filter(p => p.start_ts <= now && p.stop_ts > now);
    if (onNow.length) groups.set('On Now', onNow);

    // "Tonight" — programmes starting after 6 PM today
    const todayEvening = new Date();
    todayEvening.setHours(18, 0, 0, 0);
    const tonightTs = todayEvening.getTime() / 1000;
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    tomorrow.setHours(6, 0, 0, 0);
    const tomorrowTs = tomorrow.getTime() / 1000;
    const tonight = upcoming.filter(p => p.start_ts >= tonightTs && p.start_ts < tomorrowTs);
    if (tonight.length) groups.set('Tonight', tonight);

    // Group by genre categories
    for (const p of upcoming) {
      for (const cat of p.categories) {
        if (!groups.has(cat)) groups.set(cat, []);
        groups.get(cat)!.push(p);
      }
    }

    return groups;
  });
</script>

<div class="discover-view">
  <div class="discover-header">
    <h1>Discover</h1>
    <SearchBar onFocus={() => { searchActive = true; }} onClear={() => { searchActive = false; uiStore.setSearch(''); }} />
  </div>

  {#if searchActive && uiStore.searchQuery}
    <SearchResults />
  {:else}
    <div class="browse-rows">
      {#each [...categoryGroups] as [category, programmes]}
        <BrowseRow title={category} {programmes} />
      {/each}
    </div>
  {/if}
</div>

<style>
  .discover-view {
    padding: var(--sp-4) 0;
  }

  .discover-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: var(--sp-4);
    padding: 0 var(--sp-5);
    margin-bottom: var(--sp-6);
  }

  h1 {
    font-size: var(--text-2xl);
    font-weight: var(--font-weight-bold);
  }

  .browse-rows {
    display: flex;
    flex-direction: column;
    gap: var(--sp-8);
  }
</style>
