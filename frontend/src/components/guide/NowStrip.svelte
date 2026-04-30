<script lang="ts">
  import { epgStore } from '../../lib/stores/epg';
  import { uiStore } from '../../lib/stores/ui';
  import { getProgress, formatTime } from '../../lib/utils/time';
  import ProgressBar from '../shared/ProgressBar.svelte';
  import LiveIndicator from '../shared/LiveIndicator.svelte';

  let strip = $derived(
    epgStore.nowPlaying.filter(np => np.now_playing)
  );
</script>

{#if strip.length > 0}
  <section class="now-strip" aria-label="Now playing">
    <h3 class="strip-title">Now Playing</h3>
    <div class="strip-scroll">
      {#each strip as np}
        {@const prog = np.now_playing!}
        {@const progress = getProgress(prog.start_ts, prog.stop_ts)}
        <button
          class="now-card"
          onclick={() => uiStore.openProgramme(prog)}
          aria-label="{np.channel.name}: {prog.title}"
        >
          <div class="card-header">
            {#if np.channel.logo}
              <img class="channel-logo" src={np.channel.logo} alt="" width="28" height="28" />
            {:else}
              <span class="channel-num tabular-nums">{np.channel.number}</span>
            {/if}
            <LiveIndicator size={6} />
          </div>
          <p class="card-title">{prog.title}</p>
          <span class="card-time">{formatTime(prog.start)} - {formatTime(prog.stop)}</span>
          <ProgressBar value={progress} height="2px" />
        </button>
      {/each}
    </div>
  </section>
{/if}

<style>
  .now-strip {
    padding: var(--sp-4) 0 var(--sp-2);
  }

  .strip-title {
    padding: 0 var(--sp-5) var(--sp-3);
    font-size: var(--text-base);
    font-weight: var(--font-weight-semibold);
    color: var(--color-text-secondary);
  }

  .strip-scroll {
    display: flex;
    gap: var(--sp-3);
    padding: 0 var(--sp-5);
    overflow-x: auto;
    scroll-snap-type: x mandatory;
    scrollbar-width: none;
  }

  .strip-scroll::-webkit-scrollbar {
    display: none;
  }

  .now-card {
    flex: 0 0 200px;
    display: flex;
    flex-direction: column;
    gap: var(--sp-1);
    padding: var(--sp-3);
    background: var(--color-bg-card);
    border-radius: var(--radius-md);
    border: 1px solid var(--color-border);
    text-align: left;
    scroll-snap-align: start;
    transition: all var(--duration-fast) var(--ease-out);
  }

  .now-card:hover {
    background: var(--color-bg-hover);
    border-color: var(--color-accent);
    transform: translateY(-2px);
  }

  .card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .channel-logo {
    border-radius: var(--radius-sm);
    object-fit: contain;
  }

  .channel-num {
    font-size: var(--text-sm);
    font-weight: var(--font-weight-bold);
    color: var(--color-accent);
  }

  .card-title {
    font-size: var(--text-sm);
    font-weight: var(--font-weight-semibold);
    line-height: 1.3;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }

  .card-time {
    font-size: var(--text-xs);
    color: var(--color-text-muted);
  }
</style>
