<script lang="ts">
  import { createStreamPlayer, type StreamPlayer } from '../../lib/utils/video';
  import Icon from '../shared/Icon.svelte';
  import LiveIndicator from '../shared/LiveIndicator.svelte';
  import Spinner from '../shared/Spinner.svelte';

  interface Props {
    channelNumber: number;
  }

  let { channelNumber }: Props = $props();

  let videoEl: HTMLVideoElement;
  let streamPlayer: StreamPlayer | null = null;
  let muted = $state(true);
  let loaded = $state(false);

  $effect(() => {
    if (!videoEl || !channelNumber || !Number.isFinite(channelNumber)) return;
    loaded = false;
    streamPlayer = createStreamPlayer(videoEl, channelNumber);
    streamPlayer.mute(muted);
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
    streamPlayer?.mute(muted);
  });

  function toggleMute(e: MouseEvent) {
    e.stopPropagation();
    muted = !muted;
  }
</script>

<div class="channel-preview">
  <video
    bind:this={videoEl}
    class="preview-video"
    {muted}
    autoplay
    playsinline
    aria-label="Live channel preview"
  ></video>

  {#if !loaded}
    <div class="preview-loading">
      <Spinner size={28} />
    </div>
  {/if}

  <div class="preview-overlay">
    <div class="live-badge">
      <LiveIndicator size={6} />
      LIVE
    </div>
    <button class="mute-btn" onclick={toggleMute} aria-label={muted ? 'Unmute preview' : 'Mute preview'}>
      <Icon name={muted ? 'mute' : 'unmute'} size={16} />
    </button>
  </div>
</div>

<style>
  .channel-preview {
    position: relative;
    width: 100%;
    height: 100%;
    background: #000;
    overflow: hidden;
  }

  .preview-video {
    width: 100%;
    height: 100%;
    object-fit: cover;
    opacity: 0.55;
  }

  .preview-loading {
    position: absolute;
    inset: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(0, 0, 0, 0.4);
    color: var(--color-text-muted);
  }

  .preview-overlay {
    position: absolute;
    top: var(--sp-3);
    left: var(--sp-3);
    right: var(--sp-3);
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: var(--sp-2);
    pointer-events: none;
    z-index: 2;
  }

  .live-badge {
    display: flex;
    align-items: center;
    gap: var(--sp-1);
    padding: 2px var(--sp-2);
    background: var(--color-live);
    border-radius: var(--radius-sm);
    font-size: 0.625rem;
    font-weight: var(--font-weight-bold);
    color: white;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  .mute-btn {
    pointer-events: auto;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    border-radius: var(--radius-full);
    background: rgba(0, 0, 0, 0.55);
    color: white;
    backdrop-filter: blur(8px);
    transition: background var(--duration-fast) var(--ease-out);
  }

  .mute-btn:hover {
    background: rgba(0, 0, 0, 0.75);
  }
</style>
