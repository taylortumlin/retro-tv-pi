<script lang="ts">
  import type { Channel } from '../../lib/types/epg';
  import FavoriteStar from '../shared/FavoriteStar.svelte';

  interface Props {
    channel: Channel;
    compact?: boolean;
  }

  let { channel, compact = false }: Props = $props();
</script>

<div class="channel-badge" class:compact>
  {#if channel.logo}
    <img src={channel.logo} alt="" class="logo" />
  {/if}
  <div class="info">
    <span class="number tabular-nums">{channel.number}</span>
    {#if !compact}
      <span class="name">{channel.name}</span>
    {/if}
  </div>
  {#if !compact}
    <FavoriteStar channelId={channel.id} size={14} />
  {/if}
</div>

<style>
  .channel-badge {
    display: flex;
    align-items: center;
    gap: var(--sp-2);
    padding: var(--sp-2) var(--sp-3);
    width: 160px;
    flex-shrink: 0;
    position: sticky;
    left: 0;
    z-index: 3;
    background: var(--color-bg-elevated);
    border-right: 1px solid var(--color-border);
  }

  .compact {
    width: auto;
    position: static;
    background: none;
    border: none;
    padding: var(--sp-1);
  }

  .logo {
    width: 28px;
    height: 28px;
    border-radius: var(--radius-sm);
    object-fit: contain;
  }

  .info {
    display: flex;
    flex-direction: column;
    min-width: 0;
  }

  .number {
    font-size: var(--text-xs);
    font-weight: var(--font-weight-bold);
    color: var(--color-accent);
  }

  .name {
    font-size: var(--text-xs);
    color: var(--color-text-secondary);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
</style>
