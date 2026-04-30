<script lang="ts">
  import type { Programme } from '../../lib/types/epg';
  import { uiStore } from '../../lib/stores/ui';
  import { epgStore } from '../../lib/stores/epg';
  import { formatTime, isLive, getProgress } from '../../lib/utils/time';
  import ProgressBar from '../shared/ProgressBar.svelte';
  import LiveIndicator from '../shared/LiveIndicator.svelte';

  interface Props {
    programme: Programme;
  }

  let { programme: prog }: Props = $props();

  let live = $derived(isLive(prog.start_ts, prog.stop_ts));
  let channel = $derived(epgStore.channels.find(ch => ch.id === prog.channel_id));
</script>

<button class="browse-card" onclick={() => uiStore.openProgramme(prog)}>
  <div class="card-poster">
    {#if prog.poster || prog.thumbnail}
      <img src={prog.poster || prog.thumbnail} alt="" loading="lazy" />
    {:else}
      <div class="no-poster">
        <span>{prog.title.charAt(0)}</span>
      </div>
    {/if}
    {#if live}
      <div class="live-badge"><LiveIndicator size={6} /> LIVE</div>
    {/if}
  </div>
  <div class="card-info">
    <p class="card-title">{prog.title}</p>
    {#if channel}
      <span class="card-channel">Ch {channel.number}</span>
    {/if}
    <span class="card-time">{formatTime(prog.start)}</span>
  </div>
  {#if live}
    <ProgressBar value={getProgress(prog.start_ts, prog.stop_ts)} height="2px" color="var(--color-live)" />
  {/if}
</button>

<style>
  .browse-card {
    display: flex;
    flex-direction: column;
    background: var(--color-bg-card);
    border-radius: var(--radius-md);
    border: 1px solid var(--color-border);
    overflow: hidden;
    transition: all var(--duration-normal) var(--ease-out);
    text-align: left;
  }

  .browse-card:hover {
    transform: translateY(-4px);
    border-color: var(--color-accent);
    box-shadow: var(--glass-glow);
  }

  .card-poster {
    position: relative;
    aspect-ratio: 2 / 3;
    background: var(--color-bg);
    overflow: hidden;
  }

  .card-poster img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .no-poster {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    height: 100%;
    font-size: var(--text-2xl);
    font-weight: var(--font-weight-bold);
    color: var(--color-text-muted);
  }

  .live-badge {
    position: absolute;
    top: var(--sp-2);
    left: var(--sp-2);
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
  }

  .card-info {
    padding: var(--sp-2) var(--sp-3);
    display: flex;
    flex-direction: column;
    gap: 2px;
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

  .card-channel {
    font-size: var(--text-xs);
    color: var(--color-accent);
    font-weight: var(--font-weight-semibold);
  }

  .card-time {
    font-size: var(--text-xs);
    color: var(--color-text-muted);
  }
</style>
