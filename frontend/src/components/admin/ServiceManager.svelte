<script lang="ts">
  import { restartService, getServiceLogs } from '../../lib/api/admin';
  import { uiStore } from '../../lib/stores/ui';
  import Spinner from '../shared/Spinner.svelte';

  let restarting = $state<string | null>(null);
  let logs = $state<string[]>([]);
  let logService = $state<string | null>(null);
  let loadingLogs = $state(false);

  async function handleRestart(svc: string) {
    restarting = svc;
    try {
      const result = await restartService(svc);
      const ok = Object.values(result).every(r => r.ok);
      uiStore.toast(ok ? `${svc} restarted` : `Restart had issues`, ok ? 'success' : 'warning');
    } catch {
      uiStore.toast('Restart failed', 'error');
    } finally {
      restarting = null;
    }
  }

  async function handleLogs(svc: string) {
    logService = svc;
    loadingLogs = true;
    logs = [];
    try {
      const result = await getServiceLogs(svc);
      if (result.ok && result.lines) {
        logs = result.lines;
      }
    } catch {
      uiStore.toast('Failed to load logs', 'error');
    } finally {
      loadingLogs = false;
    }
  }

  const services = [
    { id: 'tv-guide', label: 'TV Guide' },
    { id: 'tv-player', label: 'TV Player' },
    { id: 'both', label: 'Both Services' },
  ];
</script>

<div class="service-manager">
  <h2>Services</h2>

  <div class="service-grid">
    {#each services as svc}
      <div class="service-card">
        <h3>{svc.label}</h3>
        <div class="service-actions">
          <button
            class="btn-warning"
            onclick={() => handleRestart(svc.id)}
            disabled={restarting !== null}
          >
            {#if restarting === svc.id}<Spinner size={14} />{:else}Restart{/if}
          </button>
          {#if svc.id !== 'both'}
            <button class="btn-secondary" onclick={() => handleLogs(svc.id)}>View Logs</button>
          {/if}
        </div>
      </div>
    {/each}
  </div>

  {#if logService}
    <div class="log-viewer">
      <div class="log-header">
        <h3>Logs: {logService}</h3>
        <button onclick={() => handleLogs(logService!)} aria-label="Refresh logs">Refresh</button>
      </div>
      {#if loadingLogs}
        <div class="loading"><Spinner /></div>
      {:else}
        <pre class="log-content">{logs.join('\n')}</pre>
      {/if}
    </div>
  {/if}
</div>

<style>
  .service-manager {
    display: flex;
    flex-direction: column;
    gap: var(--sp-5);
  }

  h2 { font-size: var(--text-xl); font-weight: var(--font-weight-bold); }
  h3 { font-size: var(--text-base); font-weight: var(--font-weight-semibold); }

  .service-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    gap: var(--sp-4);
  }

  .service-card {
    display: flex;
    flex-direction: column;
    gap: var(--sp-3);
    padding: var(--sp-4);
    background: var(--color-bg-card);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
  }

  .service-actions {
    display: flex;
    gap: var(--sp-2);
  }

  .btn-warning {
    display: flex;
    align-items: center;
    gap: var(--sp-1);
    padding: var(--sp-2) var(--sp-4);
    background: rgba(255, 159, 10, 0.2);
    color: var(--color-warning);
    border-radius: var(--radius-sm);
    font-weight: var(--font-weight-semibold);
    font-size: var(--text-sm);
  }

  .btn-secondary {
    padding: var(--sp-2) var(--sp-4);
    background: var(--color-surface);
    border-radius: var(--radius-sm);
    font-weight: var(--font-weight-semibold);
    font-size: var(--text-sm);
  }

  .log-viewer {
    background: var(--color-bg-card);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
    overflow: hidden;
  }

  .log-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--sp-3) var(--sp-4);
    border-bottom: 1px solid var(--color-border);
  }

  .log-header button {
    font-size: var(--text-sm);
    color: var(--color-accent);
    font-weight: var(--font-weight-semibold);
  }

  .loading {
    display: flex;
    justify-content: center;
    padding: var(--sp-5);
  }

  .log-content {
    padding: var(--sp-4);
    font-family: monospace;
    font-size: var(--text-xs);
    line-height: 1.5;
    max-height: 400px;
    overflow-y: auto;
    white-space: pre-wrap;
    word-break: break-all;
    color: var(--color-text-secondary);
  }
</style>
