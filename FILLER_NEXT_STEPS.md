# ErsatzTV Filler - Next Steps

## Current Status
- 3 custom bumper MP4s recorded in `filler/bumpers/` (local project dir)
- 102 torrents queued in qBittorrent downloading to `/mnt/x_drive/filler/`
- 7 items direct-downloading via `direct-download-filler.py` (running in background)
- Folder structure on x_drive: commercials, bumpers, psa, broadcasts, discovered

---

## Step 1: Copy Bumper Videos to Filler Directory

Copy the 3 recorded bumper MP4s to the filler storage where ErsatzTV can access them:

```bash
cp /mnt/a_drive/claudeprojects/pi-tv-channel/filler/bumpers/*.mp4 /mnt/x_drive/filler/bumpers/
```

Verify:
```bash
ls -lh /mnt/x_drive/filler/bumpers/*.mp4
```

You should see:
- `well-be-right-back.mp4` (~5 MB, 45s)
- `please-stand-by.mp4` (~7 MB, 45s)
- `up-next.mp4` (~7 MB, 45s)

---

## Step 2: Add Filler Libraries in ErsatzTV

Go to ErsatzTV at **http://192.168.1.72:8409** → **Media Sources** → **Local Libraries**

Create a local library for each filler folder. Each library should point to the corresponding directory:

| Library Name | Path | Content Type |
|---|---|---|
| Filler - Commercials | `/media/filler/commercials/` | Other Videos |
| Filler - Bumpers | `/media/filler/bumpers/` | Other Videos |
| Filler - PSA | `/media/filler/psa/` | Other Videos |
| Filler - Network Idents | `/media/filler/network-idents/` | Other Videos |
| Filler - Discovered | `/media/filler/discovered/` | Other Videos |
| Filler - Broadcasts | `/media/filler/broadcasts/` | Other Videos |

> **Note**: These paths are from ErsatzTV's perspective. If ErsatzTV runs in Docker on Proxmox, make sure `/media/filler/` or `/mnt/x_drive/filler/` is mounted inside the ErsatzTV container. Check your ErsatzTV docker-compose.yml volume mounts.

After creating each library, click the **Scan** button to index the files.

---

## Step 3: Create Smart Collections for Filler

Go to **Libraries** → **Smart Collections** and create collections that group filler by type:

| Collection Name | Query/Filter |
|---|---|
| All Commercials | Library: "Filler - Commercials" |
| All Bumpers | Library: "Filler - Bumpers" |
| All PSAs | Library: "Filler - PSA" |
| Pre-Roll Bumpers | Library: "Filler - Bumpers" AND title contains "up-next" |
| Post-Roll Bumpers | Library: "Filler - Bumpers" AND title contains "well-be-right-back" |
| Fallback Content | Library: "Filler - Bumpers" AND title contains "please-stand-by" |

---

## Step 4: Configure Filler Presets

Go to each channel's schedule settings. For each channel, configure filler:

### Pre-Roll (plays before each show)
- **Filler Kind**: Pre-Roll
- **Mode**: Count → 1 item
- **Collection**: Pre-Roll Bumpers (up-next)
- This plays the "Up Next / Your Lineup" bumper before each program

### Mid-Roll (plays between chapters/segments)
- **Filler Kind**: Mid-Roll
- **Mode**: Duration → 2-3 minutes
- **Collection**: All Commercials + All PSAs
- **Playback Order**: Shuffle
- Simulates a real commercial break with random vintage ads and PSAs

### Post-Roll (plays after each show)
- **Filler Kind**: Post-Roll
- **Mode**: Count → 1 item
- **Collection**: Post-Roll Bumpers (well-be-right-back)
- Shows "We'll Be Right Back" card after each program ends

### Tail (pads to schedule boundary)
- **Filler Kind**: Tail
- **Mode**: Pad to next 30-minute mark
- **Collection**: All Commercials + All Bumpers
- **Playback Order**: Shuffle
- Fills the gap between when a show ends and the next time slot

### Fallback (when nothing is scheduled)
- **Filler Kind**: Fallback
- **Mode**: Loop
- **Collection**: Fallback Content (please-stand-by)
- Shows the "Please Stand By" test pattern when there's a gap in the schedule

---

## Step 5: Apply Filler to All 20 Channels

Apply the filler configuration to each channel. You can do this per-channel in the schedule settings, or if all channels share the same filler setup, configure it once and apply to all.

Channels:
1. Crime & Justice
2. Prestige Drama
3. Comedy Central
4. Sci-Fi & Fantasy
5. Thriller & Mystery
6. Binge TV
7. Action Packed
8. Romance & Family
9. 9-1-1 24/7
10. Reality & Variety
11. Movies
12. Blue Bloods 24/7
13. Downton Abbey 24/7
14. Animated
15. British Telly
16. Workplace
17. Superheroes
18. Horror & Dark
19. Legal Eagles
20. Comfort TV

---

## Step 6: Verify ErsatzTV Container Has Access

If ErsatzTV runs in Docker, check that the filler directory is mounted:

```bash
# Check current ErsatzTV mounts
sudo docker inspect ersatztv --format '{{json .Mounts}}' | python3 -m json.tool

# If /mnt/x_drive/filler is NOT mounted, you'll need to recreate the container
# adding a volume like:
#   -v /mnt/x_drive/filler:/media/filler
```

This is the same fix we did for qBittorrent — ErsatzTV needs to see the files.

---

## Step 7 (Optional): Deploy ErsatzTV-Filler for Auto-Generated Content

The community [ErsatzTV-Filler](https://github.com/liam8888999/ErsatzTV-Filler) tool can auto-generate:
- Weather forecast cards
- News ticker filler
- Channel offline cards
- Animated logo bumpers

```bash
# Example Docker run (adjust paths)
docker run -d \
  --name ersatztv-filler \
  --restart unless-stopped \
  -v /mnt/x_drive/filler/generated:/output \
  -e TIMEZONE=America/New_York \
  ghcr.io/liam8888999/ersatztv-filler:latest
```

Check the GitHub repo for full configuration options and theme support.

---

## Step 8: Test and Tune

1. Pick one channel (e.g., channel 6 "Binge TV")
2. Watch it for 30-60 minutes
3. Check that:
   - Pre-roll bumper plays before each show
   - Commercial breaks appear between segments
   - Post-roll bumper plays after shows end
   - Gaps are filled with filler (no dead air)
   - Fallback plays if nothing is scheduled
4. Adjust timing:
   - If commercial breaks are too long, reduce mid-roll duration
   - If transitions feel abrupt, add more bumper variety
   - If the same clips repeat too often, wait for more downloads to complete

---

## Useful Commands

```bash
# Check torrent download progress
python3 /mnt/a_drive/claudeprojects/pi-tv-channel/filler/cleanup-filler.py

# Check direct download progress
tail -5 /tmp/claude-1000/-mnt-a-drive-claudeprojects-pi-tv-channel/tasks/bd3eb1f.output

# Re-record bumper videos (different duration)
/mnt/a_drive/claudeprojects/pi-tv-channel/filler/bumpers/record-bumpers.sh 60

# See what's downloaded so far
du -sh /mnt/x_drive/filler/*/

# Monitor qBittorrent
# http://localhost:8081
```

---

## File Locations

| What | Path |
|---|---|
| Bumper HTML sources | `/mnt/a_drive/claudeprojects/pi-tv-channel/filler/bumpers/*.html` |
| Bumper MP4 videos | `/mnt/a_drive/claudeprojects/pi-tv-channel/filler/bumpers/*.mp4` |
| Bumper recorder script | `/mnt/a_drive/claudeprojects/pi-tv-channel/filler/bumpers/record-bumpers.sh` |
| Torrent download script | `/mnt/a_drive/claudeprojects/pi-tv-channel/filler/download-filler.py` |
| Direct download script | `/mnt/a_drive/claudeprojects/pi-tv-channel/filler/direct-download-filler.py` |
| Cleanup script | `/mnt/a_drive/claudeprojects/pi-tv-channel/filler/cleanup-filler.py` |
| Filler storage (x_drive) | `/mnt/x_drive/filler/` (symlinked at `/media/filler/`) |
| ErsatzTV | `http://192.168.1.72:8409` |
| qBittorrent | `http://ttumlinpi:8081` |
