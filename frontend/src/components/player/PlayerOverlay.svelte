<script lang="ts">
  import { playerStore } from '../../lib/stores/player';
  import { epgStore } from '../../lib/stores/epg';
  import { getProgress, formatTime } from '../../lib/utils/time';
  import ProgressBar from '../shared/ProgressBar.svelte';
  import LiveIndicator from '../shared/LiveIndicator.svelte';
  import Icon from '../shared/Icon.svelte';
  import { fade } from 'svelte/transition';

  interface Props {
    onToggleMiniGuide: () => void;
  }

  let { onToggleMiniGuide }: Props = $props();

  let ch = $derived(playerStore.currentChannel);
  let currentProg = $derived(ch ? epgStore.getCurrentProgramme(ch.id) : undefined);
  let progress = $derived(currentProg ? getProgress(currentProg.start_ts, currentProg.stop_ts) : 0);
</script>

<div class="overlay" transition:fade={{ duration: 200 }}>
  <!-- Top bar: channel info -->
  <div class="overlay-top glass">
    {#if ch}
      <div class="channel-info">
        <span class="ch-num tabular-nums font-mono">{ch.number}</span>
        <span class="ch-name">{ch.name}</span>
        <LiveIndicator />
      </div>
    {/if}
    {#if currentProg}
      <div class="prog-info">
        <span class="prog-title">{currentProg.title}</span>
        {#if currentProg.subtitle}
          <span class="prog-sub">{currentProg.subtitle}</span>
        {/if}
        <span class="prog-time">{formatTime(currentProg.start)} – {formatTime(currentProg.stop)}</span>
      </div>
    {/if}
  </div>

  <!-- Bottom bar: controls -->
  <div class="overlay-bottom glass">
    {#if currentProg}
      <ProgressBar value={progress} height="3px" color="var(--color-live)" />
    {/if}
    <div class="controls">
      <button onclick={() => playerStore.togglePause()} aria-label={playerStore.paused ? 'Play' : 'Pause'}>
        <Icon name={playerStore.paused ? 'play' : 'pause'} size={24} />
      </button>

      <button onclick={() => playerStore.toggleMute()} aria-label={playerStore.muted ? 'Unmute' : 'Mute'}>
        <Icon name={playerStore.muted ? 'mute' : 'unmute'} size={22} />
      </button>

      <div class="spacer"></div>

      <button onclick={onToggleMiniGuide} aria-label="Toggle mini guide">
        <Icon name="menu" size={22} />
      </button>
    </div>
  </div>
</div>

<style>
  .overlay {
    position: absolute;
    inset: 0;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    pointer-events: none;
    z-index: 10;
  }

  .overlay-top, .overlay-bottom {
    pointer-events: auto;
    padding: var(--sp-4) var(--sp-5);
  }

  .overlay-top {
    display: flex;
    align-items: center;
    gap: var(--sp-5);
    background: linear-gradient(to bottom, rgba(0, 0, 0, 0.7), transparent);
    border: none;
    backdrop-filter: none;
  }

  .channel-info {
    display: flex;
    align-items: center;
    gap: var(--sp-2);
  }

  .ch-num {
    font-size: var(--text-xl);
    font-weight: var(--font-weight-bold);
    color: var(--color-accent);
  }

  .ch-name {
    font-size: var(--text-lg);
    font-weight: var(--font-weight-semibold);
  }

  .prog-info {
    display: flex;
    align-items: baseline;
    gap: var(--sp-3);
  }

  .prog-title {
    font-weight: var(--font-weight-semibold);
  }

  .prog-sub {
    font-size: var(--text-sm);
    color: var(--color-text-secondary);
  }

  .prog-time {
    font-size: var(--text-sm);
    color: var(--color-text-muted);
  }

  .overlay-bottom {
    background: linear-gradient(to top, rgba(0, 0, 0, 0.7), transparent);
    border: none;
    backdrop-filter: none;
    display: flex;
    flex-direction: column;
    gap: var(--sp-2);
  }

  .controls {
    display: flex;
    align-items: center;
    gap: var(--sp-4);
  }

  .controls button {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 40px;
    height: 40px;
    border-radius: var(--radius-full);
    color: white;
    transition: background var(--duration-fast) var(--ease-out);
  }

  .controls button:hover {
    background: rgba(255, 255, 255, 0.15);
  }

  .spacer { flex: 1; }
</style>
