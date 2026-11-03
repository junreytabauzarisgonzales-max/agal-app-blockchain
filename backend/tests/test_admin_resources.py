import uuid
from datetime import date, datetime, timezone

import pytest
from sqlalchemy import func, select

from app.admin import auth, views
from app.admin.resources import FORBIDDEN_COLUMN_MARKERS, RESOURCES
from app.core.security import verify_password
from app.models.batch import HarvestBatch
from app.models.custody_event import ChainOfCustodyEvent
from app.models.enums import BatchStatus, CustodyEventType, OnChainStatus, UserRole
from app.models.message import Message
from app.models.price import PriceRecord
from app.models.user import User
from app.schemas.custody_event import CustodyEventVerification

NOW = datetime(2026, 9, 19, 4, 0, tzinfo=timezone.utc)


# --- seeding helpers -----------------------------------------------------------------

def add_user(s, name="Ana Farmer", role=UserRole.FARMER, email=None, active=True) -> User:
    user = User(
        id=uuid.uuid4(), email=email or f"{name.lower().replace(' ', '.')}@example.com",
        hashed_password="$2b$12$not.a.real.hash.but.long.enough.to.look.like.one.xxxxxxxxxxxxxxx",
        full_name=name, role=role, is_active=active,
    )
    s.add(user)
    s.flush()
    return user


def add_batch(s, farmer: User) -> HarvestBatch:
    batch = HarvestBatch(
        id=uuid.uuid4(), farmer_id=farmer.id, species="Kappaphycus", estimated_weight_kg=120.5,
        harvested_at=NOW, status=BatchStatus.HARVESTED, current_holder_id=farmer.id,
    )
    s.add(batch)
    s.flush()
    return batch


def add_event(s, batch: HarvestBatch, actor: User, chain=OnChainStatus.PENDING, payload=None) -> ChainOfCustodyEvent:
    event = ChainOfCustodyEvent(
        id=uuid.uuid4(), batch_id=batch.id, event_type=CustodyEventType.NOTE_ADDED, actor_id=actor.id,
        actor_role=actor.role, occurred_at=NOW, received_at=NOW, payload=payload or {}, on_chain_status=chain,
    )
    s.add(event)
    s.flush()
    return event


def add_price(s, poster: User, species="Kappaphycus") -> PriceRecord:
    record = PriceRecord(
        id=uuid.uuid4(), species=species, price_per_kg=33.5, posted_by_id=poster.id,
        effective_date=date(2026, 9, 18), notes="dry, grade A",
    )
    s.add(record)
    s.flush()
    return record


def token() -> str:
    (session,) = auth.session_store._sessions.values()
    return auth.csrf_token_for(session)


def post(client, url, data=None, **kwargs):
    return client.post(url, data={**(data or {}), "csrf_token": token()}, **kwargs)


def count(factory, model) -> int:
    with factory() as s:
        return s.scalar(select(func.count()).select_from(model))


USER_FORM = {"full_name": "New Person", "email": "New.Person@Example.com", "role": "buyer", "password": "long-enough-pw", "is_active": "on"}
PRICE_FORM = {"species": "Kappaphycus", "price_per_kg": "33.50", "currency": "php", "effective_date": "2026-09-18",
              "posted_by_email": "sam.supplier@example.com"}


# --- registry safety -----------------------------------------------------------------

def test_no_resource_exposes_a_sensitive_column():
    for res in RESOURCES.values():
        for col in res.columns:
            assert not any(marker in col.name.lower() for marker in FORBIDDEN_COLUMN_MARKERS), (res.key, col.name)
    assert "hashed_password" not in {c.name for c in RESOURCES["users"].columns}


def test_registry_only_covers_real_tables():
    assert {r.model.__tablename__ for r in RESOURCES.values()} == {
        "users", "price_records", "harvest_batches", "custody_events", "messages", "admin_audit_logs",
    }


def test_only_users_and_prices_are_writable():
    writable = {k for k, r in RESOURCES.items() if r.can_create or r.can_edit or r.can_delete}
    assert writable == {"users", "prices"}


# --- authentication & CSRF on every route ------------------------------------------------

@pytest.mark.parametrize("url", ["/admin/users", "/admin/prices", "/admin/batches", "/admin/events", "/admin/messages",
                                 "/admin/users/new", "/admin/prices/new", f"/admin/users/{uuid.uuid4()}"])
def test_pages_require_login(client, url):
    response = client.get(url)
    assert response.status_code == 303
    assert response.headers["location"] == "/admin/login"


@pytest.mark.parametrize("url", ["/admin/users/new", "/admin/prices/new", f"/admin/users/{uuid.uuid4()}/delete",
                                 f"/admin/users/{uuid.uuid4()}/toggle-active", f"/admin/events/{uuid.uuid4()}/verify",
                                 f"/admin/events/{uuid.uuid4()}/retry-anchor"])
def test_mutations_require_login(client, url):
    assert client.post(url, data={"csrf_token": "x"}).status_code == 303


def test_mutations_reject_missing_or_bad_csrf(admin_client, db_session_factory):
    with db_session_factory() as s:
        user = add_user(s)
        batch = add_batch(s, user)
        event = add_event(s, batch, user)
        s.commit()
        uid, eid = user.id, event.id
    urls = ["/admin/users/new", f"/admin/users/{uid}/edit", f"/admin/users/{uid}/delete",
            f"/admin/users/{uid}/toggle-active", "/admin/prices/new", f"/admin/events/{eid}/verify",
            f"/admin/events/{eid}/retry-anchor"]
    for url in urls:
        assert admin_client.post(url, data=USER_FORM).status_code == 403, url
        assert admin_client.post(url, data={**USER_FORM, "csrf_token": "wrong"}).status_code == 403, url
    assert count(db_session_factory, User) == 1  # nothing was created, changed or deleted


# --- lists -----------------------------------------------------------------------------

@pytest.mark.parametrize("key", [k for k in RESOURCES if k != "audit"])  # signing in is itself audited
def test_empty_lists_show_an_empty_state(admin_client, key):
    response = admin_client.get(f"/admin/{key}")
    assert response.status_code == 200
    assert "yet</h2>" in response.text


def test_lists_show_rows_with_related_names_and_links(admin_client, db_session_factory):
    with db_session_factory() as s:
        ana, sam = add_user(s), add_user(s, "Sam Supplier", UserRole.SUPPLIER)
        batch = add_batch(s, ana)
        add_event(s, batch, ana, OnChainStatus.ANCHORED)
        add_price(s, sam)
        s.add(Message(id=uuid.uuid4(), sender_id=ana.id, recipient_id=sam.id, body="TOP SECRET CHAT", occurred_at=NOW))
        s.commit()
        ids = (ana.id, batch.id)

    users = admin_client.get("/admin/users").text
    assert "Ana Farmer" in users and "Sam Supplier" in users
    assert f'href="/admin/users/{ids[0]}"' in users

    batches = admin_client.get("/admin/batches").text
    assert f'href="/admin/users/{ids[0]}">Ana Farmer</a>' in batches  # farmer shown by name, not id
    assert "120.50 kg" in batches

    assert "Anchored" in admin_client.get("/admin/events").text
    assert "PHP 33.50" in admin_client.get("/admin/prices").text

    messages = admin_client.get("/admin/messages").text
    assert "Unread" in messages
    assert "TOP SECRET CHAT" not in messages  # bodies are never listed


def test_pagination_caps_rows_per_page(admin_client, db_session_factory):
    with db_session_factory() as s:
        for i in range(views.PER_PAGE + 5):
            add_user(s, f"Person {i:02d}", email=f"p{i}@example.com")
        s.commit()

    first = admin_client.get("/admin/users").text
    assert first.count("<tr>") - 1 == views.PER_PAGE  # minus the header row
    assert f"of {views.PER_PAGE + 5}" in first
    assert 'rel="next"' in first and 'rel="prev"' not in first

    second = admin_client.get("/admin/users?page=2").text
    assert second.count("<tr>") - 1 == 5
    assert 'rel="prev"' in second


@pytest.mark.parametrize("page", ["0", "-3", "abc", "999", ""])
def test_bad_page_numbers_are_clamped_not_errors(admin_client, db_session_factory, page):
    with db_session_factory() as s:
        add_user(s)
        s.commit()
    response = admin_client.get(f"/admin/users?page={page}")
    assert response.status_code == 200
    assert "Ana Farmer" in response.text


# --- detail pages ------------------------------------------------------------------------

def test_user_detail_shows_related_records_and_no_password_hash(admin_client, db_session_factory):
    with db_session_factory() as s:
        ana, sam = add_user(s), add_user(s, "Sam Supplier", UserRole.SUPPLIER)
        batch = add_batch(s, ana)
        add_event(s, batch, ana)
        s.add(Message(id=uuid.uuid4(), sender_id=ana.id, recipient_id=sam.id, body="private text", occurred_at=NOW))
        s.commit()
        uid = ana.id

    html = admin_client.get(f"/admin/users/{uid}").text
    assert "Harvest batches (as farmer)" in html
    assert "Custody events recorded" in html
    assert "1 message" in html  # count only
    assert "private text" not in html
    assert "$2b$" not in html and "hashed_password" not in html
    assert "cannot be deleted" in html
    assert 'action="/admin/users/%s/delete"' % uid not in html


def test_batch_detail_shows_its_custody_chain(admin_client, db_session_factory):
    with db_session_factory() as s:
        ana = add_user(s)
        batch = add_batch(s, ana)
        add_event(s, batch, ana, OnChainStatus.FAILED)
        s.commit()
        bid = batch.id
    html = admin_client.get(f"/admin/batches/{bid}").text
    assert "Chain of custody" in html
    assert "Failed" in html
    assert "Edit" not in html and "Delete" not in html  # read-only


def test_event_detail_redacts_credentials_in_payload(admin_client, db_session_factory):
    with db_session_factory() as s:
        ana = add_user(s)
        batch = add_batch(s, ana)
        event = add_event(s, batch, ana, payload={
            "weight_kg": "12", "notes": "ok", "api_key": "sk-live-123", "nested": {"auth_token": "tok-999"},
        })
        s.commit()
        eid = event.id
    html = admin_client.get(f"/admin/events/{eid}").text
    assert "weight_kg" in html and "&#34;12&#34;" in html
    assert "sk-live-123" not in html and "tok-999" not in html
    assert "[redacted]" in html


def test_message_body_appears_only_on_its_own_page(admin_client, db_session_factory):
    with db_session_factory() as s:
        a, b = add_user(s), add_user(s, "Sam Supplier", UserRole.SUPPLIER)
        msg = Message(id=uuid.uuid4(), sender_id=a.id, recipient_id=b.id, body="hello <b>there</b>", occurred_at=NOW)
        s.add(msg)
        s.commit()
        mid = msg.id
    html = admin_client.get(f"/admin/messages/{mid}").text
    assert "hello &lt;b&gt;there&lt;/b&gt;" in html  # escaped
    assert "private conversation" in html


@pytest.mark.parametrize("key", list(RESOURCES))
@pytest.mark.parametrize("bad_id", [str(uuid.uuid4()), "not-a-uuid"])
def test_missing_records_show_a_404_inside_the_layout(admin_client, key, bad_id):
    response = admin_client.get(f"/admin/{key}/{bad_id}")
    assert response.status_code == 404
    assert 'id="sidebar"' in response.text
    assert "does not exist" in response.text


@pytest.mark.parametrize("key", ["batches", "events", "messages"])
def test_read_only_resources_have_no_write_routes(admin_client, db_session_factory, key):
    fake = uuid.uuid4()
    assert admin_client.get(f"/admin/{key}/new").status_code == 404
    assert post(admin_client, f"/admin/{key}/new").status_code in (404, 405)
    assert admin_client.get(f"/admin/{key}/{fake}/edit").status_code in (404, 405)
    assert post(admin_client, f"/admin/{key}/{fake}/delete").status_code in (404, 405)


def test_names_are_escaped_everywhere(admin_client, db_session_factory):
    with db_session_factory() as s:
        evil = add_user(s, "<script>alert(1)</script>")
        s.commit()
        uid = evil.id
    for url in ("/admin/users", f"/admin/users/{uid}", f"/admin/users/{uid}/edit"):
        html = admin_client.get(url).text
        assert "<script>alert(1)" not in html, url


# --- users: create / edit / delete --------------------------------------------------------------

def test_create_user_hashes_the_password_and_normalises_email(admin_client, db_session_factory):
    response = post(admin_client, "/admin/users/new", USER_FORM)
    assert response.status_code == 303
    with db_session_factory() as s:
        user = s.scalar(select(User))
        assert user.email == "new.person@example.com"
        assert user.role == UserRole.BUYER and user.is_active is True
        assert user.hashed_password != USER_FORM["password"]
        assert verify_password(USER_FORM["password"], user.hashed_password)
    assert "Created user" in admin_client.get(response.headers["location"]).text


@pytest.mark.parametrize(
    ("changes", "field"),
    [
        ({"email": "not-an-email"}, "email"),
        ({"password": "short"}, "password"),
        ({"password": ""}, "password"),
        ({"password": "x" * 80}, "password"),
        ({"full_name": "   "}, "full_name"),
        ({"role": "admin"}, "role"),
        ({"phone_number": "9" * 40}, "phone_number"),
    ],
)
def test_create_user_validation_errors(admin_client, db_session_factory, changes, field):
    response = post(admin_client, "/admin/users/new", {**USER_FORM, **changes})
    assert response.status_code == 422
    assert f'id="f-{field}"' in response.text
    assert "field-error" in response.text
    assert count(db_session_factory, User) == 0
    assert USER_FORM["password"] not in response.text  # passwords are never echoed back


def test_create_user_rejects_duplicate_email(admin_client, db_session_factory):
    with db_session_factory() as s:
        add_user(s, email="new.person@example.com")
        s.commit()
    response = post(admin_client, "/admin/users/new", USER_FORM)
    assert response.status_code == 422
    assert "already registered" in response.text
    assert count(db_session_factory, User) == 1


def test_edit_user_keeps_password_when_blank_and_changes_it_when_given(admin_client, db_session_factory):
    with db_session_factory() as s:
        user = add_user(s)
        s.commit()
        uid, old_hash = user.id, user.hashed_password
    form = {"full_name": "Ana Renamed", "email": "ana.farmer@example.com", "role": "farmer", "password": "",
            "phone_number": "0917", "municipality": "Bongao", "is_active": "on"}

    assert post(admin_client, f"/admin/users/{uid}/edit", form).status_code == 303
    with db_session_factory() as s:
        user = s.get(User, uid)
        assert (user.full_name, user.phone_number, user.municipality) == ("Ana Renamed", "0917", "Bongao")
        assert user.hashed_password == old_hash

    assert post(admin_client, f"/admin/users/{uid}/edit", {**form, "password": "a-brand-new-pass"}).status_code == 303
    with db_session_factory() as s:
        assert verify_password("a-brand-new-pass", s.get(User, uid).hashed_password)


def test_edit_form_never_prefills_the_password(admin_client, db_session_factory):
    with db_session_factory() as s:
        user = add_user(s)
        s.commit()
        uid = user.id
    html = admin_client.get(f"/admin/users/{uid}/edit").text
    assert 'value="Ana Farmer"' in html
    assert "$2b$" not in html
    assert 'type="password"' in html and 'id="f-password"' in html


def test_edit_user_unchecking_active_deactivates(admin_client, db_session_factory):
    with db_session_factory() as s:
        user = add_user(s)
        s.commit()
        uid = user.id
    form = {"full_name": "Ana Farmer", "email": "ana.farmer@example.com", "role": "farmer"}  # no is_active
    assert post(admin_client, f"/admin/users/{uid}/edit", form).status_code == 303
    with db_session_factory() as s:
        assert s.get(User, uid).is_active is False


def test_edit_user_cannot_take_another_users_email(admin_client, db_session_factory):
    with db_session_factory() as s:
        add_user(s, "Other", email="taken@example.com")
        me = add_user(s)
        s.commit()
        uid = me.id
    form = {"full_name": "Ana Farmer", "email": "taken@example.com", "role": "farmer", "is_active": "on"}
    response = post(admin_client, f"/admin/users/{uid}/edit", form)
    assert response.status_code == 422 and "already registered" in response.text


def test_role_is_locked_once_a_user_has_related_records(admin_client, db_session_factory):
    with db_session_factory() as s:
        farmer = add_user(s)
        add_batch(s, farmer)
        s.commit()
        uid = farmer.id
    page = admin_client.get(f"/admin/users/{uid}/edit").text
    assert "Locked while this user has related records" in page

    form = {"full_name": "Ana Farmer", "email": "ana.farmer@example.com", "role": "buyer", "is_active": "on"}
    assert post(admin_client, f"/admin/users/{uid}/edit", form).status_code == 303
    with db_session_factory() as s:
        assert s.get(User, uid).role == UserRole.FARMER  # the attempted change was ignored


def test_role_can_change_while_user_has_no_records(admin_client, db_session_factory):
    with db_session_factory() as s:
        user = add_user(s)
        s.commit()
        uid = user.id
    form = {"full_name": "Ana Farmer", "email": "ana.farmer@example.com", "role": "buyer", "is_active": "on"}
    assert post(admin_client, f"/admin/users/{uid}/edit", form).status_code == 303
    with db_session_factory() as s:
        assert s.get(User, uid).role == UserRole.BUYER


def test_delete_user_without_records_after_confirmation_form(admin_client, db_session_factory):
    with db_session_factory() as s:
        user = add_user(s)
        s.commit()
        uid = user.id
    detail = admin_client.get(f"/admin/users/{uid}").text
    assert 'data-confirm="Delete this user?"' in detail  # the UI asks before submitting
    assert "cannot be undone" in detail

    response = post(admin_client, f"/admin/users/{uid}/delete")
    assert response.status_code == 303 and response.headers["location"] == "/admin/users"
    assert count(db_session_factory, User) == 0


def test_delete_user_with_records_is_refused_on_the_server(admin_client, db_session_factory):
    with db_session_factory() as s:
        user = add_user(s)
        add_batch(s, user)
        s.commit()
        uid = user.id
    response = post(admin_client, f"/admin/users/{uid}/delete")  # bypassing the hidden button
    assert response.status_code == 303
    assert count(db_session_factory, User) == 1
    assert "cannot be deleted" in admin_client.get(response.headers["location"]).text


def test_toggle_user_active(admin_client, db_session_factory):
    with db_session_factory() as s:
        user = add_user(s)
        s.commit()
        uid = user.id
    assert 'data-confirm="Deactivate Ana Farmer?"' in admin_client.get(f"/admin/users/{uid}").text
    post(admin_client, f"/admin/users/{uid}/toggle-active")
    with db_session_factory() as s:
        assert s.get(User, uid).is_active is False
    post(admin_client, f"/admin/users/{uid}/toggle-active")
    with db_session_factory() as s:
        assert s.get(User, uid).is_active is True


# --- price records ----------------------------------------------------------------------------

def _supplier(factory):
    with factory() as s:
        add_user(s, "Sam Supplier", UserRole.SUPPLIER, email="sam.supplier@example.com")
        s.commit()


def test_create_price_record(admin_client, db_session_factory):
    _supplier(db_session_factory)
    response = post(admin_client, "/admin/prices/new", PRICE_FORM)
    assert response.status_code == 303
    with db_session_factory() as s:
        record = s.scalar(select(PriceRecord))
        assert record.currency == "PHP"  # upper-cased
        assert float(record.price_per_kg) == 33.5
        assert record.posted_by_id == s.scalar(select(User.id))
    assert "Created price record" in admin_client.get(response.headers["location"]).text


@pytest.mark.parametrize(
    ("changes", "field"),
    [
        ({"species": ""}, "species"),
        ({"price_per_kg": "-1"}, "price_per_kg"),
        ({"price_per_kg": "0"}, "price_per_kg"),
        ({"price_per_kg": "abc"}, "price_per_kg"),
        ({"price_per_kg": "1.234"}, "price_per_kg"),
        ({"currency": "PESO"}, "currency"),
        ({"effective_date": "yesterday"}, "effective_date"),
        ({"posted_by_email": "nobody@example.com"}, "posted_by_email"),
    ],
)
def test_create_price_validation_errors(admin_client, db_session_factory, changes, field):
    _supplier(db_session_factory)
    response = post(admin_client, "/admin/prices/new", {**PRICE_FORM, **changes})
    assert response.status_code == 422
    assert f'id="f-{field}"' in response.text and "field-error" in response.text
    assert count(db_session_factory, PriceRecord) == 0


def test_only_suppliers_and_buyers_can_be_the_poster(admin_client, db_session_factory):
    with db_session_factory() as s:
        add_user(s, "Ana Farmer", UserRole.FARMER, email="sam.supplier@example.com")
        s.commit()
    response = post(admin_client, "/admin/prices/new", PRICE_FORM)
    assert response.status_code == 422
    assert "Only suppliers and buyers" in response.text


def test_edit_price_record(admin_client, db_session_factory):
    with db_session_factory() as s:
        sam = add_user(s, "Sam Supplier", UserRole.SUPPLIER, email="sam.supplier@example.com")
        record = add_price(s, sam)
        s.commit()
        rid = record.id
    page = admin_client.get(f"/admin/prices/{rid}/edit").text
    assert 'value="sam.supplier@example.com"' in page and 'value="33.50"' in page

    response = post(admin_client, f"/admin/prices/{rid}/edit", {**PRICE_FORM, "price_per_kg": "40", "notes": "updated"})
    assert response.status_code == 303
    with db_session_factory() as s:
        record = s.get(PriceRecord, rid)
        assert float(record.price_per_kg) == 40.0 and record.notes == "updated"


def test_delete_price_record(admin_client, db_session_factory):
    with db_session_factory() as s:
        sam = add_user(s, "Sam Supplier", UserRole.SUPPLIER)
        record = add_price(s, sam)
        s.commit()
        rid = record.id
    assert 'data-confirm="Delete this price record?"' in admin_client.get(f"/admin/prices/{rid}").text
    assert post(admin_client, f"/admin/prices/{rid}/delete").status_code == 303
    assert count(db_session_factory, PriceRecord) == 0
    assert count(db_session_factory, User) == 1  # the poster is untouched


def test_deleting_a_missing_record_is_a_404(admin_client):
    assert post(admin_client, f"/admin/prices/{uuid.uuid4()}/delete").status_code == 404
    assert post(admin_client, "/admin/prices/not-a-uuid/delete").status_code == 404


# --- custody event actions ---------------------------------------------------------------------

@pytest.fixture
def failed_event(db_session_factory):
    with db_session_factory() as s:
        ana = add_user(s)
        event = add_event(s, add_batch(s, ana), ana, OnChainStatus.FAILED)
        s.commit()
        return event.id


def test_retry_anchor_resets_status_and_queues_the_job(admin_client, db_session_factory, failed_event, monkeypatch):
    queued = []

    async def fake_anchor(event_id):
        queued.append(event_id)

    monkeypatch.setattr(views, "anchor_event", fake_anchor)
    assert 'data-confirm="Retry anchoring this event?"' in admin_client.get(f"/admin/events/{failed_event}").text

    response = post(admin_client, f"/admin/events/{failed_event}/retry-anchor")
    assert response.status_code == 303
    assert queued == [failed_event]
    with db_session_factory() as s:
        assert s.get(ChainOfCustodyEvent, failed_event).on_chain_status == OnChainStatus.PENDING
    assert "Re-anchoring queued" in admin_client.get(response.headers["location"]).text


def test_retry_anchor_is_a_no_op_for_anchored_events(admin_client, db_session_factory, monkeypatch):
    queued = []

    async def fake_anchor(event_id):
        queued.append(event_id)

    monkeypatch.setattr(views, "anchor_event", fake_anchor)
    with db_session_factory() as s:
        ana = add_user(s)
        event = add_event(s, add_batch(s, ana), ana, OnChainStatus.ANCHORED)
        s.commit()
        eid = event.id
    assert "Retry anchor" not in admin_client.get(f"/admin/events/{eid}").text  # button hidden

    response = post(admin_client, f"/admin/events/{eid}/retry-anchor")  # ...and refused server-side
    assert queued == []
    assert "already anchored" in admin_client.get(response.headers["location"]).text


def _verification(event_id, **kw) -> CustodyEventVerification:
    base = dict(event_id=event_id, on_chain_exists=True, verified=True, expected_data_hash="0x1",
                on_chain_data_hash="0x1", on_chain_recorded_at=None, tx_hash=None)
    return CustodyEventVerification(**{**base, **kw})


@pytest.mark.parametrize(
    ("result", "expected"),
    [
        ({}, "Verified: the on-chain hash matches"),
        ({"verified": False, "on_chain_data_hash": "0x2"}, "MISMATCH"),
        ({"verified": False, "on_chain_exists": False, "on_chain_data_hash": None}, "not found on-chain"),
    ],
)
def test_verify_reports_the_chain_result(admin_client, failed_event, monkeypatch, result, expected):
    async def fake_verify(event_id, db, _user):
        return _verification(event_id, **result)

    monkeypatch.setattr(views, "verify_custody_event", fake_verify)
    response = post(admin_client, f"/admin/events/{failed_event}/verify")
    assert expected in admin_client.get(response.headers["location"]).text


def test_verify_hides_provider_errors_that_may_contain_keys(admin_client, failed_event, monkeypatch):
    from fastapi import HTTPException

    async def fake_verify(event_id, db, _user):
        raise HTTPException(502, "Could not reach the chain: https://rpc.example/v3/SECRET-API-KEY")

    monkeypatch.setattr(views, "verify_custody_event", fake_verify)
    response = post(admin_client, f"/admin/events/{failed_event}/verify")
    page = admin_client.get(response.headers["location"]).text
    assert "Could not reach the blockchain" in page
    assert "SECRET-API-KEY" not in page


def test_existing_retry_endpoint_still_behaves(db_session_factory):
    """The public API route now shares queue_retry with the admin; behaviour must be unchanged."""
    import asyncio

    from app.services.chain_anchor import queue_retry

    with db_session_factory() as s:
        ana = add_user(s)
        failed = add_event(s, add_batch(s, ana), ana, OnChainStatus.FAILED)
        anchored = add_event(s, add_batch(s, ana), ana, OnChainStatus.ANCHORED)
        s.commit()
        ids = (failed.id, anchored.id)

    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

    async def run():
        engine = create_async_engine(str(db_session_factory.kw["bind"].url).replace("sqlite:", "sqlite+aiosqlite:"))
        async with async_sessionmaker(engine, expire_on_commit=False)() as db:
            f, a = await db.get(ChainOfCustodyEvent, ids[0]), await db.get(ChainOfCustodyEvent, ids[1])
            result = (await queue_retry(db, f), await queue_retry(db, a), f.on_chain_status, a.on_chain_status)
        await engine.dispose()
        return result

    assert asyncio.run(run()) == (True, False, OnChainStatus.PENDING, OnChainStatus.ANCHORED)
