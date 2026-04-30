"""News headline fetcher (RSS via feedparser). Behavior identical to the monolith."""

from __future__ import annotations

import re
import time

import feedparser

from . import _state


def fetch_news() -> None:
    ticker_cfg = _state.CONFIG.get("ticker", {})
    news_cfg = ticker_cfg.get("news", {})
    if not news_cfg.get("show_headlines", False):
        return
    feeds = news_cfg.get("feeds", [])
    headlines = []
    seen_titles = set()
    for feed_info in feeds:
        try:
            parsed = feedparser.parse(feed_info["url"])
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
    _state.news_cache["data"] = headlines
    _state.news_cache["last_fetch"] = time.time()
    print(f"News updated: {len(_state.news_cache['data'])} headlines")
