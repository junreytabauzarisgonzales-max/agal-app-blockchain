import asyncio
from datetime import date, datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.admin import auth
from app.admin.dashboard import (
    Count,
    DashboardStats,
    RecentEvent,
    RecentUser,
    load_stats,
)
from app.core.config import settings
from app.db.base import Base
from app.db.session import get_db
from app.main import app


@compiles(JSONB, "sqlite")
def _jsonb_as_json(element, compiler, **kw):
    # SQLite stands in for Postgres in tests; the only schema difference we need is JSONB.
    return "JSON"


@compiles(PG_UUID, "sqlite")
def _uuid_as_text(element, compiler, **kw):
    # SQLite's NUMERIC affinity for a literal UUID type can turn digit-only
    # UUID hex strings into floats. Production Postgres has a native UUID type.
    return "CHAR(32)"


ADMIN_EMAIL = "test-admin@example.test"
ADMIN_PASSWORD = "test-admin-password-123"
ADMIN_SECRET = "test-session-secret-not-used-anywhere-else"


def sample_stats(**overrides) -> DashboardStats:
    stats = DashboardStats(
        generated_at=datetime(2026, 9, 19, 4, 30, tzinfo=timezone.utc),
        users_total=12,
        users_active=10,
        users_by_role=[Count("farmer", "Farmer", 7), Count("supplier", "Supplier", 3), Count("buyer", "Buyer", 2)],
        prices_total=41,
        prices_latest=date(2026, 9, 18),
        batches_total=25,
        batches_total_kg=1234.5,
        batches_by_status=[Count("harvested", "Harvested", 20), Count("exported", "Exported", 5)],
        events_total=60,
        events_last_24h=6,
        events_by_chain=[
            Count("pending", "Pending", 4),
            Count("anchored", "Anchored", 54),
            Count("failed", "Failed", 2),
        ],
        messages_total=88,
        messages_unread=9,
        recent_events=[
            RecentEvent(
                datetime(2026, 9, 19, 3, 0, tzinfo=timezone.utc),
                "drying_started",
                "Ana Farmer",
                "farmer",
                "0f0e0d0c-aaaa-bbbb-cccc-000000000001",
                "anchored",
            )
        ],
        recent_users=[RecentUser("Ben Buyer", "buyer", True, datetime(2026, 9, 18, 9, 0, tzinfo=timezone.utc))],
    )
    for key, value in overrides.items():
        setattr(stats, key, value)
    return stats


@pytest.fixture
def db_session_factory(tmp_path):
    """A throwaway SQLite database (never the real one). The app is pointed at it
    through get_db; tests seed and inspect it with the returned sync session factory."""
    path = tmp_path / "admin-test.db"
    sync_engine = create_engine(f"sqlite:///{path}")
    Base.metadata.create_all(sync_engine)
    async_engine = create_async_engine(f"sqlite+aiosqlite:///{path}", poolclass=NullPool)
    maker = async_sessionmaker(async_engine, expire_on_commit=False, autoflush=False)

    async def override_get_db():
        async with maker() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    yield sessionmaker(sync_engine, expire_on_commit=False)
    asyncio.run(async_engine.dispose())
    sync_engine.dispose()


@pytest.fixture(autouse=True)
def admin_settings(monkeypatch, db_session_factory):
    """Pins admin config to test values (independent of any local .env) and
    resets the in-memory session store / login throttle between tests."""
    monkeypatch.setattr(settings, "ADMIN_EMAIL", ADMIN_EMAIL)
    monkeypatch.setattr(settings, "ADMIN_PASSWORD", ADMIN_PASSWORD)
    monkeypatch.setattr(settings, "ADMIN_SESSION_SECRET", ADMIN_SECRET)
    monkeypatch.setattr(settings, "ADMIN_SESSION_IDLE_MINUTES", 30)
    monkeypatch.setattr(settings, "ADMIN_SESSION_MAX_MINUTES", 480)
    monkeypatch.setattr(settings, "UPSTASH_REDIS_REST_URL", None)
    monkeypatch.setattr(settings, "UPSTASH_REDIS_REST_TOKEN", None)
    auth.session_store.clear()
    auth.login_throttle.clear()
    # Dashboard tests must never touch a real database; individual tests override this.
    app.dependency_overrides[load_stats] = lambda: sample_stats()
    yield
    app.dependency_overrides.clear()
    auth.session_store.clear()
    auth.login_throttle.clear()


@pytest.fixture
def client():
    with TestClient(app, follow_redirects=False) as c:
        yield c


def login(client: TestClient, email: str = ADMIN_EMAIL, password: str = ADMIN_PASSWORD):
    """GET the form for its CSRF token + cookie, then POST credentials."""
    page = client.get("/admin/login")
    token = page.text.split('name="csrf_token" value="')[1].split('"')[0]
    return client.post("/admin/login", data={"email": email, "password": password, "csrf_token": token})


@pytest.fixture
def admin_client(client):
    response = login(client)
    assert response.status_code == 303
    return client
