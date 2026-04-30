<script lang="ts">
  import { favoritesStore } from '../../lib/stores/favorites';

  interface Props {
    channelId: string;
    size?: number;
  }

  let { channelId, size = 20 }: Props = $props();
  let isFav = $derived(favoritesStore.isFavorite(channelId));
</script>

<button
  class="fav-star"
  class:active={isFav}
  onclick={() => favoritesStore.toggle(channelId)}
  aria-label={isFav ? 'Remove from favorites' : 'Add to favorites'}
  aria-pressed={isFav}
>
  <svg width={size} height={size} viewBox="0 0 24 24" fill={isFav ? 'var(--color-gold)' : 'none'} stroke={isFav ? 'var(--color-gold)' : 'currentColor'} stroke-width="2">
    <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
  </svg>
</button>

<style>
  .fav-star {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: var(--sp-1);
    border-radius: var(--radius-full);
    transition: transform var(--duration-fast) var(--ease-spring);
    color: var(--color-text-muted);
  }
  .fav-star:hover {
    transform: scale(1.15);
    color: var(--color-gold);
  }
  .fav-star.active {
    animation: pop var(--duration-normal) var(--ease-spring);
  }
  @keyframes pop {
    50% { transform: scale(1.3); }
  }
</style>
