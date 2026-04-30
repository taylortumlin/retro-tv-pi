"""Public-facing JSON API endpoints (excluding /api/player/*)."""

from __future__ import annotations

import time
from datetime import datetime

from flask import Blueprint, jsonify

from . import _state
from .epg import fetch_epg, get_visible_channels, get_filtered_epg
from .weather import fetch_weather
from .news import fetch_news

bp = Blueprint("api", __name__)


@bp.route("/epg")
def api_epg():
    if not _state.epg_cache["channels"]:
        fetch_epg()
    return jsonify(get_filtered_epg())


@bp.route("/epg/refresh", methods=["POST"])
def api_epg_refresh():
    fetch_epg()
    return jsonify({"status": "ok", "last_update": _state.epg_cache["last_update"]})


@bp.route("/now")
def api_now():
    if not _state.epg_cache["channels"]:
        fetch_epg()
    now_ts = datetime.now().timestamp()
    visible = get_visible_channels()
    result = []
    for ch in visible:
        current = next(
            (p for p in _state.epg_cache["programmes"]
             if p["channel_id"] == ch["id"]
             and p["start_ts"] <= now_ts < p["stop_ts"]),
            None
        )
        result.append({"channel": ch, "now_playing": current})
    return jsonify(result)


@bp.route("/weather")
def api_weather():
    if not _state.weather_cache["data"]:
        fetch_weather()
    return jsonify({
        "current": _state.weather_cache.get("data"),
        "hourly": _state.weather_cache.get("hourly", []),
        "daily": _state.weather_cache.get("daily", []),
        "forecast_days": _state.CONFIG.get("weather", {}).get("forecast_days", 5),
    })


@bp.route("/ticker")
def api_ticker():
    if not _state.epg_cache["channels"]:
        fetch_epg()
    ticker_cfg = _state.CONFIG.get("ticker", {})
    now_ts = datetime.now().timestamp()
    now_playing = []
    if ticker_cfg.get("show_now_playing", True):
        visible = get_visible_channels()
        for ch in visible:
            current = next(
                (p for p in _state.epg_cache["programmes"]
                 if p["channel_id"] == ch["id"]
                 and p["start_ts"] <= now_ts < p["stop_ts"]),
                None
            )
            if current:
                now_playing.append({
                    "channel_number": ch["number"],
                    "channel_name": ch["name"],
                    "title": current["title"],
                    "episode": current.get("episode", ""),
                })
    max_headlines = ticker_cfg.get("news", {}).get("max_headlines", 10)
    ticker_news = (_state.news_cache.get("data") or [])[:max_headlines]
    return jsonify({
        "weather": _state.weather_cache.get("data"),
        "now_playing": now_playing,
        "messages": ticker_cfg.get("messages", []),
        "speed": ticker_cfg.get("speed", 60),
        "news": ticker_news,
    })


@bp.route("/news")
def api_news():
    if not _state.news_cache["data"] or time.time() - _state.news_cache["last_fetch"] > 600:
        fetch_news()
    return jsonify(_state.news_cache.get("data") or [])
