<script lang="ts">
  import type { Programme } from '../../lib/types/epg';
  import BrowseCard from './BrowseCard.svelte';

  interface Props {
    title: string;
    programmes: Programme[];
  }

  let { title, programmes }: Props = $props();

  // Deduplicate by title and limit
  let unique = $derived.by(() => {
    const seen = new Set<string>();
    return programmes.filter(p => {
      if (seen.has(p.title)) return false;
      seen.add(p.title);
      return true;
    }).slice(0, 20);
  });
</script>

{#if unique.length > 0}
  <section class="browse-row" aria-label="{title}">
    <h3 class="row-title">{title}</h3>
    <div class="row-scroll">
      {#each unique as programme (programme.channel_id + programme.start)}
        <div class="card-wrap">
          <BrowseCard {programme} />
        </div>
      {/each}
    </div>
  </section>
{/if}

<style>
  .browse-row {
    display: flex;
    flex-direction: column;
    gap: var(--sp-3);
  }

  .row-title {
    padding: 0 var(--sp-5);
    font-size: var(--text-lg);
    font-weight: var(--font-weight-bold);
  }

  .row-scroll {
    display: flex;
    gap: var(--sp-3);
    padding: 0 var(--sp-5);
    overflow-x: auto;
    scroll-snap-type: x mandatory;
    scrollbar-width: none;
  }

  .row-scroll::-webkit-scrollbar { display: none; }

  .card-wrap {
    flex: 0 0 200px;
    scroll-snap-align: start;
  }

  @media (max-width: 768px) {
    .card-wrap { flex: 0 0 160px; }
  }
</style>
