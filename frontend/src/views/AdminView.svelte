<script lang="ts">
  import { checkAuth } from '../lib/api/admin';
  import LoginScreen from '../components/admin/LoginScreen.svelte';
  import Dashboard from '../components/admin/Dashboard.svelte';
  import ChannelEditor from '../components/admin/ChannelEditor.svelte';
  import TickerEditor from '../components/admin/TickerEditor.svelte';
  import ServiceManager from '../components/admin/ServiceManager.svelte';
  import BackupManager from '../components/admin/BackupManager.svelte';

  let authed = $state(false);
  let checking = $state(true);
  let activeTab = $state<'dashboard' | 'channels' | 'ticker' | 'services' | 'backups'>('dashboard');

  $effect(() => {
    checkAuth().then(r => { authed = r.authed; }).catch(() => { authed = false; }).finally(() => { checking = false; });
  });

  const tabs = [
    { id: 'dashboard' as const, label: 'Dashboard' },
    { id: 'channels' as const, label: 'Channels' },
    { id: 'ticker' as const, label: 'Ticker & Weather' },
    { id: 'services' as const, label: 'Services' },
    { id: 'backups' as const, label: 'Backups' },
  ];
</script>

<div class="admin-view">
  {#if checking}
    <div class="loading">Checking authentication...</div>
  {:else if !authed}
    <LoginScreen onLogin={() => { authed = true; }} />
  {:else}
    <div class="admin-layout">
      <aside class="sidebar glass">
        <h2>Admin</h2>
        <nav>
          {#each tabs as tab}
            <button
              class="sidebar-item"
              class:active={activeTab === tab.id}
              onclick={() => { activeTab = tab.id; }}
            >
              {tab.label}
            </button>
          {/each}
        </nav>
      </aside>

      <div class="admin-content">
        {#if activeTab === 'dashboard'}
          <Dashboard />
        {:else if activeTab === 'channels'}
          <ChannelEditor />
        {:else if activeTab === 'ticker'}
          <TickerEditor />
        {:else if activeTab === 'services'}
          <ServiceManager />
        {:else if activeTab === 'backups'}
          <BackupManager />
        {/if}
      </div>
    </div>
  {/if}
</div>

<style>
  .admin-view {
    height: calc(100vh - var(--header-height));
  }

  .loading {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: var(--color-text-muted);
  }

  .admin-layout {
    display: flex;
    height: 100%;
  }

  .sidebar {
    width: var(--sidebar-width);
    flex-shrink: 0;
    padding: var(--sp-5);
    border-right: 1px solid var(--color-border);
    display: flex;
    flex-direction: column;
    gap: var(--sp-4);
  }

  .sidebar h2 {
    font-size: var(--text-lg);
    font-weight: var(--font-weight-bold);
    padding-bottom: var(--sp-3);
    border-bottom: 1px solid var(--color-border);
  }

  .sidebar nav {
    display: flex;
    flex-direction: column;
    gap: var(--sp-1);
  }

  .sidebar-item {
    padding: var(--sp-2) var(--sp-3);
    border-radius: var(--radius-sm);
    font-size: var(--text-sm);
    font-weight: var(--font-weight-semibold);
    color: var(--color-text-secondary);
    text-align: left;
    transition: all var(--duration-fast) var(--ease-out);
  }

  .sidebar-item:hover {
    background: var(--color-surface-hover);
    color: var(--color-text);
  }

  .sidebar-item.active {
    background: var(--color-accent-subtle);
    color: var(--color-accent);
  }

  .admin-content {
    flex: 1;
    overflow-y: auto;
    padding: var(--sp-5);
  }

  @media (max-width: 768px) {
    .sidebar {
      display: none;
    }

    .admin-layout {
      flex-direction: column;
    }
  }
</style>
