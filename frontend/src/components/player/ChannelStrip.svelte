<script lang="ts">
  import { epgStore } from '../../lib/stores/epg';
  import { playerStore } from '../../lib/stores/player';
  import { fade } from 'svelte/transition';

  interface Props {
    visible: boolean;
  }

  let { visible }: Props = $props();
</script>

{#if visible}
  <div class="channel-strip" transition:fade={{ duration: 200 }}>
    {#each epgStore.channels as ch (ch.id)}
      <button
        class="strip-item"
        class:active={playerStore.currentChannel?.id === ch.id}
        onclick={() => playerStore.setChannel(ch)}
        aria-label="Switch to channel {ch.number} {ch.name}"
      >
        <span class="tabular-nums font-mono">{ch.number}</span>
      </button>
    {/each}
  </div>
{/if}

<style>
  .channel-strip {
    position: absolute;
    bottom: 60px;
    left: 50%;
    transform: translateX(-50%);
    display: flex;
    gap: var(--sp-1);
    padding: var(--sp-2);
    background: var(--glass-bg);
    backdrop-filter: var(--glass-blur);
    -webkit-backdrop-filter: var(--glass-blur);
    border-radius: var(--radius-full);
    border: var(--glass-border);
    z-index: 15;
    max-width: 90%;
    overflow-x: auto;
    scrollbar-width: none;
  }

  .channel-strip::-webkit-scrollbar { display: none; }

  .strip-item {
    width: 36px;
    height: 36px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: var(--radius-full);
    font-size: var(--text-sm);
    font-weight: var(--font-weight-bold);
    color: var(--color-text-secondary);
    transition: all var(--duration-fast) var(--ease-out);
    flex-shrink: 0;
  }

  .strip-item:hover {
    background: var(--color-surface-hover);
    color: var(--color-text);
  }

  .strip-item.active {
    background: var(--color-accent);
    color: white;
  }
</style>
