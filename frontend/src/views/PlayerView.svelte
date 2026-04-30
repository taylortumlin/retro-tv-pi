<script lang="ts">
  import VideoPlayer from '../components/player/VideoPlayer.svelte';
  import PlayerOverlay from '../components/player/PlayerOverlay.svelte';
  import MiniGuide from '../components/player/MiniGuide.svelte';
  import ChannelStrip from '../components/player/ChannelStrip.svelte';
  import { playerStore } from '../lib/stores/player';
  import { epgStore } from '../lib/stores/epg';

  let showMiniGuide = $state(false);
  let showOverlay = $state(true);
  let overlayTimeout: ReturnType<typeof setTimeout>;

  $effect(() => {
    if (epgStore.channels.length === 0) epgStore.load();
  });

  function handleActivity() {
    showOverlay = true;
    clearTimeout(overlayTimeout);
    overlayTimeout = setTimeout(() => { showOverlay = false; }, 4000);
  }

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === 'g' || e.key === 'G') {
      showMiniGuide = !showMiniGuide;
    } else if (e.key === 'm' || e.key === 'M') {
      playerStore.toggleMute();
    } else if (e.key === ' ') {
      e.preventDefault();
      playerStore.togglePause();
    }
    handleActivity();
  }
</script>

<svelte:window onkeydown={handleKeydown} />

<!-- svelte-ignore a11y_no_static_element_interactions -->
<!-- svelte-ignore a11y_click_events_have_key_events -->
<div class="player-view" onmousemove={handleActivity} onclick={handleActivity}>
  <VideoPlayer />

  {#if showOverlay}
    <PlayerOverlay onToggleMiniGuide={() => { showMiniGuide = !showMiniGuide; }} />
  {/if}

  {#if showMiniGuide}
    <MiniGuide onClose={() => { showMiniGuide = false; }} />
  {/if}

  <ChannelStrip visible={showOverlay} />
</div>

<style>
  .player-view {
    position: relative;
    width: 100%;
    height: calc(100vh - var(--header-height));
    background: black;
    cursor: none;
    overflow: hidden;
  }

  .player-view:hover {
    cursor: default;
  }
</style>
