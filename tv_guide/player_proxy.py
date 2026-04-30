"""Proxies requests to the local tv_player.py Flask server (port 5000).

Lets the browser UI control the Pi's mpv-based hardware player without CORS.
"""

from __future__ import annotations

import requests
from flask import Blueprint, jsonify, request as flask_request

from . import _state

bp = Blueprint("player_proxy", __name__)


@bp.route("/<path:endpoint>", methods=["GET", "POST"])
def proxy_player(endpoint: str):
    url = f"{_state.PLAYER_URL}/api/{endpoint}"
    try:
        # `with` ensures the underlying connection is released back to the
        # pool even though `.json()` reads the body eagerly.
        if flask_request.method == "POST":
            with requests.post(url, timeout=5) as resp:
                return jsonify(resp.json())
        with requests.get(url, timeout=5) as resp:
            return jsonify(resp.json())
    except requests.ConnectionError:
        return jsonify({
            "error": "Player not running",
            "channel": "?",
            "channel_name": "Offline",
            "muted": False,
            "paused": False,
        }), 503
    except Exception as e:
        return jsonify({"error": str(e)}), 500
