# Claude Code Prompt: ErsatzTV Filler Download via qBittorrent

## TASK
Write a Python script that downloads ErsatzTV filler content (retro TV commercials, bumpers, PSAs, network idents) from archive.org via torrent and adds them to my qBittorrent instance. Each archive.org item has a torrent file available at:
`https://archive.org/download/{IDENTIFIER}/{IDENTIFIER}_archive.torrent`

## QBITTORRENT ACCESS
- **Host**: Set via `QB_HOST` env var (default: `localhost`)
- **Port**: Set via `QB_PORT` env var (default: `8081`)
- **Username**: Set via `QB_USER` env var (default: `admin`)
- **Password**: Set via `QB_PASS` env var
- **API Docs**: qBittorrent Web API v2 — auth via POST `/api/v2/auth/login`, add torrents via POST `/api/v2/torrents/add`

## REQUIREMENTS

### 1. Use the `qbittorrent-api` Python library
```
pip install qbittorrent-api
```

### 2. Archive.org Item Identifiers to Download
Organize downloads into categories using qBittorrent categories and save paths:

**COMMERCIALS** (save to `/media/filler/commercials/`):
- `USATVCommercialCollection` — American TV Commercials 1960s-2000s (HUGE, hours of content)
- `commercialpack1` — Late 80s/Early 90s Commercials & Bumpers
- `80s-2000s-commercial-compilation` — 80s/90s/2000s Commercial Compilation
- `a-bunch-of-retro-80s-commercials-1080p-60` — Retro 80s Commercials (1080p)
- `Vintage_Commercials_Advertisements_80s` — Vintage Saturday Morning Commercials
- `ctvc` — Classic Television Commercials
- `classic_tv_commercials` — Classic TV Commercials

**NETWORK BUMPERS & IDENTS** (save to `/media/filler/bumpers/`):
- `nickelodeon-bumper-id-collection-from-the-80s-90s-720p` — Nickelodeon Bumper/ID Collection 80s/90s (720p)
- `cartoon-network-adult-swim-bumper-compilation` — Cartoon Network & Adult Swim Bumpers 2010s
- `yt-CNArchive` — Cartoon Network Archive (promos, bumpers, idents, Toonami)
- `yt-UCq3nKu5wqXi0kXYSdjdRjpg` — A Nostalgic Experience (CN, Nick, Boomerang bumpers, groovies, commercials)
- `ytvcom` — YTV Canada Commercials & Bumpers
- `spiketvcom` — Spike TV Commercials & Bumpers
- `citv-idents-29th-august-1998-to-august-1999` — CiTV Idents 1998-1999

**PSAs** (save to `/media/filler/psa/`):
- `TheMoreYouKnowWithJohnRatzenberger` — NBC "The More You Know" PSA (1990)
- `1991-jimmy-smits-anti-drug-public-service-announcement` — NBC "The More You Know" PSA (1991)
- `1993-helen-hunt-public-service-announcement` — NBC "The More You Know" PSA (1993)

**FULL BROADCAST RECORDINGS WITH COMMERCIALS** (save to `/media/filler/broadcasts/`):
- `b90_z666450` — Massive collection of full VHS broadcast recordings (ABC, NBC, CN, Nick, Adult Swim, Fox Kids, etc. from 80s-2000s — WITH all original commercials/bumpers intact)

### 3. Script Behavior
- Connect to qBittorrent and verify login
- Create categories: `filler-commercials`, `filler-bumpers`, `filler-psa`, `filler-broadcasts`
- For each identifier, construct the torrent URL: `https://archive.org/download/{ID}/{ID}_archive.torrent`
- Add each torrent to qBittorrent with the correct category and save path
- Print progress/status for each torrent added
- Handle errors gracefully (torrent might not exist for some items, connection issues, etc.)
- After all torrents are added, print a summary of what was queued
- Optionally: also search archive.org API for MORE items matching keywords like "TV bumpers", "retro commercials", "network ident", "public service announcement vintage" and add those torrents too

### 4. Additional Archive.org Search (Bonus)
Use the archive.org search API to find even MORE filler content:
```
https://archive.org/advancedsearch.php?q=subject:(tv+bumpers+commercials)&fl[]=identifier&rows=50&output=json
```

Search terms to try:
- `tv bumpers commercials 80s 90s`
- `network promos idents`
- `public service announcement vintage`
- `commercial break VHS recording`
- `saturday morning cartoons commercials`
- `station identification`
- `cartoon network bumpers`
- `nickelodeon bumpers`
- `adult swim bumpers`
- `toonami promos`
- `fox kids bumpers`

For each result, check if a torrent exists and add it to qBittorrent.

### 5. Output
The script should print:
- Connection status to qBittorrent
- Each torrent being added (identifier, category, save path)
- Any failures (torrent not available, already exists, etc.)
- Final summary: total torrents added per category

## EXAMPLE CODE STRUCTURE
```python
import qbittorrentapi
import requests

QB_HOST = os.environ.get("QB_HOST", "localhost")
QB_PORT = int(os.environ.get("QB_PORT", "8081"))
QB_USER = os.environ.get("QB_USER", "admin")
QB_PASS = os.environ.get("QB_PASS", "changeme")

FILLER_ITEMS = {
    "filler-commercials": {
        "save_path": "/media/filler/commercials/",
        "identifiers": [
            "USATVCommercialCollection",
            "commercialpack1",
            # ... etc
        ]
    },
    # ... etc
}

def get_torrent_url(identifier):
    return f"https://archive.org/download/{identifier}/{identifier}_archive.torrent"

def search_archive_org(query, rows=50):
    """Search archive.org for more filler content"""
    # Use advanced search API
    pass

def main():
    # Connect to qBittorrent
    # Create categories
    # Add all known torrents
    # Search for more and add those too
    # Print summary
    pass
```

## NOTES
- Some archive.org items may not have torrents available — handle gracefully
- The `b90_z666450` item is HUGE (100GB+) — consider adding it paused so I can selectively download files
- qBittorrent supports webseed from archive.org which means downloads work even without peers
- After downloads complete, these files will be imported into ErsatzTV as filler libraries
