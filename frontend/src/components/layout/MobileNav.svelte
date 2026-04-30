<script lang="ts">
  import { uiStore, type ViewName } from '../../lib/stores/ui';
  import Icon from '../shared/Icon.svelte';

  const items: { view: ViewName; label: string; icon: string }[] = [
    { view: 'guide', label: 'Guide', icon: 'grid' },
    { view: 'discover', label: 'Discover', icon: 'search' },
    { view: 'player', label: 'Watch', icon: 'play' },
    { view: 'weather', label: 'Weather', icon: 'cloud' },
    { view: 'admin', label: 'Admin', icon: 'settings' },
  ];
</script>

<nav class="mobile-nav glass" aria-label="Mobile navigation">
  {#each items as item}
    <button
      class="mobile-nav-item"
      class:active={uiStore.activeView === item.view}
      onclick={() => uiStore.navigate(item.view)}
      aria-current={uiStore.activeView === item.view ? 'page' : undefined}
      aria-label={item.label}
    >
      <Icon name={item.icon} size={22} strokeWidth={1.5} />
      <span class="label">{item.label}</span>
    </button>
  {/each}
</nav>

<style>
  .mobile-nav {
    display: none;
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    z-index: 100;
    height: var(--mobile-nav-height);
    border-top: 1px solid var(--color-border);
    padding: 0 var(--sp-2);
    justify-content: space-around;
    align-items: center;
  }

  @media (max-width: 768px) {
    .mobile-nav { display: flex; }
  }

  .mobile-nav-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2px;
    padding: var(--sp-1) var(--sp-3);
    border-radius: var(--radius-md);
    color: var(--color-text-muted);
    transition: color var(--duration-fast) var(--ease-out);
    min-width: 48px;
  }

  .mobile-nav-item.active {
    color: var(--color-accent);
  }

  .label {
    font-size: 0.625rem;
    font-weight: var(--font-weight-semibold);
  }
</style>
