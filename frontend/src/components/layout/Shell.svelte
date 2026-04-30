<script lang="ts">
  import type { Snippet } from 'svelte';
  import Header from './Header.svelte';
  import MobileNav from './MobileNav.svelte';
  import Toast from '../shared/Toast.svelte';

  interface Props {
    children: Snippet;
  }

  let { children }: Props = $props();
</script>

<a href="#main-content" class="skip-link">Skip to main content</a>

<Header />

<main id="main-content" class="main-content">
  {@render children()}
</main>

<MobileNav />
<Toast />

<style>
  .main-content {
    min-height: calc(100vh - var(--header-height));
    padding-bottom: var(--sp-4);
  }

  @media (max-width: 768px) {
    .main-content {
      padding-bottom: calc(var(--mobile-nav-height) + var(--sp-4));
    }
  }
</style>
