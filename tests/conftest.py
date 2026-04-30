"""Shared pytest fixtures."""

import pytest

from tv_guide import _state, app as flask_app


@pytest.fixture
def client(monkeypatch):
    """Flask test client with a deterministic admin PIN.

    The app object is module-level (gunicorn loads it that way), so we
    monkeypatch CONFIG rather than recreating the app per test.
    """
    flask_app.config["TESTING"] = True
    flask_app.config["SECRET_KEY"] = "test-secret-key"
    monkeypatch.setitem(
        _state.CONFIG,
        "admin",
        {"pin": "secure-test-pin", "session_timeout_minutes": 60},
    )
    with flask_app.test_client() as c:
        yield c
