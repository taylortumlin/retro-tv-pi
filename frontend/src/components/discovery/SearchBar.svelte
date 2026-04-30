<script lang="ts">
  import { uiStore } from '../../lib/stores/ui';

  interface Props {
    onFocus?: () => void;
    onClear?: () => void;
  }

  let { onFocus, onClear }: Props = $props();
</script>

<div class="search-bar">
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
    <circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>
  </svg>
  <input
    type="search"
    placeholder="Search..."
    bind:value={uiStore.searchQuery}
    onfocus={onFocus}
    aria-label="Search programmes"
  />
  {#if uiStore.searchQuery}
    <button onclick={() => { uiStore.setSearch(''); onClear?.(); }} aria-label="Clear">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6L6 18M6 6l12 12"/></svg>
    </button>
  {/if}
</div>

<style>
  .search-bar {
    display: flex;
    align-items: center;
    gap: var(--sp-2);
    padding: var(--sp-2) var(--sp-3);
    background: var(--color-bg-card);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-full);
    color: var(--color-text-muted);
    width: 260px;
    transition: all var(--duration-fast) var(--ease-out);
  }

  .search-bar:focus-within {
    border-color: var(--color-accent);
    box-shadow: var(--shadow-glow);
  }

  input {
    flex: 1;
    background: none;
    border: none;
    outline: none;
    font-size: var(--text-sm);
    color: var(--color-text);
  }

  input::placeholder {
    color: var(--color-text-muted);
  }

  button {
    display: flex;
    color: var(--color-text-muted);
  }
</style>
