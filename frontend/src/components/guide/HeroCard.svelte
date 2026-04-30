<script lang="ts">
  import { epgStore } from '../../lib/stores/epg';
  import { uiStore } from '../../lib/stores/ui';
  import { getProgress, formatTime, formatDuration } from '../../lib/utils/time';
  import ProgressBar from '../shared/ProgressBar.svelte';
  import Badge from '../shared/Badge.svelte';
  import LiveIndicator from '../shared/LiveIndicator.svelte';
  import type { NowPlaying } from '../../lib/types/epg';

  let heroIndex = $state(0);
  let heroItems = $derived(epgStore.nowPlaying.filter(np => np.now_playing));

  let current = $derived(heroItems[heroIndex] as NowPlaying | undefined);
  let prog = $derived(current?.now_playing);
  let ch = $derived(current?.channel);
  let progress = $derived(prog ? getProgress(prog.start_ts, prog.stop_ts) : 0);

  // Rotate hero every 30s
  $effect(() => {
    if (heroItems.length <= 1) return;
    const interval = setInterval(() => {
      heroIndex = (heroIndex + 1) % heroItems.length;
    }, 30_000);
    return () => clearInterval(interval);
  });

  function watchNow() {
    if (ch) {
      uiStore.navigate('player');
    }
  }
</script>

{#if prog && ch}
  <div class="hero-card">
    {#if prog.poster || prog.thumbnail}
      <img
        class="hero-backdrop"
        src={prog.poster || prog.thumbnail}
        alt=""
        loading="eager"
      />
    {/if}
    <div class="hero-gradient"></div>
    <div class="hero-content">
      <div class="hero-meta">
        <Badge variant="live"><LiveIndicator size={6} /> LIVE</Badge>
        {#if ch}
          <span class="channel-name">Ch {ch.number} {ch.name}</span>
        {/if}
      </div>
      <h2 class="hero-title">{prog.title}</h2>
      {#if prog.subtitle}
        <p class="hero-subtitle">{prog.subtitle}</p>
      {/if}
      <div class="hero-info">
        {#if prog.episode}<span class="episode">{prog.episode}</span>{/if}
        <span class="time">{formatTime(prog.start)} - {formatTime(prog.stop)}</span>
        <span class="duration">{formatDuration(prog.duration_min)}</span>
        {#if prog.rating}<Badge>{prog.rating}</Badge>{/if}
        {#each prog.categories.slice(0, 3) as cat}
          <Badge variant="accent">{cat}</Badge>
        {/each}
      </div>
      <div class="hero-progress">
        <ProgressBar value={progress} height="4px" />
      </div>
      <div class="hero-actions">
        <button class="watch-btn" onclick={watchNow}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"/></svg>
          Watch Now
        </button>
        <button class="info-btn" onclick={() => { if (prog) uiStore.openProgramme(prog); }}>
          More Info
        </button>
      </div>
    </div>

    {#if heroItems.length > 1}
      <div class="hero-dots">
        {#each heroItems as _, i}
          <button
            class="dot"
            class:active={i === heroIndex}
            onclick={() => { heroIndex = i; }}
            aria-label="Show programme {i + 1}"
          ></button>
        {/each}
      </div>
    {/if}
  </div>
{/if}

<style>
  .hero-card {
    position: relative;
    width: 100%;
    height: 360px;
    overflow: hidden;
  }

  @media (max-width: 768px) {
    .hero-card { height: 280px; }
  }

  .hero-backdrop {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
    opacity: 0.4;
  }

  .hero-gradient {
    position: absolute;
    inset: 0;
    background: linear-gradient(
      to top,
      var(--color-bg) 0%,
      rgba(10, 10, 15, 0.8) 40%,
      rgba(10, 10, 15, 0.4) 100%
    );
  }

  .hero-content {
    position: relative;
    z-index: 1;
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    height: 100%;
    padding: var(--sp-8) var(--sp-6);
    gap: var(--sp-2);
  }

  .hero-meta {
    display: flex;
    align-items: center;
    gap: var(--sp-3);
  }

  .channel-name {
    font-size: var(--text-sm);
    color: var(--color-text-secondary);
    font-weight: var(--font-weight-semibold);
  }

  .hero-title {
    font-size: var(--text-3xl);
    font-weight: var(--font-weight-bold);
    line-height: 1.1;
    max-width: 600px;
  }

  @media (max-width: 768px) {
    .hero-title { font-size: var(--text-2xl); }
  }

  .hero-subtitle {
    font-size: var(--text-base);
    color: var(--color-text-secondary);
    max-width: 500px;
  }

  .hero-info {
    display: flex;
    align-items: center;
    gap: var(--sp-2);
    flex-wrap: wrap;
    font-size: var(--text-sm);
    color: var(--color-text-secondary);
  }

  .episode {
    font-weight: var(--font-weight-semibold);
    color: var(--color-text);
  }

  .hero-progress {
    max-width: 400px;
    margin-top: var(--sp-1);
  }

  .hero-actions {
    display: flex;
    gap: var(--sp-3);
    margin-top: var(--sp-3);
  }

  .watch-btn {
    display: flex;
    align-items: center;
    gap: var(--sp-2);
    padding: var(--sp-3) var(--sp-6);
    background: var(--color-accent);
    color: white;
    border-radius: var(--radius-md);
    font-weight: var(--font-weight-bold);
    font-size: var(--text-base);
    transition: background var(--duration-fast) var(--ease-out);
  }

  .watch-btn:hover {
    background: var(--color-accent-hover);
  }

  .info-btn {
    padding: var(--sp-3) var(--sp-5);
    background: var(--color-surface);
    color: var(--color-text);
    border-radius: var(--radius-md);
    font-weight: var(--font-weight-semibold);
    font-size: var(--text-base);
    backdrop-filter: var(--glass-blur);
    transition: background var(--duration-fast) var(--ease-out);
  }

  .info-btn:hover {
    background: var(--color-surface-hover);
  }

  .hero-dots {
    position: absolute;
    bottom: var(--sp-4);
    right: var(--sp-6);
    display: flex;
    gap: var(--sp-2);
    z-index: 2;
  }

  .dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.3);
    transition: all var(--duration-fast) var(--ease-out);
  }

  .dot.active {
    background: var(--color-accent);
    width: 20px;
    border-radius: 4px;
  }
</style>
