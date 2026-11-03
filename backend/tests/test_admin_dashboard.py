import re
import uuid
from datetime import datetime, timedelta, timezone

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.admin import dashboard
from app.admin.dashboard import Count, RecentEvent, load_stats
from app.db.base import Base
from app.main import app
from app.models.batch import HarvestBatch
from app.models.custody_event import ChainOfCustodyEvent
from app.models.enums import BatchStatus, CustodyEventType, OnChainStatus, UserRole
from app.models.message import Message
from app.models.price import PriceRecord
from app.models.user import User
from tests.conftest import sample_stats

# --- rendering (fake stats, no database) --------------------------------------------------

def test_dashboard_shows_key_figures(admin_client):
    html = admin_client.get("/admin").text
    for expected in ("12", "10 active", "2 inactive", "25", "1,234", "60", "6 in the last 24 h", "41", "2026-09-18", "88", "9 unread"):
        assert expected in html


def test_dashboard_has_breakdowns_with_real_values(admin_client):
    html = admin_client.get("/admin").text
    for heading in ("Users by role", "Batches by status", "On-chain anchoring"):
        assert heading in html
    # <progress> carries the value + max, so bars need no inline width style.
    assert 'max="12" value="7"' in html
    assert 'max="60" value="54"' in html
    assert "chain-anchored" in html
    assert 'aria-label="Farmer: 7"' in html


def test_bars_do_not_divide_by_zero_when_a_table_is_empty(admin_client):
    app.dependency_overrides[load_stats] = lambda: sample_stats(
        users_total=0, users_active=0, users_by_role=[Count("farmer", "Farmer", 0)]
    )
    html = admin_client.get("/admin").text
    assert 'max="1" value="0"' in html


def test_failed_anchor_callout_shown_only_when_there_are_failures(admin_client):
    assert "failed to anchor on-chain" in admin_client.get("/admin").text

    app.dependency_overrides[load_stats] = lambda: sample_stats(
        events_by_chain=[Count("pending", "Pending", 0), Count("anchored", "Anchored", 60), Count("failed", "Failed", 0)]
    )
    assert "failed to anchor on-chain" not in admin_client.get("/admin").text


def test_recent_activity_tables_render(admin_client):
    html = admin_client.get("/admin").text
    assert "Recent custody events" in html
    assert "Drying Started" in html
    assert "Ana Farmer" in html
    assert "2026-09-19 03:00 UTC" in html
    # Batch ids are shown shortened, with the full id on hover.
    assert ">0f0e0d0c</td>" in html
    assert 'title="0f0e0d0c-aaaa-bbbb-cccc-000000000001"' in html
    assert "Newest users" in html
    assert "Ben Buyer" in html


def test_empty_state_rows_when_no_activity(admin_client):
    app.dependency_overrides[load_stats] = lambda: sample_stats(recent_events=[], recent_users=[])
    html = admin_client.get("/admin").text
    assert "No custody events yet." in html
    assert "No users yet." in html


def test_names_from_the_database_are_escaped(admin_client):
    event = RecentEvent(
        datetime(2026, 9, 19, tzinfo=timezone.utc), "note_added", "<img src=x onerror=alert(1)>", "farmer",
        str(uuid.uuid4()), "pending",
    )
    app.dependency_overrides[load_stats] = lambda: sample_stats(recent_events=[event])
    html = admin_client.get("/admin").text
    assert "<img src=x" not in html
    assert "&lt;img src=x onerror=alert(1)&gt;" in html


def test_error_state_when_stats_unavailable(admin_client):
    app.dependency_overrides[load_stats] = lambda: None
    response = admin_client.get("/admin")
    assert response.status_code == 200  # the page degrades; it does not 500
    assert "Could not load statistics" in response.text
    assert 'role="alert"' in response.text
    assert "stat-grid" not in response.text
    assert 'id="sidebar"' in response.text  # navigation still works


@pytest.mark.asyncio
async def test_load_stats_returns_none_and_hides_details_on_failure(monkeypatch, caplog):
    async def boom(_db):
        raise RuntimeError("password authentication failed for user agal")

    monkeypatch.setattr(dashboard, "collect_stats", boom)
    assert await dashboard.load_stats(db=None) is None
    assert "could not load admin dashboard statistics" in caplog.text


def test_dashboard_still_requires_login_and_skips_the_database(client):
    calls = []
    app.dependency_overrides[load_stats] = lambda: calls.append(1)
    response = client.get("/admin")
    assert response.status_code == 303
    assert response.headers["location"] == "/admin/login"
    assert calls == []  # unauthenticated requests never reach the statistics provider


def test_dashboard_page_has_no_sensitive_fields(admin_client):
    html = admin_client.get("/admin").text.lower()
    for word in ("hashed_password", "password_hash", "private_key", "secret_key", "payload", "message body"):
        assert word not in html


def test_stat_dataclass_helpers():
    stats = sample_stats()
    assert stats.users_inactive == 2
    assert stats.events_failed == 2
    assert stats.events_pending == 4
    assert re.fullmatch(r"With Supplier", dashboard.label_for("with_supplier"))


# --- the real queries, run against in-memory SQLite ------------------------------------------
# SQLite stands in for Postgres here (JSONB is shimmed in conftest).

@pytest_asyncio.fixture
async def db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with async_sessionmaker(engine, expire_on_commit=False)() as session:
        yield session
    await engine.dispose()


def _user(name: str, role: UserRole, active: bool = True, days_ago: int = 0) -> User:
    return User(
        id=uuid.uuid4(), email=f"{name.lower().replace(' ', '.')}@x.test", hashed_password="not-a-real-hash",
        full_name=name, role=role, is_active=active, created_at=datetime.now(timezone.utc) - timedelta(days=days_ago),
    )


def _batch(farmer: User, status: BatchStatus, kg: float) -> HarvestBatch:
    return HarvestBatch(
        id=uuid.uuid4(), farmer_id=farmer.id, species="Kappaphycus", estimated_weight_kg=kg,
        harvested_at=datetime.now(timezone.utc), status=status, current_holder_id=farmer.id,
    )


def _event(batch: HarvestBatch, actor: User, chain: OnChainStatus, hours_ago: float) -> ChainOfCustodyEvent:
    when = datetime.now(timezone.utc) - timedelta(hours=hours_ago)
    return ChainOfCustodyEvent(
        id=uuid.uuid4(), batch_id=batch.id, event_type=CustodyEventType.NOTE_ADDED, actor_id=actor.id,
        actor_role=actor.role, occurred_at=when, received_at=when, payload={"secret": "never shown"},
        on_chain_status=chain,
    )


@pytest.mark.asyncio
async def test_collect_stats_on_an_empty_database(db):
    stats = await dashboard.collect_stats(db)
    assert stats.users_total == stats.batches_total == stats.events_total == stats.messages_total == 0
    assert stats.prices_total == 0 and stats.prices_latest is None
    assert stats.recent_events == [] and stats.recent_users == []
    # Every enum member is present (zeros included) so the panels keep a stable shape.
    assert [c.key for c in stats.users_by_role] == ["farmer", "supplier", "buyer"]
    assert len(stats.batches_by_status) == len(BatchStatus)
    assert all(c.count == 0 for c in stats.events_by_chain)


@pytest.mark.asyncio
async def test_collect_stats_counts_everything(db):
    farmer = _user("Ana Farmer", UserRole.FARMER, days_ago=3)
    farmer2 = _user("Old Farmer", UserRole.FARMER, active=False, days_ago=9)
    buyer = _user("Ben Buyer", UserRole.BUYER, days_ago=1)
    db.add_all([farmer, farmer2, buyer])
    await db.flush()

    b1, b2, b3 = _batch(farmer, BatchStatus.HARVESTED, 100.5), _batch(farmer, BatchStatus.HARVESTED, 50), _batch(farmer, BatchStatus.EXPORTED, 20)
    db.add_all([b1, b2, b3])
    await db.flush()

    db.add_all([
        _event(b1, farmer, OnChainStatus.ANCHORED, hours_ago=1),
        _event(b1, farmer, OnChainStatus.FAILED, hours_ago=2),
        _event(b2, buyer, OnChainStatus.PENDING, hours_ago=48),
        _event(b3, buyer, OnChainStatus.ANCHORED, hours_ago=72),
    ])
    now = datetime.now(timezone.utc)
    db.add_all([
        Message(id=uuid.uuid4(), sender_id=farmer.id, recipient_id=buyer.id, body="private text", occurred_at=now),
        Message(id=uuid.uuid4(), sender_id=buyer.id, recipient_id=farmer.id, body="private reply", occurred_at=now, read_at=now),
    ])
    for day, price in ((5, 30), (1, 33)):
        db.add(PriceRecord(id=uuid.uuid4(), species="Kappaphycus", price_per_kg=price, posted_by_id=buyer.id,
                           effective_date=(now - timedelta(days=day)).date()))
    await db.commit()

    stats = await dashboard.collect_stats(db)

    assert (stats.users_total, stats.users_active, stats.users_inactive) == (3, 2, 1)
    assert {c.key: c.count for c in stats.users_by_role} == {"farmer": 2, "supplier": 0, "buyer": 1}
    assert stats.batches_total == 3
    assert stats.batches_total_kg == pytest.approx(170.5)
    assert {c.key: c.count for c in stats.batches_by_status}["harvested"] == 2
    assert stats.events_total == 4
    assert stats.events_last_24h == 2
    assert (stats.events_failed, stats.events_pending) == (1, 1)
    assert (stats.messages_total, stats.messages_unread) == (2, 1)
    assert stats.prices_total == 2
    assert stats.prices_latest == (now - timedelta(days=1)).date()

    # Recent events: newest first, joined to the actor's name.
    assert [(e.actor_name, e.on_chain_status) for e in stats.recent_events][:2] == [
        ("Ana Farmer", "anchored"), ("Ana Farmer", "failed"),
    ]
    # Newest users: most recently created first.
    assert [u.full_name for u in stats.recent_users] == ["Ben Buyer", "Ana Farmer", "Old Farmer"]

    # Nothing sensitive is ever collected.
    dumped = repr(stats)
    for secret in ("private text", "private reply", "not-a-real-hash", "never shown"):
        assert secret not in dumped


@pytest.mark.asyncio
async def test_recent_lists_are_capped(db):
    farmer = _user("Ana Farmer", UserRole.FARMER)
    db.add(farmer)
    await db.flush()
    batch = _batch(farmer, BatchStatus.HARVESTED, 1)
    db.add(batch)
    await db.flush()
    db.add_all([_event(batch, farmer, OnChainStatus.ANCHORED, hours_ago=i) for i in range(dashboard.RECENT_EVENTS_LIMIT + 5)])
    db.add_all([_user(f"User {i}", UserRole.BUYER, days_ago=i) for i in range(dashboard.RECENT_USERS_LIMIT + 4)])
    await db.commit()

    stats = await dashboard.collect_stats(db)
    assert len(stats.recent_events) == dashboard.RECENT_EVENTS_LIMIT
    assert len(stats.recent_users) == dashboard.RECENT_USERS_LIMIT
