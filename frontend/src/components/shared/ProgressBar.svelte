<script lang="ts">
  interface Props {
    value: number;
    max?: number;
    color?: string;
    height?: string;
  }

  let { value, max = 100, color = 'var(--color-accent)', height = '3px' }: Props = $props();
  let pct = $derived(Math.min(100, Math.max(0, (value / max) * 100)));
</script>

<div class="progress-bar" style:height={height} role="progressbar" aria-valuenow={value} aria-valuemin={0} aria-valuemax={max}>
  <div class="fill" style:width="{pct}%" style:background={color}></div>
</div>

<style>
  .progress-bar {
    width: 100%;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 2px;
    overflow: hidden;
  }
  .fill {
    height: 100%;
    border-radius: 2px;
    transition: width var(--duration-normal) var(--ease-out);
  }
</style>
