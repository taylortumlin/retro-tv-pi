# Pi TV Guide

Turn your Raspberry Pi into a retro cable TV experience with a full-featured TV guide, live channel preview, and themed viewing modes -- streaming from Jellyfin via ErsatzTV.

## Architecture

```
Jellyfin (Proxmox) --> ErsatzTV (Proxmox) --> Raspberry Pi (Display)
                        generates IPTV         tv_player.py (mpv)
                        channels + EPG         tv_guide.py (web UI)
```

## Features

- **20 themed channels** with smart collections (Crime, Comedy, Sci-Fi, Horror, etc.)
- **Prevue Guide mode** -- authentic 1993 Prevue Channel look with a rotating live video preview, a 3-hour scrolling EPG grid, and a channel banner on every rotation (15-second cycle, dual-video preload for seamless swaps)
- **Quad split view** -- 2x2 fullscreen grid of four live channels at once, click a cell to make it the audio-active one
- **Up Next & Tonight views** -- upcoming programmes across all channels (sorted) and primetime grids
- **Live channel preview in detail modal** -- clicking a live programme shows the actual channel stream right in the modal hero
- **Weather & News view** -- WeatherStar 4000-style weather with 7-day forecast, hourly chart, and live news from AP/BBC/NPR
- **4 visual themes** -- Modern Dark, Prevue Classic, Comcast Blue, CRT Retro (scanlines + vignette + flicker, respects `prefers-reduced-motion`)
- **Favorites & Reminders** -- star channels, set show reminders that fire browser notifications when the tab is open
- **Channel surfing OSD** -- type a channel number on the player view, big on-screen readout, auto-tunes after a 1.5s debounce
- **Category filtering** -- filter the guide by genre (Action, Comedy, Drama, etc.)
- **Custom SVG logos** for all 20 channels
- **Live streaming** -- watch any channel directly in the browser via mpegts.js (MPEG-TS) with native HLS fallback for Safari
- **Scrolling news ticker** with content-proportional scroll speed
- **Auto-refresh EPG** every 5 minutes

## Quick Start

### 1. Deploy ErsatzTV (on Proxmox)

```bash
cd ersatztv
docker-compose up -d
```

Access: `http://<proxmox-ip>:8409`

### 2. Configure ErsatzTV

1. Add Media Source -> Jellyfin
2. Enter your Jellyfin URL + API key
3. Sync libraries
4. Create channels and smart collections
5. Set scheduling (flood/shuffle)

### 3. Setup Pi

```bash
chmod +x setup.sh
./setup.sh
```

### 4. Configure & Run

```bash
# Edit config with your ErsatzTV IP, weather location, admin PIN
nano ~/pi-tv/config.json

# Build the frontend (run once, and after any frontend change)
cd ~/pi-tv/frontend && npm ci && npm run build

# Enable auto-start (gunicorn for the guide, mpv for the player)
sudo systemctl enable tv-player tv-guide
sudo systemctl start  tv-player tv-guide
```

For development: `npm run dev` in `frontend/` runs Vite on port 5173 with the Flask backend proxied through.

## Controls

### Web Guide (port 5001)
Open `http://<pi-ip>:5001` on any device

- **G** -- Guide view
- **P** -- Prevue mode
- **U** -- Up Next
- **T** -- Tonight
- **Q** -- Quad split view (2x2 live channels)
- **D** -- Discover
- **W** -- Weather & News
- **/** -- Search programmes
- **Shift+T** -- Cycle themes (Modern -> Prevue -> Comcast -> CRT)
- **0-9** -- Channel surfing OSD (on player view)
- **Escape** -- Exit Quad / Prevue / close modal

**Inside Prevue mode:** Space pauses rotation; Arrow Left/Right skips channels; M mutes.

**Inside Quad mode:** click a cell or press 1-4 to select it; Arrow Up/Down cycles the selected cell's channel.

### Player (port 5000)
- **1-9** -- Switch channels
- **Space** -- Pause/Play
- **M** -- Mute
- **Q** -- Quit

## Files

```
pi-tv/
├── README.md
├── PLAN.md                       # Architecture decisions
├── IMPLEMENTATION.md             # Setup guide
├── CHANNEL_SETUP.md              # Smart collection details
├── config.json                   # Channels, weather, news, ticker config
├── setup.sh                      # Pi installer
├── requirements.txt              # Python deps (Flask, feedparser, requests, gunicorn)
├── tv_guide/                     # Web guide server (Flask Blueprints)
│   ├── __init__.py               # App factory + _startup() + module-level `app`
│   ├── _state.py                 # CONFIG, caches, URLs (shared module-level state)
│   ├── api.py                    # /api/{epg,now,weather,ticker,news} blueprint
│   ├── stream.py                 # /stream/<n>.{ts,m3u8} proxy to ErsatzTV
│   ├── player_proxy.py           # /api/player/* -> tv_player.py
│   ├── admin.py                  # /admin/api/* (auth, config, status, backups)
│   ├── spa.py                    # /, /<path> -> SPA index.html
│   ├── epg.py                    # XMLTV fetch + filtering + refresh loop
│   ├── weather.py                # Open-Meteo
│   ├── news.py                   # RSS aggregation (feedparser)
│   ├── config_io.py              # atomic write + rolling backups
│   └── _xmltv.py                 # parse_xmltv_time helper
├── tv_player.py                  # mpv hardware player (port 5000, controlled via API)
├── frontend/                     # Svelte 5 SPA
│   ├── src/
│   │   ├── App.svelte
│   │   ├── views/                # GuideView, PrevueView, QuadView, PlayerView, ...
│   │   ├── components/           # detail/, guide/, player/, weather/, admin/, ...
│   │   └── lib/                  # stores/ (theme, ui, epg, ...), utils/, api/
│   ├── package.json              # vite + vitest + svelte-check
│   └── vite.config.ts
├── static/
│   ├── dist/                     # `npm run build` output (served by Flask)
│   ├── logos/                    # 20 custom SVG channel logos
│   ├── icons/                    # PWA icons
│   ├── manifest.json
│   └── sw.js                     # Service worker
├── templates/                    # legacy Jinja templates (kept for reference)
├── tv-guide.service              # systemd unit (gunicorn -k gthread --threads 32)
├── tv-player.service
├── ersatztv/
│   └── docker-compose.yml
├── backups/                      # rolling config.json backups (last 20)
└── .github/workflows/ci.yml      # Frontend build + tests + Python compile-check
```

## Requirements

- Raspberry Pi 4 or 5 (tested on Pi 5)
- Pi OS Lite or Desktop
- Network access to Jellyfin and ErsatzTV
- Monitor/TV connected via HDMI (for the hardware player)
- Python 3.11+, gunicorn, Flask, feedparser, requests
- Node 20+ (only needed when building the frontend)

## Development

```bash
# Frontend tests + build
cd frontend
npm ci
npm test              # vitest unit suite (time + video utils)
npm run build         # outputs to ../static/dist/

# Backend syntax check
python3 -m compileall tv_guide tv_player.py

# Restart after backend changes
sudo systemctl restart tv-guide
```

CI (`.github/workflows/ci.yml`) runs frontend `npm test` + `npm run build` and `python -m compileall` on every push and PR.
