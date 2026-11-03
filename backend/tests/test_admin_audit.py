import re
import uuid
from pathlib import Path

import pytest
from alembic.config import Config
from alembic.operations import Operations
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, inspect, select

from app.admin import audit, views
from app.admin.audit import changed_fields
from app.admin.resources import RESOURCES
from app.db.base import Base
from app.models.admin_audit_log import AdminAuditLog, AuditAction
from app.models.enums import OnChainStatus, UserRole
from app.models.user import User
from app.services import chain_anchor
from tests.conftest import ADMIN_EMAIL, ADMIN_PASSWORD, login
from tests.test_admin_resources import (
    PRICE_FORM,
    USER_FORM,
    add_batch,
    add_event,
    add_price,
    add_user,
    post,
)


def rows(factory, action: str | None = None) -> list[AdminAuditLog]:
    with factory() as s:
        stmt = select(AdminAuditLog).order_by(AdminAuditLog.created_at)
        if action:
            stmt = stmt.where(AdminAuditLog.action == action)
        return list(s.scalars(stmt).all())


def only(factory, action: str) -> AdminAuditLog:
    (row,) = rows(factory, action)
    return row


# --- authentication events -------------------------------------------------------------------

def test_login_is_logged_with_admin_and_ip(admin_client, db_session_factory):
    row = only(db_session_factory, "login")
    assert row.admin_email == ADMIN_EMAIL
    assert row.ip_address == "testclient"
    assert row.created_at is not None
    assert row.resource is None and row.record_id is None


def test_failed_login_is_logged_without_the_submitted_credentials(client, db_session_factory):
    login(client, email="someone@example.com", password="hunter2-secret")
    row = only(db_session_factory, "login_failed")
    assert row.admin_email == "unknown"
    assert row.ip_address == "testclient"
    dump = " ".join(str(v) for v in (row.admin_email, row.summary, row.record_id, row.resource, row.ip_address))
    assert "hunter2-secret" not in dump and "someone@example.com" not in dump
    assert not rows(db_session_factory, "login")


def test_logout_is_logged(admin_client, db_session_factory):
    post(admin_client, "/admin/logout")
    assert only(db_session_factory, "logout").admin_email == ADMIN_EMAIL


def test_login_and_logout_still_work_when_auditing_is_broken(client, db_session_factory, monkeypatch):
    def boom(*args, **kwargs):
        raise RuntimeError("audit table missing")

    monkeypatch.setattr(audit, "_entry", boom)
    assert login(client).status_code == 303          # a broken audit table must not lock the admin out
    assert post(client, "/admin/logout").status_code == 303
    assert rows(db_session_factory) == []


# --- data-changing actions ---------------------------------------------------------------------

def test_creating_a_user_is_logged_with_id_and_no_secrets(admin_client, db_session_factory):
    post(admin_client, "/admin/users/new", USER_FORM)
    with db_session_factory() as s:
        created = s.scalar(select(User))
        row = only(db_session_factory, "create")
        assert (row.resource, row.record_id) == ("users", str(created.id))
        assert row.admin_email == ADMIN_EMAIL
        assert "New Person" in row.summary
        for secret in (USER_FORM["password"], created.hashed_password):
            assert all(secret not in str(v) for v in (row.summary, row.record_id, row.admin_email, row.ip_address))


def test_update_logs_field_names_but_never_values(admin_client, db_session_factory):
    with db_session_factory() as s:
        user = add_user(s)
        s.commit()
        uid = user.id
    form = {"full_name": "Ana Renamed", "email": "ana.farmer@example.com", "role": "farmer", "is_active": "on",
            "phone_number": "0917-555-9999", "password": "a-brand-new-pass"}
    post(admin_client, f"/admin/users/{uid}/edit", form)
    row = only(db_session_factory, "update")
    assert row.record_id == str(uid) and row.resource == "users"
    assert "fields changed: full_name, phone_number, password" in row.summary
    for value in ("Ana Renamed", "0917-555-9999", "a-brand-new-pass"):
        assert value not in row.summary.split("fields changed:")[1]


def test_update_with_no_changes_says_so(admin_client, db_session_factory):
    with db_session_factory() as s:
        user = add_user(s)
        s.commit()
        uid = user.id
    form = {"full_name": "Ana Farmer", "email": "ana.farmer@example.com", "role": "farmer", "is_active": "on"}
    post(admin_client, f"/admin/users/{uid}/edit", form)
    assert only(db_session_factory, "update").summary.endswith("fields changed: none")


def test_equivalent_prices_are_not_flagged_as_changed(admin_client, db_session_factory):
    with db_session_factory() as s:
        sam = add_user(s, "Sam Supplier", UserRole.SUPPLIER, "sam.supplier@example.com")
        record = add_price(s, sam)  # price 33.5 -> shown as "33.50"
        s.commit()
        rid = record.id
    form = {**PRICE_FORM, "price_per_kg": "33.5", "notes": "dry, grade A", "currency": "PHP"}
    post(admin_client, f"/admin/prices/{rid}/edit", form)
    assert "fields changed: none" in only(db_session_factory, "update").summary


def test_delete_and_status_change_are_logged(admin_client, db_session_factory):
    with db_session_factory() as s:
        keep, gone = add_user(s, "Keep Me"), add_user(s, "Gone Soon")
        s.commit()
        keep_id, gone_id = keep.id, gone.id
    post(admin_client, f"/admin/users/{keep_id}/toggle-active")
    post(admin_client, f"/admin/users/{keep_id}/toggle-active")
    post(admin_client, f"/admin/users/{gone_id}/delete")

    status = rows(db_session_factory, "status_change")
    assert [r.summary for r in status] == ["Deactivated user: Keep Me", "Activated user: Keep Me"]
    deleted = only(db_session_factory, "delete")
    assert (deleted.resource, deleted.record_id) == ("users", str(gone_id))
    assert "Gone Soon" in deleted.summary


def test_price_lifecycle_is_logged(admin_client, db_session_factory):
    with db_session_factory() as s:
        add_user(s, "Sam Supplier", UserRole.SUPPLIER, "sam.supplier@example.com")
        s.commit()
    created = post(admin_client, "/admin/prices/new", PRICE_FORM)
    rid = created.headers["location"].rsplit("/", 1)[1]
    post(admin_client, f"/admin/prices/{rid}/edit", {**PRICE_FORM, "price_per_kg": "40"})
    post(admin_client, f"/admin/prices/{rid}/delete")
    price_rows = [r for r in rows(db_session_factory) if r.resource == "prices"]
    assert sorted(r.action for r in price_rows) == ["create", "delete", "update"]
    assert all(r.record_id == rid for r in price_rows)
    assert "price_per_kg" in only(db_session_factory, "update").summary


def test_retry_anchor_is_logged_only_when_something_happens(admin_client, db_session_factory, monkeypatch):
    async def noop(event_id):
        return None

    monkeypatch.setattr(views, "anchor_event", noop)
    with db_session_factory() as s:
        ana = add_user(s)
        failed = add_event(s, add_batch(s, ana), ana, OnChainStatus.FAILED)
        done = add_event(s, add_batch(s, ana), ana, OnChainStatus.ANCHORED)
        s.commit()
        failed_id, done_id = failed.id, done.id
    post(admin_client, f"/admin/events/{done_id}/retry-anchor")
    assert rows(db_session_factory, "retry_anchor") == []
    post(admin_client, f"/admin/events/{failed_id}/retry-anchor")
    row = only(db_session_factory, "retry_anchor")
    assert (row.resource, row.record_id) == ("events", str(failed_id))


def test_printing_is_logged(admin_client, db_session_factory):
    with db_session_factory() as s:
        ana = add_user(s)
        for i in range(3):
            add_user(s, f"Person {i}", email=f"p{i}@example.com")
        s.commit()
        uid = ana.id
    admin_client.get("/admin/users/print?q=person")
    admin_client.get(f"/admin/users/{uid}/print")
    printed = rows(db_session_factory, "print")
    assert len(printed) == 2
    assert "3 of 3 records" in printed[0].summary and printed[0].record_id is None
    assert printed[1].record_id == str(uid)


def test_a_failed_change_is_not_logged(admin_client, db_session_factory):
    post(admin_client, "/admin/users/new", {**USER_FORM, "email": "not-an-email"})  # validation failure
    post(admin_client, f"/admin/users/{uuid.uuid4()}/delete")                       # missing record
    assert rows(db_session_factory, "create") == [] and rows(db_session_factory, "delete") == []


# --- integrity: no change without a record -----------------------------------------------------

def test_a_change_is_rolled_back_if_its_audit_row_cannot_be_written(admin_client, db_session_factory, monkeypatch):
    def boom(*args, **kwargs):
        raise RuntimeError("audit table missing")

    monkeypatch.setattr(views.audit, "add", boom)
    with db_session_factory() as s:
        victim = add_user(s, "Victim")
        s.commit()
        vid = victim.id
    with pytest.raises(RuntimeError):
        post(admin_client, "/admin/users/new", USER_FORM)
    with pytest.raises(RuntimeError):
        post(admin_client, f"/admin/users/{vid}/delete")
    with pytest.raises(RuntimeError):
        post(admin_client, f"/admin/users/{vid}/toggle-active")
    with db_session_factory() as s:
        users = s.scalars(select(User)).all()
        assert [u.full_name for u in users] == ["Victim"] and users[0].is_active is True


def test_audit_rows_and_their_change_commit_together(admin_client, db_session_factory):
    post(admin_client, "/admin/users/new", USER_FORM)
    with db_session_factory() as s:
        assert s.scalar(select(User)) is not None
    assert len(rows(db_session_factory, "create")) == 1


def test_no_secret_ever_reaches_the_audit_table(admin_client, db_session_factory):
    with db_session_factory() as s:
        ana = add_user(s)
        s.commit()
        uid = ana.id
    post(admin_client, "/admin/users/new", USER_FORM)
    post(admin_client, f"/admin/users/{uid}/edit", {"full_name": "X Y", "email": "x@example.com", "role": "farmer",
                                                    "password": "another-secret-pw"})
    login_client_cookie = admin_client.cookies.get("agal_admin_session")
    text = " ".join(
        str(v) for r in rows(db_session_factory)
        for v in (r.admin_email, r.action, r.resource, r.record_id, r.summary, r.ip_address)
    )
    for secret in (ADMIN_PASSWORD, USER_FORM["password"], "another-secret-pw", "not.a.real.hash", login_client_cookie):
        assert secret and secret not in text


def test_summaries_are_length_capped(db_session_factory):
    import asyncio

    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

    async def run():
        engine = create_async_engine(str(db_session_factory.kw["bind"].url).replace("sqlite:", "sqlite+aiosqlite:"))
        async with async_sessionmaker(engine, expire_on_commit=False)() as db:
            await audit.record_safely(db, AuditAction.CREATE, summary="x" * 5000)
        await engine.dispose()

    asyncio.run(run())
    assert len(only(db_session_factory, "create").summary) == audit.MAX_SUMMARY


def test_changed_fields_helper():
    before = {"a": "1", "b": "x", "price": "33.50", "flag": True}
    assert changed_fields(before, {"a": "1", "b": "y", "price": "33.5", "flag": True}) == ["b"]
    assert changed_fields(before, {"a": "1", "password": ""}) == []
    assert changed_fields(before, {"password": "s3cret"}) == ["password"]  # flagged, value never returned


# --- the Audit Logs page -----------------------------------------------------------------------

def test_audit_page_lists_entries_and_is_in_the_nav(admin_client, db_session_factory):
    post(admin_client, "/admin/users/new", USER_FORM)
    html = admin_client.get("/admin/audit").text
    assert "<h1>Audit Logs</h1>" in html
    assert "Created user: New Person" in html
    assert ADMIN_EMAIL in html
    assert 'href="/admin/audit"' in html and 'aria-current="page"' in html


def test_audit_page_requires_login(client):
    for url in ("/admin/audit", "/admin/audit/print", f"/admin/audit/{uuid.uuid4()}", f"/admin/audit/{uuid.uuid4()}/print"):
        assert client.get(url).status_code == 303


def test_audit_search_filter_and_sort(admin_client, db_session_factory):
    with db_session_factory() as s:
        ana = add_user(s)
        s.commit()
        uid = ana.id
    post(admin_client, "/admin/users/new", USER_FORM)
    post(admin_client, f"/admin/users/{uid}/toggle-active")

    by_action = admin_client.get("/admin/audit?action=status_change").text
    assert "Deactivated user: Ana Farmer" in by_action and "Created user: New Person" not in by_action
    assert re.search(r"Action:</span>\s*Status Change", by_action)   # shown as an applied filter chip

    assert "Created user: New Person" in admin_client.get("/admin/audit?q=new+person").text
    assert "No matching audit logs" in admin_client.get("/admin/audit?q=zzzz-nothing").text
    assert "Created user: New Person" not in admin_client.get("/admin/audit?resource=prices").text
    assert admin_client.get("/admin/audit?sort=action&dir=asc").status_code == 200
    assert admin_client.get("/admin/audit?action=bogus&resource=%27%3B--").status_code == 200  # junk ignored


def test_audit_entry_detail_and_print(admin_client, db_session_factory):
    post(admin_client, "/admin/users/new", USER_FORM)
    row = only(db_session_factory, "create")
    detail = admin_client.get(f"/admin/audit/{row.id}").text
    assert "Created user: New Person" in detail and "testclient" in detail
    assert f"/admin/audit/{row.id}/print" in detail
    report = admin_client.get("/admin/audit/print?action=create").text
    assert "<h1>Audit Logs</h1>" in report and "Created user: New Person" in report and "Action: Create" in report


def test_audit_log_is_read_only_everywhere(admin_client, db_session_factory):
    post(admin_client, "/admin/users/new", USER_FORM)
    row = only(db_session_factory, "create")
    res = RESOURCES["audit"]
    assert not (res.can_create or res.can_edit or res.can_delete)

    assert admin_client.get("/admin/audit/new").status_code in (404, 405)
    assert post(admin_client, "/admin/audit/new").status_code in (404, 405)
    assert admin_client.get(f"/admin/audit/{row.id}/edit").status_code in (404, 405)
    assert post(admin_client, f"/admin/audit/{row.id}/edit").status_code in (404, 405)
    assert post(admin_client, f"/admin/audit/{row.id}/delete").status_code in (404, 405)
    assert len(rows(db_session_factory, "create")) == 1

    detail = admin_client.get(f"/admin/audit/{row.id}").text
    assert ">Edit<" not in detail and ">Delete<" not in detail


def test_only_get_routes_exist_for_the_audit_log():
    from app.admin.views import router

    methods = {m for r in router.routes if getattr(r, "path", "").startswith("/admin/audit") for m in r.methods}
    assert methods <= {"GET", "HEAD"}


# --- schema & migration ---------------------------------------------------------------------------

def _alembic_config() -> Config:
    backend = Path(__file__).resolve().parent.parent
    config = Config(str(backend / "alembic.ini"))
    config.set_main_option("script_location", str(backend / "alembic"))
    return config


def test_migration_history_has_a_single_head_that_adds_the_table():
    script = ScriptDirectory.from_config(_alembic_config())
    heads = script.get_heads()
    assert len(heads) == 1
    revision = script.get_revision(heads[0])
    assert "audit" in revision.doc.lower()


def test_migration_creates_exactly_the_columns_and_indexes_the_model_declares(tmp_path):
    script = ScriptDirectory.from_config(_alembic_config())
    migration = script.get_revision(script.get_heads()[0]).module
    engine = create_engine(f"sqlite:///{tmp_path / 'm.db'}")
    with engine.begin() as conn, Operations.context(MigrationContext.configure(conn)):
        migration.upgrade()
    inspector = inspect(engine)
    table = Base.metadata.tables["admin_audit_logs"]
    migrated = {c["name"]: c for c in inspector.get_columns("admin_audit_logs")}
    assert set(migrated) == {c.name for c in table.columns}
    for column in table.columns:
        assert migrated[column.name]["nullable"] == column.nullable, column.name
    assert {i["name"] for i in inspector.get_indexes("admin_audit_logs")} == {i.name for i in table.indexes}

    with engine.begin() as conn, Operations.context(MigrationContext.configure(conn)):
        migration.downgrade()
    assert "admin_audit_logs" not in inspect(engine).get_table_names()


def test_chain_anchor_helper_is_still_shared(db_session_factory):
    assert callable(chain_anchor.queue_retry)  # the public API and the admin both depend on it
