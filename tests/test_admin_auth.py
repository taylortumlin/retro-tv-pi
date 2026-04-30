"""Auth-chain regression tests covering Phase 2 hardening."""

import time as _time

from tv_guide import _state


def test_login_rejects_wrong_pin(client):
    r = client.post("/admin/api/auth/login", json={"pin": "nope"})
    assert r.status_code == 401


def test_login_accepts_correct_pin(client):
    r = client.post("/admin/api/auth/login", json={"pin": "secure-test-pin"})
    assert r.status_code == 200
    assert r.get_json()["ok"] is True


def test_login_no_default_pin_fallback(client, monkeypatch):
    # No `pin` key in admin config -> must NOT silently accept "1234".
    monkeypatch.setitem(_state.CONFIG, "admin", {"session_timeout_minutes": 60})
    r = client.post("/admin/api/auth/login", json={"pin": "1234"})
    assert r.status_code in (401, 500)


def test_pin_compare_uses_constant_time():
    import tv_guide.admin as adm
    src = open(adm.__file__).read()
    assert "hmac.compare_digest" in src, "PIN compare must use hmac.compare_digest"


def test_get_config_strips_admin_pin(client):
    client.post("/admin/api/auth/login", json={"pin": "secure-test-pin"})
    r = client.get("/admin/api/config")
    assert r.status_code == 200
    body = r.get_json()
    assert "admin" in body
    assert "pin" not in body["admin"], "PIN must never leave the server"


def test_session_ts_refreshes_on_use(client):
    client.post("/admin/api/auth/login", json={"pin": "secure-test-pin"})
    with client.session_transaction() as sess:
        original_ts = sess["admin_ts"]
    _time.sleep(0.05)
    client.get("/admin/api/status")
    with client.session_transaction() as sess:
        assert sess["admin_ts"] > original_ts


def test_form_post_to_admin_rejected(client):
    client.post("/admin/api/auth/login", json={"pin": "secure-test-pin"})
    r = client.post(
        "/admin/api/services/restart/tv-guide",
        data="svc=tv-guide",
        content_type="application/x-www-form-urlencoded",
    )
    assert r.status_code == 415


def test_restore_rejects_non_config_filename(client):
    client.post("/admin/api/auth/login", json={"pin": "secure-test-pin"})
    r = client.post("/admin/api/config/restore/evil.json")
    assert r.status_code == 400
