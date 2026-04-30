<script lang="ts">
  import { epgStore } from '../lib/stores/epg';
  import { uiStore } from '../lib/stores/ui';
  import QuadCell from '../components/quad/QuadCell.svelte';

  $effect(() => {
    if (epgStore.channels.length === 0) epgStore.load();
  });

  // Default to first 4 channel numbers (parsed) the moment EPG is available.
  let slots = $state<number[]>([0, 0, 0, 0]);
  let selected = $state(0);
  let initialized = $state(false);

  $effect(() => {
    if (initialized) return;
    if (epgStore.channels.length < 1) return;
    const seed = epgStore.channels.slice(0, 4).map(c => parseInt(c.number));
    // Pad with the last channel if fewer than 4.
    while (seed.length < 4) seed.push(seed[seed.length - 1] || 1);
    slots = seed;
    initialized = true;
  });

  function setSlotChannel(slot: number, dir: 1 | -1) {
    if (epgStore.channels.length === 0) return;
    const nums = epgStore.channels.map(c => parseInt(c.number)).filter(Number.isFinite);
    if (nums.length === 0) return;
    const i = nums.indexOf(slots[slot]);
    const next = nums[((i === -1 ? 0 : i) + dir + nums.length) % nums.length];
    slots[slot] = next;
  }

  function handleKey(e: KeyboardEvent) {
    const t = (e.target as HTMLElement)?.tagName;
    if (t === 'INPUT' || t === 'TEXTAREA' || t === 'SELECT') return;
    if (e.key === 'Escape' || e.key === 'q') {
      e.preventDefault();
      uiStore.navigate('guide');
      return;
    }
    if (e.key === 'ArrowUp')   { e.preventDefault(); setSlotChannel(selected, -1); return; }
    if (e.key === 'ArrowDown') { e.preventDefault(); setSlotChannel(selected,  1); return; }
    // Number keys jump audio focus to a slot 1-4.
    if (e.key === '1' || e.key === '2' || e.key === '3' || e.key === '4') {
      selected = parseInt(e.key) - 1;
    }
  }
</script>

<svelte:window onkeydown={handleKey} />

<div class="quad">
  {#each slots as channelNumber, i (i)}
    <QuadCell
      {channelNumber}
      selected={selected === i}
      onClick={() => { selected = i; }}
    />
  {/each}

  <button
    class="quad-exit"
    onclick={() => uiStore.navigate('guide')}
    aria-label="Close quad view"
  >
    ESC
  </button>

  <div class="quad-hint">
    <span class="font-mono">↑↓</span> change channel ·
    <span class="font-mono">1-4</span> select cell ·
    <span class="font-mono">ESC</span> close
  </div>
</div>

<style>
  .quad {
    position: fixed;
    inset: var(--header-height) 0 0 0;
    display: grid;
    grid-template-columns: 1fr 1fr;
    grid-template-rows: 1fr 1fr;
    gap: 2px;
    background: #000;
    z-index: 50;
  }

  @media (max-width: 768px) {
    .quad {
      inset: var(--header-height) 0 var(--mobile-nav-height) 0;
    }
  }

  .quad-exit {
    position: absolute;
    top: var(--sp-3);
    right: var(--sp-3);
    z-index: 10;
    padding: var(--sp-2) var(--sp-3);
    border-radius: var(--radius-full);
    background: rgba(0, 0, 0, 0.7);
    backdrop-filter: blur(8px);
    color: white;
    font-size: var(--text-xs);
    font-weight: var(--font-weight-bold);
    letter-spacing: 0.1em;
    border: 1px solid rgba(255, 255, 255, 0.2);
  }

  .quad-exit:hover {
    background: rgba(0, 0, 0, 0.85);
    border-color: var(--color-accent);
  }

  .quad-hint {
    position: absolute;
    bottom: var(--sp-3);
    left: 50%;
    transform: translateX(-50%);
    z-index: 10;
    padding: var(--sp-1) var(--sp-3);
    background: rgba(0, 0, 0, 0.65);
    backdrop-filter: blur(8px);
    border-radius: var(--radius-full);
    font-size: var(--text-xs);
    color: var(--color-text-secondary);
    pointer-events: none;
  }

  .quad-hint .font-mono {
    color: var(--color-accent);
    font-weight: var(--font-weight-bold);
  }
</style>
