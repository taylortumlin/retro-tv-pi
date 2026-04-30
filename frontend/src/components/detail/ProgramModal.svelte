<script lang="ts">
  import type { Programme } from '../../lib/types/epg';
  import { uiStore } from '../../lib/stores/ui';
  import { epgStore } from '../../lib/stores/epg';
  import { remindersStore } from '../../lib/stores/reminders';
  import { tuneChannel } from '../../lib/api/player';
  import { getProgress, formatTime, formatDuration, isLive, formatDate } from '../../lib/utils/time';
  import ProgressBar from '../shared/ProgressBar.svelte';
  import Badge from '../shared/Badge.svelte';
  import LiveIndicator from '../shared/LiveIndicator.svelte';
  import { focusTrap } from '../../lib/actions/focusTrap';
  import { fly, fade } from 'svelte/transition';

  interface Props {
    programme: Programme;
    onClose: () => void;
  }

  let { programme: prog, onClose }: Props = $props();

  let live = $derived(isLive(prog.start_ts, prog.stop_ts));
  let progress = $derived(live ? getProgress(prog.start_ts, prog.stop_ts) : 0);
  let channel = $derived(epgStore.channels.find(ch => ch.id === prog.channel_id));
  let hasReminder = $derived(remindersStore.hasReminder(prog.channel_id, prog.start_ts));

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === 'Escape') onClose();
  }

  function watchNow() {
    uiStore.navigate('player');
    onClose();
  }

  async function tuneTv() {
    if (!channel) return;
    try {
      await tuneChannel(parseInt(channel.number));
      uiStore.toast(`Tuned to Ch ${channel.number}`, 'success');
    } catch {
      uiStore.toast('Failed to tune TV', 'error');
    }
  }

  function toggleReminder() {
    if (hasReminder) {
      remindersStore.remove(prog.channel_id, prog.start_ts);
      uiStore.toast('Reminder removed', 'info');
    } else {
      remindersStore.add({
        programmeTitle: prog.title,
        channelId: prog.channel_id,
        startTs: prog.start_ts,
      });
      uiStore.toast('Reminder set', 'success');
    }
  }
</script>

<svelte:window onkeydown={handleKeydown} />

<!-- svelte-ignore a11y_no_static_element_interactions -->
<!-- svelte-ignore a11y_click_events_have_key_events -->
<div class="modal-backdrop" transition:fade={{ duration: 200 }} onclick={onClose}>
  <!-- svelte-ignore a11y_no_static_element_interactions -->
  <!-- svelte-ignore a11y_click_events_have_key_events -->
  <!-- svelte-ignore a11y_interactive_supports_focus -->
  <div
    class="modal"
    class:bottom-sheet={uiStore.isMobile}
    transition:fly={{ y: uiStore.isMobile ? 300 : 0, duration: 300 }}
    onclick={(e) => e.stopPropagation()}
    role="dialog"
    aria-label="{prog.title} details"
    use:focusTrap
  >
    <!-- Hero -->
    <div class="modal-hero">
      {#if prog.poster || prog.thumbnail}
        <img src={prog.poster || prog.thumbnail} alt="" class="modal-poster" />
      {/if}
      <div class="modal-hero-gradient"></div>
      <button class="close-btn" onclick={onClose} aria-label="Close">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6L6 18M6 6l12 12"/></svg>
      </button>
    </div>

    <!-- Content -->
    <div class="modal-body">
      <div class="modal-meta">
        {#if live}<Badge variant="live"><LiveIndicator size={6} /> LIVE</Badge>{/if}
        {#if channel}
          <span class="channel">Ch {channel.number} · {channel.name}</span>
        {/if}
      </div>

      <h2 class="modal-title">{prog.title}</h2>
      {#if prog.subtitle}<p class="modal-subtitle">{prog.subtitle}</p>{/if}

      <div class="modal-info">
        <span>{formatDate(prog.start)}</span>
        <span>{formatTime(prog.start)} – {formatTime(prog.stop)}</span>
        <span>{formatDuration(prog.duration_min)}</span>
        {#if prog.episode}<span class="episode">{prog.episode}</span>{/if}
      </div>

      {#if live}
        <div class="modal-progress">
          <ProgressBar value={progress} height="4px" color="var(--color-live)" />
          <span class="progress-label">{Math.round(progress)}% complete</span>
        </div>
      {/if}

      <div class="modal-badges">
        {#if prog.rating}<Badge>{prog.rating}</Badge>{/if}
        {#each prog.categories as cat}
          <Badge variant="accent">{cat}</Badge>
        {/each}
      </div>

      <div class="modal-actions">
        {#if live}
          <button class="action-primary" onclick={watchNow}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"/></svg>
            Watch Now
          </button>
        {/if}
        <button class="action-secondary" onclick={tuneTv}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="7" width="20" height="15" rx="2" ry="2"/><polyline points="17 2 12 7 7 2"/></svg>
          Tune TV
        </button>
        {#if !live}
          <button
            class="action-secondary"
            class:active={hasReminder}
            onclick={toggleReminder}
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill={hasReminder ? 'currentColor' : 'none'} stroke="currentColor" stroke-width="2"><path d="M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9M13.73 21a2 2 0 01-3.46 0"/></svg>
            {hasReminder ? 'Reminder Set' : 'Set Reminder'}
          </button>
        {/if}
      </div>
    </div>
  </div>
</div>

<style>
  .modal-backdrop {
    position: fixed;
    inset: 0;
    z-index: 200;
    background: rgba(0, 0, 0, 0.7);
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .modal {
    width: 90%;
    max-width: 560px;
    max-height: 85vh;
    background: var(--color-bg-elevated);
    border-radius: var(--radius-lg);
    overflow: hidden;
    overflow-y: auto;
    box-shadow: var(--shadow-lg);
  }

  .modal.bottom-sheet {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    width: 100%;
    max-width: 100%;
    max-height: 90vh;
    border-radius: var(--radius-xl) var(--radius-xl) 0 0;
  }

  .modal-hero {
    position: relative;
    height: 200px;
    background: var(--color-bg-card);
    overflow: hidden;
  }

  .modal-poster {
    width: 100%;
    height: 100%;
    object-fit: cover;
    opacity: 0.6;
  }

  .modal-hero-gradient {
    position: absolute;
    inset: 0;
    background: linear-gradient(to top, var(--color-bg-elevated) 0%, transparent 60%);
  }

  .close-btn {
    position: absolute;
    top: var(--sp-3);
    right: var(--sp-3);
    width: 36px;
    height: 36px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(0, 0, 0, 0.5);
    border-radius: var(--radius-full);
    color: white;
    backdrop-filter: blur(8px);
  }

  .modal-body {
    padding: var(--sp-5);
    display: flex;
    flex-direction: column;
    gap: var(--sp-3);
  }

  .modal-meta {
    display: flex;
    align-items: center;
    gap: var(--sp-3);
  }

  .channel {
    font-size: var(--text-sm);
    color: var(--color-text-secondary);
    font-weight: var(--font-weight-semibold);
  }

  .modal-title {
    font-size: var(--text-2xl);
    font-weight: var(--font-weight-bold);
    line-height: 1.1;
  }

  .modal-subtitle {
    font-size: var(--text-base);
    color: var(--color-text-secondary);
  }

  .modal-info {
    display: flex;
    flex-wrap: wrap;
    gap: var(--sp-2);
    font-size: var(--text-sm);
    color: var(--color-text-secondary);
  }

  .modal-info span:not(:last-child)::after {
    content: '·';
    margin-left: var(--sp-2);
    color: var(--color-text-muted);
  }

  .episode {
    font-weight: var(--font-weight-semibold);
    color: var(--color-text);
  }

  .modal-progress {
    display: flex;
    flex-direction: column;
    gap: var(--sp-1);
  }

  .progress-label {
    font-size: var(--text-xs);
    color: var(--color-text-muted);
  }

  .modal-badges {
    display: flex;
    flex-wrap: wrap;
    gap: var(--sp-2);
  }

  .modal-actions {
    display: flex;
    flex-wrap: wrap;
    gap: var(--sp-3);
    margin-top: var(--sp-2);
  }

  .action-primary {
    display: flex;
    align-items: center;
    gap: var(--sp-2);
    padding: var(--sp-3) var(--sp-5);
    background: var(--color-accent);
    color: white;
    border-radius: var(--radius-md);
    font-weight: var(--font-weight-bold);
    transition: background var(--duration-fast) var(--ease-out);
  }

  .action-primary:hover {
    background: var(--color-accent-hover);
  }

  .action-secondary {
    display: flex;
    align-items: center;
    gap: var(--sp-2);
    padding: var(--sp-3) var(--sp-4);
    background: var(--color-surface);
    border-radius: var(--radius-md);
    font-weight: var(--font-weight-semibold);
    transition: all var(--duration-fast) var(--ease-out);
  }

  .action-secondary:hover {
    background: var(--color-surface-hover);
  }

  .action-secondary.active {
    color: var(--color-gold);
  }
</style>
