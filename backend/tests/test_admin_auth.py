import re
from uuid import uuid4

import pytest
from itsdangerous import URLSafeSerializer
from pydantic import ValidationError

from app.admin import auth
from app.core.config import Settings, settings
from app.core.security import create_access_token
from tests.conftest import ADMIN_EMAIL, ADMIN_PASSWORD, ADMIN_SECRET, login

# --- login -----------------------------------------------------------------

def test_login_page_renders(client):
    response = client.get("/admin/login")
    assert response.status_code == 200
    assert 'name="csrf_token"' in response.text
    assert 'type="password"' in response.text


def test_correct_login_redirects_and_sets_secure_cookie(client):
    response = login(client)
    assert response.status_code == 303
    assert response.headers["location"] == "/admin"
    cookie = response.headers["set-cookie"].lower()
    assert f"{auth.SESSION_COOKIE}=" in cookie
    assert "httponly" in cookie
    assert "samesite=strict" in cookie
    assert "path=/admin" in cookie
    assert client.get("/admin").status_code == 200


def test_email_is_case_insensitive_but_password_is_not(client):
    assert login(client, email=ADMIN_EMAIL.upper()).status_code == 303
    client.cookies.clear()
    assert login(client, password=ADMIN_PASSWORD.upper()).status_code == 401


@pytest.mark.parametrize(
    ("email", "password"),
    [(ADMIN_EMAIL, "wrong"), ("other@example.test", ADMIN_PASSWORD), ("", ""), (ADMIN_EMAIL, "")],
)
def test_invalid_login_is_rejected(client, email, password):
    response = login(client, email=email, password=password)
    assert response.status_code == 401
    assert "Invalid email or password" in response.text
    assert auth.SESSION_COOKIE not in response.headers.get("set-cookie", "")
    assert client.get("/admin").status_code == 303


def test_login_without_csrf_token_is_rejected(client):
    client.get("/admin/login")
    response = client.post("/admin/login", data={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
    assert response.status_code == 403
    assert client.get("/admin").status_code == 303


def test_login_csrf_token_must_match_cookie(client):
    client.get("/admin/login")
    _, forged = auth.new_login_csrf()  # valid HMAC, but for a nonce the browser never got
    response = client.post(
        "/admin/login", data={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD, "csrf_token": forged}
    )
    assert response.status_code == 403


def test_repeated_failures_lock_out_even_correct_password(client):
    for _ in range(auth.MAX_FAILED_LOGINS):
        assert login(client, password="wrong").status_code == 401
    assert login(client).status_code == 429
    assert client.get("/admin").status_code == 303


def test_lockout_expires(client, monkeypatch):
    now = [1000.0]
    monkeypatch.setattr(auth.login_throttle, "_clock", lambda: now[0])
    for _ in range(auth.MAX_FAILED_LOGINS):
        login(client, password="wrong")
    assert login(client).status_code == 429
    now[0] += auth.LOCKOUT_SECONDS + 1
    assert login(client).status_code == 303


def test_login_page_redirects_when_already_signed_in(admin_client):
    response = admin_client.get("/admin/login")
    assert response.status_code == 303
    assert response.headers["location"] == "/admin"


def test_login_rotates_session_and_destroys_the_old_one(client):
    login(client)
    old_cookie = client.cookies.get(auth.SESSION_COOKIE)

    # Sign in again while still holding the old session (needs a fresh login CSRF pair).
    nonce, token = auth.new_login_csrf()
    client.cookies.set(auth.LOGIN_CSRF_COOKIE, nonce, path="/admin")
    response = client.post(
        "/admin/login", data={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD, "csrf_token": token}
    )
    assert response.status_code == 303
    assert client.cookies.get(auth.SESSION_COOKIE) != old_cookie

    client.cookies.set(auth.SESSION_COOKIE, old_cookie, path="/admin")
    assert client.get("/admin").status_code == 303  # old session no longer valid


# --- protected routes --------------------------------------------------------

def test_dashboard_requires_login(client):
    response = client.get("/admin")
    assert response.status_code == 303
    assert response.headers["location"] == "/admin/login"


def test_admin_pages_send_security_headers(admin_client):
    response = admin_client.get("/admin")
    assert response.headers["cache-control"] == "no-store"
    assert response.headers["x-frame-options"] == "DENY"
    assert "frame-ancestors 'none'" in response.headers["content-security-policy"]


def test_admin_routes_are_not_in_openapi(client):
    paths = client.get("/openapi.json").json()["paths"]
    assert not [p for p in paths if p.startswith("/admin")]


def test_admin_disabled_when_not_configured(client, monkeypatch):
    monkeypatch.setattr(settings, "ADMIN_EMAIL", None)
    monkeypatch.setattr(settings, "ADMIN_PASSWORD", None)
    monkeypatch.setattr(settings, "ADMIN_SESSION_SECRET", None)
    assert client.get("/admin/login").status_code == 503
    assert client.post("/admin/login", data={"email": "a", "password": "b"}).status_code == 503


# --- authorization: app users are not admins ------------------------------------

def test_app_user_jwt_does_not_grant_admin_access(client):
    token = create_access_token(uuid4())
    response = client.get("/admin", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 303
    assert response.headers["location"] == "/admin/login"


def test_app_user_token_as_cookie_does_not_grant_admin_access(client):
    client.cookies.set(auth.SESSION_COOKIE, create_access_token(uuid4()), path="/admin")
    assert client.get("/admin").status_code == 303


def test_app_user_credentials_cannot_log_in_as_admin(client):
    assert login(client, email="farmer@example.test", password="farmer-password").status_code == 401


def test_forged_cookie_signed_with_wrong_secret_is_rejected(client):
    session = auth.session_store.create()  # a real, live sid...
    forged = URLSafeSerializer("some-other-secret", salt="admin-session").dumps(session.sid)
    client.cookies.set(auth.SESSION_COOKIE, forged, path="/admin")
    assert client.get("/admin").status_code == 303


def test_correctly_signed_cookie_for_unknown_session_is_rejected(client):
    cookie = URLSafeSerializer(ADMIN_SECRET, salt="admin-session").dumps("never-issued")
    client.cookies.set(auth.SESSION_COOKIE, cookie, path="/admin")
    assert client.get("/admin").status_code == 303


# --- logout ------------------------------------------------------------------

def _csrf(client) -> str:
    return re.search(r'name="csrf_token" value="([^"]+)"', client.get("/admin").text).group(1)


def test_logout_invalidates_session_server_side(admin_client):
    stolen_cookie = admin_client.cookies.get(auth.SESSION_COOKIE)
    response = admin_client.post("/admin/logout", data={"csrf_token": _csrf(admin_client)})
    assert response.status_code == 303
    assert response.headers["location"] == "/admin/login"
    assert admin_client.get("/admin").status_code == 303

    # Replaying the old cookie must fail too: the session is gone on the server.
    admin_client.cookies.set(auth.SESSION_COOKIE, stolen_cookie, path="/admin")
    assert admin_client.get("/admin").status_code == 303


def test_logout_requires_csrf_token(admin_client):
    assert admin_client.post("/admin/logout").status_code == 403
    assert admin_client.post("/admin/logout", data={"csrf_token": "nope"}).status_code == 403
    assert admin_client.get("/admin").status_code == 200  # still signed in


def test_logout_accepts_csrf_header(admin_client):
    response = admin_client.post("/admin/logout", headers={"X-CSRF-Token": _csrf(admin_client)})
    assert response.status_code == 303


def test_logout_get_is_not_allowed(admin_client):
    assert admin_client.get("/admin/logout").status_code == 405


def test_logout_when_signed_out_redirects_to_login(client):
    assert client.post("/admin/logout").status_code == 303


# --- session expiry --------------------------------------------------------------

def test_session_expires_after_idle_timeout(client, monkeypatch):
    now = [5000.0]
    monkeypatch.setattr(auth.session_store, "_clock", lambda: now[0])
    assert login(client).status_code == 303
    now[0] += settings.ADMIN_SESSION_IDLE_MINUTES * 60 - 1
    assert client.get("/admin").status_code == 200  # just inside the window
    now[0] += settings.ADMIN_SESSION_IDLE_MINUTES * 60 + 1
    assert client.get("/admin").status_code == 303  # idled out


def test_activity_keeps_session_alive_until_absolute_limit(client, monkeypatch):
    now = [10_000.0]
    monkeypatch.setattr(auth.session_store, "_clock", lambda: now[0])
    assert login(client).status_code == 303

    step = (settings.ADMIN_SESSION_IDLE_MINUTES - 1) * 60
    elapsed = 0
    while elapsed + step < settings.ADMIN_SESSION_MAX_MINUTES * 60:
        now[0] += step
        elapsed += step
        assert client.get("/admin").status_code == 200  # idle timer keeps resetting

    now[0] += step  # crosses the absolute lifetime despite constant activity
    assert client.get("/admin").status_code == 303


# --- secrets & configuration ----------------------------------------------------------

def test_credentials_are_not_rendered_in_any_page(admin_client):
    for page in (admin_client.get("/admin"), admin_client.get("/admin/static/admin.css")):
        assert ADMIN_PASSWORD not in page.text
        assert ADMIN_SECRET not in page.text


def test_failed_login_log_does_not_contain_credentials(client, caplog):
    with caplog.at_level("DEBUG"):
        login(client, email="someone@example.test", password="hunter2-secret")
    assert "hunter2-secret" not in caplog.text
    assert "someone@example.test" not in caplog.text



def _settings(**overrides) -> Settings:
    base = {"ADMIN_EMAIL": "a@b.test", "ADMIN_PASSWORD": "x" * 16, "ADMIN_SESSION_SECRET": "s" * 40, "SECRET_KEY": "test-only-jwt-signing-secret-1234567890"}
    return Settings(_env_file=None, **{**base, **overrides})


def test_partial_admin_config_is_rejected():
    with pytest.raises(ValidationError):
        Settings(_env_file=None, ADMIN_EMAIL="a@b.test")


def test_production_rejects_weak_or_placeholder_admin_config():
    _settings(ENVIRONMENT="production")  # strong values are fine
    for bad in (
        {"ADMIN_PASSWORD": "short"},
        {"ADMIN_SESSION_SECRET": "short-secret"},
        {"ADMIN_PASSWORD": "change-this-password"},
        {"ADMIN_SESSION_SECRET": "change-this-secret"},
        {"ADMIN_EMAIL": "admin@example.com"},
    ):
        with pytest.raises(ValidationError):
            _settings(ENVIRONMENT="production", **bad)


def test_placeholders_are_allowed_in_development():
    _settings(ENVIRONMENT="development", ADMIN_PASSWORD="change-this-password")
