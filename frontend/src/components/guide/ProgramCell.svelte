<script lang="ts">
  import type { Programme } from '../../lib/types/epg';
  import { getProgress, isLive } from '../../lib/utils/time';
  import { uiStore } from '../../lib/stores/ui';
  import ProgressBar from '../shared/ProgressBar.svelte';

  interface Props {
    programme: Programme;
    pixelsPerHour?: number;
    gridStartTs: number;
  }

  let { programme: prog, pixelsPerHour = 300, gridStartTs }: Props = $props();

  let live = $derived(isLive(prog.start_ts, prog.stop_ts));
  let progress = $derived(live ? getProgress(prog.start_ts, prog.stop_ts) : 0);
  let width = $derived(((prog.stop_ts - prog.start_ts) / 3600) * pixelsPerHour);
  let offset = $derived(((prog.start_ts - gridStartTs) / 3600) * pixelsPerHour);
</script>

<button
  class="program-cell"
  class:live
  style:width="{Math.max(width, 60)}px"
  style:left="{Math.max(offset, 0)}px"
  onclick={() => uiStore.openProgramme(prog)}
  title="{prog.title}{prog.subtitle ? ` — ${prog.subtitle}` : ''}"
  aria-label="{prog.title}, {live ? 'Live now' : ''}"
>
  <span class="cell-title">{prog.title}</span>
  {#if prog.subtitle}
    <span class="cell-sub">{prog.subtitle}</span>
  {/if}
  {#if live}
    <div class="cell-progress">
      <ProgressBar value={progress} height="2px" color="var(--color-live)" />
    </div>
  {/if}
</button>

<style>
  .program-cell {
    position: absolute;
    top: 2px;
    bottom: 2px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    padding: var(--sp-1) var(--sp-2);
    background: var(--color-bg-card);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-sm);
    overflow: hidden;
    text-align: left;
    transition: all var(--duration-fast) var(--ease-out);
  }

  .program-cell:hover {
    background: var(--color-bg-hover);
    border-color: var(--color-accent);
    z-index: 2;
  }

  .program-cell.live {
    border-color: var(--color-live);
    border-left: 3px solid var(--color-live);
  }

  .cell-title {
    font-size: var(--text-xs);
    font-weight: var(--font-weight-semibold);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    line-height: 1.3;
  }

  .cell-sub {
    font-size: 0.625rem;
    color: var(--color-text-muted);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .cell-progress {
    margin-top: var(--sp-1);
  }
</style>
