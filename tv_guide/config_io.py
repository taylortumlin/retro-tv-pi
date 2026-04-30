"""Config file IO: atomic write + rolling backups."""

from __future__ import annotations

import json
import shutil
import time
from datetime import datetime

from . import _state


def backup_config() -> str:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = _state.BACKUPS_DIR / f"config_{ts}.json"
    shutil.copy2(_state.CONFIG_PATH, dest)
    # Keep last 20 backups.
    backups = sorted(_state.BACKUPS_DIR.glob("config_*.json"))
    for old in backups[:-20]:
        old.unlink()
    return dest.name


def atomic_write_config(data: dict) -> None:
    tmp = _state.CONFIG_PATH.with_suffix(".tmp")
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")
    tmp.rename(_state.CONFIG_PATH)


def check_login_rate_limit(ip: str) -> bool:
    now = time.time()
    rec = _state._login_attempts.get(ip, {"count": 0, "last": 0})
    if rec["count"] >= 5 and now - rec["last"] < 300:
        return False
    return True


def record_failed_login(ip: str) -> None:
    now = time.time()
    rec = _state._login_attempts.get(ip, {"count": 0, "last": 0})
    if now - rec["last"] > 300:
        rec = {"count": 0, "last": now}
    rec["count"] += 1
    rec["last"] = now
    _state._login_attempts[ip] = rec


def clear_login_attempts(ip: str) -> None:
    _state._login_attempts.pop(ip, None)
