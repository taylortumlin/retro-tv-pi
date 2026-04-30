<script lang="ts">
  import type { Channel, Programme } from '../../lib/types/epg';
  import ChannelBadge from './ChannelBadge.svelte';
  import ProgramCell from './ProgramCell.svelte';

  interface Props {
    channel: Channel;
    programmes: Programme[];
    pixelsPerHour?: number;
    gridStartTs: number;
    gridHours: number;
  }

  let { channel, programmes, pixelsPerHour = 300, gridStartTs, gridHours }: Props = $props();

  let visible = $derived(
    programmes
      .filter(p => p.stop_ts > gridStartTs && p.start_ts < gridStartTs + gridHours * 3600)
      .sort((a, b) => a.start_ts - b.start_ts)
  );
</script>

<div class="guide-row" role="row">
  <ChannelBadge {channel} />
  <div class="programmes" style:width="{gridHours * pixelsPerHour}px" role="gridcell">
    {#each visible as prog (prog.channel_id + prog.start)}
      <ProgramCell programme={prog} {pixelsPerHour} {gridStartTs} />
    {/each}
  </div>
</div>

<style>
  .guide-row {
    display: flex;
    height: 56px;
    border-bottom: 1px solid var(--color-border);
  }

  .programmes {
    position: relative;
    flex-shrink: 0;
  }
</style>
