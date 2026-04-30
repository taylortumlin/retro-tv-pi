"""Admin panel API: auth, config CRUD, status, backups, services, EPG refresh."""

from __future__ import annotations

import hmac
import json
import os
import subprocess
import time
import xml.etree.ElementTree as ET
from datetime import datetime
from functools import wraps

import requests
from flask import Blueprint, Response, jsonify, request as flask_request, session

from . import _state
from .config_io import (
    atomic_write_config,
    backup_config,
    check_login_rate_limit,
    clear_login_attempts,
    record_failed_login,
)
from .epg import fetch_epg
from .news import fetch_feed
from .weather import WMO_CODES

bp = Blueprint("admin", __name__)


HOT_RELOAD_KEYS = {"ticker", "default_theme", "channels", "default_channel", "admin"}
GUIDE_RESTART_KEYS = {"guide_port", "ersatztv_url", "player_url"}
PLAYER_RESTART_KEYS = {"web_port", "mpv_options", "mpv_socket", "ersatztv_url"}


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("admin_authed"):
            return jsonify({"error": "unauthorized"}), 401
        timeout = _state.CONFIG.get("admin", {}).get("session_timeout_minutes", 60)
        if time.time() - session.get("admin_ts", 0) > timeout * 60:
            session.clear()
            return jsonify({"error": "session expired"}), 401
        # Sliding-window: each authed request refreshes the activity timestamp
        # so timeout means "idle for N minutes" rather than "force logout
        # N minutes after login regardless of activity".
        session["admin_ts"] = time.time()
        # CSRF defense-in-depth: reject form-encoded mutating requests.
        # SameSite=Strict (set in __init__.py) is the primary defense, but
        # has known top-level-navigation bypasses; this rejects the most
        # common attack vector (an auto-POSTed HTML form from another
        # LAN page).
        if flask_request.method in ("POST", "PUT", "DELETE", "PATCH"):
            ctype = (flask_request.content_type or "").split(";")[0].strip().lower()
            # Allow JSON or no body. Reject form-encoded.
            if ctype and ctype != "application/json":
                return jsonify({"error": "JSON content-type required"}), 415
        return f(*args, **kwargs)
    return decorated


# --- Auth ---

@bp.route("/auth/login", methods=["POST"])
def admin_login():
    ip = flask_request.remote_addr
    if not check_login_rate_limit(ip):
        return jsonify({"error": "Too many attempts. Try again in 5 minutes."}), 429
    data = flask_request.get_json(silent=True) or {}
    pin = str(data.get("pin", ""))
    expected = _state.CONFIG.get("admin", {}).get("pin")
    if not expected:
        # Fail closed if no PIN is configured -- previously this fell back
        # to "1234" which would silently accept any guesser typing the
        # default during fresh-install windows.
        return jsonify({"error": "Admin PIN not configured"}), 500
    if hmac.compare_digest(pin, str(expected)):
        session["admin_authed"] = True
        session["admin_ts"] = time.time()
        clear_login_attempts(ip)
        return jsonify({"ok": True})
    record_failed_login(ip)
    return jsonify({"error": "Invalid PIN"}), 401


@bp.route("/auth/logout", methods=["POST"])
def admin_logout():
    session.clear()
    return jsonify({"ok": True})


@bp.route("/auth/check")
def admin_auth_check():
    if not session.get("admin_authed"):
        return jsonify({"authed": False}), 401
    timeout = _state.CONFIG.get("admin", {}).get("session_timeout_minutes", 60)
    if time.time() - session.get("admin_ts", 0) > timeout * 60:
        session.clear()
        return jsonify({"authed": False}), 401
    return jsonify({"authed": True})


# --- Config ---

@bp.route("/config")
@admin_required
def admin_get_config():
    # Strip the PIN before responding -- the SPA never needs it (PIN is
    # set via PUT /admin/api/config/section/admin), and leaving it in the
    # response leaks the credential to anything that can read CacheStorage
    # for this origin.
    safe = dict(_state.CONFIG)
    if isinstance(safe.get("admin"), dict):
        safe["admin"] = {k: v for k, v in safe["admin"].items() if k != "pin"}
    return jsonify(safe)


@bp.route("/config", methods=["PUT"])
@admin_required
def admin_put_config():
    data = flask_request.get_json(silent=True)
    if not data or not isinstance(data, dict):
        return jsonify({"error": "Invalid JSON"}), 400
    backup_config()
    changed_keys = set(data.keys())
    _state.CONFIG.clear()
    _state.CONFIG.update(data)
    atomic_write_config(_state.CONFIG)
    _state.ERSATZTV_URL = _state.CONFIG["ersatztv_url"].rstrip("/")
    _state.PLAYER_URL = _state.CONFIG.get("player_url", "http://localhost:5000").rstrip("/")
    restart_services = []
    if changed_keys & GUIDE_RESTART_KEYS:
        restart_services.append("tv-guide")
    if changed_keys & PLAYER_RESTART_KEYS:
        restart_services.append("tv-player")
    return jsonify({"saved": True, "restart_needed": len(restart_services) > 0,
                    "services": restart_services})


@bp.route("/config/section/<name>", methods=["PUT"])
@admin_required
def admin_put_config_section(name: str):
    data = flask_request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Invalid JSON"}), 400
    backup_config()
    _state.CONFIG[name] = data
    atomic_write_config(_state.CONFIG)
    _state.reload_from_disk()
    restart_services = []
    if name in GUIDE_RESTART_KEYS or (name == "ersatztv_url"):
        restart_services.append("tv-guide")
    if name in PLAYER_RESTART_KEYS or name in ("mpv_options", "mpv_socket"):
        restart_services.append("tv-player")
    return jsonify({"saved": True, "restart_needed": len(restart_services) > 0,
                    "services": restart_services})


# --- Status ---

@bp.route("/status")
@admin_required
def admin_status():
    info = {}
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
    for svc in ("tv-guide", "tv-player"):
        try:
            r = subprocess.run(["sudo", "systemctl", "is-active", svc],
                               capture_output=True, text=True, timeout=5)
            info[svc.replace("-", "_") + "_status"] = r.stdout.strip()
        except Exception:
            info[svc.replace("-", "_") + "_status"] = "unknown"
    try:
        r = requests.get(_state.ERSATZTV_URL, timeout=5)
        info["ersatztv_reachable"] = r.status_code < 500
    except Exception:
        info["ersatztv_reachable"] = False
    info["epg_last_update"] = _state.epg_cache.get("last_update")
    info["epg_channels"] = len(_state.epg_cache.get("channels", []))
    info["epg_programmes"] = len(_state.epg_cache.get("programmes", []))
    info["weather_ok"] = _state.weather_cache.get("data") is not None
    info["weather_last_fetch"] = _state.weather_cache.get("last_fetch", 0)
    return jsonify(info)


@bp.route("/status/test-ersatztv", methods=["POST"])
@admin_required
def admin_test_ersatztv():
    data = flask_request.get_json(silent=True) or {}
    url = data.get("url", _state.ERSATZTV_URL).rstrip("/")
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


@bp.route("/status/test-weather", methods=["POST"])
@admin_required
def admin_test_weather():
    data = flask_request.get_json(silent=True) or {}
    weather_cfg = _state.CONFIG.get("ticker", {}).get("weather", {})
    lat = data.get("latitude", weather_cfg.get("latitude", 33.749))
    lon = data.get("longitude", weather_cfg.get("longitude", -84.388))
    unit = data.get("temperature_unit", weather_cfg.get("temperature_unit", "fahrenheit"))
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


@bp.route("/status/test-feed", methods=["POST"])
@admin_required
def admin_test_feed():
    data = flask_request.get_json(silent=True) or {}
    url = data.get("url", "")
    if not url:
        return jsonify({"ok": False, "error": "No URL provided"})
    parsed = fetch_feed(url)
    if parsed is None:
        return jsonify({"ok": False, "error": "Feed fetch failed (timeout or HTTP error)"})
    try:
        count = len(parsed.entries)
        titles = [e.get("title", "")[:80] for e in parsed.entries[:3]]
        return jsonify({"ok": True, "entry_count": count, "sample_titles": titles})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})


@bp.route("/status/test-stream/<int:ch_num>", methods=["POST"])
@admin_required
def admin_test_stream(ch_num: int):
    url = f"{_state.ERSATZTV_URL}/iptv/channel/{ch_num}.ts"
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

@bp.route("/channels/discover")
@admin_required
def admin_discover_channels():
    try:
        url = _state.ERSATZTV_URL + "/iptv/xmltv.xml"
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

@bp.route("/services/restart/<svc>", methods=["POST"])
@admin_required
def admin_restart_service(svc: str):
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


@bp.route("/services/logs/<svc>")
@admin_required
def admin_service_logs(svc: str):
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

@bp.route("/config/backup", methods=["POST"])
@admin_required
def admin_create_backup():
    name = backup_config()
    return jsonify({"ok": True, "filename": name})


@bp.route("/config/backups")
@admin_required
def admin_list_backups():
    files = sorted(_state.BACKUPS_DIR.glob("config_*.json"), reverse=True)
    result = []
    for f in files:
        stat = f.stat()
        result.append({
            "filename": f.name,
            "size": stat.st_size,
            "created": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        })
    return jsonify(result)


@bp.route("/config/restore/<filename>", methods=["POST"])
@admin_required
def admin_restore_backup(filename: str):
    if "/" in filename or "\\" in filename or ".." in filename:
        return jsonify({"error": "Invalid filename"}), 400
    # Restrict to the glob the listing endpoint produces. Without this, any
    # sibling JSON file in BACKUPS_DIR (placed there by another process or
    # dropped in manually) could be loaded as the live config -- including
    # malicious mpv_options or SSRF-bait ersatztv_url.
    if not (filename.startswith("config_") and filename.endswith(".json")):
        return jsonify({"error": "Invalid backup filename"}), 400
    src = _state.BACKUPS_DIR / filename
    if not src.exists():
        return jsonify({"error": "Backup not found"}), 404
    backup_config()
    try:
        with open(src) as f:
            data = json.load(f)
    except json.JSONDecodeError:
        return jsonify({"error": "Backup file is not valid JSON"}), 400
    if not isinstance(data, dict) or "channels" not in data or "ersatztv_url" not in data:
        return jsonify({"error": "Backup is missing required keys"}), 400
    atomic_write_config(data)
    _state.reload_from_disk()
    return jsonify({"ok": True, "restored": filename})


@bp.route("/config/backups/<filename>")
@admin_required
def admin_download_backup(filename: str):
    if "/" in filename or "\\" in filename or ".." in filename:
        return jsonify({"error": "Invalid filename"}), 400
    if not (filename.startswith("config_") and filename.endswith(".json")):
        return jsonify({"error": "Invalid backup filename"}), 400
    src = _state.BACKUPS_DIR / filename
    if not src.exists():
        return jsonify({"error": "Backup not found"}), 404
    return Response(src.read_text(), content_type="application/json",
                    headers={"Content-Disposition": f"attachment; filename={filename}"})


# --- EPG ---

@bp.route("/epg/refresh", methods=["POST"])
@admin_required
def admin_epg_refresh():
    ok = fetch_epg()
    return jsonify({
        "ok": ok,
        "channels": len(_state.epg_cache.get("channels", [])),
        "programmes": len(_state.epg_cache.get("programmes", [])),
        "last_update": _state.epg_cache.get("last_update"),
    })
