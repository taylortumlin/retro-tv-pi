"""News headline fetcher (RSS via feedparser)."""

from __future__ import annotations

import re
import time
from typing import Any

import feedparser
import requests

from . import _state


def fetch_feed(url: str) -> Any:
    """Fetch an RSS URL with a hard timeout, then hand the bytes to feedparser.

    feedparser.parse(url) has no timeout knob; a slow/hung feed would block
    the entire epg_refresh_loop thread, freezing weather + EPG refreshes
    too. Doing the HTTP fetch ourselves bounds the wait at 10s.
    """
    try:
        r = requests.get(url, timeout=10, headers={"User-Agent": "PiTV/1.0"})
        r.raise_for_status()
        return feedparser.parse(r.content)
    except Exception as e:
        print(f"News feed fetch error {url}: {e}")
        return None


def fetch_news() -> None:
    ticker_cfg = _state.CONFIG.get("ticker", {})
    news_cfg = ticker_cfg.get("news", {})
    if not news_cfg.get("show_headlines", False):
        return
    feeds = news_cfg.get("feeds", [])
    headlines = []
    seen_titles = set()
    for feed_info in feeds:
        parsed = fetch_feed(feed_info["url"])
        if parsed is None:
            continue
        try:
            for entry in parsed.entries:
                title = entry.get("title", "").strip()
                if title and title not in seen_titles:
                    seen_titles.add(title)
                    summary = entry.get("summary", entry.get("description", "")).strip()
                    summary = re.sub(r"<[^>]+>", "", summary)
                    if len(summary) > 200:
                        summary = summary[:197] + "..."
                    published = ""
                    if hasattr(entry, "published_parsed") and entry.published_parsed:
                        try:
                            published = time.strftime("%I:%M %p", entry.published_parsed)
                        except Exception:
                            pass
                    headlines.append({
                        "source": feed_info["name"],
                        "title": title,
                        "summary": summary,
                        "published": published,
                    })
        except Exception as e:
            print(f"News feed error ({feed_info.get('name', '?')}): {e}")
    with _state.cache_lock:
        _state.news_cache["data"] = headlines
        _state.news_cache["last_fetch"] = time.time()
    print(f"News updated: {len(headlines)} headlines")
