#!/usr/bin/env python3
"""
ErsatzTV Filler Content Downloader
Downloads retro TV commercials, bumpers, PSAs, and network idents
from archive.org via torrent through qBittorrent.
"""

import os
import sys
import time
import requests
import qbittorrentapi

# ── qBittorrent connection ──────────────────────────────────────
QB_HOST = os.environ.get("QB_HOST", "localhost")
QB_PORT = int(os.environ.get("QB_PORT", "8081"))
QB_USER = os.environ.get("QB_USER", "admin")
QB_PASS = os.environ.get("QB_PASS", "changeme")

# ── Filler content organized by category ────────────────────────
FILLER_ITEMS = {
    "filler-commercials": {
        "save_path": "/media/filler/commercials/",
        "identifiers": [
            "USATVCommercialCollection",
            "commercialpack1",
            "80s-2000s-commercial-compilation",
            "a-bunch-of-retro-80s-commercials-1080p-60",
            "Vintage_Commercials_Advertisements_80s",
            "ctvc",
            "classic_tv_commercials",
        ],
    },
    "filler-bumpers": {
        "save_path": "/media/filler/bumpers/",
        "identifiers": [
            "nickelodeon-bumper-id-collection-from-the-80s-90s-720p",
            "cartoon-network-adult-swim-bumper-compilation",
            "yt-CNArchive",
            "yt-UCq3nKu5wqXi0kXYSdjdRjpg",
            "ytvcom",
            "spiketvcom",
            "citv-idents-29th-august-1998-to-august-1999",
        ],
    },
    "filler-psa": {
        "save_path": "/media/filler/psa/",
        "identifiers": [
            "TheMoreYouKnowWithJohnRatzenberger",
            "1991-jimmy-smits-anti-drug-public-service-announcement",
            "1993-helen-hunt-public-service-announcement",
        ],
    },
    "filler-broadcasts": {
        "save_path": "/media/filler/broadcasts/",
        "identifiers": [
            "b90_z666450",
        ],
    },
}

# Large items to add paused (100GB+)
PAUSED_ITEMS = {"b90_z666450"}

# ── Archive.org search terms for discovering more content ───────
SEARCH_QUERIES = [
    "tv bumpers commercials 80s 90s",
    "network promos idents",
    "public service announcement vintage",
    "commercial break VHS recording",
    "saturday morning cartoons commercials",
    "station identification",
    "cartoon network bumpers",
    "nickelodeon bumpers",
    "adult swim bumpers",
    "toonami promos",
    "fox kids bumpers",
]


def get_torrent_url(identifier):
    return f"https://archive.org/download/{identifier}/{identifier}_archive.torrent"


def check_torrent_exists(identifier):
    """Check if a torrent file exists on archive.org for this item."""
    url = get_torrent_url(identifier)
    try:
        r = requests.head(url, timeout=10, allow_redirects=True)
        return r.status_code == 200
    except requests.RequestException:
        return False


def search_archive_org(query, rows=25):
    """Search archive.org for items matching query, return identifiers."""
    url = "https://archive.org/advancedsearch.php"
    params = {
        "q": f"subject:({query}) AND mediatype:(movies)",
        "fl[]": "identifier",
        "rows": rows,
        "output": "json",
    }
    try:
        r = requests.get(url, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
        docs = data.get("response", {}).get("docs", [])
        return [d["identifier"] for d in docs if "identifier" in d]
    except Exception as e:
        print(f"    Search failed: {e}")
        return []


def main():
    print("=" * 60)
    print("  ErsatzTV Filler Content Downloader")
    print("=" * 60)
    print()

    # ── Connect to qBittorrent ──────────────────────────────────
    print(f"[*] Connecting to qBittorrent at {QB_HOST}:{QB_PORT}...")
    try:
        qb = qbittorrentapi.Client(
            host=QB_HOST,
            port=QB_PORT,
            username=QB_USER,
            password=QB_PASS,
        )
        qb.auth_log_in()
        print(f"[OK] Connected! qBittorrent v{qb.app.version}")
        print(f"     Web API v{qb.app.web_api_version}")
    except Exception as e:
        print(f"[FAIL] Could not connect: {e}")
        sys.exit(1)

    print()

    # ── Create categories ───────────────────────────────────────
    print("[*] Setting up categories...")
    for category, info in FILLER_ITEMS.items():
        try:
            qb.torrents_create_category(name=category, save_path=info["save_path"])
            print(f"    Created: {category} -> {info['save_path']}")
        except qbittorrentapi.Conflict409Error:
            print(f"    Exists:  {category} -> {info['save_path']}")
        except Exception as e:
            print(f"    Error creating {category}: {e}")

    # Also create a category for search discoveries
    try:
        qb.torrents_create_category(
            name="filler-discovered", save_path="/media/filler/discovered/"
        )
        print("    Created: filler-discovered -> /media/filler/discovered/")
    except qbittorrentapi.Conflict409Error:
        print("    Exists:  filler-discovered -> /media/filler/discovered/")

    print()

    # ── Add known torrents ──────────────────────────────────────
    stats = {"added": 0, "failed": 0, "skipped": 0}
    all_known_ids = set()

    for category, info in FILLER_ITEMS.items():
        print(f"[*] Category: {category}")
        print(f"    Save path: {info['save_path']}")
        print()

        for identifier in info["identifiers"]:
            all_known_ids.add(identifier)
            url = get_torrent_url(identifier)
            is_paused = identifier in PAUSED_ITEMS
            status_note = " (PAUSED - large item)" if is_paused else ""

            print(f"    Adding: {identifier}{status_note}")
            print(f"    URL:    {url}")

            try:
                result = qb.torrents_add(
                    urls=url,
                    category=category,
                    save_path=info["save_path"],
                    is_paused=is_paused,
                )
                if result == "Ok.":
                    print("    -> Queued!")
                    stats["added"] += 1
                elif result == "Fails.":
                    print("    -> Failed (torrent may not exist or already added)")
                    stats["failed"] += 1
                else:
                    print(f"    -> Response: {result}")
                    stats["added"] += 1
            except Exception as e:
                print(f"    -> Error: {e}")
                stats["failed"] += 1

            print()
            time.sleep(0.5)  # Be polite to archive.org

    # ── Search archive.org for more content ─────────────────────
    print("=" * 60)
    print("[*] Searching archive.org for additional filler content...")
    print("=" * 60)
    print()

    discovered = set()
    for query in SEARCH_QUERIES:
        print(f"  Searching: \"{query}\"")
        ids = search_archive_org(query, rows=15)
        new_ids = [i for i in ids if i not in all_known_ids and i not in discovered]
        if new_ids:
            print(f"    Found {len(new_ids)} new items")
            discovered.update(new_ids)
        else:
            print("    No new items")
        time.sleep(1)  # Rate limit

    print()

    if discovered:
        print(f"[*] Checking {len(discovered)} discovered items for torrents...")
        print()
        discover_added = 0

        for identifier in sorted(discovered):
            if check_torrent_exists(identifier):
                url = get_torrent_url(identifier)
                print(f"    Adding: {identifier}")
                try:
                    result = qb.torrents_add(
                        urls=url,
                        category="filler-discovered",
                        save_path="/media/filler/discovered/",
                    )
                    if result == "Ok.":
                        discover_added += 1
                        stats["added"] += 1
                        print("    -> Queued!")
                    else:
                        stats["skipped"] += 1
                except Exception as e:
                    print(f"    -> Error: {e}")
                    stats["failed"] += 1
                time.sleep(0.5)

        print()
        print(f"    Discovered items added: {discover_added}")
    else:
        print("[*] No additional items discovered")

    # ── Summary ─────────────────────────────────────────────────
    print()
    print("=" * 60)
    print("  SUMMARY")
    print("=" * 60)
    print(f"  Torrents added:   {stats['added']}")
    print(f"  Failed/missing:   {stats['failed']}")
    print(f"  Skipped:          {stats['skipped']}")
    print()

    # Show current qBittorrent status
    try:
        torrents = qb.torrents_info()
        filler_torrents = [t for t in torrents if t.category.startswith("filler-")]
        if filler_torrents:
            print("  Active filler downloads:")
            for t in filler_torrents:
                size_mb = t.size / (1024 * 1024)
                state = t.state
                print(f"    [{t.category}] {t.name[:60]} ({size_mb:.0f} MB) - {state}")
    except Exception:
        pass

    print()
    print("Done! Monitor progress at http://ttumlinpi:8081")


if __name__ == "__main__":
    main()
