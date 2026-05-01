<script lang="ts">
  import { getConfig, putConfigSection, discoverChannels } from '../../lib/api/admin';
  import type { ConfigChannel, DiscoveredChannel } from '../../lib/types/admin';
  import { uiStore } from '../../lib/stores/ui';
  import Spinner from '../shared/Spinner.svelte';
  import Icon from '../shared/Icon.svelte';

  let channels = $state<ConfigChannel[]>([]);
  let loading = $state(true);
  let saving = $state(false);
  let discovering = $state(false);
  let discovered = $state<DiscoveredChannel[]>([]);
  let dirty = $state(false);

  $effect(() => { loadChannels(); });

  async function loadChannels() {
    try {
      const config = await getConfig();
      channels = config.channels || [];
      dirty = false;
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
      dirty = false;
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

  function parseChannelNumber(s: string): number | null {
    const n = parseInt(s);
    return Number.isFinite(n) ? n : null;
  }

  // Reactive split of discovered channels: which ones are new vs already
  // imported. Match key is the channel number; if a channel with the same
  // number already exists we treat it as imported (we don't re-name).
  let existingNumbers = $derived(new Set(channels.map(c => c.number)));
  let missingDiscovered = $derived(
    discovered.filter(d => {
      const n = parseChannelNumber(d.number);
      return n !== null && !existingNumbers.has(n);
    })
  );
  let alreadyImportedCount = $derived(
    discovered.length - missingDiscovered.length
  );

  function sortByNumber(arr: ConfigChannel[]): ConfigChannel[] {
    return [...arr].sort((a, b) => a.number - b.number);
  }

  function importOne(ch: DiscoveredChannel) {
    const num = parseChannelNumber(ch.number);
    if (num === null) {
      uiStore.toast(`Skipped "${ch.name}" — not a valid channel number`, 'warning');
      return;
    }
    if (existingNumbers.has(num)) return;
    channels = sortByNumber([...channels, { number: num, name: ch.name }]);
    dirty = true;
  }

  function importAllMissing() {
    if (missingDiscovered.length === 0) return;
    const additions: ConfigChannel[] = [];
    for (const ch of missingDiscovered) {
      const num = parseChannelNumber(ch.number);
      if (num === null || existingNumbers.has(num)) continue;
      additions.push({ number: num, name: ch.name });
    }
    if (additions.length === 0) return;
    channels = sortByNumber([...channels, ...additions]);
    dirty = true;
    uiStore.toast(
      `Imported ${additions.length} channel${additions.length === 1 ? '' : 's'} — click Save to apply`,
      'success',
    );
  }

  function addChannel() {
    const nextNum = channels.length > 0 ? Math.max(...channels.map(c => c.number)) + 1 : 1;
    channels = [...channels, { number: nextNum, name: 'New Channel' }];
    dirty = true;
  }

  function removeChannel(index: number) {
    channels = channels.filter((_, i) => i !== index);
    dirty = true;
  }

  function moveUp(i: number) {
    if (i === 0) return;
    const arr = [...channels];
    [arr[i - 1], arr[i]] = [arr[i], arr[i - 1]];
    channels = arr;
    dirty = true;
  }

  function moveDown(i: number) {
    if (i >= channels.length - 1) return;
    const arr = [...channels];
    [arr[i], arr[i + 1]] = [arr[i + 1], arr[i]];
    channels = arr;
    dirty = true;
  }

  function onChannelEdit() {
    dirty = true;
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
      <button class="btn-primary" class:dirty onclick={save} disabled={saving || !dirty}>
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
            <button onclick={() => moveUp(i)} disabled={i === 0} aria-label="Move up"><Icon name="chevron-up" size={14} /></button>
            <button onclick={() => moveDown(i)} disabled={i === channels.length - 1} aria-label="Move down"><Icon name="chevron-down" size={14} /></button>
          </div>
          <input
            type="number"
            bind:value={ch.number}
            oninput={onChannelEdit}
            class="ch-num-input tabular-nums font-mono"
            aria-label="Channel number"
          />
          <input
            type="text"
            bind:value={ch.name}
            oninput={onChannelEdit}
            class="ch-name-input"
            aria-label="Channel name"
          />
          <button class="remove-btn" onclick={() => removeChannel(i)} aria-label="Remove channel">
            <Icon name="close" size={16} />
          </button>
        </div>
      {/each}
    </div>

    {#if discovered.length > 0}
      <div class="discovered-section">
        <div class="discovered-header">
          <h3>Discovered from ErsatzTV</h3>
          <p class="discovered-summary">
            {discovered.length} found
            {#if alreadyImportedCount > 0} · <span class="dim">{alreadyImportedCount} already in your list</span>{/if}
            {#if missingDiscovered.length > 0} · <strong class="accent">{missingDiscovered.length} new</strong>{/if}
          </p>
        </div>

        {#if missingDiscovered.length === 0}
          <div class="empty-state">
            <Icon name="star-filled" size={20} />
            <span>You have everything from ErsatzTV. Nothing new to import.</span>
          </div>
        {:else}
          <div class="discovered-actions">
            <button class="btn-primary" onclick={importAllMissing}>
              Import all {missingDiscovered.length} new {missingDiscovered.length === 1 ? 'channel' : 'channels'}
            </button>
            <span class="hint">Or import them one at a time below.</span>
          </div>
          <div class="discovered-list">
            {#each missingDiscovered as ch (ch.id)}
              <div class="discovered-row">
                <span class="d-num font-mono tabular-nums">{ch.number}</span>
                <span class="d-name">{ch.name}</span>
                <button class="btn-small" onclick={() => importOne(ch)}>Import</button>
              </div>
            {/each}
          </div>
        {/if}
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
    transition: opacity var(--duration-fast) var(--ease-out);
  }

  .btn-primary:disabled {
    opacity: 0.4;
    cursor: not-allowed;
  }

  .btn-primary.dirty {
    box-shadow: 0 0 0 2px var(--color-accent-subtle);
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

  .btn-secondary:hover {
    background: var(--color-surface-hover);
  }

  .btn-small {
    padding: var(--sp-1) var(--sp-3);
    background: var(--color-accent-subtle);
    color: var(--color-accent);
    border-radius: var(--radius-sm);
    font-size: var(--text-xs);
    font-weight: var(--font-weight-semibold);
  }

  .btn-small:hover {
    background: var(--color-accent);
    color: white;
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

  /* ===== Discovered section ===== */
  .discovered-section {
    margin-top: var(--sp-4);
    padding: var(--sp-4);
    background: var(--color-bg-card);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
  }

  .discovered-header {
    margin-bottom: var(--sp-3);
  }

  .discovered-section h3 {
    font-size: var(--text-base);
    font-weight: var(--font-weight-semibold);
  }

  .discovered-summary {
    margin-top: var(--sp-1);
    font-size: var(--text-xs);
    color: var(--color-text-secondary);
  }

  .discovered-summary .dim { color: var(--color-text-muted); }
  .discovered-summary .accent { color: var(--color-accent); font-weight: var(--font-weight-semibold); }

  .empty-state {
    display: flex;
    align-items: center;
    gap: var(--sp-2);
    padding: var(--sp-4);
    background: var(--color-accent-subtle);
    border-radius: var(--radius-sm);
    font-size: var(--text-sm);
    color: var(--color-text);
  }

  .empty-state :global(svg) { color: var(--color-gold); flex-shrink: 0; }

  .discovered-actions {
    display: flex;
    align-items: center;
    gap: var(--sp-3);
    margin-bottom: var(--sp-3);
    flex-wrap: wrap;
  }

  .hint {
    font-size: var(--text-xs);
    color: var(--color-text-muted);
  }

  .discovered-list {
    display: flex;
    flex-direction: column;
    gap: var(--sp-1);
  }

  .discovered-row {
    display: grid;
    grid-template-columns: 60px 1fr auto;
    align-items: center;
    gap: var(--sp-3);
    padding: var(--sp-2) var(--sp-3);
    font-size: var(--text-sm);
    background: var(--color-bg);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-sm);
    transition: border-color var(--duration-fast) var(--ease-out);
  }

  .discovered-row:hover {
    border-color: var(--color-accent);
  }

  .d-num {
    font-weight: var(--font-weight-bold);
    color: var(--color-accent);
    text-align: center;
  }

  .d-name {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
</style>
