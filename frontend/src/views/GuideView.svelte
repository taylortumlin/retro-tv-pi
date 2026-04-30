<script lang="ts">
  import { epgStore } from '../lib/stores/epg';
  import { uiStore } from '../lib/stores/ui';
  import HeroCard from '../components/guide/HeroCard.svelte';
  import NowStrip from '../components/guide/NowStrip.svelte';
  import GuideGrid from '../components/guide/GuideGrid.svelte';
  import MobileGuide from '../components/guide/MobileGuide.svelte';
  import CategoryPills from '../components/discovery/CategoryPills.svelte';
  import SkeletonLoader from '../components/shared/SkeletonLoader.svelte';
  import Icon from '../components/shared/Icon.svelte';

  let selectedCategory = $state<string | null>(null);
  let showFavoritesOnly = $state(false);

  $effect(() => {
    epgStore.load();
    epgStore.loadNowPlaying();
    const interval = setInterval(() => {
      epgStore.loadNowPlaying();
    }, 30_000);
    return () => clearInterval(interval);
  });
</script>

<div class="guide-view">
  {#if epgStore.loading && epgStore.channels.length === 0}
    <div class="loading-hero">
      <SkeletonLoader width="100%" height="320px" radius="0" />
    </div>
    <div class="loading-strip">
      {#each Array(6) as _}
        <SkeletonLoader width="200px" height="80px" radius="var(--radius-md)" />
      {/each}
    </div>
  {:else if epgStore.error}
    <div class="error-banner">
      <p>Failed to load guide data: {epgStore.error}</p>
      <button onclick={() => epgStore.load()}>Retry</button>
    </div>
  {:else}
    <HeroCard />
    <NowStrip />

    <div class="guide-filters">
      <CategoryPills
        categories={epgStore.getAllCategories()}
        selected={selectedCategory}
        onSelect={(cat) => { selectedCategory = cat; }}
      />
      <button
        class="fav-filter"
        class:active={showFavoritesOnly}
        onclick={() => { showFavoritesOnly = !showFavoritesOnly; }}
        aria-pressed={showFavoritesOnly}
      >
        <Icon name={showFavoritesOnly ? 'star-filled' : 'star'} size={16} fill={showFavoritesOnly ? 'var(--color-gold)' : 'none'} />
        Favorites
      </button>
    </div>

    {#if uiStore.isMobile}
      <MobileGuide category={selectedCategory} favoritesOnly={showFavoritesOnly} />
    {:else}
      <GuideGrid category={selectedCategory} favoritesOnly={showFavoritesOnly} />
    {/if}
  {/if}
</div>

<style>
  .guide-view {
    display: flex;
    flex-direction: column;
  }

  .loading-hero {
    margin-bottom: var(--sp-4);
  }

  .loading-strip {
    display: flex;
    gap: var(--sp-3);
    padding: 0 var(--sp-5);
    overflow: hidden;
  }

  .error-banner {
    display: flex;
    align-items: center;
    gap: var(--sp-4);
    padding: var(--sp-5);
    margin: var(--sp-5);
    background: rgba(255, 69, 58, 0.1);
    border: 1px solid var(--color-error);
    border-radius: var(--radius-md);
  }

  .error-banner button {
    padding: var(--sp-2) var(--sp-4);
    background: var(--color-accent);
    color: white;
    border-radius: var(--radius-sm);
    font-weight: var(--font-weight-semibold);
    white-space: nowrap;
  }

  .guide-filters {
    display: flex;
    align-items: center;
    gap: var(--sp-3);
    padding: var(--sp-3) var(--sp-5);
  }

  .fav-filter {
    display: flex;
    align-items: center;
    gap: var(--sp-1);
    padding: var(--sp-1) var(--sp-3);
    border-radius: var(--radius-full);
    font-size: var(--text-sm);
    font-weight: var(--font-weight-semibold);
    color: var(--color-text-secondary);
    transition: all var(--duration-fast) var(--ease-out);
    white-space: nowrap;
  }

  .fav-filter:hover {
    background: var(--color-surface-hover);
    color: var(--color-text);
  }

  .fav-filter.active {
    background: rgba(240, 192, 64, 0.15);
    color: var(--color-gold);
  }
</style>
