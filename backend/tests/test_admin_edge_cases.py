"""Edge cases found by the Phase 8 coverage review: race/conflict handling, missing
records, nested redaction, and behaviour when the admin is switched off."""

import uuid
from datetime import date, datetime, timezone

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.admin import auth, ui, views
from app.admin.listing import _valid_filter_value
from app.admin.resources import Filter
from app.core.config import Settings, settings
from app.models.enums import OnChainStatus, UserRole
from app.models.user import User
from tests.conftest import login
from tests.test_admin_resources import (
    USER_FORM,
    add_batch,
    add_event,
    add_price,
    add_user,
    post,
)


def conflict(*args, **kwargs):
    raise IntegrityError("INSERT ...", {}, Exception("duplicate key value violates unique constraint"))


# --- database conflicts (e.g. two admins racing) are handled, not 500s -------------------------------------

def test_create_conflict_is_reported_and_rolled_back(admin_client, db_session_factory, monkeypatch):
    monkeypatch.setattr(views.audit, "add", conflict)  # raised inside the create transaction
    response = post(admin_client, "/admin/users/new", USER_FORM)
    assert response.status_code == 409
    assert "That record already exists." in response.text
    with db_session_factory() as s:
        assert s.scalar(select(User)) is None            # the half-created row was rolled back


def test_edit_conflict_is_reported_and_leaves_the_record_unchanged(admin_client, db_session_factory, monkeypatch):
    with db_session_factory() as s:
        user = add_user(s)
        s.commit()
        uid = user.id
    monkeypatch.setattr(views.audit, "add", conflict)
    form = {"full_name": "Renamed", "email": "ana.farmer@example.com", "role": "farmer", "is_active": "on"}
    response = post(admin_client, f"/admin/users/{uid}/edit", form)
    assert response.status_code == 409 and "conflicts with an existing record" in response.text
    with db_session_factory() as s:
        assert s.get(User, uid).full_name == "Ana Farmer"


def test_delete_conflict_keeps_the_record_and_explains(admin_client, db_session_factory, monkeypatch):
    with db_session_factory() as s:
        user = add_user(s)
        s.commit()
        uid = user.id
    monkeypatch.setattr(views.audit, "add", conflict)
    response = post(admin_client, f"/admin/users/{uid}/delete")
    assert response.status_code == 303
    assert "still referenced elsewhere" in admin_client.get(response.headers["location"]).text
    with db_session_factory() as s:
        assert s.get(User, uid) is not None


# --- missing / malformed record ids ---------------------------------------------------------------------------

@pytest.mark.parametrize("bad_id", [str(uuid.uuid4()), "not-a-uuid", "1"])
def test_every_record_action_handles_unknown_ids_with_a_404(admin_client, bad_id):
    for path in (f"/admin/users/{bad_id}/edit", f"/admin/prices/{bad_id}/edit"):
        assert admin_client.get(path).status_code == 404, path
        assert post(admin_client, path, {"full_name": "x"}).status_code == 404, path
    for path in (f"/admin/users/{bad_id}/toggle-active", f"/admin/events/{bad_id}/retry-anchor",
                 f"/admin/events/{bad_id}/verify", f"/admin/users/{bad_id}/delete"):
        response = post(admin_client, path)
        assert response.status_code == 404 and "does not exist" in response.text, path


# --- redaction of nested payloads ---------------------------------------------------------------------------------

def test_redaction_reaches_into_lists_and_nested_objects(admin_client, db_session_factory):
    with db_session_factory() as s:
        ana = add_user(s)
        event = add_event(s, add_batch(s, ana), ana, payload={
            "items": [{"api_key": "LIST-SECRET-1", "kept": "visible-value"}, {"deep": [{"password": "LIST-SECRET-2"}]}],
            "tokens": ["LIST-SECRET-3"],
            "Authorization": "LIST-SECRET-4",
        })
        s.commit()
        eid = event.id
    for url in (f"/admin/events/{eid}", f"/admin/events/{eid}/print"):
        html = admin_client.get(url).text
        for n in range(1, 5):
            assert f"LIST-SECRET-{n}" not in html, (url, n)
        assert "visible-value" in html


def test_redact_helper_leaves_harmless_values_alone():
    assert views._redact({"a": 1, "b": [1, {"c": "d"}], "note": None}) == {"a": 1, "b": [1, {"c": "d"}], "note": None}
    assert views._redact(["x", {"secret": "y"}]) == ["x", {"secret": "[redacted]"}]


# --- the admin switched off -----------------------------------------------------------------------------------------

def test_turning_the_admin_off_invalidates_existing_sessions(client, monkeypatch):
    assert login(client).status_code == 303
    assert client.get("/admin").status_code == 200
    monkeypatch.setattr(settings, "ADMIN_PASSWORD", None)
    monkeypatch.setattr(settings, "ADMIN_EMAIL", None)
    monkeypatch.setattr(settings, "ADMIN_SESSION_SECRET", None)
    assert client.get("/admin").status_code == 303
    assert client.get("/admin/login").status_code == 503
    assert auth.check_credentials("anything", "anything") is False


def test_disabled_admin_never_authenticates_even_with_a_cookie():
    class FakeRequest:
        cookies = {auth.SESSION_COOKIE: "whatever"}

    settings_backup = (settings.ADMIN_EMAIL, settings.ADMIN_PASSWORD, settings.ADMIN_SESSION_SECRET)
    try:
        settings.ADMIN_EMAIL = settings.ADMIN_PASSWORD = settings.ADMIN_SESSION_SECRET = None
        assert auth.session_from_request(FakeRequest()) is None
    finally:
        settings.ADMIN_EMAIL, settings.ADMIN_PASSWORD, settings.ADMIN_SESSION_SECRET = settings_backup


# --- small helpers --------------------------------------------------------------------------------------------------------

def test_datetime_filter_formats_everything_it_may_receive():
    fmt = ui.templates.env.filters["dt"]
    assert fmt(None) == "—"
    assert fmt(datetime(2026, 9, 19, 4, 5, tzinfo=timezone.utc)) == "2026-09-19 04:05 UTC"
    assert fmt(datetime(2026, 9, 19, 4, 5)) == "2026-09-19 04:05 UTC"      # naive values are treated as UTC
    assert fmt(date(2026, 9, 19)) == "2026-09-19"
    assert ui.templates.env.filters["num"](None) == "0" and ui.templates.env.filters["num"](12345.6) == "12,346"
    assert ui.templates.env.filters["label"]("with_supplier") == "With Supplier"


def test_unknown_filter_kinds_are_ignored_not_trusted():
    assert _valid_filter_value(Filter("x", "X", "bogus", ("id",)), "value") is None
    assert _valid_filter_value(Filter("x", "X", "uuid", ("id",)), "") is None


def test_cors_origins_list_parsing():
    assert Settings(_env_file=None, CORS_ORIGINS="*").cors_origins_list == ["*"]
    parsed = Settings(_env_file=None, CORS_ORIGINS="https://a.example, https://b.example ,,")
    assert parsed.cors_origins_list == ["https://a.example", "https://b.example"]


def test_retry_and_verify_buttons_follow_event_state(admin_client, db_session_factory):
    with db_session_factory() as s:
        ana = add_user(s)
        pending = add_event(s, add_batch(s, ana), ana, OnChainStatus.PENDING)
        s.commit()
        pid = pending.id
    page = admin_client.get(f"/admin/events/{pid}").text
    assert "Verify on-chain" in page and "Retry anchor" in page


def test_price_and_user_pages_render_after_edits_with_related_data(admin_client, db_session_factory):
    with db_session_factory() as s:
        sam = add_user(s, "Sam Supplier", UserRole.SUPPLIER)
        price = add_price(s, sam)
        s.commit()
        sid, pid = sam.id, price.id
    assert admin_client.get(f"/admin/users/{sid}").status_code == 200
    assert "Price records posted" in admin_client.get(f"/admin/users/{sid}").text
    assert admin_client.get(f"/admin/prices/{pid}").status_code == 200


def test_record_deleted_by_someone_else_during_a_conflicting_edit_is_a_404(admin_client, db_session_factory, monkeypatch):
    """Edit conflicts, and by the time the form would re-render the row is gone."""
    from sqlalchemy.ext.asyncio import AsyncSession

    with db_session_factory() as s:
        user = add_user(s)
        s.commit()
        uid = user.id

    real_get = AsyncSession.get

    async def get_that_finds_nothing_on_reload(self, entity, ident, **kwargs):
        if kwargs.get("populate_existing"):
            return None  # the post-rollback reload: the record has vanished
        return await real_get(self, entity, ident, **kwargs)

    monkeypatch.setattr(views.audit, "add", conflict)
    monkeypatch.setattr(AsyncSession, "get", get_that_finds_nothing_on_reload)
    form = {"full_name": "Renamed", "email": "ana.farmer@example.com", "role": "farmer", "is_active": "on"}
    response = post(admin_client, f"/admin/users/{uid}/edit", form)
    assert response.status_code == 404 and "does not exist" in response.text
