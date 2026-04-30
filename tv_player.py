#!/usr/bin/env python3
"""
Pi TV Channel Player
Controls mpv playback of ErsatzTV IPTV streams with web interface control.

Usage:
    python3 tv_player.py              # Production (uses config mpv_options)
    python3 tv_player.py --headless   # Headless testing (vo=null, ao=null)
"""

import argparse
import json
import logging
import os
import subprocess
import signal
import socket
import sys
import threading
import time
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory, Response
import requests as http_requests

# ====== Logging ======
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("tv-player")

# Load config
CONFIG_PATH = Path(__file__).parent / "config.json"
with open(CONFIG_PATH) as f:
    CONFIG = json.load(f)

MPV_SOCKET = CONFIG.get("mpv_socket", "/tmp/mpvsocket")

# Admins set mpv_options via config.json. Anything that can load executable
# code (--script, --input-conf, --include, --load-scripts, --lua,
# --script-opts, --input-cmdlist, ...) would turn config write access into
# RCE; restrict to display/decode/cache flags that are safe for the player
# to expose.
ALLOWED_MPV_OPTS = {
    "fullscreen", "vo", "hwdec", "profile", "audio-display", "osd-level",
    "osc", "really-quiet", "no-terminal", "cache", "demuxer-readahead-secs",
    "cache-secs", "stream-buffer-size", "screen", "fs-screen", "geometry",
    "audio-device", "ao", "volume", "mute", "input-default-bindings",
    "input-vo-keyboard", "keepaspect", "panscan",
}

STATIC_DIR = Path(__file__).parent / "static"
TEMPLATE_DIR = Path(__file__).parent / "templates"

app = Flask(__name__, static_folder=str(STATIC_DIR))

HEADLESS = False


# Global state
class PlayerState:
    def __init__(self):
        self.current_channel = CONFIG["default_channel"]
        self.mpv_process = None
        self.muted = False
        self.paused = False
        self.volume = 100
        self.lock = threading.Lock()

state = PlayerState()


def get_channel_name(num):
    for ch in CONFIG["channels"]:
        if ch["number"] == num:
            return ch["name"]
    return f"Channel {num}"


def get_stream_url(channel_num):
    base = CONFIG["ersatztv_url"].rstrip("/")
    return f"{base}/iptv/channel/{channel_num}.ts"


def start_mpv(channel_num):
    url = get_stream_url(channel_num)
    cmd = ["mpv", f"--input-ipc-server={MPV_SOCKET}"]

    if HEADLESS:
        cmd += ["--vo=null", "--ao=null"]
    else:
        opts = CONFIG.get("mpv_options", {})
        for key, value in opts.items():
            if key not in ALLOWED_MPV_OPTS:
                log.warning("Ignoring disallowed mpv option: %s", key)
                continue
            if value is True:
                cmd.append(f"--{key}")
            elif value is not False:
                cmd.append(f"--{key}={value}")

    cmd.append(url)
    log.info("Starting mpv: %s", " ".join(cmd))
    return subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def stop_mpv():
    if state.mpv_process:
        state.mpv_process.terminate()
        try:
            state.mpv_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            state.mpv_process.kill()
        state.mpv_process = None


def mpv_command(cmd):
    try:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.settimeout(2)
        sock.connect(MPV_SOCKET)
        sock.send((json.dumps({"command": cmd}) + "\n").encode())
        sock.close()
    except FileNotFoundError:
        log.warning("mpv socket not found at %s — is mpv running?", MPV_SOCKET)
    except ConnectionRefusedError:
        log.warning("mpv socket connection refused — mpv may be starting up")
    except Exception as e:
        log.error("mpv command error: %s", e)


def switch_channel(channel_num):
    with state.lock:
        stop_mpv()
        state.current_channel = channel_num
        state.mpv_process = start_mpv(channel_num)
        state.paused = False


def channel_up():
    numbers = sorted(ch["number"] for ch in CONFIG["channels"])
    idx = numbers.index(state.current_channel) if state.current_channel in numbers else -1
    next_ch = numbers[(idx + 1) % len(numbers)]
    switch_channel(next_ch)


def channel_down():
    numbers = sorted(ch["number"] for ch in CONFIG["channels"])
    idx = numbers.index(state.current_channel) if state.current_channel in numbers else 0
    prev_ch = numbers[(idx - 1) % len(numbers)]
    switch_channel(prev_ch)


# ====== Flask routes ======

@app.route("/")
def index():
    return send_from_directory(str(TEMPLATE_DIR), "player.html")


def _status_dict():
    return {
        "channel": state.current_channel,
        "channel_name": get_channel_name(state.current_channel),
        "muted": state.muted,
        "paused": state.paused,
        "volume": state.volume,
        "mpv_running": state.mpv_process is not None and state.mpv_process.poll() is None,
    }


@app.route("/api/status")
def api_status():
    return jsonify(_status_dict())


@app.route("/api/channels")
def api_channels():
    return jsonify(CONFIG["channels"])


@app.route("/api/channel/<int:num>", methods=["POST"])
def api_channel(num):
    switch_channel(num)
    return jsonify(_status_dict())


@app.route("/api/channel/up", methods=["POST"])
def api_channel_up():
    channel_up()
    return jsonify(_status_dict())


@app.route("/api/channel/down", methods=["POST"])
def api_channel_down():
    channel_down()
    return jsonify(_status_dict())


@app.route("/api/pause", methods=["POST"])
def api_pause():
    state.paused = not state.paused
    mpv_command(["cycle", "pause"])
    return jsonify(_status_dict())


@app.route("/api/mute", methods=["POST"])
def api_mute():
    state.muted = not state.muted
    mpv_command(["cycle", "mute"])
    return jsonify(_status_dict())


@app.route("/api/volume/<direction>", methods=["POST"])
def api_volume(direction):
    if direction == "up":
        state.volume = min(150, state.volume + 5)
        mpv_command(["add", "volume", "5"])
    elif direction == "down":
        state.volume = max(0, state.volume - 5)
        mpv_command(["add", "volume", "-5"])
    return jsonify(_status_dict())


# ====== Stream proxy (for in-browser preview) ======

@app.route("/stream/<int:ch_num>.ts")
def stream_proxy(ch_num):
    url = f"{CONFIG['ersatztv_url'].rstrip('/')}/iptv/channel/{ch_num}.ts"
    try:
        resp = http_requests.get(url, stream=True, timeout=10)

        def generate():
            try:
                for chunk in resp.iter_content(chunk_size=32 * 1024):
                    if chunk:
                        yield chunk
            except GeneratorExit:
                resp.close()
            except Exception:
                resp.close()

        return Response(
            generate(),
            content_type="video/mp2t",
            headers={
                "Cache-Control": "no-cache, no-store",
                "Access-Control-Allow-Origin": "*",
                "X-Content-Type-Options": "nosniff",
                "Transfer-Encoding": "chunked",
            },
            direct_passthrough=True,
        )
    except Exception as e:
        log.error("Stream proxy error ch%d: %s", ch_num, e)
        return f"Stream error: {e}", 502


@app.route("/api/refresh", methods=["POST"])
def api_refresh():
    switch_channel(state.current_channel)
    return jsonify(_status_dict())


# ====== Keyboard listener ======

def keyboard_listener():
    try:
        from evdev import InputDevice, ecodes, list_devices

        devices = [InputDevice(path) for path in list_devices()]
        keyboard = None
        for device in devices:
            if "keyboard" in device.name.lower():
                keyboard = device
                break

        if not keyboard:
            log.info("No keyboard found for input")
            return

        log.info("Listening on keyboard: %s", keyboard.name)

        key_map = {
            ecodes.KEY_1: 1, ecodes.KEY_2: 2, ecodes.KEY_3: 3,
            ecodes.KEY_4: 4, ecodes.KEY_5: 5, ecodes.KEY_6: 6,
            ecodes.KEY_7: 7, ecodes.KEY_8: 8, ecodes.KEY_9: 9,
            ecodes.KEY_0: 10,
        }

        # Multi-digit channel entry: type "15" within 1.5s to go to ch 15
        pending_digit = None
        pending_time = 0

        for event in keyboard.read_loop():
            if event.type != ecodes.EV_KEY or event.value != 1:
                continue

            if event.code in key_map:
                digit = key_map[event.code]
                now = time.time()
                if pending_digit is not None and now - pending_time < 1.5:
                    # Second digit: combine e.g. 1 then 5 -> 15
                    target = pending_digit * 10 + digit
                    pending_digit = None
                    if any(ch["number"] == target for ch in CONFIG["channels"]):
                        switch_channel(target)
                    else:
                        switch_channel(digit)
                else:
                    pending_digit = digit
                    pending_time = now
                    # Wait briefly for second digit, then switch
                    def _delayed_switch(d=digit, t=now):
                        time.sleep(1.5)
                        if pending_digit == d and pending_time == t:
                            switch_channel(d)
                    threading.Thread(target=_delayed_switch, daemon=True).start()
            elif event.code == ecodes.KEY_UP:
                channel_up()
            elif event.code == ecodes.KEY_DOWN:
                channel_down()
            elif event.code == ecodes.KEY_SPACE:
                state.paused = not state.paused
                mpv_command(["cycle", "pause"])
            elif event.code == ecodes.KEY_M:
                state.muted = not state.muted
                mpv_command(["cycle", "mute"])
            elif event.code == ecodes.KEY_Q:
                log.info("Quit requested")
                stop_mpv()
                sys.exit(0)

    except ImportError:
        log.info("evdev not installed, keyboard control disabled")
    except Exception as e:
        log.error("Keyboard listener error: %s", e)


def signal_handler(sig, frame):
    log.info("Shutting down...")
    stop_mpv()
    sys.exit(0)


def check_port_available(port):
    """Check if the web port is available before starting Flask."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("0.0.0.0", port))
        s.close()
        return True
    except OSError:
        return False


def check_ersatztv_reachable():
    """Non-blocking check if ErsatzTV is reachable on startup."""
    url = CONFIG["ersatztv_url"].rstrip("/")
    try:
        resp = http_requests.get(url, timeout=5)
        log.info("ErsatzTV reachable at %s (status %d)", url, resp.status_code)
    except Exception as e:
        log.warning("ErsatzTV not reachable at %s — %s", url, e)


def cleanup_stale_socket():
    """Remove stale mpv socket file if it exists."""
    if os.path.exists(MPV_SOCKET):
        try:
            # Try connecting to see if it's actually in use
            s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            s.settimeout(1)
            s.connect(MPV_SOCKET)
            s.close()
            log.warning("mpv socket %s is in use by another process", MPV_SOCKET)
        except (ConnectionRefusedError, FileNotFoundError, OSError):
            os.remove(MPV_SOCKET)
            log.info("Removed stale mpv socket %s", MPV_SOCKET)


def main():
    global HEADLESS

    parser = argparse.ArgumentParser(description="Pi TV Channel Player")
    parser.add_argument("--headless", action="store_true",
                        help="Run with null video/audio output for testing without a display")
    args = parser.parse_args()
    HEADLESS = args.headless

    if HEADLESS:
        log.info("=== HEADLESS TEST MODE (vo=null, ao=null) ===")

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    port = CONFIG["web_port"]

    # Pre-flight checks
    if not check_port_available(port):
        log.error("Port %d is already in use — is another instance running?", port)
        sys.exit(1)

    cleanup_stale_socket()
    check_ersatztv_reachable()

    kb_thread = threading.Thread(target=keyboard_listener, daemon=True)
    kb_thread.start()

    log.info("Starting Pi TV on channel %d (%s)", CONFIG["default_channel"], get_channel_name(CONFIG["default_channel"]))
    state.mpv_process = start_mpv(CONFIG["default_channel"])

    log.info("Web interface at http://0.0.0.0:%d", port)
    app.run(host="0.0.0.0", port=port, threaded=True)


if __name__ == "__main__":
    main()
