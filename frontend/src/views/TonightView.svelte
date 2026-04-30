<script lang="ts">
  import { epgStore } from '../lib/stores/epg';
  import { uiStore } from '../lib/stores/ui';
  import { tonightWindow, formatTime, formatDuration, isLive } from '../lib/utils/time';
  import LiveIndicator from '../components/shared/LiveIndicator.svelte';
  import ProgressBar from '../components/shared/ProgressBar.svelte';
  import SkeletonLoader from '../components/shared/SkeletonLoader.svelte';
  import type { Programme } from '../lib/types/epg';

  $effect(() => {
    if (epgStore.channels.length === 0) epgStore.load();
  });

  let window_ = $derived(tonightWindow());

  let tonightByChannel = $derived.by(() => {
    const [startTs, stopTs] = window_;
    const map = new Map<string, Programme[]>();
    for (const p of epgStore.programmes) {
      // Include any programme overlapping the primetime window.
      if (p.stop_ts <= startTs || p.start_ts >= stopTs) continue;
      const arr = map.get(p.channel_id) ?? [];
      arr.push(p);
      map.set(p.channel_id, arr);
    }
    for (const [, arr] of map) arr.sort((a, b) => a.start_ts - b.start_ts);
    // Use channel order from epgStore.channels.
    return epgStore.channels
      .map(ch => ({ channel: ch, programmes: map.get(ch.id) ?? [] }))
      .filter(row => row.programmes.length > 0);
  });

  let windowLabel = $derived.by(() => {
    const [startTs] = window_;
    const d = new Date(startTs * 1000);
    const today = new Date();
    const sameDay = d.toDateString() === today.toDateString();
    return sameDay ? 'Tonight' : 'Tomorrow';
  });
</script>

<div class="tonight-view">
  <header class="view-header">
    <h2>{windowLabel}</h2>
    <p class="view-sub">Primetime, 7:00 PM – 11:00 PM</p>
  </header>

  {#if epgStore.loading && tonightByChannel.length === 0}
    <div class="loading">
      {#each Array(6) as _}
        <SkeletonLoader width="100%" height="80px" radius="var(--radius-md)" />
      {/each}
    </div>
  {:else if tonightByChannel.length === 0}
    <p class="empty">No primetime programmes scheduled.</p>
  {:else}
    <div class="rows">
      {#each tonightByChannel as row (row.channel.id)}
        <section class="row">
          <div class="ch-cell">
            {#if row.channel.logo}
              <div class="logo-wrap">
                <img src={row.channel.logo} alt="" class="logo" />
              </div>
            {:else}
              <div class="logo-fallback font-mono">{row.channel.name?.charAt(0) || '?'}</div>
            {/if}
            <div class="ch-text">
              <span class="ch-num font-mono tabular-nums">{row.channel.number}</span>
              <span class="ch-name">{row.channel.name}</span>
            </div>
          </div>
          <div class="prog-strip">
            {#each row.programmes as prog}
              {@const live = isLive(prog.start_ts, prog.stop_ts)}
              <button
                class="prog-cell"
                class:live
                onclick={() => uiStore.openProgramme(prog)}
                title="{prog.title}{prog.subtitle ? ` — ${prog.subtitle}` : ''}"
              >
                <div class="prog-head">
                  <span class="prog-time font-mono">{formatTime(prog.start)}</span>
                  <span class="prog-dur">{formatDuration(prog.duration_min)}</span>
                  {#if live}<LiveIndicator size={6} />{/if}
                </div>
                <span class="prog-title">{prog.title}</span>
                {#if live}
                  <ProgressBar value={(Date.now() / 1000 - prog.start_ts) / (prog.stop_ts - prog.start_ts) * 100} height="2px" color="var(--color-live)" />
                {/if}
              </button>
            {/each}
          </div>
        </section>
      {/each}
    </div>
  {/if}
</div>

<style>
  .tonight-view {
    padding: var(--sp-5);
    max-width: 1400px;
    margin: 0 auto;
  }

  .view-header {
    margin-bottom: var(--sp-6);
  }

  .view-header h2 {
    font-size: var(--text-2xl);
    font-weight: var(--font-weight-bold);
  }

  .view-sub {
    margin-top: var(--sp-1);
    font-size: var(--text-sm);
    color: var(--color-text-muted);
  }

  .rows {
    display: flex;
    flex-direction: column;
    gap: var(--sp-3);
  }

  .row {
    display: flex;
    gap: var(--sp-3);
    align-items: stretch;
    background: var(--color-bg-card);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
    padding: var(--sp-3);
  }

  .ch-cell {
    flex: 0 0 160px;
    display: flex;
    align-items: center;
    gap: var(--sp-2);
    border-right: 1px solid var(--color-border);
    padding-right: var(--sp-3);
  }

  .logo-wrap {
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--color-surface);
    border-radius: var(--radius-sm);
    padding: 2px;
    flex-shrink: 0;
  }

  .logo { width: 100%; height: 100%; object-fit: contain; }

  .logo-fallback {
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--color-accent-subtle);
    border-radius: var(--radius-sm);
    font-size: var(--text-sm);
    font-weight: var(--font-weight-bold);
    color: var(--color-accent);
    flex-shrink: 0;
  }

  .ch-text {
    display: flex;
    flex-direction: column;
    min-width: 0;
  }

  .ch-num {
    font-size: var(--text-xs);
    font-weight: var(--font-weight-bold);
    color: var(--color-accent);
  }

  .ch-name {
    font-size: var(--text-sm);
    font-weight: var(--font-weight-semibold);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .prog-strip {
    flex: 1;
    display: flex;
    gap: var(--sp-2);
    overflow-x: auto;
    scrollbar-width: thin;
  }

  .prog-cell {
    flex: 0 0 220px;
    display: flex;
    flex-direction: column;
    gap: var(--sp-1);
    padding: var(--sp-2) var(--sp-3);
    background: var(--color-surface);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-sm);
    text-align: left;
    transition: all var(--duration-fast) var(--ease-out);
  }

  .prog-cell:hover {
    background: var(--color-surface-hover);
    border-color: var(--color-accent);
    box-shadow: var(--glass-glow);
  }

  .prog-cell.live {
    border-left: 3px solid var(--color-live);
  }

  .prog-head {
    display: flex;
    align-items: center;
    gap: var(--sp-2);
    font-size: var(--text-xs);
    color: var(--color-text-secondary);
  }

  .prog-time {
    font-weight: var(--font-weight-semibold);
  }

  .prog-dur {
    color: var(--color-text-muted);
  }

  .prog-title {
    font-size: var(--text-sm);
    font-weight: var(--font-weight-semibold);
    line-height: 1.3;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }

  .empty {
    padding: var(--sp-10);
    text-align: center;
    color: var(--color-text-muted);
  }

  .loading {
    display: flex;
    flex-direction: column;
    gap: var(--sp-3);
  }
</style>
