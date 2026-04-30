<script lang="ts">
  import type { Snippet } from 'svelte';

  interface Props {
    icon?: string;
    title: string;
    message?: string;
    children?: Snippet;
  }

  let { icon = '📺', title, message = '', children }: Props = $props();
</script>

<div class="empty-state">
  <span class="icon">{icon}</span>
  <h3>{title}</h3>
  {#if message}<p>{message}</p>{/if}
  {#if children}
    <div class="actions">
      {@render children()}
    </div>
  {/if}
</div>

<style>
  .empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: var(--sp-3);
    padding: var(--sp-16) var(--sp-6);
    text-align: center;
  }
  .icon {
    font-size: 3rem;
    opacity: 0.5;
  }
  h3 {
    font-size: var(--text-lg);
    font-weight: var(--font-weight-semibold);
    color: var(--color-text);
  }
  p {
    font-size: var(--text-sm);
    color: var(--color-text-muted);
    max-width: 300px;
  }
  .actions {
    margin-top: var(--sp-2);
  }
</style>
