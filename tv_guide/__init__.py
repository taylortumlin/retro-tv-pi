"""Pi TV Guide — Flask package entry point.

Identical behaviour to the legacy `tv_guide.py` monolith. The
`gunicorn ... tv_guide:app` import path resolves to the module-level
`app` defined here, so no systemd-unit changes are required for the swap.
"""

from __future__ import annotations

import os
import secrets
from pathlib import Path

from flask import Flask

from . import _state
from . import api as api_module
from . import admin as admin_module
from . import player_proxy as player_proxy_module
from . import spa as spa_module
from . import stream as stream_module
from .epg import fetch_epg, start_background_refresh
from .news import fetch_news
from .weather import fetch_weather

# Re-exports so callers that still do `from tv_guide import fetch_epg` etc.
# (or read module-level globals like CONFIG) keep working.
CONFIG = _state.CONFIG
ERSATZTV_URL = _state.ERSATZTV_URL
PLAYER_URL = _state.PLAYER_URL


def create_app() -> Flask:
    project_root = Path(__file__).parent.parent
    flask_app = Flask(
        __name__,
        # Both folders are at the project root, not inside the package.
        template_folder=str(project_root / "templates"),
        static_folder=str(project_root / "static"),
        static_url_path="/static",
    )

    flask_app.config.update(
        # HttpOnly: keep the session cookie out of `document.cookie` /
        # XSS reach. SameSite=Strict: never sent on cross-site navigations,
        # which blocks the most common CSRF vector. Secure: would require
        # HTTPS; this app runs on HTTP on a LAN, so leave False.
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Strict",
        SESSION_COOKIE_SECURE=False,
    )

    # Persisted Flask secret key (auto-generated on first run).
    # O_EXCL makes concurrent gunicorn workers race-safe: the loser gets
    # FileExistsError and reads the winner's value. 0o600 keeps the key
    # out of reach of other local users (it signs admin sessions).
    secret_path = Path(__file__).parent.parent / ".admin_secret"
    try:
        fd = os.open(secret_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        try:
            os.write(fd, secrets.token_hex(32).encode())
        finally:
            os.close(fd)
    except FileExistsError:
        pass
    flask_app.secret_key = secret_path.read_text().strip()

    flask_app.register_blueprint(api_module.bp, url_prefix="/api")
    flask_app.register_blueprint(stream_module.bp, url_prefix="/stream")
    flask_app.register_blueprint(player_proxy_module.bp, url_prefix="/api/player")
    flask_app.register_blueprint(admin_module.bp, url_prefix="/admin/api")
    # SPA catch-all is registered last so the more specific prefixes win.
    flask_app.register_blueprint(spa_module.bp)

    return flask_app


def _startup() -> None:
    """Initial data fetch + background refresh thread.

    Runs under gunicorn workers AND under direct `python3 -m tv_guide`.
    """
    print("Fetching EPG data...")
    fetch_epg()
    print("Fetching weather...")
    fetch_weather()
    print("Fetching news...")
    fetch_news()
    print(
        f"Loaded {len(_state.epg_cache['channels'])} channels, "
        f"{len(_state.epg_cache['programmes'])} programmes"
    )
    start_background_refresh()


app = create_app()
_startup()


def main() -> None:
    port = _state.CONFIG.get("guide_port", 5001)
    print(f"TV Guide at http://0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port, threaded=True)


if __name__ == "__main__":
    main()
