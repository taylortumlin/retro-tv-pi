<script lang="ts">
  import { createBackup, listBackups, restoreBackup } from '../../lib/api/admin';
  import type { BackupEntry } from '../../lib/types/admin';
  import { uiStore } from '../../lib/stores/ui';
  import Spinner from '../shared/Spinner.svelte';

  let backups = $state<BackupEntry[]>([]);
  let loading = $state(true);
  let creating = $state(false);
  let restoring = $state<string | null>(null);

  $effect(() => {
    loadBackups();
  });

  async function loadBackups() {
    try {
      backups = await listBackups();
    } catch {
      uiStore.toast('Failed to load backups', 'error');
    } finally {
      loading = false;
    }
  }

  async function handleCreate() {
    creating = true;
    try {
      const result = await createBackup();
      uiStore.toast(`Backup created: ${result.filename}`, 'success');
      await loadBackups();
    } catch {
      uiStore.toast('Backup failed', 'error');
    } finally {
      creating = false;
    }
  }

  async function handleRestore(filename: string) {
    if (!confirm(`Restore from ${filename}? This will replace the current config.`)) return;
    restoring = filename;
    try {
      await restoreBackup(filename);
      uiStore.toast('Config restored. Refresh may be needed.', 'success');
    } catch {
      uiStore.toast('Restore failed', 'error');
    } finally {
      restoring = null;
    }
  }

  function formatSize(bytes: number): string {
    if (bytes < 1024) return `${bytes} B`;
    return `${(bytes / 1024).toFixed(1)} KB`;
  }
</script>

<div class="backup-manager">
  <div class="editor-header">
    <h2>Backups</h2>
    <button class="btn-primary" onclick={handleCreate} disabled={creating}>
      {#if creating}<Spinner size={14} />{:else}Create Backup{/if}
    </button>
  </div>

  {#if loading}
    <div class="loading"><Spinner /></div>
  {:else if backups.length === 0}
    <p class="empty">No backups yet</p>
  {:else}
    <div class="backup-list">
      {#each backups as backup}
        <div class="backup-row">
          <div class="backup-info">
            <span class="backup-name">{backup.filename}</span>
            <span class="backup-meta">{formatSize(backup.size)} · {new Date(backup.created).toLocaleString()}</span>
          </div>
          <div class="backup-actions">
            <a
              href="/admin/api/config/backups/{backup.filename}"
              class="btn-secondary"
              download
            >
              Download
            </a>
            <button
              class="btn-warning"
              onclick={() => handleRestore(backup.filename)}
              disabled={restoring !== null}
            >
              {#if restoring === backup.filename}<Spinner size={14} />{:else}Restore{/if}
            </button>
          </div>
        </div>
      {/each}
    </div>
  {/if}
</div>

<style>
  .backup-manager {
    display: flex;
    flex-direction: column;
    gap: var(--sp-5);
  }

  .editor-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  h2 { font-size: var(--text-xl); font-weight: var(--font-weight-bold); }

  .btn-primary {
    display: flex; align-items: center; gap: var(--sp-1);
    padding: var(--sp-2) var(--sp-4);
    background: var(--color-accent); color: white;
    border-radius: var(--radius-sm);
    font-weight: var(--font-weight-semibold);
    font-size: var(--text-sm);
  }

  .btn-secondary {
    padding: var(--sp-1) var(--sp-3);
    background: var(--color-surface);
    border-radius: var(--radius-sm);
    font-size: var(--text-xs);
    font-weight: var(--font-weight-semibold);
    color: var(--color-text);
    text-decoration: none;
  }

  .btn-warning {
    display: flex; align-items: center; gap: var(--sp-1);
    padding: var(--sp-1) var(--sp-3);
    background: rgba(255, 159, 10, 0.2);
    color: var(--color-warning);
    border-radius: var(--radius-sm);
    font-size: var(--text-xs);
    font-weight: var(--font-weight-semibold);
  }

  .loading { display: flex; justify-content: center; padding: var(--sp-10); }
  .empty { color: var(--color-text-muted); text-align: center; padding: var(--sp-10); }

  .backup-list {
    display: flex;
    flex-direction: column;
    gap: var(--sp-2);
  }

  .backup-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--sp-3) var(--sp-4);
    background: var(--color-bg-card);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-sm);
  }

  .backup-info {
    display: flex;
    flex-direction: column;
    gap: 2px;
  }

  .backup-name {
    font-size: var(--text-sm);
    font-weight: var(--font-weight-semibold);
  }

  .backup-meta {
    font-size: var(--text-xs);
    color: var(--color-text-muted);
  }

  .backup-actions {
    display: flex;
    gap: var(--sp-2);
  }
</style>
