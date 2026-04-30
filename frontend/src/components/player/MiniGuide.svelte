<script lang="ts">
  import { epgStore } from '../../lib/stores/epg';
  import { playerStore } from '../../lib/stores/player';
  import { formatTime, isLive, getProgress } from '../../lib/utils/time';
  import ProgressBar from '../shared/ProgressBar.svelte';
  import LiveIndicator from '../shared/LiveIndicator.svelte';
  import { fly } from 'svelte/transition';

  interface Props {
    onClose: () => void;
  }

  let { onClose }: Props = $props();
</script>

<!-- svelte-ignore a11y_no_static_element_interactions -->
<div class="mini-guide glass" transition:fly={{ y: 200, duration: 300 }} onkeydown={(e) => { if (e.key === 'Escape') onClose(); }}>
  <div class="mg-header">
    <h3>Channels</h3>
    <button onclick={onClose} aria-label="Close mini guide">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6L6 18M6 6l12 12"/></svg>
    </button>
  </div>
  <div class="mg-list">
    {#each epgStore.channels as ch (ch.id)}
      {@const prog = epgStore.getCurrentProgramme(ch.id)}
      {@const active = playerStore.currentChannel?.id === ch.id}
      <button
        class="mg-item"
        class:active
        onclick={() => { playerStore.setChannel(ch); onClose(); }}
      >
        <span class="mg-num tabular-nums">{ch.number}</span>
        <div class="mg-info">
          <span class="mg-name">{ch.name}</span>
          {#if prog}
            <span class="mg-prog">{prog.title}</span>
            {#if isLive(prog.start_ts, prog.stop_ts)}
              <ProgressBar value={getProgress(prog.start_ts, prog.stop_ts)} height="2px" color="var(--color-live)" />
            {/if}
          {/if}
        </div>
        {#if active}<LiveIndicator size={8} />{/if}
      </button>
    {/each}
  </div>
</div>

<style>
  .mini-guide {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    max-height: 50%;
    z-index: 20;
    border-radius: var(--radius-xl) var(--radius-xl) 0 0;
    overflow: hidden;
    display: flex;
    flex-direction: column;
  }

  .mg-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--sp-4) var(--sp-5);
    border-bottom: 1px solid var(--color-border);
  }

  .mg-header h3 {
    font-size: var(--text-base);
    font-weight: var(--font-weight-bold);
  }

  .mg-list {
    overflow-y: auto;
    flex: 1;
  }

  .mg-item {
    display: flex;
    align-items: center;
    gap: var(--sp-3);
    width: 100%;
    padding: var(--sp-3) var(--sp-5);
    text-align: left;
    border-bottom: 1px solid var(--color-border);
    transition: background var(--duration-fast) var(--ease-out);
  }

  .mg-item:hover {
    background: var(--color-surface-hover);
  }

  .mg-item.active {
    background: var(--color-accent-subtle);
  }

  .mg-num {
    font-size: var(--text-sm);
    font-weight: var(--font-weight-bold);
    color: var(--color-accent);
    min-width: 28px;
  }

  .mg-info {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 2px;
    min-width: 0;
  }

  .mg-name {
    font-size: var(--text-sm);
    font-weight: var(--font-weight-semibold);
  }

  .mg-prog {
    font-size: var(--text-xs);
    color: var(--color-text-secondary);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
</style>
