<script lang="ts">
  import { login } from '../../lib/api/admin';
  import Spinner from '../shared/Spinner.svelte';

  interface Props {
    onLogin: () => void;
  }

  let { onLogin }: Props = $props();

  let pin = $state('');
  let error = $state('');
  let loading = $state(false);
  let inputEl: HTMLInputElement;

  async function handleSubmit() {
    if (pin.length < 4) return;
    loading = true;
    error = '';
    try {
      await login(pin);
      onLogin();
    } catch (e: any) {
      error = e.message?.includes('429') ? 'Too many attempts. Try again in 5 minutes.' : 'Invalid PIN';
      pin = '';
      inputEl?.focus();
    } finally {
      loading = false;
    }
  }

  function handleInput() {
    if (pin.length === 4) handleSubmit();
  }
</script>

<div class="login-screen">
  <div class="login-card glass">
    <h2>Admin</h2>
    <p class="login-hint">Enter your 4-digit PIN</p>

    <form onsubmit={(e) => { e.preventDefault(); handleSubmit(); }}>
      <div class="pin-input-wrap">
        <input
          bind:this={inputEl}
          bind:value={pin}
          oninput={handleInput}
          type="password"
          inputmode="numeric"
          pattern="[0-9]*"
          maxlength="4"
          placeholder="····"
          autocomplete="off"
          aria-label="PIN"
          class="pin-input tabular-nums"
        />
      </div>

      {#if error}
        <p class="error">{error}</p>
      {/if}

      <button type="submit" class="submit-btn" disabled={loading || pin.length < 4}>
        {#if loading}
          <Spinner size={18} />
        {:else}
          Unlock
        {/if}
      </button>
    </form>
  </div>
</div>

<style>
  .login-screen {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    padding: var(--sp-5);
  }

  .login-card {
    width: 100%;
    max-width: 340px;
    padding: var(--sp-8);
    border-radius: var(--radius-lg);
    text-align: center;
    display: flex;
    flex-direction: column;
    gap: var(--sp-4);
  }

  h2 {
    font-size: var(--text-2xl);
    font-weight: var(--font-weight-bold);
  }

  .login-hint {
    color: var(--color-text-secondary);
    font-size: var(--text-sm);
  }

  form {
    display: flex;
    flex-direction: column;
    gap: var(--sp-4);
  }

  .pin-input-wrap {
    display: flex;
    justify-content: center;
  }

  .pin-input {
    width: 160px;
    text-align: center;
    font-size: var(--text-2xl);
    letter-spacing: 0.5em;
    padding: var(--sp-3);
    background: var(--color-bg-card);
    border: 2px solid var(--color-border);
    border-radius: var(--radius-md);
    outline: none;
    transition: border-color var(--duration-fast) var(--ease-out);
  }

  .pin-input:focus {
    border-color: var(--color-accent);
  }

  .error {
    color: var(--color-error);
    font-size: var(--text-sm);
  }

  .submit-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: var(--sp-3);
    background: var(--color-accent);
    color: white;
    border-radius: var(--radius-md);
    font-weight: var(--font-weight-bold);
    transition: background var(--duration-fast) var(--ease-out);
  }

  .submit-btn:hover:not(:disabled) {
    background: var(--color-accent-hover);
  }

  .submit-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
</style>
