# Channel Setup Guide

## Smart Collections (DONE - Created via API)

| ID | Name | Query |
|----|------|-------|
| 1 | Crime & Justice | genre:Crime OR genre:Thriller |
| 2 | Prestige Drama | (genre:Drama OR genre:Thriller) AND NOT genre:Comedy AND NOT genre:Crime |
| 3 | Comedy Central | genre:Comedy OR genre:Animation |
| 4 | Sci-Fi & Fantasy | genre:"Science Fiction" OR genre:Fantasy OR genre:Adventure |
| 5 | Thriller & Mystery | genre:Mystery OR genre:Suspense |
| 6 | All Shows Shuffle | type:show |

---

## Step 1: Create Channels (UI)

You already have channels 1 and 2. Create the remaining:

Go to **Channels** → **Add Channel** for each:

| Number | Name | FFmpeg Profile | Streaming Mode |
|--------|------|----------------|----------------|
| 1 | Crime & Justice | 1920x1080 x264 aac | MPEG-TS |
| 2 | Prestige Drama | 1920x1080 x264 aac | MPEG-TS |
| 3 | Comedy Central | 1920x1080 x264 aac | MPEG-TS |
| 4 | Sci-Fi & Fantasy | 1920x1080 x264 aac | MPEG-TS |
| 5 | Thriller & Mystery | 1920x1080 x264 aac | MPEG-TS |
| 6 | Binge TV | 1920x1080 x264 aac | MPEG-TS |

You can rename your existing channels 1 & 2 to match, or keep them as-is.

---

## Step 2: Create Schedules (UI)

For each channel, go to **Scheduling** → **Schedules** → **Add Schedule**:

### Simple Shuffle Schedule (for all channels):
1. Name: "[Channel Name] Schedule"
2. Add Schedule Item:
   - Type: **Smart Collection**
   - Smart Collection: Pick the matching collection
   - Playback Order: **Shuffle**
3. Save

Repeat for each channel.

---

## Step 3: Create Playouts (UI)

Go to **Scheduling** → **Playouts** → **Add Playout** for each:

| Channel | Schedule |
|---------|----------|
| Crime & Justice | Crime & Justice Schedule |
| Prestige Drama | Prestige Drama Schedule |
| Comedy Central | Comedy Central Schedule |
| Sci-Fi & Fantasy | Sci-Fi & Fantasy Schedule |
| Thriller & Mystery | Thriller & Mystery Schedule |
| Binge TV | All Shows Schedule |

---

## EPG Metadata - Getting Show Details in Guide

### In ErsatzTV:

1. **Settings** (gear icon bottom-left) → **General**
   - Ensure "Use ErsatzTV as the EPG source" is checked

2. **Channel Settings** (click each channel → edit):
   - **Categories**: Set genre (e.g., "Crime" for Crime channel)
   - **Logo**: Upload or set URL for channel logo
   - **Preferred Language**: Set to English

3. **XMLTV/EPG URL** for Jellyfin:
   ```
   http://192.168.1.72:8409/iptv/xmltv.xml
   ```

### In Jellyfin (TV Guide setup):

1. **Dashboard** → **Live TV**
2. Under **TV Sources**:
   - Add Tuner → M3U Tuner
   - URL: `http://192.168.1.72:8409/iptv/playlist.m3u`
3. Under **TV Guide Data Providers**:
   - Add → XMLTV
   - URL: `http://192.168.1.72:8409/iptv/xmltv.xml`
4. Click **Save**
5. Go to **Guide Data** → **Map Channels**
   - Map each ErsatzTV channel to the correct guide data

### What the EPG shows:
- **Show name** and **episode title**
- **Description/synopsis** (pulled from Jellyfin metadata)
- **Episode number** (S01E01 format)
- **Air date**
- **Genre tags**
- **Channel logos** (if configured)

### Improving EPG Detail:
- ErsatzTV pulls metadata from Jellyfin, so the better your Jellyfin metadata, the better the EPG
- Make sure Jellyfin has good metadata (TheTVDB/TheMovieDb scrapers enabled)
- In ErsatzTV, re-sync libraries after Jellyfin metadata changes:
  **Media Sources** → Click sync icon on Jellyfin source

---

## Stream URLs

| Channel | URL |
|---------|-----|
| All channels | http://192.168.1.72:8409/iptv/playlist.m3u |
| EPG/Guide | http://192.168.1.72:8409/iptv/xmltv.xml |
| Channel 1 | http://192.168.1.72:8409/iptv/channel/1.ts |
| Channel 2 | http://192.168.1.72:8409/iptv/channel/2.ts |
| Channel 3 | http://192.168.1.72:8409/iptv/channel/3.ts |
| Channel 4 | http://192.168.1.72:8409/iptv/channel/4.ts |
| Channel 5 | http://192.168.1.72:8409/iptv/channel/5.ts |
| Channel 6 | http://192.168.1.72:8409/iptv/channel/6.ts |
