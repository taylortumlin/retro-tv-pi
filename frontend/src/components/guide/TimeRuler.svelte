<script lang="ts">
  interface Props {
    startHour: number;
    hours?: number;
    pixelsPerHour?: number;
  }

  let { startHour, hours = 4, pixelsPerHour = 300 }: Props = $props();

  let slots = $derived(
    Array.from({ length: hours * 2 }, (_, i) => {
      const totalMinutes = startHour * 60 + i * 30;
      const h = Math.floor(totalMinutes / 60) % 24;
      const m = totalMinutes % 60;
      const d = new Date();
      d.setHours(h, m, 0, 0);
      return d.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });
    })
  );
</script>

<div class="time-ruler" style:width="{hours * pixelsPerHour}px" role="presentation">
  {#each slots as label, i}
    <div class="time-slot" style:width="{pixelsPerHour / 2}px">
      <span class="time-label tabular-nums">{label}</span>
    </div>
  {/each}
</div>

<style>
  .time-ruler {
    display: flex;
    height: 32px;
    background: var(--color-bg-elevated);
    border-bottom: 1px solid var(--color-border);
    position: sticky;
    top: 0;
    z-index: 5;
  }

  .time-slot {
    flex-shrink: 0;
    display: flex;
    align-items: center;
    padding-left: var(--sp-2);
    border-left: 1px solid var(--color-border);
  }

  .time-label {
    font-size: var(--text-xs);
    color: var(--color-text-muted);
    white-space: nowrap;
  }
</style>
