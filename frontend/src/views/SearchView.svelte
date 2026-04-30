<script lang="ts">
  import { epgStore } from '../lib/stores/epg';
  import { uiStore } from '../lib/stores/ui';
  import { fuzzySearch } from '../lib/utils/search';
  import BrowseCard from '../components/discovery/BrowseCard.svelte';
  import Icon from '../components/shared/Icon.svelte';

  let inputEl: HTMLInputElement;
  let query = $state('');

  let results = $derived(fuzzySearch(epgStore.programmes, query));

  $effect(() => {
    if (epgStore.channels.length === 0) epgStore.load();
    inputEl?.focus();
  });
</script>

<div class="search-view">
  <div class="search-header">
    <div class="search-input-wrap">
      <Icon name="search" size={20} />
      <input
        bind:this={inputEl}
        bind:value={query}
        type="search"
        placeholder="Search programmes..."
        aria-label="Search programmes"
      />
      {#if query}
        <button class="clear-btn" onclick={() => { query = ''; inputEl?.focus(); }} aria-label="Clear search">
          <Icon name="close" size={18} />
        </button>
      {/if}
    </div>
    <button class="cancel-btn" onclick={() => uiStore.navigate('guide')}>Cancel</button>
  </div>

  {#if query && results.length > 0}
    <div class="results-grid">
      {#each results.slice(0, 50) as programme}
        <BrowseCard {programme} />
      {/each}
    </div>
    <p class="result-count">{results.length} result{results.length !== 1 ? 's' : ''}</p>
  {:else if query}
    <div class="no-results">
      <p>No programmes found for "{query}"</p>
    </div>
  {:else}
    <div class="search-hint">
      <p>Search by title, genre, or episode</p>
    </div>
  {/if}
</div>

<style>
  .search-view {
    padding: var(--sp-5);
    max-width: 1000px;
    margin: 0 auto;
  }

  .search-header {
    display: flex;
    align-items: center;
    gap: var(--sp-3);
    margin-bottom: var(--sp-6);
  }

  .search-input-wrap {
    flex: 1;
    display: flex;
    align-items: center;
    gap: var(--sp-2);
    padding: var(--sp-3) var(--sp-4);
    background: var(--color-bg-card);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-lg);
    color: var(--color-text-muted);
  }

  .search-input-wrap:focus-within {
    border-color: var(--color-accent);
    box-shadow: var(--shadow-glow);
  }

  .search-input-wrap input {
    flex: 1;
    background: none;
    border: none;
    outline: none;
    font-size: var(--text-lg);
    color: var(--color-text);
  }

  .search-input-wrap input::placeholder {
    color: var(--color-text-muted);
  }

  .clear-btn {
    display: flex;
    color: var(--color-text-muted);
  }

  .clear-btn:hover {
    color: var(--color-text);
  }

  .cancel-btn {
    color: var(--color-accent);
    font-weight: var(--font-weight-semibold);
    white-space: nowrap;
  }

  .results-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: var(--sp-4);
  }

  .result-count {
    margin-top: var(--sp-4);
    text-align: center;
    font-size: var(--text-sm);
    color: var(--color-text-muted);
  }

  .no-results, .search-hint {
    display: flex;
    justify-content: center;
    padding: var(--sp-16);
    color: var(--color-text-muted);
  }
</style>
