<script lang="ts">
  import { epgStore } from '../../lib/stores/epg';
  import { uiStore } from '../../lib/stores/ui';
  import { fuzzySearch } from '../../lib/utils/search';
  import BrowseCard from './BrowseCard.svelte';

  let results = $derived(fuzzySearch(epgStore.programmes, uiStore.searchQuery));
</script>

<div class="search-results">
  {#if results.length > 0}
    <p class="count">{results.length} result{results.length !== 1 ? 's' : ''}</p>
    <div class="results-grid">
      {#each results.slice(0, 40) as programme (programme.channel_id + programme.start)}
        <BrowseCard {programme} />
      {/each}
    </div>
  {:else if uiStore.searchQuery}
    <p class="no-results">No results for "{uiStore.searchQuery}"</p>
  {/if}
</div>

<style>
  .search-results {
    padding: var(--sp-4) var(--sp-5);
  }

  .count {
    font-size: var(--text-sm);
    color: var(--color-text-muted);
    margin-bottom: var(--sp-4);
  }

  .results-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
    gap: var(--sp-4);
  }

  .no-results {
    text-align: center;
    padding: var(--sp-16);
    color: var(--color-text-muted);
  }
</style>
