#!/usr/bin/env python3
"""
Pi TV Guide - Classic cable TV guide experience.
Parses XMLTV from ErsatzTV and serves a responsive TV guide web dashboard
with remote control, pre-buffered Prevue mode, and Up Next/Tonight views.
"""

import json
import os
import secrets
import shutil
import subprocess
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from functools import wraps
from pathlib import Path
from threading import Thread
import time
import re

import requests
import feedparser
from flask import (Flask, render_template, jsonify, request as flask_request,
                   Response, session, redirect)

CONFIG_PATH = Path(__file__).parent / "config.json"
with open(CONFIG_PATH) as f:
    CONFIG = json.load(f)

app = Flask(__name__, template_folder=str(Path(__file__).parent / "templates"))

# ====== Admin: Flask secret key (auto-generated) ======
SECRET_PATH = Path(__file__).parent / ".admin_secret"
if SECRET_PATH.exists():
    app.secret_key = SECRET_PATH.read_text().strip()
else:
    app.secret_key = secrets.token_hex(32)
    SECRET_PATH.write_text(app.secret_key)

BACKUPS_DIR = Path(__file__).parent / "backups"
BACKUPS_DIR.mkdir(exist_ok=True)

# Rate limiting for PIN auth
_login_attempts = {}  # ip -> {"count": int, "last": float}

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
        auto_import_channels()
        return True
    except Exception as e:
        print(f"EPG fetch error: {e}")
        return False


def auto_import_channels():
    """If CONFIG has no channels, auto-populate from EPG data."""
    if CONFIG.get("channels"):
        return
    if not epg_cache["channels"]:
        return
    CONFIG["channels"] = [
        {"number": int(ch["number"]) if ch["number"].isdigit() else 0,
         "name": ch["name"]}
        for ch in epg_cache["channels"]
    ]
    try:
        _backup_config()
        _atomic_write_config(CONFIG)
        print(f"Auto-imported {len(CONFIG['channels'])} channels from EPG")
    except Exception as e:
        print(f"Auto-import save error: {e}")


def _config_channel_map():
    """Build a lookup map of str(number) -> config channel entry."""
    channels = CONFIG.get("channels", [])
    if not channels:
        return None  # None = no filtering
    return {str(c["number"]): c for c in channels}


def get_visible_channels():
    """Return EPG channels filtered by config, with name overrides applied."""
    cmap = _config_channel_map()
    if cmap is None:
        return epg_cache["channels"]
    visible = []
    for ch in epg_cache["channels"]:
        cc = cmap.get(ch["number"])
        if cc is None:
            continue
        ch_copy = dict(ch)
        if cc.get("name"):
            ch_copy["name"] = cc["name"]
        visible.append(ch_copy)
    return visible


def get_filtered_epg():
    """Return epg_cache filtered to only configured channels."""
    visible = get_visible_channels()
    if visible is epg_cache["channels"]:
        return epg_cache  # no filtering needed
    visible_ids = {ch["id"] for ch in visible}
    programmes = [p for p in epg_cache["programmes"]
                  if p["channel_id"] in visible_ids]
    return {
        "channels": visible,
        "programmes": programmes,
        "last_update": epg_cache.get("last_update"),
    }


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
    return jsonify(get_filtered_epg())


@app.route("/api/epg/refresh", methods=["POST"])
def api_epg_refresh():
    fetch_epg()
    return jsonify({"status": "ok", "last_update": epg_cache["last_update"]})


@app.route("/api/now")
def api_now():
    if not epg_cache["channels"]:
        fetch_epg()
    now_ts = datetime.now().timestamp()
    visible = get_visible_channels()
    result = []
    for ch in visible:
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
        "forecast_days": CONFIG.get("weather", {}).get("forecast_days", 5),
    })


@app.route("/api/ticker")
def api_ticker():
    if not epg_cache["channels"]:
        fetch_epg()
    ticker_cfg = CONFIG.get("ticker", {})
    now_ts = datetime.now().timestamp()
    now_playing = []
    if ticker_cfg.get("show_now_playing", True):
        visible = get_visible_channels()
        for ch in visible:
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


# ====== Admin Panel ======

HOT_RELOAD_KEYS = {"ticker", "default_theme", "channels", "default_channel", "admin"}
GUIDE_RESTART_KEYS = {"guide_port", "ersatztv_url", "player_url"}
PLAYER_RESTART_KEYS = {"web_port", "mpv_options", "mpv_socket", "ersatztv_url"}


def reload_config():
    global CONFIG, ERSATZTV_URL, PLAYER_URL
    with open(CONFIG_PATH) as f:
        new = json.load(f)
    CONFIG.clear()
    CONFIG.update(new)
    ERSATZTV_URL = CONFIG["ersatztv_url"].rstrip("/")
    PLAYER_URL = CONFIG.get("player_url", "http://localhost:5000").rstrip("/")


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("admin_authed"):
            return jsonify({"error": "unauthorized"}), 401
        timeout = CONFIG.get("admin", {}).get("session_timeout_minutes", 60)
        if time.time() - session.get("admin_ts", 0) > timeout * 60:
            session.clear()
            return jsonify({"error": "session expired"}), 401
        return f(*args, **kwargs)
    return decorated


def _backup_config():
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = BACKUPS_DIR / f"config_{ts}.json"
    shutil.copy2(CONFIG_PATH, dest)
    # Keep last 20 backups
    backups = sorted(BACKUPS_DIR.glob("config_*.json"))
    for old in backups[:-20]:
        old.unlink()
    return dest.name


def _atomic_write_config(data):
    tmp = CONFIG_PATH.with_suffix(".tmp")
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")
    tmp.rename(CONFIG_PATH)


def _check_rate_limit(ip):
    now = time.time()
    rec = _login_attempts.get(ip, {"count": 0, "last": 0})
    if rec["count"] >= 5 and now - rec["last"] < 300:
        return False
    return True


def _record_failed_login(ip):
    now = time.time()
    rec = _login_attempts.get(ip, {"count": 0, "last": 0})
    if now - rec["last"] > 300:
        rec = {"count": 0, "last": now}
    rec["count"] += 1
    rec["last"] = now
    _login_attempts[ip] = rec


# --- Admin page ---

@app.route("/admin")
def admin_page():
    return render_template("admin.html")


# --- Auth ---

@app.route("/admin/api/auth/login", methods=["POST"])
def admin_login():
    ip = flask_request.remote_addr
    if not _check_rate_limit(ip):
        return jsonify({"error": "Too many attempts. Try again in 5 minutes."}), 429
    data = flask_request.get_json(silent=True) or {}
    pin = str(data.get("pin", ""))
    expected = str(CONFIG.get("admin", {}).get("pin", "1234"))
    if pin == expected:
        session["admin_authed"] = True
        session["admin_ts"] = time.time()
        _login_attempts.pop(ip, None)
        return jsonify({"ok": True})
    _record_failed_login(ip)
    return jsonify({"error": "Invalid PIN"}), 401


@app.route("/admin/api/auth/logout", methods=["POST"])
def admin_logout():
    session.clear()
    return jsonify({"ok": True})


@app.route("/admin/api/auth/check")
def admin_auth_check():
    if not session.get("admin_authed"):
        return jsonify({"authed": False}), 401
    timeout = CONFIG.get("admin", {}).get("session_timeout_minutes", 60)
    if time.time() - session.get("admin_ts", 0) > timeout * 60:
        session.clear()
        return jsonify({"authed": False}), 401
    return jsonify({"authed": True})


# --- Config ---

@app.route("/admin/api/config")
@admin_required
def admin_get_config():
    return jsonify(CONFIG)


@app.route("/admin/api/config", methods=["PUT"])
@admin_required
def admin_put_config():
    data = flask_request.get_json(silent=True)
    if not data or not isinstance(data, dict):
        return jsonify({"error": "Invalid JSON"}), 400
    global ERSATZTV_URL, PLAYER_URL
    _backup_config()
    changed_keys = set(data.keys())
    CONFIG.clear()
    CONFIG.update(data)
    _atomic_write_config(CONFIG)
    ERSATZTV_URL = CONFIG["ersatztv_url"].rstrip("/")
    PLAYER_URL = CONFIG.get("player_url", "http://localhost:5000").rstrip("/")
    restart_services = []
    if changed_keys & GUIDE_RESTART_KEYS:
        restart_services.append("tv-guide")
    if changed_keys & PLAYER_RESTART_KEYS:
        restart_services.append("tv-player")
    return jsonify({"saved": True, "restart_needed": len(restart_services) > 0,
                     "services": restart_services})


@app.route("/admin/api/config/section/<name>", methods=["PUT"])
@admin_required
def admin_put_config_section(name):
    data = flask_request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Invalid JSON"}), 400
    _backup_config()
    CONFIG[name] = data
    _atomic_write_config(CONFIG)
    reload_config()
    restart_services = []
    if name in GUIDE_RESTART_KEYS or (name == "ersatztv_url"):
        restart_services.append("tv-guide")
    if name in PLAYER_RESTART_KEYS or name in ("mpv_options", "mpv_socket"):
        restart_services.append("tv-player")
    return jsonify({"saved": True, "restart_needed": len(restart_services) > 0,
                     "services": restart_services})


# --- Status ---

@app.route("/admin/api/status")
@admin_required
def admin_status():
    info = {}
    # System info
    try:
        with open("/proc/uptime") as f:
            uptime_secs = float(f.read().split()[0])
        days = int(uptime_secs // 86400)
        hours = int((uptime_secs % 86400) // 3600)
        mins = int((uptime_secs % 3600) // 60)
        info["uptime"] = f"{days}d {hours}h {mins}m"
    except Exception:
        info["uptime"] = "unknown"
    try:
        with open("/proc/meminfo") as f:
            mem = {}
            for line in f:
                parts = line.split()
                if parts[0] in ("MemTotal:", "MemAvailable:"):
                    mem[parts[0].rstrip(":")] = int(parts[1])
            total = mem.get("MemTotal", 0) // 1024
            avail = mem.get("MemAvailable", 0) // 1024
            info["memory"] = {"total_mb": total, "available_mb": avail,
                              "used_mb": total - avail}
    except Exception:
        info["memory"] = {}
    try:
        st = os.statvfs("/")
        total_gb = round((st.f_blocks * st.f_frsize) / (1024**3), 1)
        free_gb = round((st.f_bavail * st.f_frsize) / (1024**3), 1)
        info["disk"] = {"total_gb": total_gb, "free_gb": free_gb,
                        "used_gb": round(total_gb - free_gb, 1)}
    except Exception:
        info["disk"] = {}
    try:
        with open("/sys/class/thermal/thermal_zone0/temp") as f:
            info["cpu_temp_c"] = round(int(f.read().strip()) / 1000, 1)
    except Exception:
        info["cpu_temp_c"] = None
    try:
        with open("/proc/loadavg") as f:
            parts = f.read().split()
            info["load_average"] = [float(parts[0]), float(parts[1]), float(parts[2])]
    except Exception:
        info["load_average"] = []
    # Service status
    for svc in ("tv-guide", "tv-player"):
        try:
            r = subprocess.run(["sudo", "systemctl", "is-active", svc],
                               capture_output=True, text=True, timeout=5)
            info[svc.replace("-", "_") + "_status"] = r.stdout.strip()
        except Exception:
            info[svc.replace("-", "_") + "_status"] = "unknown"
    # ErsatzTV connectivity
    try:
        r = requests.get(ERSATZTV_URL, timeout=5)
        info["ersatztv_reachable"] = r.status_code < 500
    except Exception:
        info["ersatztv_reachable"] = False
    # EPG info
    info["epg_last_update"] = epg_cache.get("last_update")
    info["epg_channels"] = len(epg_cache.get("channels", []))
    info["epg_programmes"] = len(epg_cache.get("programmes", []))
    # Weather status
    info["weather_ok"] = weather_cache.get("data") is not None
    info["weather_last_fetch"] = weather_cache.get("last_fetch", 0)
    return jsonify(info)


@app.route("/admin/api/status/test-ersatztv", methods=["POST"])
@admin_required
def admin_test_ersatztv():
    data = flask_request.get_json(silent=True) or {}
    url = data.get("url", ERSATZTV_URL).rstrip("/")
    try:
        r = requests.get(url, timeout=5)
        xmltv = requests.get(url + "/iptv/xmltv.xml", timeout=10)
        ch_count = 0
        if xmltv.status_code == 200:
            root = ET.fromstring(xmltv.content)
            ch_count = len(root.findall("channel"))
        return jsonify({"ok": True, "status_code": r.status_code,
                        "channels_found": ch_count})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})


@app.route("/admin/api/status/test-weather", methods=["POST"])
@admin_required
def admin_test_weather():
    data = flask_request.get_json(silent=True) or {}
    lat = data.get("latitude", CONFIG.get("ticker", {}).get("weather", {}).get("latitude", 33.749))
    lon = data.get("longitude", CONFIG.get("ticker", {}).get("weather", {}).get("longitude", -84.388))
    unit = data.get("temperature_unit", CONFIG.get("ticker", {}).get("weather", {}).get("temperature_unit", "fahrenheit"))
    try:
        url = (f"https://api.open-meteo.com/v1/forecast"
               f"?latitude={lat}&longitude={lon}"
               f"&current=temperature_2m,weather_code"
               f"&temperature_unit={unit}")
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        d = r.json().get("current", {})
        code = d.get("weather_code", 0)
        return jsonify({"ok": True, "temperature": d.get("temperature_2m"),
                        "condition": WMO_CODES.get(code, "Unknown"),
                        "unit": "F" if unit == "fahrenheit" else "C"})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})


@app.route("/admin/api/status/test-feed", methods=["POST"])
@admin_required
def admin_test_feed():
    data = flask_request.get_json(silent=True) or {}
    url = data.get("url", "")
    if not url:
        return jsonify({"ok": False, "error": "No URL provided"})
    try:
        parsed = feedparser.parse(url)
        count = len(parsed.entries)
        titles = [e.get("title", "")[:80] for e in parsed.entries[:3]]
        return jsonify({"ok": True, "entry_count": count, "sample_titles": titles})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})


@app.route("/admin/api/status/test-stream/<int:ch_num>", methods=["POST"])
@admin_required
def admin_test_stream(ch_num):
    url = f"{ERSATZTV_URL}/iptv/channel/{ch_num}.ts"
    try:
        start = time.time()
        r = requests.get(url, stream=True, timeout=10)
        chunk = next(r.iter_content(chunk_size=1024), None)
        latency = round((time.time() - start) * 1000)
        r.close()
        if chunk and len(chunk) > 0:
            return jsonify({"ok": True, "latency_ms": latency, "bytes": len(chunk)})
        return jsonify({"ok": False, "error": "Empty stream", "latency_ms": latency})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})


# --- Channel Discovery ---

@app.route("/admin/api/channels/discover")
@admin_required
def admin_discover_channels():
    try:
        url = ERSATZTV_URL + "/iptv/xmltv.xml"
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        root = ET.fromstring(r.content)
        discovered = []
        for ch in root.findall("channel"):
            names = [n.text for n in ch.findall("display-name")]
            discovered.append({
                "id": ch.get("id"),
                "number": names[1] if len(names) > 1 else "0",
                "name": names[2] if len(names) > 2 else names[0],
            })
        return jsonify({"ok": True, "channels": discovered})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})


# --- Services ---

@app.route("/admin/api/services/restart/<svc>", methods=["POST"])
@admin_required
def admin_restart_service(svc):
    allowed = {"tv-guide", "tv-player", "both"}
    if svc not in allowed:
        return jsonify({"error": "Invalid service"}), 400
    results = {}
    targets = ["tv-guide", "tv-player"] if svc == "both" else [svc]
    for s in targets:
        try:
            r = subprocess.run(["sudo", "systemctl", "restart", s],
                               capture_output=True, text=True, timeout=15)
            results[s] = {"ok": r.returncode == 0, "output": r.stderr.strip()}
        except Exception as e:
            results[s] = {"ok": False, "output": str(e)}
    return jsonify(results)


@app.route("/admin/api/services/logs/<svc>")
@admin_required
def admin_service_logs(svc):
    if svc not in ("tv-guide", "tv-player"):
        return jsonify({"error": "Invalid service"}), 400
    try:
        r = subprocess.run(
            ["sudo", "journalctl", "-u", svc, "-n", "100", "--no-pager", "-o", "short-iso"],
            capture_output=True, text=True, timeout=10)
        return jsonify({"ok": True, "lines": r.stdout.strip().split("\n")})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})


# --- Backups ---

@app.route("/admin/api/config/backup", methods=["POST"])
@admin_required
def admin_create_backup():
    name = _backup_config()
    return jsonify({"ok": True, "filename": name})


@app.route("/admin/api/config/backups")
@admin_required
def admin_list_backups():
    files = sorted(BACKUPS_DIR.glob("config_*.json"), reverse=True)
    result = []
    for f in files:
        stat = f.stat()
        result.append({
            "filename": f.name,
            "size": stat.st_size,
            "created": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        })
    return jsonify(result)


@app.route("/admin/api/config/restore/<filename>", methods=["POST"])
@admin_required
def admin_restore_backup(filename):
    # Sanitize filename
    if "/" in filename or "\\" in filename or ".." in filename:
        return jsonify({"error": "Invalid filename"}), 400
    src = BACKUPS_DIR / filename
    if not src.exists():
        return jsonify({"error": "Backup not found"}), 404
    # Backup current before restoring
    _backup_config()
    # Validate the backup is valid JSON
    try:
        with open(src) as f:
            data = json.load(f)
    except json.JSONDecodeError:
        return jsonify({"error": "Backup file is not valid JSON"}), 400
    _atomic_write_config(data)
    reload_config()
    return jsonify({"ok": True, "restored": filename})


@app.route("/admin/api/config/backups/<filename>")
@admin_required
def admin_download_backup(filename):
    if "/" in filename or "\\" in filename or ".." in filename:
        return jsonify({"error": "Invalid filename"}), 400
    src = BACKUPS_DIR / filename
    if not src.exists():
        return jsonify({"error": "Backup not found"}), 404
    return Response(src.read_text(), content_type="application/json",
                    headers={"Content-Disposition": f"attachment; filename={filename}"})


# --- EPG ---

@app.route("/admin/api/epg/refresh", methods=["POST"])
@admin_required
def admin_epg_refresh():
    ok = fetch_epg()
    return jsonify({
        "ok": ok,
        "channels": len(epg_cache.get("channels", [])),
        "programmes": len(epg_cache.get("programmes", [])),
        "last_update": epg_cache.get("last_update"),
    })


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
