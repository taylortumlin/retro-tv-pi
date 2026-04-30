<script lang="ts">
  import type { NewsHeadline } from '../../lib/types/weather';

  interface Props {
    headlines: NewsHeadline[];
  }

  let { headlines }: Props = $props();
  let expanded = $state<number | null>(null);
</script>

<div class="news-headlines">
  <h3>Headlines</h3>
  <div class="headline-list">
    {#each headlines.slice(0, 15) as item, i}
      <button
        class="headline-item"
        class:expanded={expanded === i}
        onclick={() => { expanded = expanded === i ? null : i; }}
        aria-expanded={expanded === i}
      >
        <div class="headline-header">
          <span class="headline-source">{item.source}</span>
          {#if item.published}<span class="headline-time">{item.published}</span>{/if}
        </div>
        <p class="headline-title">{item.title}</p>
        {#if expanded === i && item.summary}
          <p class="headline-summary">{item.summary}</p>
        {/if}
      </button>
    {/each}
  </div>
</div>

<style>
  .news-headlines {
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

  .headline-list {
    display: flex;
    flex-direction: column;
    max-height: 400px;
    overflow-y: auto;
  }

  .headline-item {
    display: flex;
    flex-direction: column;
    gap: var(--sp-1);
    padding: var(--sp-3) 0;
    border-bottom: 1px solid var(--color-border);
    text-align: left;
    transition: background var(--duration-fast) var(--ease-out);
  }

  .headline-item:hover {
    background: var(--color-surface);
    margin: 0 calc(-1 * var(--sp-3));
    padding-left: var(--sp-3);
    padding-right: var(--sp-3);
    border-radius: var(--radius-sm);
  }

  .headline-header {
    display: flex;
    align-items: center;
    gap: var(--sp-2);
  }

  .headline-source {
    font-size: var(--text-xs);
    font-weight: var(--font-weight-bold);
    color: var(--color-accent);
    text-transform: uppercase;
  }

  .headline-time {
    font-size: var(--text-xs);
    color: var(--color-text-muted);
  }

  .headline-title {
    font-size: var(--text-sm);
    font-weight: var(--font-weight-semibold);
    line-height: 1.3;
  }

  .headline-summary {
    font-size: var(--text-sm);
    color: var(--color-text-secondary);
    line-height: 1.5;
    margin-top: var(--sp-1);
  }
</style>
