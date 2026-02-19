# ErsatzTV Filler Content Master Plan
## Retro/Nostalgia Mixed Channel Setup

---

## 1. Folder Structure

Organize your filler content into these directories on your Proxmox server:

```
/media/filler/
├── bumpers/
│   ├── we-ll-be-right-back/
│   ├── please-stand-by/
│   ├── up-next/
│   └── channel-id/
├── commercials/
│   ├── 80s/
│   ├── 90s/
│   └── mixed/
├── psa/
│   ├── the-more-you-know/
│   ├── schoolhouse-rock/
│   └── general/
├── network-idents/
│   ├── nbc/
│   ├── abc/
│   ├── cbs/
│   ├── nickelodeon/
│   └── cartoon-network/
├── test-patterns/
│   └── color-bars/
└── fallback/
    └── static-loops/
```

---

## 2. Archive.org Filler Packs (Ready to Download)

### 🎬 Commercials

| Collection | Link | Era | Notes |
|---|---|---|---|
| American TV Commercials (1960s-2000s) | [archive.org/details/USATVCommercialCollection](https://archive.org/details/USATVCommercialCollection) | 60s-00s | HOURS of content, individual .avi files, huge variety |
| Late 80s/Early 90s Commercials & Bumpers | [archive.org/details/commercialpack1](https://archive.org/details/commercialpack1) | 80s-90s | Pre-cut from VHS tapes, includes bumpers |
| 80s/90s/2000s Commercial Compilation | [archive.org/details/80s-2000s-commercial-compilation](https://archive.org/details/80s-2000s-commercial-compilation) | 80s-00s | Curated favorites compilation |
| Retro 80s Commercials (1080p) | [archive.org/details/a-bunch-of-retro-80s-commercials-1080p-60](https://archive.org/details/a-bunch-of-retro-80s-commercials-1080p-60) | 80s | High quality 1080p upscale |
| Vintage Saturday Morning Commercials | [archive.org/details/Vintage_Commercials_Advertisements_80s](https://archive.org/details/Vintage_Commercials_Advertisements_80s) | 80s-90s | CBS/Garfield era, includes bumpers |
| Classic Television Commercials | [archive.org/details/ctvc](https://archive.org/details/ctvc) | Mixed | Large general collection |
| Classic TV Commercials | [archive.org/details/classic_tv_commercials](https://archive.org/details/classic_tv_commercials) | Mixed | Another broad collection |

### 📺 Network Bumpers & Idents

| Collection | Link | Network | Notes |
|---|---|---|---|
| Nickelodeon Bumper/ID Collection (80s/90s) | [archive.org/details/nickelodeon-bumper-id-collection-from-the-80s-90s-720p](https://archive.org/details/nickelodeon-bumper-id-collection-from-the-80s-90s-720p) | Nickelodeon | 720p, huge variety of classic Nick bumpers |
| YTV Canada Commercials & Bumpers | [archive.org/details/ytvcom](https://archive.org/details/ytvcom) | YTV | Canadian nostalgia, great bumpers |
| Spike TV Commercials & Bumpers | [archive.org/details/spiketvcom](https://archive.org/details/spiketvcom) | Spike TV | Good for action/variety channels |

### 📢 PSAs

| What to Search | Where | Notes |
|---|---|---|
| "The More You Know" | archive.org search: `the more you know PSA` | Individual clips available, 15-30 sec each |
| "I Learned It by Watching You" (1980s) | YouTube/archive.org | Iconic anti-drug PSA |
| "Crying Indian" Keep America Beautiful | YouTube/archive.org | Classic 1970s environmental PSA |
| Pee-wee Herman Crack PSA | YouTube/archive.org | Memorable, great for 80s/90s channels |
| General PSA collections | archive.org search: `public service announcement vintage` | Broad results |

### 🔍 Additional Archive.org Search Terms

Try these searches on archive.org for more hidden gems:
- `TV bumper compilation`
- `commercial break VHS`
- `network promo 90s`
- `station identification`
- `after these messages`
- `ABC Saturday morning`
- `FOX kids bumpers`

---

## 3. yt-dlp Download Script

Use this to batch-download filler content from YouTube playlists:

```bash
#!/bin/bash
# ErsatzTV Filler Downloader
# Run on your Proxmox server or media machine

FILLER_DIR="/media/filler"

# === 80s Commercials ===
# Replace URL with your chosen playlist
yt-dlp \
  --output "$FILLER_DIR/commercials/80s/%(title)s.%(ext)s" \
  --format "bestvideo[height<=1080]+bestaudio/best[height<=1080]" \
  --merge-output-format mp4 \
  --no-playlist \
  "PASTE_VIDEO_URL_HERE"

# === For playlists (batch download) ===
yt-dlp \
  --output "$FILLER_DIR/commercials/90s/%(title)s.%(ext)s" \
  --format "bestvideo[height<=1080]+bestaudio/best[height<=1080]" \
  --merge-output-format mp4 \
  --yes-playlist \
  "PASTE_PLAYLIST_URL_HERE"

# === For archive.org items ===
# Use wget or curl for archive.org bulk downloads
wget -r -np -nd -A "*.mp4,*.avi,*.mkv" \
  -P "$FILLER_DIR/commercials/mixed/" \
  "https://archive.org/download/ITEM_IDENTIFIER/"
```

---

## 4. Custom Bumper Templates (Included)

Three HTML bumper templates are included with this plan. Open them in a browser at 1920x1080 and screen-record with OBS for 15-60 seconds:

| Template | File | Best For |
|---|---|---|
| We'll Be Right Back | `bumper-well-be-right-back.html` | Mid-roll breaks between shows |
| Please Stand By | `bumper-please-stand-by.html` | Schedule gaps, late night, fallback |
| Up Next | `bumper-up-next.html` | Pre-roll before each show |

### How to Convert HTML Bumpers to Video

**Option A: OBS Studio (easiest)**
1. Open the HTML file in Chrome at full screen (1920x1080)
2. Record with OBS for 15-60 seconds
3. Export as MP4 (H.264)

**Option B: FFmpeg + Chrome headless (automated)**
```bash
# Take a screenshot and make a static bumper
google-chrome --headless --screenshot --window-size=1920,1080 bumper.html
ffmpeg -loop 1 -i screenshot.png -c:v libx264 -t 15 -pix_fmt yuv420p bumper.mp4
```

**Option C: DaVinci Resolve**
- Import the screenshot as a still
- Add VHS/CRT effects from the Effects Library
- Add ambient music or tone
- Export as 1080p MP4

### Customizing the Templates
Each template has `✏️ CUSTOMIZE` comments in the HTML. Edit:
- Channel name/logo
- Colors (CSS variables)
- Show names (for Up Next template)
- Time slots
- Fonts (swap Google Fonts imports)

---

## 5. ErsatzTV Filler Configuration

Based on the [official ErsatzTV filler documentation](https://ersatztv.org/docs/lists/filler/), here's the recommended setup:

### Filler Kinds to Configure

| Filler Kind | What to Put There | Collection |
|---|---|---|
| **Pre-roll** | Channel ID bumper + "Up Next" card | `/filler/bumpers/channel-id/` + `/filler/bumpers/up-next/` |
| **Mid-roll** | Commercials + PSAs (between chapters) | `/filler/commercials/` + `/filler/psa/` |
| **Post-roll** | "We'll Be Right Back" bumper | `/filler/bumpers/we-ll-be-right-back/` |
| **Tail** | Network idents, short filler | `/filler/network-idents/` |
| **Fallback** | Test pattern / "Please Stand By" loop | `/filler/test-patterns/` + `/filler/bumpers/please-stand-by/` |

### Recommended Filler Modes

- **Pre-roll**: Count mode → 1-2 items (quick channel ID + up next)
- **Mid-roll**: Duration mode → 2-3 minutes of commercials/PSAs
- **Post-roll**: Count mode → 1 item ("We'll Be Right Back")
- **Tail**: Pad mode → pad to next 30-min mark
- **Fallback**: Loop → "Please Stand By" test pattern

### Using YAML Playout (Advanced)

For more control with sequential schedules:

```yaml
playout:
  - epg_group: true
    advance: true
  - count: 1
    content: "CHANNEL_BUMPERS"
    filler_kind: "preroll"
  - count: 1
    content: "MAIN_SHOW"
  - count: 1
    content: "COMMERCIALS"
    filler_kind: "postroll"
  - epg_group: false
```

---

## 6. ErsatzTV-Filler Tool (Bonus)

There's a community project called **[ErsatzTV-Filler](https://github.com/liam8888999/ErsatzTV-Filler)** that auto-generates:

- **Weather forecast filler** — dynamic weather cards
- **News ticker filler** — scrolling headlines
- **Channel offline cards** — branded offline screens
- **Channel logo bumpers** — animated logo reveals
- **Vanity cards** — production company style cards

It supports custom themes: [ErsatzTV-Filler-Themes](https://github.com/liam8888999/ErsatzTV-Filler-Themes)

Discord community: https://discord.gg/x4Nk4sfgSg

This would run great on your Proxmox homelab as a Docker container alongside ErsatzTV.

---

## 7. Quick Start Checklist

- [ ] Create the filler folder structure on your media server
- [ ] Download 2-3 commercial packs from archive.org
- [ ] Download Nickelodeon bumper collection (best quality retro bumpers)
- [ ] Customize and record the 3 included HTML bumper templates
- [ ] Set up filler libraries in ErsatzTV (one per folder)
- [ ] Create smart collections for each filler kind
- [ ] Configure pre-roll, mid-roll, post-roll, tail, and fallback
- [ ] Deploy ErsatzTV-Filler Docker container for auto-generated content
- [ ] Test a channel with a full schedule + filler and tune timing

---

*Generated for ErsatzTV retro/nostalgia mixed channel setup*
