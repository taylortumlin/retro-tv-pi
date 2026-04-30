"""Service worker + SPA catch-all routes."""

from __future__ import annotations

from flask import Blueprint, current_app

bp = Blueprint("spa", __name__)


@bp.route("/sw.js")
def service_worker():
    return current_app.send_static_file("sw.js"), 200, {
        "Content-Type": "application/javascript",
        "Service-Worker-Allowed": "/",
    }


@bp.route("/")
@bp.route("/<path:path>")
def spa(path: str = ""):
    # Let API, stream, admin API, and static routes pass through.
    if path.startswith(("api/", "stream/", "admin/api/", "static/")):
        return "Not Found", 404
    return current_app.send_static_file("dist/index.html")
