<script lang="ts">
  import Shell from './components/layout/Shell.svelte';
  import { uiStore } from './lib/stores/ui';
  import GuideView from './views/GuideView.svelte';
  import DiscoverView from './views/DiscoverView.svelte';
  import PlayerView from './views/PlayerView.svelte';
  import WeatherView from './views/WeatherView.svelte';
  import AdminView from './views/AdminView.svelte';
  import SearchView from './views/SearchView.svelte';
  import UpNextView from './views/UpNextView.svelte';
  import TonightView from './views/TonightView.svelte';
  import QuadView from './views/QuadView.svelte';
  import PrevueView from './views/PrevueView.svelte';
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
    {:else if uiStore.activeView === 'upnext'}
      <UpNextView />
    {:else if uiStore.activeView === 'tonight'}
      <TonightView />
    {:else if uiStore.activeView === 'quad'}
      <QuadView />
    {:else if uiStore.activeView === 'prevue'}
      <PrevueView />
    {:else}
      <div style="padding: var(--sp-10); text-align: center; color: var(--color-text-muted)">
        <h2 style="font-size: var(--text-2xl); color: var(--color-text); margin-bottom: var(--sp-3)">
          {uiStore.activeView.charAt(0).toUpperCase() + uiStore.activeView.slice(1)} mode
        </h2>
        <p>Coming soon.</p>
      </div>
    {/if}

    {#if uiStore.modalProgramme}
      <ProgramModal programme={uiStore.modalProgramme} onClose={() => uiStore.closeProgramme()} />
    {/if}
  {/snippet}
</Shell>
