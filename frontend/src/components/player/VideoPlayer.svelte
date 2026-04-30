<script lang="ts">
  import { playerStore } from '../../lib/stores/player';
  import { epgStore } from '../../lib/stores/epg';
  import { createStreamPlayer, type StreamPlayer } from '../../lib/utils/video';

  let videoEl: HTMLVideoElement;
  let streamPlayer: StreamPlayer | null = null;

  // Auto-play when channel changes
  $effect(() => {
    const ch = playerStore.currentChannel;
    if (!ch || !videoEl) return;
    const num = parseInt(ch.number);
    if (!Number.isFinite(num) || num <= 0) return;

    // Destroy previous
    streamPlayer?.destroy();

    streamPlayer = createStreamPlayer(videoEl, num);
    streamPlayer.play();

    return () => {
      streamPlayer?.destroy();
      streamPlayer = null;
    };
  });

  // Sync mute state
  $effect(() => {
    streamPlayer?.mute(playerStore.muted);
  });

  // Sync volume
  $effect(() => {
    streamPlayer?.setVolume(playerStore.volume);
  });

  // Auto-select first channel if none selected
  $effect(() => {
    if (!playerStore.currentChannel && epgStore.channels.length > 0) {
      playerStore.setChannel(epgStore.channels[0]);
    }
  });
</script>

<video
  bind:this={videoEl}
  class="video-element"
  autoplay
  playsinline
  muted={playerStore.muted}
  aria-label="Live TV stream"
></video>

<style>
  .video-element {
    width: 100%;
    height: 100%;
    object-fit: contain;
    background: black;
  }
</style>
