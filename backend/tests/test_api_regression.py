"""The admin UI was added to an existing API. These tests pin the API's behaviour
(so the admin work cannot have changed it) and prove that real app accounts and
the admin are completely separate identities."""

import uuid

import pytest
from sqlalchemy import select

from app.admin import auth
from app.core.config import settings
from app.models.custody_event import ChainOfCustodyEvent
from app.models.enums import OnChainStatus
from app.models.user import User
from tests.conftest import ADMIN_PASSWORD, login
from tests.test_admin_resources import add_batch, add_event, add_user

APP_PASSWORD = "app-user-password-1"


def register(client, email="farmer@example.com", role="farmer", password=APP_PASSWORD, name="App User"):
    response = client.post("/auth/register", json={"email": email, "password": password, "full_name": name, "role": role})
    assert response.status_code == 201, response.text
    return response.json()


def token_for(client, email="farmer@example.com", password=APP_PASSWORD) -> dict:
    response = client.post("/auth/login", data={"username": email, "password": password})
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


# --- the existing API still behaves as before ------------------------------------------------------

def test_health_endpoint(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_register_login_and_profile_flow(client):
    created = register(client)
    assert created["email"] == "farmer@example.com" and created["role"] == "farmer" and created["is_active"] is True
    assert "hashed_password" not in created and "password" not in created

    headers = token_for(client)
    me = client.get("/users/me", headers=headers)
    assert me.status_code == 200 and me.json()["id"] == created["id"]

    patched = client.patch("/users/me", headers=headers, json={"municipality": "Bongao"})
    assert patched.status_code == 200 and patched.json()["municipality"] == "Bongao"


def test_register_rejects_duplicates_and_login_rejects_bad_passwords(client):
    register(client)
    assert client.post("/auth/register", json={"email": "farmer@example.com", "password": "x", "full_name": "Dup",
                                                "role": "farmer"}).status_code == 409
    assert client.post("/auth/login", data={"username": "farmer@example.com", "password": "wrong"}).status_code == 401
    assert client.post("/auth/login", data={"username": "nobody@example.com", "password": APP_PASSWORD}).status_code == 401


def test_api_requires_a_bearer_token(client):
    assert client.get("/users/me").status_code == 401
    assert client.get("/prices").status_code == 401
    assert client.get("/users/me", headers={"Authorization": "Bearer not-a-token"}).status_code == 401


def test_price_records_follow_the_role_rules(client):
    register(client, "farmer@example.com", "farmer")
    register(client, "sup@example.com", "supplier", name="Sam Supplier")
    payload = {"species": "Kappaphycus", "price_per_kg": "33.50", "effective_date": "2026-09-18"}
    assert client.post("/prices", json=payload, headers=token_for(client)).status_code == 403
    created = client.post("/prices", json=payload, headers=token_for(client, "sup@example.com"))
    assert created.status_code == 201 and created.json()["currency"] == "PHP"
    listed = client.get("/prices", headers=token_for(client))
    assert [p["species"] for p in listed.json()] == ["Kappaphycus"]


def test_deactivated_users_lose_api_access(client, db_session_factory):
    register(client)
    headers = token_for(client)
    with db_session_factory() as s:
        user = s.scalar(select(User))
        user.is_active = False
        s.commit()
    assert client.get("/users/me", headers=headers).status_code == 401


def test_public_retry_anchor_endpoint_is_unchanged(client, db_session_factory, monkeypatch):
    queued = []

    async def fake_anchor(event_id):
        queued.append(event_id)

    monkeypatch.setattr("app.api.routes.custody_events.anchor_event", fake_anchor)
    register(client)
    headers = token_for(client)
    with db_session_factory() as s:
        ana = add_user(s, email="someone@example.com")
        failed = add_event(s, add_batch(s, ana), ana, OnChainStatus.FAILED)
        done = add_event(s, add_batch(s, ana), ana, OnChainStatus.ANCHORED)
        s.commit()
        failed_id, done_id = failed.id, done.id

    already = client.post(f"/custody-events/{done_id}/retry-anchor", headers=headers)
    assert already.status_code == 202 and already.json() == {"status": "already anchored"}
    queued_response = client.post(f"/custody-events/{failed_id}/retry-anchor", headers=headers)
    assert queued_response.status_code == 202 and queued_response.json() == {"status": "retry queued"}
    assert queued == [failed_id]
    assert client.post(f"/custody-events/{uuid.uuid4()}/retry-anchor", headers=headers).status_code == 404
    with db_session_factory() as s:
        assert s.get(ChainOfCustodyEvent, failed_id).on_chain_status == OnChainStatus.PENDING


# --- app accounts and the admin are separate identities ---------------------------------------------------

def test_a_real_registered_user_cannot_reach_the_admin(client):
    register(client)
    headers = token_for(client)
    for url in ("/admin", "/admin/users", "/admin/audit", "/admin/users/print"):
        response = client.get(url, headers=headers)
        assert response.status_code == 303 and response.headers["location"] == "/admin/login", url
    # ...nor by smuggling the token in as the admin session cookie.
    client.cookies.set(auth.SESSION_COOKIE, headers["Authorization"].split()[1], path="/admin")
    assert client.get("/admin").status_code == 303


@pytest.mark.parametrize("role", ["farmer", "supplier", "buyer"])
def test_no_app_role_grants_admin_access(client, role):
    register(client, f"{role}@example.com", role)
    headers = token_for(client, f"{role}@example.com")
    assert client.get("/admin", headers=headers).status_code == 303
    assert login(client, f"{role}@example.com", APP_PASSWORD).status_code == 401


def test_an_app_account_with_the_admins_email_gains_nothing(client, db_session_factory, monkeypatch):
    boss = "boss@example.com"  # the app's own email validation rejects the reserved .test test address
    monkeypatch.setattr(settings, "ADMIN_EMAIL", boss)
    register(client, boss, "buyer", password="attacker-chosen-pw")
    headers = token_for(client, boss, "attacker-chosen-pw")
    assert client.get("/admin", headers=headers).status_code == 303
    assert login(client, boss, "attacker-chosen-pw").status_code == 401   # not the admin password
    assert login(client, boss, ADMIN_PASSWORD).status_code == 303          # the env password still works


def test_the_admin_session_does_not_authenticate_api_calls(admin_client):
    assert admin_client.get("/admin").status_code == 200
    assert admin_client.get("/users/me").status_code == 401
    assert admin_client.get("/prices").status_code == 401


def test_admin_login_does_not_depend_on_the_users_table(client, db_session_factory):
    with db_session_factory() as s:
        assert s.scalar(select(User)) is None            # no users at all
    assert login(client).status_code == 303
    assert client.get("/admin").status_code == 200


# --- anchoring: what the admin's "Retry anchor" ultimately triggers -----------------------------------------------

@pytest.fixture
def anchor_env(db_session_factory, monkeypatch):
    """Points chain_anchor at the throwaway DB and a fake chain."""
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
    from sqlalchemy.pool import NullPool

    from app.services import chain_anchor

    engine = create_async_engine(str(db_session_factory.kw["bind"].url).replace("sqlite:", "sqlite+aiosqlite:"), poolclass=NullPool)
    monkeypatch.setattr(chain_anchor, "AsyncSessionLocal", async_sessionmaker(engine, expire_on_commit=False))
    calls = []

    def fake_chain(event_id, batch_id, data_hash):
        calls.append(event_id)
        return {"tx_hash": "0x" + "ab" * 32, "block_number": 1234}

    monkeypatch.setattr(chain_anchor, "record_event_on_chain", fake_chain)
    yield chain_anchor, calls
    import asyncio
    asyncio.run(engine.dispose())


def _event(factory, status):
    with factory() as s:
        ana = add_user(s)
        event = add_event(s, add_batch(s, ana), ana, status)
        s.commit()
        return event.id


def test_anchor_event_anchors_a_pending_event(anchor_env, db_session_factory):
    import asyncio

    chain_anchor, calls = anchor_env
    eid = _event(db_session_factory, OnChainStatus.PENDING)
    asyncio.run(chain_anchor.anchor_event(eid))
    with db_session_factory() as s:
        event = s.get(ChainOfCustodyEvent, eid)
        assert event.on_chain_status == OnChainStatus.ANCHORED
        assert event.on_chain_tx_hash == "0x" + "ab" * 32 and event.on_chain_block_number == 1234
    assert calls == [eid]


def test_anchor_event_marks_failures_and_ignores_non_pending_or_missing_events(anchor_env, db_session_factory, monkeypatch):
    import asyncio

    chain_anchor, calls = anchor_env

    def broken(*args):
        raise RuntimeError("rpc down")

    monkeypatch.setattr(chain_anchor, "record_event_on_chain", broken)
    eid = _event(db_session_factory, OnChainStatus.PENDING)
    asyncio.run(chain_anchor.anchor_event(eid))
    with db_session_factory() as s:
        assert s.get(ChainOfCustodyEvent, eid).on_chain_status == OnChainStatus.FAILED

    monkeypatch.setattr(chain_anchor, "record_event_on_chain", lambda *a: calls.append("called") or {})
    asyncio.run(chain_anchor.anchor_event(eid))                      # FAILED is not PENDING: untouched
    asyncio.run(chain_anchor.anchor_event(uuid.uuid4()))             # unknown id: no error
    assert calls == []


def test_admin_retry_then_background_anchor_recovers_a_failed_event(admin_client, anchor_env, db_session_factory, monkeypatch):
    """End to end: failed event -> admin clicks Retry -> status resets -> background task anchors it."""
    from app.admin import views
    from tests.test_admin_resources import post

    chain_anchor, calls = anchor_env
    monkeypatch.setattr(views, "anchor_event", chain_anchor.anchor_event)   # run the real task
    eid = _event(db_session_factory, OnChainStatus.FAILED)

    response = post(admin_client, f"/admin/events/{eid}/retry-anchor")
    assert response.status_code == 303
    assert calls == [eid]
    with db_session_factory() as s:
        assert s.get(ChainOfCustodyEvent, eid).on_chain_status == OnChainStatus.ANCHORED
    assert "Anchored" in admin_client.get(f"/admin/events/{eid}").text
