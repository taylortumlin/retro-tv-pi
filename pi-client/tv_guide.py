#!/usr/bin/env python3
"""
Pi TV Guide - Classic cable TV guide experience.
Parses XMLTV from ErsatzTV and serves a responsive TV guide web dashboard
with remote control, pre-buffered Prevue mode, and Up Next/Tonight views.
"""

import json
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path
from threading import Thread
import time
import re

import requests
import feedparser
from flask import Flask, render_template, jsonify, request as flask_request, Response

CONFIG_PATH = Path(__file__).parent / "config.json"
with open(CONFIG_PATH) as f:
    CONFIG = json.load(f)

app = Flask(__name__, template_folder=str(Path(__file__).parent / "templates"))
epg_cache = {"channels": [], "programmes": [], "last_update": None}

ERSATZTV_URL = CONFIG["ersatztv_url"].rstrip("/")
PLAYER_URL = CONFIG.get("player_url", "http://localhost:5000").rstrip("/")

# ====== Weather (Open-Meteo) ======
WMO_CODES = {
    0: "Clear", 1: "Mainly Clear", 2: "Partly Cloudy", 3: "Overcast",
    45: "Fog", 48: "Rime Fog",
    51: "Light Drizzle", 53: "Drizzle", 55: "Heavy Drizzle",
    56: "Freezing Drizzle", 57: "Heavy Freezing Drizzle",
    61: "Light Rain", 63: "Rain", 65: "Heavy Rain",
    66: "Freezing Rain", 67: "Heavy Freezing Rain",
    71: "Light Snow", 73: "Snow", 75: "Heavy Snow", 77: "Snow Grains",
    80: "Light Showers", 81: "Showers", 82: "Heavy Showers",
    85: "Light Snow Showers", 86: "Heavy Snow Showers",
    95: "Thunderstorm", 96: "Thunderstorm w/ Hail", 99: "Heavy Thunderstorm w/ Hail",
}

weather_cache = {"data": None, "hourly": None, "daily": None, "last_fetch": 0}
news_cache = {"data": None, "last_fetch": 0}


def parse_xmltv_time(s):
    s = s.strip()
    match = re.match(r"(\d{14})\s*([+-]\d{4})", s)
    if match:
        dt_str, tz_str = match.groups()
        dt = datetime.strptime(dt_str, "%Y%m%d%H%M%S")
        tz_hours = int(tz_str[:3])
        tz_mins = int(tz_str[0] + tz_str[3:])
        tz = timezone(timedelta(hours=tz_hours, minutes=tz_mins))
        return dt.replace(tzinfo=tz)
    return datetime.strptime(s[:14], "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc)


def fetch_weather():
    ticker_cfg = CONFIG.get("ticker", {})
    weather_cfg = ticker_cfg.get("weather", {})
    lat = weather_cfg.get("latitude", 33.749)
    lon = weather_cfg.get("longitude", -84.388)
    unit = weather_cfg.get("temperature_unit", "fahrenheit")
    location = weather_cfg.get("location_name", "Atlanta")
    forecast_days = ticker_cfg.get("forecast_days", 7)
    try:
        url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}"
            f"&current=temperature_2m,apparent_temperature,weather_code,wind_speed_10m,relative_humidity_2m,uv_index"
            f"&hourly=temperature_2m,weather_code,precipitation_probability"
            f"&daily=temperature_2m_max,temperature_2m_min,weather_code,precipitation_probability_max,uv_index_max"
            f"&temperature_unit={unit}"
            f"&wind_speed_unit=mph"
            f"&forecast_days={forecast_days}&timezone=auto"
        )
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        d = data.get("current", {})
        code = d.get("weather_code", 0)
        weather_cache["data"] = {
            "temperature": d.get("temperature_2m"),
            "feels_like": d.get("apparent_temperature"),
            "condition": WMO_CODES.get(code, "Unknown"),
            "weather_code": code,
            "wind_speed": d.get("wind_speed_10m"),
            "humidity": d.get("relative_humidity_2m"),
            "uv_index": d.get("uv_index"),
            "unit": "F" if unit == "fahrenheit" else "C",
            "location": location,
        }
        # Hourly forecast (24 hours)
        hourly_raw = data.get("hourly", {})
        hourly = []
        h_times = hourly_raw.get("time", [])
        h_temps = hourly_raw.get("temperature_2m", [])
        h_codes = hourly_raw.get("weather_code", [])
        h_precip = hourly_raw.get("precipitation_probability", [])
        for i in range(min(24, len(h_times))):
            hourly.append({
                "time": h_times[i] if i < len(h_times) else None,
                "temperature": h_temps[i] if i < len(h_temps) else None,
                "weather_code": h_codes[i] if i < len(h_codes) else 0,
                "condition": WMO_CODES.get(h_codes[i] if i < len(h_codes) else 0, "Unknown"),
                "precip_probability": h_precip[i] if i < len(h_precip) else 0,
            })
        weather_cache["hourly"] = hourly
        # Daily forecast
        daily_raw = data.get("daily", {})
        daily = []
        d_times = daily_raw.get("time", [])
        d_max = daily_raw.get("temperature_2m_max", [])
        d_min = daily_raw.get("temperature_2m_min", [])
        d_codes = daily_raw.get("weather_code", [])
        d_precip = daily_raw.get("precipitation_probability_max", [])
        d_uv = daily_raw.get("uv_index_max", [])
        for i in range(min(forecast_days, len(d_times))):
            daily.append({
                "date": d_times[i] if i < len(d_times) else None,
                "high": d_max[i] if i < len(d_max) else None,
                "low": d_min[i] if i < len(d_min) else None,
                "weather_code": d_codes[i] if i < len(d_codes) else 0,
                "condition": WMO_CODES.get(d_codes[i] if i < len(d_codes) else 0, "Unknown"),
                "precip_probability": d_precip[i] if i < len(d_precip) else 0,
                "uv_index": d_uv[i] if i < len(d_uv) else None,
            })
        weather_cache["daily"] = daily
        weather_cache["last_fetch"] = time.time()
        print(f"Weather updated: {weather_cache['data']['temperature']}°{weather_cache['data']['unit']} {weather_cache['data']['condition']}")
    except Exception as e:
        print(f"Weather fetch error: {e}")


def fetch_news():
    ticker_cfg = CONFIG.get("ticker", {})
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
                    # Strip HTML tags from summary
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
    news_cache["data"] = headlines
    news_cache["last_fetch"] = time.time()
    print(f"News updated: {len(news_cache['data'])} headlines")


def fetch_epg():
    try:
        url = ERSATZTV_URL + "/iptv/xmltv.xml"
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
        epg_cache["channels"] = channels
        epg_cache["programmes"] = programmes
        epg_cache["last_update"] = datetime.now().isoformat()
        return True
    except Exception as e:
        print(f"EPG fetch error: {e}")
        return False


def epg_refresh_loop():
    while True:
        fetch_epg()
        fetch_weather()
        fetch_news()
        time.sleep(300)


# ====== Routes ======

@app.route("/")
def index():
    default_theme = CONFIG.get("default_theme", "default")
    ticker_cfg = CONFIG.get("ticker", {})
    ws_music = ticker_cfg.get("weatherstar_music_url", "")
    ws_playlist = json.dumps(ticker_cfg.get("weatherstar_playlist", []))
    return render_template("guide.html", etv_url=ERSATZTV_URL,
                           default_theme=default_theme, ws_music_url=ws_music,
                           ws_playlist=ws_playlist)


@app.route("/sw.js")
def service_worker():
    return app.send_static_file("sw.js"), 200, {
        "Content-Type": "application/javascript",
        "Service-Worker-Allowed": "/",
    }


@app.route("/api/epg")
def api_epg():
    if not epg_cache["channels"]:
        fetch_epg()
    return jsonify(epg_cache)


@app.route("/api/epg/refresh", methods=["POST"])
def api_epg_refresh():
    fetch_epg()
    return jsonify({"status": "ok", "last_update": epg_cache["last_update"]})


@app.route("/api/now")
def api_now():
    if not epg_cache["channels"]:
        fetch_epg()
    now_ts = datetime.now().timestamp()
    result = []
    for ch in epg_cache["channels"]:
        current = next(
            (p for p in epg_cache["programmes"]
             if p["channel_id"] == ch["id"]
             and p["start_ts"] <= now_ts < p["stop_ts"]),
            None
        )
        result.append({"channel": ch, "now_playing": current})
    return jsonify(result)


@app.route("/api/weather")
def api_weather():
    if not weather_cache["data"]:
        fetch_weather()
    return jsonify({
        "current": weather_cache.get("data"),
        "hourly": weather_cache.get("hourly", []),
        "daily": weather_cache.get("daily", []),
    })


@app.route("/api/ticker")
def api_ticker():
    if not epg_cache["channels"]:
        fetch_epg()
    ticker_cfg = CONFIG.get("ticker", {})
    now_ts = datetime.now().timestamp()
    now_playing = []
    if ticker_cfg.get("show_now_playing", True):
        for ch in epg_cache["channels"]:
            current = next(
                (p for p in epg_cache["programmes"]
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
    ticker_news = (news_cache.get("data") or [])[:max_headlines]
    return jsonify({
        "weather": weather_cache.get("data"),
        "now_playing": now_playing,
        "messages": ticker_cfg.get("messages", []),
        "speed": ticker_cfg.get("speed", 60),
        "news": ticker_news,
    })


@app.route("/api/news")
def api_news():
    if not news_cache["data"] or time.time() - news_cache["last_fetch"] > 600:
        fetch_news()
    return jsonify(news_cache.get("data") or [])


# ====== Stream Proxy ======
# Proxies IPTV streams so mobile browsers avoid CORS issues with ErsatzTV.

@app.route("/stream/<int:ch_num>.ts")
def stream_proxy_ts(ch_num):
    url = f"{ERSATZTV_URL}/iptv/channel/{ch_num}.ts"
    try:
        resp = requests.get(url, stream=True, timeout=10)
        return Response(
            resp.iter_content(chunk_size=64 * 1024),
            content_type=resp.headers.get("Content-Type", "video/mp2t"),
            headers={"Cache-Control": "no-cache", "Access-Control-Allow-Origin": "*"},
        )
    except Exception as e:
        print(f"Stream proxy error ch{ch_num}: {e}")
        return f"Stream error: {e}", 502


@app.route("/stream/<int:ch_num>.m3u8")
def stream_proxy_hls(ch_num):
    url = f"{ERSATZTV_URL}/iptv/channel/{ch_num}.m3u8"
    try:
        resp = requests.get(url, timeout=10, allow_redirects=False)
        if resp.status_code in (301, 302):
            # ErsatzTV doesn't serve HLS; let client fall back to .ts
            return "HLS not available", 404
        return Response(
            resp.content,
            content_type=resp.headers.get("Content-Type", "application/vnd.apple.mpegurl"),
            headers={"Cache-Control": "no-cache", "Access-Control-Allow-Origin": "*"},
        )
    except Exception as e:
        return f"HLS error: {e}", 502


# ====== Player Proxy ======
# Proxies requests to the Pi's tv_player.py (port 5000) so the web UI
# can control the Pi's mpv player without CORS issues.

@app.route("/api/player/<path:endpoint>", methods=["GET", "POST"])
def proxy_player(endpoint):
    url = f"{PLAYER_URL}/api/{endpoint}"
    try:
        if flask_request.method == "POST":
            resp = requests.post(url, timeout=5)
        else:
            resp = requests.get(url, timeout=5)
        return jsonify(resp.json())
    except requests.ConnectionError:
        return jsonify({"error": "Player not running", "channel": "?", "channel_name": "Offline", "muted": False, "paused": False}), 503
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def main():
    print("Fetching EPG data...")
    fetch_epg()
    print("Fetching weather...")
    fetch_weather()
    print("Fetching news...")
    fetch_news()
    print(f"Loaded {len(epg_cache['channels'])} channels, {len(epg_cache['programmes'])} programmes")
    Thread(target=epg_refresh_loop, daemon=True).start()
    port = CONFIG.get("guide_port", 5001)
    print(f"TV Guide at http://0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port, threaded=True)


if __name__ == "__main__":
    main()
