<script lang="ts">
  import { getStatus } from '../../lib/api/admin';
  import type { SystemStatus } from '../../lib/types/admin';
  import Spinner from '../shared/Spinner.svelte';
  import { themeStore } from '../../lib/stores/theme.svelte';

  let status = $state<SystemStatus | null>(null);
  let loading = $state(true);

  $effect(() => {
    loadStatus();
    const interval = setInterval(loadStatus, 30_000);
    return () => clearInterval(interval);
  });

  async function loadStatus() {
    try {
      status = await getStatus();
    } catch {
      // silent
    } finally {
      loading = false;
    }
  }
</script>

<div class="dashboard">
  <h2>Dashboard</h2>

  <section class="theme-picker">
    <h3>Theme</h3>
    <div class="theme-options">
      {#each themeStore.themes as t}
        <button
          class="theme-btn"
          class:active={themeStore.active === t}
          onclick={() => themeStore.set(t)}
        >
          {themeStore.label(t)}
        </button>
      {/each}
    </div>
    <p class="theme-hint">Press <kbd>Shift</kbd> + <kbd>T</kbd> to cycle themes.</p>
  </section>

  {#if loading && !status}
    <div class="loading"><Spinner /></div>
  {:else if status}
    <div class="status-grid">
      <div class="status-card">
        <span class="card-label">Uptime</span>
        <span class="card-value">{status.uptime}</span>
      </div>

      <div class="status-card">
        <span class="card-label">CPU Temp</span>
        <span class="card-value" class:warning={status.cpu_temp_c !== null && status.cpu_temp_c > 70}>
          {status.cpu_temp_c !== null ? `${status.cpu_temp_c}°C` : '--'}
        </span>
      </div>

      <div class="status-card">
        <span class="card-label">Memory</span>
        <span class="card-value">
          {status.memory?.used_mb ?? '--'} / {status.memory?.total_mb ?? '--'} MB
        </span>
        {#if status.memory?.total_mb}
          <div class="usage-bar">
            <div class="usage-fill" style:width="{(status.memory.used_mb / status.memory.total_mb) * 100}%"></div>
          </div>
        {/if}
      </div>

      <div class="status-card">
        <span class="card-label">Disk</span>
        <span class="card-value">
          {status.disk?.used_gb ?? '--'} / {status.disk?.total_gb ?? '--'} GB
        </span>
        {#if status.disk?.total_gb}
          <div class="usage-bar">
            <div class="usage-fill" style:width="{(status.disk.used_gb / status.disk.total_gb) * 100}%"></div>
          </div>
        {/if}
      </div>

      <div class="status-card">
        <span class="card-label">Load Average</span>
        <span class="card-value">
          {status.load_average?.map(v => v.toFixed(2)).join(', ') || '--'}
        </span>
      </div>

      <div class="status-card">
        <span class="card-label">TV Guide</span>
        <span class="card-value svc-status" class:active={status.tv_guide_status === 'active'}>
          {status.tv_guide_status}
        </span>
      </div>

      <div class="status-card">
        <span class="card-label">TV Player</span>
        <span class="card-value svc-status" class:active={status.tv_player_status === 'active'}>
          {status.tv_player_status}
        </span>
      </div>

      <div class="status-card">
        <span class="card-label">ErsatzTV</span>
        <span class="card-value svc-status" class:active={status.ersatztv_reachable}>
          {status.ersatztv_reachable ? 'connected' : 'unreachable'}
        </span>
      </div>

      <div class="status-card">
        <span class="card-label">EPG Data</span>
        <span class="card-value">
          {status.epg_channels} channels, {status.epg_programmes} programmes
        </span>
        {#if status.epg_last_update}
          <span class="card-sub">Updated: {new Date(status.epg_last_update).toLocaleTimeString()}</span>
        {/if}
      </div>
    </div>
  {/if}
</div>

<style>
  .dashboard {
    display: flex;
    flex-direction: column;
    gap: var(--sp-5);
  }

  h2 {
    font-size: var(--text-xl);
    font-weight: var(--font-weight-bold);
  }

  .theme-picker {
    display: flex;
    flex-direction: column;
    gap: var(--sp-2);
    padding: var(--sp-4);
    background: var(--color-bg-card);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
  }

  .theme-picker h3 {
    font-size: var(--text-base);
    font-weight: var(--font-weight-semibold);
  }

  .theme-options {
    display: flex;
    gap: var(--sp-2);
    flex-wrap: wrap;
  }

  .theme-btn {
    padding: var(--sp-2) var(--sp-4);
    background: var(--color-surface);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-sm);
    font-size: var(--text-sm);
    font-weight: var(--font-weight-semibold);
    color: var(--color-text-secondary);
    transition: all var(--duration-fast) var(--ease-out);
  }

  .theme-btn:hover {
    background: var(--color-surface-hover);
    color: var(--color-text);
  }

  .theme-btn.active {
    background: var(--color-accent-subtle);
    border-color: var(--color-accent);
    color: var(--color-accent);
  }

  .theme-hint {
    font-size: var(--text-xs);
    color: var(--color-text-muted);
  }

  .theme-hint kbd {
    display: inline-block;
    padding: 1px var(--sp-1);
    background: var(--color-surface);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-sm);
    font-family: var(--font-mono);
    font-size: 0.6875rem;
  }

  .loading {
    display: flex;
    justify-content: center;
    padding: var(--sp-10);
  }

  .status-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    gap: var(--sp-4);
  }

  .status-card {
    display: flex;
    flex-direction: column;
    gap: var(--sp-1);
    padding: var(--sp-4);
    background: var(--color-bg-card);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
  }

  .card-label {
    font-size: var(--text-xs);
    color: var(--color-text-muted);
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  .card-value {
    font-size: var(--text-lg);
    font-weight: var(--font-weight-semibold);
  }

  .card-value.warning {
    color: var(--color-warning);
  }

  .card-sub {
    font-size: var(--text-xs);
    color: var(--color-text-muted);
  }

  .svc-status {
    color: var(--color-error);
  }

  .svc-status.active {
    color: var(--color-success);
  }

  .usage-bar {
    height: 4px;
    background: var(--color-surface);
    border-radius: 2px;
    overflow: hidden;
    margin-top: var(--sp-1);
  }

  .usage-fill {
    height: 100%;
    background: var(--color-accent);
    border-radius: 2px;
    transition: width var(--duration-normal) var(--ease-out);
  }
</style>
