<script lang="ts">
  import { uiStore, type ViewName } from '../../lib/stores/ui';

  const items: { view: ViewName; label: string; icon: string }[] = [
    { view: 'guide', label: 'Guide', icon: 'M4 6h16M4 12h16M4 18h16' },
    { view: 'discover', label: 'Discover', icon: 'M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z' },
    { view: 'player', label: 'Watch', icon: 'M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z M21 12a9 9 0 11-18 0 9 9 0 0118 0z' },
    { view: 'weather', label: 'Weather', icon: 'M3 15a4 4 0 004 4h9a5 5 0 10-.1-9.999 5.002 5.002 0 10-9.78 2.096A4.001 4.001 0 003 15z' },
    { view: 'admin', label: 'Admin', icon: 'M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z M15 12a3 3 0 11-6 0 3 3 0 016 0z' },
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
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
        <path d={item.icon} />
      </svg>
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
