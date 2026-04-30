<script lang="ts">
  import { uiStore, type ViewName } from '../../lib/stores/ui';
  import { clockTime } from '../../lib/utils/time';
  import Icon from '../shared/Icon.svelte';

  let time = $state(clockTime());

  $effect(() => {
    const interval = setInterval(() => { time = clockTime(); }, 10_000);
    return () => clearInterval(interval);
  });

  const navItems: { view: ViewName; label: string }[] = [
    { view: 'guide', label: 'Guide' },
    { view: 'upnext', label: 'Up Next' },
    { view: 'tonight', label: 'Tonight' },
    { view: 'discover', label: 'Discover' },
    { view: 'player', label: 'Player' },
    { view: 'quad', label: 'Quad' },
    { view: 'weather', label: 'Weather' },
    { view: 'admin', label: 'Admin' },
  ];
</script>

<header class="header glass">
  <a href="/" class="logo" onclick={(e) => { e.preventDefault(); uiStore.navigate('guide'); }}>
    <span class="logo-text">Pi TV</span>
  </a>

  <nav class="nav" aria-label="Main navigation">
    {#each navItems as item}
      <button
        class="nav-pill"
        class:active={uiStore.activeView === item.view}
        onclick={() => uiStore.navigate(item.view)}
        aria-current={uiStore.activeView === item.view ? 'page' : undefined}
      >
        {item.label}
      </button>
    {/each}
  </nav>

  <button class="search-btn" onclick={() => uiStore.navigate('search')} aria-label="Search programmes">
    <Icon name="search" size={18} />
  </button>

  <time class="clock tabular-nums font-mono" aria-live="polite" aria-label="Current time">{time}</time>
</header>

<style>
  .header {
    position: sticky;
    top: 0;
    z-index: 100;
    display: flex;
    align-items: center;
    gap: var(--sp-4);
    height: var(--header-height);
    padding: 0 var(--sp-5);
    border-bottom: 1px solid var(--color-border);
  }

  .logo {
    display: flex;
    align-items: center;
    gap: var(--sp-2);
    text-decoration: none;
    color: var(--color-text);
    flex-shrink: 0;
  }

  .logo-text {
    font-size: var(--text-lg);
    font-weight: var(--font-weight-bold);
    background: linear-gradient(135deg, var(--color-accent), var(--color-gold));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  .nav {
    display: flex;
    gap: var(--sp-1);
    flex: 1;
    justify-content: center;
  }

  .nav-pill {
    padding: var(--sp-2) var(--sp-4);
    border-radius: var(--radius-full);
    font-size: var(--text-sm);
    font-weight: var(--font-weight-semibold);
    color: var(--color-text-secondary);
    transition: all var(--duration-fast) var(--ease-out);
  }

  .nav-pill:hover {
    color: var(--color-text);
    background: var(--color-surface-hover);
  }

  .nav-pill.active {
    color: var(--color-accent);
    background: var(--color-accent-subtle);
  }

  .search-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 36px;
    height: 36px;
    border-radius: var(--radius-full);
    color: var(--color-text-secondary);
    transition: all var(--duration-fast) var(--ease-out);
  }

  .search-btn:hover {
    background: var(--color-surface-hover);
    color: var(--color-text);
  }

  .clock {
    font-size: var(--text-sm);
    color: var(--color-text-secondary);
    white-space: nowrap;
  }

  @media (max-width: 768px) {
    .nav { display: none; }
    .search-btn { display: none; }
  }
</style>
