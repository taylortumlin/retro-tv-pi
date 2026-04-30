<script lang="ts">
  import type { Snippet } from 'svelte';

  interface Props {
    variant?: 'default' | 'live' | 'accent' | 'gold';
    small?: boolean;
    children?: Snippet;
  }

  let { variant = 'default', small = false, children }: Props = $props();
</script>

<span class="badge {variant}" class:small>
  {#if children}{@render children()}{/if}
</span>

<style>
  .badge {
    display: inline-flex;
    align-items: center;
    gap: var(--sp-1);
    padding: 2px var(--sp-2);
    border-radius: var(--radius-full);
    font-size: var(--text-xs);
    font-weight: var(--font-weight-semibold);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    white-space: nowrap;
  }
  .small {
    font-size: 0.625rem;
    padding: 1px var(--sp-1);
  }
  .default {
    background: var(--color-surface);
    color: var(--color-text-secondary);
  }
  .live {
    background: var(--color-live);
    color: white;
  }
  .accent {
    background: var(--color-accent-subtle);
    color: var(--color-accent);
  }
  .gold {
    background: rgba(240, 192, 64, 0.15);
    color: var(--color-gold);
  }
</style>
