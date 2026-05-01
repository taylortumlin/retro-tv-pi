# Implementation Guide

## Architecture
```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Jellyfin       │────▶│   ErsatzTV      │────▶│  Raspberry Pi   │
│  (Proxmox)      │     │  (Proxmox LXC)  │     │  TV Display     │
│  Media Server   │     │  :8409 Web UI   │     │  mpv + web ctrl │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

---

## Part 1: ErsatzTV on Proxmox

### Option A: LXC Container (Recommended)
```bash
# On Proxmox, create Debian 12 LXC
# 2GB RAM, 2 cores, 8GB disk minimum

# Inside the container:
apt update && apt install -y curl docker.io docker-compose

# Create docker-compose.yml
mkdir -p /opt/ersatztv && cd /opt/ersatztv
```

docker-compose.yml:
```yaml
version: "3"
services:
  ersatztv:
    image: jasongdove/ersatztv:latest
    container_name: ersatztv
    ports:
      - "8409:8409"
    volumes:
      - ./config:/root/.local/share/ersatztv
      - /path/to/media:/media:ro  # Mount your media or use Jellyfin
    environment:
      - TZ=America/New_York  # Your timezone
    restart: unless-stopped
```

### Option B: Docker on Existing System
If you have a Docker host already on Proxmox, just add the container there.

### Initial ErsatzTV Setup
1. Access web UI at `http://<proxmox-ip>:8409`
2. Add Media Source → Jellyfin
3. Enter Jellyfin URL and API key
4. Sync libraries
5. Create channels:
   - Movies 24/7
   - TV Shows Marathon
   - Genre-specific channels
6. Configure scheduling or use shuffle mode
7. Note the M3U playlist URL (Settings → Streaming)

---

## Part 2: Pi Display Client

### Install Dependencies (on Pi)
```bash
# mpv with hardware acceleration
sudo apt update
sudo apt install -y mpv python3 python3-pip python3-flask

# For keyboard input handling
sudo apt install -y python3-evdev
```

### Test Basic Playback
```bash
# Test with framebuffer (no desktop)
mpv --vo=drm --hwdec=v4l2m2m-copy "http://<ersatztv-ip>:8409/iptv/channel/1.ts"

# Or with X11 if you have a desktop
mpv --fullscreen "http://<ersatztv-ip>:8409/iptv/channel/1.ts"
```

### Pi Client Files
The active code lives at the repo root:
- `tv_guide/` - Flask web guide server (Blueprints package)
- `tv_player.py` - mpv hardware player with web control
- `tv-guide.service` / `tv-player.service` - systemd units
- `config.json` - channel + weather + news configuration
- `frontend/` - Svelte 5 SPA source (built into `static/dist/`)

---

## Part 3: Channel Switching

### Web Interface
- Runs on Pi port 5000
- Access from phone: `http://<pi-ip>:5000`
- Shows channel list, current playing, controls

### Keyboard Controls
- Number keys (1-9): Switch to channel
- Space: Pause/Play
- M: Mute
- Q: Quit

---

## Startup Flow

1. Pi boots
2. Systemd starts `tv-player.service`
3. Player connects to ErsatzTV stream
4. Web interface available for control
5. Keyboard input monitored for channel changes

---

## Network Requirements

| Service | Port | Purpose |
|---------|------|---------|
| Jellyfin | 8096 | Media streaming |
| ErsatzTV | 8409 | Channel generation + IPTV |
| Pi Web UI | 5000 | Channel control |

Ensure Pi can reach both Jellyfin and ErsatzTV on your network.
