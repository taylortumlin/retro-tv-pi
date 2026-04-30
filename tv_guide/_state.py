"""Shared module-level state for the tv_guide package.

Other modules access these via `from tv_guide import _state` and read/write
`_state.CONFIG`, `_state.ERSATZTV_URL`, etc., so reassignments in
`reload_config()` are visible to every module rather than being captured
at import time.
"""

from __future__ import annotations

import json
import threading
from pathlib import Path

ROOT = Path(__file__).parent.parent
CONFIG_PATH = ROOT / "config.json"

with open(CONFIG_PATH) as f:
    CONFIG = json.load(f)

ERSATZTV_URL: str = CONFIG["ersatztv_url"].rstrip("/")
PLAYER_URL: str = CONFIG.get("player_url", "http://localhost:5000").rstrip("/")

BACKUPS_DIR = ROOT / "backups"
BACKUPS_DIR.mkdir(exist_ok=True)

# Caches populated by the fetcher modules.
epg_cache = {"channels": [], "programmes": [], "last_update": None}
weather_cache = {"data": None, "hourly": None, "daily": None, "last_fetch": 0}
news_cache = {"data": None, "last_fetch": 0}

# Rate limiting bookkeeping for PIN auth.
_login_attempts: dict = {}

# Single lock guarding writes to all three caches. Readers should snapshot
# coupled data (e.g. channels + programmes) under the lock and iterate
# outside it, otherwise a reader can hold the OLD channels list against
# the NEW programmes list and produce inconsistent now-playing snapshots.
cache_lock = threading.Lock()


def reload_from_disk() -> None:
    """Re-read config.json and rebind URL globals.

    Other modules that read `ERSATZTV_URL` / `PLAYER_URL` via the module
    (i.e. `_state.ERSATZTV_URL`) will see the new values; modules that
    captured the values at import time would not.
    """
    global ERSATZTV_URL, PLAYER_URL
    with open(CONFIG_PATH) as f:
        new = json.load(f)
    CONFIG.clear()
    CONFIG.update(new)
    ERSATZTV_URL = CONFIG["ersatztv_url"].rstrip("/")
    PLAYER_URL = CONFIG.get("player_url", "http://localhost:5000").rstrip("/")
