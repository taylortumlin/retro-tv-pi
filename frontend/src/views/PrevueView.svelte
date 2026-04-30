<script lang="ts">
  import { epgStore } from '../lib/stores/epg';
  import { uiStore } from '../lib/stores/ui';
  import { createStreamPlayer, type StreamPlayer } from '../lib/utils/video';
  import { formatTime, isLive, getProgress } from '../lib/utils/time';
  import LiveIndicator from '../components/shared/LiveIndicator.svelte';
  import Spinner from '../components/shared/Spinner.svelte';
  import Icon from '../components/shared/Icon.svelte';
  import { fly } from 'svelte/transition';

  const ROTATION_MS = 15_000;

  $effect(() => {
    if (epgStore.channels.length === 0) epgStore.load();
  });

  // Two video elements; whichever is "active" is visible/audible.
  // The other holds the next channel pre-loaded for a near-seamless swap.
  let videoA: HTMLVideoElement;
  let videoB: HTMLVideoElement;
  let playerA: StreamPlayer | null = null;
  let playerB: StreamPlayer | null = null;
  let slotA = $state(0);   // channel number
  let slotB = $state(0);
  let activeSlot = $state<'a' | 'b'>('a');
  let nextIdx = $state(2); // next channel index in epgStore.channels to preload
  let muted = $state(true);
  let paused = $state(false);
  let bannerKey = $state(0);
  let loadedA = $state(false);
  let loadedB = $state(false);

  // --- Init: seed both slots once channels are loaded ---
  let seeded = $state(false);
  $effect(() => {
    if (seeded) return;
    if (epgStore.channels.length < 1) return;
    const nums = epgStore.channels.map(c => parseInt(c.number)).filter(Number.isFinite);
    if (nums.length === 0) return;
    slotA = nums[0];
    slotB = nums[Math.min(1, nums.length - 1)];
    nextIdx = 2 % nums.length;
    seeded = true;
  });

  // --- Stream player lifecycle for slot A ---
  $effect(() => {
    if (!videoA || !slotA) return;
    loadedA = false;
    playerA = createStreamPlayer(videoA, slotA);
    playerA.mute(activeSlot !== 'a' || muted);
    playerA.play();
    const onReady = () => { loadedA = true; };
    videoA.addEventListener('loadeddata', onReady);
    videoA.addEventListener('playing', onReady);
    return () => {
      videoA.removeEventListener('loadeddata', onReady);
      videoA.removeEventListener('playing', onReady);
      playerA?.destroy();
      playerA = null;
    };
  });

  // --- Stream player lifecycle for slot B ---
  $effect(() => {
    if (!videoB || !slotB) return;
    loadedB = false;
    playerB = createStreamPlayer(videoB, slotB);
    playerB.mute(activeSlot !== 'b' || muted);
    playerB.play();
    const onReady = () => { loadedB = true; };
    videoB.addEventListener('loadeddata', onReady);
    videoB.addEventListener('playing', onReady);
    return () => {
      videoB.removeEventListener('loadeddata', onReady);
      videoB.removeEventListener('playing', onReady);
      playerB?.destroy();
      playerB = null;
    };
  });

  // --- Mute state sync ---
  $effect(() => {
    playerA?.mute(activeSlot !== 'a' || muted);
    playerB?.mute(activeSlot !== 'b' || muted);
  });

  // --- Rotation timer ---
  let rotateTimer: ReturnType<typeof setInterval> | null = null;
  $effect(() => {
    if (!seeded || paused) return;
    rotateTimer = setInterval(rotate, ROTATION_MS);
    return () => {
      if (rotateTimer) clearInterval(rotateTimer);
      rotateTimer = null;
    };
  });

  function rotate() {
    if (epgStore.channels.length === 0) return;
    const nums = epgStore.channels.map(c => parseInt(c.number)).filter(Number.isFinite);
    if (nums.length === 0) return;

    // Swap active slot — the previously preloaded one becomes visible.
    activeSlot = activeSlot === 'a' ? 'b' : 'a';
    bannerKey++;

    // Then load the next channel into the now-inactive slot for the next swap.
    const nextChannel = nums[nextIdx % nums.length];
    if (activeSlot === 'a') {
      slotB = nextChannel;
    } else {
      slotA = nextChannel;
    }
    nextIdx = (nextIdx + 1) % nums.length;
  }

  function skip(dir: 1 | -1) {
    if (epgStore.channels.length === 0) return;
    const nums = epgStore.channels.map(c => parseInt(c.number)).filter(Number.isFinite);
    if (nums.length === 0) return;
    const currentNum = activeSlot === 'a' ? slotA : slotB;
    const i = nums.indexOf(currentNum);
    const target = nums[((i === -1 ? 0 : i) + dir + nums.length) % nums.length];
    if (activeSlot === 'a') slotA = target;
    else slotB = target;
    bannerKey++;
    // Reset rotation timer to give the user a fresh 15s on the new channel.
    if (rotateTimer) {
      clearInterval(rotateTimer);
      rotateTimer = setInterval(rotate, ROTATION_MS);
    }
  }

  // --- Active channel + programme derived for the banner / overlay ---
  let activeChannelNum = $derived(activeSlot === 'a' ? slotA : slotB);
  let activeChannel = $derived(
    epgStore.channels.find(c => parseInt(c.number) === activeChannelNum)
  );
  let activeProg = $derived(activeChannel ? epgStore.getCurrentProgramme(activeChannel.id) : undefined);
  let progress = $derived(activeProg ? getProgress(activeProg.start_ts, activeProg.stop_ts) : 0);

  // --- Keyboard ---
  function handleKey(e: KeyboardEvent) {
    const t = (e.target as HTMLElement)?.tagName;
    if (t === 'INPUT' || t === 'TEXTAREA' || t === 'SELECT') return;

    if (e.key === 'Escape') { e.preventDefault(); uiStore.navigate('guide'); return; }
    if (e.key === ' ')      { e.preventDefault(); paused = !paused; return; }
    if (e.key === 'm')      { e.preventDefault(); muted = !muted; return; }
    if (e.key === 'ArrowLeft')  { e.preventDefault(); skip(-1); return; }
    if (e.key === 'ArrowRight') { e.preventDefault(); skip(1); return; }
  }

  // --- EPG grid: 3-hour slice for visible channel context ---
  let gridStartTs = $derived(Math.floor(Date.now() / 1000 / 1800) * 1800);
  let gridSlots = $derived(Array.from({ length: 6 }, (_, i) => gridStartTs + i * 1800));
</script>

<svelte:window onkeydown={handleKey} />

<div class="prevue">
  <!-- Video stage: both <video>s live here; only the active one is visible. -->
  <div class="stage">
    <video
      bind:this={videoA}
      class="stage-video"
      class:hidden={activeSlot !== 'a'}
      autoplay
      playsinline
      muted={activeSlot !== 'a' || muted}
    ></video>
    <video
      bind:this={videoB}
      class="stage-video"
      class:hidden={activeSlot !== 'b'}
      autoplay
      playsinline
      muted={activeSlot !== 'b' || muted}
    ></video>

    {#if (activeSlot === 'a' && !loadedA) || (activeSlot === 'b' && !loadedB)}
      <div class="stage-loading">
        <Spinner size={48} />
      </div>
    {/if}

    <!-- Sliding channel banner — re-keys on each rotation. -->
    {#key bannerKey}
      {#if activeChannel}
        <div class="banner" in:fly={{ x: -260, duration: 380 }}>
          <div class="banner-num font-mono">CH {activeChannel.number}</div>
          <div class="banner-text">
            <span class="banner-name">{activeChannel.name}</span>
            {#if activeProg}
              <span class="banner-prog">{activeProg.title}</span>
            {/if}
          </div>
          <LiveIndicator size={8} />
        </div>
      {/if}
    {/key}

    <!-- Bottom info / progress -->
    {#if activeProg}
      <div class="bottom-info">
        <div class="bottom-line">
          <span class="bottom-title">{activeProg.title}</span>
          {#if activeProg.subtitle}<span class="bottom-sub">{activeProg.subtitle}</span>{/if}
        </div>
        <div class="bottom-line">
          <span class="bottom-time font-mono">{formatTime(activeProg.start)} – {formatTime(activeProg.stop)}</span>
          <span class="bottom-pct font-mono">{Math.round(progress)}%</span>
        </div>
        <div class="bottom-bar">
          <div class="bottom-fill" style:width="{progress}%"></div>
        </div>
      </div>
    {/if}

    <!-- Controls -->
    <div class="controls">
      <button onclick={() => skip(-1)} aria-label="Previous channel">
        <Icon name="chevron-left" size={20} />
      </button>
      <button onclick={() => { paused = !paused; }} aria-label={paused ? 'Resume rotation' : 'Pause rotation'}>
        <Icon name={paused ? 'play' : 'pause'} size={20} />
      </button>
      <button onclick={() => { muted = !muted; }} aria-label={muted ? 'Unmute' : 'Mute'}>
        <Icon name={muted ? 'mute' : 'unmute'} size={20} />
      </button>
      <button onclick={() => skip(1)} aria-label="Next channel">
        <Icon name="chevron-right" size={20} />
      </button>
      <span class="rot-status">
        {paused ? 'Paused' : 'Rotating every 15s'}
      </span>
      <button class="exit" onclick={() => uiStore.navigate('guide')} aria-label="Exit Prevue">
        ESC
      </button>
    </div>
  </div>

  <!-- EPG grid — 3-hour preview of all channels -->
  <div class="grid">
    <div class="grid-ruler">
      <div class="ruler-spacer"></div>
      {#each gridSlots as ts (ts)}
        <div class="ruler-cell font-mono">{formatTime(new Date(ts * 1000).toISOString())}</div>
      {/each}
    </div>
    <div class="grid-rows">
      {#each epgStore.channels as ch (ch.id)}
        {@const progs = epgStore.getProgrammesForChannel(ch.id)
            .filter(p => p.stop_ts > gridStartTs && p.start_ts < gridStartTs + 6 * 1800)
            .sort((a, b) => a.start_ts - b.start_ts)}
        <div class="grid-row" class:active={parseInt(ch.number) === activeChannelNum}>
          <div class="row-channel">
            <span class="row-num font-mono tabular-nums">{ch.number}</span>
            <span class="row-name">{ch.name}</span>
          </div>
          <div class="row-cells">
            {#each progs as p}
              {@const live = isLive(p.start_ts, p.stop_ts)}
              <button
                class="grid-cell"
                class:live
                onclick={() => uiStore.openProgramme(p)}
                title="{p.title}"
              >
                <span class="cell-time font-mono">{formatTime(p.start)}</span>
                <span class="cell-title">{p.title}</span>
              </button>
            {/each}
          </div>
        </div>
      {/each}
    </div>
  </div>
</div>

<style>
  .prevue {
    position: fixed;
    inset: var(--header-height) 0 0 0;
    display: grid;
    grid-template-rows: 60% 40%;
    background: var(--color-bg);
    z-index: 50;
    overflow: hidden;
  }

  @media (max-width: 768px) {
    .prevue {
      inset: var(--header-height) 0 var(--mobile-nav-height) 0;
    }
  }

  .stage {
    position: relative;
    background: #000;
    overflow: hidden;
  }

  .stage-video {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    object-fit: contain;
    background: #000;
    transition: opacity var(--duration-fast) var(--ease-out);
  }

  .stage-video.hidden {
    opacity: 0;
    pointer-events: none;
  }

  .stage-loading {
    position: absolute;
    inset: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--color-text-muted);
    background: rgba(0, 0, 0, 0.5);
  }

  .banner {
    position: absolute;
    top: var(--sp-4);
    left: var(--sp-4);
    z-index: 5;
    display: flex;
    align-items: center;
    gap: var(--sp-3);
    padding: var(--sp-3) var(--sp-4);
    background: rgba(0, 0, 0, 0.78);
    border: 2px solid var(--color-accent);
    border-radius: var(--radius-md);
    backdrop-filter: blur(8px);
    box-shadow: var(--glass-glow);
    max-width: 70%;
  }

  .banner-num {
    font-size: var(--text-2xl);
    font-weight: var(--font-weight-bold);
    color: var(--color-gold);
    letter-spacing: 0.05em;
  }

  .banner-text {
    display: flex;
    flex-direction: column;
    min-width: 0;
  }

  .banner-name {
    font-size: var(--text-base);
    font-weight: var(--font-weight-bold);
    color: white;
  }

  .banner-prog {
    font-size: var(--text-sm);
    color: var(--color-text-secondary);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .bottom-info {
    position: absolute;
    bottom: var(--sp-12);
    left: 0;
    right: 0;
    z-index: 4;
    padding: var(--sp-4) var(--sp-6);
    background: linear-gradient(to top, rgba(0, 0, 0, 0.85), transparent);
    color: white;
    display: flex;
    flex-direction: column;
    gap: var(--sp-1);
  }

  .bottom-line {
    display: flex;
    align-items: baseline;
    gap: var(--sp-3);
    flex-wrap: wrap;
  }

  .bottom-title {
    font-size: var(--text-xl);
    font-weight: var(--font-weight-bold);
  }

  .bottom-sub {
    font-size: var(--text-sm);
    color: var(--color-text-secondary);
  }

  .bottom-time {
    font-size: var(--text-sm);
    color: var(--color-text-secondary);
  }

  .bottom-pct {
    font-size: var(--text-xs);
    color: var(--color-text-muted);
  }

  .bottom-bar {
    height: 3px;
    background: rgba(255, 255, 255, 0.15);
    border-radius: 2px;
    overflow: hidden;
  }

  .bottom-fill {
    height: 100%;
    background: var(--color-live);
    transition: width 1s linear;
  }

  .controls {
    position: absolute;
    bottom: var(--sp-3);
    left: var(--sp-4);
    right: var(--sp-4);
    z-index: 6;
    display: flex;
    align-items: center;
    gap: var(--sp-2);
  }

  .controls button {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 36px;
    height: 36px;
    border-radius: var(--radius-full);
    background: rgba(0, 0, 0, 0.6);
    color: white;
    border: 1px solid rgba(255, 255, 255, 0.15);
    transition: all var(--duration-fast) var(--ease-out);
  }

  .controls button:hover {
    background: rgba(0, 0, 0, 0.85);
    border-color: var(--color-accent);
  }

  .controls .exit {
    margin-left: auto;
    width: auto;
    padding: 0 var(--sp-3);
    font-size: var(--text-xs);
    font-weight: var(--font-weight-bold);
    letter-spacing: 0.1em;
  }

  .rot-status {
    margin-left: var(--sp-3);
    font-size: var(--text-xs);
    color: var(--color-text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  /* ===== EPG grid ===== */
  .grid {
    display: flex;
    flex-direction: column;
    background: var(--color-bg-elevated);
    border-top: 1px solid var(--color-accent);
    overflow: hidden;
  }

  .grid-ruler {
    display: grid;
    grid-template-columns: 160px repeat(6, 1fr);
    background: var(--color-bg-card);
    border-bottom: 1px solid var(--color-border);
  }

  .ruler-cell {
    padding: var(--sp-2) var(--sp-3);
    font-size: var(--text-xs);
    color: var(--color-accent);
    font-weight: var(--font-weight-bold);
    border-left: 1px solid var(--color-border);
  }

  .ruler-spacer {
    border-right: 1px solid var(--color-border);
  }

  .grid-rows {
    flex: 1;
    overflow-y: auto;
  }

  .grid-row {
    display: grid;
    grid-template-columns: 160px 1fr;
    border-bottom: 1px solid var(--color-border);
    min-height: 40px;
  }

  .grid-row.active {
    background: var(--color-accent-subtle);
  }

  .row-channel {
    display: flex;
    align-items: center;
    gap: var(--sp-2);
    padding: var(--sp-2) var(--sp-3);
    background: var(--color-bg-card);
    border-right: 1px solid var(--color-border);
  }

  .row-num {
    font-size: var(--text-sm);
    font-weight: var(--font-weight-bold);
    color: var(--color-accent);
    min-width: 28px;
  }

  .row-name {
    font-size: var(--text-sm);
    font-weight: var(--font-weight-semibold);
    color: var(--color-text);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .row-cells {
    display: flex;
    overflow-x: auto;
    scrollbar-width: none;
  }

  .row-cells::-webkit-scrollbar { display: none; }

  .grid-cell {
    flex: 1 0 200px;
    display: flex;
    flex-direction: column;
    gap: 2px;
    padding: var(--sp-1) var(--sp-2);
    text-align: left;
    border-right: 1px solid var(--color-border);
    transition: background var(--duration-fast) var(--ease-out);
  }

  .grid-cell:hover {
    background: var(--color-surface-hover);
  }

  .grid-cell.live {
    border-left: 3px solid var(--color-live);
    background: rgba(255, 59, 59, 0.05);
  }

  .cell-time {
    font-size: 0.625rem;
    color: var(--color-text-muted);
    font-weight: var(--font-weight-semibold);
  }

  .cell-title {
    font-size: var(--text-xs);
    font-weight: var(--font-weight-semibold);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
</style>
