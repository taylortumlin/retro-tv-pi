<script lang="ts">
  import { playerStore } from '../../lib/stores/player';
  import { epgStore } from '../../lib/stores/epg';
  import { uiStore } from '../../lib/stores/ui';
  import { fade } from 'svelte/transition';

  let buffer = $state('');
  let timer: ReturnType<typeof setTimeout> | null = null;

  function tune() {
    const num = parseInt(buffer);
    buffer = '';
    if (timer) { clearTimeout(timer); timer = null; }
    if (!Number.isFinite(num) || num <= 0) return;
    const target = epgStore.channels.find(c => parseInt(c.number) === num);
    if (target) {
      playerStore.setChannel(target);
      uiStore.toast(`Tuned to Ch ${num}`, 'success');
    } else {
      uiStore.toast(`No channel ${num}`, 'error');
    }
  }

  function handleKey(e: KeyboardEvent) {
    const t = (e.target as HTMLElement)?.tagName;
    if (t === 'INPUT' || t === 'TEXTAREA' || t === 'SELECT') return;
    if (e.ctrlKey || e.metaKey || e.altKey) return;

    if (e.key >= '0' && e.key <= '9') {
      e.preventDefault();
      // Cap at 4 digits — channel numbers are realistically <= 999.
      buffer = (buffer + e.key).slice(0, 4);
      if (timer) clearTimeout(timer);
      timer = setTimeout(tune, 1500);
      return;
    }

    if (buffer && e.key === 'Enter') {
      e.preventDefault();
      tune();
    }
    if (buffer && e.key === 'Escape') {
      e.preventDefault();
      buffer = '';
      if (timer) { clearTimeout(timer); timer = null; }
    }
  }
</script>

<svelte:window onkeydown={handleKey} />

{#if buffer}
  <div class="osd" transition:fade={{ duration: 120 }}>
    <span class="osd-label">CH</span>
    <span class="osd-num font-mono">{buffer}</span>
  </div>
{/if}

<style>
  .osd {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    display: flex;
    align-items: baseline;
    gap: var(--sp-3);
    padding: var(--sp-4) var(--sp-8);
    background: rgba(0, 0, 0, 0.78);
    border: 2px solid var(--color-accent);
    border-radius: var(--radius-lg);
    box-shadow: var(--glass-glow);
    z-index: 30;
    pointer-events: none;
    backdrop-filter: blur(8px);
  }

  .osd-label {
    font-size: var(--text-xl);
    font-weight: var(--font-weight-bold);
    color: var(--color-accent);
    letter-spacing: 0.1em;
  }

  .osd-num {
    font-size: 5rem;
    line-height: 1;
    font-weight: var(--font-weight-bold);
    color: white;
    letter-spacing: 0.05em;
    min-width: 2ch;
    text-align: center;
  }
</style>
