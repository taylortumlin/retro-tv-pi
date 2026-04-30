# CLAUDE.md

Guidance for Claude when working on this repo. Read this before making changes.

## What this is

Pi TV is a Raspberry Pi 5 cable-TV experience. Jellyfin → ErsatzTV (Docker on
Proxmox) → Raspberry Pi. The Pi runs two Flask services:

- **`tv_guide`** (port 5001, gunicorn) — the web app. Serves the Svelte SPA,
  proxies `/stream/<n>.ts` from ErsatzTV, exposes `/api/*` and `/admin/api/*`.
- **`tv_player.py`** (port 5000) — controls a local `mpv` for HDMI output.
  `tv_guide` proxies `/api/player/*` to it.

The frontend is a **Svelte 5 SPA** in `frontend/` (uses `$state` / `$derived`
runes), built with Vite, output to `static/dist/`. The browser playback path
uses **mpegts.js** with native HLS fallback for Safari.

## Working on the backend

`tv_guide` is a **package** (`tv_guide/`), not a single file — refactored
from a monolith. The systemd unit still imports `tv_guide:app`, so the
import path is unchanged.

Module-level state lives in `tv_guide/_state.py` (`CONFIG`, `ERSATZTV_URL`,
`PLAYER_URL`, the three caches, login rate-limit dict). When you need to
read or write it from a submodule:

```python
from tv_guide import _state
url = f"{_state.ERSATZTV_URL}/iptv/..."   # ✓ always current
```

Don't do `from tv_guide._state import ERSATZTV_URL` — that captures the
value at import time and `reload_from_disk()` won't update it.

After changing any Python file:

```bash
sudo systemctl restart tv-guide
sudo systemctl status  tv-guide --no-pager   # confirm Active: running
```

Smoke check after restart:

```bash
for p in / /sw.js /api/epg /admin/api/auth/check /stream/1.ts; do
  curl -s -o /dev/null -w "%{http_code} $p\n" --max-time 5 "http://localhost:5001$p"
done
```

Expect: `200 /`, `200 /sw.js`, `200 /api/epg`, `401 /admin/api/auth/check`,
`200 /stream/1.ts`.

## Working on the frontend

```bash
cd frontend
npm run dev          # vite dev server on :5173, proxies API/stream to :5001
npm test             # vitest one-shot
npm run build        # production build → ../static/dist/
```

After a build, the SPA is served by Flask. Hard-refresh the browser; Vite
hashes filenames so the service worker won't serve a stale bundle.

**Svelte 5 reactivity files MUST end in `.svelte.ts`** if they use runes
outside a `.svelte` component (e.g. `lib/stores/*.svelte.ts`). Don't rename
them to `.ts` — runes won't compile.

## Streaming gotchas (each one cost a real bug)

1. **mpegts.js URLs must be absolute.** The loader runs in a Web Worker,
   which has no document base — relative `/stream/N.ts` throws
   `Failed to parse URL`. Build the URL with `${location.origin}/stream/N.ts`.

2. **Use the proven buffer config in `lib/utils/video.ts`.** The aggressive
   defaults (`liveBufferLatencyChasing: true`, MaxLatency 3, MinRemain 0.5)
   stall continuously against the Flask proxy chunk pattern. Keep:

   ```ts
   liveBufferLatencyChasing: false,
   liveBufferLatencyMaxLatency: 30,
   liveBufferLatencyMinRemain: 8,
   stashInitialSize: 512 * 1024,
   enableStashBuffer: true,
   autoCleanupSourceBuffer: true,
   ```

3. **gunicorn must use `gthread` workers**, not the default sync class. The
   stream proxy holds a worker per active client; with `-w 2 sync`, two
   concurrent streams deadlock everything else (EPG, admin, etc.). The
   systemd unit currently runs `-w 2 -k gthread --threads 32`.

4. **Channel-number guard before `createStreamPlayer`.** Reject zero / NaN
   to avoid stray `/stream/0.ts` requests during component teardown.

5. **First-channel cold start on ErsatzTV is 5–15 s** while ffmpeg spins up.
   Always show a spinner during the wait. Once warm, swaps are <100 ms.

## Themes

`<html data-theme="prevue|comcast|crt">` (omitted for Modern Dark, the
default). Tokens override `:root` in `app.css`. Theme persistence + cycle
shortcut (`Shift+T`) are in `lib/stores/theme.svelte.ts`. Theme is applied
**before** mount in `main.ts` so first paint is correct.

## CI

`.github/workflows/ci.yml` runs on push/PR:

- Frontend: `npm ci → npm test → npm run build` and uploads
  `static/dist/` as an artifact.
- Backend: `python -m compileall tv_guide tv_player.py`.

`npm run check` (svelte-check) is **not** gated yet — there are pre-existing
type errors. If you add new code, keep it passing locally; we can flip the
gate on once the backlog is cleaned up.

Pushing changes to `.github/workflows/` requires the GitHub `workflow` OAuth
scope. The user pushes those commits from their own shell.

## Watch out

- **`config.json` contains personal data** (admin PIN, ErsatzTV LAN IP,
  weather coords) and is already committed in repo history. Don't add new
  personal data; if the user ever wants a clean public snapshot, that needs
  a `git filter-repo` plus a `config.example.json`.

- **Don't restart `tv-guide` without a smoke check.** A bad import or
  startup error and the service flaps. The unit's `Restart=on-failure`
  handles transient blips but not real bugs.

- **Don't amend or force-push.** Always create new commits. (See user's
  global CLAUDE.md: "Always create NEW commits rather than amending".)

- **Verify before claiming success.** When tests pass / build is clean /
  service comes up, run an actual end-to-end check before reporting done —
  every regression we caught this session showed up only at runtime, not in
  the build.

## Quick file map

```
tv_guide/             Flask Blueprints (api, stream, admin, player_proxy, spa) + state
tv_player.py          Local mpv controller (port 5000, separate process)
frontend/src/         Svelte SPA source
  views/              GuideView, PrevueView, QuadView, PlayerView, ...
  components/         detail/ (ProgramModal, ChannelPreview), guide/, player/, ...
  lib/stores/         *.svelte.ts — runes-based state
  lib/utils/video.ts  createStreamPlayer (mpegts.js + HLS fallback)
static/dist/          Built SPA bundle (don't edit; rebuild instead)
templates/            Legacy Jinja, kept for reference; not used at runtime
config.json           Active config (PIN, ErsatzTV URL, channels, weather, ticker)
backups/              Rolling 20 config.json snapshots
.github/workflows/    CI
```
