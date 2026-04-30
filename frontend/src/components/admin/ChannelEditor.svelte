<script lang="ts">
  import { getConfig, putConfigSection, discoverChannels } from '../../lib/api/admin';
  import type { ConfigChannel, DiscoveredChannel } from '../../lib/types/admin';
  import { uiStore } from '../../lib/stores/ui';
  import Spinner from '../shared/Spinner.svelte';

  let channels = $state<ConfigChannel[]>([]);
  let loading = $state(true);
  let saving = $state(false);
  let discovering = $state(false);
  let discovered = $state<DiscoveredChannel[]>([]);

  $effect(() => {
    loadChannels();
  });

  async function loadChannels() {
    try {
      const config = await getConfig();
      channels = config.channels || [];
    } catch {
      uiStore.toast('Failed to load channels', 'error');
    } finally {
      loading = false;
    }
  }

  async function save() {
    saving = true;
    try {
      await putConfigSection('channels', channels);
      uiStore.toast('Channels saved', 'success');
    } catch {
      uiStore.toast('Failed to save', 'error');
    } finally {
      saving = false;
    }
  }

  async function discover() {
    discovering = true;
    try {
      const result = await discoverChannels();
      if (result.ok && result.channels) {
        discovered = result.channels;
      } else {
        uiStore.toast(result.error || 'Discovery failed', 'error');
      }
    } catch {
      uiStore.toast('Discovery failed', 'error');
    } finally {
      discovering = false;
    }
  }

  function addChannel() {
    const nextNum = channels.length > 0 ? Math.max(...channels.map(c => c.number)) + 1 : 1;
    channels = [...channels, { number: nextNum, name: 'New Channel' }];
  }

  function removeChannel(index: number) {
    channels = channels.filter((_, i) => i !== index);
  }

  function importDiscovered(ch: DiscoveredChannel) {
    const num = parseInt(ch.number) || channels.length;
    if (!channels.some(c => c.number === num)) {
      channels = [...channels, { number: num, name: ch.name }];
    }
  }

  function moveUp(i: number) {
    if (i === 0) return;
    const arr = [...channels];
    [arr[i - 1], arr[i]] = [arr[i], arr[i - 1]];
    channels = arr;
  }

  function moveDown(i: number) {
    if (i >= channels.length - 1) return;
    const arr = [...channels];
    [arr[i], arr[i + 1]] = [arr[i + 1], arr[i]];
    channels = arr;
  }
</script>

<div class="channel-editor">
  <div class="editor-header">
    <h2>Channels</h2>
    <div class="header-actions">
      <button class="btn-secondary" onclick={discover} disabled={discovering}>
        {#if discovering}<Spinner size={14} />{:else}Discover{/if}
      </button>
      <button class="btn-secondary" onclick={addChannel}>+ Add</button>
      <button class="btn-primary" onclick={save} disabled={saving}>
        {#if saving}<Spinner size={14} />{:else}Save{/if}
      </button>
    </div>
  </div>

  {#if loading}
    <div class="loading"><Spinner /></div>
  {:else}
    <div class="channel-list">
      {#each channels as ch, i}
        <div class="channel-row">
          <div class="reorder-btns">
            <button onclick={() => moveUp(i)} disabled={i === 0} aria-label="Move up">&uarr;</button>
            <button onclick={() => moveDown(i)} disabled={i === channels.length - 1} aria-label="Move down">&darr;</button>
          </div>
          <input
            type="number"
            bind:value={ch.number}
            class="ch-num-input tabular-nums"
            aria-label="Channel number"
          />
          <input
            type="text"
            bind:value={ch.name}
            class="ch-name-input"
            aria-label="Channel name"
          />
          <button class="remove-btn" onclick={() => removeChannel(i)} aria-label="Remove channel">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6L6 18M6 6l12 12"/></svg>
          </button>
        </div>
      {/each}
    </div>

    {#if discovered.length > 0}
      <div class="discovered-section">
        <h3>Discovered Channels</h3>
        <div class="discovered-list">
          {#each discovered as ch}
            <div class="discovered-row">
              <span class="tabular-nums">{ch.number}</span>
              <span>{ch.name}</span>
              <button class="btn-small" onclick={() => importDiscovered(ch)}>Import</button>
            </div>
          {/each}
        </div>
      </div>
    {/if}
  {/if}
</div>

<style>
  .channel-editor {
    display: flex;
    flex-direction: column;
    gap: var(--sp-5);
  }

  .editor-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  h2 {
    font-size: var(--text-xl);
    font-weight: var(--font-weight-bold);
  }

  .header-actions {
    display: flex;
    gap: var(--sp-2);
  }

  .btn-primary {
    display: flex;
    align-items: center;
    gap: var(--sp-1);
    padding: var(--sp-2) var(--sp-4);
    background: var(--color-accent);
    color: white;
    border-radius: var(--radius-sm);
    font-weight: var(--font-weight-semibold);
    font-size: var(--text-sm);
  }

  .btn-secondary {
    display: flex;
    align-items: center;
    gap: var(--sp-1);
    padding: var(--sp-2) var(--sp-4);
    background: var(--color-surface);
    border-radius: var(--radius-sm);
    font-weight: var(--font-weight-semibold);
    font-size: var(--text-sm);
  }

  .btn-small {
    padding: var(--sp-1) var(--sp-2);
    background: var(--color-accent-subtle);
    color: var(--color-accent);
    border-radius: var(--radius-sm);
    font-size: var(--text-xs);
    font-weight: var(--font-weight-semibold);
  }

  .loading {
    display: flex;
    justify-content: center;
    padding: var(--sp-10);
  }

  .channel-list {
    display: flex;
    flex-direction: column;
    gap: var(--sp-2);
  }

  .channel-row {
    display: flex;
    align-items: center;
    gap: var(--sp-2);
    padding: var(--sp-2);
    background: var(--color-bg-card);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-sm);
  }

  .reorder-btns {
    display: flex;
    flex-direction: column;
    gap: 2px;
  }

  .reorder-btns button {
    padding: 0 var(--sp-1);
    font-size: var(--text-xs);
    color: var(--color-text-muted);
    line-height: 1;
  }

  .reorder-btns button:disabled {
    opacity: 0.3;
  }

  .ch-num-input {
    width: 60px;
    padding: var(--sp-1) var(--sp-2);
    background: var(--color-bg);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-sm);
    text-align: center;
    font-size: var(--text-sm);
  }

  .ch-name-input {
    flex: 1;
    padding: var(--sp-1) var(--sp-2);
    background: var(--color-bg);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-sm);
    font-size: var(--text-sm);
  }

  .remove-btn {
    display: flex;
    color: var(--color-text-muted);
    padding: var(--sp-1);
  }

  .remove-btn:hover {
    color: var(--color-error);
  }

  .discovered-section {
    margin-top: var(--sp-4);
  }

  .discovered-section h3 {
    font-size: var(--text-base);
    font-weight: var(--font-weight-semibold);
    margin-bottom: var(--sp-3);
  }

  .discovered-list {
    display: flex;
    flex-direction: column;
    gap: var(--sp-1);
  }

  .discovered-row {
    display: flex;
    align-items: center;
    gap: var(--sp-3);
    padding: var(--sp-2);
    font-size: var(--text-sm);
    background: var(--color-bg-card);
    border-radius: var(--radius-sm);
  }
</style>
