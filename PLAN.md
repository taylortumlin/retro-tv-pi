# Pi TV Channel Service - Project Plan

## Goal
Turn a Raspberry Pi into a "TV channel" display device that streams media from Jellyfin like old-school linear TV - with multiple themed channels, scheduling, and continuous playback.

## Current Setup
- **This Pi**: Pi OS Lite + CasaOS (Docker) + qBittorrent + dedicated storage
- **Jellyfin**: Running on separate Proxmox server
- **Requirement**: Don't rebuild the Pi if possible

---

## Architecture Decision: Build vs Use Existing

### Option A: ErsatzTV (Recommended)
**What it is**: Mature open-source tool that creates IPTV channels from your media library (Jellyfin, Plex, Emby supported).

**Features**:
- Multiple channels with themes (Movies, Comedy, Action, etc.)
- Full scheduling (TV Guide/EPG)
- Filler content (bumpers, commercials, station IDs)
- Channel logos, guide data
- Outputs standard IPTV/M3U streams any player can consume

**Architecture with your setup**:
```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Jellyfin       │────▶│   ErsatzTV      │────▶│  Raspberry Pi   │
│  (Proxmox)      │     │  (Proxmox LXC)  │     │  (Display)      │
│                 │     │  Channel Gen    │     │  mpv/VLC player │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

**Pros**:
- Battle-tested, active development
- Web UI for channel management
- No coding required
- Full EPG support
- Pi stays lightweight (just a player)

**Cons**:
- Another service on Proxmox
- Learning curve for channel setup
- Less custom control

---

### Option B: dizqueTV
Similar to ErsatzTV but originally Plex-focused. Has Jellyfin support but ErsatzTV is generally better for Jellyfin-first setups.

---

### Option C: Build Custom Solution
**What we'd build**: Python service that talks to Jellyfin API, manages playlists, and streams via mpv.

**Architecture**:
```
┌─────────────────┐     ┌─────────────────────────────────┐
│  Jellyfin       │────▶│  Raspberry Pi                   │
│  (Proxmox)      │     │  ┌─────────────┐  ┌───────────┐│
│                 │     │  │ Python      │─▶│ mpv       ││
│                 │     │  │ Scheduler   │  │ player    ││
└─────────────────┘     │  └─────────────┘  └───────────┘│
                        └─────────────────────────────────┘
```

**Pros**:
- Full control
- Lightweight
- Fun project
- No additional Proxmox services

**Cons**:
- More work to build
- Need to implement: scheduling, EPG, channel switching, error handling
- Maintenance burden
- No web UI (unless we build one)

---

## Recommendation

**Go with ErsatzTV** for these reasons:
1. You want full TV simulation (multiple channels, scheduling) - that's complex to build
2. You have Proxmox with spare capacity
3. ErsatzTV has great Jellyfin integration
4. Pi stays simple - just displays the stream
5. Active community and development

**BUT** if you want a fun build project, we can create a simpler "single channel endless shuffle" system that runs entirely on the Pi.

---

## Implementation Plan (ErsatzTV Route)

### Phase 1: Proxmox Setup
- [ ] Create LXC container for ErsatzTV
- [ ] Install ErsatzTV via Docker or native
- [ ] Connect to Jellyfin, sync libraries
- [ ] Create initial channels

### Phase 2: Pi Display Client
- [ ] Install mpv with framebuffer support (no full desktop needed)
- [ ] Create systemd service for auto-start
- [ ] Configure IPTV stream connection
- [ ] Add channel switching capability (IR remote? keyboard? web interface?)

### Phase 3: Polish
- [ ] Boot splash/channel animation
- [ ] Channel guide overlay (optional)
- [ ] Auto-recovery on network issues
- [ ] Remote control setup

---

## Implementation Plan (Custom Build Route)

### Phase 1: Core Player
- [ ] Python + mpv integration
- [ ] Jellyfin API client
- [ ] Basic shuffle playback

### Phase 2: Channels & Scheduling
- [ ] Channel definitions (genre filters, playlists)
- [ ] Time-based scheduling
- [ ] Channel switching (IR/keyboard/API)

### Phase 3: Polish
- [ ] Web UI for management
- [ ] EPG generation
- [ ] Filler content support

---

## Pi Client Options (Either Route)

### Keep Pi OS Lite (No Desktop)
**Method**: mpv with DRM/framebuffer output
```bash
# Plays directly to display, no X11 needed
mpv --vo=drm --hwdec=v4l2m2m-copy <stream_url>
```
**Pros**: Lightweight, keeps CasaOS running, minimal changes
**Cons**: No graphical overlays without more work

### Add Minimal Desktop
**Method**: Install X11 + openbox + mpv
```bash
sudo apt install xorg openbox mpv
```
**Pros**: Easier to add overlays, web UI
**Cons**: More resources, but Pi can handle it

### Switch to LibreELEC/OSMC
**Method**: Dedicated Kodi-based OS with IPTV addon
**Pros**: Best TV interface, remote-friendly
**Cons**: Would need to rebuild Pi, lose CasaOS setup

---

## Questions to Resolve

1. **ErsatzTV or Custom?** (need your decision)
2. **How do you want to switch channels?** (IR remote, keyboard, phone app, web?)
3. **Do you want an on-screen guide?** (EPG overlay)
4. **Pi display method?** (Framebuffer vs minimal X11)

---

## Resources
- ErsatzTV: https://ersatztv.org/
- dizqueTV: https://github.com/vexorian/dizquetv
- Jellyfin API: https://api.jellyfin.org/
