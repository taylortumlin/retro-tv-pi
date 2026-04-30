<script lang="ts">
  import { favoritesStore } from '../../lib/stores/favorites';
  import Icon from './Icon.svelte';

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
  <span style:color={isFav ? 'var(--color-gold)' : 'currentColor'}>
    <Icon name={isFav ? 'star-filled' : 'star'} {size} fill={isFav ? 'var(--color-gold)' : 'none'} />
  </span>
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
