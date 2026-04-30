<script lang="ts">
  import { uiStore } from '../../lib/stores/ui';
  import { fly, fade } from 'svelte/transition';
</script>

{#if uiStore.toasts.length > 0}
  <div class="toast-container" aria-live="polite">
    {#each uiStore.toasts as toast (toast.id)}
      <div class="toast {toast.type}" transition:fly={{ y: 20, duration: 250 }}>
        {toast.message}
      </div>
    {/each}
  </div>
{/if}

<style>
  .toast-container {
    position: fixed;
    bottom: calc(var(--mobile-nav-height) + var(--sp-4));
    left: 50%;
    transform: translateX(-50%);
    z-index: 9000;
    display: flex;
    flex-direction: column;
    gap: var(--sp-2);
    pointer-events: none;
  }
  .toast {
    padding: var(--sp-3) var(--sp-5);
    border-radius: var(--radius-md);
    font-size: var(--text-sm);
    font-weight: var(--font-weight-semibold);
    backdrop-filter: var(--glass-blur);
    -webkit-backdrop-filter: var(--glass-blur);
    box-shadow: var(--shadow-lg);
    white-space: nowrap;
  }
  .info {
    background: rgba(18, 18, 26, 0.9);
    border: 1px solid var(--color-border);
  }
  .success {
    background: rgba(52, 199, 89, 0.2);
    border: 1px solid var(--color-success);
    color: var(--color-success);
  }
  .error {
    background: rgba(255, 69, 58, 0.2);
    border: 1px solid var(--color-error);
    color: var(--color-error);
  }
  .warning {
    background: rgba(255, 159, 10, 0.2);
    border: 1px solid var(--color-warning);
    color: var(--color-warning);
  }
</style>
