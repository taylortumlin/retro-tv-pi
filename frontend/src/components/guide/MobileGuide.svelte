<script lang="ts">
  import { epgStore } from '../../lib/stores/epg';
  import { favoritesStore } from '../../lib/stores/favorites';
  import { uiStore } from '../../lib/stores/ui';
  import { getProgress, formatTime, isLive, formatDuration } from '../../lib/utils/time';
  import ProgressBar from '../shared/ProgressBar.svelte';
  import LiveIndicator from '../shared/LiveIndicator.svelte';
  import FavoriteStar from '../shared/FavoriteStar.svelte';
  import type { Channel } from '../../lib/types/epg';

  interface Props {
    category?: string | null;
    favoritesOnly?: boolean;
  }

  let { category = null, favoritesOnly = false }: Props = $props();

  let filteredChannels = $derived.by(() => {
    let chs: Channel[] = epgStore.channels;
    if (favoritesOnly) chs = chs.filter(ch => favoritesStore.isFavorite(ch.id));
    if (category) {
      const ids = new Set(epgStore.programmes.filter(p => p.categories.includes(category!)).map(p => p.channel_id));
      chs = chs.filter(ch => ids.has(ch.id));
    }
    return chs;
  });
</script>

<div class="mobile-guide">
  {#each filteredChannels as channel (channel.id)}
    {@const upcoming = epgStore.getUpcoming(channel.id, 4)}
    <div class="channel-group">
      <div class="channel-header">
        <span class="ch-num tabular-nums font-mono">{channel.number}</span>
        <span class="ch-name">{channel.name}</span>
        <FavoriteStar channelId={channel.id} size={16} />
      </div>

      <div class="programme-list">
        {#each upcoming as prog}
          {@const live = isLive(prog.start_ts, prog.stop_ts)}
          <button
            class="programme-card"
            class:live
            onclick={() => uiStore.openProgramme(prog)}
          >
            <div class="prog-header">
              {#if live}<LiveIndicator size={6} />{/if}
              <span class="prog-time tabular-nums">{formatTime(prog.start)}</span>
              <span class="prog-dur">{formatDuration(prog.duration_min)}</span>
            </div>
            <p class="prog-title">{prog.title}</p>
            {#if prog.subtitle}<p class="prog-sub">{prog.subtitle}</p>{/if}
            {#if live}
              <ProgressBar value={getProgress(prog.start_ts, prog.stop_ts)} height="2px" color="var(--color-live)" />
            {/if}
          </button>
        {/each}
      </div>
    </div>
  {/each}
</div>

<style>
  .mobile-guide {
    display: flex;
    flex-direction: column;
    gap: var(--sp-4);
    padding: 0 var(--sp-4);
  }

  .channel-group {
    background: var(--color-bg-card);
    border-radius: var(--radius-md);
    border: 1px solid var(--color-border);
    overflow: hidden;
  }

  .channel-header {
    display: flex;
    align-items: center;
    gap: var(--sp-2);
    padding: var(--sp-3) var(--sp-4);
    background: var(--color-bg-elevated);
    border-bottom: 1px solid var(--color-border);
    position: sticky;
    top: 0;
    z-index: 2;
  }

  .ch-num {
    font-size: var(--text-sm);
    font-weight: var(--font-weight-bold);
    color: var(--color-accent);
    min-width: 24px;
  }

  .ch-name {
    font-size: var(--text-sm);
    font-weight: var(--font-weight-semibold);
    flex: 1;
  }

  .programme-list {
    display: flex;
    flex-direction: column;
  }

  .programme-card {
    display: flex;
    flex-direction: column;
    gap: var(--sp-1);
    padding: var(--sp-3) var(--sp-4);
    text-align: left;
    border-bottom: 1px solid var(--color-border);
    transition: background var(--duration-fast) var(--ease-out);
  }

  .programme-card:last-child {
    border-bottom: none;
  }

  .programme-card:hover {
    background: var(--color-bg-hover);
  }

  .programme-card.live {
    border-left: 3px solid var(--color-live);
  }

  .prog-header {
    display: flex;
    align-items: center;
    gap: var(--sp-2);
  }

  .prog-time {
    font-size: var(--text-xs);
    font-weight: var(--font-weight-semibold);
    color: var(--color-text-secondary);
  }

  .prog-dur {
    font-size: var(--text-xs);
    color: var(--color-text-muted);
  }

  .prog-title {
    font-size: var(--text-sm);
    font-weight: var(--font-weight-semibold);
  }

  .prog-sub {
    font-size: var(--text-xs);
    color: var(--color-text-secondary);
  }
</style>
