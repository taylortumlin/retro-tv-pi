"""EPG fetch + visibility filtering + background refresh loop."""

from __future__ import annotations

import time
import xml.etree.ElementTree as ET
from datetime import datetime
from threading import Thread

import requests

from . import _state
from ._xmltv import parse_xmltv_time
from .weather import fetch_weather
from .news import fetch_news


def fetch_epg() -> bool:
    try:
        url = _state.ERSATZTV_URL + "/iptv/xmltv.xml"
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        root = ET.fromstring(resp.content)
        channels = []
        for ch in root.findall("channel"):
            names = [n.text for n in ch.findall("display-name")]
            icon = ch.find("icon")
            categories = [c.text for c in ch.findall("category")]
            channels.append({
                "id": ch.get("id"),
                "number": names[1] if len(names) > 1 else "0",
                "name": names[2] if len(names) > 2 else names[0],
                "logo": icon.get("src") if icon is not None else None,
                "categories": categories,
            })
        programmes = []
        for prog in root.findall("programme"):
            title_el = prog.find("title")
            sub_el = prog.find("sub-title")
            icon_el = prog.find("icon")
            ep_el = prog.find('.//episode-num[@system="onscreen"]')
            rating_el = prog.find(".//rating/value")
            categories = [c.text for c in prog.findall("category")]
            still = None
            for img in prog.findall("image"):
                if img.get("type") == "still":
                    still = img.text
                    break
            start = parse_xmltv_time(prog.get("start"))
            stop = parse_xmltv_time(prog.get("stop"))
            programmes.append({
                "channel_id": prog.get("channel"),
                "title": title_el.text if title_el is not None else "Unknown",
                "subtitle": sub_el.text if sub_el is not None else "",
                "start": start.isoformat(),
                "stop": stop.isoformat(),
                "start_ts": start.timestamp(),
                "stop_ts": stop.timestamp(),
                "duration_min": int((stop - start).total_seconds() / 60),
                "episode": ep_el.text if ep_el is not None else "",
                "rating": rating_el.text if rating_el is not None else "",
                "categories": categories,
                "poster": icon_el.get("src") if icon_el is not None else None,
                "thumbnail": still,
            })
        channels.sort(key=lambda c: int(c["number"]) if c["number"].isdigit() else 999)
        with _state.cache_lock:
            _state.epg_cache["channels"] = channels
            _state.epg_cache["programmes"] = programmes
            _state.epg_cache["last_update"] = datetime.now().isoformat()
        auto_import_channels()
        return True
    except Exception as e:
        print(f"EPG fetch error: {e}")
        return False


def auto_import_channels() -> None:
    """If CONFIG has no channels, auto-populate from EPG data."""
    if _state.CONFIG.get("channels"):
        return
    if not _state.epg_cache["channels"]:
        return
    _state.CONFIG["channels"] = [
        {"number": int(ch["number"]) if ch["number"].isdigit() else 0,
         "name": ch["name"]}
        for ch in _state.epg_cache["channels"]
    ]
    try:
        # Local imports to avoid a circular dependency at module import time.
        from .config_io import backup_config, atomic_write_config
        backup_config()
        atomic_write_config(_state.CONFIG)
        print(f"Auto-imported {len(_state.CONFIG['channels'])} channels from EPG")
    except Exception as e:
        print(f"Auto-import save error: {e}")


def _config_channel_map():
    """Build a lookup map of str(number) -> config channel entry."""
    channels = _state.CONFIG.get("channels", [])
    if not channels:
        return None  # None = no filtering
    return {str(c["number"]): c for c in channels}


def get_visible_channels():
    """Return EPG channels filtered by config, with name overrides applied."""
    cmap = _config_channel_map()
    if cmap is None:
        return _state.epg_cache["channels"]
    visible = []
    for ch in _state.epg_cache["channels"]:
        cc = cmap.get(ch["number"])
        if cc is None:
            continue
        ch_copy = dict(ch)
        if cc.get("name"):
            ch_copy["name"] = cc["name"]
        visible.append(ch_copy)
    return visible


def get_filtered_epg():
    """Return _state.epg_cache filtered to only configured channels."""
    visible = get_visible_channels()
    if visible is _state.epg_cache["channels"]:
        return _state.epg_cache  # no filtering needed
    visible_ids = {ch["id"] for ch in visible}
    programmes = [p for p in _state.epg_cache["programmes"]
                  if p["channel_id"] in visible_ids]
    return {
        "channels": visible,
        "programmes": programmes,
        "last_update": _state.epg_cache.get("last_update"),
    }


def epg_refresh_loop() -> None:
    while True:
        fetch_epg()
        fetch_weather()
        fetch_news()
        time.sleep(300)


def start_background_refresh() -> None:
    Thread(target=epg_refresh_loop, daemon=True).start()
