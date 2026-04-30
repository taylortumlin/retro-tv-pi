"""Pi TV Guide — Flask package entry point.

Identical behaviour to the legacy `tv_guide.py` monolith. The
`gunicorn ... tv_guide:app` import path resolves to the module-level
`app` defined here, so no systemd-unit changes are required for the swap.
"""

from __future__ import annotations

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
    template_folder = str(Path(__file__).parent.parent / "templates")
    flask_app = Flask(__name__, template_folder=template_folder)

    # Persisted Flask secret key (auto-generated on first run).
    secret_path = Path(__file__).parent.parent / ".admin_secret"
    if secret_path.exists():
        flask_app.secret_key = secret_path.read_text().strip()
    else:
        flask_app.secret_key = secrets.token_hex(32)
        secret_path.write_text(flask_app.secret_key)

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
