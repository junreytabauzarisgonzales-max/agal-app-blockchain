import json
from pathlib import Path
from uuid import UUID

import pytest
from dotenv import dotenv_values
from pydantic import ValidationError
from sqlalchemy.pool import NullPool

from app.core.config import Settings, settings
from app.db.session import engine_options
from app.db.url import async_database_url
from scripts.generate_secrets import prepare
from app.models.enums import UserRole
from app.models.user import User

TEST_SECRET = "test-only-signing-key-with-more-than-32-characters"


def test_sqlite_test_database_preserves_digit_only_postgres_uuids(db_session_factory):
    identifier = UUID("00000000-0000-4000-8000-000000000001")
    with db_session_factory() as db:
        db.add(User(id=identifier, email="uuid-test@example.test", full_name="UUID test", hashed_password="test-only", role=UserRole.FARMER))
        db.commit()
    with db_session_factory() as db:
        assert db.get(User, identifier).id == identifier


def test_secret_generator_replaces_placeholders_without_changing_other_values(tmp_path, capsys):
    path = tmp_path / ".env"
    path.write_text('PROJECT_NAME="Agal API"\nSECRET_KEY=change-me-to-a-random-secret\nDATABASE_URL=keep-this\n', encoding="utf-8")
    assert prepare(path) == ["SECRET_KEY", "CRON_SECRET"]
    values = dotenv_values(path)
    assert len(values["SECRET_KEY"]) == 64 and len(values["CRON_SECRET"]) == 64
    assert values["SECRET_KEY"] != values["CRON_SECRET"]
    assert values["DATABASE_URL"] == "keep-this"
    original = path.read_text()
    assert prepare(path) == [] and path.read_text() == original
    assert capsys.readouterr().out == ""


def test_production_requires_a_real_jwt_secret_without_echoing_secrets():
    for value in ("change-me-to-a-random-secret", "short"):
        with pytest.raises(ValidationError):
            Settings(_env_file=None, ENVIRONMENT="production", SECRET_KEY=value)
    Settings(_env_file=None, ENVIRONMENT="production", SECRET_KEY=TEST_SECRET)
    with pytest.raises(ValidationError) as error:
        Settings(_env_file=None, ENVIRONMENT="production", SECRET_KEY="short", SERVICE_WALLET_PRIVATE_KEY="test-private-material-do-not-print")
    assert "test-private-material-do-not-print" not in str(error.value)


def test_vercel_requires_external_postgres_and_shared_admin_sessions():
    values = {"VERCEL": True, "SECRET_KEY": TEST_SECRET, "DATABASE_URL": "postgresql://u:p@db.example.test/agal?sslmode=require"}
    configured = Settings(_env_file=None, **values)
    assert configured.ENVIRONMENT == "production"
    with pytest.raises(ValidationError, match="external PostgreSQL"):
        Settings(_env_file=None, **{**values, "DATABASE_URL": "postgresql://u:p@localhost/agal"})
    admin = {"ADMIN_EMAIL": "admin@example.test", "ADMIN_PASSWORD": "test-only-password-123", "ADMIN_SESSION_SECRET": "s" * 40}
    with pytest.raises(ValidationError, match="shared Upstash"):
        Settings(_env_file=None, **values, **admin)
    shared = Settings(_env_file=None, **values, **admin, UPSTASH_REDIS_REST_URL="https://redis.example.test", UPSTASH_REDIS_REST_TOKEN="test-token")
    assert shared.admin_shared_store_enabled and shared.admin_enabled


def test_provider_database_urls_are_compatible_with_asyncpg():
    url = async_database_url("postgres://user:p%40ss@db.example.test/agal?sslmode=require&channel_binding=require")
    assert url.drivername == "postgresql+asyncpg"
    assert url.password == "p@ss"
    assert url.query == {"ssl": "require"}
    assert async_database_url("sqlite+aiosqlite:///:memory:").drivername == "sqlite+aiosqlite"
    options = engine_options(serverless=True, postgres=True)
    assert options["poolclass"] is NullPool
    assert options["connect_args"] == {"statement_cache_size": 0, "prepared_statement_cache_size": 0}
    assert "poolclass" not in engine_options(serverless=False, postgres=True)


def test_cron_is_authenticated_bounded_and_hidden_from_public_schema(client, monkeypatch):
    calls = []
    async def sweep(limit, *, retry_failed):
        calls.append((limit, retry_failed))
        return 1
    monkeypatch.setattr(settings, "CRON_SECRET", "test-only-cron-secret-of-sufficient-length")
    monkeypatch.setattr("app.api.routes.cron.anchor_pending_events", sweep)
    route = "/internal/cron/chain-anchors"
    assert client.get(route).status_code == 401
    assert client.get(route, headers={"Authorization": "Bearer wrong"}).status_code == 401
    auth = {"Authorization": f"Bearer {settings.CRON_SECRET}"}
    monkeypatch.setattr(settings, "WEB3_PROVIDER_URL", None)
    assert client.get(route, headers=auth).status_code == 503
    for field in ("WEB3_PROVIDER_URL", "HARVEST_LEDGER_ADDRESS", "SERVICE_WALLET_PRIVATE_KEY"):
        monkeypatch.setattr(settings, field, "test-only-value")
    response = client.get(route, headers=auth)
    assert response.status_code == 200 and response.json() == {"status": "ok", "checked": 1}
    assert response.headers["cache-control"] == "no-store"
    assert calls == [(1, True)]
    assert route not in client.get("/openapi.json").json()["paths"]


def test_vercel_config_uses_current_entrypoint_and_a_hobby_compatible_schedule():
    config = json.loads((Path(__file__).resolve().parents[1] / "vercel.json").read_text())
    assert config["framework"] == "fastapi"
    assert config["functions"]["app/main.py"]["maxDuration"] == 300
    assert "builds" not in config and "routes" not in config
    assert config["crons"] == [{"path": "/internal/cron/chain-anchors", "schedule": "0 0 * * *"}]
