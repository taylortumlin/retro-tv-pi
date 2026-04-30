<script lang="ts">
  interface Props {
    width?: string;
    height?: string;
    radius?: string;
  }
  let { width = '100%', height = '1em', radius = 'var(--radius-sm)' }: Props = $props();
</script>

<div class="skeleton" style:width style:height style:border-radius={radius}></div>

<style>
  .skeleton {
    background: linear-gradient(90deg, var(--color-bg-card) 25%, var(--color-bg-hover) 50%, var(--color-bg-card) 75%);
    background-size: 200% 100%;
    animation: shimmer 1.5s infinite;
  }
  @keyframes shimmer {
    0% { background-position: 200% 0; }
    100% { background-position: -200% 0; }
  }
</style>
