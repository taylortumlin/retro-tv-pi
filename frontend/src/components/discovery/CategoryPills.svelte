<script lang="ts">
  interface Props {
    categories: string[];
    selected: string | null;
    onSelect: (cat: string | null) => void;
  }

  let { categories, selected, onSelect }: Props = $props();
</script>

<div class="category-pills" role="listbox" aria-label="Filter by category">
  <button
    class="pill"
    class:active={!selected}
    onclick={() => onSelect(null)}
    role="option"
    aria-selected={!selected}
  >
    All
  </button>
  {#each categories as cat}
    <button
      class="pill"
      class:active={selected === cat}
      onclick={() => onSelect(selected === cat ? null : cat)}
      role="option"
      aria-selected={selected === cat}
    >
      {cat}
    </button>
  {/each}
</div>

<style>
  .category-pills {
    display: flex;
    gap: var(--sp-2);
    overflow-x: auto;
    scrollbar-width: none;
    flex: 1;
  }

  .category-pills::-webkit-scrollbar { display: none; }

  .pill {
    padding: var(--sp-1) var(--sp-3);
    border-radius: var(--radius-full);
    font-size: var(--text-xs);
    font-weight: var(--font-weight-semibold);
    color: var(--color-text-secondary);
    background: var(--color-surface);
    white-space: nowrap;
    transition: all var(--duration-fast) var(--ease-out);
  }

  .pill:hover {
    background: var(--color-surface-hover);
    color: var(--color-text);
  }

  .pill.active {
    background: var(--color-accent-subtle);
    color: var(--color-accent);
  }
</style>
