import re
import uuid
from datetime import datetime, timezone

import pytest
from fastapi import Response
from fastapi.testclient import TestClient
from sqlalchemy import func, select

from app.admin import auth, views
from app.admin.auth import LoginThrottle, SessionStore
from app.admin.router import router as auth_router
from app.core.config import settings
from app.main import app
from app.models.admin_audit_log import AdminAuditLog
from app.models.enums import OnChainStatus, UserRole
from app.models.message import Message
from tests.conftest import ADMIN_EMAIL, ADMIN_PASSWORD, ADMIN_SECRET, login
from tests.test_admin_resources import add_batch, add_event, add_price, add_user, post


def _routes():
    """(path with a real uuid filled in, methods) for every route of the admin routers."""
    for router in (auth_router, views.router):
        for route in router.routes:
            path = getattr(route, "path", None)
            if path:
                yield re.sub(r"\{obj_id\}", str(uuid.uuid4()), path), set(route.methods)


def _login_form(client) -> tuple[str, dict]:
    page = client.get("/admin/login")
    token = re.search(r'name="csrf_token" value="([^"]+)"', page.text).group(1)
    return token, {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD, "csrf_token": token}


# --- CSRF / authentication on every state-changing route ----------------------------------------

def test_the_route_table_has_state_changing_routes_to_check():
    posts = [p for p, m in _routes() if "POST" in m]
    assert len(posts) >= 10  # guards against this whole class of test silently checking nothing


def test_every_post_route_requires_login(client):
    for path, methods in _routes():
        if "POST" in methods and path != "/admin/login":
            response = client.post(path, data={"csrf_token": "x"})
            assert response.status_code == 303 and response.headers["location"] == "/admin/login", path


def test_every_post_route_requires_a_csrf_token_once_logged_in(admin_client):
    for path, methods in _routes():
        if "POST" in methods and path != "/admin/login":
            assert admin_client.post(path).status_code == 403, path
            assert admin_client.post(path, data={"csrf_token": "forged"}).status_code == 403, path
            assert admin_client.post(path, headers={"X-CSRF-Token": "forged"}).status_code == 403, path


def test_state_changing_actions_are_not_reachable_by_get(admin_client):
    for path, methods in _routes():
        # Form pages (/new, /edit, /login) legitimately answer GET at the same path as their POST.
        if "POST" in methods and not path.endswith(("/new", "/edit", "/login")):
            assert admin_client.get(path).status_code in (404, 405), path


def test_get_requests_never_modify_data(admin_client, db_session_factory):
    with db_session_factory() as s:
        ana = add_user(s)
        batch = add_batch(s, ana)
        add_event(s, batch, ana, OnChainStatus.FAILED)
        add_price(s, add_user(s, "Sam Supplier", UserRole.SUPPLIER))
        s.commit()

    def snapshot():
        with db_session_factory() as s:
            return [(u.id, u.is_active, u.full_name) for u in s.scalars(select(auth_user()))]

    from app.models.custody_event import ChainOfCustodyEvent

    def auth_user():
        from app.models.user import User

        return User

    before = snapshot()
    for path, methods in _routes():
        if "GET" in methods and not path.endswith("/print"):
            admin_client.get(path)
    assert snapshot() == before
    with db_session_factory() as s:
        assert {e.on_chain_status for e in s.scalars(select(ChainOfCustodyEvent))} == {OnChainStatus.FAILED}


# --- same-origin enforcement -------------------------------------------------------------------------

@pytest.mark.parametrize("headers", [
    {"Origin": "https://evil.example"},
    {"Origin": "null"},
    {"Origin": "http://testserver.evil.example"},
    {"Sec-Fetch-Site": "cross-site"},
    {"Sec-Fetch-Site": "same-site"},   # a sibling subdomain / other local port is same-site, not same-origin
])
def test_cross_origin_state_changes_are_blocked(admin_client, db_session_factory, headers):
    with db_session_factory() as s:
        user = add_user(s)
        s.commit()
        uid = user.id
    assert post(admin_client, f"/admin/users/{uid}/delete", headers=headers).status_code == 403
    assert post(admin_client, f"/admin/users/{uid}/toggle-active", headers=headers).status_code == 403
    assert post(admin_client, "/admin/logout", headers=headers).status_code == 403
    assert admin_client.get("/admin").status_code == 200        # still signed in
    with db_session_factory() as s:
        assert s.scalar(select(func.count()).select_from(auth_user_model())) == 1


def auth_user_model():
    from app.models.user import User

    return User


@pytest.mark.parametrize("headers", [
    {},
    {"Origin": "http://testserver"},
    {"Origin": "https://testserver"},   # scheme differs behind a TLS-terminating proxy; the host is what matters
    {"Sec-Fetch-Site": "same-origin"},
    {"Sec-Fetch-Site": "none"},
])
def test_same_origin_requests_are_accepted(admin_client, headers):
    assert post(admin_client, "/admin/logout", headers=headers).status_code == 303


def test_cross_origin_login_posts_are_blocked(client, db_session_factory):
    _, form = _login_form(client)
    for headers in ({"Origin": "https://evil.example"}, {"Sec-Fetch-Site": "cross-site"}):
        assert client.post("/admin/login", data=form, headers=headers).status_code == 403
    assert client.get("/admin").status_code == 303              # never signed in
    assert client.post("/admin/login", data=form, headers={"Origin": "http://testserver"}).status_code == 303


# --- CORS ---------------------------------------------------------------------------------------------------

ATTACKER = {"Origin": "https://evil.example"}


def test_admin_responses_carry_no_cors_headers(admin_client):
    for path in ("/admin", "/admin/login", "/admin/users", "/admin/static/admin.css", "/admin/nope"):
        response = admin_client.get(path, headers=ATTACKER)
        assert not [h for h in response.headers if h.lower().startswith("access-control-")], path


def test_admin_preflights_are_refused(client):
    response = client.options("/admin/users", headers={**ATTACKER, "Access-Control-Request-Method": "POST"})
    assert response.status_code == 405
    assert not [h for h in response.headers if h.lower().startswith("access-control-")]


def test_the_apis_cors_behaviour_is_unchanged(client):
    plain = client.get("/health", headers=ATTACKER)
    assert plain.status_code == 200 and "access-control-allow-origin" in plain.headers
    preflight = client.options("/auth/login", headers={**ATTACKER, "Access-Control-Request-Method": "POST"})
    assert preflight.status_code == 200 and "access-control-allow-origin" in preflight.headers


# --- security headers ----------------------------------------------------------------------------------------

EXPECTED_HEADERS = {
    "cache-control": "no-store",
    "x-frame-options": "DENY",
    "x-content-type-options": "nosniff",
    "referrer-policy": "no-referrer",
    "cross-origin-opener-policy": "same-origin",
    "cross-origin-resource-policy": "same-origin",
}


def test_security_headers_on_pages_assets_and_errors(admin_client):
    for path in ("/admin", "/admin/login", "/admin/users/print", "/admin/static/admin.css", "/admin/nope"):
        headers = admin_client.get(path).headers
        for name, value in EXPECTED_HEADERS.items():
            assert headers.get(name) == value, (path, name)
        csp = headers["content-security-policy"]
        assert "default-src 'self'" in csp and "object-src 'none'" in csp and "frame-ancestors 'none'" in csp
        assert "camera=()" in headers["permissions-policy"]


def test_hsts_and_secure_cookies_only_in_production(client, monkeypatch):
    assert "strict-transport-security" not in client.get("/admin/login").headers
    _, form = _login_form(client)
    assert "secure" not in client.post("/admin/login", data=form).headers["set-cookie"].lower()

    monkeypatch.setattr(settings, "ENVIRONMENT", "production")
    page = TestClient(app, follow_redirects=False).get("/admin/login")  # fresh client: not signed in
    assert page.headers["strict-transport-security"].startswith("max-age=31536000")

    # Production cookies are marked Secure, so the (plain-HTTP) test client would not send them
    # back; check the flags on the Set-Cookie headers themselves instead.
    login_csrf = next(c for c in page.headers.get_list("set-cookie") if c.startswith(auth.LOGIN_CSRF_COOKIE))
    session_response = Response()
    auth.set_session_cookie(session_response, auth.session_store.create())
    for cookie in (login_csrf, session_response.headers["set-cookie"]):
        lowered = cookie.lower()
        assert "secure" in lowered and "httponly" in lowered and "samesite=strict" in lowered, cookie
        assert "path=/admin" in lowered


def test_api_responses_do_not_get_admin_headers(client):
    headers = client.get("/health").headers
    assert "content-security-policy" not in headers and "x-frame-options" not in headers


# --- error handling: no leaks, no stack traces --------------------------------------------------------------------

def test_admin_errors_are_html_pages_not_json(admin_client):
    missing = admin_client.get("/admin/does-not-exist")
    assert missing.status_code == 404 and "text/html" in missing.headers["content-type"]
    assert "That page does not exist." in missing.text and "detail" not in missing.text.lower().replace("details", "")
    not_allowed = admin_client.get("/admin/logout")
    assert not_allowed.status_code == 405 and "text/html" in not_allowed.headers["content-type"]


def test_validation_errors_do_not_echo_submitted_values(client):
    secret = "P" * 2000                                          # exceeds the password field's limit
    response = client.post("/admin/login", data={"email": "a@example.com", "password": secret, "csrf_token": "x"})
    assert response.status_code == 422 and "text/html" in response.headers["content-type"]
    assert secret not in response.text and "PPPP" not in response.text
    assert "Some of the submitted values were not valid." in response.text


def test_the_apis_error_format_is_unchanged(client):
    missing = client.get("/definitely-not-a-route")
    assert missing.status_code == 404 and missing.json() == {"detail": "Not Found"}
    invalid = client.post("/auth/login", data={})
    assert invalid.status_code == 422 and isinstance(invalid.json()["detail"], list)


def test_unhandled_errors_on_admin_are_generic_and_logged(db_session_factory, monkeypatch, caplog):
    with db_session_factory() as s:
        user = add_user(s)
        s.commit()
        uid = user.id

    async def boom(*args, **kwargs):
        raise RuntimeError("password=hunter2 postgresql://user:dbpass@host/db")

    monkeypatch.setattr(views, "_load_related", boom)
    client = TestClient(app, follow_redirects=False, raise_server_exceptions=False)
    login(client)
    response = client.get(f"/admin/users/{uid}")
    assert response.status_code == 500 and "text/html" in response.headers["content-type"]
    assert "An unexpected error occurred" in response.text
    for leaked in ("hunter2", "dbpass", "RuntimeError", "Traceback", "boom", "views.py"):
        assert leaked not in response.text
    assert response.headers["content-security-policy"] and response.headers["cache-control"] == "no-store"
    assert "unhandled error on GET" in caplog.text            # the detail goes to the server log instead


def test_unhandled_errors_elsewhere_keep_the_default_plain_response(monkeypatch):
    async def explode():
        raise RuntimeError("secret internals")

    app.add_api_route("/__test_boom", explode)
    try:
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/__test_boom")
        assert response.status_code == 500 and response.text == "Internal Server Error"
        assert "secret internals" not in response.text
    finally:
        app.router.routes.pop()


# --- sensitive-data exposure -----------------------------------------------------------------------------------------

def test_no_secret_from_the_environment_appears_in_any_page(admin_client, db_session_factory, monkeypatch):
    planted = {
        "SECRET_KEY": "JWT-SIGNING-KEY-should-never-render",
        "SERVICE_WALLET_PRIVATE_KEY": "0xWALLET-PRIVATE-KEY-should-never-render",
        "WEB3_PROVIDER_URL": "https://rpc.example/v3/RPC-API-KEY-should-never-render",
        "DATABASE_URL": "postgresql+asyncpg://dbuser:DB-PASSWORD-should-never-render@host/db",
    }
    for name, value in planted.items():
        monkeypatch.setattr(settings, name, value)

    with db_session_factory() as s:
        ana, sam = add_user(s), add_user(s, "Sam Supplier", UserRole.SUPPLIER)
        batch = add_batch(s, ana)
        event = add_event(s, batch, ana, OnChainStatus.FAILED, payload={"note": "x"})
        price = add_price(s, sam)
        msg = Message(id=uuid.uuid4(), sender_id=ana.id, recipient_id=sam.id, body="hi", occurred_at=datetime.now(timezone.utc))
        s.add(msg)
        s.commit()
        ids = {"users": ana.id, "prices": price.id, "batches": batch.id, "events": event.id, "messages": msg.id}
        audit_row = s.scalar(select(AdminAuditLog))

    paths = ["/admin", "/admin/users/new", "/admin/prices/new", "/admin/nope", "/admin/static/admin.js",
             "/admin/static/admin.css", "/admin/static/print.css", "/admin/audit", f"/admin/audit/{audit_row.id}"]
    for key, rid in ids.items():
        paths += [f"/admin/{key}", f"/admin/{key}/{rid}", f"/admin/{key}/print", f"/admin/{key}/{rid}/print"]
        if key in ("users", "prices"):
            paths.append(f"/admin/{key}/{rid}/edit")

    forbidden = [*planted.values(), ADMIN_PASSWORD, ADMIN_SECRET, "$2b$", "hashed_password"]
    for path in paths:
        response = admin_client.get(path)
        assert response.status_code == 200 or path.endswith("/nope"), path
        blob = response.text + str(dict(response.headers))
        for secret in forbidden:
            assert secret not in blob, (path, secret)
    for cookie in admin_client.cookies.jar:
        assert ADMIN_SECRET not in cookie.value and ADMIN_PASSWORD not in cookie.value


def test_login_page_never_contains_credentials_or_secrets(client):
    html = client.get("/admin/login").text
    assert ADMIN_PASSWORD not in html and ADMIN_SECRET not in html and ADMIN_EMAIL not in html


# --- brute force & memory ---------------------------------------------------------------------------------------------

def test_lockout_bounds_the_audit_rows_an_attacker_can_create(client, db_session_factory):
    for _ in range(auth.MAX_FAILED_LOGINS + 5):
        login(client, password="wrong")
    with db_session_factory() as s:
        failed = s.scalar(select(func.count()).select_from(AdminAuditLog).where(AdminAuditLog.action == "login_failed"))
    assert failed == auth.MAX_FAILED_LOGINS


def test_expired_sessions_are_purged_when_new_ones_are_created(monkeypatch):
    now = [1000.0]
    store = SessionStore(clock=lambda: now[0])
    old = store.create()
    now[0] += settings.ADMIN_SESSION_IDLE_MINUTES * 60 + 1
    fresh = store.create()
    assert set(store._sessions) == {fresh.sid} and old.sid not in store._sessions


def test_absolute_lifetime_also_purges(monkeypatch):
    now = [1000.0]
    store = SessionStore(clock=lambda: now[0])
    first = store.create()
    for _ in range(20):  # stays active but crosses the absolute limit
        now[0] += (settings.ADMIN_SESSION_IDLE_MINUTES - 1) * 60
        store._sessions[first.sid].last_seen = now[0]
    second = store.create()
    assert set(store._sessions) == {second.sid}


def test_stale_login_failures_are_purged():
    now = [1000.0]
    throttle = LoginThrottle(clock=lambda: now[0])
    for i in range(50):
        throttle.record_failure(f"10.0.0.{i}")
    now[0] += auth.LOCKOUT_SECONDS + 1
    throttle.record_failure("10.9.9.9")
    assert list(throttle._failures) == ["10.9.9.9"]
