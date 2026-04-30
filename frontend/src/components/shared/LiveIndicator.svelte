<script lang="ts">
  interface Props {
    size?: number;
  }
  let { size = 8 }: Props = $props();
</script>

<span class="live-dot" style:width="{size}px" style:height="{size}px" aria-label="Live">
</span>

<style>
  .live-dot {
    display: inline-block;
    border-radius: 50%;
    background: var(--color-live);
    box-shadow: 0 0 6px var(--color-live-glow);
    animation: pulse 2s ease-in-out infinite;
    flex-shrink: 0;
  }
  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
  }
</style>
