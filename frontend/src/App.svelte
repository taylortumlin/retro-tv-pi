<script lang="ts">
  import Shell from './components/layout/Shell.svelte';
  import { uiStore } from './lib/stores/ui';
  import GuideView from './views/GuideView.svelte';
  import DiscoverView from './views/DiscoverView.svelte';
  import PlayerView from './views/PlayerView.svelte';
  import WeatherView from './views/WeatherView.svelte';
  import AdminView from './views/AdminView.svelte';
  import SearchView from './views/SearchView.svelte';
  import ProgramModal from './components/detail/ProgramModal.svelte';
</script>

<Shell>
  {#snippet children()}
    {#if uiStore.activeView === 'guide'}
      <GuideView />
    {:else if uiStore.activeView === 'discover'}
      <DiscoverView />
    {:else if uiStore.activeView === 'player'}
      <PlayerView />
    {:else if uiStore.activeView === 'weather'}
      <WeatherView />
    {:else if uiStore.activeView === 'admin'}
      <AdminView />
    {:else if uiStore.activeView === 'search'}
      <SearchView />
    {/if}

    {#if uiStore.modalProgramme}
      <ProgramModal programme={uiStore.modalProgramme} onClose={() => uiStore.closeProgramme()} />
    {/if}
  {/snippet}
</Shell>
