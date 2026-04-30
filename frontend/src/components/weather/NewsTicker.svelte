<script lang="ts">
  import type { NewsHeadline } from '../../lib/types/weather';

  interface Props {
    headlines: NewsHeadline[];
  }

  let { headlines }: Props = $props();

  let text = $derived(
    headlines.map(h => `${h.source}: ${h.title}`).join('   ·   ')
  );
</script>

<div class="news-ticker" aria-label="News ticker" role="marquee">
  <div class="ticker-track">
    <span class="ticker-text">{text}   ·   {text}</span>
  </div>
</div>

<style>
  .news-ticker {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    height: 32px;
    background: var(--color-bg-elevated);
    border-top: 1px solid var(--color-border);
    overflow: hidden;
    z-index: 50;
    display: flex;
    align-items: center;
  }

  @media (max-width: 768px) {
    .news-ticker {
      bottom: var(--mobile-nav-height);
    }
  }

  .ticker-track {
    display: flex;
    white-space: nowrap;
    animation: scroll 60s linear infinite;
  }

  .ticker-text {
    font-size: var(--text-xs);
    color: var(--color-text-secondary);
    padding: 0 var(--sp-8);
  }

  @keyframes scroll {
    0% { transform: translateX(0); }
    100% { transform: translateX(-50%); }
  }
</style>
