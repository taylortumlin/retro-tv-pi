<script lang="ts">
  import { getConfig, putConfigSection, testWeather, testFeed } from '../../lib/api/admin';
  import type { TickerConfig, NewsFeed } from '../../lib/types/admin';
  import { uiStore } from '../../lib/stores/ui';
  import Spinner from '../shared/Spinner.svelte';
  import Icon from '../shared/Icon.svelte';

  let ticker = $state<TickerConfig | null>(null);
  let loading = $state(true);
  let saving = $state(false);

  $effect(() => {
    loadConfig();
  });

  async function loadConfig() {
    try {
      const config = await getConfig();
      ticker = config.ticker;
    } catch {
      uiStore.toast('Failed to load config', 'error');
    } finally {
      loading = false;
    }
  }

  async function save() {
    if (!ticker) return;
    saving = true;
    try {
      await putConfigSection('ticker', ticker);
      uiStore.toast('Ticker config saved', 'success');
    } catch {
      uiStore.toast('Failed to save', 'error');
    } finally {
      saving = false;
    }
  }

  async function handleTestWeather() {
    if (!ticker) return;
    try {
      const result = await testWeather({
        latitude: ticker.weather.latitude,
        longitude: ticker.weather.longitude,
        temperature_unit: ticker.weather.temperature_unit,
      });
      if (result.ok) {
        uiStore.toast(`Weather OK: ${result.temperature}°${result.unit} ${result.condition}`, 'success');
      } else {
        uiStore.toast(`Weather test failed: ${result.error}`, 'error');
      }
    } catch {
      uiStore.toast('Weather test failed', 'error');
    }
  }

  async function handleTestFeed(url: string) {
    try {
      const result = await testFeed(url);
      if (result.ok) {
        uiStore.toast(`Feed OK: ${result.entry_count} entries`, 'success');
      } else {
        uiStore.toast(`Feed test failed: ${result.error}`, 'error');
      }
    } catch {
      uiStore.toast('Feed test failed', 'error');
    }
  }

  function addMessage() {
    if (!ticker) return;
    ticker.messages = [...ticker.messages, ''];
  }

  function removeMessage(i: number) {
    if (!ticker) return;
    ticker.messages = ticker.messages.filter((_, idx) => idx !== i);
  }

  function addFeed() {
    if (!ticker) return;
    ticker.news.feeds = [...ticker.news.feeds, { name: '', url: '' }];
  }

  function removeFeed(i: number) {
    if (!ticker) return;
    ticker.news.feeds = ticker.news.feeds.filter((_, idx) => idx !== i);
  }
</script>

<div class="ticker-editor">
  <div class="editor-header">
    <h2>Ticker & Weather</h2>
    <button class="btn-primary" onclick={save} disabled={saving}>
      {#if saving}<Spinner size={14} />{:else}Save{/if}
    </button>
  </div>

  {#if loading || !ticker}
    <div class="loading"><Spinner /></div>
  {:else}
    <!-- Weather -->
    <section class="config-section">
      <h3>Weather</h3>
      <div class="form-grid">
        <label>
          <span>Location</span>
          <input type="text" bind:value={ticker.weather.location_name} />
        </label>
        <label>
          <span>Latitude</span>
          <input type="number" step="0.001" bind:value={ticker.weather.latitude} />
        </label>
        <label>
          <span>Longitude</span>
          <input type="number" step="0.001" bind:value={ticker.weather.longitude} />
        </label>
        <label>
          <span>Unit</span>
          <select bind:value={ticker.weather.temperature_unit}>
            <option value="fahrenheit">Fahrenheit</option>
            <option value="celsius">Celsius</option>
          </select>
        </label>
        <label>
          <span>Forecast Days</span>
          <input type="number" min="1" max="14" bind:value={ticker.forecast_days} />
        </label>
      </div>
      <button class="btn-secondary" onclick={handleTestWeather}>Test Weather</button>
    </section>

    <!-- Ticker Messages -->
    <section class="config-section">
      <h3>Ticker Messages</h3>
      <div class="message-list">
        {#each ticker.messages as msg, i}
          <div class="message-row">
            <input type="text" bind:value={ticker.messages[i]} placeholder="Message text..." />
            <button class="remove-btn" onclick={() => removeMessage(i)} aria-label="Remove message">
              <Icon name="close" size={16} />
            </button>
          </div>
        {/each}
        <button class="btn-secondary" onclick={addMessage}>+ Add Message</button>
      </div>
      <label class="inline-label">
        <input type="number" min="10" max="200" bind:value={ticker.speed} style="width: 80px;" />
        <span>Speed (px/s)</span>
      </label>
    </section>

    <!-- News Feeds -->
    <section class="config-section">
      <h3>News Feeds</h3>
      <label class="checkbox-label">
        <input type="checkbox" bind:checked={ticker.news.show_headlines} />
        Show Headlines
      </label>
      <div class="feed-list">
        {#each ticker.news.feeds as feed, i}
          <div class="feed-row">
            <input type="text" bind:value={feed.name} placeholder="Name" class="feed-name" />
            <input type="url" bind:value={feed.url} placeholder="RSS URL" class="feed-url" />
            <button class="btn-small" onclick={() => handleTestFeed(feed.url)}>Test</button>
            <button class="remove-btn" onclick={() => removeFeed(i)} aria-label="Remove feed">
              <Icon name="close" size={16} />
            </button>
          </div>
        {/each}
        <button class="btn-secondary" onclick={addFeed}>+ Add Feed</button>
      </div>
      <label class="inline-label">
        <input type="number" min="1" max="50" bind:value={ticker.news.max_headlines} style="width: 60px;" />
        <span>Max Headlines</span>
      </label>
    </section>
  {/if}
</div>

<style>
  .ticker-editor {
    display: flex;
    flex-direction: column;
    gap: var(--sp-5);
  }

  .editor-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  h2 { font-size: var(--text-xl); font-weight: var(--font-weight-bold); }
  h3 { font-size: var(--text-base); font-weight: var(--font-weight-semibold); margin-bottom: var(--sp-3); }

  .btn-primary, .btn-secondary, .btn-small {
    display: flex;
    align-items: center;
    gap: var(--sp-1);
    padding: var(--sp-2) var(--sp-4);
    border-radius: var(--radius-sm);
    font-weight: var(--font-weight-semibold);
    font-size: var(--text-sm);
  }

  .btn-primary { background: var(--color-accent); color: white; }
  .btn-secondary { background: var(--color-surface); }
  .btn-small { padding: var(--sp-1) var(--sp-2); font-size: var(--text-xs); background: var(--color-accent-subtle); color: var(--color-accent); }

  .loading { display: flex; justify-content: center; padding: var(--sp-10); }

  .config-section {
    padding: var(--sp-5);
    background: var(--color-bg-card);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
  }

  .form-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: var(--sp-3);
    margin-bottom: var(--sp-3);
  }

  label {
    display: flex;
    flex-direction: column;
    gap: var(--sp-1);
    font-size: var(--text-sm);
  }

  label span {
    color: var(--color-text-secondary);
    font-size: var(--text-xs);
  }

  input, select {
    padding: var(--sp-2);
    background: var(--color-bg);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-sm);
    font-size: var(--text-sm);
  }

  input:focus, select:focus {
    border-color: var(--color-accent);
    outline: none;
  }

  .checkbox-label {
    flex-direction: row;
    align-items: center;
    gap: var(--sp-2);
    margin-bottom: var(--sp-3);
  }

  .checkbox-label input[type="checkbox"] {
    width: 18px;
    height: 18px;
  }

  .inline-label {
    flex-direction: row;
    align-items: center;
    gap: var(--sp-2);
    margin-top: var(--sp-3);
  }

  .message-list, .feed-list {
    display: flex;
    flex-direction: column;
    gap: var(--sp-2);
    margin-bottom: var(--sp-3);
  }

  .message-row, .feed-row {
    display: flex;
    gap: var(--sp-2);
    align-items: center;
  }

  .message-row input {
    flex: 1;
  }

  .feed-name { width: 100px; flex-shrink: 0; }
  .feed-url { flex: 1; }

  .remove-btn {
    display: flex;
    color: var(--color-text-muted);
    padding: var(--sp-1);
  }

  .remove-btn:hover { color: var(--color-error); }
</style>
