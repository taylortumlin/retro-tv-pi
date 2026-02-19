#!/usr/bin/env python3
"""
Clean up filler torrents that are stuck in error state.
Removes torrents that failed to download (404, missing torrent, etc.)
"""

import os
import qbittorrentapi

QB_HOST = os.environ.get("QB_HOST", "localhost")
QB_PORT = int(os.environ.get("QB_PORT", "8081"))
QB_USER = os.environ.get("QB_USER", "admin")
QB_PASS = os.environ.get("QB_PASS", "changeme")

def main():
    print("[*] Connecting to qBittorrent...")
    qb = qbittorrentapi.Client(host=QB_HOST, port=QB_PORT, username=QB_USER, password=QB_PASS)
    qb.auth_log_in()
    print(f"[OK] Connected to qBittorrent v{qb.app.version}")
    print()

    torrents = qb.torrents_info()
    filler = [t for t in torrents if t.category.startswith("filler-")]

    error_torrents = [t for t in filler if t.state in ("error", "missingFiles", "unknown")]
    stalled = [t for t in filler if t.state == "stalledDL" and t.downloaded == 0 and t.num_seeds == 0]
    downloading = [t for t in filler if t.state in ("downloading", "queuedDL", "stalledDL") and t.state not in ("error",)]
    paused = [t for t in filler if t.state in ("pausedDL", "stoppedDL")]
    completed = [t for t in filler if t.state in ("uploading", "stalledUP", "pausedUP", "stoppedUP")]

    print(f"  Total filler torrents: {len(filler)}")
    print(f"  Downloading/queued:    {len(downloading)}")
    print(f"  Completed:             {len(completed)}")
    print(f"  Paused:                {len(paused)}")
    print(f"  Error state:           {len(error_torrents)}")
    print(f"  Stalled (0 seeds):     {len(stalled)}")
    print()

    if error_torrents:
        print(f"[*] Removing {len(error_torrents)} error-state torrents:")
        for t in error_torrents:
            size_mb = t.size / (1024 * 1024)
            print(f"    REMOVE: [{t.category}] {t.name[:70]} ({size_mb:.0f} MB) - {t.state}")
            t.delete(delete_files=True)
        print(f"    Removed {len(error_torrents)} broken torrents.")
    else:
        print("[OK] No error-state torrents found.")

    print()

    # Show what's still active
    active = [t for t in filler if t.state not in ("error", "missingFiles", "unknown")]
    if active:
        print(f"[*] Remaining filler torrents ({len(active)}):")
        by_cat = {}
        for t in active:
            by_cat.setdefault(t.category, []).append(t)

        total_size = 0
        total_done = 0
        for cat in sorted(by_cat):
            items = by_cat[cat]
            cat_size = sum(t.size for t in items)
            cat_done = sum(t.downloaded for t in items)
            total_size += cat_size
            total_done += cat_done
            print(f"\n  {cat} ({len(items)} torrents, {cat_size/(1024**3):.1f} GB):")
            for t in sorted(items, key=lambda x: x.name):
                size_mb = t.size / (1024 * 1024)
                pct = (t.progress * 100)
                print(f"    {t.state:12s} {pct:5.1f}%  {t.name[:65]} ({size_mb:.0f} MB)")

        print(f"\n  Total: {total_size/(1024**3):.1f} GB queued, {total_done/(1024**3):.1f} GB downloaded")

    print()
    print("Done!")


if __name__ == "__main__":
    main()
