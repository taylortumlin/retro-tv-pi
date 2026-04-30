#!/usr/bin/env python3
"""
Direct download filler content from archive.org for items that don't have torrents.
Uses archive.org's download API to fetch video files directly.
"""

import os
import sys
import time
import requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# Items that failed torrent download - need direct download
ITEMS = {
    "commercials": {
        "save_path": "/media/filler/commercials/",
        "identifiers": [
            "USATVCommercialCollection",
            "commercialpack1",
            "80s-2000s-commercial-compilation",
            "a-bunch-of-retro-80s-commercials-1080p-60",
            "Vintage_Commercials_Advertisements_80s",
            "ctvc",
        ],
    },
    "bumpers": {
        "save_path": "/media/filler/bumpers/",
        "identifiers": [
            "nickelodeon-bumper-id-collection-from-the-80s-90s-720p",
        ],
    },
}

# Video/audio file extensions to download
VIDEO_EXTS = {".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm", ".mpg", ".mpeg", ".ogv", ".m4v"}

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "PiTV-Filler-Downloader/1.0"})


def get_file_list(identifier):
    """Get list of files in an archive.org item via metadata API."""
    url = f"https://archive.org/metadata/{identifier}/files"
    try:
        r = SESSION.get(url, timeout=30)
        r.raise_for_status()
        data = r.json()
        files = data.get("result", [])
        # Filter to video files only
        video_files = []
        for f in files:
            name = f.get("name", "")
            ext = os.path.splitext(name)[1].lower()
            if ext in VIDEO_EXTS:
                size = int(f.get("size", 0))
                video_files.append({"name": name, "size": size})
        return video_files
    except Exception as e:
        print(f"    Error fetching file list: {e}")
        return []


def download_file(identifier, filename, save_dir, existing_size=0):
    """Download a single file from archive.org with resume support.

    Writes to <name>.part and only renames on full completion, so a
    Ctrl+C mid-download leaves a `.part` file (resume target) rather
    than a partially-written final file that looks complete.
    """
    url = f"https://archive.org/download/{identifier}/{requests.utils.quote(filename)}"
    filepath = Path(save_dir) / identifier / filename

    # Path-traversal guard: filename comes from archive.org's metadata
    # (user-uploaded), so a "name": "../../etc/foo" must not escape the
    # per-identifier dir.
    base = (Path(save_dir) / identifier).resolve()
    try:
        resolved = filepath.resolve()
        resolved.relative_to(base)
    except (ValueError, RuntimeError):
        return "error: unsafe filename", 0

    filepath.parent.mkdir(parents=True, exist_ok=True)
    part = filepath.with_suffix(filepath.suffix + ".part")

    # Already fully downloaded.
    if filepath.exists():
        local_size = filepath.stat().st_size
        if existing_size > 0 and local_size >= existing_size:
            return "exists", local_size

    # Resume from .part if present.
    if part.exists():
        downloaded = part.stat().st_size
        headers = {"Range": f"bytes={downloaded}-"}
    else:
        downloaded = 0
        headers = {}

    try:
        with SESSION.get(url, headers=headers, stream=True, timeout=30) as r:
            if r.status_code == 416:
                # Server says the byte range is past EOF; the .part is
                # already complete.
                if part.exists():
                    part.rename(filepath)
                    downloaded = filepath.stat().st_size
                return "exists", downloaded
            r.raise_for_status()

            # Some CDNs ignore Range and return 200 with the full file
            # from offset 0. Append-mode would corrupt the .part with
            # duplicate header bytes; restart cleanly instead.
            if headers.get("Range") and r.status_code == 200:
                downloaded = 0
                mode = "wb"
            elif headers.get("Range") and r.status_code == 206:
                mode = "ab"
            else:
                mode = "wb"

            with open(part, mode) as f:
                for chunk in r.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)

        # Atomic promote: only on successful completion.
        part.rename(filepath)
        return "ok", downloaded
    except Exception as e:
        return f"error: {e}", downloaded


def format_size(bytes_val):
    if bytes_val >= 1024 ** 3:
        return f"{bytes_val / (1024**3):.1f} GB"
    elif bytes_val >= 1024 ** 2:
        return f"{bytes_val / (1024**2):.0f} MB"
    elif bytes_val >= 1024:
        return f"{bytes_val / 1024:.0f} KB"
    return f"{bytes_val} B"


def main():
    print("=" * 60)
    print("  Archive.org Direct Downloader")
    print("  (For items without torrent support)")
    print("=" * 60)
    print()

    total_files = 0
    total_downloaded = 0
    total_skipped = 0
    total_errors = 0
    total_bytes = 0

    for category, info in ITEMS.items():
        save_path = info["save_path"]
        print(f"[*] Category: {category}")
        print(f"    Save path: {save_path}")
        print()

        for identifier in info["identifiers"]:
            print(f"  [{identifier}]")
            print(f"    Fetching file list...")

            files = get_file_list(identifier)
            if not files:
                print(f"    No video files found!")
                print()
                continue

            item_size = sum(f["size"] for f in files)
            print(f"    Found {len(files)} video files ({format_size(item_size)})")

            for i, f in enumerate(files, 1):
                name = f["name"]
                size = f["size"]
                prefix = f"    [{i}/{len(files)}]"

                print(f"{prefix} {name} ({format_size(size)})", end="", flush=True)

                status, dl_bytes = download_file(identifier, name, save_path, size)

                if status == "exists":
                    print(f" - already downloaded")
                    total_skipped += 1
                elif status == "ok":
                    print(f" - done")
                    total_downloaded += 1
                    total_bytes += dl_bytes
                else:
                    print(f" - {status}")
                    total_errors += 1

                total_files += 1

            print()

    print("=" * 60)
    print("  SUMMARY")
    print("=" * 60)
    print(f"  Files processed:  {total_files}")
    print(f"  Downloaded:       {total_downloaded} ({format_size(total_bytes)})")
    print(f"  Already existed:  {total_skipped}")
    print(f"  Errors:           {total_errors}")
    print()
    print("Done!")


if __name__ == "__main__":
    main()
