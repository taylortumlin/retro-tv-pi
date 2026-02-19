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
- **Prevue Guide mode** -- authentic 1993 Prevue Channel look with auto-scrolling grid, live video preview, and channel rotation
- **Weather & News view** -- WeatherStar 4000-style weather with 7-day forecast, hourly chart, and live news from AP/BBC/NPR
- **4 visual themes** -- Modern Dark, Prevue Classic, Comcast Blue, CRT Retro (with scanlines + flicker)
- **Favorites & Reminders** -- star channels, set show reminders with browser notifications
- **Channel surfing OSD** -- press number keys for TV-style on-screen channel display
- **Category filtering** -- filter the guide by genre (Action, Comedy, Drama, etc.)
- **Custom SVG logos** for all 20 channels
- **Live streaming** -- watch any channel directly in the browser via HLS/MPEG-TS
- **Scrolling news ticker** in Prevue and Watch modes
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

### 3. Setup Pi Client

```bash
cd pi-client
chmod +x setup.sh
./setup.sh
```

### 4. Configure & Run

```bash
# Edit config with your ErsatzTV IP
nano ~/pi-tv/config.json

# Start the guide server
python3 ~/pi-tv/tv_guide.py

# Start the player (for TV output via mpv)
python3 ~/pi-tv/tv_player.py

# Enable auto-start
sudo systemctl enable tv-player tv-guide
sudo systemctl start tv-player tv-guide
```

## Controls

### Web Guide (port 5001)
Open `http://<pi-ip>:5001` on any device

- **G** -- Guide view
- **P** -- Prevue mode
- **W** -- Weather & News
- **U** -- Up Next
- **T** -- Tonight
- **Shift+T** -- Cycle themes
- **0-9** -- Channel surfing OSD
- **Escape** -- Exit current view

### Player (port 5000)
- **1-9** -- Switch channels
- **Space** -- Pause/Play
- **M** -- Mute
- **Q** -- Quit

## Files

```
pi-tv-channel/
├── README.md
├── PLAN.md                    # Architecture decisions
├── IMPLEMENTATION.md          # Setup guide
├── CHANNEL_SETUP.md           # Smart collection details
├── ersatztv/
│   └── docker-compose.yml
└── pi-client/
    ├── tv_guide.py            # Flask web guide server
    ├── tv_player.py           # mpv player controller
    ├── config.json            # Channels, weather, news config
    ├── setup.sh               # Pi installer script
    ├── tv-guide.service       # systemd for guide
    ├── tv-player.service      # systemd for player
    ├── templates/
    │   └── guide.html         # Single-page guide app (~2500 lines)
    └── static/
        └── logos/             # 20 custom SVG channel logos
            ├── 1.svg ... 20.svg
```

## Requirements

- Raspberry Pi 4 or 5 (tested on Pi 5)
- Pi OS Lite or Desktop
- Network access to Jellyfin and ErsatzTV
- Monitor/TV connected via HDMI
- Python 3 + Flask, feedparser, requests
