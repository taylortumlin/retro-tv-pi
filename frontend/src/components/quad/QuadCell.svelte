<script lang="ts">
  import { createStreamPlayer, type StreamPlayer } from '../../lib/utils/video';
  import { epgStore } from '../../lib/stores/epg';
  import LiveIndicator from '../shared/LiveIndicator.svelte';
  import Spinner from '../shared/Spinner.svelte';

  interface Props {
    channelNumber: number;
    selected: boolean;
    onClick: () => void;
  }

  let { channelNumber, selected, onClick }: Props = $props();

  let videoEl: HTMLVideoElement;
  let streamPlayer: StreamPlayer | null = null;
  let loaded = $state(false);

  let channel = $derived(
    epgStore.channels.find(c => parseInt(c.number) === channelNumber)
  );
  let nowProg = $derived(channel ? epgStore.getCurrentProgramme(channel.id) : undefined);

  $effect(() => {
    if (!videoEl || !channelNumber || !Number.isFinite(channelNumber)) return;
    loaded = false;
    streamPlayer = createStreamPlayer(videoEl, channelNumber);
    streamPlayer.mute(!selected);
    streamPlayer.play();

    const onLoaded = () => { loaded = true; };
    videoEl.addEventListener('loadeddata', onLoaded);
    videoEl.addEventListener('playing', onLoaded);

    return () => {
      videoEl.removeEventListener('loadeddata', onLoaded);
      videoEl.removeEventListener('playing', onLoaded);
      streamPlayer?.destroy();
      streamPlayer = null;
    };
  });

  $effect(() => {
    streamPlayer?.mute(!selected);
  });
</script>

<!-- svelte-ignore a11y_no_static_element_interactions -->
<!-- svelte-ignore a11y_click_events_have_key_events -->
<div class="quad-cell" class:selected onclick={onClick}>
  <video
    bind:this={videoEl}
    class="quad-video"
    muted={!selected}
    autoplay
    playsinline
    aria-label="Channel {channelNumber} preview"
  ></video>

  {#if !loaded}
    <div class="cell-loading">
      <Spinner size={36} />
    </div>
  {/if}

  <div class="cell-label">
    <LiveIndicator size={6} />
    <span class="font-mono">CH {channelNumber}</span>
    {#if channel}
      <span class="ch-name">{channel.name}</span>
    {/if}
  </div>

  {#if nowProg}
    <div class="cell-now">
      <strong>{nowProg.title}</strong>
      {#if nowProg.subtitle}<span> · {nowProg.subtitle}</span>{/if}
    </div>
  {/if}
</div>

<style>
  .quad-cell {
    position: relative;
    overflow: hidden;
    background: #000;
    border: 2px solid var(--color-border);
    cursor: pointer;
    transition: border-color var(--duration-fast) var(--ease-out);
  }

  .quad-cell.selected {
    border-color: var(--color-accent);
    box-shadow: var(--glass-glow);
  }

  .quad-video {
    width: 100%;
    height: 100%;
    object-fit: contain;
    background: #000;
  }

  .cell-loading {
    position: absolute;
    inset: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--color-text-muted);
    background: rgba(0, 0, 0, 0.3);
  }

  .cell-label {
    position: absolute;
    top: var(--sp-2);
    left: var(--sp-2);
    z-index: 2;
    display: flex;
    align-items: center;
    gap: var(--sp-2);
    padding: 4px var(--sp-3);
    background: rgba(0, 0, 0, 0.7);
    backdrop-filter: blur(8px);
    border-radius: var(--radius-sm);
    font-size: var(--text-xs);
    font-weight: var(--font-weight-bold);
    color: var(--color-gold);
  }

  .cell-label .ch-name {
    color: var(--color-text);
    font-weight: var(--font-weight-semibold);
  }

  .cell-now {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    z-index: 2;
    padding: var(--sp-3) var(--sp-4);
    background: linear-gradient(to top, rgba(0, 0, 0, 0.85), transparent);
    font-size: var(--text-sm);
    color: var(--color-text);
    opacity: 0;
    transition: opacity var(--duration-normal) var(--ease-out);
  }

  .quad-cell:hover .cell-now,
  .quad-cell.selected .cell-now {
    opacity: 1;
  }

  .cell-now strong {
    font-weight: var(--font-weight-semibold);
  }

  .cell-now span {
    color: var(--color-text-secondary);
  }
</style>
