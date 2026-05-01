"""Cache-lock regression tests.

The snapshot helpers in tv_guide.epg must return a coupled (channels,
programmes) view from the same EPG fetch. Without this the API can
match new programmes against old channel ids during a refresh and
silently produce empty now-playing rows.
"""

import threading
import time

import pytest

from tv_guide import _state
from tv_guide.epg import snapshot_cache


@pytest.fixture
def seeded_cache(monkeypatch):
    """Install a deterministic EPG snapshot, restore on teardown."""
    monkeypatch.setitem(_state.CONFIG, "channels", [])  # no filtering
    saved = (
        list(_state.epg_cache.get("channels", [])),
        list(_state.epg_cache.get("programmes", [])),
        _state.epg_cache.get("last_update"),
    )
    with _state.cache_lock:
        _state.epg_cache["channels"] = [{"id": "v1", "number": "1", "name": "Ch 1"}]
        _state.epg_cache["programmes"] = [
            {"channel_id": "v1", "start_ts": 0, "stop_ts": 100, "title": "v1 prog"}
        ]
        _state.epg_cache["last_update"] = "v1"
    yield
    with _state.cache_lock:
        _state.epg_cache["channels"] = saved[0]
        _state.epg_cache["programmes"] = saved[1]
        _state.epg_cache["last_update"] = saved[2]


def test_snapshot_returns_coupled_view(seeded_cache):
    channels, programmes, _ = snapshot_cache()
    assert len(channels) == 1
    assert programmes[0]["channel_id"] == channels[0]["id"]


def test_snapshot_is_atomic_under_concurrent_writes(seeded_cache):
    """Spawn a writer that swaps to v2 while a reader takes snapshots.

    Every snapshot must have channels and programmes whose channel ids
    line up. If the lock is wrong, eventually a snapshot will pair v1
    channels with v2 programmes (or vice versa) and the assertion fires.
    """
    stop = threading.Event()
    errors = []

    def writer():
        n = 0
        while not stop.is_set():
            n += 1
            tag = f"v{n}"
            new_channels = [{"id": tag, "number": "1", "name": tag}]
            new_progs = [
                {"channel_id": tag, "start_ts": 0, "stop_ts": 100, "title": tag}
            ]
            with _state.cache_lock:
                _state.epg_cache["channels"] = new_channels
                _state.epg_cache["programmes"] = new_progs
            time.sleep(0)  # yield

    def reader():
        for _ in range(2000):
            channels, programmes, _ = snapshot_cache()
            if channels and programmes:
                ids = {c["id"] for c in channels}
                for p in programmes:
                    if p["channel_id"] not in ids:
                        errors.append((channels, programmes))
                        return

    w = threading.Thread(target=writer, daemon=True)
    r = threading.Thread(target=reader, daemon=True)
    w.start()
    r.start()
    r.join(timeout=5)
    stop.set()
    w.join(timeout=2)

    assert not errors, f"Torn snapshot detected: {errors[:1]}"
